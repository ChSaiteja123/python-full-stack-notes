def letter_grade(score: int) -> str:
    if not 0 <= score <= 100:
        raise ValueError("score must be between 0 and 100")
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    return "Review"


if __name__ == "__main__":
    for sample_score in (95, 84, 72, 55):
        print(f"{sample_score}: {letter_grade(sample_score)}")
