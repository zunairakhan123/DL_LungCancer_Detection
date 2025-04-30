from sqlalchemy.orm import Session
from . import models, auth
from .models import Prediction
from sqlalchemy.exc import SQLAlchemyError

# Create a new user
def create_user(db: Session, user: auth.UserCreate) -> models.User:
    try:
        # Hash the user's password
        hashed_password = auth.get_password_hash(user.password)
        
        # Create a new User object
        db_user = models.User(username=user.username, password=hashed_password)
        
        # Add the new user to the database session
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        db.rollback()  # Rollback the transaction in case of an error
        raise e

# Save a prediction to the database
def save_prediction(prediction: Prediction, db: Session) -> Prediction:
    try:
        # Add the prediction to the database session
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        return prediction
    except SQLAlchemyError as e:
        db.rollback()  # Rollback in case of an error
        raise e
