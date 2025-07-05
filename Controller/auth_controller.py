import logging
from flask import Blueprint, request, jsonify
from flasgger import swag_from
from Service.auth_service import AuthService
from Exceptions.custom_exception import CustomException
from Config.logging_config import LoggingConfig

# Create Blueprint with new clear endpoint structure
auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1')

@auth_bp.before_request
def set_request_context():
    """Set request context for logging"""
    LoggingConfig.set_request_context()

@auth_bp.route('/get/professions', methods=['GET'])
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Get available profession choices',
    'description': 'Retrieve the list of available profession choices for user registration',
    'responses': {
        200: {
            'description': 'List of profession choices retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'message': {'type': 'string', 'example': 'Profession choices retrieved successfully'},
                    'professions': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'example': ['Software Engineer', 'Data Scientist', 'Product Manager']
                    }
                }
            }
        },
        500: {
            'description': 'Internal server error',
            'schema': {
                'type': 'object',
                'properties': {
                    'statusMessage': {'type': 'string'},
                    'statusCode': {'type': 'string'},
                    'requestId': {'type': 'string'}
                }
            }
        }
    }
})
def get_professions():
    """Get available profession choices"""
    try:
        logging.info("Fetching profession choices")
        
        professions = AuthService.get_profession_choices()
        
        return jsonify({
            'success': True,
            'message': 'Profession choices retrieved successfully',
            'professions': professions
        }), 200
        
    except CustomException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error in get_professions: {str(e)}")
        raise CustomException.service_error("Failed to fetch profession choices")

@auth_bp.route('/register', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Register a new user',
    'description': 'Register a new user with personal details',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['first_name', 'last_name', 'mobile_number', 'occupation'],
                'properties': {
                    'first_name': {
                        'type': 'string',
                        'example': 'John',
                        'description': 'User first name (max 100 characters)'
                    },
                    'last_name': {
                        'type': 'string',
                        'example': 'Doe',
                        'description': 'User last name (max 100 characters)'
                    },
                    'mobile_number': {
                        'type': 'string',
                        'example': '+1234567890',
                        'description': 'User mobile number (10 digits)'
                    },
                    'occupation': {
                        'type': 'string',
                        'example': 'Software Engineer',
                        'description': 'User occupation (must be from profession choices)'
                    }
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'User registered successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'message': {'type': 'string', 'example': 'User registered successfully'},
                    'user': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string', 'example': 'uuid'},
                            'first_name': {'type': 'string', 'example': 'John'},
                            'last_name': {'type': 'string', 'example': 'Doe'},
                            'mobile_number': {'type': 'string', 'example': '1234567890'},
                            'occupation': {'type': 'string', 'example': 'Software Engineer'},
                            'created_at': {'type': 'string', 'format': 'date-time'},
                            'updated_at': {'type': 'string', 'format': 'date-time'}
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Validation error',
            'schema': {
                'type': 'object',
                'properties': {
                    'statusMessage': {'type': 'string'},
                    'statusCode': {'type': 'string'},
                    'requestId': {'type': 'string'}
                }
            }
        },
        409: {
            'description': 'User already exists',
            'schema': {
                'type': 'object',
                'properties': {
                    'statusMessage': {'type': 'string'},
                    'statusCode': {'type': 'string'},
                    'requestId': {'type': 'string'}
                }
            }
        }
    }
})
def register():
    """Register a new user"""
    try:
        logging.info("User registration request received")
        
        # Get request data
        data = request.get_json()
        if not data:
            logging.error("Registration failed: No data provided")
            raise CustomException.validation_error("Request body is required")
        
        # Extract required fields
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        mobile_number = data.get('mobile_number')
        occupation = data.get('occupation')
        
        # Validate required fields
        if not all([first_name, last_name, mobile_number, occupation]):
            logging.error("Registration failed: Missing required fields")
            raise CustomException.validation_error("All fields are required: first_name, last_name, mobile_number, occupation")
        
        # Register user
        result = AuthService.register_user(first_name, last_name, mobile_number, occupation)
        
        return jsonify(result), 201
        
    except CustomException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error in register: {str(e)}")
        raise CustomException.service_error("Failed to register user")

@auth_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Initiate user login',
    'description': 'Start the login process by providing mobile number. OTP will be sent (for MVP, use 1234)',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['mobile_number'],
                'properties': {
                    'mobile_number': {
                        'type': 'string',
                        'example': '+1234567890',
                        'description': 'User mobile number (10 digits)'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'OTP sent successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'message': {'type': 'string', 'example': 'OTP sent to +1234567890. Please use OTP: 1234'},
                    'mobile_number': {'type': 'string', 'example': '1234567890'}
                }
            }
        },
        400: {
            'description': 'Validation error',
            'schema': {
                'type': 'object',
                'properties': {
                    'statusMessage': {'type': 'string'},
                    'statusCode': {'type': 'string'},
                    'requestId': {'type': 'string'}
                }
            }
        },
        404: {
            'description': 'User not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'statusMessage': {'type': 'string'},
                    'statusCode': {'type': 'string'},
                    'requestId': {'type': 'string'}
                }
            }
        }
    }
})
def login():
    """Initiate user login"""
    try:
        logging.info("User login request received")
        
        # Get request data
        data = request.get_json()
        if not data:
            logging.error("Login failed: No data provided")
            raise CustomException.validation_error("Request body is required")
        
        # Extract mobile number
        mobile_number = data.get('mobile_number')
        if not mobile_number:
            logging.error("Login failed: Mobile number is required")
            raise CustomException.validation_error("Mobile number is required")
        
        # Initiate login
        result = AuthService.login_user(mobile_number)
        
        return jsonify(result), 200
        
    except CustomException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error in login: {str(e)}")
        raise CustomException.service_error("Failed to initiate login")

@auth_bp.route('/verify-otp', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Verify OTP and complete login',
    'description': 'Verify the OTP and complete the login process. For MVP, use OTP: 1234',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['mobile_number', 'otp'],
                'properties': {
                    'mobile_number': {
                        'type': 'string',
                        'example': '+1234567890',
                        'description': 'User mobile number (10 digits)'
                    },
                    'otp': {
                        'type': 'string',
                        'example': '1234',
                        'description': 'OTP received (use 1234 for MVP)'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Login successful',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'message': {'type': 'string', 'example': 'Login successful'},
                    'user': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string', 'example': 'uuid'},
                            'first_name': {'type': 'string', 'example': 'John'},
                            'last_name': {'type': 'string', 'example': 'Doe'},
                            'mobile_number': {'type': 'string', 'example': '1234567890'},
                            'occupation': {'type': 'string', 'example': 'Software Engineer'},
                            'created_at': {'type': 'string', 'format': 'date-time'},
                            'updated_at': {'type': 'string', 'format': 'date-time'}
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Validation error or invalid OTP',
            'schema': {
                'type': 'object',
                'properties': {
                    'statusMessage': {'type': 'string'},
                    'statusCode': {'type': 'string'},
                    'requestId': {'type': 'string'}
                }
            }
        },
        404: {
            'description': 'User not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'statusMessage': {'type': 'string'},
                    'statusCode': {'type': 'string'},
                    'requestId': {'type': 'string'}
                }
            }
        }
    }
})
def verify_otp():
    """Verify OTP and complete login"""
    try:
        logging.info("OTP verification request received")
        
        # Get request data
        data = request.get_json()
        if not data:
            logging.error("OTP verification failed: No data provided")
            raise CustomException.validation_error("Request body is required")
        
        # Extract required fields
        mobile_number = data.get('mobile_number')
        otp = data.get('otp')
        
        # Validate required fields
        if not all([mobile_number, otp]):
            logging.error("OTP verification failed: Missing required fields")
            raise CustomException.validation_error("Mobile number and OTP are required")
        
        # Verify OTP
        result = AuthService.verify_otp(mobile_number, otp)
        
        return jsonify(result), 200
        
    except CustomException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error in verify_otp: {str(e)}")
        raise CustomException.service_error("Failed to verify OTP")

@auth_bp.route('/get/user/<string:user_id>', methods=['GET'])
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Get user by ID',
    'description': 'Retrieve user information by user UUID',
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'User UUID'
        }
    ],
    'responses': {
        200: {
            'description': 'User retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'string', 'example': 'uuid'},
                    'first_name': {'type': 'string', 'example': 'John'},
                    'last_name': {'type': 'string', 'example': 'Doe'},
                    'mobile_number': {'type': 'string', 'example': '1234567890'},
                    'occupation': {'type': 'string', 'example': 'Software Engineer'},
                    'created_at': {'type': 'string', 'format': 'date-time'},
                    'updated_at': {'type': 'string', 'format': 'date-time'}
                }
            }
        },
        404: {
            'description': 'User not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'statusMessage': {'type': 'string'},
                    'statusCode': {'type': 'string'},
                    'requestId': {'type': 'string'}
                }
            }
        }
    }
})
def get_user(user_id):
    """Get user by ID"""
    try:
        logging.info(f"Get user request received for ID: {user_id}")
        
        # Get user
        user = AuthService.get_user_by_id(user_id)
        
        return jsonify(user), 200
        
    except CustomException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error in get_user: {str(e)}")
        raise CustomException.service_error("Failed to fetch user") 