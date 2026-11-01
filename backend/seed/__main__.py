from sqlmodel import Session

from app.db import create_db_and_tables, engine
from seed import seed_customers

if __name__ == "__main__":
    create_db_and_tables()
    with Session(engine) as session:
        count = seed_customers(session)
    print(f"seeded {count} fake customers")
