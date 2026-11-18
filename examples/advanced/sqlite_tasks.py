import sqlite3


with sqlite3.connect(":memory:") as connection:
    connection.execute(
        "CREATE TABLE tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL, done INTEGER NOT NULL)"
    )
    connection.executemany(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        [("Read the lesson", 1), ("Write a test", 0)],
    )
    rows = connection.execute(
        "SELECT title FROM tasks WHERE done = ? ORDER BY title",
        (0,),
    ).fetchall()

print("Open tasks:", [row[0] for row in rows])
