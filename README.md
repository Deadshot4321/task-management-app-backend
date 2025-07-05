# The Engine for a Time-Aware Task API

A powerful, production-grade REST API that serves as the backend for an intelligent task management application. This system provides comprehensive task management with time-aware auto-bucketing and advanced AI-powered features that make task organization smarter and more efficient.

## 🎯 Project Overview

This is a robust, scalable backend service built with Flask that acts as the "single source of truth" for task management applications. The system automatically categorizes tasks based on their deadlines and leverages AI to provide intelligent insights and automation.

### Key Features

- **🔐 User Authentication**: Simple registration and OTP-based login system
- **📋 Task Management**: Full CRUD operations with intelligent status tracking
- **⏰ Time-Aware Auto-Bucketing**: Automatic task categorization based on deadlines
- **🤖 AI-Powered Intelligence**: Advanced AI features for priority analysis and smart tagging
- **🏗️ Production Architecture**: Scalable design with proper separation of concerns
- **📊 Comprehensive Logging**: Request tracking with colored output and context
- **🔧 Custom Exception Handling**: Standardized error responses
- **📚 API Documentation**: Complete Swagger documentation
- **🌐 CORS Support**: Ready for frontend integration
- **🖥️ Streamlit UI**: Beautiful dark-themed UI for complete user experience

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Groq API Key (for AI features)

### 1. Clone & Setup
```bash
git clone <repository-url>
cd task-management-app-backend
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a configuration file `Task_Management.cfg` with the following settings:

```ini
# Database Configuration
SQLALCHEMY_DATABASE_URI = postgresql://postgres:your_password@localhost:5432/task_management_db
SQLALCHEMY_TRACK_MODIFICATIONS = False

# AI Configuration
GROQ_API_KEY = your_groq_api_key
GROQ_MODEL = llama-3.3-70b-versatile
AI_ENABLED = true

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

### 4. Database Setup
Create PostgreSQL database:
```sql
CREATE DATABASE task_management_db;
```

Set environment variable:
```bash
export TASK_MANAGEMENT=/path/to/your/Task_Management.cfg
```

### 5. Run the Application
```bash
python main.py
```

The API will be available at: `http://localhost:5005`

**Note:** Database tables will be created automatically on first run.

## 🎨 Complete UI Experience

### Streamlit Dashboard
This project includes a beautiful, modern Streamlit UI with:
- **🌙 Dark Theme**: Eye-friendly interface
- **📱 Responsive Design**: Works on all devices
- **🔄 Real-time Updates**: Auto-refresh capabilities
- **📊 Visual Task Buckets**: Clear separation of task states
- **📈 Live Statistics**: Task completion metrics
- **✨ Intuitive CRUD**: Easy task management

### Quick Demo Setup
```bash
# Install Streamlit dependencies
pip install streamlit plotly

# Terminal 1: Start Flask backend
python main.py

# Terminal 2: Launch Streamlit UI
streamlit run streamlit_app.py
```

## 🏗️ System Architecture

```
task-management-app-backend/
├── AI/                     # AI Integration Layer
│   ├── groq_client.py      # Groq API client
│   └── prompts.py          # AI prompt templates
├── Config/                 # Configuration modules
│   ├── database_config.py  # SQLAlchemy setup
│   ├── logging_config.py   # Comprehensive logging
│   ├── swagger_config.py   # API documentation
│   └── exception_config.py # Global exception handlers
├── Controller/             # API route controllers
│   ├── auth_controller.py  # Authentication endpoints
│   └── task_controller.py  # Task management endpoints
├── Service/               # Business logic layer
│   ├── ai_service.py      # AI feature coordination
│   ├── auth_service.py    # Authentication logic
│   └── task_service.py    # Task management logic
├── Datastore/            # Database models
│   └── models/
│       ├── user_model.py  # User model
│       ├── task_model.py  # Task model with AI features
│       └── tag_model.py   # Tag model for AI tagging
├── Exceptions/           # Custom exception classes
│   └── custom_exception.py
├── Utils/               # Utility functions
└── main.py             # Application entry point
```

## 🧠 AI Innovation Feature

### Overview
We have implemented two cutting-edge AI features that significantly enhance the task management experience by providing intelligent automation and insights. These features leverage the power of Groq's API with the LLaMA model to analyze task content and provide smart recommendations.

### Why We Chose Groq
- **Generous Free Limits**: Allows extensive usage without cost concerns
- **LLaMA Model Performance**: Provides excellent output quality for our specific use cases
- **Low Latency**: Fast response times for real-time task processing
- **Reliability**: Consistent performance for production environments

### 1. 🎯 AI Priority Tagging

**Feature Description:**
Automatically analyzes new tasks to assign intelligent priority levels (Low, Medium, High, Critical) based on task content, context, and user occupation.

**Technical Implementation:**
- **Model**: LLaMA 3.3 70B Versatile via Groq API
- **Database Field**: `priority` column in Task model
- **Trigger**: Automatic on task creation via POST `/api/tasks/`
- **Context-Aware**: Considers user's occupation for professional context
- **Fallback**: Defaults to 'Medium' priority if AI analysis fails

**AI Prompt Strategy:**
```
You are a smart task prioritization assistant. Analyze this task considering 
the person's occupation and professional context.

PRIORITY RULES:
- Critical: Immediate deadlines, production issues, emergency meetings
- High: Important work deadlines, key meetings, career-impacting tasks
- Medium: Regular work tasks, routine meetings, personal important tasks
- Low: Non-urgent personal tasks, optional activities
```

**API Integration:**
```python
# Automatic priority assignment
priority = ai_service.analyze_task_priority(
    title=task_title,
    description=task_description,
    occupation=user_occupation
)
```

**Benefits:**
- Helps users focus on what matters most
- Reduces cognitive load in task prioritization
- Adapts to professional context for better accuracy
- Enables priority-based sorting and filtering

### 2. 🏷️ AI Task Tagging

**Feature Description:**
Automatically generates up to 3 relevant tags from a predefined list based on task content, making tasks easily searchable and organizable.

**Technical Implementation:**
- **Model**: LLaMA 3.3 70B Versatile via Groq API
- **Database**: Many-to-Many relationship between Task and Tag models
- **Predefined Tags**: [Work, Personal, Health, Finance, Learning, Urgent, Shopping, Travel, Meeting, Project]
- **Trigger**: Automatic on task creation
- **JSON Response**: Structured output for reliable parsing

**AI Prompt Strategy:**
```
Based on the following task, generate up to 3 relevant one-word tags 
from this list: [Work, Personal, Health, Finance, Learning, Urgent, 
Shopping, Travel, Meeting, Project]

Return them as a JSON array of strings. Be selective and choose 
the most relevant tags.
```

**API Integration:**
```python
# Automatic tag generation
tags = ai_service.analyze_task_tags(
    title=task_title,
    description=task_description
)

# Create and associate tags with task
for tag_name in tags:
    tag = Tag.get_or_create(name=tag_name)
    task.tags.append(tag)
```

**Benefits:**
- Automatic organization without manual effort
- Consistent tagging across all tasks
- Enables powerful filtering and search capabilities
- Reduces time spent on task categorization

### 3. 🔧 AI Service Architecture

**Centralized AI Management:**
- **AIService Class**: Coordinates all AI features
- **Graceful Degradation**: Functions continue if AI is disabled
- **Error Handling**: Robust fallbacks for API failures
- **Configuration**: Easy enable/disable of AI features

**Performance Optimizations:**
- **Low Temperature**: Consistent, predictable outputs
- **Limited Tokens**: Fast responses with focused content
- **Response Validation**: Ensures output quality and format
- **Caching Strategy**: Reduces API calls for similar tasks

### 4. 📊 Usage Examples

**Creating a Task with AI Features:**
```bash
curl -X POST "http://localhost:5005/api/v1/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Prepare quarterly financial report",
    "description": "Compile Q4 revenue data and create presentation for board meeting",
    "deadline": "2024-01-15T09:00:00"
  }'
```

**Response with AI-Generated Fields:**
```json
{
  "id": "uuid",
  "title": "Prepare quarterly financial report",
  "description": "Compile Q4 revenue data...",
  "priority": "High",
  "tags": ["Work", "Finance", "Meeting"],
  "deadline": "2024-01-15T09:00:00",
  "status": "upcoming"
}
```

**Filtering by AI-Generated Priority:**
```bash
curl "http://localhost:5005/api/v1/tasks?priority=High&ordering=-priority"
```

**Filtering by AI-Generated Tags:**
```bash
curl "http://localhost:5005/api/v1/tasks?tag=Work"
```

### 5. 🎯 Configuration

**Environment Variables:**
```ini
# Enable/disable AI features
AI_ENABLED = true

# Groq API configuration
GROQ_API_KEY = your_groq_api_key
GROQ_MODEL = llama-3.3-70b-versatile
GROQ_BASE_URL = https://api.groq.com/openai/v1
```

**AI Feature Toggle:**
AI features can be completely disabled by setting `AI_ENABLED = false`, ensuring the system remains fully functional with default values.

## 📋 Time-Aware Auto-Bucketing

Tasks are automatically categorized into three intelligent buckets:

### 🟡 Upcoming
- Future deadlines
- Not yet completed
- Automatically sorted by deadline proximity

### 🟢 Completed
- Manually marked as complete by user
- Preserves completion timestamp
- Maintains task history

### 🔴 Missed
- Past deadlines
- Not completed
- Automatic transition when deadline passes

## 🛠️ API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - OTP-based login
- `GET /api/v1/auth/user` - Get current user info

### Task Management
- `POST /api/v1/tasks` - Create task (with AI features)
- `GET /api/v1/tasks` - Get tasks with filters
- `GET /api/v1/tasks/{id}` - Get specific task
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `PATCH /api/v1/tasks/{id}/complete` - Mark complete
- `GET /api/v1/tasks/stats` - Get task statistics

### Query Parameters
- `status` - Filter by task status
- `priority` - Filter by AI-generated priority
- `tag` - Filter by AI-generated tags
- `ordering` - Sort by deadline, priority, created_at

## 📱 Demo Data

Generate sample data for testing:
```bash
python demo_data.py
```

Creates:
- 3 demo users with different professions
- 10 sample tasks per user with varied AI-generated priorities and tags
- Mix of upcoming, completed, and missed tasks

**Demo Login Credentials:**
- Alice (Software Engineer): 1234567890
- Bob (Product Manager): 2345678901
- Carol (Data Scientist): 3456789012
- OTP: 1234

## 🎨 Streamlit UI Features

### Real-time Dashboard
- **Live Statistics**: Task completion metrics
- **Auto-refresh**: Configurable refresh intervals
- **Visual Indicators**: Color-coded priority and status
- **Responsive Layout**: Mobile-friendly design

### Task Management
- **Create Tasks**: Sidebar form with validation
- **Edit Tasks**: Inline editing capabilities
- **Complete Tasks**: One-click completion
- **Delete Tasks**: Confirmation dialogs

### AI Features Showcase
- **Priority Badges**: Visual priority indicators
- **Tag Clouds**: Organized tag display
- **Smart Filtering**: AI-generated metadata filtering
- **Context Awareness**: Professional occupation consideration

## 🔧 Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Style
```bash
black .
flake8 .
```

### Database Migrations
```bash
# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade
```

## 🚀 Deployment

### Production Checklist
- [ ] Set secure database credentials
- [ ] Configure proper GROQ_API_KEY
- [ ] Enable production logging
- [ ] Set up SSL/TLS
- [ ] Configure proper CORS origins
- [ ] Set up monitoring and alerting

### Docker Deployment
```bash
# Build image
docker build -t task-management-api .

# Run container
docker run -p 5005:5005 -e GROQ_API_KEY=your_key task-management-api
```

## 📊 Monitoring

### Logging Features
- **Colored Output**: Easy-to-read console logs
- **Request Tracking**: Unique request IDs
- **Performance Metrics**: Response time tracking
- **Error Tracking**: Comprehensive error logging
- **AI Usage Tracking**: AI feature usage statistics

### Health Checks
- `GET /health` - API health status
- `GET /api/v1/auth/health` - Authentication service health
- `GET /api/v1/tasks/health` - Task service health

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add comprehensive tests
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Groq**: For providing excellent AI API with generous free limits
- **LLaMA**: For the powerful language model that powers our AI features
- **Flask**: For the robust web framework
- **SQLAlchemy**: For excellent ORM capabilities
- **Streamlit**: For the beautiful UI framework

---

**Built with ❤️ using cutting-edge AI technology to make task management smarter and more efficient.** 