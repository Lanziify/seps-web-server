import os
from flask import Blueprint
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from ..config import db
from ..schema.users import User

mail_bp = Blueprint("mail", __name__)


@mail_bp.route("/confirm_email/<token>", methods=["GET"])
def confirm_email(token):
    try:
        serializer = URLSafeTimedSerializer(os.getenv("SECRET_KEY"))
        email = serializer.loads(token, salt="email-confirm", max_age=86400)
        user = User.query.filter_by(email=email).first()
        if user:
            user.verified = True
            db.session.commit()
            return (
                "Email successfully verified! You can now log into your account.",
                200,
            )
        else:
            return "User not found", 404
    except SignatureExpired:
        return "The verification link has expired.", 400
    except BadSignature:
        return "The verification link is invalid.", 400
