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

    # Load environment configuration
    task_management = os.getenv('TASK_MANAGEMENT')
    if task_management:
        try:
            app.config.from_envvar('TASK_MANAGEMENT')
        except Exception as e:
            logging.warning(f"Could not load config from TASK_MANAGEMENT environment variable: {e}")
    else:
        logging.warning("TASK_MANAGEMENT environment variable not set, using default configuration")

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
    app.run(host="0.0.0.0", port=5005, debug=False)