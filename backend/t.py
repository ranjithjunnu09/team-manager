from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
real_hash = pwd.hash("Password@123")

engine = create_engine(os.getenv("DATABASE_URL"))

with engine.begin() as conn:
    result = conn.execute(text("""
        UPDATE users 
        SET hashed_password = :hash
        WHERE hashed_password LIKE '$2b$12$KIXvDemoHashedPassword%'
    """), {"hash": real_hash})
    print(f"Updated {result.rowcount} users")