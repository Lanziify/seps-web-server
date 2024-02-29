import os
import jwt


def decodeToken(auth_header):
    token = auth_header.split("Bearer ")[1]
    decoded_token = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms="HS256")
    return decoded_token
