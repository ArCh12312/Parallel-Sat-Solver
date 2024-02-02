def parse_dimacs_cnf(file_path):
    clauses = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('c') or line.startswith('p') or line.startswith('%') or line.startswith('0'):
                continue
            clause = [int(x) for x in line.strip().split() if x != '0']
            if clause:
                clauses.append(clause)
    return clauses

def read_assignment_from_file(file_path):
    with open(file_path, 'r') as file:
        assignment_str = file.read().strip()
    return assignment_str

def parse_assignment(assignment_str):
    # Split the input string by newline to separate the satisfiable part and the model
    parts = assignment_str.strip().split('\n')
    # Extract the model part (assuming it's the second line)
    model_str = parts[1].strip()
    # Remove the "Model: " part and the square brackets
    literals_str = model_str[len("Model: ["):-1]
    # Split by commas and convert to integers
    literals = [int(x) for x in literals_str.split(',') if x.strip()]  # Filter out empty strings
    return set(literals)

def verify(formula, literals):
    for literal in literals:
        formula = [clause for clause in formula if literal not in clause]
        formula = [[lit for lit in clause if lit != -literal] for clause in formula]
        if  any(clause == [] for clause in formula):
            print("empty clause present")
            return False
    print("all literals exhausted")
    print(formula)
    if not formula:
        return True
    return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python sat_verifier.py <input_file_path> <output_file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    assignment_file_path = sys.argv[2]
    clauses = parse_dimacs_cnf(file_path)
    assignment_str = read_assignment_from_file(assignment_file_path)
    assignment = parse_assignment(assignment_str)
    result = verify(clauses, assignment)

    print("Satisfiable" if result else "Not satisfiable")
