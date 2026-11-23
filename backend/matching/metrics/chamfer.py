"""Directed Chamfer: how much of the job the CV covers (job -> CV)."""


def chamfer(matrix):
    """Matrix (rows = job requirements) -> (score 0-100 or None, best per row).

    best per row = (value, column index of the best CV skill, or None if value is 0).
    Extra CV skills never lower the score. No requirements -> score None.
    """
    best = []
    for row in matrix:
        value = max(row) if row else 0.0
        column = row.index(value) if value > 0 else None
        best.append((value, column))

    if not best:
        return None, []

    score = sum(value for value, _ in best) / len(best) * 100
    return round(score, 1), best
