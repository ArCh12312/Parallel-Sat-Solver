#include <iostream>
#include <sstream>
#include <fstream>
#include <vector>
#include <string>
#include <stack>
#include <set>
#include <utility>
#include <algorithm>

class DPLL_Solver {
public:

    struct Model {
        std::set<int> literals; // Set to hold the current assignments (model)
    };

    // Model to hold the current assignments
    Model model;

    // Stack to hold models during recursion or backtracking
    std::stack<Model> model_stack;

    std::pair<bool, Model> solve(const std::string& filename) {
        Formula formula = readDimacsCnf(filename);
        model_stack.push({});
        bool isSatisfiable = DPLL(formula);
        return {isSatisfiable, model};
    }

private:
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

    Clause findUnitClause(const Formula& formula) {
        for (const auto& clause : formula.clauses) {
            if (clause.literals.size() == 1) {
                return clause; // Found a unit clause
            }
        }
        return {}; // Return an empty clause if no unit clause is found
    }

    void unitPropagate(Formula& formula) {
        while (true) {
            Clause unitClause = findUnitClause(formula);
            if (unitClause.literals.empty()) {
                break; // No unit clause found
            }

            int unitLiteral = unitClause.literals[0];

            formula.clauses.erase(
                std::remove_if(
                    formula.clauses.begin(), formula.clauses.end(),
                    [unitLiteral](const Clause& clause) {
                        return std::find(clause.literals.begin(), clause.literals.end(), unitLiteral) != clause.literals.end();
                    }
                ),
                formula.clauses.end()
            );

            for (auto& clause : formula.clauses) {
                clause.literals.erase(
                    std::remove(clause.literals.begin(), clause.literals.end(), -unitLiteral),
                    clause.literals.end()
                );
            }
            // Add the unit clause's literal to the model
            model.literals.insert(unitLiteral);
        }
    }

    int chooseLiteral(const Formula& formula) {
        if (!formula.clauses.empty() && !formula.clauses[0].literals.empty()) {
            return formula.clauses[0].literals[0];
        } else {
            std::cerr << "Error: No literals available to choose from." << std::endl;
            return 0;
        }
    }

    bool DPLL(Formula& formula) {
        unitPropagate(formula);
        if (formula.clauses.empty()) {
            return true; 
        }
        for (const auto& clause : formula.clauses) {
            if (clause.literals.empty()) {
                return false; 
            }
        }
        int literal = chooseLiteral(formula);

        // Push the current model onto the stack before making recursive calls
        model_stack.push(model);

        Formula formulaWithLiteral = formula;
        formulaWithLiteral.clauses.push_back({{literal}});
        if (DPLL(formulaWithLiteral)) {
            return true;
        }

        // Backtrack: revert to the previous model
        model = model_stack.top();
        model_stack.pop();

        Formula formulaWithNegatedLiteral = formula;
        formulaWithNegatedLiteral.clauses.push_back({{-literal}});
        if (DPLL(formulaWithNegatedLiteral)) {
            return true;
        }
        
        // Backtrack: revert to the previous model
        model = model_stack.top();
        model_stack.pop();

        return false; // Neither assignment led to a solution
    }
};

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " [DIMACS file]" << std::endl;
        return 1;
    }

    DPLL_Solver solver;
    auto result = solver.solve(argv[1]);
    if (result.first) {
        std::cout << "SATISFIABLE" << std::endl;
        std::cout << "Model: ";
        for (const auto& lit : result.second.literals) {
            std::cout << lit << " ";
        }
        std::cout << std::endl;
    } else {
        std::cout << "UNSATISFIABLE" << std::endl;
    }

    return 0;
}