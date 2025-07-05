"""
Datastore module for Task Management System
Contains all database models and related functionality
"""

from .models import User, Task, Tag
from Config.database_config import db

__all__ = ['User', 'Task', 'Tag', 'db']
