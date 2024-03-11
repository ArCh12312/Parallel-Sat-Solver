# from multiprocessing import Process, Pool, cpu_count, Manager, Value, Lock
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor
import threading
from queue import PriorityQueue
import sys
import time

class DPLLSolver:
    def __init__(self, file_path):
        self.file_path = file_path
        self.clauses = []
        self.num_vars = 0
        self.num_clauses = 0
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
        if method == "first":
            return formula[0][0]

    def dpll(self, formula, model = []): ### Iterative
        formula, model = self.unit_propagate(formula, model)
        if formula == []:
            return True, model
        if formula == [[]]:
            return False, model
        literal = self.select_literal(formula)
        # print(formula)
        formula_pos = formula+[[literal]]
        formula_neg = formula+[[-literal]]

        # # Parallelize the recursive calls
        # future1 = self.executor.submit(self.dpll, formula_pos, model)
        # future2 = self.executor.submit(self.dpll, formula_neg, model)

        # sat1, model1 = future1.result()
        # sat2, model2 = future2.result()

        # if sat1:
        #     return True, model1
        # elif sat2:
        #     return True, model2
        # else:
        #     return False, []

        sat, model = self.dpll(formula_pos, model)
        if sat:
            return True, model
        
        sat, model = self.dpll(formula_neg, model)
        if sat:
            return True, model
        
        return False, []

    def solve(self):
        return self.dpll(self.clauses)

def main():
    # if len(sys.argv) != 3:
    #     print("Usage: python parallel_dpll.py <input_file_path> <output_file_path>")
    #     sys.exit(1)

    # input_file_path = sys.argv[1]
    input_file_path = "./tests/uf20-91/uf20-099.cnf"
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