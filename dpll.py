def read_dimacs_cnf(file_path):
    clauses = []
    num_vars = 0
    num_clauses = 0

    with open(file_path, 'r') as file:
        for line in file:
            # Ignore comments
            if line.startswith('c'):
                continue

            # Read problem line
            elif line.startswith('p'):
                _, _, num_vars, num_clauses = line.split()
                num_vars, num_clauses = int(num_vars), int(num_clauses)

            # Read clauses
            else:
                clause = [int(x) for x in line.split() if x != '0']
                if clause:  # Ignore empty lines
                    clauses.append(clause)

    return num_vars, num_clauses, clauses

def find_unit_clauses(formula):
    unit_clauses = [clause for clause in formula if len(clause) == 1]
    return unit_clauses

def unit_propagate(formula, model):
    while True:
        unit_clauses = find_unit_clauses(formula)
        if not unit_clauses:
            break

        unit_clause = unit_clauses[0][0]  # Get the literal in the unit clause
        formula = [clause for clause in formula if unit_clause not in clause]
        formula = [[lit for lit in clause if lit != -unit_clause] for clause in formula]

        if unit_clause not in model:
            model.append(unit_clause)
    return formula, model

def pure_literal_elimination(formula, model):
    literals = {literal for clause in formula for literal in clause}
    pure_literals = {literal for literal in literals if -literal not in literals}
    # Add pure literals to the model, ensuring no duplicates
    for literal in pure_literals:
        if literal not in model:
            model.append(literal)
    new_formula = [clause for clause in formula if not any(literal in clause for literal in pure_literals)]
    return new_formula, model

def select_literal(formula, method="first"):
    if method == "first":
        return formula[0][0]

def dpll(formula, model=[]):
    # Find a unit clause and propagate it
    formula, model = unit_propagate(formula, model)
    # Pure literal elimination
    formula, model = pure_literal_elimination(formula, model)
    # Check if the formula is satisfiable or unsatisfiable after simplifications
    if not formula: # Satisfiable as the formula is empty
        return True, model
    if any(len(clause) == 0 for clause in formula): # Unsatisfiable as there is an empty clause
        return False
    literal = select_literal(formula, method="first")
    # Add literal as a unit clause
    if dpll(formula+[[literal]], model[:]):
        return True, model
    elif dpll(formula+[[-literal]], model[:]):
        return True, model
    return False

if __name__ == "__main__":
    file_path = './test_example.txt'
    num_vars, num_clauses, clauses = read_dimacs_cnf(file_path)
    print("Number of Variables:", num_vars)
    print("Number of Clauses:", num_clauses)
    print("Clauses:", clauses)

    sat, model = dpll(clauses)
    if sat:
        print("Satisfiable", model)
    else:
        print("Unsatisfiable")
