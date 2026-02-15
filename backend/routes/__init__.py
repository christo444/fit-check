from flask import Blueprint


def register_routes(app):
    """Register all route blueprints"""

    # Import route blueprints
    from routes.upload import upload_bp
    from routes.outfit import outfit_bp
    from routes.health import health_bp
    from routes.detect import detect_bp
    from routes.pose import pose_bp

    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(upload_bp, url_prefix="/api")
    app.register_blueprint(outfit_bp, url_prefix="/api")
    app.register_blueprint(detect_bp, url_prefix="/api")
    app.register_blueprint(pose_bp, url_prefix="/api")

    print("✅ Routes registered successfully")
