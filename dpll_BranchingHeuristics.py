import random
import sys
import cProfile
import pstats

class DPLLSolver:
    def __init__(self, file_path, method="first"):
        self.file_path = file_path
        self.clauses = []
        self.num_vars = 0
        self.num_clauses = 0
        self.method = method
        self.frequency = {}
        self.model = []
        self.model_stack = []
        self.read_dimacs_cnf()
        self.intialize_literal_frequency()
        self.frequency_stack = [self.frequency]

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

    def intialize_literal_frequency(self):
        for clause in self.clauses:
            for literal in clause:
                if literal in self.frequency:
                    self.frequency[literal] += 1
                else:
                    self.frequency[literal] = 1

    def push_model_state(self):
        self.model_stack.append(self.model.copy())

    def pop_model_state(self):
        if self.model_stack:
            self.model = self.model_stack.pop()
    
    def push_frequency_state(self):
        self.frequency_stack.append(self.frequency.copy())

    def pop_frequency_state(self):
        if self.frequency_stack:
            self.frequency = self.frequency_stack.pop()

    def update_frequency(self, clause):
        for lit in clause:
            if lit in self.frequency: 
                self.frequency[lit] -= 1
                if self.frequency[lit] == 0:
                    del self.frequency[lit]

    @staticmethod
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
                    self.update_frequency(clause)
                    continue
                elif -unit_clause in clause:
                    clause = [lit for lit in clause if lit != -unit_clause]
                if clause == []:
                    return -1
                if len(clause) == 1:
                    new_unit_clause = clause[0]
                new_formula.append(clause)
            formula = new_formula
            if -unit_clause in self.frequency:
                del self.frequency[-unit_clause]
            if unit_clause not in self.model:
                self.model.append(unit_clause)
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

    def select_literal(self, formula):
        if self.method == "first":
            return formula[0][0]
        elif self.method == "random":
            literals = {literal for clause in formula for literal in clause}
            return random.choice(list(literals))
        elif self.method == "mfv":
            # Most Frequent Variable (MFV) heuristic
            return max(self.frequency, key=self.frequency.get, default=None)
        elif self.method == "moms":
            # Most Occurrences in Minimum Size Clauses (MOMS)
            min_clause_size = min(len(clause) for clause in formula)
            min_clauses = [clause for clause in formula if len(clause) == min_clause_size]
            literals_frequency = {literal: self.frequency.get(abs(literal), 0) for clause in min_clauses for literal in clause}
            return max(literals_frequency, key=literals_frequency.get)
        elif self.method == "jw":
            # Jeroslow-Wang Heuristic
            jw_scores = {literal: 2**-len(clause) for clause in formula for literal in clause}
            return max(jw_scores, key=jw_scores.get)

    def dpll(self, formula):
        formula = self.unit_propagate(formula)
        if formula == []:
            return True, self.model
        if formula == -1:
            return False, []
        self.push_frequency_state()  # Push state before making a decision
        self.push_model_state()
        literal = self.select_literal(formula)
        sat, model = self.dpll(formula + [[literal]])
        if sat:
            return True, self.model
        self.pop_model_state()
        self.pop_frequency_state()  # Pop state when backtracking
        self.push_model_state()
        self.push_frequency_state()  # Push again for the opposite decision
        sat, model = self.dpll(formula + [[-literal]])
        if sat:
            return True, self.model
        self.pop_model_state()
        self.pop_frequency_state()  # Pop again if this path also fails
        return False, []

    def solve(self):
        return self.dpll(self.clauses)
        
def main():
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python dpll.py <input_file_path> <output_file_path> [method]")
        sys.exit(1)

    input_file_path = sys.argv[1]
    method = sys.argv[3] if len(sys.argv) == 4 else "first"  # Default to "first" if not specified
    solver = DPLLSolver(input_file_path, method)
    sat, model = solver.solve()
    
    # Write the output to a text file
    output_file_path = sys.argv[2]
    with open(output_file_path, "w") as file:
        file.write(f"Satisfiable: {sat}\n")
        file.write(f"Model: {model}\n")
    print(f"Output written to {output_file_path}")

if __name__ == "__main__":
    main()
    # cProfile.run('main()', 'solver_profile_stats')

    # # Create a Stats object based on the saved stats file
    # p = pstats.Stats('solver_profile_stats')

    # # Sort and print the stats
    # # Sort by cumulative time spent in a function and print the top 10 functions
    # p.sort_stats('cumulative').print_stats(10)
