from sqlalchemy.orm import Session
from . import models, schemas
import string
import secrets

# Helper: Generate a random 5-character string (e.g., "Abx9Z")
def create_random_key(length=5):
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))

# 1. Create a shortened URL
def create_db_url(db: Session, url: schemas.URLCreate):
    # Generate a random key
    key = create_random_key()
    
    # Check if this key already exists (rare, but safety first)
    while db.query(models.URL).filter(models.URL.key == key).first():
        key = create_random_key()

    # Create the database entry
    db_url = models.URL(target_url=url.target_url, key=key)
    
    # Add to session and commit (save)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url

# 2. Get a URL by its short key (used for redirection)
def get_db_url_by_key(db: Session, url_key: str):
    return db.query(models.URL).filter(models.URL.key == url_key, models.URL.is_active == True).first()