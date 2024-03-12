# from multiprocessing import Process, Pool, cpu_count, Manager, Value, Lock
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
from queue import PriorityQueue, Queue
import sys
import time

# Create ThreadPoolExecutor for I/O-bound tasks
thread_executor = ThreadPoolExecutor(max_workers=cpu_count())

# executor = ProcessPoolExecutor(max_workers=cpu_count())

    # def __init__(self, file_path):
    #     self.file_path = file_path
    #     self.clauses = []
    #     self.num_vars = 0
    #     self.num_clauses = 0
    #     self.formula_queue = Queue()
    #     self.executor = ThreadPoolExecutor(max_workers=cpu_count())
    #     self.read_dimacs_cnf()

def read_dimacs_cnf(file_path):
    with open(file_path, 'r') as file:
        clauses = []
        for line in file:
            if line.startswith('c') or line.startswith('0') or line.startswith('%'):
                continue
            elif line.startswith('p'):
                _, _, num_vars, num_clauses = line.split()
                num_vars, num_clauses = int(num_vars), int(num_clauses)
            else:
                clause = [int(x) for x in line.split() if x != '0']
                if clause:
                    clauses.append(clause)
    return num_vars, num_clauses, clauses

def find_unit_clause(formula):
    for clause in formula:
        if len(clause) == 1:
            return clause[0]
    return 0
                    
def unit_propagate(formula, model):
    unit_clause = find_unit_clause(formula)
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

def select_literal(formula, method="first"):
    if method == "first":
        return formula[0][0]

def dpll(formula, model = [], depth = 0):
    formula, model = unit_propagate(formula, model)
    if formula == []:
        return True, model
    if formula == [[]]:
        return False, []
    literal = select_literal(formula)
    if depth == 3:
        cubes.append(formula+[[literal]], model)
        cubes.append(formula + [[-literal]], model)
        
    pos_formula = formula + [[literal]]
    neg_formula = formula + [[-literal]]
    pos_model = model[:]
    neg_model = model[:]

    sat_pos, pos_model = dpll(pos_formula, pos_model)
    if sat_pos:
        return True, model
    
    sat_neg, neg_model = dpll(neg_formula, neg_model)
    if sat_neg:
        return True, model
    
    return False, []
        
def solve(clauses):
    return dpll(clauses)

def main():

    input_file_path = "./tests/uf20-91/uf20-099.cnf"
    num_vars, num_clauses, clauses = read_dimacs_cnf(input_file_path)
    start = time.time()
    sat, model = solve(clauses)
    end = time.time()
    
    # Write the output to a text file
    output_file_path = "./dpll_output.txt"
    with open(output_file_path, "w") as file:
        file.write(f"Satisfiable: {sat}\n")
        file.write(f"Model: {model}\n")
    print(f"Output written to {output_file_path}")
    print(f"Solving time: {end-start}seconds")

if  __name__ == '__main__':
    main()