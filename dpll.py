def read_dimacs_cnf(file_path):
    clauses = []
    num_vars = 0
    num_clauses = 0

    with open(file_path, 'r') as file:
        for line in file:
            # Ignore comments
            if line.startswith('c') or line.startswith('0') or line.startswith('%'):
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

def find_unit_clause(formula):
    for clause in formula:
        if len(clause) == 1:
            return clause
    return None

def unit_propagate(formula, model):
    while True:
        unit_clause = find_unit_clause(formula)
        if not unit_clause:
            break

        unit_clause = unit_clause[0]  # Get the literal in the unit clause
        formula = [clause for clause in formula if unit_clause not in clause]
        formula = [[lit for lit in clause if lit != -unit_clause] for clause in formula]
        
        if unit_clause not in model:
            model.append(unit_clause)
    return formula, model

def pure_literal_elimination(formula, model):
    while True:
        literals = {literal for clause in formula for literal in clause} # Collect all literals from the formula
        pure_literals = {literal for literal in literals if -literal not in literals} # Identify pure literals
        if not pure_literals:
            break
        for literal in pure_literals: # Add pure literals to the model if not already present
            if literal not in model:
                model.append(literal)
        # Eliminate clauses containing pure literals
        formula = [clause for clause in formula if not any(literal in clause for literal in pure_literals)]
    return formula, model

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
        return False, []
    literal = select_literal(formula, method="first")
    # Try assigning the literal to True
    new_model = model[:]
    sat, updated_model = dpll(formula + [[literal]], new_model)
    if sat:
        return True, updated_model
    # Try assigning the literal to False
    new_model = model[:]
    sat, updated_model = dpll(formula + [[-literal]], new_model)
    if sat:
        return True, updated_model
    
    return False, []

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python dpll.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    _, _, clauses = read_dimacs_cnf(file_path)
    sat, model = dpll(clauses)
    print(sat, model)

# if __name__ == "__main__":
#     file_path = './input1.cnf'
#     num_vars, num_clauses, clauses = read_dimacs_cnf(file_path)
#     print("Number of Variables:", num_vars)
#     print("Number of Clauses:", num_clauses)
#     print("Clauses:", clauses)

#     sat, model = dpll(clauses)
#     if sat:
#         print("Satisfiable", model)
#     else:
#         print("Unsatisfiable")
