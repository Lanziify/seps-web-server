import os
from flask import Blueprint, request, session, url_for, jsonify

from server.middleware.auth import required_auth
from ..schema.users import User
from ..utils.tokenUtils import decodeToken
from datetime import datetime, timedelta
from ..config import db, mail
import jwt
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

user_bp = Blueprint("user", __name__)

# get list of users by page with a default size of 10
# accepts sorting query by using sort_by and sort_order
# returns a list of users


@user_bp.route("/users", methods=["GET"])
def get_user():
    try:
        page = request.args.get("page", 1, type=int)
        item = request.args.get("item", 10, type=int)
        sort_by = request.args.get("sort_by", "user_id")
        sort_order = request.args.get("sort_order", "asc")

        sort_column = getattr(User, sort_by)

        if sort_order == "asc":
            sort_column = sort_column.asc()
        elif sort_order == "desc":
            sort_column = sort_column.desc()

        users = User.query.order_by(sort_column).paginate(page=page, per_page=item)

        if users:
            users_list = []
            for user in users:
                user_dict = {
                    "user_id": user.user_id,
                    "username": user.username,
                    "email": user.email,
                    "verified": user.verified,
                    "created_at": user.created_at,
                }
                users_list.append(user_dict)
            return jsonify({"users": users_list}), 200
        else:
            return jsonify({"message": "No users found"}), 404
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@user_bp.route("/user/details", methods=["GET"])
@required_auth
def get_user_details():
    auth_header = request.headers.get("Authorization")
    token = decodeToken(auth_header)
    user_id = token.get("user_id")
    user = User.query.filter_by(user_id=user_id).first()
    if user:
        return (
            jsonify(
                {
                    "user": {
                        "user_id": user.user_id,
                        "username": user.username,
                        "created_at": user.created_at,
                    }
                }
            ),
            200,
        )
    else:
        return jsonify({"message": "User not found"}), 404


# get the data from the request body
# check empty fields
# store credentials
# initialize email token
# create and send email msg
# return creation message


@user_bp.route("/register", methods=["POST"])
def register_user():
    try:
        data = request.get_json()

        user = User.query.filter_by(email=data["email"]).first()

        if user is not None:
            return (
                jsonify({"message": "This email is already taken"}),
                400,
            )

        new_user = User(
            username=data["username"], email=data["email"], password=data["password"]
        )

        db.session.add(new_user)
        db.session.commit()

        serializer = URLSafeTimedSerializer(os.getenv("SECRET_KEY"))
        token = serializer.dumps(data["email"], salt="email-confirm")

        verification_url = url_for("mail.confirm_email", token=token, _external=True)

        message = Message(
            subject="Confirm Your Email",
            sender=os.getenv("MAIL_USERNAME"),
            recipients=[data["email"]],
            body=f"Please click the following link to verify your email: \n{verification_url}",
        )

        mail.send(message)

        return (
            jsonify(
                {
                    "title": "Verify Your Email",
                    "message": f"We've sent an email to {data['email']} to verify your email address and activate your account. The link in the email will expire in 24 hours.",
                }
            ),
            201,
        )

    except Exception as e:
        print(e)
        return jsonify({"message": "Oops! Something went wrong"}), 400


# get the data from the request body
# check empty fields
# check if the email exists in the database
# check if password is correct
# Generate JWT token


@user_bp.route("/login", methods=["POST"])
def login_user():
    try:
        data = request.get_json()

        user = User.query.filter_by(email=data["email"]).first()

        if not user or not user.authenticate(data["password"]):
            return (
                jsonify(
                    {"message": "Your password is incorrect or email doesn't exist"}
                ),
                400,
            )

        if not user.verified:
            return (
                jsonify(
                    {
                        "message": "Please check your email and confirm to log into your account"
                    }
                ),
                400,
            )

        access_token_payload = {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "verified": user.verified,
            "create_at": user.created_at,
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        refresh_token_payload = {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "create_at": user.created_at,
            "verified": user.verified,
        }

        access_token = jwt.encode(
            access_token_payload, os.getenv("SECRET_KEY"), algorithm="HS256"
        )
        refresh_token = jwt.encode(
            refresh_token_payload, os.getenv("SECRET_KEY"), algorithm="HS256"
        )

        return (
            jsonify({"accessToken": access_token, "refreshToken": refresh_token}),
            200,
        )
    except Exception as e:
        print(e)
        return jsonify({"message": "Oops! Something went wrong"}), 500


@user_bp.route("/refresh_token", methods=["POST"])
def new_access_token():
    refresh_token = request.get_json()

    decoded_token = decodeToken(refresh_token["refresh"])

    user_id = decoded_token.get("user_id")

    user = User.query.filter_by(user_id=user_id).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    access_token_payload = {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "verified": user.verified,
        "create_at": user.created_at,
        "exp": datetime.utcnow() + timedelta(hours=1),
    }

    access_token = jwt.encode(
        access_token_payload, os.getenv("SECRET_KEY"), algorithm="HS256"
    )

    return jsonify({"accessToken": access_token}), 200
