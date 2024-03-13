import time 
from collections import defaultdict

class Look_ahead_Solver:
    def __init__(self):
        self.clauses = []
        self.num_vars = 0
        self.num_clauses = 0
        self.branch_count = 0
        self.weights = [0,0,0]
    
    def read_dimacs_cnf(self, file_path):
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('c') or line.startswith('0') or line.startswith('%'):
                    continue
                elif line.startswith('p'):
                    _, _, self.num_vars, self.num_clauses = line.split()
                    self.num_vars, self.num_clauses = int(self.num_vars), int(self.num_clauses)
                else:
                    clause = [int(x) for x in line.split() if x != '0']
                    if clause:
                        self.clauses.append(clause)
    
    def find_unit_clause(self, formula):
        for clause in formula:
            if len(clause) == 1:
                return clause[0]
        return 0
                        
    def unit_propagate(self, formula, model):
        unit_clause = self.find_unit_clause(formula)
        while unit_clause != 0:
            new_unit_clause = 0
            new_formula = []
            for clause in formula:
                if unit_clause in clause:
                    continue
                elif -unit_clause in clause:
                    clause = [lit for lit in clause if lit != -unit_clause]
                if clause == []:
                    return [[]], []
                if len(clause) == 1:
                    new_unit_clause = clause[0]
                new_formula.append(clause)
            formula = new_formula
            if unit_clause not in model:
                model.append(unit_clause)
            unit_clause = new_unit_clause
        return formula, model

    # @staticmethod
    # def pure_literal_elimination(formula, model):
    #     while True:
    #         literals = {literal for clause in formula for literal in clause}
    #         pure_literals = {literal for literal in literals if -literal not in literals}
    #         if not pure_literals:
    #             break
    #         for literal in pure_literals:
    #             if literal not in model:
    #                 model.append(literal)
    #         formula = [clause for clause in formula if not any(literal in clause for literal in pure_literals)]
    #     return formula, model
 
    def select_candidate_literals(self, formula):
        # Jeroslow-Wang Heuristic
        jw_scores = defaultdict(float)
        for clause in formula:
            for literal in clause:
                jw_scores[literal] += 2**-len(clause)
                
        # Sort the literals based on their Jeroslow-Wang scores in descending order
        sorted_literals = sorted(jw_scores, key=jw_scores.get, reverse=True)
        
        # Return the top 5 literals
        return sorted_literals[:5]

    def compute_score(self, original_formula, new_formula, original_model, new_model):
        # # Reduction in the number of clauses, prioritizing larger reductions.
        # clause_reduction = len(original_formula) - len(new_formula)

        # # Increase in the model size, prioritizing larger increases.
        # model_increase = len(new_model) - len(original_model)

        # # Consider the complexity reduction, focusing on clauses' length shortening.
        # original_complexity = sum(len(clause) for clause in original_formula)
        # new_complexity = sum(len(clause) for clause in new_formula)
        # complexity_reduction = original_complexity - new_complexity

        # # The score combines these factors with appropriate weights.
        # score = (clause_reduction * self.weights[0]) + (model_increase * self.weights[1]) + (complexity_reduction*self.weights[2])
        
                # Original components
        clause_reduction = len(original_formula) - len(new_formula)
        model_increase = len(new_model) - len(original_model)

        # New JW-like scoring for clause complexity reduction
        jw_score_original = sum(2**-len(clause) for clause in original_formula)
        jw_score_new = sum(2**-len(clause) for clause in new_formula)
        jw_complexity_reduction = jw_score_original - jw_score_new

        # Combine scores with adjusted weights
        score = (clause_reduction * self.weights[0]) + (model_increase * self.weights[1]) + (jw_complexity_reduction * self.weights[2])
        
        # score = 1

        return score

    def look_ahead(self, formula, literals, model):
        best_score = 0
        best_output = []
        for literal in literals:
            model_pos = model[:]
            model_neg = model[:]
            formula_pos, model_pos = self.unit_propagate(formula+[[literal]], model_pos)
            formula_neg, model_neg = self.unit_propagate(formula+[[-literal]], model_neg)
            if formula_pos == [[]] and formula_neg == [[]]:
                return [[]], [], [[]], []
            elif formula_pos == [[]]:
                return [[]], [], formula_neg, model_neg
            elif formula_neg == [[]]:
                return formula_pos, model_pos, [[]], []
            elif formula_pos == []:
                return formula_pos, model_pos, formula_neg, model_neg
            elif formula_neg == []:
                return formula_neg, model_neg, formula_pos, model_pos
            else:
                score_pos = self.compute_score(formula, formula_pos, model, model_pos)
                score_neg = self.compute_score(formula, formula_neg, model, model_neg)
                if score_pos > best_score:
                    best_score = score_pos
                    best_output = [formula_pos, model_pos, formula_neg, model_neg] 
                if score_neg > best_score:
                    best_score = score_neg
                    best_output = [formula_neg, model_neg, formula_pos, model_pos]
        return best_output[0], best_output[1], best_output[2], best_output[3]

    def look_ahead_dpll(self, formula, model = []):
        formula, model = self.unit_propagate(formula, model)
        # formula = self.pure_literal_elimination(formula, model)
        if formula == []:
            return True, model
        if formula == [[]]:
            return False, []
        
        literals = self.select_candidate_literals(formula)
        best_formula, best_model, alternative_formula, alternative_model = self.look_ahead(formula, literals, model)
        
        self.branch_count += 1

        sat, model = self.look_ahead_dpll(best_formula, best_model)
        if sat:
            return True, model
        
        sat, model = self.look_ahead_dpll(alternative_formula,alternative_model)
        if sat:
            return True, model
        
        return False, []
    
    def check_model_consistency(self, model):
        variables = set()
        for literal in model:
            variable = abs(literal)
            if variable in variables:
                print("Inconsistent")
                return False  # Inconsistent model
            variables.add(variable)
        return True

    def verify_solution(self, model):
        # Verify the solution
        next = self.check_model_consistency(model)
        if not next:
            return False
        for clause in self.clauses :                   # for each clause
            flag = False
            for literal in clause:
                if literal in model:                 # atleast one literal should be true
                    flag = True
                    break
            if not flag:
                print(f"Unsatisfied clause: {clause}")
                return False
        return True

    def solve(self, input_file_path, weights = [1,1,4]):
        start = time.time()
        self.read_dimacs_cnf(input_file_path)
        end = time.time()
        read_time = end - start
        self.weights = weights
        start = time.time()
        sat, model = self.look_ahead_dpll(self.clauses)
        end = time.time()
        solve_time = end - start
        if sat:
            verification_result = self.verify_solution(model)
        else:
            verification_result = True
        return sat, model, verification_result, self.branch_count, read_time, solve_time

def main():
    # input_file_path = "./tests/uf20-91/uf20-01.cnf"
    input_file_path = "./tests/UF250.1065.100/uf250-01.cnf"
    # input_file_path = "./tests/uf100-01.cnf"
    # input_file_path = input("Enter input file path: ")
    solver = Look_ahead_Solver()
    sat, model, verification_result, branch_count, read_time, solve_time = solver.solve(input_file_path)

    # Write the output to a text file
    output_file_path = "./log_file.txt"
    with open(output_file_path, "w") as file:
        file.write(f"Read time: {read_time} seconds\n")
        file.write(f"Satisfiable: {sat}\n")
        file.write(f"Model: {model}\n")
        file.write(f"Assignment verification result: {verification_result}\n")
        file.write(f"Branch count: {branch_count}\n")
        file.write(f"Solving time: {solve_time} seconds\n")
    print(f"Read time: {read_time} seconds")
    print(f"Satisfiable: {sat}")
    print(f"Model: {model}")
    print(f"Assignment verification result: {verification_result}")
    print(f"Branch count: {branch_count}")
    print(f"Solving time: {solve_time} seconds")
    print(f"Output written to {output_file_path}")

if __name__ == "__main__":
    main()