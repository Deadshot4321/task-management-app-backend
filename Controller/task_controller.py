import logging
from flask import Blueprint, request, jsonify
from flasgger import swag_from
from Service.task_service import TaskService
from Exceptions.custom_exception import CustomException
from Config.logging_config import LoggingConfig

# Create Blueprint with new clear endpoint structure
task_bp = Blueprint('tasks', __name__, url_prefix='/api/v1')

@task_bp.before_request
def set_request_context():
    """Set request context for logging"""
    LoggingConfig.set_request_context()

def get_user_id_from_request():
    """Extract user_id from request headers or query params"""
    # For MVP, we'll use a simple header approach
    # In production, this would be extracted from JWT token
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        user_id = request.args.get('user_id')
    
    if not user_id:
        logging.error("User ID not provided in request")
        raise CustomException.validation_error("User ID is required. Provide X-User-ID header or user_id query parameter")
    
    # Validate UUID format
    try:
        import uuid
        uuid.UUID(user_id)  # This will raise ValueError if invalid
        return user_id  # Return as string, services will handle conversion
    except ValueError:
        logging.error(f"Invalid user ID format: {user_id}")
        raise CustomException.validation_error("User ID must be a valid UUID")

@task_bp.route('/create/task', methods=['POST'])
@swag_from({
    'tags': ['Tasks'],
    'summary': 'Create a new task',
    'description': 'Create a new task for the authenticated user',
    'parameters': [
        {
            'name': 'X-User-ID',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'User ID (for MVP authentication)'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['title', 'deadline'],
                'properties': {
                    'title': {
                        'type': 'string',
                        'example': 'Complete project documentation',
                        'description': 'Task title (max 500 characters)'
                    },
                    'description': {
                        'type': 'string',
                        'example': 'Write comprehensive API documentation',
                        'description': 'Task description (max 500 characters, optional)'
                    },
                    'deadline': {
                        'type': 'string',
                        'format': 'date-time',
                        'example': '2024-01-15T18:00:00Z',
                        'description': 'Task deadline in ISO format'
                    }
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'Task created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'message': {'type': 'string', 'example': 'Task created successfully'},
                    'task': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string', 'example': 'uuid'},
                            'title': {'type': 'string', 'example': 'Complete project documentation'},
                            'description': {'type': 'string', 'example': 'Write comprehensive API documentation'},
                            'deadline': {'type': 'string', 'format': 'date-time'},
                            'completed': {'type': 'boolean', 'example': False},
                            'status': {'type': 'string', 'example': 'upcoming'},
                            'is_past_deadline': {'type': 'boolean', 'example': False},
                            'user_id': {'type': 'string', 'example': 'uuid'},
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
def create_task():
    """Create a new task"""
    try:
        logging.info("Create task request received")
        
        # Get user ID
        user_id = get_user_id_from_request()
        
        # Get request data
        data = request.get_json()
        if not data:
            logging.error("Task creation failed: No data provided")
            raise CustomException.validation_error("Request body is required")
        
        # Extract required fields
        title = data.get('title')
        deadline = data.get('deadline')
        description = data.get('description')
        
        # Validate required fields
        if not all([title, deadline]):
            logging.error("Task creation failed: Missing required fields")
            raise CustomException.validation_error("Title and deadline are required")
        
        # Create task
        result = TaskService.create_task(title, deadline, user_id, description)
        
        return jsonify(result), 201
        
    except CustomException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error in create_task: {str(e)}")
        raise CustomException.service_error("Failed to create task")

@task_bp.route('/get/tasks', methods=['GET'])
@swag_from({
    'tags': ['Tasks'],
    'summary': 'Get all tasks for user',
    'description': 'Retrieve all tasks for the authenticated user with optional filtering and sorting',
    'parameters': [
        {
            'name': 'X-User-ID',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'User ID (for MVP authentication)'
        },
        {
            'name': 'status',
            'in': 'query',
            'type': 'string',
            'enum': ['upcoming', 'completed', 'missed'],
            'description': 'Filter tasks by status'
        },
        {
            'name': 'sort_by',
            'in': 'query',
            'type': 'string',
            'enum': ['deadline', 'created_at', 'title'],
            'default': 'deadline',
            'description': 'Sort tasks by field'
        },
        {
            'name': 'sort_order',
            'in': 'query',
            'type': 'string',
            'enum': ['asc', 'desc'],
            'default': 'asc',
            'description': 'Sort order'
        }
    ],
    'responses': {
        200: {
            'description': 'Tasks retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'tasks': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'string', 'example': 'uuid'},
                                'title': {'type': 'string', 'example': 'Complete project documentation'},
                                'description': {'type': 'string', 'example': 'Write comprehensive API documentation'},
                                'deadline': {'type': 'string', 'format': 'date-time'},
                                'completed': {'type': 'boolean', 'example': False},
                                'status': {'type': 'string', 'example': 'upcoming'},
                                'is_past_deadline': {'type': 'boolean', 'example': False},
                                'user_id': {'type': 'string', 'example': 'uuid'},
                                'created_at': {'type': 'string', 'format': 'date-time'},
                                'updated_at': {'type': 'string', 'format': 'date-time'}
                            }
                        }
                    },
                    'total': {'type': 'integer', 'example': 10},
                    'user_id': {'type': 'string', 'example': 'uuid'}
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
def get_tasks():
    """Get all tasks for user"""
    try:
        logging.info("Get tasks request received")
        
        # Get user ID
        user_id = get_user_id_from_request()
        
        # Get query parameters
        status = request.args.get('status')
        sort_by = request.args.get('sort_by', 'deadline')
        sort_order = request.args.get('sort_order', 'asc')
        
        # Get tasks
        result = TaskService.get_user_tasks(user_id, status, sort_by, sort_order)
        
        return jsonify(result), 200
        
    except CustomException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error in get_tasks: {str(e)}")
        raise CustomException.service_error("Failed to fetch tasks")

@task_bp.route('/get/task/<string:task_id>', methods=['GET'])
@swag_from({
    'tags': ['Tasks'],
    'summary': 'Get task by ID',
    'description': 'Retrieve a specific task by its ID',
    'parameters': [
        {
            'name': 'X-User-ID',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'User ID (for MVP authentication)'
        },
        {
            'name': 'task_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Task ID'
        }
    ],
    'responses': {
        200: {
            'description': 'Task retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'string', 'example': 'uuid'},
                    'title': {'type': 'string', 'example': 'Complete project documentation'},
                    'description': {'type': 'string', 'example': 'Write comprehensive API documentation'},
                    'deadline': {'type': 'string', 'format': 'date-time'},
                    'completed': {'type': 'boolean', 'example': False},
                    'status': {'type': 'string', 'example': 'upcoming'},
                    'is_past_deadline': {'type': 'boolean', 'example': False},
                    'user_id': {'type': 'string', 'example': 'uuid'},
                    'created_at': {'type': 'string', 'format': 'date-time'},
                    'updated_at': {'type': 'string', 'format': 'date-time'}
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
            'description': 'Task not found',
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
def get_task(task_id):
    """Get task by ID"""
    try:
        logging.info(f"Get task request received for ID: {task_id}")
        
        # Get user ID
        user_id = get_user_id_from_request()
        
        # Get task
        task = TaskService.get_task_by_id(task_id, user_id)
        
        return jsonify(task), 200
        
    except CustomException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error in get_task: {str(e)}")
        raise CustomException.service_error("Failed to fetch task")

@task_bp.route('/update/task/<string:task_id>', methods=['PUT'])
@swag_from({
    'tags': ['Tasks'],
    'summary': 'Update task',
    'description': 'Update task fields. Can be used for partial updates (e.g., just marking as complete) or complete updates.',
    'parameters': [
        {
            'name': 'X-User-ID',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'User ID (for MVP authentication)'
        },
        {
            'name': 'task_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Task ID'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {
                        'type': 'string',
                        'example': 'Updated task title',
                        'description': 'Task title (max 500 characters)'
                    },
                    'description': {
                        'type': 'string',
                        'example': 'Updated task description',
                        'description': 'Task description (max 500 characters)'
                    },
                    'deadline': {
                        'type': 'string',
                        'format': 'date-time',
                        'example': '2024-01-20T18:00:00Z',
                        'description': 'Task deadline in ISO format'
                    },
                    'completed': {
                        'type': 'boolean',
                        'example': True,
                        'description': 'Task completion status'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Task updated successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'message': {'type': 'string', 'example': 'Task updated successfully'},
                    'task': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string', 'example': 'uuid'},
                            'title': {'type': 'string', 'example': 'Updated task title'},
                            'description': {'type': 'string', 'example': 'Updated task description'},
                            'deadline': {'type': 'string', 'format': 'date-time'},
                            'completed': {'type': 'boolean', 'example': True},
                            'status': {'type': 'string', 'example': 'completed'},
                            'is_past_deadline': {'type': 'boolean', 'example': False},
                            'user_id': {'type': 'string', 'example': 'uuid'},
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
        404: {
            'description': 'Task not found',
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
def update_task(task_id):
    """Update task - allows partial updates"""
    try:
        logging.info(f"Update task request received for ID: {task_id}")
        
        # Get user ID
        user_id = get_user_id_from_request()
        
        # Get request data
        data = request.get_json()
        if not data:
            logging.error("Task update failed: No data provided")
            raise CustomException.validation_error("Request body is required")
        
        # Extract fields (all optional for flexible updates)
        title = data.get('title')
        description = data.get('description')
        deadline = data.get('deadline')
        completed = data.get('completed')
        
        # At least one field should be provided
        if not any([title, description, deadline, completed is not None]):
            logging.error("Task update failed: No fields to update")
            raise CustomException.validation_error("At least one field must be provided for update")
        
        # Update task
        result = TaskService.update_task(task_id, user_id, title, description, deadline, completed)
        
        return jsonify(result), 200
        
    except CustomException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error in update_task: {str(e)}")
        raise CustomException.service_error("Failed to update task")

@task_bp.route('/complete/task/<string:task_id>', methods=['PUT'])
@swag_from({
    'tags': ['Tasks'],
    'summary': 'Mark task as complete',
    'description': 'Mark a specific task as complete',
    'parameters': [
        {
            'name': 'X-User-ID',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'User ID (for MVP authentication)'
        },
        {
            'name': 'task_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Task ID'
        }
    ],
    'responses': {
        200: {
            'description': 'Task marked as complete successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'message': {'type': 'string', 'example': 'Task marked as complete successfully'},
                    'task': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string', 'example': 'uuid'},
                            'title': {'type': 'string', 'example': 'Complete project documentation'},
                            'description': {'type': 'string', 'example': 'Write comprehensive API documentation'},
                            'deadline': {'type': 'string', 'format': 'date-time'},
                            'completed': {'type': 'boolean', 'example': True},
                            'status': {'type': 'string', 'example': 'completed'},
                            'is_past_deadline': {'type': 'boolean', 'example': False},
                            'user_id': {'type': 'string', 'example': 'uuid'},
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
        404: {
            'description': 'Task not found',
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
def complete_task(task_id):
    """Mark task as complete"""
    try:
        logging.info(f"Complete task request received for ID: {task_id}")
        
        # Get user ID
        user_id = get_user_id_from_request()
        
        # Mark task as complete
        result = TaskService.update_task(task_id, user_id, None, None, None, True)
        
        return jsonify(result), 200
        
    except CustomException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error in complete_task: {str(e)}")
        raise CustomException.service_error("Failed to complete task")

@task_bp.route('/delete/task/<string:task_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Tasks'],
    'summary': 'Delete task',
    'description': 'Delete a specific task by its ID',
    'parameters': [
        {
            'name': 'X-User-ID',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'User ID (for MVP authentication)'
        },
        {
            'name': 'task_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Task ID'
        }
    ],
    'responses': {
        200: {
            'description': 'Task deleted successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'message': {'type': 'string', 'example': 'Task deleted successfully'},
                    'deleted_task_id': {'type': 'string', 'example': 'uuid'}
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
            'description': 'Task not found',
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
def delete_task(task_id):
    """Delete task"""
    try:
        logging.info(f"Delete task request received for ID: {task_id}")
        
        # Get user ID
        user_id = get_user_id_from_request()
        
        # Delete task
        result = TaskService.delete_task(task_id, user_id)
        
        return jsonify(result), 200
        
    except CustomException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error in delete_task: {str(e)}")
        raise CustomException.service_error("Failed to delete task")

@task_bp.route('/get/task/statistics', methods=['GET'])
@swag_from({
    'tags': ['Tasks'],
    'summary': 'Get task statistics',
    'description': 'Get task statistics for the authenticated user',
    'parameters': [
        {
            'name': 'X-User-ID',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'User ID (for MVP authentication)'
        }
    ],
    'responses': {
        200: {
            'description': 'Statistics retrieved successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean', 'example': True},
                    'statistics': {
                        'type': 'object',
                        'properties': {
                            'total_tasks': {'type': 'integer', 'example': 50},
                            'completed_tasks': {'type': 'integer', 'example': 30},
                            'upcoming_tasks': {'type': 'integer', 'example': 15},
                            'missed_tasks': {'type': 'integer', 'example': 5},
                            'completion_rate': {'type': 'number', 'example': 60.0}
                        }
                    },
                    'user_id': {'type': 'string', 'example': 'uuid'}
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
        }
    }
})
def get_task_statistics():
    """Get task statistics"""
    try:
        logging.info("Get task statistics request received")
        
        # Get user ID
        user_id = get_user_id_from_request()
        
        # Get statistics
        result = TaskService.get_task_statistics(user_id)
        
        return jsonify(result), 200
        
    except CustomException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error in get_task_statistics: {str(e)}")
        raise CustomException.service_error("Failed to fetch task statistics") 