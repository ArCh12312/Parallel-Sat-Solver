import sys
import time 
from collections import defaultdict
import threading

class Cube_and_Conquer_Solver:
    def __init__(self, file_path, method="first"):
        self.file_path = file_path
        self.clauses = []
        self.num_vars = 0
        self.num_clauses = 0
        self.method = method # For Candidate Selection
        self.num_cubes = 0
        self.cubes = []
        self.read_dimacs_cnf()
    
    def read_dimacs_cnf(self):
        with open(self.file_path, 'r') as file:
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
    
    @staticmethod
    def find_unit_clause(formula):
        for clause in formula:
            if len(clause) == 1:
                return clause[0]
        return 0

    def unit_propagate(self, formula, model=[]):
        unit_clause = Cube_and_Conquer_Solver.find_unit_clause(formula)
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

    # def create_watchlist(self):
    #     literal_watch = {}
    #     for x in range(0, self.num_clauses):
    #         for literal in self.clauses[x]:
    #             if literal not in literal_watch:
    #                 literal_watch[literal] = [x]
    #                 continue
    #             literal_watch[literal] += [x]

    def is_formula_easy(self, formula, model):
        threshold = 4.3
        ratio = len(formula) / (self.num_vars - len(model))
        if ratio < threshold - 0.7 or ratio > threshold+1.5:
            self.num_cubes += 1
            return True
        return False

    def CDCL_solve(self, formula, model):
        # print(formula, model)
        # if self.depth == 16:
        #     return True, model
        print(f"Number of cubes learnt: {self.num_cubes}")
        self.cubes.append([formula, model])
        return False, []
    
    def select_candidate_literals(self, formula):
        # Branching Heuristics?
        # Jeroslow-Wang Heuristic
        jw_scores = defaultdict(float)
        for clause in formula:
            for literal in clause:
                jw_scores[literal] += 2**-len(clause)
                
        # Sort the literals based on their Jeroslow-Wang scores in descending order
        sorted_literals = sorted(jw_scores, key=jw_scores.get, reverse=True)
        
        # Return the top 5 literals
        return sorted_literals[:5]

    def compute_score(self, formula, subformula, model, new_model):
        return (len(formula)/len(subformula))*((len(new_model)+1)/(len(model)+1))

    def look_ahead(self, formula, literals, model):
        ### return the best literal to propogate or we could just return the best literal propagted formula( not need to do unit propagation again)
        ### Return the formulas and the models
        best_score = 0
        output = []
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
                return [], [], [[]], []
            elif formula_neg == []:
                return [[]], [], [], []
            else:
                score_pos = self.compute_score(formula, formula_pos, model, model_pos)
                score_neg = self.compute_score(formula, formula_neg, model, model_neg)
                if score_pos > best_score:
                    best_score = score_pos
                    output = [formula_pos, model_pos,  formula_neg, model_neg]
                if score_neg > best_score:
                    best_score = score_neg
                    output = [formula_neg, model_neg, formula_pos, model_pos]
        return output[0],output[1], output[2], output[3]

    def cube_and_conquer(self, formula, model = []):
        formula, model = self.unit_propagate(formula, model)
        # formula = self.pure_literal_elimination(formula, model)
        if formula == []:
            return True, model
        if formula == [[]]:
            return False, []
        if self.is_formula_easy(formula, model):
            return self.CDCL_solve(formula, model)
        literals = self.select_candidate_literals(formula)
        best_formula, best_model, alternative_formula, alternative_model = self.look_ahead(formula, literals, model)
        sat, model = self.cube_and_conquer(best_formula, best_model)
        if sat:
            return True, model
        sat, model = self.cube_and_conquer(alternative_formula, alternative_model)
        if sat:
            return True, model
        return False, []
                # Container for results
        # results = [None, None]

        # # Define a worker function for threads
        # def worker(formula, model, index):
        #     sat, model = self.cube_and_conquer(formula, model)
        #     results[index] = (sat, model)

        # # Create threads for best and alternative formulas
        # best_thread = threading.Thread(target=worker, args=(best_formula, best_model, 0))
        # alternative_thread = threading.Thread(target=worker, args=(alternative_formula, alternative_model, 1))

        # # Start threads
        # best_thread.start()
        # alternative_thread.start()

        # # Wait for threads to complete
        # best_thread.join()
        # alternative_thread.join()

        # # Check results
        # for sat, model in results:
        #     if sat:
        #         return True, model
        # return False, []
    
    def solve(self):
        sat, model = self.cube_and_conquer(self.clauses)
        print(self.cubes)
        return sat, model
    
def main():
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python CnC_draft1.py <input_file_path> <output_file_path> [method]")
        sys.exit(1)

    # input_file_path = "./tests/uf20-91/uf20-01.cnf"
    input_file_path = sys.argv[1]
    method = sys.argv[3] if len(sys.argv) == 4 else "first"  # Default to "first" if not specified
    # method = "mfv"
    solver = Cube_and_Conquer_Solver(input_file_path, method)
    start = time.time()
    sat, model = solver.solve()
    end = time.time()
    
    # Write the output to a text file
    output_file_path = sys.argv[2]
    # output_file_path = "./dpll_output.txt"
    with open(output_file_path, "w") as file:
        file.write(f"Satisfiable: {sat}\n")
        file.write(f"Model: {model}\n")
    print(f"Output written to {output_file_path}")
    print(f"Completed in {end-start}")

if __name__ == "__main__":
    main()