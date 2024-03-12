from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import desc
from ..config import db
from ..middleware.middleware import required_new_student
from ..schema import dataset

dataset_bp = Blueprint("dataset", __name__)


@dataset_bp.route("/upload", methods=["POST"])
@jwt_required()
@required_new_student
def upload_data():
    try:
        data = request.get_json()

        data_features = dataset.Dataset()

        data_features.student_id = (data["studentId"],)
        data_features.general_appearance = (data["features"][0],)
        data_features.manner_of_speaking = (data["features"][1],)
        data_features.physical_condition = (data["features"][2],)
        data_features.mental_alertness = (data["features"][3],)
        data_features.self_confidence = (data["features"][4],)
        data_features.ability_to_present_ideas = (data["features"][5],)
        data_features.communication_skills = (data["features"][6],)
        data_features.performance_rating = (data["features"][7],)

        # db.session.add(data_features)
        # db.session.commit()

        return (
            jsonify(
                {
                    "title": "Evaluation Uploaded",
                    "message": "Data have been successfully added to the datasets.",
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
                    "title": "Opss! Something went wrong",
                    "message": "Something went wrong saving the data. Please try again.",
                }
            ),
            400,
        )


@dataset_bp.route("/dataset", methods=["GET"])
@jwt_required()
def get_dataset():
    try:
        page = request.args.get("page", 1, type=int)
        limit = request.args.get("limit", 10, type=int)

        paginated_dataset = dataset.Dataset.query.order_by(
            desc(dataset.Dataset.data_id)
        ).paginate(page=page, per_page=limit)

        total_items = paginated_dataset.total
        dataset_result = paginated_dataset.items

        datasets = []

        if dataset_result:
            for datapoint in dataset_result:
                datapoint_dict = datapoint.__dict__
                datapoint_dict = {
                    key: value
                    for key, value in datapoint_dict.items()
                    if not key.startswith("_")
                }
                datasets.append(datapoint_dict)

        return jsonify({"total_items": total_items, "datasets": datasets}), 200
    except Exception as e:
        return (
            jsonify({"message": "Something went wrong when getting the datasets"}),
            500,
        )
