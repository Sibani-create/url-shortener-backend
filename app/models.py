from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from .database import Base

class URL(Base):
    __tablename__ = "urls"

    # The unique ID for the database
    id = Column(Integer, primary_key=True, index=True)
    
    # The short code (e.g., "abc12") - Must be unique!
    key = Column(String, unique=True, index=True)
    
    # The original long website link
    target_url = Column(String, index=True)
    
    # Is the link working? (Allows us to ban links later)
    is_active = Column(Boolean, default=True)
    
    # Simple analytics: How many times was it clicked?
    clicks = Column(Integer, default=0)
    
    # When was it created? (Auto-filled by the database)
    created_at = Column(DateTime(timezone=True), server_default=func.now())