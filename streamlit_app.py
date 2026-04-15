import streamlit as st
import requests
import json

# Configuration
API_BASE_URL = "http://127.0.0.1:8001/api"

# Page config
st.set_page_config(
    page_title="AI Event Organizer",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Soft UI
st.markdown("""
<style>
    /* Add Custom CSS to make it beautiful */
    .stApp {
        background-color: #f7f9fc;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1000px;
    }
    h1 {
        color: #1E3A8A;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        text-align: center;
        margin-bottom: 30px;
    }
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #2563eb;
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "session_token" not in st.session_state:
    st.session_state.session_token = None
if "plan_result" not in st.session_state:
    st.session_state.plan_result = None

# ---- SIDEBAR: AUTHENTICATION ----
with st.sidebar:
    st.header("🔑 Authentication")
    
    if st.session_state.session_token is None:
        st.write("Please log in to your account.")
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="admin@example.com")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log In")
            
            if submitted:
                # 1. Hit login
                try:
                    resp = requests.post(
                        f"{API_BASE_URL}/auth/login",
                        data={"username": email, "password": password, "grant_type": "password"}
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        access_token = data.get("access_token")
                        st.session_state.access_token = access_token
                        
                        # 2. Hit session endpoint
                        sess_resp = requests.post(
                            f"{API_BASE_URL}/auth/session",
                            headers={"Authorization": f"Bearer {access_token}"}
                        )
                        if sess_resp.status_code == 200:
                            sess_data = sess_resp.json()
                            st.session_state.session_token = sess_data.get("token").get("access_token")
                            st.success("Successfully logged in & session created!")
                            st.rerun()
                        else:
                            st.error(f"Session failed: {sess_resp.text}")
                    else:
                        st.error(f"Login failed: {resp.text}")
                except Exception as e:
                    st.error(f"Error connecting to backend: {e}")
                    
        st.divider()
        st.write("Don't have an account?")
        with st.form("register_form"):
            reg_email = st.text_input("New Email")
            reg_pass = st.text_input("New Password", type="password")
            reg_submit = st.form_submit_button("Register")
            if reg_submit:
                try:
                    r_resp = requests.post(f"{API_BASE_URL}/auth/register", json={"email": reg_email, "password": reg_pass})
                    if r_resp.status_code == 200:
                        st.success("Registered successfully! You can now log in.")
                    else:
                        st.error(f"Registration failed: {r_resp.text}")
                except Exception as e:
                    st.error(f"Error connecting to backend: {e}")
    else:
        st.success("Authenticated!")
        if st.button("Log Out"):
            st.session_state.access_token = None
            st.session_state.session_token = None
            st.session_state.plan_result = None
            st.rerun()

# ---- MAIN AREA: EVENT FORM ----
st.markdown("<h1>✨ AI Conference Organizer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6b7280; font-size: 1.1rem;'>Orchestrate your next massive event exactly how you envision it, powered by a 6-Agent AI Crew.</p>", unsafe_allow_html=True)

if st.session_state.session_token is None:
    st.info("Please log in using the sidebar to start configuring your event.")
else:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Event Configuration")
    
    with st.form("event_config_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            event_type = st.selectbox("Event Type", ["Conference", "Music Festival", "Sporting Event", "Hackathon", "Exhibition", "Corporate Retreat"])
            event_category = st.text_input("Event Category", value="AI & Web3")
            event_topic = st.text_input("Event Topic (Focus)", value="The Future of Autonomous Agents")
            location = st.text_input("Location (City)", value="San Francisco, CA")
            
        with col2:
            expected_footfall = st.number_input("Expected Footfall", min_value=10, max_value=100000, value=1500)
            max_budget = st.number_input("Max Budget ($)", min_value=1000.0, max_value=100000000.0, value=250000.0, step=1000.0)
            target_audience = st.text_input("Target Audience", value="Enterprise Founders and Gen Z Devs")
            search_domains = st.text_input("Venue Search Domains", value="Cvent.com, eventlocations.com, peerspace.com")
            
        st.markdown("<br>", unsafe_allow_html=True)
        generate_btn = st.form_submit_button("🚀 Deploy Agentic Crew & Generate Plan", use_container_width=True)
        
        if generate_btn:
            payload = {
                "event_type": event_type,
                "event_category": event_category,
                "event_topic": event_topic,
                "location": location,
                "expected_footfall": int(expected_footfall),
                "max_budget": float(max_budget),
                "target_audience": target_audience,
                "search_domains": search_domains
            }
            
            with st.spinner("Deploying 6-Agent AI Crew (Sponsors, Speakers, Ops, GTM, Exhibitors, Venues)... This may take a few minutes!"):
                try:
                    headers = {"Authorization": f"Bearer {st.session_state.session_token}"}
                    response = requests.post(f"{API_BASE_URL}/event/plan", headers=headers, json=payload)
                    
                    if response.status_code == 200:
                        st.session_state.plan_result = response.json().get("plan", "")
                        st.success("Plan generated successfully!")
                    else:
                        st.error(f"Error generating plan: {response.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

# ---- RESULTS DISPLAY ----
if st.session_state.plan_result:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Master Event Plan")
    st.markdown(st.session_state.plan_result)
    st.markdown('</div>', unsafe_allow_html=True)
