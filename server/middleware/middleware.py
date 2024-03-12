import os
from flask import request, jsonify
import jwt
from functools import wraps
from server.schema import dataset


def required_new_student(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        request_data = request.get_json()

        current_student_id = dataset.Dataset.query.filter_by(
            student_id=request_data["studentId"]
        ).first()

        if current_student_id is not None:
            return (
                jsonify(
                    {
                        "title": "Student Id Already Exists!",
                        "message": "The data you are trying to upload already exists. Please check the student id and try again.",
                    }
                ),
                400,
            )

        return func(*args, **kwargs)

    return decorated
