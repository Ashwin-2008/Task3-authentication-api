import os
from app.db.base import Base
from app.db.session import engine
from app.models import Submission, Admin  # noqa: F401


def init_db() -> None:
    """Create all database tables if they do not exist."""
    # Ensure data directory exists if using default SQLite path
    db_url = str(engine.url)
    if "sqlite" in db_url:
        database_file = engine.url.database
        if database_file and database_file != ":memory:":
            db_dir = os.path.dirname(database_file)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables initialized successfully.")

