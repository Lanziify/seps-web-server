import os
from flask import Blueprint, request, url_for, jsonify
from ..schema.blocklist import TokenBlocklist
from ..schema.refresh_token import RefreshToken
from ..schema.users import User
from datetime import datetime, timezone
from ..config import db, mail
from flask_mail import Message
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    current_user,
    get_jwt,
    jwt_required,
)
from itsdangerous import URLSafeTimedSerializer
from flask import current_app


user_bp = Blueprint("user", __name__)

# get list of users by page with a default size of 10
# accepts sorting query by using sort_by and sort_order
# returns a list of users


@user_bp.route("/users", methods=["GET"])
def get_users():
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
        db.session.rollback()
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

        user_metadata = {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "verified": user.verified,
            "create_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

        access_token = create_access_token(identity=user.user_id)
        refresh_token = create_refresh_token(identity=user.user_id)

        stored_refresh = RefreshToken(
            token=refresh_token,
            user=user,
        )

        db.session.add(stored_refresh)
        db.session.commit()

        return (
            jsonify(
                {
                    "user": user_metadata,
                    "accessToken": access_token,
                }
            ),
            200,
        )
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({"message": "Oops! Something went wrong"}), 500


@user_bp.route("/logout", methods=["DELETE"])
@jwt_required()
def logout_user():
    jti = get_jwt()["jti"]
    sub = get_jwt()["sub"]
    now = datetime.now(timezone.utc)
    current_refresh_token = RefreshToken.query.filter_by(
        user_id=sub, blocklisted=False
    ).first()
    current_refresh_token.blocklisted = True
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    return jsonify(msg="JWT revoked")


@user_bp.route("/user", methods=["GET"])
@jwt_required()
def user_details():
    try:
        return (
            jsonify(
                {
                    "user_id": current_user.user_id,
                    "username": current_user.username,
                    "email": current_user.email,
                    "verified": current_user.verified,
                    "created_at": current_user.created_at,
                }
            ),
            200,
        )
    except Exception as e:
        print(e)
        return jsonify(message="Error")


@user_bp.route("/<string:user_id>/refresh_token", methods=["GET"])
def new_access_token(user_id):

    user = User.query.get_or_404(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    refresh_tokens = user.refresh_token
    access_token = None

    for token in refresh_tokens:
        if not token.blocklisted:
            access_token = create_access_token(identity=user.user_id)
            break

    if access_token:
        return jsonify({"accessToken": access_token}), 200
    else:
        return jsonify({"message": "No valid token found"}), 404
