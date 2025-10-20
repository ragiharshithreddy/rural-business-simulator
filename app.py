import streamlit as st
from pathlib import Path
import sys

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

# Page configuration
st.set_page_config(
    page_title="Rural Business Simulator",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-size: 1.1rem;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'business_data' not in st.session_state:
    st.session_state.business_data = {}
if 'game_score' not in st.session_state:
    st.session_state.game_score = 0
if 'game_round' not in st.session_state:
    st.session_state.game_round = 1

# Main landing page
def main():
    st.markdown('<h1 class="main-header">🌾 Rural Business Simulator</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h2>Welcome to Rural Entrepreneurship Learning Platform</h2>
            <p>Learn business management through realistic scenarios, make strategic decisions, and grow your virtual rural enterprise!</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🎯 What You'll Learn:")
        st.markdown("""
        - **Business Planning**: Set up and manage rural enterprises
        - **Decision Making**: Navigate real-world business challenges
        - **Resource Management**: Optimize capital, labor, and inventory
        - **Market Dynamics**: Understand auctions, sales, and pricing
        - **Risk Management**: Handle unexpected events and crises
        """)
        
        st.markdown("---")
        
        st.markdown("### 🚀 Get Started:")
        
        # Quick start form
        with st.form("quick_start"):
            name = st.text_input("Your Name", placeholder="Enter your name")
            language = st.selectbox("Preferred Language", ["English", "Telugu", "Hindi", "Tamil"])
            
            submitted = st.form_submit_button("Start Your Journey →")
            
            if submitted and name:
                st.session_state.user_name = name
                st.session_state.language = language
                st.success(f"Welcome {name}! Navigate to 'Business Setup' to begin.")
                st.balloons()
        
        st.markdown("---")
        
        # Feature highlights
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("#### 📊 Features")
            st.markdown("""
            - Multiple business types
            - Dynamic AI scenarios
            - Real-time scoring
            - Progress tracking
            """)
        
        with col_b:
            st.markdown("#### 🎮 Game Modes")
            st.markdown("""
            - Story-based scenarios
            - Auction simulations
            - Market trading
            - Crisis management
            """)

if __name__ == "__main__":
    main()
