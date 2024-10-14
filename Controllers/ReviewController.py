from sqlalchemy.orm import Session
from typing import List, Optional
from textblob import TextBlob
from Models.Review import Review
from Pydantic_Models.ReviewModel import ReviewCreate,ReviewResponse, ReviewUpdate
from Utilities.Db import get_db
from fastapi import Depends

def analyze_sentiment(text: str) -> str:
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    if sentiment > 0:
        return "positive"
    elif sentiment < 0:
        return "negative"
    else:
        return "neutral"

class ReviewService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_reviews(self) -> List[ReviewResponse]:
        return self.db.query(Review).all()

    def get_review_by_id(self, review_id: int) -> Optional[ReviewResponse]:
        return self.db.query(Review).filter(Review.review_id == review_id).first()

    def get_reviews_by_rating(self, rating: int) -> List[ReviewResponse]:
        return self.db.query(Review).filter(Review.rating == rating).all()

    def get_reviews_by_user_id(self, user_id: int) -> List[ReviewResponse]:
        return self.db.query(Review).filter(Review.user_id == user_id).all()

    def get_reviews_by_restaurant_id(self, restaurant_id: int) -> List[ReviewResponse]:
        return self.db.query(Review).filter(Review.restaurant_id == restaurant_id).all()

    def create_review(self, review: ReviewCreate) -> ReviewResponse:
        sentiment = analyze_sentiment(review.description)
        db_review = Review(
            rating=review.rating,
            description=review.description,
            user_id=review.user_id,
            restaurant_id=review.restaurant_id,
            sentiment=sentiment
        )
        self.db.add(db_review)
        self.db.commit()
        self.db.refresh(db_review)
        return db_review

    def update_review(self, review_id: int, review: ReviewUpdate) -> Optional[ReviewResponse]:
        db_review = self.db.query(Review).filter(Review.review_id == review_id).first()
        if db_review:
            for key, value in review.dict(exclude_unset=True).items():
                if key == 'description':
                    value = analyze_sentiment(value)
                setattr(db_review, key, value)
            self.db.commit()
            self.db.refresh(db_review)
            return db_review
        return None
    
def get_review_service(db: Session = Depends(get_db)) -> ReviewService:
    return ReviewService(db)
