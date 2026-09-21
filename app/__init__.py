import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app():

    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )

    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "retail-intelligence-secret"
    )

    app.config["UPLOAD_FOLDER"] = os.path.join(
        os.getcwd(),
        "uploads"
    )

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    from .routes import bp

    app.register_blueprint(bp)

    return app