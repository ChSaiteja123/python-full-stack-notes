import json


class StudentRegistry:
    def __init__(self) -> None:
        self._students: dict[int, dict[str, object]] = {}

    def add(self, student_id: int, name: str, score: int) -> None:
        clean_name = name.strip()
        if student_id <= 0 or not clean_name or not 0 <= score <= 100:
            raise ValueError("provide a positive ID, non-empty name, and score from 0 to 100")
        if student_id in self._students:
            raise ValueError("student ID already exists")
        self._students[student_id] = {"name": clean_name, "score": score}

    def average_score(self) -> float:
        if not self._students:
            return 0.0
        scores = [int(student["score"]) for student in self._students.values()]
        return sum(scores) / len(scores)

    def to_json(self) -> str:
        return json.dumps(self._students, sort_keys=True)

    @classmethod
    def from_json(cls, payload: str) -> "StudentRegistry":
        restored = cls()
        data = json.loads(payload)
        for student_id, student in data.items():
            restored.add(int(student_id), str(student["name"]), int(student["score"]))
        return restored


if __name__ == "__main__":
    registry = StudentRegistry()
    registry.add(1, "Ari", 82)
    registry.add(2, "Mina", 94)
    restored = StudentRegistry.from_json(registry.to_json())
    print("Average:", round(restored.average_score(), 1))
