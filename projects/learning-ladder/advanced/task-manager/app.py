import sqlite3


class TaskManager:
    def __init__(self) -> None:
        self._connection = sqlite3.connect(":memory:")
        self._connection.execute(
            "CREATE TABLE tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0)"
        )

    def add(self, title: str) -> int:
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("task title is required")
        cursor = self._connection.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (clean_title,),
        )
        self._connection.commit()
        return int(cursor.lastrowid)

    def complete(self, task_id: int) -> bool:
        cursor = self._connection.execute(
            "UPDATE tasks SET done = 1 WHERE id = ?",
            (task_id,),
        )
        self._connection.commit()
        return cursor.rowcount == 1

    def list_open(self) -> list[tuple[int, str]]:
        cursor = self._connection.execute(
            "SELECT id, title FROM tasks WHERE done = ? ORDER BY id",
            (0,),
        )
        return cursor.fetchall()

    def close(self) -> None:
        self._connection.close()


if __name__ == "__main__":
    tasks = TaskManager()
    first_task = tasks.add("Write a failing test")
    tasks.add("Implement the smallest fix")
    tasks.complete(first_task)
    print("Open tasks:", tasks.list_open())
    tasks.close()
