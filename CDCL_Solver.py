import os
import time
import random

class CDCLSolver:
    def __init__(self):
        self.clauses = []
        self.num_vars = 0
        self.num_clauses = 0
        self.counter = {}
        self.literal_watch = {}
        self.clauses_literal_watched = []
        self.probability = 0.9
        self.restart_count = 0
        self.imp_count = 0
        self.decide_count = 0
        self.learned_count = 0
        self.decide_pos = []
        self.back = []
        self.model = []
        self.solution = None

    def read_dimacs_cnf(self, file_path):
        with open(file_path, 'r') as file:
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
    
    def find_unit_clause(self):
        for clause in self.clauses:
            if len(clause) == 1:
                return clause[0]
        return 0

    def unit_propagate(self):
        unit_clause = self.find_unit_clause()
        while unit_clause != 0:
            new_unit_clause = 0
            new_formula = []
            for clause in self.clauses:
                if unit_clause in clause:
                    continue
                elif -unit_clause in clause:
                    clause = [lit for lit in clause if lit != -unit_clause]
                if clause == []:
                    return [[]], []
                if len(clause) == 1:
                    new_unit_clause = clause[0]
                new_formula.append(clause)
            self.clauses = new_formula
            if unit_clause not in self.model:
                self.model.append(unit_clause)
            unit_clause = new_unit_clause
        return
    
    def pure_literal_elimination(self):
        while True:
            literals = {literal for clause in self.clauses for literal in clause}
            pure_literals = {literal for literal in literals if -literal not in literals}
            if not pure_literals:
                break
            for literal in pure_literals:
                if literal not in self.model:
                    self.model.append(literal)
            self.clauses = [clause for clause in self.clauses if not any(literal in clause for literal in pure_literals)]
        return 

    def vsids_init(self):
        # Initialize VSIDS counter for literals
        for clause in self.clauses:
            for literal in clause:
                if literal in self.counter:
                    self.counter[literal] += 1
                    continue
                self.counter[literal] = 1
        return

    def vsids_conflict(self, conflict_clause):
        # Increment counter for literals in the conflict clause
        for literal in conflict_clause:
            self.counter[literal]+=1
        return

    def vsids_decay(self):
        # Decay counter for literals at each conflict
        for literal in self.counter:
            self.counter[literal] *= .95
        return

    def vsids_decide(self):
        # Choose a variable based on VSIDS heuristic
        max=0
        var=0
        for literal in self.counter:
            if self.counter[literal]>max and literal not in self.model and -literal not in self.model:
                    max=self.counter[literal]
                    var=literal
        return var

    def init_watch_list(self):
        # Initialise the literal watch dictionary
        for literal in self.counter:
            self.literal_watch[literal] = []

        # Populate the watch lists
        for i, clause in enumerate(self.clauses):
            watched_literals = []
            for literal in clause:
                watched_literals.append(literal)
                if len(watched_literals) == 2:
                    break
            self.clauses_literal_watched.append(watched_literals)
            for watched_literal in watched_literals:
                self.literal_watch[watched_literal].append(i)

        return
    
    def two_watch_propagate(self, literal):
        # Perform 2-literal watch propagation
        propagation_queue = [literal]
        while propagation_queue:
            literal = propagation_queue.pop()
            for clause_index in reversed(self.literal_watch[-literal]):
                clause = self.clauses[clause_index]
                watched_literal_1 = self.clauses_literal_watched[clause_index][0]
                watched_literal_2 = self.clauses_literal_watched[clause_index][1]
                # Case that the clause is satisfied
                if watched_literal_1 in self.model or watched_literal_2 in self.model:  # If one of the watched literals is already true
                    continue  # Skip to the next watched clause
                unassigned_literals = [new_literal for new_literal in clause if -new_literal not in self.model]
                if len(unassigned_literals) == 1:
                    if unassigned_literals[0] not in self.model:
                        propagation_queue.append(unassigned_literals[0])
                        self.model.append(unassigned_literals[0])
                        continue
                    new_literal = watched_literal_1 if watched_literal_1 != -literal else watched_literal_2
                    unassigned_literals.append(new_literal)
                # Conflict detection: if no unassigned literals, return the conflicting clause
                if not unassigned_literals:
                    return clause
                # Update watched literals and their corresponding clauses
                self.literal_watch [watched_literal_1].remove(clause_index)
                self.literal_watch [watched_literal_2].remove(clause_index)
                self.clauses_literal_watched[clause_index] = unassigned_literals
                self.literal_watch [unassigned_literals[0]].append(clause_index)
                self.literal_watch [unassigned_literals[1]].append(clause_index)
        return None # No conflict Detected

    def random_restart(self):
        # Perform random restarts with decaying probability
        if random.random() < self.probability:  # If the generated random probability is less than the current probability
            self.model = self.back[:]
            self.decide_pos = []  # Clear the decision position list
            self.probability *= 0.5  # Decay the probability by 50%
            self.restart_count += 1  # Increment the restart count
            if self.probability < 0.001:  # Ensure minimum probability
                self.probability = 0.2
            if self.restart_count > len(self.model) + 10:  # Avoid excessive restarts
                self.probability = 0
        return
    
    def analyze_conflict(self):
        # Analyze conflict and generate a learned clause
        learn = []
        for x in self.decide_pos:
            learn.append(-self.model[x])
        return learn

    def backjump(self): ### Change this to use dec_level
        self.imp_count += len(self.model) - len(self.decide_pos)
        # Perform backjumping to a decision level
        if not self.decide_pos:
            return -1,-1
        dec_level = self.decide_pos.pop()
        literal = self.model[dec_level]
        del self.model[dec_level:]
        return 0,-literal

    def all_vars_assigned(self):        # Returns True if all variables already assigne , False otherwise
        return len(self.model) >= self.num_vars
    
    def assign(self,literal):             # Adds the decision literal to M and correponding update to decision level
        self.decide_pos.append(len(self.model))
        self.model.append(literal)
        return

    def add_learned_clause(self, learned_clause):
        self.learned_count += 1
        if len(learned_clause) == 0:
            return
        if len(learned_clause) == 1:
            self.model.append(learned_clause[0])
            self.clauses_literal_watched.append([learned_clause[0]])
            self.literal_watch[learned_clause[0]].append(self.num_clauses)
            self.clauses.append(learned_clause)
            return
        self.clauses_literal_watched.append([learned_clause[0],learned_clause[1]])
        self.literal_watch[learned_clause[0]].append(self.num_clauses)
        self.literal_watch[learned_clause[1]].append(self.num_clauses)
        self.clauses.append(learned_clause)
        return 


    def solve(self, input_file_path):
        # Solve the CNF formula using CDCL algorithm
        self.read_dimacs_cnf(input_file_path)
        self.unit_propagate()
        self.pure_literal_elimination()
        if self.clauses == []:
            print("solved!")
            return self.model, self.restart_count, self.decide_count, self.imp_count, self.learned_count
        if self.clauses == [[]]:
            return -1, self.restart_count, self.decide_count, self.imp_count, self.learned_count
        self.back = self.model[:]
        self.num_clauses = len(self.clauses)
        self.vsids_init()
        self.init_watch_list()
        while not self.all_vars_assigned():
            literal = self.vsids_decide()
            self.decide_count += 1
            self.assign(literal)
            conflict_clause = self.two_watch_propagate(literal)

            while conflict_clause is not None:
                self.vsids_conflict(conflict_clause)
                self.vsids_decay()
                learned_clause = self.analyze_conflict()
                self.add_learned_clause(learned_clause)
                status, unit = self.backjump() 
            
                if status == -1:
                    return -1, self.restart_count, self.decide_count, self.imp_count, self.learned_count
                
                self.model.append(unit)
                self.random_restart()
                conflict_clause = self.two_watch_propagate(unit)
        
        return self.model, self.restart_count, self.decide_count, self.imp_count, self.learned_count

    def verify_solution(self, model):
        # Verify the solution
        for clause in self.clauses :                   # for each clause
            flag = False
            for literal in clause:
                if literal in model:                 # atleast one literal should be true
                    flag = True
                    break
            if not flag:
                print(clause)
                return False
        return True

def write_solution_to_file(self, filename):
    # Write the solution to a file
    pass

def print_statistics(self):
    # Print statistics about solving process
    pass

def main(input_file_path):
    # Main method to read CNF, solve, and print results
    solver = CDCLSolver()
    start_time = time.time()
    model, restart_count, decide_count, imp_count, learned_count = solver.solve(input_file_path)
    end_time = time.time()

    if model == -1:
        print("No solution found.")
    else:
        print("Solution found:", model)
        # solver.write_solution_to_file("solution.cnf")
        print("Assignment verification result:", solver.verify_solution(model))
    print()
    print("Statistics :")
    print("=============================================")
    print(f"# Restarts : {restart_count}")
    print(f"# Learned Clauses : {learned_count}")
    print(f"# Decisions : {decide_count}")
    print(f"# Implications : {imp_count}")
    print("=============================================")
    
    # solver.print_statistics()
    print("Time taken:", end_time - start_time, "seconds")

# Example usage:
if __name__ == "__main__":
    # input_file_path = input("Enter input file path: ")
    input_file_path = "./tests/UF250.1065.100/uf250-01.cnf"
    main(input_file_path)
