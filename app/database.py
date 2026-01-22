from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# 1. Load the password from the .env file
load_dotenv()

# 2. Get the URL
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 3. Create the connection engine
# echo=True prints SQL queries to the terminal (great for debugging)
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# 4. Create a "Session" factory (this creates a new database connection for each request)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Create the Base class (we will inherit from this to create tables)
Base = declarative_base()

# 6. Dependency Injection (We will use this later in the API)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()