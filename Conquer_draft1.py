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
        self.solution = None

    def read_cube(self, cube):
        # Read the cube given by the Look-ahead solver and initialize clauses, num_vars, and num_clauses
        self.clauses = cube[0]
        unique_variables = set()
        for clause in self.clauses:
            for variable in clause:
                unique_variables.add(abs(variable))
        self.num_vars = len(unique_variables)
        self.num_clauses = len(self.clauses)
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

    def vsids_decide(self, model):
        # Choose a variable based on VSIDS heuristic
        max=0
        var=0
        for literal in self.counter:
            if self.counter[literal]>max and literal not in model and -literal not in model:
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
    
    def two_watch_propagate(self, literal, model):
        # Perform 2-literal watch propagation
        propagation_queue = [literal]
        while propagation_queue:
            literal = propagation_queue.pop()
            for clause_index in reversed(self.literal_watch[-literal]):
                clause = self.clauses[clause_index]
                watched_literal_1 = self.clauses_literal_watched[clause_index][0]
                watched_literal_2 = self.clauses_literal_watched[clause_index][1]
                # Case that the clause is satisfied
                if watched_literal_1 in model or watched_literal_2 in model:  # If one of the watched literals is already true
                    continue  # Skip to the next watched clause
                unassigned_literals = [new_literal for new_literal in clause if -new_literal not in model]
                if len(unassigned_literals) == 1:
                    if unassigned_literals[0] not in model:
                        propagation_queue.append(unassigned_literals[0])
                        model.append(unassigned_literals[0])
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

    def random_restart(self, model):
        # Perform random restarts with decaying probability
        if random.random() < self.probability:  # If the generated random probability is less than the current probability
            model = self.back[:]
            self.decide_pos = []  # Clear the decision position list
            self.probability *= 0.5  # Decay the probability by 50%
            self.restart_count += 1  # Increment the restart count
            if self.probability < 0.001:  # Ensure minimum probability
                self.probability = 0.2
            if self.restart_count > len(model) + 10:  # Avoid excessive restarts
                self.probability = 0
        return
    
    def analyze_conflict(self, model, conflict_clause):
        # Analyze conflict and generate a learned clause
        learn = []
        for x in self.decide_pos:
            learn.append(-model[x])
        return learn

    def backjump(self, model): ### Change this to use dec_level
        self.imp_count += len(model) - len(self.decide_pos)
        # Perform backjumping to a decision level
        if not self.decide_pos:
            return -1,-1
        dec_level = self.decide_pos.pop()
        literal = model[dec_level]
        del model[dec_level:]
        return 0,-literal

    def all_vars_assigned(self, model):        # Returns True if all variables already assigne , False otherwise
        return len(model) >= self.num_vars
    
    def assign(self,literal,model):             # Adds the decision literal to M and correponding update to decision level
        self.decide_pos.append(len(model))
        model.append(literal)
        return model

    def add_learned_clause(self, model, learned_clause):
        self.learned_count += 1
        if len(learned_clause) == 0:
            return
        if len(learned_clause) == 1:
            model.append(learned_clause[0])
            return 1, learned_clause[0]
        self.clauses_literal_watched.append([learned_clause[0],learned_clause[1]])
        self.literal_watch[learned_clause[0]].append(self.num_clauses)
        self.literal_watch[learned_clause[1]].append(self.num_clauses)
        self.clauses.append(learned_clause)
        return 


    def solve(self, cube):
        # Solve the CNF formula using CDCL algorithm
        self.read_cube(cube)
        model = []
        self.vsids_init()
        self.init_watch_list()
        while not self.all_vars_assigned(model):
            literal = self.vsids_decide(model)
            self.decide_count += 1
            model = self.assign(literal, model)
            conflict_clause = self.two_watch_propagate(literal, model)

            while conflict_clause is not None:
                self.vsids_conflict(conflict_clause)
                learned_clause = self.analyze_conflict(model, conflict_clause)
                self.add_learned_clause(model, learned_clause)
                status, unit = self.backjump(model) 
            
                if status == -1:
                    return -1, self.restart_count, self.decide_count, self.imp_count, self.learned_count
                
                model.append(unit)
                self.random_restart(model)
                conflict_clause = self.two_watch_propagate(literal, model)
        
        return model, self.restart_count, self.decide_count, self.imp_count, self.learned_count

    def verify_solution(self, model):
        # Verify the solution
        for clause in self.clauses :                   # for each clause
            flag = False
            for literal in clause:
                if literal in model:                 # atleast one literal should be true
                    flag = True
                    break
            if not flag:
                return False
        return True

def write_solution_to_file(self, filename):
    # Write the solution to a file
    pass

def print_statistics(self):
    # Print statistics about solving process
    pass

# def main(cube):
    # Main method to read CNF, solve, and print results
    # solver = CDCLSolver()
    # solver.read_cube(cube)
    # start_time = time.time()
    # solution = solver.solve()
    # end_time = time.time()

#     if solution == -1:
#         print("No solution found.")
#     else:
#         print("Solution found:", solution)
#         # solver.write_solution_to_file("solution.cnf")
#         print("Solution verification result:", solver.verify_solution(solution))
    
#     # solver.print_statistics()
#     print("Time taken:", end_time - start_time, "seconds")

# # Example usage:
# if __name__ == "__main__":
#     main(cube = [[[-4, -16, 12], [8, 2, 14], [-9, -19, 14], [7, 4, 18], [-19, -16, 5], [-1, -16], [12, 8, -14], [-1, -2, -3], [-8, 5], [4, 10, 12], [7, 10, 3], [4, 18, 13], [-2, -9, 20], [2, -5, 19], [-8, -13, 20], [-9, 8, 13], [2, -14, -7], [3, 16], [-2, 13], [-18, -13, 16], [-18, 1, -16], [18, 2, 14], [19, 3, -14], [18, -1, 12], [18, -2, -4], [5, 13, -20], [19, -12], [12, 2, -7], [3, 5, -19], [3, 13, -10], [1, 8], [-18, -14, -3], [7, 5, -14], [13, 19, -12], [-12, -7, -3], [9, 7, -19], [20, -1, -4], [-18, 1, 5], [9, 18, 14], [-3, 9], [14, 12, 9], [5, 14, 2], [-10, -8], [14, 9], [-20, 13], [-8, 19, 7], [-7, 3, -1], [-18, 10], [12, -4, 14], [7, 10, 19], [10, -9, 3], [12, 1, -13], [16, -2, -1]], [15, -11, -17, 6]])
