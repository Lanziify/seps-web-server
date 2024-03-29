from flask import Blueprint, request, jsonify
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy import desc
from server.middleware.middleware import required_new_student
from ..config import db
from ..schema import predictions, dataset, classifications
from ..model.bagged_tree import model
from datetime import datetime

predict_bp = Blueprint("predict", __name__)


@predict_bp.route("/predict", methods=["POST"])
@jwt_required()
def predict():
    try:
        request_data = request.get_json()

        already_predicted = predictions.Prediction.query.filter_by(
            data_id=request_data["datasetId"]
        ).first()

        if already_predicted:
            return jsonify({"message": "Dataset already predicted!"}), 400

        data = dataset.Dataset.query.filter_by(
            data_id=request_data["datasetId"]
        ).first()

        features = []

        features.append(data.general_appearance)
        features.append(data.manner_of_speaking)
        features.append(data.physical_condition)
        features.append(data.mental_alertness)
        features.append(data.self_confidence)
        features.append(data.ability_to_present_ideas)
        features.append(data.communication_skills)
        features.append(data.performance_rating)

        start_time = datetime.utcnow()

        model_prediction = model.predict([features])

        end_time = datetime.utcnow()

        prediction_time = (end_time - start_time).total_seconds()

        class_prediction = classifications.Classification.query.filter_by(
            class_id=int(model_prediction) + 1
        ).first()

        if not class_prediction:
            return (
                jsonify(
                    {"message": "Classification not found for the predicted value"}
                ),
                404,
            )

        prediction = predictions.Prediction(
            data_id=request_data["datasetId"],
            classification_id=int(model_prediction) + 1,
            user=current_user,
        )

        data.already_predicted = True
        db.session.add(prediction)
        db.session.commit()

        return (
            jsonify(
                {
                    "title": "Employability Predicted!",
                    "body": f"The system has identified student <b>#{data.student_id}</b> as <b>{class_prediction.class_name}</b>! <br> Timestamp: {prediction.prediction_time}",
                    "prediction": class_prediction.class_name,
                    "prediction_time": prediction_time,
                }
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error inserting prediction"}), 500


@predict_bp.route("/upload_predict", methods=["POST"])
@jwt_required()
@required_new_student
def upload_predict():
    try:
        request_data = request.get_json()

        data_features = dataset.Dataset()

        data_features.student_id = (request_data["studentId"],)
        data_features.general_appearance = (request_data["features"][0],)
        data_features.manner_of_speaking = (request_data["features"][1],)
        data_features.physical_condition = (request_data["features"][2],)
        data_features.mental_alertness = (request_data["features"][3],)
        data_features.self_confidence = (request_data["features"][4],)
        data_features.ability_to_present_ideas = (request_data["features"][5],)
        data_features.communication_skills = (request_data["features"][6],)
        data_features.performance_rating = (request_data["features"][7],)

        db.session.add(data_features)
        db.session.commit()

        data_id = data_features.data_id

        data = dataset.Dataset.query.filter_by(data_id=data_id).first()

        features = []

        features.append(data.general_appearance)
        features.append(data.manner_of_speaking)
        features.append(data.physical_condition)
        features.append(data.mental_alertness)
        features.append(data.self_confidence)
        features.append(data.ability_to_present_ideas)
        features.append(data.communication_skills)
        features.append(data.performance_rating)

        model_prediction = model.predict([features])

        class_prediction = classifications.Classification.query.filter_by(
            class_id=int(model_prediction) + 1
        ).first()

        if not class_prediction:
            return (
                jsonify(
                    {"message": "Classification not found for the predicted value"}
                ),
                404,
            )

        prediction = predictions.Prediction(
            data_id=data_id,
            classification_id=int(model_prediction) + 1,
            user=current_user,
        )

        data.already_predicted = True
        db.session.add(prediction)
        db.session.commit()

        return (
            jsonify(
                {
                    "title": "Employability Predicted!",
                    "message": f"Dataset has been successfully uploaded in the database and has identified student <b>#{data.student_id}</b> as <b>{class_prediction.class_name}</b>! <br> Timestamp: <b>{prediction.prediction_time}</b>",
                }
            ),
            200,
        )

    except Exception as e:
        print(e)
        db.session.rollback()
        return (
            jsonify(
                {
                    "title": "Employability Predicted!",
                    "message": f"Dataset has been successfully uploaded in the database and has identified student <b>#{data.student_id}</b> as <b>{class_prediction.class_name}</b>! <br> Timestamp: <b>{prediction.prediction_time}</b>",
                }
            ),
            500,
        )


@predict_bp.route("/predictions", methods=["GET"])
@jwt_required()
def get_predictions():
    try:
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)

        paginated_predictions = predictions.Prediction.query.order_by(
            desc(predictions.Prediction.prediction_id)
        ).paginate(page=page, per_page=limit)

        total_items = paginated_predictions.total

        prediction_items = []

        for prediction_item in paginated_predictions:
            prediction_dict = {
                "prediction_id": prediction_item.prediction_id,
                "classification": prediction_item.classification.class_name,
                "dataset_id": prediction_item.data_id,
                "predicted_by": prediction_item.user.username,
                "email": prediction_item.user.email,
                "prediction_time": prediction_item.prediction_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
            prediction_items.append(prediction_dict)

        return (
            jsonify({"total_items": total_items, "predictions": prediction_items}),
            200,
        )

    except Exception as e:
        return (
            jsonify({"message": "Something went wrong when getting the datasets"}),
            500,
        )
