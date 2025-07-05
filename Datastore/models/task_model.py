import logging
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from Config.database_config import db
from Exceptions.custom_exception import CustomException

class Task(db.Model):
    """
    Task model for task management system
    """
    __tablename__ = 'tasks'
    
    # Priority choices
    PRIORITY_CHOICES = ['Low', 'Medium', 'High', 'Critical']
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Task details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    deadline = Column(DateTime, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    priority = Column(String(20), default='Medium', nullable=False)  # AI-generated priority
    
    # Foreign key to user
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __init__(self, title, deadline, user_id, description=None, completed=False, priority='Medium'):
        self.title = title
        self.description = description
        self.deadline = deadline
        self.completed = completed
        self.priority = priority
        self.user_id = user_id
        logging.info(f"Creating new task: {title} for user_id: {user_id} with priority: {priority}")
    
    def validate_title(self):
        """
        Validate task title
        """
        try:
            title = str(self.title or "")
            if not title or not title.strip():
                logging.error("Task title validation failed: Title is required")
                raise CustomException.validation_error("Task title is required")
            
            if len(title) > 200:
                logging.error(f"Task title validation failed: Title too long - {len(title)} characters")
                raise CustomException.validation_error("Task title cannot exceed 500 characters")
            
            logging.debug(f"Task title validation successful: {title}")
            return True
            
        except CustomException:
            raise
        except Exception as e:
            logging.error(f"Unexpected error during title validation: {str(e)}")
            raise CustomException.validation_error("Invalid task title")
    
    def validate_description(self):
        """
        Validate task description
        """
        try:
            description = str(self.description or "")
            if description and len(description) > 500:
                logging.error(f"Task description validation failed: Description too long - {len(description)} characters")
                raise CustomException.validation_error("Task description cannot exceed 500 characters")
            
            logging.debug("Task description validation successful")
            return True
            
        except CustomException:
            raise
        except Exception as e:
            logging.error(f"Unexpected error during description validation: {str(e)}")
            raise CustomException.validation_error("Invalid task description")
    
    def validate_deadline(self):
        """
        Validate task deadline
        """
        try:
            deadline = self.deadline
            if deadline is None:
                logging.error("Task deadline validation failed: Deadline is required")
                raise CustomException.validation_error("Task deadline is required")
            
            # Convert string to datetime if needed
            if isinstance(deadline, str):
                try:
                    self.deadline = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                except ValueError:
                    logging.error(f"Invalid deadline format: {deadline}")
                    raise CustomException.validation_error("Invalid deadline format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
            
            logging.debug(f"Task deadline validation successful: {self.deadline}")
            return True
            
        except CustomException:
            raise
        except Exception as e:
            logging.error(f"Unexpected error during deadline validation: {str(e)}")
            raise CustomException.validation_error("Invalid task deadline")
    
    def validate_priority(self):
        """
        Validate task priority
        """
        try:
            priority = self.priority
            if priority not in self.PRIORITY_CHOICES:
                logging.error(f"Task priority validation failed: Invalid priority - {priority}")
                raise CustomException.validation_error(f"Priority must be one of {self.PRIORITY_CHOICES}")
            
            logging.debug(f"Task priority validation successful: {priority}")
            return True
            
        except CustomException:
            raise
        except Exception as e:
            logging.error(f"Unexpected error during priority validation: {str(e)}")
            raise CustomException.validation_error("Invalid task priority")
    
    def validate_user_id(self):
        """
        Validate user_id
        """
        try:
            user_id = self.user_id
            if user_id is None:
                logging.error("Task user_id validation failed: User ID is required")
                raise CustomException.validation_error("User ID is required")
            
            logging.debug(f"Task user_id validation successful: {user_id}")
            return True
            
        except CustomException:
            raise
        except Exception as e:
            logging.error(f"Unexpected error during user_id validation: {str(e)}")
            raise CustomException.validation_error("Invalid user ID")
    
    def validate(self):
        """
        Validate all task fields
        """
        try:
            logging.info(f"Starting validation for task: {self.title}")
            
            self.validate_title()
            self.validate_description()
            self.validate_deadline()
            self.validate_priority()
            self.validate_user_id()
            
            logging.info(f"Task validation successful: {self.title}")
            return True
            
        except CustomException:
            raise
        except Exception as e:
            logging.error(f"Unexpected error during task validation: {str(e)}")
            raise CustomException.validation_error("Task validation failed")
    
    def get_status(self):
        """
        Dynamically compute task status based on deadline and completion
        """
        try:
            completed = bool(self.completed)
            deadline = self.deadline
            if completed:
                return "completed"
            elif deadline and deadline < datetime.now():
                return "missed"
            else:
                return "upcoming"
        except Exception as e:
            logging.error(f"Error computing task status: {str(e)}")
            return "unknown"
    
    def is_past_deadline(self):
        """
        Check if task is past deadline
        """
        try:
            deadline = self.deadline
            return deadline and deadline < datetime.now()
        except Exception as e:
            logging.error(f"Error checking past deadline: {str(e)}")
            return False
    
    def mark_completed(self):
        """
        Mark task as completed
        """
        try:
            self.completed = True
            logging.info(f"Task marked as completed: {self.title}")
            return True
        except Exception as e:
            logging.error(f"Error marking task as completed: {str(e)}")
            raise CustomException.service_error("Failed to mark task as completed")
    
    def mark_uncompleted(self):
        """
        Mark task as uncompleted
        """
        try:
            self.completed = False
            logging.info(f"Task marked as uncompleted: {self.title}")
            return True
        except Exception as e:
            logging.error(f"Error marking task as uncompleted: {str(e)}")
            raise CustomException.service_error("Failed to mark task as uncompleted")
    
    def to_dict(self):
        """
        Convert task object to dictionary
        """
        return {
            'id': str(self.id),  # Convert UUID to string for JSON serialization
            'title': self.title,
            'description': self.description,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'completed': self.completed,
            'priority': self.priority,
            'status': self.get_status(),
            'is_past_deadline': self.is_past_deadline(),
            'user_id': str(self.user_id),  # Convert UUID to string for JSON serialization
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Task {self.title} - {self.get_status()} - Priority: {self.priority}>' 