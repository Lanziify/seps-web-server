from flask import jsonify
from flask_jwt_extended import JWTManager
from server.schema.blocklist import TokenBlocklist
from ..config import db
from server.schema.users import User

jwt = JWTManager()


@jwt.user_lookup_loader
def user_lookup_loader(_jwt_headers, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(user_id=identity).one_or_none()


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
    return token is not None


@jwt.unauthorized_loader
def unauthorized_response(callback):
    return jsonify({"message": "Missing Authorization Header"}), 401


@jwt.invalid_token_loader
def unauthorized_response(callback):
    return jsonify({"message": "Invalid Authorization Header"}), 401


@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({"message": "Token has expired"}), 401
