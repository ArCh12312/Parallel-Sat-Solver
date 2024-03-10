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

    # @staticmethod
    # def find_unit_clause(formula):
    #     for clause in formula:
    #         if len(clause) == 1:
    #             return clause
    #     return None

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
                        
    def unit_propagate(self, formula):
        unit_clauses = {clause[0] for clause in formula if len(clause) == 1}
        while unit_clauses:
            unit_clause = unit_clauses.pop()
            new_formula = []
            for clause in formula:
                if unit_clause in clause:
                    continue  # Remove the entire clause
                if -unit_clause in clause:
                    new_clause = [lit for lit in clause if lit != -unit_clause]
                    if len(new_clause) == 0:
                        return [[]]  # Formula is unsatisfiable
                    if len(new_clause) == 1:
                        unit_clauses.add(new_clause[0])  # Found a new unit clause
                    new_formula.append(new_clause)
                else:
                    new_formula.append(clause)
            formula = new_formula
        return formula

    def select_literal(self, formula, method="first"):
        if method == "first":
            return formula[0][0]

    # def dpll(self, formula): ### Iterative
    #     formula = self.unit_propagate(formula)
    #     if formula == []:
    #         return True
    #     if formula == [[]]:
    #         return False
    #     literal = self.select_literal(formula)
    #     sat = self.dpll(formula+[[literal]])
    #     if sat:
    #         return True
    #     sat = self.dpll(formula+[[-literal]])
    #     if sat:
    #         return True
    #     return False
        
    def dpll(self, formula): ### Iterative
        formula = self.unit_propagate(formula)
        if formula == []:
            return True
        if formula == [[]]:
            return False
        literal = self.select_literal(formula)
        with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
            futures = [executor.submit(self.dpll_worker, formula + [[literal]]),
                       executor.submit(self.dpll_worker, formula + [[-literal]])]
            results = [future.result() for future in futures]
        return any(results)

    def dpll_worker(self, formula):
        formula = self.unit_propagate(formula)
        if formula == []:
            return True
        if formula == [[]]:
            return False
        literal = self.select_literal(formula)
        
        futures = [self.executor.submit(self.dpll_worker, formula + [[literal]]),
                    self.executor.submit(self.dpll_worker, formula + [[-literal]])]
        results = [future.result() for future in futures]
        return any(results)

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