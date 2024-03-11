class SatVerifier:
    def __init__(self, clauses, model):
        self.clauses = clauses
        self.model = model

    def verify_solution(self):
        # Verify the solution
        for clause in self.clauses:
            flag = False
            for literal in clause:
                if literal in self.model:  # At least one literal should be true
                    flag = True
                    break
            if not flag:
                return False
        return True