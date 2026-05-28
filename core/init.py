from sqlalchemy.orm import Session

from database import SessionLocal
from core.security import hash_password
from models.user import UserModel


def create_default_user():
    db = SessionLocal()
    try:
        existing_admin = db.query(UserModel).filter(UserModel.username == "admin").first()
        if existing_admin is None:
            default_password = "admin123"
            db_user = UserModel(
                username="admin",
                password_hash=hash_password(default_password),
                role="Admin",
            )
            db.add(db_user)
            db.commit()
    finally:
        db.close()
