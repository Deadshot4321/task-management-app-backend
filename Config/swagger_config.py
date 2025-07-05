import logging
from flask import current_app
from flasgger import Swagger


class SwaggerConfig:
    """
    Configuration class for Swagger/OpenAPI documentation using Flasgger
    This approach works better with traditional Flask blueprints
    """

    @staticmethod
    def configure_swagger(app):
        """
        Configure Swagger API documentation for the Flask application using Flasgger

        Args:
            app: Flask application instance

        Returns:
            Swagger: Flasgger Swagger instance
        """
        try:
            # Get configuration from .cfg file
            swagger_config = {
                "swagger": "2.0",
                "info": {
                    "title": current_app.config.get('API_TITLE', 'Task Management API'),
                    "version": current_app.config.get('API_VERSION', 'v1.0'),
                    "description": current_app.config.get('API_DESCRIPTION', 'Task Management System API'),
                    "contact": {
                        "name": "API Support",
                        "email": "support@taskmanagement.com"
                    }
                },
                "host": current_app.config.get('API_HOST', 'localhost:5005'),
                "basePath": current_app.config.get('API_BASE_PATH', '/api/v1'),
                "schemes": current_app.config.get('API_SCHEMES', ['http', 'https']),
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "securityDefinitions": current_app.config.get('API_SECURITY_DEFINITIONS', {
                    "Bearer": {
                        "type": "apiKey",
                        "name": "Authorization",
                        "in": "header",
                        "description": "JWT Authorization header using the Bearer scheme. Example: 'Authorization: Bearer {token}'"
                    }
                })
            }

            # Flasgger configuration
            flasgger_config = {
                "swagger_ui": True,
                "specs_route": current_app.config.get('API_DOC_URL', '/docs/'),
                "swagger_config": swagger_config,
                "headers": [],
                "specs": [
                    {
                        "endpoint": 'apispec',
                        "route": current_app.config.get('API_SPEC_URL', '/swagger.json'),
                        "rule_filter": lambda rule: True,
                        "model_filter": lambda tag: True,
                    }
                ],
                "static_url_path": "/flasgger_static",
                "swagger_ui_bundle_js": current_app.config.get('SWAGGER_UI_BUNDLE_JS',
                                                               '//unpkg.com/swagger-ui-dist@3/swagger-ui-bundle.js'),
                "swagger_ui_standalone_preset_js": current_app.config.get('SWAGGER_UI_STANDALONE_PRESET_JS',
                                                                          '//unpkg.com/swagger-ui-dist@3/swagger-ui-standalone-preset.js'),
                "swagger_ui_css": current_app.config.get('SWAGGER_UI_CSS',
                                                         '//unpkg.com/swagger-ui-dist@3/swagger-ui.css'),
                "swagger_ui_template_path": None,
                "swagger_ui_template_args": {
                    "title": current_app.config.get('API_TITLE', 'Task Management API'),
                    "favicon": "//unpkg.com/swagger-ui-dist@3/favicon-32x32.png"
                }
            }

            # Initialize Flasgger
            swagger = Swagger(app, config=flasgger_config)

            logging.info("Swagger documentation configured successfully with Flasgger")
            logging.info(f"API Documentation available at: {current_app.config.get('API_DOC_URL', '/docs/')}")
            logging.info(f"API Specification available at: {current_app.config.get('API_SPEC_URL', '/swagger.json')}")

            return swagger

        except Exception as e:
            logging.error(f"Failed to configure Swagger documentation: {str(e)}")
            raise

    @staticmethod
    def get_common_response_schemas():
        """
        Get common response schemas for API documentation

        Returns:
            dict: Dictionary containing common response schemas
        """
        return {
            "CommonResponse": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "description": "Indicates if the request was successful"
                    },
                    "message": {
                        "type": "string",
                        "description": "Response message"
                    },
                    "data": {
                        "type": "object",
                        "description": "Response data"
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Response timestamp"
                    }
                }
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": False
                    },
                    "error": {
                        "type": "string",
                        "description": "Error message"
                    },
                    "code": {
                        "type": "string",
                        "description": "Error code"
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Error timestamp"
                    }
                }
            }
        }