#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <cstdlib>
#include <algorithm>
#include <set>
#include <optional>

class DPLLSolver {
private:
    std::string file_path;
    std::vector<std::vector<int>> clauses;
    int num_vars;
    int num_clauses;
    std::string method;

    void read_dimacs_cnf() {
        std::ifstream file(file_path);
        std::string line;

        if (!file.is_open()) {
            throw std::runtime_error("Cannot open file: " + file_path);
        }

        while (std::getline(file, line)) {
            std::istringstream iss(line);
            char first_char;
            iss >> first_char;

            if (first_char == 'c') {
                continue; // Comment line, skip it
            } else if (first_char == 'p') {
                std::string cnf;
                iss >> cnf >> num_vars >> num_clauses;
            } else {
                std::vector<int> clause;
                int var;
                while (iss >> var && var != 0) {
                    clause.push_back(var);
                }
                if (!clause.empty()) {
                    clauses.push_back(clause);
                }
            }
        }
        file.close();
    }

    static int find_unit_clause(const std::vector<std::vector<int>>& formula) {
        for (const auto& clause : formula) {
            if (clause.size() == 1) {
                return clause[0];
            }
        }
        return 0;
    }

    static std::pair<std::vector<std::vector<int>>, std::vector<int>> unit_propagate(std::vector<std::vector<int>> formula, std::vector<int> model) {
        while (true) {
            int unit_clause = find_unit_clause(formula);
            if (unit_clause == 0) break;
            formula.erase(std::remove_if(formula.begin(), formula.end(), [unit_clause](const std::vector<int>& clause) { return std::find(clause.begin(), clause.end(), unit_clause) != clause.end(); }), formula.end());
            for (auto& clause : formula) {
                clause.erase(std::remove(clause.begin(), clause.end(), -unit_clause), clause.end());
            }
            if (std::find(model.begin(), model.end(), unit_clause) == model.end()) {
                model.push_back(unit_clause);
            }
        }
        return {formula, model};
    }

    static std::pair<std::vector<std::vector<int>>, std::vector<int>> pure_literal_elimination(std::vector<std::vector<int>> formula, std::vector<int> model) {
        while (true) {
            std::set<int> literals;
            for (const auto& clause : formula) {
                literals.insert(clause.begin(), clause.end());
            }

            std::set<int> pure_literals;
            for (int lit : literals) {
                if (literals.find(-lit) == literals.end()) {
                    pure_literals.insert(lit);
                }
            }

            if (pure_literals.empty()) break;

            for (int lit : pure_literals) {
                if (std::find(model.begin(), model.end(), lit) == model.end()) {
                    model.push_back(lit);
                }
            }

            formula.erase(std::remove_if(formula.begin(), formula.end(), [&pure_literals](const std::vector<int>& clause) {
                for (int lit : clause) {
                    if (pure_literals.find(lit) != pure_literals.end()) return true;
                }
                return false;
            }), formula.end());
        }
        return {formula, model};
    }

    int select_literal(const std::vector<std::vector<int>>& formula) {
        if (method == "first") {
            return formula[0][0];
        } else if (method == "random") {
            std::set<int> literals;
            for (const auto& clause : formula) {
                for (int lit : clause) {
                    literals.insert(abs(lit));
                }
            }
            int nth = rand() % literals.size();
            auto it = literals.begin();
            std::advance(it, nth);
            return *it;
        }
        return 0; // Default return
    }

    std::pair<bool, std::vector<int>> dpll(std::vector<std::vector<int>> formula, std::vector<int> model = {}) {
        auto [propagated_formula, propagated_model] = unit_propagate(formula, model);
        auto [eliminated_formula, eliminated_model] = pure_literal_elimination(propagated_formula, propagated_model);
        if (eliminated_formula.empty()) {
            return {true, eliminated_model};
        }

        if (std::any_of(eliminated_formula.begin(), eliminated_formula.end(), [](const std::vector<int>& clause) { return clause.empty(); })) {
            return {false, {}};
        }

        int literal = select_literal(eliminated_formula);
        std::vector<int> new_model = eliminated_model;
        new_model.push_back(literal);

        auto [sat, updated_model] = dpll(eliminated_formula, new_model);
        if (sat) {
            return {true, updated_model};
        }

        new_model = eliminated_model;
        new_model.push_back(-literal);
        return dpll(eliminated_formula, new_model);
    }

public:
    DPLLSolver(std::string path, std::string meth = "first") : file_path(path), method(meth) {
        read_dimacs_cnf();
    }

    std::pair<bool, std::vector<int>> solve() {
        return dpll(clauses);
    }
};

int main(int argc, char *argv[]) {
    if (argc != 2) {
        std::cout << "Usage: " << argv[0] << " <file_path>\n";
        return 1;
    }

    std::string file_path = argv[1];
    DPLLSolver solver(file_path);
    auto [sat, model] = solver.solve();
    std::cout << (sat ? "SATISFIABLE" : "UNSATISFIABLE") << std::endl;
    if (sat) {
        for (int lit : model) {
            std::cout << lit << " ";
        }
        std::cout << std::endl;
    }
    return 0;
}
