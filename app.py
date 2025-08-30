import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

# Page configuration
st.set_page_config(
    page_title="NGC Assignment Tracker",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for data persistence
if 'assignments' not in st.session_state:
    st.session_state.assignments = []

if 'assignment_counter' not in st.session_state:
    st.session_state.assignment_counter = 1

# Chief Engineers list
CHIEF_ENGINEERS = [
    "Chief Engineer (Substation Design)",
    "Chief Engineer (Transmission Line Design)",
    "Chief Engineer (Telecom)",
    "Chief Engineer (Scada-III)",
    "Chief Engineer (Protection & Control)",
    "Chief Engineer (Standards & Specification)"
]

# Priority levels
PRIORITY_LEVELS = ["Low", "Medium", "High", "Critical"]

# Status options
STATUS_OPTIONS = ["Not Started", "In Progress", "Under Review", "Completed", "On Hold"]

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2d5aa0 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .main-header p {
        color: #e6f3ff;
        margin: 0;
        font-size: 1.1rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f4e79;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .status-not-started { color: #6c757d; }
    .status-in-progress { color: #007bff; }
    .status-under-review { color: #ffc107; }
    .status-completed { color: #28a745; }
    .status-on-hold { color: #dc3545; }
    .priority-low { background-color: #d4edda; }
    .priority-medium { background-color: #fff3cd; }
    .priority-high { background-color: #f8d7da; }
    .priority-critical { background-color: #721c24; color: white; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>⚡ NGC Assignment Tracker</h1>
    <p>General Manager (D&E) - Task Management System</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("📊 Navigation")
page = st.sidebar.selectbox("Select Page", [
    "Dashboard", 
    "Create Assignment", 
    "Manage Assignments", 
    "Reports & Analytics",
    "Engineer Workload"
])

def create_assignment():
    st.header("📝 Create New Assignment")
    
    with st.form("create_assignment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Assignment Title *", placeholder="Enter assignment title")
            assigned_to = st.selectbox("Assign To *", CHIEF_ENGINEERS)
            priority = st.selectbox("Priority Level *", PRIORITY_LEVELS, index=1)
            due_date = st.date_input("Due Date *", min_value=date.today())
            
        with col2:
            category = st.selectbox("Category", [
                "Design Review",
                "Technical Specification",
                "Quality Assurance",
                "Project Planning",
                "System Analysis",
                "Documentation",
                "Testing & Commissioning",
                "Other"
            ])
            estimated_hours = st.number_input("Estimated Hours", min_value=1, max_value=1000, value=8)
            status = st.selectbox("Initial Status", STATUS_OPTIONS, index=0)
            
        description = st.text_area("Assignment Description", placeholder="Detailed description of the assignment...")
        deliverables = st.text_area("Expected Deliverables", placeholder="List the expected deliverables...")
        
        submitted = st.form_submit_button("Create Assignment", type="primary")
        
        if submitted:
            if title and assigned_to and description:
                new_assignment = {
                    'id': st.session_state.assignment_counter,
                    'title': title,
                    'assigned_to': assigned_to,
                    'priority': priority,
                    'status': status,
                    'category': category,
                    'description': description,
                    'deliverables': deliverables,
                    'due_date': due_date.strftime('%Y-%m-%d'),
                    'created_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'estimated_hours': estimated_hours,
                    'actual_hours': 0,
                    'progress_percentage': 0,
                    'comments': []
                }
                
                st.session_state.assignments.append(new_assignment)
                st.session_state.assignment_counter += 1
                st.success(f"✅ Assignment '{title}' created successfully!")
                st.rerun()
            else:
                st.error("❌ Please fill in all required fields marked with *")

def dashboard():
    st.header("📊 Dashboard Overview")
    
    if not st.session_state.assignments:
        st.info("👋 Welcome to your Assignment Tracker! No assignments created yet. Use the 'Create Assignment' page to get started.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(st.session_state.assignments)
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_assignments = len(df)
        st.metric("Total Assignments", total_assignments)
    
    with col2:
        completed = len(df[df['status'] == 'Completed'])
        st.metric("Completed", completed)
    
    with col3:
        in_progress = len(df[df['status'] == 'In Progress'])
        st.metric("In Progress", in_progress)
    
    with col4:
        overdue = len(df[pd.to_datetime(df['due_date']) < datetime.now()])
        st.metric("⚠️ Overdue", overdue, delta_color="inverse")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Status Distribution
        status_counts = df['status'].value_counts()
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Assignment Status Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Priority Distribution
        priority_counts = df['priority'].value_counts()
        fig_priority = px.bar(
            x=priority_counts.index,
            y=priority_counts.values,
            title="Priority Level Distribution",
            color=priority_counts.index,
            color_discrete_map={
                'Low': '#28a745',
                'Medium': '#ffc107',
                'High': '#fd7e14',
                'Critical': '#dc3545'
            }
        )
        st.plotly_chart(fig_priority, use_container_width=True)
    
    # Engineer Workload
    st.subheader("👥 Engineer Workload Overview")
    engineer_workload = df.groupby('assigned_to').agg({
        'id': 'count',
        'status': lambda x: (x == 'Completed').sum(),
        'priority': lambda x: (x == 'Critical').sum()
    }).rename(columns={'id': 'total', 'status': 'completed', 'priority': 'critical'})
    
    engineer_workload['pending'] = engineer_workload['total'] - engineer_workload['completed']
    engineer_workload['completion_rate'] = (engineer_workload['completed'] / engineer_workload['total'] * 100).round(1)
    
    st.dataframe(engineer_workload, use_container_width=True)
    
    # Recent Assignments
    st.subheader("📋 Recent Assignments")
    recent_df = df.sort_values('created_date', ascending=False).head(5)
    
    for _, assignment in recent_df.iterrows():
        with st.expander(f"{assignment['title']} - {assignment['assigned_to']}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Status:** {assignment['status']}")
                st.write(f"**Priority:** {assignment['priority']}")
            with col2:
                st.write(f"**Due Date:** {assignment['due_date']}")
                st.write(f"**Category:** {assignment['category']}")
            with col3:
                st.write(f"**Created:** {assignment['created_date']}")
                st.write(f"**Est. Hours:** {assignment['estimated_hours']}")

def manage_assignments():
    st.header("🔧 Manage Assignments")
    
    if not st.session_state.assignments:
        st.info("No assignments to manage. Create some assignments first!")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_engineer = st.selectbox("Filter by Engineer", ["All"] + CHIEF_ENGINEERS)
    with col2:
        filter_status = st.selectbox("Filter by Status", ["All"] + STATUS_OPTIONS)
    with col3:
        filter_priority = st.selectbox("Filter by Priority", ["All"] + PRIORITY_LEVELS)
    
    # Filter data
    df = pd.DataFrame(st.session_state.assignments)
    
    if filter_engineer != "All":
        df = df[df['assigned_to'] == filter_engineer]
    if filter_status != "All":
        df = df[df['status'] == filter_status]
    if filter_priority != "All":
        df = df[df['priority'] == filter_priority]
    
    # Display assignments
    for idx, assignment in df.iterrows():
        with st.expander(f"ID: {assignment['id']} - {assignment['title']} [{assignment['status']}]"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Assigned to:** {assignment['assigned_to']}")
                st.write(f"**Description:** {assignment['description']}")
                st.write(f"**Deliverables:** {assignment['deliverables']}")
                
            with col2:
                st.write(f"**Priority:** {assignment['priority']}")
                st.write(f"**Due Date:** {assignment['due_date']}")
                st.write(f"**Category:** {assignment['category']}")
                st.write(f"**Progress:** {assignment['progress_percentage']}%")
            
            # Update form
            with st.form(f"update_{assignment['id']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    new_status = st.selectbox("Update Status", STATUS_OPTIONS, 
                                            index=STATUS_OPTIONS.index(assignment['status']), 
                                            key=f"status_{assignment['id']}")
                with col2:
                    new_progress = st.slider("Progress %", 0, 100, assignment['progress_percentage'],
                                           key=f"progress_{assignment['id']}")
                with col3:
                    actual_hours = st.number_input("Actual Hours Spent", 
                                                 min_value=0, 
                                                 value=assignment['actual_hours'],
                                                 key=f"hours_{assignment['id']}")
                
                comment = st.text_area("Add Comment", key=f"comment_{assignment['id']}")
                
                if st.form_submit_button("Update Assignment"):
                    # Update the assignment
                    for i, a in enumerate(st.session_state.assignments):
                        if a['id'] == assignment['id']:
                            st.session_state.assignments[i]['status'] = new_status
                            st.session_state.assignments[i]['progress_percentage'] = new_progress
                            st.session_state.assignments[i]['actual_hours'] = actual_hours
                            
                            if comment:
                                if 'comments' not in st.session_state.assignments[i]:
                                    st.session_state.assignments[i]['comments'] = []
                                st.session_state.assignments[i]['comments'].append({
                                    'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                                    'comment': comment
                                })
                            break
                    
                    st.success("Assignment updated successfully!")
                    st.rerun()

def reports_analytics():
    st.header("📈 Reports & Analytics")
    
    if not st.session_state.assignments:
        st.info("No data available for reports. Create some assignments first!")
        return
    
    df = pd.DataFrame(st.session_state.assignments)
    
    # Time-based analysis
    st.subheader("⏰ Timeline Analysis")
    
    # Convert dates
    df['due_date'] = pd.to_datetime(df['due_date'])
    df['created_date'] = pd.to_datetime(df['created_date'])
    
    # Assignments by month
    df['month'] = df['created_date'].dt.to_period('M')
    monthly_assignments = df.groupby('month').size()
    
    fig_timeline = px.line(
        x=monthly_assignments.index.astype(str),
        y=monthly_assignments.values,
        title="Assignments Created Over Time",
        labels={'x': 'Month', 'y': 'Number of Assignments'}
    )
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Performance metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚡ Performance Metrics")
        completed_assignments = df[df['status'] == 'Completed']
        
        if not completed_assignments.empty:
            avg_completion_time = (pd.to_datetime(datetime.now()) - completed_assignments['created_date']).dt.days.mean()
            st.metric("Avg Completion Time", f"{avg_completion_time:.1f} days")
            
            total_estimated = completed_assignments['estimated_hours'].sum()
            total_actual = completed_assignments['actual_hours'].sum()
            if total_estimated > 0:
                efficiency = (total_estimated / total_actual * 100) if total_actual > 0 else 0
                st.metric("Time Efficiency", f"{efficiency:.1f}%")
        
    with col2:
        st.subheader("🎯 Category Performance")
        category_performance = df.groupby('category')['status'].apply(
            lambda x: (x == 'Completed').sum() / len(x) * 100 if len(x) > 0 else 0
        ).round(1)
        
        fig_category = px.bar(
            x=category_performance.index,
            y=category_performance.values,
            title="Completion Rate by Category (%)",
            labels={'x': 'Category', 'y': 'Completion Rate (%)'}
        )
        fig_category.update_xaxis(tickangle=45)
        st.plotly_chart(fig_category, use_container_width=True)

def engineer_workload():
    st.header("👥 Engineer Workload Analysis")
    
    if not st.session_state.assignments:
        st.info("No workload data available. Create some assignments first!")
        return
    
    df = pd.DataFrame(st.session_state.assignments)
    
    # Detailed workload by engineer
    for engineer in CHIEF_ENGINEERS:
        engineer_data = df[df['assigned_to'] == engineer]
        
        if len(engineer_data) > 0:
            with st.expander(f"📊 {engineer}"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_tasks = len(engineer_data)
                    st.metric("Total Tasks", total_tasks)
                
                with col2:
                    completed_tasks = len(engineer_data[engineer_data['status'] == 'Completed'])
                    st.metric("Completed", completed_tasks)
                
                with col3:
                    avg_progress = engineer_data['progress_percentage'].mean()
                    st.metric("Avg Progress", f"{avg_progress:.1f}%")
                
                with col4:
                    total_hours = engineer_data['actual_hours'].sum()
                    st.metric("Hours Logged", f"{total_hours}")
                
                # Task breakdown
                status_breakdown = engineer_data['status'].value_counts()
                priority_breakdown = engineer_data['priority'].value_counts()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_status = px.pie(
                        values=status_breakdown.values,
                        names=status_breakdown.index,
                        title=f"Status Distribution - {engineer.split('(')[1].split(')')[0]}"
                    )
                    st.plotly_chart(fig_status, use_container_width=True)
                
                with col2:
                    fig_priority = px.bar(
                        x=priority_breakdown.index,
                        y=priority_breakdown.values,
                        title=f"Priority Distribution - {engineer.split('(')[1].split(')')[0]}",
                        color=priority_breakdown.index
                    )
                    st.plotly_chart(fig_priority, use_container_width=True)

# Export/Import functionality
st.sidebar.markdown("---")
st.sidebar.subheader("💾 Data Management")

if st.sidebar.button("📥 Export Data"):
    if st.session_state.assignments:
        export_data = {
            'assignments': st.session_state.assignments,
            'export_date': datetime.now().isoformat()
        }
        st.sidebar.download_button(
            label="⬇️ Download JSON",
            data=json.dumps(export_data, indent=2),
            file_name=f"ngc_assignments_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )
    else:
        st.sidebar.warning("No data to export")

uploaded_file = st.sidebar.file_uploader("📤 Import Data", type="json")
if uploaded_file is not None:
    try:
        import_data = json.load(uploaded_file)
        st.session_state.assignments = import_data['assignments']
        st.session_state.assignment_counter = max([a['id'] for a in st.session_state.assignments]) + 1 if st.session_state.assignments else 1
        st.sidebar.success("Data imported successfully!")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Import failed: {str(e)}")

# Route to different pages
if page == "Dashboard":
    dashboard()
elif page == "Create Assignment":
    create_assignment()
elif page == "Manage Assignments":
    manage_assignments()
elif page == "Reports & Analytics":
    reports_analytics()
elif page == "Engineer Workload":
    engineer_workload()

# Footer
st.markdown("---")
st.markdown("**NGC Assignment Tracker** | General Manager (D&E) | Developed for efficient task management")
