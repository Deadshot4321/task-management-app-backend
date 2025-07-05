import logging
from flask import jsonify
from Exceptions.custom_exception import CustomException
from Config.logging_config import LoggingConfig


class ExceptionConfig:
    """
    Global exception handlers configuration
    """

    @staticmethod
    def configure_exception_handlers(app):
        """
        Configure global exception handlers for the Flask app
        """

        @app.errorhandler(CustomException)
        def handle_custom_exception(error):
            """
            Handle custom exceptions with proper logging
            """
            request_id = LoggingConfig.get_request_id()
            logging.error(
                f"Custom exception occurred - Request ID: {request_id}, "
                f"Message: {error.message}, Status: {error.status_code}"
            )

            response = {
                "statusMessage": error.message,
                "statusCode": error.status_code,
                "requestId": request_id
            }
            return jsonify(response), error.http_status_code

        @app.errorhandler(400)
        def handle_bad_request(error):
            """
            Handle bad request errors
            """
            request_id = LoggingConfig.get_request_id()
            logging.error(f"Bad Request - Request ID: {request_id}, Error: {str(error)}")

            response = {
                "statusMessage": "Bad Request - Invalid input provided",
                "statusCode": "VALIDATION_ERROR",
                "requestId": request_id
            }
            return jsonify(response), 400

        @app.errorhandler(401)
        def handle_unauthorized(error):
            """
            Handle unauthorized errors
            """
            request_id = LoggingConfig.get_request_id()
            logging.error(f"Unauthorized - Request ID: {request_id}, Error: {str(error)}")

            response = {
                "statusMessage": "Unauthorized - Invalid or missing authentication",
                "statusCode": "AUTHENTICATION_ERROR",
                "requestId": request_id
            }
            return jsonify(response), 401

        @app.errorhandler(404)
        def handle_not_found(error):
            """
            Handle not found errors
            """
            request_id = LoggingConfig.get_request_id()
            logging.error(f"Not Found - Request ID: {request_id}, Error: {str(error)}")

            response = {
                "statusMessage": "Resource not found",
                "statusCode": "NOT_FOUND",
                "requestId": request_id
            }
            return jsonify(response), 404

        @app.errorhandler(500)
        def handle_internal_server_error(error):
            """
            Handle internal server errors
            """
            request_id = LoggingConfig.get_request_id()
            logging.critical(f"Internal Server Error - Request ID: {request_id}, Error: {str(error)}")

            response = {
                "statusMessage": "Oops! An unexpected error encountered while processing your request. Please try again.",
                "statusCode": "INTERNAL_SERVER_ERROR",
                "requestId": request_id
            }
            return jsonify(response), 500

        @app.errorhandler(Exception)
        def handle_generic_exception(error):
            """
            Handle all other unhandled exceptions
            """
            request_id = LoggingConfig.get_request_id()
            logging.critical(
                f"Unhandled Exception - Request ID: {request_id}, "
                f"Type: {type(error).__name__}, Message: {str(error)}",
                exc_info=True
            )

            response = {
                "statusMessage": "Oops! An unexpected error encountered while processing your request. Please try again.",
                "statusCode": "INTERNAL_SERVER_ERROR",
                "requestId": request_id
            }
            return jsonify(response), 500

        logging.info("Exception handlers configured successfully") 