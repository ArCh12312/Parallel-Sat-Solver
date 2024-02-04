#include <iostream>
#include <sstream>
#include <fstream>
#include <vector>
#include <string>
#include <algorithm>

struct Literal {
    int value; // Literal value (positive or negative integer)
};

struct Clause {
    std::vector<int> literals; // A clause is a disjunction of literals
};

struct Formula {
    std::vector<Clause> clauses;
};

Formula readDimacsCnf(const std::string& filename) {
    std::ifstream file(filename);
    std::string line;
    Formula formula;

    if (!file.is_open()) {
        std::cerr << "Unable to open file." << std::endl;
        return formula;
    }

    while (getline(file, line)) {
        if (line.empty() || line[0] == 'c') continue; // Skip comments and empty lines
        if (line[0] == 'p') {
            // Parse problem line here (if needed)
        } else {
            std::istringstream iss(line);
            int lit;
            Clause clause;
            while (iss >> lit && lit != 0) {
                clause.literals.push_back(lit);
            }
            formula.clauses.push_back(clause);
        }
    }

    file.close();
    return formula;
}

// Function to print the formula
void printFormula(const Formula& formula) {
    std::cout << "Formula:" << std::endl;
    for (const auto& clause : formula.clauses) {
        std::cout << "(";
        for (size_t i = 0; i < clause.literals.size(); ++i) {
            std::cout << clause.literals[i];
            if (i < clause.literals.size() - 1) {
                std::cout << " \\/ "; // 'V' represents the logical OR
            }
        }
        std::cout << ")";
        if (&clause != &formula.clauses.back()) {
            std::cout << " /\\ "; // '^' represents the logical AND
        }
    }
    std::cout << std::endl;
}

// Function to find a unit clause
Clause findUnitClause(const Formula& formula) {
    for (const auto& clause : formula.clauses) {
        if (clause.literals.size() == 1) {
            return clause; // Found a unit clause
        }
    }
    return {}; // Return an empty clause if no unit clause is found
}

// Function to apply unit propagation, now takes a reference to Formula
void unitPropagate(Formula& formula) {
    while (true) {
        Clause unitClause = findUnitClause(formula);
        if (unitClause.literals.empty()) {
            break; // No unit clause found
        }

        int unitLiteral = unitClause.literals[0];

        // Remove clauses satisfied by the unit literal
        formula.clauses.erase(
            std::remove_if(
                formula.clauses.begin(), formula.clauses.end(),
                [unitLiteral](const Clause& clause) {
                    return std::find(clause.literals.begin(), clause.literals.end(), unitLiteral) != clause.literals.end();
                }
            ),
            formula.clauses.end()
        );

        // Remove the negation of the unit literal from all clauses
        for (auto& clause : formula.clauses) {
            clause.literals.erase(
                std::remove(clause.literals.begin(), clause.literals.end(), -unitLiteral),
                clause.literals.end()
            );
        }
    }
}

int chooseLiteral(const Formula& formula) {
    if (!formula.clauses.empty() && !formula.clauses[0].literals.empty()) {
        return formula.clauses[0].literals[0];
    } else {
        // Handle the case where there are no clauses or no literals in the first clause
        // This could be an error or a special value indicating an empty formula
        std::cerr << "Error: No literals available to choose from." << std::endl;
        return 0; // Return a special value, or handle this scenario as needed
    }
}

bool DPLL(Formula& formula) {
    unitPropagate(formula);
    if (formula.clauses.empty()) {
        return true; 
    }
    for (const auto& clause : formula.clauses) {
        if (clause.literals.empty()) {
            return false; // Contains an empty clause
        }
    }
    int literal = chooseLiteral(formula);
    // Try assigning the literal to true
    Formula formulaWithLiteral = formula;
    formulaWithLiteral.clauses.push_back({{literal}});
    if (DPLL(formulaWithLiteral)) {
        return true;
    }
    // Try assigning the literal to false
    Formula formulaWithNegatedLiteral = formula;
    formulaWithNegatedLiteral.clauses.push_back({{-literal}});
    if (DPLL(formulaWithNegatedLiteral)) {
        return true;
    }

    return false; // Neither assignment led to a solution
}

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " [DIMACS file]" << std::endl;
        return 1;
    }

    Formula formula = readDimacsCnf(argv[1]);
    // printFormula(formula);
    if (DPLL(formula)) {
        std::cout << "SATISFIABLE" << std::endl;
        // Output the satisfying assignment if needed
    } else {
        std::cout << "UNSATISFIABLE" << std::endl;
    }

    return 0;
}