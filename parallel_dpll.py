# from multiprocessing import Process, Pool, cpu_count, Manager, Value, Lock
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor
import threading
import sys

class DPLLSolver:
    def __init__(self, file_path):
        self.file_path = file_path
        self.clauses = []
        self.num_vars = 0
        self.num_clauses = 0
        self.result = False
        self.formula_stack = []
        self.lock = threading.Lock()
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
    def unit_propagate(formula):
        while True:
            unit_clause = DPLLSolver.find_unit_clause(formula)
            if not unit_clause:
                break
            unit_clause = unit_clause[0]
            formula = [clause for clause in formula if unit_clause not in clause]
            formula = [[lit for lit in clause if lit != -unit_clause] for clause in formula]
        return formula

    @staticmethod
    def select_literal(formula, method="first"):
        if method == "first":
            return formula[0][0]

    def dpll(self, formula):
        formula = self.unit_propagate(formula)
        if not formula: 
            with self.lock:
                self.result = True
                quit()
        elif all(len(clause) != 0 for clause in formula):
            literal = self.select_literal(formula)
            with self.lock:
                self.formula_stack.append(formula + [[literal]])
                self.formula_stack.append(formula + [[-literal]])

    def worker(self):
        while True:
            with self.lock:
                if not self.formula_stack:
                    break
                formula = self.formula_stack.pop()
            self.dpll(formula)
            if self.result:
                break
    
    def solve(self):
        self.formula_stack.append(self.clauses)
        with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
            futures = [executor.submit(self.worker) for _ in range(cpu_count())]

        # Wait for all threads to complete
        for future in futures:
            future.result()

        return self.result

def main():
    if len(sys.argv) != 3:
        print("Usage: python parallel_dpll.py <input_file_path> <output_file_path>")
        sys.exit(1)

    input_file_path = sys.argv[1]
    solver = DPLLSolver(input_file_path)
    sat = solver.solve()
    
    # Write the output to a text file
    output_file_path = sys.argv[2]
    with open(output_file_path, "w") as file:
        file.write(f"Satisfiable: {sat}\n")
    print(f"Output written to {output_file_path}")

if  __name__ == '__main__':
    main()

# There are 16 cpu cores.
    # 16 workers.
    # A worker picks the first formula on the stack and runs dpll on it
    # Once 2 new formulae have been pushed on to the stack the worker is freed
    # Then two free workers take one each.
    # More workers are allocated as the stack grows
    # This runs until either result is set True(Satisfiable) or there are no formulas left on the stack indicating they all lead to contradictions

















        # sat = DPLLSolver.dpll(formula + [[literal]])
        # if sat:
        #     return True
        # sat = DPLLSolver.dpll(formula + [[-literal]])
        # if sat:
        #     return True
        # return False

    # def dpll_1(self, formula, depth=0):
    #     if depth == 4:
    #         print("reached max depth")
    #         self.formula_stack.append(formula)
    #         return False
    #     formula = DPLLSolver.unit_propagate(formula)
    #     # formula, model = DPLLSolver.pure_literal_elimination(formula, model)
    #     if not formula:
    #         return True
    #     if any(len(clause) == 0 for clause in formula):
    #         print(1)
    #         return False
    #     literal = DPLLSolver.select_literal(formula)
    #     sat = self.dpll_1(formula + [[literal]], depth+1)
    #     if sat:
    #         return True
    #     sat = self.dpll_1(formula + [[-literal]],  depth+1)
    #     if sat:
    #         return True
    #     return False

    # def dpll(formula):
    #     formula = DPLLSolver.unit_propagate(formula)
    #     # formula, model = DPLLSolver.pure_literal_elimination(formula, model)
    #     if not formula:
    #         return True
    #     if any(len(clause) == 0 for clause in formula):
    #         return False
    #     literal = DPLLSolver.select_literal(formula)
    #     sat = DPLLSolver.dpll(formula + [[literal]])
    #     if sat:
    #         return True
    #     sat = DPLLSolver.dpll(formula + [[-literal]])
    #     if sat:
    #         return True
    #     return False

    # def solve(self):
    #     self.dpll_1(self.clauses)
    #     with Pool(16) as p:
    #         result = p.map(DPLLSolver.dpll,self.formula_stack)
    #     return (any(result))
    # def solve(self):
    #     return DPLLSolver.dpll(self.clauses)


# if __name__ == "__main__":
#     import sys
#     if len(sys.argv) != 3:
#         print("Usage: python parallel_dpll.py <input_file_path> <output_file_path>")
#         sys.exit(1)

#     input_file_path = sys.argv[1]
#     solver = DPLLSolver(input_file_path)
#     sat = solver.solve()
    
#     # Write the output to a text file
#     output_file_path = sys.argv[2]
#     with open(output_file_path, "w") as file:
#         file.write(f"Satisfiable: {sat}\n")
#     print(f"Output written to {output_file_path}")