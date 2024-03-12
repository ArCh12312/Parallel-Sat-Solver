# from multiprocessing import Process, Pool, cpu_count, Manager, Value, Lock
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
from queue import PriorityQueue, Queue
import sys
import time
from collections  import defaultdict

class DPLLSolver:
    def __init__(self, file_path):
        self.file_path = file_path
        self.clauses = []
        self.num_vars = 0
        self.num_clauses = 0
        self.cubes = []
        self.formula_queue = Queue()
        self.executor = ThreadPoolExecutor(max_workers=cpu_count())
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

    def find_unit_clause(self, formula):
        for clause in formula:
            if len(clause) == 1:
                return clause[0]
        return 0

    # @staticmethod
    # def unit_propagate(formula):
    #     while True:
    #         unit_clause = DPLLSolver.find_unit_clause(formula)
    #         if not unit_clause:
    #             break
    #         unit_clause = unit_clause[0]
    #         formula = [clause for clause in formula if unit_clause not in clause]
    #         formula = [[lit for lit in clause if lit != -unit_clause] for clause in formula]
    #     return formula
                        
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

    def select_literal(self, formula, method="first"):
        jw_scores = defaultdict(float)
        for clause in formula:
            for literal in clause:
                jw_scores[literal] += 2**-len(clause)
                
        # Sort the literals based on their Jeroslow-Wang scores in descending order
        sorted_literals = sorted(jw_scores, key=jw_scores.get, reverse=True)
        # Return the top 5 literals
        return sorted_literals[0]
        # if method == "first":
        #     return formula[0][0]

    def dpll_1(self, formula, model = [], depth = 0):
        formula, model = self.unit_propagate(formula, model)
        if formula == []:
            return True, model
        if formula == [[]]:
            return False, []
        literal = self.select_literal(formula)
        pos_formula = formula + [[literal]]
        neg_formula = formula + [[-literal]]
        pos_model = model[:]
        neg_model = model[:]

        if depth == 3:
            self.cubes.append([pos_formula, model])
            self.cubes.append([neg_formula, model])
            return False, []

        else:
            depth += 1
            sat_pos, pos_model = self.dpll_1(pos_formula, pos_model, depth)
            if sat_pos:
                return True, pos_model

            sat_neg, neg_model = self.dpll_1(neg_formula, neg_model, depth)
            if sat_neg:
                return True, neg_model

            return False, []

    def dpll(self, formula, model = []):
        formula, model = self.unit_propagate(formula, model)
        if formula == []:
            return True, model
        if formula == [[]]:
            return False, []
        literal = self.select_literal(formula)
        pos_formula = formula + [[literal]]
        neg_formula = formula + [[-literal]]
        pos_model = model[:]
        neg_model = model[:]

        sat_pos, pos_model = self.dpll(pos_formula, pos_model)
        if sat_pos:
            return True, pos_model

        sat_neg, neg_model = self.dpll(neg_formula, neg_model)
        if sat_neg:
            return True, neg_model

        return False, []

    def dpll_parallel(self):
        cubes = self.cubes
        with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
            futures = [executor.submit(self.dpll, cube[0], cube[1]) for cube in cubes]
            for future in futures:
                sat, model = future.result()
                if sat:
                    return True, model
        return False, []

    def solve(self):
        sat, model = self.dpll_1(self.clauses)
        if not sat and len(self.cubes) != 0:
            return self.dpll_parallel()
        return sat, model 
    
def main():
    # if len(sys.argv) != 3:
    #     print("Usage: python parallel_dpll.py <input_file_path> <output_file_path>")
    #     sys.exit(1)

    # input_file_path = sys.argv[1]
    input_file_path = "./tests/UF250.1065.100/uf250-02.cnf"
    solver = DPLLSolver(input_file_path)
    start = time.time()
    sat, model = solver.solve()
    end = time.time()
    
    # Write the output to a text file
    # output_file_path = sys.argv[2]
    output_file_path = "./dpll_output.txt"
    with open(output_file_path, "w") as file:
        file.write(f"Satisfiable: {sat}\n")
        file.write(f"Model: {model}\n")
    print(f"Output written to {output_file_path}")
    print(f"Solving time: {end-start}seconds")

if  __name__ == '__main__':
    main()