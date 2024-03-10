import time
from CnC_draft1 import Look_ahead_Solver
from Conquer_draft1 import CDCLSolver

class Cube_and_Conquer_solver:
    def __init__(self):
        self.look_ahead_solver = Look_ahead_Solver()
        self.cdcl_solver = CDCLSolver()
        self.total_implication_count = 0
        self.total_restart_count = 0
        self.total_decide_count = 0
        self.total_learned_count = 0
        self.model = []

    def solve(self, file_path):
        cubes = self.look_ahead_solver.solve(file_path)
        for cube in cubes:
            model, restart_count, decide_count, imp_count, learned_count = self.cdcl_solver.solve(cube)
            self.total_implication_count = imp_count 
            self.total_restart_count = restart_count
            self.total_decide_count = decide_count
            self.total_learned_count = learned_count
            self.model = model
            if model == -1:
                print("Failed to solve cube.")
            else:
                return self.model,self.total_implication_count, self.total_restart_count, self.total_decide_count, self.total_learned_count
        return self.model, self.total_implication_count, self.total_restart_count, self.total_decide_count, self.total_learned_count
def print_statistics(model, imp_count, restart_count, decide_count, learned_count):
    print()
    print("Result:")
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
    file_path = input("Enter file name: ")
    solver = Cube_and_Conquer_solver()
    start = time.time()
    model, total_implication_count, total_restart_count, total_decide_count, total_learned_count = solver.solve(file_path)
    end  = time.time()
    print_statistics(model, total_implication_count, total_restart_count, total_decide_count, total_learned_count)
    print(f"Total time taken to find a solution: {end - start} seconds")

if __name__ == "__main__":
    main()