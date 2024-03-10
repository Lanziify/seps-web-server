from datetime import datetime
from ..config import db

class Dataset(db.Model):
    __tablename__ = "dataset"

    data_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, unique=True, nullable=False)
    general_appearance = db.Column(db.Integer, nullable=False)
    manner_of_speaking = db.Column(db.Integer, nullable=False)
    physical_condition = db.Column(db.Integer, nullable=False)
    mental_alertness = db.Column(db.Integer, nullable=False)
    self_confidence = db.Column(db.Integer, nullable=False)
    ability_to_present_ideas = db.Column(db.Integer, nullable=False)
    communication_skills = db.Column(db.Integer, nullable=False)
    performance_rating = db.Column(db.Integer, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    already_predicted = db.Column(db.Boolean, nullable=False, default=False)
    prediction_details = db.relationship(
        "Prediction", uselist=False, back_populates="data_inputs"
    )
