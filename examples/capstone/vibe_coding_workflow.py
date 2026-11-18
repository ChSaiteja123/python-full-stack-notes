"""Model a safe, human-reviewed vibe-coding workflow without calling an AI."""

REQUIRED_CHECKS = {
    "acceptance_criteria",
    "tests",
    "diff_review",
    "security_review",
}


def review_change(completed_checks: set[str]) -> tuple[bool, list[str]]:
    missing = sorted(REQUIRED_CHECKS - completed_checks)
    return not missing, missing


if __name__ == "__main__":
    draft_checks = {"acceptance_criteria", "tests"}
    accepted, missing = review_change(draft_checks)
    print("Decision:", "ACCEPT" if accepted else "HOLD")
    print("Still required:", ", ".join(missing) or "nothing")

    reviewed_checks = REQUIRED_CHECKS.copy()
    accepted, missing = review_change(reviewed_checks)
    print("Decision after human review:", "ACCEPT" if accepted else "HOLD")
    print("Still required:", ", ".join(missing) or "nothing")
