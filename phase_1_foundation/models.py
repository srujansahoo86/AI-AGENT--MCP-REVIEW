from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Review(BaseModel):
    id: str = Field(..., description="Unique identifier for the review")
    date: datetime = Field(..., description="Date the review was posted")
    rating: int = Field(..., description="Rating given by the user (1-5)")
    title: Optional[str] = Field(None, description="Title of the review (often absent on Play Store)")
    review_text: str = Field(..., description="The actual text content of the review")
    version: Optional[str] = Field(None, description="App version the user reviewed")
    source: str = Field(..., description="Source of the review, e.g., 'App Store' or 'Play Store'")
