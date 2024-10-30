from Pydantic_Models.ReviewModel import ReviewCreate, ReviewResponse, ReviewUpdate
from Pydantic_Models.UserModel import UserResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from textblob import TextBlob
from Models.Review import Review
from Models.User import User
from Controllers.RestaurantController import RestaurantService, get_restaurant_service
from Utilities.Db import get_db
from Utilities.redis import RedisClient, get_redis
from fastapi import Depends

def analyze_sentiment(text: str) -> str:
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    return "positive" if sentiment > 0 else "negative" if sentiment < 0 else "neutral"

class ReviewService:
    def __init__(self, db: Session = Depends(get_db), redis_client: RedisClient = Depends(get_redis), restaurant_service: RestaurantService = Depends(get_restaurant_service)):
        self.db = db
        self.restaurant_service = restaurant_service
        self.redis_client = redis_client

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
    
    def update_restaurant_average_rating(self, restaurant_id: int):
        restaurant = self.restaurant_service.get_restaurant(restaurant_id)
        if restaurant:
            average_rating = self.db.query(func.avg(Review.rating)).filter(Review.restaurant_id == restaurant_id).scalar()
            restaurant.average_rating = round(average_rating, 2) if average_rating else 0
            self.db.commit()
            return restaurant.average_rating
        return None

    def create_review(self, review: ReviewCreate, current_user: int) -> ReviewResponse:
        sentiment = analyze_sentiment(review.description)
        user_id = current_user
        db_review = Review(
            rating=review.rating,
            description=review.description,
            user_id=user_id,
            restaurant_id=review.restaurant_id,
            sentiment=sentiment
        )
        self.db.add(db_review)
        self.db.commit()
        self.db.refresh(db_review)

        user = self.db.query(User).filter(User.user_id == current_user).first()
        if user:
            user.review_count += 1
            self.db.commit()


        restaurant = self.restaurant_service.get_restaurant(db_review.restaurant_id)
        if restaurant:
            score = 1 if sentiment == "positive" else -1 if sentiment == "negative" else 0
            self.redis_client.add_or_update_restaurant_score(str(db_review.restaurant_id), restaurant.name,score)
            self.redis_client.add_or_update_restaurant(str(db_review.restaurant_id), restaurant.name,score)

        self.update_restaurant_average_rating(review.restaurant_id)    

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
    
#Dependency
def get_review_service(db: Session = Depends(get_db), restaurant_service: RestaurantService = Depends(get_restaurant_service), redis_client: RedisClient = Depends(get_redis)) -> ReviewService:
    return ReviewService(db, redis_client, restaurant_service)
