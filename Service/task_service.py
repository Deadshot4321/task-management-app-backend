import logging
import uuid
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc, asc
from Config.database_config import db
from Datastore.models.task_model import Task
from Datastore.models.user_model import User
from Exceptions.custom_exception import CustomException
from Service.ai_service import AIService

class TaskService:
    """
    Task service for all task-related operations
    """
    
    @staticmethod
    def create_task(title, deadline, user_id, description=None):
        """
        Create a new task with AI-generated priority
        
        Args:
            title (str): Task title
            deadline (str): Task deadline in ISO format
            user_id (str): User UUID as string who owns the task
            description (str): Optional task description
            
        Returns:
            dict: Created task data
            
        Raises:
            CustomException: If task creation fails
        """
        try:
            logging.info(f"Creating new task: {title} for user_id: {user_id}")
            
            # Convert string UUID to UUID object
            try:
                user_uuid = uuid.UUID(user_id)
            except ValueError:
                logging.error(f"Invalid user UUID format: {user_id}")
                raise CustomException.validation_error("User ID must be a valid UUID")
            
            # Validate user exists
            user = User.query.get(user_uuid)
            if not user:
                logging.error(f"Task creation failed: User not found with ID {user_id}")
                raise CustomException.not_found_error("User not found")
            
            # Parse deadline
            try:
                if isinstance(deadline, str):
                    deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                else:
                    deadline_dt = deadline
            except ValueError:
                logging.error(f"Task creation failed: Invalid deadline format - {deadline}")
                raise CustomException.validation_error("Invalid deadline format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
            
            # Analyze task priority using AI
            try:
                ai_service = AIService()
                priority = ai_service.analyze_task_priority(
                    title=title,
                    description=description or "",
                    occupation=user.occupation
                )
                logging.info(f"AI analyzed priority for task '{title}': {priority}")
            except Exception as e:
                logging.warning(f"AI priority analysis failed: {str(e)}. Using default priority.")
                priority = 'Medium'  # Fallback to default priority
            
            # Create new task with AI-generated priority
            new_task = Task(
                title=title,
                deadline=deadline_dt,
                user_id=user_uuid,
                description=description,
                priority=priority
            )
            
            # Validate task data
            new_task.validate()
            
            # Save to database
            db.session.add(new_task)
            db.session.commit()
            
            logging.info(f"Task created successfully: {new_task.id} - {title} with priority: {priority}")
            return {
                "success": True,
                "message": "Task created successfully",
                "task": new_task.to_dict()
            }
            
        except CustomException:
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            logging.error(f"Unexpected error during task creation: {str(e)}")
            raise CustomException.service_error("Failed to create task")
    
    @staticmethod
    def get_task_by_id(task_id, user_id):
        """
        Get task by ID (only if it belongs to the user)
        
        Args:
            task_id (str): Task UUID as string
            user_id (str): User UUID as string who owns the task
            
        Returns:
            dict: Task data
            
        Raises:
            CustomException: If task not found
        """
        try:
            logging.debug(f"Fetching task by ID: {task_id} for user: {user_id}")
            
            if not task_id or not user_id:
                logging.error("Get task failed: Task ID and User ID are required")
                raise CustomException.validation_error("Task ID and User ID are required")
            
            # Convert string UUIDs to UUID objects
            try:
                task_uuid = uuid.UUID(task_id)
                user_uuid = uuid.UUID(user_id)
            except ValueError:
                logging.error(f"Invalid UUID format - Task ID: {task_id}, User ID: {user_id}")
                raise CustomException.validation_error("Task ID and User ID must be valid UUIDs")
            
            task = Task.query.filter_by(id=task_uuid, user_id=user_uuid).first()
            if not task:
                logging.warning(f"Task not found: ID {task_id} for user {user_id}")
                raise CustomException.not_found_error("Task not found")
            
            logging.debug(f"Task fetched successfully: {task.id} - {task.title}")
            return task.to_dict()
            
        except CustomException:
            raise
        except Exception as e:
            logging.error(f"Unexpected error while fetching task: {str(e)}")
            raise CustomException.service_error("Failed to fetch task")
    
    @staticmethod
    def get_user_tasks(user_id, status=None, priority=None, sort_by='deadline', sort_order='asc'):
        """
        Get all tasks for a user with optional filtering and sorting
        
        Args:
            user_id (str): User UUID as string
            status (str): Optional status filter (upcoming, completed, missed)
            priority (str): Optional priority filter (Low, Medium, High, Critical)
            sort_by (str): Sort field (deadline, created_at, title, priority)
            sort_order (str): Sort order (asc, desc)
            
        Returns:
            dict: List of tasks
            
        Raises:
            CustomException: If fetching fails
        """
        try:
            logging.info(f"Fetching tasks for user: {user_id}, status: {status}, priority: {priority}, sort: {sort_by} {sort_order}")
            
            if not user_id:
                logging.error("Get tasks failed: User ID is required")
                raise CustomException.validation_error("User ID is required")
            
            # Convert string UUID to UUID object
            try:
                user_uuid = uuid.UUID(user_id)
            except ValueError:
                logging.error(f"Invalid user UUID format: {user_id}")
                raise CustomException.validation_error("User ID must be a valid UUID")
            
            # Validate user exists
            user = User.query.get(user_uuid)
            if not user:
                logging.error(f"Get tasks failed: User not found with ID {user_id}")
                raise CustomException.not_found_error("User not found")
            
            # Base query
            query = Task.query.filter_by(user_id=user_uuid)
            
            # Apply priority filter if specified
            if priority:
                if priority not in Task.PRIORITY_CHOICES:
                    logging.error(f"Invalid priority filter: {priority}")
                    raise CustomException.validation_error(f"Priority must be one of {Task.PRIORITY_CHOICES}")
                query = query.filter_by(priority=priority)
            
            # Apply sorting
            if sort_by == 'deadline':
                if sort_order.lower() == 'desc':
                    query = query.order_by(desc(Task.deadline))
                else:
                    query = query.order_by(asc(Task.deadline))
            elif sort_by == 'created_at':
                if sort_order.lower() == 'desc':
                    query = query.order_by(desc(Task.created_at))
                else:
                    query = query.order_by(asc(Task.created_at))
            elif sort_by == 'title':
                if sort_order.lower() == 'desc':
                    query = query.order_by(desc(Task.title))
                else:
                    query = query.order_by(asc(Task.title))
            elif sort_by == 'priority':
                # Custom priority sorting: Critical > High > Medium > Low
                priority_order = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
                if sort_order.lower() == 'desc':
                    # High priority first (Critical -> High -> Medium -> Low)
                    query = query.order_by(desc(Task.priority))
                else:
                    # Low priority first (Low -> Medium -> High -> Critical)
                    query = query.order_by(asc(Task.priority))
            else:
                # Default sort by deadline ascending
                query = query.order_by(asc(Task.deadline))
            
            # Get all tasks
            tasks = query.all()
            
            # Convert to dict and apply status filter if specified
            task_list = []
            for task in tasks:
                task_dict = task.to_dict()
                
                # Apply status filter if specified
                if status and task_dict['status'] != status:
                    continue
                
                task_list.append(task_dict)
            
            logging.info(f"Fetched {len(task_list)} tasks for user {user_id}")
            return {
                "success": True,
                "tasks": task_list,
                "total": len(task_list),
                "user_id": user_id
            }
            
        except CustomException:
            raise
        except Exception as e:
            logging.error(f"Unexpected error while fetching tasks: {str(e)}")
            raise CustomException.service_error("Failed to fetch tasks")
    
    @staticmethod
    def update_task(task_id, user_id, title=None, description=None, deadline=None, completed=None):
        """
        Update an existing task
        
        Args:
            task_id (str): Task UUID as string
            user_id (str): User UUID as string who owns the task
            title (str): Optional new title
            description (str): Optional new description
            deadline (str): Optional new deadline
            completed (bool): Optional completion status
            
        Returns:
            dict: Updated task data
            
        Raises:
            CustomException: If update fails
        """
        try:
            logging.info(f"Updating task: {task_id} for user: {user_id}")
            
            # Convert string UUIDs to UUID objects
            try:
                task_uuid = uuid.UUID(task_id)
                user_uuid = uuid.UUID(user_id)
            except ValueError:
                logging.error(f"Invalid UUID format - Task ID: {task_id}, User ID: {user_id}")
                raise CustomException.validation_error("Task ID and User ID must be valid UUIDs")
            
            # Get existing task
            task = Task.query.filter_by(id=task_uuid, user_id=user_uuid).first()
            if not task:
                logging.warning(f"Update failed: Task not found - ID {task_id} for user {user_id}")
                raise CustomException.not_found_error("Task not found")
            
            # Update fields if provided
            if title is not None:
                task.title = title
            
            if description is not None:
                task.description = description
            
            if deadline is not None:
                try:
                    if isinstance(deadline, str):
                        task.deadline = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
                    else:
                        task.deadline = deadline
                except ValueError:
                    logging.error(f"Task update failed: Invalid deadline format - {deadline}")
                    raise CustomException.validation_error("Invalid deadline format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
            
            if completed is not None:
                task.completed = bool(completed)
                if completed:
                    logging.info(f"Task marked as completed: {task.id} - {task.title}")
                else:
                    logging.info(f"Task marked as uncompleted: {task.id} - {task.title}")
            
            # Validate updated task
            task.validate()
            
            # Save changes
            db.session.commit()
            
            logging.info(f"Task updated successfully: {task.id} - {task.title}")
            return {
                "success": True,
                "message": "Task updated successfully",
                "task": task.to_dict()
            }
            
        except CustomException:
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            logging.error(f"Unexpected error during task update: {str(e)}")
            raise CustomException.service_error("Failed to update task")
    
    @staticmethod
    def delete_task(task_id, user_id):
        """
        Delete a task
        
        Args:
            task_id (str): Task UUID as string
            user_id (str): User UUID as string who owns the task
            
        Returns:
            dict: Deletion confirmation
            
        Raises:
            CustomException: If deletion fails
        """
        try:
            logging.info(f"Deleting task: {task_id} for user: {user_id}")
            
            # Convert string UUIDs to UUID objects
            try:
                task_uuid = uuid.UUID(task_id)
                user_uuid = uuid.UUID(user_id)
            except ValueError:
                logging.error(f"Invalid UUID format - Task ID: {task_id}, User ID: {user_id}")
                raise CustomException.validation_error("Task ID and User ID must be valid UUIDs")
            
            # Get existing task
            task = Task.query.filter_by(id=task_uuid, user_id=user_uuid).first()
            if not task:
                logging.warning(f"Delete failed: Task not found - ID {task_id} for user {user_id}")
                raise CustomException.not_found_error("Task not found")
            
            task_title = task.title
            
            # Delete task
            db.session.delete(task)
            db.session.commit()
            
            logging.info(f"Task deleted successfully: {task_id} - {task_title}")
            return {
                "success": True,
                "message": "Task deleted successfully",
                "deleted_task_id": task_id
            }
            
        except CustomException:
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            logging.error(f"Unexpected error during task deletion: {str(e)}")
            raise CustomException.service_error("Failed to delete task")
    
    @staticmethod
    def get_task_statistics(user_id):
        """
        Get task statistics for a user
        
        Args:
            user_id (str): User UUID as string
            
        Returns:
            dict: Task statistics
            
        Raises:
            CustomException: If fetching fails
        """
        try:
            logging.info(f"Fetching task statistics for user: {user_id}")
            
            if not user_id:
                logging.error("Get statistics failed: User ID is required")
                raise CustomException.validation_error("User ID is required")
            
            # Convert string UUID to UUID object
            try:
                user_uuid = uuid.UUID(user_id)
            except ValueError:
                logging.error(f"Invalid user UUID format: {user_id}")
                raise CustomException.validation_error("User ID must be a valid UUID")
            
            # Get all tasks for user
            tasks = Task.query.filter_by(user_id=user_uuid).all()
            
            # Calculate statistics
            total_tasks = len(tasks)
            completed_tasks = sum(1 for task in tasks if task.completed)
            upcoming_tasks = sum(1 for task in tasks if not task.completed and task.deadline >= datetime.now())
            missed_tasks = sum(1 for task in tasks if not task.completed and task.deadline < datetime.now())
            
            statistics = {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "upcoming_tasks": upcoming_tasks,
                "missed_tasks": missed_tasks,
                "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2)
            }
            
            logging.info(f"Task statistics calculated for user {user_id}: {statistics}")
            return {
                "success": True,
                "statistics": statistics,
                "user_id": user_id
            }
            
        except CustomException:
            raise
        except Exception as e:
            logging.error(f"Unexpected error while fetching statistics: {str(e)}")
            raise CustomException.service_error("Failed to fetch task statistics") 