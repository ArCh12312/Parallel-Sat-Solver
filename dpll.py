import sys
import time

class DPLLSolver:
    def __init__(self, file_path):
        self.file_path = file_path
        self.clauses = []
        self.num_vars = 0
        self.num_clauses = 0
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

    def find_unit_clause(formula):
        for clause in formula:
            if len(clause) == 1:
                return clause[0]
        return 0

    def unit_propagate(self, formula):
        unit_clause = DPLLSolver.find_unit_clause(formula)
        while unit_clause != 0:
            new_unit_clause = 0
            new_formula = []
            for clause in formula:
                if unit_clause in clause:
                    continue
                else:
                    clause = [lit for lit in clause if lit != -unit_clause]
                    if clause == []:
                        return -1
                    if len(clause) == 1:
                        new_unit_clause = clause[0]
                    new_formula.append(clause)
            formula = new_formula
            unit_clause = new_unit_clause
        return formula

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

    @staticmethod
    def select_literal(formula, method="first"):
        if method == "first":
            return formula[0][0]

    def dpll(self, formula):
        formula = self.unit_propagate(formula)
        if formula == []:
            return True
        if formula == -1:
            return False
        literal = DPLLSolver.select_literal(formula)
        sat = self.dpll(formula + [[literal]])
        if sat:
            return True
        sat = self.dpll(formula + [[-literal]])
        if sat:
            return True
        return False

    def solve(self):
        return self.dpll(self.clauses)


def main():
    if len(sys.argv) != 3:
        print("Usage: python parallel_dpll.py <input_file_path> <output_file_path>")
        sys.exit(1)

    input_file_path = sys.argv[1]
    solver = DPLLSolver(input_file_path)
    start = time.time()
    sat = solver.solve()
    end = time.time()
    
    # Write the output to a text file
    output_file_path = sys.argv[2]
    with open(output_file_path, "w") as file:
        file.write(f"Satisfiable: {sat}\n")
    print(f"Output written to {output_file_path}")
    print(f"Solving time: {end-start}seconds")

if  __name__ == '__main__':
    main()