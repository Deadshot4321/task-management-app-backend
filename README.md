# Task Management API Backend

A comprehensive task management system API built with Flask, featuring time-aware auto-bucketing and user authentication.

## 🎯 Project Overview

This is a production-grade REST API that serves as the backend for a task management application. The system provides:

- **User Authentication**: Simple registration and OTP-based login
- **Task Management**: Full CRUD operations for tasks
- **Time-Aware Auto-Bucketing**: Automatic categorization based on deadlines
- **Smart Status Tracking**: Dynamic status computation (upcoming/completed/missed)

## ✨ Features

### User Management
- User registration with profession selection
- OTP-based login (MVP uses default OTP: 1234)
- 10-digit mobile number validation
- Top 30 profession choices

### Task Management
- Create, read, update, delete tasks
- Dynamic status computation
- Past deadline tracking
- User-specific task filtering
- Sorting and filtering capabilities
- Task statistics

### Technical Features
- **Production-grade architecture** with proper separation of concerns
- **Comprehensive logging** with request context and colors
- **Custom exception handling** with standardized error responses
- **Swagger documentation** for all API endpoints
- **Database migrations** support
- **CORS** enabled for frontend integration

## 🏗️ Architecture

```
task-management-app-backend/
├── Config/                 # Configuration modules
│   ├── database_config.py  # SQLAlchemy database setup
│   ├── logging_config.py   # Comprehensive logging configuration
│   ├── swagger_config.py   # API documentation setup
│   └── exception_config.py # Global exception handlers
├── Controller/             # API route controllers
│   ├── auth_controller.py  # Authentication endpoints
│   └── task_controller.py  # Task management endpoints
├── Service/               # Business logic layer
│   ├── auth_service.py    # Authentication business logic
│   └── task_service.py    # Task management business logic
├── Datastore/            # Database models
│   └── models/
│       ├── user_model.py  # User database model
│       └── task_model.py  # Task database model
├── Exceptions/           # Custom exception classes
│   └── custom_exception.py
├── Utils/               # Utility functions
│   └── database_setup.py # Database initialization
└── main.py             # Application entry point
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip

### 1. Clone & Setup
```bash
git clone <repository-url>
cd task-management-app-backend
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Configuration
1. Create PostgreSQL database:
```sql
CREATE DATABASE task_management_db;
```

2. Set environment variable or update the configuration:
```bash
export TASK_MANAGEMENT=/path/to/your/config.cfg
```

Your `Task_Management.cfg` should contain:
```ini
# Database Configuration
SQLALCHEMY_DATABASE_URI = postgresql://postgres:your_password@localhost:5432/task_management_db
SQLALCHEMY_TRACK_MODIFICATIONS = False

# API Configuration
API_TITLE = Task Management API
API_VERSION = v1.0
API_HOST = localhost:5005
API_BASE_PATH = /api/v1

# Logging Configuration
LOG_LEVEL = INFO
LOG_HANDLERS = BOTH
LOG_COLORS = True
LOG_FILE_PATH = logs/app.log
```

### 4. Run the Application
```bash
python main.py
```

The API will be available at: `http://localhost:5005`

**Note:** Database tables will be created automatically on first run.

## 🎨 Streamlit UI (Complete Solution)

This project now includes a **beautiful dark-themed Streamlit UI** that provides a complete frontend for your task management system!

### 🚀 Quick Demo Setup
```bash
# One-click setup with UI
./run_demo.sh
```

This script will:
1. Install all dependencies (Flask + Streamlit)
2. Start the Flask backend
3. Optionally create sample data
4. Launch the Streamlit UI in your browser

### 🌟 UI Features
- **🌙 Dark Theme**: Modern, eye-friendly dark interface
- **📱 Mobile Responsive**: Works perfectly on desktop and mobile
- **🔄 Real-time Updates**: Auto-refresh every 30 seconds
- **📊 Task Buckets**: Visual separation of Upcoming, Completed, and Missed tasks
- **📈 Live Statistics**: Task completion rates and counts
- **✨ Intuitive CRUD**: Create, edit, complete, and delete tasks
- **🎯 Smart Authentication**: Login/register with profession selection
- **⚡ Instant Feedback**: Loading states and success/error messages

### 🎛️ Manual UI Setup
If you prefer manual setup:

```bash
# Install Streamlit dependencies
pip install -r requirements_streamlit.txt

# Terminal 1: Start Flask backend
python main.py

# Terminal 2: Create demo data (optional)
python demo_data.py

# Terminal 3: Launch Streamlit UI
streamlit run streamlit_app.py
```

### 📱 Using the UI

1. **Authentication**
   - Register new users with profession selection
   - Login with mobile number (OTP: 1234)
   - Automatic session management

2. **Task Management**
   - Create tasks using sidebar form
   - View tasks in three buckets (Upcoming/Completed/Missed)
   - Edit tasks with inline forms
   - Mark tasks as complete with one click
   - Delete tasks with confirmation

3. **Dashboard Features**
   - Real-time task statistics
   - Auto-refresh toggle
   - Visual deadline indicators
   - Responsive design

### 🎯 Demo Data
The `demo_data.py` script creates realistic sample data:
- **3 Demo Users**: Alice (Software Engineer), Bob (Product Manager), Carol (Data Scientist)
- **10 Sample Tasks per User**: Mix of upcoming, completed, and missed tasks
- **Login Credentials**: Use mobile numbers 1234567890, 2345678901, 3456789012

### 📊 Auto-Bucketing in Action
The UI showcases your intelligent auto-bucketing system:
- **🟡 Upcoming**: Future deadlines, not completed
- **🟢 Completed**: Manually marked as done
- **🔴 Missed**: Past deadlines, not completed

Tasks automatically move between buckets as time passes!

### 🔧 UI Configuration
- **API URL**: Edit line 99 in `streamlit_app.py`
- **Refresh Rate**: Modify auto-refresh interval (default: 30s)
- **Theme**: Customize CSS colors and styling
- **Mobile**: Responsive design works on all screen sizes

### 🎨 UI Architecture
```
streamlit_app.py          # Main UI application
├── Authentication Pages  # Login/Register tabs
├── Task Management UI    # Three-column bucket layout
├── Sidebar Tools         # Task creation form + statistics
├── API Integration       # Full backend communication
└── Dark Theme Styling    # Custom CSS for modern look
```

### 🚀 Production Considerations
- **Environment Variables**: Configure API URL
- **HTTPS**: Secure connections for production
- **Performance**: Optimize refresh rates for scale
- **Monitoring**: Add error tracking and analytics
- **Mobile App**: Foundation for React Native/Flutter

**🎉 The Streamlit UI transforms your robust Flask backend into a complete, production-ready task management solution!**

## 📚 API Documentation

Once the application is running, visit:
- **Swagger UI**: `http://localhost:5005/docs/`
- **API Spec**: `http://localhost:5005/swagger.json`

## 🔗 API Endpoints

### Authentication Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/get/professions` | Get available profession choices |
| POST | `/api/v1/register` | Register a new user |
| POST | `/api/v1/login` | Initiate login (get OTP) |
| POST | `/api/v1/verify-otp` | Verify OTP and complete login |
| GET | `/api/v1/get/user/{id}` | Get user by ID |

### Task Management Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/create/task` | Create a new task |
| GET | `/api/v1/get/tasks` | Get all user tasks (with filtering) |
| GET | `/api/v1/get/task/{id}` | Get specific task |
| PUT | `/api/v1/update/task/{id}` | Update task (flexible - can be partial) |
| PUT | `/api/v1/complete/task/{id}` | Mark task as complete |
| DELETE | `/api/v1/delete/task/{id}` | Delete task |
| GET | `/api/v1/get/task/statistics` | Get task statistics |

## 📝 Usage Examples

### 1. User Registration
```bash
curl -X POST http://localhost:5005/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "mobile_number": "1234567890",
    "occupation": "Software Engineer"
  }'
```

### 2. Login Flow
```bash
# Step 1: Initiate login
curl -X POST http://localhost:5005/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"mobile_number": "1234567890"}'

# Step 2: Verify OTP (use 1234 for MVP)
curl -X POST http://localhost:5005/api/v1/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "mobile_number": "1234567890",
    "otp": "1234"
  }'
```

### 3. Create Task
```bash
curl -X POST http://localhost:5005/api/v1/create/task \
  -H "Content-Type: application/json" \
  -H "X-User-ID: c06d410b-4684-435a-a9b6-d89fd70dcf41" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive API docs",
    "deadline": "2024-01-15T18:00:00Z"
  }'
```

### 4. Get Tasks with Filtering
```bash
# Get all upcoming tasks, sorted by deadline
curl "http://localhost:5005/api/v1/get/tasks?status=upcoming&sort_by=deadline&sort_order=asc" \
  -H "X-User-ID: c06d410b-4684-435a-a9b6-d89fd70dcf41"
```

### 5. Mark Task as Complete
```bash
curl -X PUT http://localhost:5005/api/v1/complete/task/257a84b6-d063-4417-9b30-6fc13557ed17 \
  -H "Content-Type: application/json" \
  -H "X-User-ID: c06d410b-4684-435a-a9b6-d89fd70dcf41"
```

### 6. Update Task (Flexible - Partial or Complete)
```bash
# Update only completion status
curl -X PUT http://localhost:5005/api/v1/update/task/257a84b6-d063-4417-9b30-6fc13557ed17 \
  -H "Content-Type: application/json" \
  -H "X-User-ID: c06d410b-4684-435a-a9b6-d89fd70dcf41" \
  -d '{"completed": true}'

# Update title and description
curl -X PUT http://localhost:5005/api/v1/update/task/257a84b6-d063-4417-9b30-6fc13557ed17 \
  -H "Content-Type: application/json" \
  -H "X-User-ID: c06d410b-4684-435a-a9b6-d89fd70dcf41" \
  -d '{
    "title": "Updated task title",
    "description": "Updated description"
  }'
```

## 🔧 Configuration

### Environment Variables
- `TASK_MANAGEMENT`: Path to configuration file
- `DATABASE_URL`: PostgreSQL connection string (optional)

### Configuration File Options
See the sample configuration in the Quick Start section above.

## 🧪 Testing

The API includes comprehensive error handling and validation. Test with invalid data to see the robust error responses:

```bash
# Test validation error
curl -X POST http://localhost:5005/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"first_name": "John"}'  # Missing required fields
```

## 🏆 Task Status Auto-Bucketing

Tasks are automatically categorized into three buckets:

1. **Upcoming**: Deadline in the future, not completed
2. **Completed**: Manually marked as complete (regardless of deadline)
3. **Missed**: Deadline has passed, not completed

The status is computed dynamically, ensuring real-time accuracy without background jobs.

## 🎨 User Authentication (MVP)

For the MVP version:
- **Registration**: Simple form with personal details
- **Login**: Mobile number + OTP verification
- **OTP**: Default OTP is `1234` (no real SMS integration)
- **Session**: Simple user ID in headers (X-User-ID)

## 🔮 Future Enhancements

This MVP provides the foundation for advanced features:
- JWT token authentication
- Real OTP integration
- AI-powered task prioritization
- Task tagging and categorization
- Sub-task generation
- Email notifications
- Mobile app support

## 🛡️ Security Notes

For production deployment:
- Replace default OTP with real SMS service
- Implement proper JWT authentication
- Add rate limiting
- Enable HTTPS
- Add input sanitization
- Implement proper session management

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify PostgreSQL is running
   - Check database credentials in config
   - Ensure database exists

2. **Import Errors**
   - Run `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

3. **Port Already in Use**
   - Change port in main.py or kill existing process

### Logs
Check application logs for detailed error information:
- Console output (colored)
- Log file (if configured)

## 📄 License

This project is built for educational and portfolio purposes.

## 🆔 UUID Implementation (Security Enhancement)

**Important Change**: All user and task IDs are now **UUIDs** instead of sequential integers.

### Why UUIDs?
- ✅ **Prevents ID enumeration attacks** - Users can't guess other user/task IDs
- ✅ **Better security and privacy** - No predictable patterns
- ✅ **Scalable across distributed systems** - Globally unique identifiers
- ✅ **Production-ready** - Industry standard for secure systems

### Technical Details
- **UUID Version**: v4 (random)
- **Format**: `123e4567-e89b-12d3-a456-426614174000` 
- **Database**: PostgreSQL native UUID type (efficient storage)
- **API**: Serialized as strings in JSON responses

### Migration Impact
- **Headers**: `X-User-ID` now expects UUID string instead of integer
- **Path Parameters**: All `/tasks/{id}` and `/users/{id}` endpoints now use UUIDs
- **Responses**: All `id` fields in JSON responses are now UUID strings

### Updated API Examples

#### Authentication with UUID
```bash
# Register user (response will have UUID)
curl -X POST http://localhost:5005/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "mobile_number": "1234567890",
    "occupation": "Software Engineer"
  }'

# Response includes UUID
{
  "success": true,
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "first_name": "John",
    "last_name": "Doe",
    "mobile_number": "1234567890",
    "occupation": "Software Engineer"
  }
}
```

#### Task Management with UUIDs
```bash
# Create task with UUID in header
curl -X POST http://localhost:5005/api/v1/create/task \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 123e4567-e89b-12d3-a456-426614174000" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive API documentation",
    "deadline": "2024-12-31T23:59:59"
  }'

# Get specific task by UUID
curl -X GET http://localhost:5005/api/v1/get/task/456e7890-e89b-12d3-a456-426614174111 \
  -H "X-User-ID: 123e4567-e89b-12d3-a456-426614174000"

# Update task by UUID
curl -X PUT http://localhost:5005/api/v1/update/task/456e7890-e89b-12d3-a456-426614174111 \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 123e4567-e89b-12d3-a456-426614174000" \
  -d '{"completed": true}'
```

#### Task Response Format
```json
{
  "success": true,
  "task": {
    "id": "456e7890-e89b-12d3-a456-426614174111",
    "title": "Complete project documentation",
    "description": "Write comprehensive API documentation",
    "deadline": "2024-12-31T23:59:59",
    "completed": false,
    "status": "upcoming",
    "is_past_deadline": false,
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### Backward Compatibility
- **Breaking Change**: This is a breaking change from integer IDs
- **Database**: Existing data will be migrated to UUID format
- **Clients**: All client applications must be updated to handle UUID strings

---

**Built with ❤️ using Flask, SQLAlchemy, and modern Python practices** 