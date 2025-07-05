import logging
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import current_app
from sqlalchemy import text

# Global SQLAlchemy instance
db = SQLAlchemy()
migrate = Migrate()


class DatabaseConfig:
    """
    Simple PostgreSQL database configuration using Flask-SQLAlchemy
    """

    @staticmethod
    def initialize(app):
        """
        Initialize database connection with Flask app

        Args:
            app: Flask application instance
        """
        try:
            # Initialize SQLAlchemy with the app
            db.init_app(app)

            # Initialize Flask-Migrate for database migrations
            migrate.init_app(app, db)

            # Test database connection
            with app.app_context():
                # This will test the connection using the new SQLAlchemy 2.0+ syntax
                with db.engine.connect() as connection:
                    connection.execute(text('SELECT 1'))
                logging.info("Database connection established successfully")
                logging.info(f"Connected to: {current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Unknown DB')}")

        except Exception as e:
            logging.critical(f"Failed to initialize database: {str(e)}")
            raise

    @staticmethod
    def create_tables():
        """
        Create all database tables
        """
        try:
            db.create_all()
            logging.info("Database tables created successfully")
        except Exception as e:
            logging.error(f"Failed to create database tables: {str(e)}")
            raise

    @staticmethod
    def get_db():
        """
        Get database instance

        Returns:
            SQLAlchemy: Database instance
        """
        return db