from ..config import db

class Classification(db.Model):
    __tablename__ = "class"
    
    class_id = db.Column(db.Integer, primary_key=True)
    class_name  = db.Column(db.String(255), nullable=False)
    prediction_details = db.relationship('Prediction', uselist=False, back_populates="classification")

    def initialize_default_class(*args, **kwargs):
        class_item = [
            {"class_name" : "LessEmployable"},
            {"class_name" : "Employable"}
        ]
        for item in class_item:
            new_class_name = Classification(**item)
            db.session.add(new_class_name)
        db.session.commit()