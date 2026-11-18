import json


students = [
    {"id": 1, "name": "Ari", "score": 82},
    {"id": 2, "name": "Mina", "score": 94},
]

average = sum(student["score"] for student in students) / len(students)
encoded = json.dumps(students)
restored = json.loads(encoded)

print(f"Average score: {average:.1f}")
print("Top students:", [student["name"] for student in restored if student["score"] >= 90])
