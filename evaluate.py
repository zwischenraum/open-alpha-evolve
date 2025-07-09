from candidate import get_magic_number


def evaluate():
    score = -abs(42 - get_magic_number())
    return {"average_score": score}
