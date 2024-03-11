import time
from CnC_draft1 import Look_ahead_Solver
from Conquer_draft1 import CDCLSolver

class Cube_and_Conquer_solver:
    def __init__(self):
        self.look_ahead_solver = Look_ahead_Solver()
        self.cdcl_solver = CDCLSolver()
        self.clauses = []
        self.total_implication_count = 0
        self.total_restart_count = 0
        self.total_decide_count = 0
        self.total_learned_count = 0
        self.model = []

    def solve(self, file_path):
        self.clauses, cubes = self.look_ahead_solver.solve(file_path)
        for cube in cubes:
            model, restart_count, decide_count, imp_count, learned_count = self.cdcl_solver.solve(cube)
            self.total_implication_count = imp_count 
            self.total_restart_count = restart_count
            self.total_decide_count = decide_count
            self.total_learned_count = learned_count
            self.model = cube[1] + model
            if model == -1:
                print("Failed to solve cube.")
            else:
                return self.model,self.total_implication_count, self.total_restart_count, self.total_decide_count, self.total_learned_count
        return self.model, self.total_implication_count, self.total_restart_count, self.total_decide_count, self.total_learned_count

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

def print_statistics(model, imp_count, restart_count, decide_count, learned_count):
    print()
    if model == -1:
        print("Unsatisfiable")
    else:
        print(f"Model : {model}")
    print()
    print("Statistics :")
    print("=============================================")
    print(f"# Restarts : {restart_count}")
    print(f"# Learned Clauses : {learned_count}")
    print(f"# Decisions : {decide_count}")
    print(f"# Implications : {imp_count}")
    print("=============================================")

def main():
    # file_path = input("Enter file name: ")
    file_path = "./tests/uf20-91/uf20-099.cnf"
    solver = Cube_and_Conquer_solver()
    start = time.time()
    model, total_implication_count, total_restart_count, total_decide_count, total_learned_count = solver.solve(file_path)
    end  = time.time()
    verified = solver.verify_solution(model)
    if verified:
        print()
        print("Assignment verified: True")
        print_statistics(model, total_implication_count, total_restart_count, total_decide_count, total_learned_count)
    else:
        print("Assignment verified: False")
    print(f"Total time taken to find a solution: {end - start} seconds")

if __name__ == "__main__":
    main()