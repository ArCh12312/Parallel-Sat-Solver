import time

class DPLLSolver:
    def __init__(self):
        self.clauses = []
        self.num_vars = 0
        self.num_clauses = 0
        self.branch_count = 0

    def read_dimacs_cnf(self, input_file_path):
        with open(input_file_path, 'r') as file:
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

    def pure_literal_elimination(self, formula, model):
        while True:
            literals = {literal for clause in formula for literal in clause}
            pure_literals = {literal for literal in literals if -literal not in literals}
            if not pure_literals:
                break
            for literal in pure_literals:
                if literal not in model:
                    model.append(literal)
            formula = [clause for clause in formula if not any(literal in clause for literal in pure_literals)]
        return formula, model

    def select_literal(self, formula, method="first"):
        if method == "first":
            return formula[0][0]

    def dpll(self, formula, model = []):
        formula, model = self.unit_propagate(formula, model)
        formula, model = self.pure_literal_elimination(formula, model)

        if formula == []:
            return True, model
        if formula == [[]]:
            return False, []
        
        literal = self.select_literal(formula)
        pos_formula = formula + [[literal]]
        neg_formula = formula + [[-literal]]
        pos_model = model[:]
        neg_model = model[:]

        self.branch_count += 1

        sat_pos, pos_model = self.dpll(pos_formula, pos_model)
        if sat_pos:
            return True, pos_model

        sat_neg, neg_model = self.dpll(neg_formula, neg_model)
        if sat_neg:
            return True, neg_model

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

    def solve(self, input_file_path):
        start = time.time()
        self.read_dimacs_cnf(input_file_path)
        end = time.time()
        read_time = end - start
        start = time.time()
        sat, model = self.dpll(self.clauses)
        end = time.time()
        solve_time = end - start
        if sat:
            verification_result = self.verify_solution(model)
        else:
            verification_result = True
        return sat, model, verification_result, self.branch_count, read_time, solve_time

def main():
    # input_file_path = "./tests/uf20-91/uf20-01.cnf"
    # input_file_path = "./tests/UF250.1065.100/uf250-01.cnf"
    input_file_path = input("Enter input file path: ")
    solver = DPLLSolver()
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