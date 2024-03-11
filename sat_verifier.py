class SatVerifier:
    def __init__(self):
        pass

    def verify_solution(self, clauses, model):
        # Verify the solution
        for clause in clauses:
            flag = False
            for literal in clause:
                if literal in model:  # At least one literal should be true
                    flag = True
                    break
            if not flag:
                return False
        return True