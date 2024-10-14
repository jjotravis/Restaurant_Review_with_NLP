from pydantic import BaseModel, Field

class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Review rating between 1 and 5")
    description: str = Field("You can eat here if you have no other way to go", max_length=300, description="Description of the review")
    user_id: int = Field(..., description="ID of the user who made the review")
    restaurant_id: int = Field(..., description="ID of the restaurant being reviewed")

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(ReviewBase):
    sentiment: str = Field(None, description="Sentiment of the review text")

class ReviewResponse(ReviewBase):
    review_id: int
    sentiment: str = None

    class Config:
        from_attributes = True
