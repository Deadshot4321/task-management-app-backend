from flask import jsonify


class CustomException(Exception):
    """
    Custom exception class for application-specific errors
    """

    def __init__(self, message, status_code, http_status_code, details=None):
        """
        Initialize custom exception

        Args:
            message (str): Error message
            status_code (str): Application status code
            http_status_code (int): HTTP status code
            details (dict, optional): Additional error details
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.http_status_code = http_status_code
        self.details = details or {}

    @staticmethod
    def get_custom_exception_message(message, status_code, http_status_code, request_id=None):
        """
        Create standardized error response
        """
        response = {
            "statusMessage": message,
            "statusCode": status_code
        }

        if request_id:
            response["requestId"] = request_id

        return jsonify(response), http_status_code

    @classmethod
    def validation_error(cls, message="Validation failed"):
        """
        Create validation error
        """
        return cls(message, "VALIDATION_ERROR", 400)

    # @classmethod
    # def authentication_error(cls, message="Authentication failed"):
    #     """
    #     Create authentication error
    #     """
    #     return cls(message, "AUTHENTICATION_ERROR", 401)

    # @classmethod
    # def authorization_error(cls, message="Authorization failed"):
    #     """
    #     Create authorization error
    #     """
    #     return cls(message, "AUTHORIZATION_ERROR", 403)

    @classmethod
    def not_found_error(cls, message="Resource not found"):
        """
        Create not found error
        """
        return cls(message, "NOT_FOUND", 404)

    @classmethod
    def database_error(cls, message="Database operation failed"):
        """
        Create database error
        """
        return cls(message, "DATABASE_ERROR", 500)

    @classmethod
    def service_error(cls, message="Service operation failed"):
        """
        Create service error
        """
        return cls(message, "SERVICE_ERROR", 500)

    @classmethod
    def configuration_error(cls, message="Configuration error"):
        """
        Create configuration error
        """
        return cls(message, "CONFIGURATION_ERROR", 500)

    @classmethod
    def external_service_error(cls, message="External service error"):
        """
        Create external service error
        """
        return cls(message, "EXTERNAL_SERVICE_ERROR", 502)

    def __str__(self):
        return f"{self.status_code}: {self.message}"