from app.db import seed_db

if __name__ == "__main__":
    seed_db()
    print("Database ready: data/coach.db (users 1, 2, 3 added)")