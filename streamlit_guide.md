# 🚀 Streamlit UI Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements_streamlit.txt
```

### 2. Start Your Flask Backend
```bash
# In one terminal
python main.py
```
The Flask API should be running on `http://localhost:5005`

### 3. Launch Streamlit UI
```bash
# In another terminal
streamlit run streamlit_app.py
```
The Streamlit app will open in your browser at `http://localhost:8501`

## 🎯 Features

### ✅ **What Works**
- **Dark Theme** - Beautiful dark UI with custom styling
- **Authentication** - Login/Register with your Flask backend
- **Task Buckets** - Visual separation of Upcoming, Completed, and Missed tasks
- **Real-time Updates** - Auto-refresh every 30 seconds
- **CRUD Operations** - Create, Read, Update, Delete tasks
- **Statistics** - Live task statistics in sidebar
- **Mobile Responsive** - Works on desktop and mobile

### 🎨 **UI Components**
- **Login/Register Tabs** - Clean authentication interface
- **Task Creation Form** - In sidebar for easy access
- **Three-Column Layout** - Upcoming | Completed | Missed
- **Task Cards** - Rich task display with deadlines
- **Action Buttons** - Complete, Edit, Delete with confirmations
- **Statistics Dashboard** - Real-time metrics

### 🔄 **Auto-Bucketing Integration**
- **Dynamic Status** - Tasks automatically move between buckets
- **Time-Aware** - Shows days until/past deadline
- **Visual Feedback** - Color-coded buckets and status indicators
- **Instant Updates** - Changes reflect immediately

## 🎛️ **Usage**

### First Time Setup
1. **Register** - Create a new account with your details
2. **Login** - Use your mobile number (OTP: "1234")
3. **Create Tasks** - Use the sidebar form
4. **Manage Tasks** - Click tasks to edit, complete, or delete

### Daily Usage
1. **Check Buckets** - See your task status at a glance
2. **Complete Tasks** - Click "Complete" button
3. **Add New Tasks** - Use sidebar form
4. **Monitor Progress** - Check statistics in sidebar

## 🛠️ **Troubleshooting**

### Common Issues

**"Cannot connect to backend API"**
- Ensure Flask server is running on `localhost:5005`
- Check if `python main.py` is running successfully

**"Empty task list"**
- Create your first task using the sidebar
- Check if you're logged in with correct user

**"Page not refreshing"**
- Enable auto-refresh in sidebar
- Manually refresh using browser F5

**"Tasks not updating"**
- Wait for auto-refresh (30 seconds)
- Check network connection to Flask backend

### Configuration

**Change API URL**
Edit `streamlit_app.py` line 99:
```python
API_BASE_URL = "http://localhost:5005/api/v1"
```

**Disable Auto-refresh**
Uncheck "Auto-refresh (30s)" in sidebar

**Modify Refresh Interval**
Edit line 337 in `streamlit_app.py`:
```python
time.sleep(30)  # Change to desired seconds
```

## 🎨 **Customization**

### Theme Colors
Edit the CSS in `streamlit_app.py` lines 15-88 to customize:
- Background colors
- Button colors  
- Card styling
- Bucket headers

### Layout
- **Sidebar width**: Streamlit handles automatically
- **Column ratios**: Edit `st.columns([2, 1, 1])` ratios
- **Card spacing**: Modify CSS padding/margins

## 📱 **Mobile Experience**

The UI is fully responsive and works great on mobile:
- **Touch-friendly buttons**
- **Readable text sizing**
- **Responsive columns** (stack on mobile)
- **Mobile-optimized forms**

## 🔗 **API Integration**

The Streamlit app integrates with all your Flask API endpoints:

- `POST /auth/register` - User registration
- `POST /auth/login` - User login  
- `POST /auth/verify-otp` - OTP verification
- `GET /auth/professions` - Get profession list
- `POST /tasks` - Create task
- `GET /tasks` - Get user tasks
- `GET /tasks?status=upcoming` - Filter by status
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task
- `GET /tasks/statistics` - Get statistics

## 🚀 **Next Steps**

### Potential Enhancements
1. **Drag & Drop** - Move tasks between buckets
2. **Real-time Notifications** - WebSocket integration
3. **Advanced Filtering** - Date ranges, priorities
4. **Bulk Operations** - Select multiple tasks
5. **Export Features** - Download task reports
6. **Calendar View** - Timeline visualization

### Production Deployment
1. **Environment Variables** - Configure API URL
2. **HTTPS** - Secure connections
3. **Authentication** - JWT token integration
4. **Performance** - Optimize refresh rates
5. **Monitoring** - Error tracking and logging

---

🎉 **Enjoy your new Task Management UI!** The dark theme and real-time features showcase your robust Flask backend perfectly. 