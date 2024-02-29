import os
from flask import Flask
from .config import db, migrate, cors, mail, bcrypt
from dotenv import load_dotenv
from .routes import index, dataset, emails, predict, users


def create_app():
    app = Flask(__name__)
    load_dotenv()

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
    app.config["MAIL_PORT"] = os.getenv("MAIL_PORT")
    app.config["MAIL_USE_TLS"] = False
    app.config["MAIL_USE_SSL"] = True
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

    db.init_app(app)
    migrate.init_app(app, db, compare_type=True)
    cors.init_app(app, supports_credentials=True)
    mail.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(index.index_bp)
    app.register_blueprint(users.user_bp)
    app.register_blueprint(emails.mail_bp)
    app.register_blueprint(dataset.dataset_bp)
    app.register_blueprint(predict.predict_bp)

    return app
