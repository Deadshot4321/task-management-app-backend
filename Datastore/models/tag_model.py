import logging
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, func, Table, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from Config.database_config import db
from Exceptions.custom_exception import CustomException

# Association table for Many-to-Many relationship between Task and Tag
task_tags = Table(
    'task_tags',
    db.Model.metadata,
    Column('task_id', UUID(as_uuid=True), ForeignKey('tasks.id'), primary_key=True),
    Column('tag_id', UUID(as_uuid=True), ForeignKey('tags.id'), primary_key=True),
    Column('created_at', DateTime, default=func.now())
)

class Tag(db.Model):
    """
    Tag model for task categorization system
    """
    __tablename__ = 'tags'
    
    # Predefined tag choices for AI generation
    PREDEFINED_TAGS = [
        'Work', 'Personal', 'Health', 'Finance', 'Learning', 
        'Urgent', 'Shopping', 'Travel', 'Meeting', 'Project'
    ]
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Tag details
    name = Column(String(50), nullable=False, unique=True)
    color = Column(String(7), nullable=True)  # Hex color code for UI
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship with tasks (Many-to-Many)
    tasks = relationship('Task', secondary=task_tags, back_populates='tags')
    
    def __init__(self, name, color=None):
        self.name = name.strip().title()  # Normalize tag name
        self.color = color or self._get_default_color()
        logging.info(f"Creating new tag: {self.name}")
    
    def _get_default_color(self):
        """Get default color based on tag name"""
        color_mapping = {
            'Work': '#58a6ff',      # Blue
            'Personal': '#3fb950',   # Green
            'Health': '#f85149',     # Red
            'Finance': '#f7cc02',    # Yellow
            'Learning': '#a5a5a5',   # Gray
            'Urgent': '#ff6b35',     # Orange
            'Shopping': '#9d4edd',   # Purple
            'Travel': '#06d6a0',     # Teal
            'Meeting': '#ffd60a',    # Gold
            'Project': '#003566'     # Dark Blue
        }
        return color_mapping.get(self.name, '#58a6ff')
    
    def validate_name(self):
        """
        Validate tag name
        """
        try:
            name = str(self.name or "")
            if not name or not name.strip():
                logging.error("Tag name validation failed: Name is required")
                raise CustomException.validation_error("Tag name is required")
            
            if len(name) > 50:
                logging.error(f"Tag name validation failed: Name too long - {len(name)} characters")
                raise CustomException.validation_error("Tag name cannot exceed 50 characters")
            
            # Check for invalid characters
            if not name.replace(' ', '').replace('-', '').replace('_', '').isalnum():
                logging.error(f"Tag name validation failed: Invalid characters in name - {name}")
                raise CustomException.validation_error("Tag name can only contain letters, numbers, spaces, hyphens, and underscores")
            
            logging.debug(f"Tag name validation successful: {name}")
            return True
            
        except CustomException:
            raise
        except Exception as e:
            logging.error(f"Unexpected error during tag name validation: {str(e)}")
            raise CustomException.validation_error("Invalid tag name")
    
    def validate_color(self):
        """
        Validate tag color (hex format)
        """
        try:
            if self.color:
                color = str(self.color)
                if not color.startswith('#') or len(color) != 7:
                    logging.error(f"Tag color validation failed: Invalid hex format - {color}")
                    raise CustomException.validation_error("Color must be in hex format (#RRGGBB)")
                
                # Validate hex characters
                try:
                    int(color[1:], 16)
                except ValueError:
                    logging.error(f"Tag color validation failed: Invalid hex characters - {color}")
                    raise CustomException.validation_error("Color must contain valid hex characters")
            
            logging.debug(f"Tag color validation successful: {self.color}")
            return True
            
        except CustomException:
            raise
        except Exception as e:
            logging.error(f"Unexpected error during color validation: {str(e)}")
            raise CustomException.validation_error("Invalid tag color")
    
    def validate(self):
        """
        Validate all tag fields
        """
        try:
            logging.info(f"Starting validation for tag: {self.name}")
            
            self.validate_name()
            self.validate_color()
            
            logging.info(f"Tag validation successful: {self.name}")
            return True
            
        except CustomException:
            raise
        except Exception as e:
            logging.error(f"Unexpected error during tag validation: {str(e)}")
            raise CustomException.validation_error("Tag validation failed")
    
    def to_dict(self):
        """
        Convert tag object to dictionary
        """
        return {
            'id': str(self.id),  # Convert UUID to string for JSON serialization
            'name': self.name,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def get_or_create(name, color=None):
        """
        Get existing tag or create new one
        
        Args:
            name (str): Tag name
            color (str): Optional hex color code
            
        Returns:
            Tag: Tag object
        """
        try:
            normalized_name = name.strip().title()
            
            # Try to find existing tag
            existing_tag = Tag.query.filter_by(name=normalized_name).first()
            if existing_tag:
                logging.debug(f"Found existing tag: {normalized_name}")
                return existing_tag
            
            # Create new tag
            new_tag = Tag(name=normalized_name, color=color)
            new_tag.validate()
            
            db.session.add(new_tag)
            db.session.flush()  # Get ID without committing transaction
            
            logging.info(f"Created new tag: {normalized_name}")
            return new_tag
            
        except Exception as e:
            logging.error(f"Error in get_or_create for tag {name}: {str(e)}")
            raise CustomException.service_error("Failed to get or create tag")
    
    def __repr__(self):
        return f'<Tag {self.name}>' 