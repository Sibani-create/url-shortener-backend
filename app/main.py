from fastapi import FastAPI, Depends, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from . import models, database, schemas, crud, redis_client
from .config import settings

# Initialize Database
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# --- SECURITY SETUP START ---
# Define the header key name
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == settings.API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        )
# --- SECURITY SETUP END ---

# Dependency to get DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the URL Shortener API"}

# 1. THE SHORTENER ENDPOINT (PROTECTED)
# Added 'dependencies' list here
@app.post("/url", response_model=schemas.URLInfo, dependencies=[Depends(get_api_key)])
def create_url(url: schemas.URLCreate, request: Request, db: Session = Depends(get_db)):
    # Rate Limiting Logic
    client_ip = request.client.host
    rate_limit_key = f"rate_limit:{client_ip}"
    
    current_count = redis_client.r.get(rate_limit_key)
    if current_count and int(current_count) >= 5:
        raise HTTPException(status_code=429, detail="Too many requests. Wait 1 minute.")
        
    redis_client.r.incr(rate_limit_key)
    if not current_count:
        redis_client.r.expire(rate_limit_key, 60)

    # URL Logic
    if not url.target_url.startswith(("http://", "https://")):
        url.target_url = "http://" + url.target_url

    db_url = crud.create_db_url(db=db, url=url)
    base_url = str(request.base_url)
    db_url.url = f"{base_url}{db_url.key}"
    
    return db_url

# 2. THE REDIRECT ENDPOINT (PUBLIC - NO API KEY NEEDED)
@app.get("/{url_key}")
def forward_to_target_url(url_key: str, request: Request, db: Session = Depends(get_db)):
    db_url = crud.get_db_url_by_key(db, url_key=url_key)
    if db_url:
        db_url.clicks += 1
        db.commit()
        return RedirectResponse(db_url.target_url)
    else:
        raise HTTPException(status_code=404, detail=f"URL '{url_key}' not found")

# 3. THE ANALYTICS ENDPOINT (PROTECTED)
@app.get("/stats/{url_key}", response_model=schemas.URLInfo, dependencies=[Depends(get_api_key)])
def get_url_stats(url_key: str, db: Session = Depends(get_db)):
    db_url = crud.get_db_url_by_key(db, url_key=url_key)
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    db_url.url = f"http://127.0.0.1:8000/{db_url.key}"
    return db_url