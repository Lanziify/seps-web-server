import os
from flask import request, jsonify
import jwt
from functools import wraps


def required_auth(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token or token is None:
            return (
                jsonify(
                    {
                        "message": "Oops! It seems like you're trying to access this resource without authenticating. Please login your account to continue."
                    }
                ),
                401,
            )
        token = token.split("Bearer ")[-1]
        try:
            jwt.decode(token, os.getenv("SECRET_KEY"), algorithms="HS256")
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 403

        return func(*args, **kwargs)

    return decorated
