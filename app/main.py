from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from . import models, database, auth, crud
import logging

app = FastAPI()

# Initialize the database and create tables on startup
@app.on_event("startup")
def on_startup():
    database.create_db_and_tables()

# User Registration Route
@app.post("/register/", response_model=models.User)
def register(user_create: auth.UserCreate, db: Session = Depends(database.get_session)):
    return auth.register_user(user_create, db)

# User Login Route
@app.post("/login", response_model=auth.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_session)):
    return auth.login_user(form_data, db)

# Save Prediction Route
@app.post("/predictions/")
def create_prediction(
    prediction: models.Prediction, 
    db: Session = Depends(database.get_session), 
    current_user: models.User = Depends(auth.get_current_user)
):
    logging.info(f"Received prediction: {prediction}")
    try:
        # Call the `save_prediction` function from `crud.py`
        result = crud.save_prediction(prediction, db)
        logging.info(f"Prediction saved: {result}")
        return result
    except Exception as e:
        logging.error(f"Error saving prediction: {e}")
        raise HTTPException(status_code=500, detail="Failed to save prediction")
