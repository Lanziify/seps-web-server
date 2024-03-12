from ..config import db, bcrypt
import uuid
from datetime import datetime
import pytz


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.String(36), primary_key=True, default=uuid.uuid4().hex)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    verified = db.Column(db.Boolean, default=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(tz=pytz.UTC))
    predictions = db.relationship("Prediction", backref="user")
    refresh_token = db.relationship("RefreshToken", backref="user")

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.hash_password(password)

    def hash_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def authenticate(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def __repr__(self):
        return "<User %r>" % self.username
