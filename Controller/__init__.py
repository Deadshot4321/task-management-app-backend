"""
Controller module for Task Management System
Contains all API controllers and route definitions
"""

from .auth_controller import auth_bp
from .task_controller import task_bp

__all__ = ['auth_bp', 'task_bp']
