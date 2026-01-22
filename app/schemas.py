from pydantic import BaseModel

# 1. What the user sends TO us
class URLCreate(BaseModel):
    target_url: str

# 2. What we send BACK to the user
class URLInfo(BaseModel):
    target_url: str
    is_active: bool
    clicks: int
    url: str  # This will be the full short URL

    class Config:
        from_attributes = True