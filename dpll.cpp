#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <algorithm>
#include <cstdlib>
#include <ctime>

class DPLLSolver {
public:
    DPLLSolver(const std::string& file_path, const std::string& method = "first") 
        : file_path(file_path), method(method) {
        readDimacsCnf();
        initializeLiteralFrequency();
        frequency_stack.push_back(frequency);
    }

    std::pair<bool, std::vector<int>> solve();

private:
    std::string file_path;
    std::vector<std::vector<int>> clauses;
    int num_vars;
    int num_clauses;
    std::string method;
    std::unordered_map<int, int> frequency;
    std::vector<std::unordered_map<int, int>> frequency_stack;

    void readDimacsCnf();
    void initializeLiteralFrequency();
    void pushFrequencyState();
    void popFrequencyState();
    void updateFrequency(const std::vector<int>& clause);
    static std::vector<int> findUnitClause(const std::vector<std::vector<int>>& formula);
    std::pair<bool, std::vector<int>> unitPropagate(std::vector<std::vector<int>>& formula, std::vector<int>& model);
    int selectLiteral(const std::vector<std::vector<int>>& formula);
    std::pair<bool, std::vector<int>> dpll(std::vector<std::vector<int>> formula, std::vector<int> model);
};

void DPLLSolver::readDimacsCnf() {
    std::ifstream file(file_path);
    std::string line;
    while (getline(file, line)) {
        if (line[0] == 'c' || line[0] == '0' || line[0] == '%') continue;
        else if (line[0] == 'p') {
            sscanf(line.c_str(), "p cnf %d %d", &num_vars, &num_clauses);
        } else {
            std::istringstream iss(line);
            std::vector<int> clause;
            int num;
            while (iss >> num) {
                if (num != 0) clause.push_back(num);
            }
            if (!clause.empty()) clauses.push_back(clause);
        }
    }
}


void DPLLSolver::initializeLiteralFrequency() {
    for (const auto& clause : clauses) {
        for (int lit : clause) {
            frequency[lit]++;
        }
    }
}

void DPLLSolver::pushFrequencyState() {
    frequency_stack.push_back(frequency);
}

void DPLLSolver::popFrequencyState() {
    if (!frequency_stack.empty()) {
        frequency = frequency_stack.back();
        frequency_stack.pop_back();
    }
}

void DPLLSolver::updateFrequency(const std::vector<int>& clause) {
    for (int lit : clause) {
        if (frequency.find(lit) != frequency.end()) {
            frequency[lit]--;
            if (frequency[lit] == 0) {
                frequency.erase(lit);
            }
        }
    }
}

std::vector<int> DPLLSolver::findUnitClause(const std::vector<std::vector<int>>& formula) {
    for (const auto& clause : formula) {
        if (clause.size() == 1) {
            return clause;
        }
    }
    return std::vector<int>();
}

std::pair<bool, std::vector<int>> DPLLSolver::unitPropagate(std::vector<std::vector<int>>& formula, std::vector<int>& model) {
    while (true) {
        auto unit_clause = findUnitClause(formula);
        if (unit_clause.empty()) {
            break;
        }
        
        int unit = unit_clause[0];
        std::vector<std::vector<int>> new_formula;
        for (auto& clause : formula) {
            if (std::find(clause.begin(), clause.end(), unit) != clause.end()) {
                updateFrequency(clause);
            } else {
                new_formula.push_back(clause);
            }
        }
        formula = std::vector<std::vector<int>>();
        for (auto& clause : new_formula) {
            std::vector<int> new_clause;
            for (int lit : clause) {
                if (lit != -unit) {
                    new_clause.push_back(lit);
                }
            }
            formula.push_back(new_clause);
        }
        if (frequency.find(-unit) != frequency.end()) {
            frequency.erase(-unit);
        }
        if (std::find(model.begin(), model.end(), unit) == model.end()) {
            model.push_back(unit);
        }
    }
    return {true, model};
}

int DPLLSolver::selectLiteral(const std::vector<std::vector<int>>& formula) {
    if (method == "first") {
        return formula[0][0];
    } else if (method == "random") {
        srand(time(nullptr));
        std::unordered_set<int> literals;
        for (const auto& clause : formula) {
            for (int lit : clause) {
                literals.insert(lit);
            }
        }
        auto it = literals.begin();
        std::advance(it, rand() % literals.size());
        return *it;
    } else if (method == "mfv") {
        // Most Frequent Variable (MFV) heuristic
        return std::max_element(frequency.begin(), frequency.end(),
            [](const std::pair<int, int>& a, const std::pair<int, int>& b) {
                return a.second < b.second;
            })->first;
    }
    // Other heuristics like "moms" and "jw" can be implemented similarly.
}

std::pair<bool, std::vector<int>> DPLLSolver::dpll(std::vector<std::vector<int>> formula, std::vector<int> model) {
    auto unitPropResult = unitPropagate(formula, model);
    if (formula.empty()) {
        return {true, model};
    }
    if (std::any_of(formula.begin(), formula.end(), [](const std::vector<int>& clause) { return clause.empty(); })) {
        return {false, std::vector<int>()};
    }
    pushFrequencyState();
    int literal = selectLiteral(formula);
    std::vector<int> new_model = model;
    new_model.push_back(literal);
    std::vector<std::vector<int>> formula_with_literal = formula;
    formula_with_literal.push_back({literal});
    auto satModel = dpll(formula_with_literal, model);
    if (satModel.first) {
        return satModel;
    }
    popFrequencyState();
    pushFrequencyState();
    new_model = model;
    new_model.push_back(-literal);
    formula_with_literal = formula;
    formula_with_literal.push_back({-literal});
    satModel = dpll(formula_with_literal, model);
    if (satModel.first) {
        return satModel;
    }
    popFrequencyState();
    return {false, std::vector<int>()};
}

std::pair<bool, std::vector<int>> DPLLSolver::solve() {
    return dpll(clauses, std::vector<int>());
}

int main(int argc, char *argv[]) {
    // Command line argument handling
    if (argc != 3 && argc != 4) {
        std::cerr << "Usage: " << argv[0] << " <input_file_path> <output_file_path> [method]" << std::endl;
        return 1;
    }

    std::string input_file_path = argv[1];
    std::string output_file_path = argv[2];
    std::string method = (argc == 4) ? argv[3] : "first";

    DPLLSolver solver(input_file_path, method);
    auto result = solver.solve();

    std::ofstream output_file(output_file_path);
    output_file << "Satisfiable: " << (result.first ? "true" : "false") << "\n";
    output_file << "Model: ";
    for (int val : result.second) {
        output_file << val << " ";
    }
    output_file << "\n";
    std::cout << "Output written to " << output_file_path << std::endl;

    return 0;
}
