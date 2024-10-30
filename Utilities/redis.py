import redis
from typing import List, Tuple

class RedisClient:
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)

    def add_or_update_restaurant(self, restaurant_id: str,restaurant_name: str, score: float):
        """
        Add or update a restaurant's score. Use a sorted set where:
        - `restaurant_leaderboard` is the key
        - The score is the average rating or a weighted score based on criteria
        - `restaurant_id` is the member
        """
        self.client.zincrby("restaurant_lead", score, f"{restaurant_id}:{restaurant_name}")

    def add_or_update_restaurant_score(self, restaurant_id: str, restaurant_name: str, score: int):
        """
        Updates the restaurant score based on the sentiment score.
        """
        # Track cumulative score and review count for each restaurant
        self.client.hincrby("restaurant_leaderboard", f"{restaurant_id}:score", score)
        self.client.hincrby("restaurant_leaderboard", f"{restaurant_id}:count", 1)
        self.client.hset("restaurant_leaderboard", f"{restaurant_id}:name", restaurant_name)

    def get_restaurant_rating(self, restaurant_id: str) -> float:
        """
        Calculates the average sentiment score for the restaurant, returning it as a rating.
        """
        # Retrieve cumulative score and review count
        total_score = int(self.client.hget("restaurant_leaderboard", f"{restaurant_id}:score") or 0)
        review_count = int(self.client.hget("restaurant_leaderboard", f"{restaurant_id}:count") or 1)

        # Calculate the average sentiment score, scaled to a 1-5 rating
        avg_sentiment_score = total_score / review_count
        # Map the average score to a rating scale (e.g., 1 to 5 stars)
        return max(1, min(5, 3 + avg_sentiment_score * 2))
    
    def get_all_restaurant_ratings(self) -> list[tuple[str, float]]:
        """
        Retrieve and calculate average ratings for all restaurants, sorted by rating from highest to lowest.
        """
        # Collect all restaurant data from Redis
        keys = self.client.hkeys("restaurant_leaderboard")
        restaurant_data = {}

        # Parse Redis data into a dictionary
        for key in keys:
            if ":name" in key:
                restaurant_id = key.split(":")[0]
                restaurant_data[restaurant_id] = {
                    "name": self.client.hget("restaurant_leaderboard", f"{restaurant_id}:name"),
                    "score": int(self.client.hget("restaurant_leaderboard", f"{restaurant_id}:score") or 0),
                    "count": int(self.client.hget("restaurant_leaderboard", f"{restaurant_id}:count") or 1)
                }

        # Calculate average rating and sort by it
        ratings = []
        for restaurant_id, data in restaurant_data.items():
            avg_score = data["score"] / data["count"]
            # Scale to a 1-5 star rating
            rating = max(1, min(5, 3 + avg_score * 2))  # Neutral (0) -> 3 stars, etc.
            ratings.append((data["name"], rating))

        # Sort by rating in descending order
        ratings.sort(key=lambda x: x[1], reverse=True)
        return ratings
    def get_top_restaurants(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Retrieve the top restaurants from the leaderboard based on score.
        Returns a list of tuples (restaurant_id, score).
        """
        try:
            return self.client.zrevrange("restaurant_lead", 0, top_n - 1, withscores=True, score_cast_func=float)
        except redis.RedisError as e:
            print(f"Error accessing Redis: {e}")
            return []

    def remove_restaurant(self, restaurant_id: str):
        """
        Remove a restaurant from the leaderboard.
        """
        self.client.zrem("restaurant_leaderboard", restaurant_id)


# Dependency Injection for FastAPI
def get_redis():
    return RedisClient()
