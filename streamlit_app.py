import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import time
import re

# Configure Streamlit page
st.set_page_config(
    page_title="Task Manager",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced dark theme CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0f1419;
        color: #e6f1ff;
    }
    
    .main-header {
        font-size: 2.8rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #58a6ff;
        text-shadow: 0 2px 4px rgba(88, 166, 255, 0.3);
    }
    
    .sub-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: #79c0ff;
        margin-bottom: 1rem;
    }
    
    .bucket-header {
        font-size: 1.4rem;
        font-weight: bold;
        margin-bottom: 1rem;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        border: 2px solid;
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        backdrop-filter: blur(10px);
    }
    
    .upcoming-bucket {
        border-color: #f7cc02;
        color: #f7cc02;
        background: linear-gradient(135deg, rgba(247, 204, 2, 0.2), rgba(247, 204, 2, 0.1));
    }
    
    .completed-bucket {
        border-color: #3fb950;
        color: #3fb950;
        background: linear-gradient(135deg, rgba(63, 185, 80, 0.2), rgba(63, 185, 80, 0.1));
    }
    
    .missed-bucket {
        border-color: #f85149;
        color: #f85149;
        background: linear-gradient(135deg, rgba(248, 81, 73, 0.2), rgba(248, 81, 73, 0.1));
    }
    
    .task-card {
        background: linear-gradient(135deg, #161b22, #21262d);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        transition: all 0.3s ease;
    }
    
    .task-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        border-color: #58a6ff;
    }
    
    .task-title {
        font-weight: bold;
        font-size: 1.2rem;
        color: #f0f6fc;
        margin-bottom: 0.8rem;
    }
    
    .task-description {
        color: #8b949e;
        font-size: 0.95rem;
        margin-bottom: 0.8rem;
        line-height: 1.5;
    }
    
    .task-deadline {
        color: #a5a5a5;
        font-size: 0.85rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .priority-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
        border: 1px solid;
    }
    
    .priority-critical {
        background: linear-gradient(135deg, rgba(248, 81, 73, 0.2), rgba(248, 81, 73, 0.1));
        color: #f85149;
        border-color: #f85149;
    }
    
    .priority-high {
        background: linear-gradient(135deg, rgba(255, 165, 0, 0.2), rgba(255, 165, 0, 0.1));
        color: #ffa500;
        border-color: #ffa500;
    }
    
    .priority-medium {
        background: linear-gradient(135deg, rgba(247, 204, 2, 0.2), rgba(247, 204, 2, 0.1));
        color: #f7cc02;
        border-color: #f7cc02;
    }
    
    .priority-low {
        background: linear-gradient(135deg, rgba(63, 185, 80, 0.2), rgba(63, 185, 80, 0.1));
        color: #3fb950;
        border-color: #3fb950;
    }
    
    .sort-controls {
        background: linear-gradient(135deg, #161b22, #21262d);
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .filter-controls {
        display: flex;
        gap: 1rem;
        align-items: center;
        flex-wrap: wrap;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #161b22, #21262d);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #58a6ff;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        color: #8b949e;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .info-box {
        background: linear-gradient(135deg, rgba(88, 166, 255, 0.1), rgba(88, 166, 255, 0.05));
        border: 1px solid #58a6ff;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .success-box {
        background: linear-gradient(135deg, rgba(63, 185, 80, 0.1), rgba(63, 185, 80, 0.05));
        border: 1px solid #3fb950;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .error-box {
        background: linear-gradient(135deg, rgba(248, 81, 73, 0.1), rgba(248, 81, 73, 0.05));
        border: 1px solid #f85149;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #58a6ff, #316dca);
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #316dca, #1f4788);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(88, 166, 255, 0.3);
    }
    
    .stSelectbox > div > div {
        background-color: #21262d;
        border: 1px solid #30363d;
        border-radius: 8px;
    }
    
    .stTextInput > div > div > input {
        background-color: #21262d;
        border: 1px solid #30363d;
        border-radius: 8px;
        color: #e6f1ff;
    }
    
    .stTextArea > div > div > textarea {
        background-color: #21262d;
        border: 1px solid #30363d;
        border-radius: 8px;
        color: #e6f1ff;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:5005/api/v1"

# Helper functions
def make_api_request(method, endpoint, headers=None, json_data=None):
    """Make API request with robust error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.request(method, url, headers=headers, json=json_data, timeout=10)
        
        if response.status_code in [200, 201]:
            return {"success": True, "data": response.json()}
        else:
            error_msg = f"API Error: {response.status_code}"
            try:
                error_data = response.json()
                if "message" in error_data:
                    error_msg = error_data["message"]
            except:
                error_msg = response.text
            return {"success": False, "error": error_msg}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "🔌 Cannot connect to backend API. Please ensure the Flask server is running on localhost:5005"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "⏱️ Request timeout. Please try again."}
    except Exception as e:
        return {"success": False, "error": f"❌ Request failed: {str(e)}"}

def get_user_headers():
    """Get headers with user ID for API requests"""
    if 'user_id' in st.session_state:
        return {"X-User-ID": st.session_state.user_id, "Content-Type": "application/json"}
    return {"Content-Type": "application/json"}

def get_professions():
    """Get list of available professions with robust fallback"""
    # Default profession list (always available)
    default_professions = [
        'Software Engineer', 'Data Scientist', 'Product Manager', 
        'Marketing Manager', 'Sales Manager', 'Business Analyst',
        'Project Manager', 'Graphic Designer', 'UI/UX Designer',
        'Content Writer', 'Digital Marketer', 'Financial Analyst',
        'Accountant', 'Human Resources Manager', 'Operations Manager',
        'Customer Success Manager', 'DevOps Engineer', 'Quality Assurance Engineer',
        'Consultant', 'Teacher/Educator', 'Doctor/Physician', 'Lawyer',
        'Architect', 'Civil Engineer', 'Mechanical Engineer', 'Electrical Engineer',
        'Research Scientist', 'Entrepreneur', 'Freelancer', 'Student', 'None'
    ]
    
    # Try to load from API only once
    if 'professions_loaded' not in st.session_state:
        st.session_state.professions_loaded = True
        
        try:
            response = make_api_request("GET", "/get/professions")
            if response["success"] and response["data"] and response["data"].get("professions"):
                professions_from_api = response["data"]["professions"]
                st.session_state.professions = professions_from_api
            else:
                st.warning("⚠️ Using default profession list (API unavailable)")
                st.session_state.professions = default_professions
        except Exception as e:
            st.warning(f"⚠️ Using default profession list (Error: {str(e)})")
            st.session_state.professions = default_professions
    
    return st.session_state.get('professions', default_professions)

def register_user(first_name, last_name, mobile_number, occupation):
    """Register new user with validation"""
    # Validate inputs
    if not all([first_name, last_name, mobile_number, occupation]):
        return {"success": False, "error": "All fields are required"}
    
    # Clean mobile number
    clean_mobile = re.sub(r'\D', '', mobile_number)
    if len(clean_mobile) != 10:
        return {"success": False, "error": "Mobile number must be exactly 10 digits"}
    
    return make_api_request("POST", "/register", 
                          json_data={
                              "first_name": first_name,
                              "last_name": last_name,
                              "mobile_number": clean_mobile,
                              "occupation": occupation
                          })

def login_user(mobile_number):
    """Login user and get user ID"""
    # Clean mobile number
    clean_mobile = re.sub(r'\D', '', mobile_number)
    if len(clean_mobile) != 10:
        return {"success": False, "error": "Mobile number must be exactly 10 digits"}
    
    # First, try to login
    response = make_api_request("POST", "/login", json_data={"mobile_number": clean_mobile})
    
    if response["success"]:
        return {"success": True, "mobile_number": clean_mobile, "message": response["data"].get("message", "OTP sent")}
    else:
        return response

def verify_otp(mobile_number, otp):
    """Verify OTP and complete login"""
    response = make_api_request("POST", "/verify-otp", 
                               json_data={"mobile_number": mobile_number, "otp": otp})
    
    if response["success"]:
        user_data = response["data"].get("user", {})
        return {"success": True, "user": user_data}
    else:
        return response

def create_task(title, description, deadline):
    """Create new task"""
    return make_api_request("POST", "/create/task", 
                          headers=get_user_headers(),
                          json_data={
                              "title": title,
                              "description": description,
                              "deadline": deadline
                          })

def get_tasks(status=None, priority=None, sort_by='deadline', sort_order='asc'):
    """Get user tasks with optional filters and sorting"""
    endpoint = "/get/tasks"
    params = []
    
    if status:
        params.append(f"status={status}")
    if priority:
        params.append(f"priority={priority}")
    if sort_by:
        params.append(f"sort_by={sort_by}")
    if sort_order:
        params.append(f"sort_order={sort_order}")
    
    if params:
        endpoint += "?" + "&".join(params)
    
    response = make_api_request("GET", endpoint, headers=get_user_headers())
    if response["success"]:
        return response["data"].get("tasks", [])
    return []

def update_task(task_id, **updates):
    """Update task"""
    return make_api_request("PUT", f"/update/task/{task_id}", 
                          headers=get_user_headers(),
                          json_data=updates)

def complete_task(task_id):
    """Mark task as complete using dedicated endpoint"""
    return make_api_request("PUT", f"/complete/task/{task_id}", headers=get_user_headers())

def delete_task(task_id):
    """Delete task"""
    return make_api_request("DELETE", f"/delete/task/{task_id}", headers=get_user_headers())

def get_statistics():
    """Get task statistics"""
    response = make_api_request("GET", "/get/task/statistics", headers=get_user_headers())
    if response["success"]:
        return response["data"].get("statistics", {})
    return {}

# Authentication UI
def show_auth_page():
    """Show enhanced authentication page"""
    st.markdown('<h1 class="main-header">📋 Task Manager</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.markdown('<h2 class="sub-header">Welcome Back!</h2>', unsafe_allow_html=True)
        
        # Check if we're in OTP verification mode
        if 'otp_verification' in st.session_state and st.session_state.otp_verification:
            show_otp_verification()
        else:
            show_login_form()
    
    with tab2:
        st.markdown('<h2 class="sub-header">Create New Account</h2>', unsafe_allow_html=True)
        show_registration_form()

def show_login_form():
    """Show login form"""
    with st.form("login_form"):
        mobile = st.text_input("📱 Mobile Number", 
                             placeholder="Enter your 10-digit mobile number",
                             max_chars=10,
                             help="Enter the mobile number you used to register")
        
        submitted = st.form_submit_button("🚀 Send OTP", use_container_width=True)
        
        if submitted:
            if mobile:
                with st.spinner("Sending OTP..."):
                    result = login_user(mobile)
                
                if result["success"]:
                    st.session_state.otp_verification = True
                    st.session_state.otp_mobile = result["mobile_number"]
                    st.success("✅ OTP sent successfully!")
                    st.info("📱 Check your messages for the OTP (MVP: use 1234)")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")
            else:
                st.error("❌ Please enter your mobile number")
    
    st.markdown("""
    <div class="info-box">
        <h4>💡 Demo Information</h4>
        <p>• Use any registered mobile number</p>
        <p>• Default OTP is always <strong>1234</strong></p>
        <p>• No real SMS integration in MVP</p>
    </div>
    """, unsafe_allow_html=True)

def show_otp_verification():
    """Show OTP verification form"""
    st.markdown(f"<h3>🔐 Enter OTP</h3>", unsafe_allow_html=True)
    st.markdown(f"<p>OTP sent to: <strong>{st.session_state.otp_mobile}</strong></p>", unsafe_allow_html=True)
    
    with st.form("otp_form"):
        otp = st.text_input("🔢 Enter OTP", 
                          placeholder="Enter 4-digit OTP",
                          max_chars=4,
                          help="Enter the OTP sent to your mobile number")
        
        col1, col2 = st.columns(2)
        
        with col1:
            verify_submitted = st.form_submit_button("✅ Verify OTP", use_container_width=True)
        
        with col2:
            if st.form_submit_button("🔙 Back to Login", use_container_width=True):
                st.session_state.otp_verification = False
                st.rerun()
        
        if verify_submitted:
            if otp:
                with st.spinner("Verifying OTP..."):
                    result = verify_otp(st.session_state.otp_mobile, otp)
                
                if result["success"]:
                    st.session_state.user_id = result["user"]["id"]
                    st.session_state.user_name = f"{result['user']['first_name']} {result['user']['last_name']}"
                    st.session_state.otp_verification = False
                    st.success(f"🎉 Welcome back, {st.session_state.user_name}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")
            else:
                st.error("❌ Please enter the OTP")
    
    st.markdown("""
    <div class="info-box">
        <h4>💡 MVP Demo</h4>
        <p>For this demo, always use OTP: <strong>1234</strong></p>
    </div>
    """, unsafe_allow_html=True)

def show_registration_form():
    """Show registration form"""
    with st.form("registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("👤 First Name", placeholder="Enter your first name")
            mobile_reg = st.text_input("📱 Mobile Number", 
                                     placeholder="Enter 10-digit mobile number",
                                     max_chars=10,
                                     key="reg_mobile")
        
        with col2:
            last_name = st.text_input("👤 Last Name", placeholder="Enter your last name")
            
            # Get professions with better error handling
            professions = get_professions()
            
            if professions and len(professions) > 0:
                occupation = st.selectbox("💼 Occupation", 
                                        options=professions,
                                        index=0,
                                        help="Select your profession from the list")
            else:
                st.error("⚠️ No professions loaded!")
                occupation = st.text_input("💼 Occupation", 
                                         placeholder="Enter your occupation",
                                         help="Profession list failed to load")
        
        submitted = st.form_submit_button("✨ Create Account", use_container_width=True)
        
        if submitted:
            if all([first_name, last_name, mobile_reg, occupation]):
                with st.spinner("Creating your account..."):
                    result = register_user(first_name, last_name, mobile_reg, occupation)
                
                if result["success"]:
                    st.success("🎉 Account created successfully!")
                    st.info("👉 Please switch to the Login tab to sign in")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")
            else:
                st.error("❌ Please fill in all fields")
    
    st.markdown("""
    <div class="info-box">
        <h4>📝 Registration Tips</h4>
        <p>• Use a unique 10-digit mobile number</p>
        <p>• Choose from the available professions</p>
        <p>• All fields are required</p>
    </div>
    """, unsafe_allow_html=True)

# Main Task Management UI
def show_task_manager():
    """Show enhanced task management interface"""
    # Header with user info and logout
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown('<h1 class="main-header">📋 Task Manager</h1>', unsafe_allow_html=True)
        if 'user_name' in st.session_state:
            st.markdown(f"<p style='color: #79c0ff; font-size: 1.1rem;'>Welcome back, <strong>{st.session_state.user_name}</strong>! 👋</p>", unsafe_allow_html=True)
    
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Sidebar for creating new tasks
    with st.sidebar:
        st.markdown("### ➕ Create New Task")
        
        with st.form("new_task_form"):
            title = st.text_input("📝 Task Title", 
                                placeholder="Enter a descriptive title...",
                                max_chars=500)
            
            description = st.text_area("📄 Description", 
                                     placeholder="Add details about your task (optional)",
                                     height=100)
            
            # Separate date and time inputs
            col1, col2 = st.columns(2)
            with col1:
                deadline_date = st.date_input("📅 Deadline Date", 
                                            value=(datetime.now() + timedelta(days=1)).date(),
                                            min_value=datetime.now().date())
            with col2:
                deadline_time = st.time_input("⏰ Time", 
                                            value=datetime.now().replace(hour=23, minute=59).time())
            
            submitted = st.form_submit_button("🚀 Create Task", use_container_width=True)
            
            if submitted:
                if title:
                    # Combine date and time (handle Streamlit's DateWidgetReturn)
                    if isinstance(deadline_date, tuple):
                        deadline_date = deadline_date[0] if deadline_date else (datetime.now() + timedelta(days=1)).date()
                    
                    # Ensure deadline_date is not None
                    if deadline_date is None:
                        deadline_date = (datetime.now() + timedelta(days=1)).date()
                    
                    deadline = datetime.combine(deadline_date, deadline_time)
                    
                    with st.spinner("Creating task..."):
                        result = create_task(title, description, deadline.isoformat())
                    
                    if result["success"]:
                        st.success("✅ Task created successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {result['error']}")
                else:
                    st.error("❌ Please enter a task title")
        
        st.markdown("---")
        
        # Statistics
        st.markdown("### 📊 Your Statistics")
        stats = get_statistics()
        
        if stats:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stat-number">{stats.get('total_tasks', 0)}</div>
                <div class="stat-label">Total Tasks</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="stats-card">
                <div class="stat-number">{stats.get('completion_rate', 0)}%</div>
                <div class="stat-label">Completion Rate</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="stats-card">
                <div class="stat-number">{stats.get('upcoming_tasks', 0)}</div>
                <div class="stat-label">Upcoming Tasks</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("📊 Statistics will appear after creating tasks")
        
        # Auto-refresh toggle
        st.markdown("---")
        auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=False)
        
        if auto_refresh:
            time.sleep(30)
            st.rerun()
    
    # Main content area - Task Buckets
    st.markdown("### 🎯 Task Dashboard")
    
    # Sorting and Filtering Controls
    st.markdown('<div class="sort-controls">', unsafe_allow_html=True)
    st.markdown("#### 🔧 Sort & Filter Options")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        sort_by = st.selectbox(
            "📊 Sort by",
            options=["deadline", "priority", "created_at", "title"],
            index=0,
            format_func=lambda x: {
                "deadline": "📅 Deadline",
                "priority": "🎯 Priority",
                "created_at": "📝 Created Date",
                "title": "🔤 Title"
            }[x]
        )
    
    with col2:
        sort_order = st.selectbox(
            "📈 Sort order",
            options=["asc", "desc"],
            index=0,
            format_func=lambda x: {
                "asc": "⬆️ Ascending",
                "desc": "⬇️ Descending"
            }[x]
        )
    
    with col3:
        filter_priority = st.selectbox(
            "🎯 Filter by Priority",
            options=[None, "Critical", "High", "Medium", "Low"],
            index=0,
            format_func=lambda x: "🔍 All Priorities" if x is None else {
                "Critical": "🔴 Critical",
                "High": "🟠 High", 
                "Medium": "🟡 Medium",
                "Low": "🟢 Low"
            }[x]
        )
    
    with col4:
        filter_status = st.selectbox(
            "📋 Filter by Status",
            options=[None, "upcoming", "completed", "missed"],
            index=0,
            format_func=lambda x: "📝 All Status" if x is None else {
                "upcoming": "🟡 Upcoming",
                "completed": "🟢 Completed",
                "missed": "🔴 Missed"
            }[x]
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Get all tasks with filters and sorting
    with st.spinner("Loading tasks..."):
        all_tasks = get_tasks(
            status=filter_status,
            priority=filter_priority,
            sort_by=sort_by or "deadline",
            sort_order=sort_order or "asc"
        )
    
    if not all_tasks:
        st.markdown("""
        <div class="info-box">
            <h3>🎉 Welcome to Your Task Manager!</h3>
            <p>You don't have any tasks yet. Get started by creating your first task using the sidebar form.</p>
            <p><strong>💡 Tips:</strong></p>
            <ul>
                <li>Tasks are automatically organized into buckets</li>
                <li>🟡 <strong>Upcoming</strong>: Future deadlines, not completed</li>
                <li>🟢 <strong>Completed</strong>: Tasks you've finished</li>
                <li>🔴 <strong>Missed</strong>: Past deadlines, not completed</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Get task counts for all statuses (for metrics)
    total_upcoming = len([t for t in all_tasks if t['status'] == 'upcoming'])
    total_completed = len([t for t in all_tasks if t['status'] == 'completed'])
    total_missed = len([t for t in all_tasks if t['status'] == 'missed'])
    
    # Statistics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📝 Total Tasks", len(all_tasks))
    with col2:
        st.metric("🟡 Upcoming", total_upcoming)
    with col3:
        st.metric("🟢 Completed", total_completed)
    with col4:
        st.metric("🔴 Missed", total_missed)
    
    st.markdown("---")
    
    # Check if status filter is applied
    if filter_status:
        # Show filtered tasks in a single view
        st.markdown(f'<div class="bucket-header upcoming-bucket">📋 Filtered Tasks ({filter_status.title()})</div>', unsafe_allow_html=True)
        
        if all_tasks:
            for task in all_tasks:
                render_task_card(task, task['status'])
        else:
            st.info(f"No {filter_status} tasks found with current filters")
    else:
        # Show traditional three-column bucket view
        # Separate tasks by status
        upcoming_tasks = [t for t in all_tasks if t['status'] == 'upcoming']
        completed_tasks = [t for t in all_tasks if t['status'] == 'completed']
        missed_tasks = [t for t in all_tasks if t['status'] == 'missed']
        
        # Task Buckets
        col1, col2, col3 = st.columns(3)
        
        # Upcoming Tasks
        with col1:
            st.markdown('<div class="bucket-header upcoming-bucket">🟡 Upcoming Tasks</div>', unsafe_allow_html=True)
            
            if upcoming_tasks:
                for task in upcoming_tasks:
                    render_task_card(task, "upcoming")
            else:
                st.info("No upcoming tasks! 🎉")
        
        # Completed Tasks
        with col2:
            st.markdown('<div class="bucket-header completed-bucket">🟢 Completed Tasks</div>', unsafe_allow_html=True)
            
            if completed_tasks:
                for task in completed_tasks:
                    render_task_card(task, "completed")
            else:
                st.info("No completed tasks yet")
        
        # Missed Tasks
        with col3:
            st.markdown('<div class="bucket-header missed-bucket">🔴 Missed Tasks</div>', unsafe_allow_html=True)
            
            if missed_tasks:
                for task in missed_tasks:
                    render_task_card(task, "missed")
            else:
                st.info("No missed tasks! 🎉")

def render_task_card(task, status):
    """Render enhanced task card with AI priority"""
    # Get priority and format it
    priority = task.get('priority', 'Medium')
    priority_class = f"priority-{priority.lower()}"
    priority_icons = {
        'Critical': '🔴',
        'High': '🟠', 
        'Medium': '🟡',
        'Low': '🟢'
    }
    priority_icon = priority_icons.get(priority, '🟡')
    
    # Format deadline
    try:
        deadline_dt = datetime.fromisoformat(task['deadline'].replace('Z', '+00:00'))
        deadline_str = deadline_dt.strftime("%b %d, %Y at %I:%M %p")
        days_diff = (deadline_dt - datetime.now()).days
        
        if days_diff > 0:
            deadline_info = f"📅 {deadline_str} (in {days_diff} days)"
            deadline_color = "#3fb950"
        elif days_diff == 0:
            deadline_info = f"📅 {deadline_str} (today!)"
            deadline_color = "#f7cc02"
        else:
            deadline_info = f"📅 {deadline_str} ({abs(days_diff)} days overdue)"
            deadline_color = "#f85149"
    except:
        deadline_info = f"📅 {task['deadline']}"
        deadline_color = "#a5a5a5"
    
    # Task card HTML with priority badge
    card_html = f"""
    <div class="task-card">
        <div class="priority-badge {priority_class}">{priority_icon} {priority} Priority</div>
        <div class="task-title">{task['title']}</div>
        <div class="task-description">{task.get('description', 'No description provided')}</div>
        <div class="task-deadline" style="color: {deadline_color};">{deadline_info}</div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    # Complete button (only for non-completed tasks)
    if status != "completed":
        with col1:
            if st.button("✅ Complete", key=f"complete_{task['id']}", use_container_width=True):
                with st.spinner("Marking as complete..."):
                    result = complete_task(task['id'])
                
                if result["success"]:
                    st.success("✅ Task completed!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")
    
    # Edit button
    with col2:
        if st.button("✏️ Edit", key=f"edit_{task['id']}", use_container_width=True):
            st.session_state[f"editing_{task['id']}"] = True
            st.rerun()
    
    # Delete button
    with col3:
        if st.button("🗑️ Delete", key=f"delete_{task['id']}", use_container_width=True):
            if st.session_state.get(f"confirm_delete_{task['id']}", False):
                with st.spinner("Deleting task..."):
                    result = delete_task(task['id'])
                
                if result["success"]:
                    st.success("🗑️ Task deleted!")
                    if f"confirm_delete_{task['id']}" in st.session_state:
                        del st.session_state[f"confirm_delete_{task['id']}"]
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")
            else:
                st.session_state[f"confirm_delete_{task['id']}"] = True
                st.rerun()
    
    # Show confirmation for delete
    if st.session_state.get(f"confirm_delete_{task['id']}", False):
        st.warning("⚠️ Click Delete again to confirm removal")
    
    # Edit form
    if st.session_state.get(f"editing_{task['id']}", False):
        with st.expander("✏️ Edit Task", expanded=True):
            with st.form(f"edit_form_{task['id']}"):
                new_title = st.text_input("Title", value=task['title'])
                new_description = st.text_area("Description", value=task.get('description', ''))
                
                try:
                    current_deadline = datetime.fromisoformat(task['deadline'].replace('Z', '+00:00'))
                except:
                    current_deadline = datetime.now()
                
                col1, col2 = st.columns(2)
                with col1:
                    new_deadline_date = st.date_input("Deadline Date", value=current_deadline.date())
                with col2:
                    new_deadline_time = st.time_input("Deadline Time", value=current_deadline.time())
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("💾 Save Changes"):
                        # Handle Streamlit's DateWidgetReturn
                        if isinstance(new_deadline_date, tuple):
                            new_deadline_date = new_deadline_date[0] if new_deadline_date else current_deadline.date()
                        
                        # Ensure new_deadline_date is not None
                        if new_deadline_date is None:
                            new_deadline_date = current_deadline.date()
                        
                        new_deadline = datetime.combine(new_deadline_date, new_deadline_time)
                        
                        with st.spinner("Updating task..."):
                            result = update_task(task['id'], 
                                               title=new_title, 
                                               description=new_description,
                                               deadline=new_deadline.isoformat())
                        
                        if result["success"]:
                            st.success("✅ Task updated!")
                            del st.session_state[f"editing_{task['id']}"]
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {result['error']}")
                
                with col2:
                    if st.form_submit_button("❌ Cancel"):
                        del st.session_state[f"editing_{task['id']}"]
                        st.rerun()

# Main App
def main():
    """Main application entry point"""
    
    # Initialize session state
    if 'professions' not in st.session_state:
        st.session_state.professions = []
    
    if 'otp_verification' not in st.session_state:
        st.session_state.otp_verification = False
    
    # Check if user is logged in
    if 'user_id' not in st.session_state:
        show_auth_page()
    else:
        show_task_manager()

if __name__ == "__main__":
    main() 