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

    def dpll(self, formula): ### Iterative
        formula = self.unit_propagate(formula)
        if formula == []:
            return True
        if formula == [[]]:
            return False
        literal = self.select_literal(formula)
        pos_formula = formula+[[literal]]
        neg_formula = formula+[[-literal]]
        # sat = self.dpll(formula+[[literal]])
        # if sat:
        #     return True
        # sat = self.dpll(formula+[[-literal]])
        # if sat:
        #     return True
        # return False

        # Container for results
        if literal is not None:
            pos_formula = formula + [[literal]]
            neg_formula = formula + [[-literal]]

            # Use ThreadPoolExecutor for parallelism
            with ThreadPoolExecutor(max_workers=2) as executor:
                # Submit the tasks and retrieve results
                futures = [executor.submit(self.dpll, pos_formula), executor.submit(self.dpll, neg_formula)]

                # Wait for the tasks to complete
                results = [future.result() for future in futures]

            return any(results)
        else:
            # No literal to choose, return False
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