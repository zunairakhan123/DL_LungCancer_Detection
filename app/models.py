from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str  # Ensure this is hashed before storage

class Prediction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    predicted_class: str
    true_class: Optional[str] = None  # Optional field
    model_name: str
    confidence: float


    class Config:
        # Suppress the protected namespace warning
        protected_namespaces = ()