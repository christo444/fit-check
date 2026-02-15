from flask import Flask
from flask_cors import CORS
import os
from config import config, Config


def create_app(config_name="default"):
    """Application factory function"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please set up your .env file based on .env.example")

    # Enable CORS
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["FRONTEND_URL"]}},
        supports_credentials=True,
    )

    # Create upload folder if it doesn't exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Register blueprints
    from routes import register_routes

    register_routes(app)

    return app


if __name__ == "__main__":
    env = os.getenv("FLASK_ENV", "development")
    app = create_app(env)

    print(f"\n{'='*50}")
    print(f"🚀 FitCheck Backend Server")
    print(f"{'='*50}")
    print(f"Environment: {env}")
    print(f"Debug Mode: {app.config['DEBUG']}")
    print(f"Upload Folder: {app.config['UPLOAD_FOLDER']}")
    print(f"Frontend URL: {app.config['FRONTEND_URL']}")
    print(f"{'='*50}\n")

    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
