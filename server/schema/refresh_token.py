from datetime import datetime
from ..config import db
import uuid


class RefreshToken(db.Model):
    __tablename__ = "refresh_token"

    token_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String, db.ForeignKey("users.user_id"), nullable=False)
    token = db.Column(db.String, unique=True, nullable=False)
    blocklisted = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
