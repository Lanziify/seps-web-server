from flask import jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
mail = Mail()
bcrypt = Bcrypt()
