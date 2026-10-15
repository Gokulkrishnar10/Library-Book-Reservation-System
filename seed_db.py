import sqlite3
import pathlib

def seed():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='books'")
    if cursor.fetchone()[0] == 0:
        print("Books table does not exist yet. Run alembic upgrade head first.")
        conn.close()
        return

    count = cursor.execute("SELECT count(*) FROM books").fetchone()[0]
    if count == 0:
        sql = pathlib.Path("seed_data.sql").read_text(encoding="utf-8")
        cursor.executescript(sql)
        conn.commit()
        print("Database seeded successfully with initial books and reservations.")
    else:
        print(f"Database already contains {count} books. Seeding skipped.")
    conn.close()

if __name__ == "__main__":
    seed()
