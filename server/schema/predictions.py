from ..config import db
import time

class Prediction(db.Model):
    __tablename__ = 'predictions'

    prediction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data_id =  db.Column(db.Integer, db.ForeignKey("dataset.data_id"), nullable=False)
    classification_id = db.Column(db.Integer, db.ForeignKey('class.class_id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=False)
    prediction_time = db.Column(db.Integer, default=int(time.time()))
    classification = db.relationship("Classification", back_populates='prediction_details')
    data_inputs = db.relationship("Dataset", back_populates="prediction_details")
