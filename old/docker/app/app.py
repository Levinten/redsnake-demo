"""
RedSnake Platform - Flask Application

Dynamic automation platform with secure script execution.
"""
import os
import logging
from pathlib import Path
from flask import Flask, jsonify, request
from celery import Celery, Task

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def celery_init_app(app: Flask) -> Celery:
    """Initialize Celery with Flask app context."""
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object({
        "broker_url": app.config["CELERY_BROKER_URL"],
        "result_backend": app.config["CELERY_RESULT_BACKEND"],
        "task_ignore_result": False,
    })
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configuration from environment variables
    app.config["DATABASE_URL"] = os.getenv("DATABASE_URL")
    app.config["CELERY_BROKER_URL"] = os.getenv("CELERY_BROKER_URL")
    app.config["CELERY_RESULT_BACKEND"] = os.getenv("CELERY_RESULT_BACKEND")
    app.config["REDIS_URL"] = os.getenv("REDIS_URL")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me-in-production")
    app.config["SCRIPTS_DIR"] = os.getenv("SCRIPTS_DIR", "/app/scripts")
    app.config["VAULT_FILE"] = os.getenv("VAULT_FILE", "/app/data/vault.enc")
    app.config["ENVIRONMENT"] = os.getenv("FLASK_ENV", "development")
    
    # Security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response
    
    # Initialize Celery
    celery_init_app(app)
    
    # Discover scripts on startup
    logger.info("Discovering scripts...")
    
    @app.route("/")
    def index():
        """Platform information."""
        return jsonify({
            "name": "RedSnake Automation Platform",
            "version": "0.1.0",
            "environment": app.config["ENVIRONMENT"],
            "scripts_loaded": 0
        }), 200

    @app.route("/healthz")
    def healthz():
        """Health check endpoint used by Docker."""
        return jsonify({"status": "ok"}), 200

    return app
    
# This is used by the Celery worker
celery_app = celery_init_app(create_app())
