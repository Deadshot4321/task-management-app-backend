import logging
import uuid
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from Config.database_config import db
from Datastore.models.user_model import User
from Exceptions.custom_exception import CustomException

class AuthService:
    """
    Authentication service for user registration, login, and OTP verification
    """
    
    # Default OTP for MVP
    DEFAULT_OTP = "1234"
    
    @staticmethod
    def get_profession_choices():
        """
        Get available profession choices
        """
        try:
            logging.debug("Fetching profession choices")
            return User.PROFESSION_CHOICES
        except Exception as e:
            logging.error(f"Error fetching profession choices: {str(e)}")
            raise CustomException.service_error("Failed to fetch profession choices")
    
    @staticmethod
    def register_user(first_name, last_name, mobile_number, occupation):
        """
        Register a new user
        
        Args:
            first_name (str): User's first name
            last_name (str): User's last name
            mobile_number (str): User's mobile number
            occupation (str): User's occupation
            
        Returns:
            dict: User data if successful
            
        Raises:
            CustomException: If registration fails
        """
        try:
            logging.info(f"Starting user registration for: {first_name} {last_name} - {mobile_number}")
            
            # Check if user already exists
            existing_user = User.query.filter_by(mobile_number=mobile_number).first()
            if existing_user:
                logging.warning(f"Registration failed: User already exists with mobile number {mobile_number}")
                raise CustomException.validation_error("User with this mobile number already exists")
            
            # Create new user
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                mobile_number=mobile_number,
                occupation=occupation
            )
            
            # Validate user data
            new_user.validate()
            
            # Save to database
            db.session.add(new_user)
            db.session.commit()
            
            logging.info(f"User registered successfully: {new_user.id} - {first_name} {last_name}")
            return {
                "success": True,
                "message": "User registered successfully",
                "user": new_user.to_dict()
            }
            
        except CustomException:
            db.session.rollback()
            raise
        except IntegrityError as e:
            db.session.rollback()
            logging.error(f"Database integrity error during registration: {str(e)}")
            raise CustomException.database_error("User with this mobile number already exists")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Unexpected error during user registration: {str(e)}")
            raise CustomException.service_error("Failed to register user")
    
    @staticmethod
    def login_user(mobile_number):
        """
        Initiate login process for user
        
        Args:
            mobile_number (str): User's mobile number
            
        Returns:
            dict: Login response
            
        Raises:
            CustomException: If login initiation fails
        """
        try:
            logging.info(f"Starting login process for mobile number: {mobile_number}")
            
            # Validate mobile number format
            if not mobile_number:
                logging.error("Login failed: Mobile number is required")
                raise CustomException.validation_error("Mobile number is required")
            
            # Clean mobile number (remove non-digits)
            import re
            clean_mobile = re.sub(r'\D', '', mobile_number)
            
            if len(clean_mobile) != 10:
                logging.error(f"Login failed: Invalid mobile number format - {mobile_number}")
                raise CustomException.validation_error("Mobile number must be exactly 10 digits")
            
            # Check if user exists
            user = User.query.filter_by(mobile_number=clean_mobile).first()
            if not user:
                logging.warning(f"Login failed: User not found with mobile number {clean_mobile}")
                raise CustomException.not_found_error("User not found with this mobile number")
            
            logging.info(f"Login initiated for user: {user.id} - {user.first_name} {user.last_name}")
            return {
                "success": True,
                "message": f"OTP sent to {mobile_number}. Please use OTP: {AuthService.DEFAULT_OTP}",
                "mobile_number": clean_mobile
            }
            
        except CustomException:
            raise
        except Exception as e:
            logging.error(f"Unexpected error during login initiation: {str(e)}")
            raise CustomException.service_error("Failed to initiate login")
    
    @staticmethod
    def verify_otp(mobile_number, otp):
        """
        Verify OTP and complete login
        
        Args:
            mobile_number (str): User's mobile number
            otp (str): OTP entered by user
            
        Returns:
            dict: Login success response with user data
            
        Raises:
            CustomException: If OTP verification fails
        """
        try:
            logging.info(f"Starting OTP verification for mobile number: {mobile_number}")
            
            # Validate inputs
            if not mobile_number or not otp:
                logging.error("OTP verification failed: Mobile number and OTP are required")
                raise CustomException.validation_error("Mobile number and OTP are required")
            
            # Clean mobile number
            import re
            clean_mobile = re.sub(r'\D', '', mobile_number)
            
            # Verify OTP
            if otp != AuthService.DEFAULT_OTP:
                logging.warning(f"OTP verification failed: Invalid OTP {otp} for mobile {clean_mobile}")
                raise CustomException.validation_error("Invalid OTP. Please try again.")
            
            # Get user
            user = User.query.filter_by(mobile_number=clean_mobile).first()
            if not user:
                logging.error(f"OTP verification failed: User not found with mobile number {clean_mobile}")
                raise CustomException.not_found_error("User not found")
            
            logging.info(f"OTP verification successful for user: {user.id} - {user.first_name} {user.last_name}")
            return {
                "success": True,
                "message": "Login successful",
                "user": user.to_dict()
            }
            
        except CustomException:
            raise
        except Exception as e:
            logging.error(f"Unexpected error during OTP verification: {str(e)}")
            raise CustomException.service_error("Failed to verify OTP")
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        Get user by ID
        
        Args:
            user_id (str): User's UUID as string
            
        Returns:
            dict: User data
            
        Raises:
            CustomException: If user not found
        """
        try:
            logging.debug(f"Fetching user by ID: {user_id}")
            
            if not user_id:
                logging.error("Get user failed: User ID is required")
                raise CustomException.validation_error("User ID is required")
            
            # Convert string UUID to UUID object
            try:
                user_uuid = uuid.UUID(user_id)
            except ValueError:
                logging.error(f"Invalid UUID format: {user_id}")
                raise CustomException.validation_error("User ID must be a valid UUID")
            
            user = User.query.get(user_uuid)
            if not user:
                logging.warning(f"User not found with ID: {user_id}")
                raise CustomException.not_found_error("User not found")
            
            logging.debug(f"User fetched successfully: {user.id} - {user.first_name} {user.last_name}")
            return user.to_dict()
            
        except CustomException:
            raise
        except Exception as e:
            logging.error(f"Unexpected error while fetching user: {str(e)}")
            raise CustomException.service_error("Failed to fetch user")
    
    @staticmethod
    def get_user_by_mobile(mobile_number):
        """
        Get user by mobile number
        
        Args:
            mobile_number (str): User's mobile number
            
        Returns:
            dict: User data
            
        Raises:
            CustomException: If user not found
        """
        try:
            logging.debug(f"Fetching user by mobile number: {mobile_number}")
            
            if not mobile_number:
                logging.error("Get user failed: Mobile number is required")
                raise CustomException.validation_error("Mobile number is required")
            
            # Clean mobile number
            import re
            clean_mobile = re.sub(r'\D', '', mobile_number)
            
            user = User.query.filter_by(mobile_number=clean_mobile).first()
            if not user:
                logging.warning(f"User not found with mobile number: {clean_mobile}")
                raise CustomException.not_found_error("User not found")
            
            logging.debug(f"User fetched successfully: {user.id} - {user.first_name} {user.last_name}")
            return user.to_dict()
            
        except CustomException:
            raise
        except Exception as e:
            logging.error(f"Unexpected error while fetching user: {str(e)}")
            raise CustomException.service_error("Failed to fetch user") 