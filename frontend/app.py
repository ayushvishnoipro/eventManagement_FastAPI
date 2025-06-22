import streamlit as st
import requests
from datetime import datetime, date, time

# Backend API URL
API_BASE_URL = "http://localhost:8000"

def init_session_state():
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'user' not in st.session_state:
        st.session_state.user = None

def make_request(endpoint, method="GET", data=None, headers=None):
    url = f"{API_BASE_URL}{endpoint}"
    if headers is None:
        headers = {}
    
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return None

def login_page():
    st.title("Event Booking System - Login")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.header("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            data = {"email": email, "password": password}
            response = make_request("/login", "POST", data)
            
            if response:
                st.session_state.token = response["access_token"]
                st.session_state.user = response["user"]
                st.success("Login successful!")
                st.rerun()
    
    with tab2:
        st.header("Sign Up")
        name = st.text_input("Name", key="signup_name")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        role = st.selectbox("Role", ["customer", "manager"])
        
        if st.button("Sign Up"):
            data = {
                "name": name,
                "email": email,
                "password": password,
                "role": role
            }
            response = make_request("/signup", "POST", data)
            
            if response:
                st.success("Account created successfully! Please login.")

def manager_dashboard():
    st.title("Manager Dashboard")
    st.write(f"Welcome, {st.session_state.user['name']}!")
    
    tab1, tab2 = st.tabs(["Create Event", "View Events"])
    
    with tab1:
        st.header("Create New Event")
        title = st.text_input("Event Title")
        description = st.text_area("Description")
        
        col1, col2 = st.columns(2)
        with col1:
            event_date = st.date_input("Event Date")
        with col2:
            event_time = st.time_input("Event Time")
        
        location = st.text_input("Location")
        capacity = st.number_input("Capacity", min_value=1, value=50)
        
        if st.button("Create Event"):
            # Combine date and time
            event_datetime = datetime.combine(event_date, event_time)
            
            data = {
                "title": title,
                "description": description,
                "datetime": event_datetime.isoformat(),
                "location": location,
                "capacity": capacity
            }
            
            response = make_request("/events", "POST", data)
            if response:
                st.success("Event created successfully!")
    
    with tab2:
        st.header("All Events")
        events = make_request("/events")
        
        if events:
            for event in events:
                with st.expander(f"{event['title']} - {event['datetime'][:16]}"):
                    st.write(f"**Description:** {event['description']}")
                    st.write(f"**Location:** {event['location']}")
                    st.write(f"**Capacity:** {len(event['attendees'])}/{event['capacity']}")
                    
                    if event['attendees']:
                        st.write("**Attendees:**")
                        for attendee in event['attendees']:
                            st.write(f"- {attendee['name']} ({attendee['email']})")

def customer_dashboard():
    st.title("Customer Dashboard")
    st.write(f"Welcome, {st.session_state.user['name']}!")
    
    st.header("Available Events")
    events = make_request("/events")
    
    if events:
        for event in events:
            with st.expander(f"{event['title']} - {event['datetime'][:16]}"):
                st.write(f"**Description:** {event['description']}")
                st.write(f"**Location:** {event['location']}")
                st.write(f"**Available Spots:** {event['capacity'] - len(event['attendees'])}/{event['capacity']}")
                
                # Check if user is already registered
                user_registered = any(
                    attendee['id'] == st.session_state.user['id'] 
                    for attendee in event['attendees']
                )
                
                if user_registered:
                    st.success("You are registered for this event!")
                elif len(event['attendees']) >= event['capacity']:
                    st.error("Event is at full capacity")
                else:
                    if st.button(f"Register for {event['title']}", key=f"register_{event['id']}"):
                        data = {"event_id": event['id']}
                        response = make_request("/register", "POST", data)
                        
                        if response:
                            st.success("Registration successful!")
                            st.rerun()

def main():
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        if st.session_state.user:
            st.write(f"Logged in as: {st.session_state.user['name']}")
            st.write(f"Role: {st.session_state.user['role']}")
            
            if st.button("Logout"):
                st.session_state.token = None
                st.session_state.user = None
                st.rerun()
    
    # Main content
    if not st.session_state.user:
        login_page()
    else:
        if st.session_state.user['role'] == 'manager':
            manager_dashboard()
        else:
            customer_dashboard()

if __name__ == "__main__":
    main()
