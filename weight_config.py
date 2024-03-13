from Look_Ahead_Solver import Look_ahead_Solver
import itertools

# Define a range of weights to test for each factor.
weight_range = [i for i in range(1, 11, 1)]

# Generate all possible combinations of weights within the specified range.
weight_combinations = list(itertools.product(weight_range, repeat=3))

# Placeholder for storing the best weight combination and its performance.
best_combination = None
lowest_branch_count = float('inf')

def adjust_and_run_solver(weights, input_file_path):
    """
    Adjust the compute_score function according to the given weights,
    run the solver, and return the branch count.
    """
    # Adjust the weights in the compute_score function.
    # This requires modifying the Look_ahead_Solver class to accept dynamic weights,
    # possibly by passing them as parameters to the constructor or a separate method.
    # For demonstration, let's assume we have a method to set weights:
    # solver.set_weights(weights)
    
    solver = Look_ahead_Solver()
    solver.solve(input_file_path, weights)
    
    return solver.branch_count

# Loop through each weight combination to test them.
for weights in weight_combinations:
    # Assuming you have a function to set the weights for the solver,
    # and a function that runs the solver and returns the branch count.
    
    # For demonstration, let's assume a single CNF file for testing.
    # You might want to average over several files for more reliable results.
    input_file_path = "./tests/uf100-01.cnf"
    
    branch_count = adjust_and_run_solver(weights, input_file_path)
    
    # Update the best combination if the current one performs better.
    if branch_count < lowest_branch_count:
        best_combination = weights
        lowest_branch_count = branch_count

# Output the best combination found.
print(f"Best combination: {best_combination} with branch count: {lowest_branch_count}")
