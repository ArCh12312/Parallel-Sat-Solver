import random

class DPLLSolver:
    def __init__(self, file_path, method="first"):
        self.file_path = file_path
        self.clauses = []
        self.num_vars = 0
        self.num_clauses = 0
        self.method = method
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
                return clause
        return None

    @staticmethod
    def unit_propagate(formula, model):
        while True:
            unit_clause = DPLLSolver.find_unit_clause(formula)
            if not unit_clause:
                break
            unit_clause = unit_clause[0]
            formula = [clause for clause in formula if unit_clause not in clause]
            formula = [[lit for lit in clause if lit != -unit_clause] for clause in formula]
            if unit_clause not in model:
                model.append(unit_clause)
        return formula, model

    @staticmethod
    def pure_literal_elimination(formula, model):
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

    def literal_frequency(self, formula):
        frequency = {}
        for clause in formula:
            for literal in clause:
                if literal in frequency:
                    frequency[literal] += 1
                else:
                    frequency[literal] = 1
        return frequency

    def select_literal(self, formula):
        if self.method == "first":
            return formula[0][0]
        elif self.method == "random":
            literals = {literal for clause in formula for literal in clause}
            return random.choice(list(literals))
        elif self.method == "mfv":
            frequency = self.literal_frequency(formula)
            return max(frequency, key=frequency.get)
        elif self.method == "moms":
            min_clause_size = min(len(clause) for clause in formula)
            min_clauses = [clause for clause in formula if len(clause) == min_clause_size]
            frequency = self.literal_frequency(min_clauses)
            return max(frequency, key=frequency.get)
        elif self.method == "jw":
            frequency = self.literal_frequency(formula)
            jw_scores = {literal: 2**-len(clause) for clause in formula for literal in clause}
            return max(jw_scores, key=jw_scores.get)

    def dpll(self, formula, model=[]):
        formula, model = DPLLSolver.unit_propagate(formula, model)
        formula, model = DPLLSolver.pure_literal_elimination(formula, model)
        if not formula:
            return True, model
        if any(len(clause) == 0 for clause in formula):
            return False, []
        literal = self.select_literal(formula)
        new_model = model[:]
        sat, updated_model = self.dpll(formula + [[literal]], new_model)
        if sat:
            return True, updated_model
        new_model = model[:]
        sat, updated_model = self.dpll(formula + [[-literal]], new_model)
        if sat:
            return True, updated_model
        return False, []

    def solve(self):
        return self.dpll(self.clauses)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python dpll.py <file_path> [method]")
        sys.exit(1)

    file_path = sys.argv[1]
    method = sys.argv[2] if len(sys.argv) == 3 else "first"  # Default to "first" if not specified
    solver = DPLLSolver(file_path, method)
    sat, model = solver.solve()
    print(sat, model)
