import logging
import re
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from Config.database_config import db
from Exceptions.custom_exception import CustomException

class User(db.Model):
    """
    User model for task management system
    """
    __tablename__ = 'users'
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User details
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    mobile_number = Column(String(15), unique=True, nullable=False)
    occupation = Column(String(100), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship with tasks
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')
    
    # Top 30 profession choices + None option
    PROFESSION_CHOICES = [
        'Software Engineer',
        'Data Scientist', 
        'Product Manager',
        'Marketing Manager',
        'Sales Manager',
        'Business Analyst',
        'Project Manager',
        'Graphic Designer',
        'UI/UX Designer',
        'Content Writer',
        'Digital Marketer',
        'Financial Analyst',
        'Accountant',
        'Human Resources Manager',
        'Operations Manager',
        'Customer Success Manager',
        'DevOps Engineer',
        'Quality Assurance Engineer',
        'Consultant',
        'Teacher/Educator',
        'Doctor/Physician',
        'Lawyer',
        'Architect',
        'Civil Engineer',
        'Mechanical Engineer',
        'Electrical Engineer',
        'Research Scientist',
        'Entrepreneur',
        'Freelancer',
        'Student',
        'None'
    ]
    
    def __init__(self, first_name, last_name, mobile_number, occupation):
        self.first_name = first_name
        self.last_name = last_name
        self.mobile_number = mobile_number
        self.occupation = occupation
        logging.info(f"Creating new user: {first_name} {last_name} - {mobile_number}")
    
    def validate_mobile_number(self):
        """
        Validate mobile number - must be 10 digits
        """
        try:
            mobile_num = str(self.mobile_number or "")
            if not mobile_num:
                logging.error("Mobile number validation failed: Mobile number is required")
                raise CustomException.validation_error("Mobile number is required")
            
            # Remove any non-digit characters
            digits_only = re.sub(r'\D', '', mobile_num)
            
            if len(digits_only) != 10:
                logging.error(f"Mobile number validation failed: {mobile_num} - Must be 10 digits")
                raise CustomException.validation_error("Mobile number must be exactly 10 digits")
            
            # Update mobile number to digits only
            self.mobile_number = digits_only
            logging.debug(f"Mobile number validation successful: {self.mobile_number}")
            return True
            
        except CustomException:
            raise
        except Exception as e:
            logging.error(f"Unexpected error during mobile number validation: {str(e)}")
            raise CustomException.validation_error("Invalid mobile number format")
    
    def validate_occupation(self):
        """
        Validate occupation against predefined choices
        """
        try:
            if self.occupation not in self.PROFESSION_CHOICES:
                logging.error(f"Occupation validation failed: {self.occupation} not in allowed choices")
                raise CustomException.validation_error(f"Invalid occupation. Must be one of: {', '.join(self.PROFESSION_CHOICES)}")
            
            logging.debug(f"Occupation validation successful: {self.occupation}")
            return True
            
        except CustomException:
            raise
        except Exception as e:
            logging.error(f"Unexpected error during occupation validation: {str(e)}")
            raise CustomException.validation_error("Invalid occupation")
    
    def validate_name(self):
        """
        Validate first and last name
        """
        try:
            first_name = str(self.first_name or "")
            last_name = str(self.last_name or "")
            
            if not first_name or not first_name.strip():
                logging.error("Name validation failed: First name is required")
                raise CustomException.validation_error("First name is required")
            
            if not last_name or not last_name.strip():
                logging.error("Name validation failed: Last name is required")
                raise CustomException.validation_error("Last name is required")
            
            if len(first_name) > 100:
                logging.error(f"Name validation failed: First name too long - {len(first_name)} characters")
                raise CustomException.validation_error("First name cannot exceed 100 characters")
            
            if len(last_name) > 100:
                logging.error(f"Name validation failed: Last name too long - {len(last_name)} characters")
                raise CustomException.validation_error("Last name cannot exceed 100 characters")
            
            logging.debug(f"Name validation successful: {first_name} {last_name}")
            return True
            
        except CustomException:
            raise
        except Exception as e:
            logging.error(f"Unexpected error during name validation: {str(e)}")
            raise CustomException.validation_error("Invalid name format")
    
    def validate(self):
        """
        Validate all user fields
        """
        try:
            logging.info(f"Starting validation for user: {self.first_name} {self.last_name}")
            
            self.validate_name()
            self.validate_mobile_number()
            self.validate_occupation()
            
            logging.info(f"User validation successful: {self.first_name} {self.last_name}")
            return True
            
        except CustomException:
            raise
        except Exception as e:
            logging.error(f"Unexpected error during user validation: {str(e)}")
            raise CustomException.validation_error("User validation failed")
    
    def to_dict(self):
        """
        Convert user object to dictionary
        """
        return {
            'id': str(self.id),  # Convert UUID to string for JSON serialization
            'first_name': self.first_name,
            'last_name': self.last_name,
            'mobile_number': self.mobile_number,
            'occupation': self.occupation,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.first_name} {self.last_name} - {self.mobile_number}>' 