
# Restaurant_Review_with_NLP

As the last project requirents for completing ALX course i've built an API that is majorly used to create and post reviews on restaurants. The reviews are automaticaly analyzed to determine whether the review is positive, neutral or negative, And again using redis we maintain a leaderboard on average rating of a restaurant based on the sentiment analysis.
In order to post a review user must be signed in and there are also admin priveledges like adding restaurants and users to the DB.


## API Reference

## Features

- **Authentication**: OAuth2-based authentication with JWT tokens.
- **User Management**: CRUD operations for users with different roles.
- **Admin Management**: CRUD operations for admin users.
- **Restaurant Management**: CRUD operations for restaurants.
- **Review Management**: CRUD operations for reviews, including sentiment analysis.
- **Leaderboard**: Track restaurant ratings and rankings using Redis.

## Dependencies

- FastAPI
- SQLAlchemy
- Redis
- Text Blob

## Endpoints

### Authentication
- `POST /token`: Login to obtain an access token.

### Admin Management
- `GET /restaurant_review/admin`: Get all admins.
- `GET /restaurant_review/admin/{admin_id}`: Get admin by ID.
- `GET /restaurant_review/admin/username/{username}`: Get admin by username.
- `POST /restaurant_review/admin/new`: Create a new admin.
- `PUT /restaurant_review/admin/update`: Update an existing admin.
- `DELETE /restaurant_review/admin/delete/{admin_id}`: Delete an admin by ID.

### Restaurant Management
- `GET /restaurant_review/restaurant`: List restaurants.
- `GET /restaurant_review/restaurant/{restaurant_id}`: Get restaurant details by ID.
- `POST /restaurant_review/restaurant`: Create a new restaurant.
- `PUT /restaurant_review/restaurant/{restaurant_id}`: Update restaurant details.
- `DELETE /restaurant_review/restaurant/{restaurant_id}`: Delete a restaurant.

### Review Management
- `GET /restaurant_review/reviews`: Get all reviews.
- `GET /restaurant_review/reviews/{review_id}`: Get review by ID.
- `GET /restaurant_review/reviews/rating/{rating}`: Get reviews by rating.
- `GET /restaurant_review/reviews/user`: Get reviews by the current user.
- `GET /restaurant_review/reviews/restaurant/{restaurant_id}`: Get reviews for a specific restaurant.
- `POST /restaurant_review/reviews/`: Create a new review.
- `PUT /restaurant_review/reviews/{review_id}`: Update a review.
  
### User Management
- `GET /restaurant_review/user`: Get all users.
- `GET /restaurant_review/user/id/{user_id}`: Get user by ID.
- `GET /restaurant_review/user/username/{username}`: Get user by username.
- `POST /restaurant_review/user/add`: Create a new user.
- `PUT /restaurant_review/user/update`: Update an existing user.
- `DELETE /restaurant_review/user/delete/{user_id}`: Delete a user.

### Leaderboard
- `GET /leaderboard`: Get the restaurant leaderboard.
- `GET /restaurant_review/restaurant/ratings`: Get all restaurant ratings.



