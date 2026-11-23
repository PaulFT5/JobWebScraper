"""Minimal match report: score, best CV skill per requirement, missing requirements."""


def make_report(job_skills, cv_skills, score, best):
    """job_skills: requirement names (Jobs.required_skills order).
    cv_skills: CV skill names (matrix column order).
    score, best: output of chamfer().
    """
    requirements = []
    missing = []
    for name, (value, column) in zip(job_skills, best):
        cv_skill = cv_skills[column] if column is not None else None
        requirements.append({"requirement": name, "best_cv_skill": cv_skill, "value": value})
        if value == 0:
            missing.append(name)

    return {"score": score, "requirements": requirements, "missing": missing}
