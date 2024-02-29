from flask import Blueprint, session, request

index_bp = Blueprint("home", __name__)

@index_bp.route('/', methods=['GET'])
def index():
    
    return 'Hello world!'