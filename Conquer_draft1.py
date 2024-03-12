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
        self.probability = 1.0
        self.restart_count = 0
        self.imp_count = 0
        self.decide_count = 0
        self.learned_count = 0
        self.decide_pos = []
        self.back = []
        self.model = []
        self.solution = None

    def read_cube(self, clauses, cube):
        # Read the cube given by the Look-ahead solver and initialize clauses, num_vars, and num_clauses
        for literal in cube:
            self.clauses.append([literal])
        self.clauses += clauses
        unique_variables = set()
        for clause in self.clauses:
            for variable in clause:
                unique_variables.add(abs(variable))
        self.num_vars = len(unique_variables)
        self.num_clauses = len(self.clauses)
        return
    
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


    def solve(self, clauses, cube):
        # Solve the CNF formula using CDCL algorithm
        self.read_cube(clauses, cube)
        self.unit_propagate()
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

def main(clauses, cube):
    # Main method to read CNF, solve, and print results
    solver = CDCLSolver()
    # solver.read_cube(cube)
    start_time = time.time()
    model, restart_count, decide_count, imp_count, learned_count = solver.solve(clauses, cube)
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
    main(clauses = [[-15, -13, 17], [-19, -4, -16], [-8, -18, -5], [-10, -15, -18], [-13, 20, 5], [-19, -3, -16], [16, -19, -14], [17, 12, -7], [-1, -6, 12], [-12, -5, -20], [-3, 10, -15], [15, -3, -6], [20, -8, 14], [-2, 14, 7], [-18, -19, 11], [-16, -20, -11], [3, -14, -17], [-6, 16, -1], [1, -2, -8], [14, 12, 4], [-5, 9, 15], [18, -2, -5], [-12, -13, -18], [-12, 15, -19], [-12, 20, -3], [-20, 14, 1], [2, -6, 10], [5, -3, -19], [-14, 5, -6], [4, 15, 14], [-18, 8, 15], [-7, -4, -8], [2, -15, -1], [-12, 11, 18], [10, -5, 15], [-5, 8, -12], [2, 12, 17], [8, 9, -2], [-2, -1, 9], [-1, 7, 15], [-19, -15, -14], [-4, 16, -11], [7, -13, 9], [3, -16, 15], [3, 20, -18], [-4, -18, 7], [-13, 8, -10], [-11, 12, -5], [-14, -3, 6], [-19, 14, -9], [-13, 6, 11], [-10, 16, -20], [-5, -12, -1], [9, -2, 17], [-4, -10, 15], [-13, 18, 19], [-2, 17, -1], [15, -14, 17], [19, 14, 4], [7, -19, -4], [-19, 8, -10], [-12, -5, -18], [-9, 13, -5], [-17, 20, 16], [-6, -8, 12], [-5, 8, -20], [-18, -20, -5], [-2, -12, 18], [-16, 17, 5], [-1, 13, -16], [1, -15, 8], [4, 17, -19], [-15, -8, -19], [-9, 2, 15], [-7, 1, -17], [1, -2, 20], [-9, 11, 3], [-6, 8, -1], [-7, -4, 1], [3, -13, -4], [4, 16, -15], [16, 1, 3], [12, -8, -6], [-16, -19, -4], [3, 18, 10], [-2, -4, 19], [-16, -7, 8], [2, -5, 16], [7, 9, 11], [-8, -20, -16], [-15, -3, 17]], 
         cube = [-19, -2, -13])
