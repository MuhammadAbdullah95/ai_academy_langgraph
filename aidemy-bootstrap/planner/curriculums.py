import os
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base  # Correct import!
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

db_host = os.getenv("HOST")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_name = os.getenv("DB_NAME")

# Check if environment variables are loaded correctly
if not all([db_host, db_user, db_pass, db_name]):
    raise ValueError("Missing database environment variables. Please check your .env file.")

SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_pass}@{db_host}/{db_name}"

print(f"--------------------------->db_user: {db_user!r}")
print(f"--------------------------->db_pass: {db_pass!r}")
print(f"--------------------------->db_name: {db_name!r}")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()  # Correct usage

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_curriculum(year: int, subject: str):
    """
    Get school curriculum

    Args:
        subject: User's request subject string
        year: User's request year int
    """
    db = SessionLocal()
    try:
        stmt = text(
            "SELECT description FROM curriculums WHERE year = :year AND subject = :subject"
        )

        # Correct way to pass parameters in SQLAlchemy 2.0: use 'params'
        result = db.execute(stmt, params={"year": year, "subject": subject})
        row = result.fetchone()
        if row:
            return row[0]
        else:
            return None

    except Exception as e:
        print(f"Error in get_curriculum: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    print(get_curriculum(6, "Mathematics"))
