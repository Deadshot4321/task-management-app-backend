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
    
    .task-actions {
        position: absolute;
        top: 1rem;
        right: 1rem;
        display: flex;
        gap: 0.5rem;
    }
    
    .action-button {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid #30363d;
        border-radius: 50%;
        width: 32px;
        height: 32px;
        display: flex;
        justify-content: center;
        align-items: center;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .action-button:hover {
        background: #58a6ff;
        border-color: #58a6ff;
        color: white;
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
    
    .task-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 0.8rem;
    }
    
    .tag-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 16px;
        font-size: 0.7rem;
        font-weight: 500;
        text-transform: capitalize;
        letter-spacing: 0.3px;
        border: 1px solid;
        color: #ffffff;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        background: linear-gradient(135deg, currentColor, rgba(255,255,255,0.1));
        backdrop-filter: blur(4px);
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
        width: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #316dca, #1f4788);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(88, 166, 255, 0.3);
    }
    
    .stButton.delete-button > button {
        background: linear-gradient(135deg, #f85149, #d9363e);
    }
    
    .stButton.delete-button > button:hover {
        background: linear-gradient(135deg, #d9363e, #b02a2f);
        box-shadow: 0 4px 12px rgba(248, 81, 73, 0.3);
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

def get_tasks(status=None, priority=None, tag=None, sort_by='deadline', sort_order='asc'):
    """Get user tasks with optional filters and sorting"""
    endpoint = "/get/tasks"
    params = []
    
    if status:
        params.append(f"status={status}")
    if priority:
        params.append(f"priority={priority}")
    if tag:
        params.append(f"tag={tag}")
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
                    st.session_state.user_first_name = result["user"]["first_name"]
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
    """Display the main task manager interface"""
    st.markdown('<p class="main-header">📋 Your Personal Task Manager</p>', unsafe_allow_html=True)

    # Sidebar for creating tasks and filters
    with st.sidebar:
        st.markdown("## ⚡️ Quick Actions")

        # User Info
        with st.container():
            st.markdown(f"**Welcome, {st.session_state.get('user_first_name', 'User')}!**")
            if st.button("Logout", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        st.markdown("---")

        # Create Task Form
        with st.expander("📝 Create New Task", expanded=True):
            with st.form("new_task_form", clear_on_submit=True):
                st.markdown("##### Add a new item to your list")
                title = st.text_input("Title", placeholder="e.g., Finish project report")
                description = st.text_area("Description", placeholder="Add more details here...")
                
                d_col, t_col = st.columns(2)
                deadline_date = d_col.date_input("Deadline Date", min_value=datetime.now().date())
                deadline_time = t_col.time_input("Deadline Time")
                
                submitted = st.form_submit_button("🚀 Add Task", use_container_width=True)
                
                if submitted:
                    if title:
                        # Handle Streamlit's DateWidgetReturn
                        if isinstance(deadline_date, tuple):
                            deadline_date = deadline_date[0] if deadline_date else datetime.now().date()
                        
                        # Ensure deadline_date is not None
                        if deadline_date is None:
                            deadline_date = datetime.now().date()
                            
                        deadline = datetime.combine(deadline_date, deadline_time)
                        with st.spinner("Creating task..."):
                            result = create_task(title, description, deadline.isoformat())
                        
                        if result["success"]:
                            st.success("🎉 Task created successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                    else:
                        st.warning("Title is required to create a task.")
        
        st.markdown("---")
        
        # Filtering and Sorting
        st.markdown("## ⚙️ Controls")
        with st.expander("Filter & Sort Tasks", expanded=True):
            st.session_state.sort_by = st.selectbox(
                "Sort by",
                ['deadline', 'priority', 'title'],
                index=0,
                key='sort_by_select'
            )
            st.session_state.sort_order = st.selectbox(
                "Order",
                ['asc', 'desc'],
                index=0,
                key='sort_order_select'
            )
            
            # Fetch all tags for filtering
            all_tags = ["All"] # Assuming a function get_all_tags() exists or is added
            st.session_state.filter_tag = st.selectbox(
                "Filter by Tag",
                options=all_tags,
                index=0,
                key='filter_tag_select'
            )

    # Main content area
    
    # Statistics
    stats = get_statistics()
    if stats:
        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stat-number">{stats.get('upcoming_tasks', 0)}</div>
                <div class="stat-label">Upcoming</div>
            </div>
            """, unsafe_allow_html=True)
        with s_col2:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stat-number">{stats.get('completed_tasks', 0)}</div>
                <div class="stat-label">Completed</div>
            </div>
            """, unsafe_allow_html=True)
        with s_col3:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stat-number">{stats.get('missed_tasks', 0)}</div>
                <div class="stat-label">Missed</div>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown('<div class="sub-header">Your Tasks</div>', unsafe_allow_html=True)

    # Fetch tasks based on filters
    try:
        tasks = get_tasks(
            sort_by=st.session_state.get('sort_by', 'deadline'),
            sort_order=st.session_state.get('sort_order', 'asc'),
            tag=st.session_state.get('filter_tag') if st.session_state.get('filter_tag') != 'All' else None
        )
    except Exception as e:
        st.error(f"Failed to load tasks: {e}")
        tasks = []

    if not tasks:
        st.info("You have no tasks. Add one from the sidebar!")
        return

    # Categorize tasks
    now = datetime.now()
    upcoming_tasks = []
    completed_tasks = []
    missed_tasks = []

    for task in tasks:
        if task.get('status') == 'completed':
            completed_tasks.append(task)
        else:
            try:
                deadline = datetime.fromisoformat(task['deadline'].replace('Z', ''))
                if deadline < now:
                    missed_tasks.append(task)
                else:
                    upcoming_tasks.append(task)
            except (ValueError, TypeError):
                upcoming_tasks.append(task) # Fallback for misformatted deadline

    # Display task buckets
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="bucket-header upcoming-bucket">🟡 Upcoming</div>', unsafe_allow_html=True)
        if upcoming_tasks:
            for task in upcoming_tasks:
                render_task_card(task, "upcoming")
        else:
            st.info("No upcoming tasks! 🎉")
    
    with col2:
        st.markdown('<div class="bucket-header completed-bucket">🟢 Completed</div>', unsafe_allow_html=True)
        if completed_tasks:
            for task in completed_tasks:
                render_task_card(task, "completed")
        else:
            st.info("No tasks completed yet.")
            
    with col3:
        st.markdown('<div class="bucket-header missed-bucket">🔴 Missed</div>', unsafe_allow_html=True)
        if missed_tasks:
            for task in missed_tasks:
                render_task_card(task, "missed")
        else:
            st.info("No missed tasks! Great job! 🎉")

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
        days_diff = (deadline_dt - datetime.now(deadline_dt.tzinfo)).days
        
        if deadline_dt.date() > datetime.now(deadline_dt.tzinfo).date():
            deadline_info = f"📅 {deadline_str} ({days_diff} days left)"
            deadline_color = "#3fb950"
        elif deadline_dt.date() == datetime.now(deadline_dt.tzinfo).date():
            deadline_info = f"📅 {deadline_str} (Due Today!)"
            deadline_color = "#f7cc02"
        else:
            deadline_info = f"📅 {deadline_str} ({abs(days_diff)} days overdue)"
            deadline_color = "#f85149"
    except Exception as e:
        deadline_info = f"📅 {task['deadline']}"
        deadline_color = "#a5a5a5"
        st.error(f"Error parsing deadline: {e}")
    
    # Get tags and format them
    tags = task.get('tags', [])
    tag_html = ""
    if tags:
        tag_badges = []
        for tag in tags:
            tag_name = tag.get('name', '') if isinstance(tag, dict) else str(tag)
            tag_color = tag.get('color', '#58a6ff') if isinstance(tag, dict) else '#58a6ff'
            tag_badges.append(f'<span class="tag-badge" style="background-color: {tag_color}; border-color: {tag_color}; color: #fff;">🏷️ {tag_name}</span>')
        tag_html = f'<div class="task-tags">{"".join(tag_badges)}</div>'
    
    # Task card container
    with st.container():
        st.markdown(f"""
        <div class="task-card">
            <div style="position: relative;">
                <div class="priority-badge {priority_class}">{priority_icon} {priority} Priority</div>
                <div class="task-title">{task['title']}</div>
                <div class="task-description">{task.get('description', 'No description provided')}</div>
                {tag_html}
                <div class="task-deadline" style="color: {deadline_color};">{deadline_info}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        cols = st.columns([1, 1, 1, 3])
        
        with cols[0]:
            if status != "completed":
                if st.button("✅", key=f"complete_{task['id']}", help="Mark as Complete"):
                    with st.spinner("Marking as complete..."):
                        result = complete_task(task['id'])
                    if result["success"]:
                        st.toast("✅ Task completed!", icon="🎉")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {result['error']}")

        with cols[1]:
            if st.button("✏️", key=f"edit_{task['id']}", help="Edit Task"):
                st.session_state[f"editing_{task['id']}"] = not st.session_state.get(f"editing_{task['id']}", False)
                st.rerun()

        with cols[2]:
            if st.button("🗑️", key=f"delete_{task['id']}", help="Delete Task"):
                if st.session_state.get(f"confirm_delete_{task['id']}", False):
                    with st.spinner("Deleting task..."):
                        result = delete_task(task['id'])
                    if result["success"]:
                        st.toast("🗑️ Task deleted!", icon="🗑️")
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
        with st.form(f"edit_form_{task['id']}", clear_on_submit=True):
            st.markdown("##### ✏️ Edit Task")
            new_title = st.text_input("Title", value=task['title'], label_visibility="collapsed", placeholder="Title")
            new_description = st.text_area("Description", value=task.get('description', ''), label_visibility="collapsed", placeholder="Description")
            
            try:
                current_deadline = datetime.fromisoformat(task['deadline'].replace('Z', '+00:00'))
            except:
                current_deadline = datetime.now()
            
            d_col, t_col = st.columns(2)
            new_deadline_date = d_col.date_input("Deadline Date", value=current_deadline.date(), label_visibility="collapsed")
            new_deadline_time = t_col.time_input("Deadline Time", value=current_deadline.time(), label_visibility="collapsed")
            
            s_col, c_col = st.columns(2)
            if s_col.form_submit_button("💾 Save Changes", use_container_width=True):
                
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
                    st.toast("✅ Task updated!", icon="👍")
                    st.session_state[f"editing_{task['id']}"] = False
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")
            
            if c_col.form_submit_button("❌ Cancel", use_container_width=True):
                st.session_state[f"editing_{task['id']}"] = False
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