"""
RedSnake Platform - Flask Application

Dynamic automation platform with secure script execution.
"""
import os
import logging
from pathlib import Path
from flask import Flask, jsonify, request
from celery import Celery, Task

# Import RedSnake framework
from redsnake.execution import ExecutionEngine
from redsnake.core.exceptions import ValidationError, SecurityError, ExecutionError

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
    
    # Initialize RedSnake Execution Engine
    engine = ExecutionEngine(
        scripts_dir=app.config["SCRIPTS_DIR"],
        vault_file=app.config["VAULT_FILE"]
    )
    
    # Discover scripts on startup
    logger.info("Discovering scripts...")
    count = engine.discover_scripts()
    logger.info(f"Loaded {count} script(s)")
    
    # Store engine in app
    app.extensions["redsnake_engine"] = engine
    
    # === ROUTES ===
    
    @app.route("/healthz")
    def health_check():
        """Health check for container orchestration."""
        return jsonify({"status": "healthy"}), 200
    
    @app.route("/")
    def index():
        """Platform information."""
        return jsonify({
            "name": "RedSnake Automation Platform",
            "version": "0.1.0",
            "environment": app.config["ENVIRONMENT"],
            "scripts_loaded": len(engine.registry.list_names())
        }), 200
    
    @app.route("/api/scripts")
    def list_scripts():
        """List all available scripts."""
        try:
            catalog = engine.get_script_catalog()
            return jsonify({
                "success": True,
                "count": len(catalog),
                "scripts": catalog
            }), 200
        except Exception as e:
            logger.error(f"Failed to list scripts: {e}")
            return jsonify({
                "success": False,
                "error": "Failed to retrieve scripts"
            }), 500
    
    @app.route("/api/scripts/<script_name>")
    def get_script(script_name: str):
        """Get details of a specific script."""
        instance = engine.registry.get_instance(script_name)
        if not instance:
            return jsonify({
                "success": False,
                "error": "Script not found"
            }), 404
        
        return jsonify({
            "success": True,
            "script": instance.to_dict()
        }), 200
    
    @app.route("/api/scripts/<script_name>/execute", methods=["POST"])
    def execute_script(script_name: str):
        """
        Execute a script.
        
        Security: Validates all inputs, requires authentication (TODO)
        """
        try:
            # Get request data
            data = request.get_json()
            if not data:
                return jsonify({
                    "success": False,
                    "error": "No JSON data provided"
                }), 400
            
            arguments = data.get("arguments", {})
            
            # TODO: Get user from authentication
            user = data.get("user", "anonymous")
            
            # Execute script
            result = engine.execute_script(
                script_name=script_name,
                arguments=arguments,
                environment=app.config["ENVIRONMENT"],
                user=user,
                source="api"
            )
            
            return jsonify({
                "success": result.success,
                "execution_id": result.execution_id,
                "result": result.result,
                "error": result.error,
                "duration_seconds": result.duration_seconds
            }), 200 if result.success else 400
            
        except ValidationError as e:
            return jsonify({
                "success": False,
                "error": e.safe_message
            }), 400
        except SecurityError as e:
            return jsonify({
                "success": False,
                "error": e.safe_message
            }), 403
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return jsonify({
                "success": False,
                "error": "Internal server error"
            }), 500
    
    return app


# This is used by the Celery worker
celery_app = celery_init_app(create_app())
