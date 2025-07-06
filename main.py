import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS

# Import configurations
from Config.logging_config import LoggingConfig
from Config.database_config import DatabaseConfig
# from Config.exception_config import ExceptionConfig
from Config.swagger_config import SwaggerConfig


# Import blueprints
from Controller.auth_controller import auth_bp
from Controller.task_controller import task_bp


def create_app():
    """
    Application factory pattern for creating Flask app
    """
    app = Flask(__name__)

    # Configure app for both local and deployment environments
    configure_app_settings(app)

    # Configure CORS
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    # Configure logging
    LoggingConfig.configure_logging(app)

    # Configure exception handlers
    from Config.exception_config import ExceptionConfig
    ExceptionConfig.configure_exception_handlers(app)

    # Initialize database connection within app context
    with app.app_context():
        try:
            # Initialize database connection
            DatabaseConfig.initialize(app)
            
            # Create database tables if they don't exist
            DatabaseConfig.create_tables()

            # Configure Swagger API Documentation
            SwaggerConfig.configure_swagger(app)

            # Register blueprints
            register_blueprints(app)

            logging.info("Application initialization completed successfully")

        except Exception as e:
            logging.critical(f"Failed to initialize application components: {str(e)}")
            raise

    return app


def configure_app_settings(app):
    """
    Configure app settings for both local (.cfg file) and deployment (env vars)
    """
    # First, try to load from .cfg file (for local development)
    task_management = os.getenv('TASK_MANAGEMENT')
    if task_management:
        try:
            app.config.from_envvar('TASK_MANAGEMENT')
            logging.info("Configuration loaded from TASK_MANAGEMENT .cfg file")
        except Exception as e:
            logging.warning(f"Could not load config from TASK_MANAGEMENT environment variable: {e}")
    
    # Then, override with individual environment variables (for deployment)
    # This allows deployment platforms to override .cfg file settings
    env_configs = {
        'SQLALCHEMY_DATABASE_URI': os.getenv('DATABASE_URL') or os.getenv('SQLALCHEMY_DATABASE_URI'),
        'SQLALCHEMY_TRACK_MODIFICATIONS': os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False').lower() == 'true',
        'GROQ_API_KEY': os.getenv('GROQ_API_KEY'),
        'AI_ENABLED': os.getenv('AI_ENABLED', 'true').lower() == 'true',
        'API_TITLE': os.getenv('API_TITLE', 'Task Management API'),
        'API_VERSION': os.getenv('API_VERSION', 'v1.0'),
        'API_DESCRIPTION': os.getenv('API_DESCRIPTION', 'A comprehensive task management system API'),
        'API_HOST': os.getenv('API_HOST', 'localhost:5005'),
        'API_BASE_PATH': os.getenv('API_BASE_PATH', '/api/v1'),
        'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        'LOG_HANDLERS': os.getenv('LOG_HANDLERS', 'CONSOLE'),
        'LOG_COLORS': os.getenv('LOG_COLORS', 'False').lower() == 'true',  # Disable colors for deployment
        'PROPAGATE_EXCEPTIONS': os.getenv('PROPAGATE_EXCEPTIONS', 'True').lower() == 'true',
    }
    
    # Update app config with environment variables (only if they exist)
    for key, value in env_configs.items():
        if value is not None:
            app.config[key] = value
    
    logging.info("Application configuration completed")


def register_blueprints(app):
    """
    Register all blueprints with the Flask application
    """
    try:
        # Register authentication blueprint
        app.register_blueprint(auth_bp)
        logging.info("Authentication blueprint registered successfully")
        
        # Register task management blueprint
        app.register_blueprint(task_bp)
        logging.info("Task management blueprint registered successfully")

        logging.info("All blueprints registered successfully")

    except Exception as e:
        logging.error(f"Failed to register blueprints: {str(e)}")
        raise


# Create the Flask application
app = create_app()

if __name__ == '__main__':
    # Use PORT environment variable for deployment platforms like Render
    port = int(os.getenv('PORT', 5005))
    app.run(host="0.0.0.0", port=port, debug=False)