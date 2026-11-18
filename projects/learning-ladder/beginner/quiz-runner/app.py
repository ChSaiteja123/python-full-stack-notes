QUESTIONS = (
    ("Which type stores an ordered sequence?", "list"),
    ("Which keyword defines a function?", "def"),
)


def score_answers(answers: tuple[str, ...]) -> tuple[int, int]:
    correct = sum(
        answer.strip().lower() == expected
        for (_, expected), answer in zip(QUESTIONS, answers)
    )
    return correct, len(QUESTIONS)


if __name__ == "__main__":
    sample_answers = ("list", "def")
    correct, total = score_answers(sample_answers)
    print(f"Score: {correct}/{total}")
