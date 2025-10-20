"""
Business Setup Page - Create and configure your rural business
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import BUSINESS_TYPES, SUPPORTED_LANGUAGES
from utils.database import DatabaseManager

st.set_page_config(page_title="Business Setup", page_icon="🏢", layout="wide")

# Initialize database
db = DatabaseManager()

# Custom CSS
st.markdown("""
    <style>
    .business-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .resource-box {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    st.title("🏢 Business Setup")
    st.markdown("### Create your rural enterprise and start your entrepreneurial journey!")
    
    # Check if user is logged in
    if 'user_name' not in st.session_state or not st.session_state.user_name:
        st.warning("⚠️ Please return to the home page and enter your name first!")
        return
    
    st.success(f"👋 Welcome, {st.session_state.user_name}!")
    
    # Create user in database if not exists
    if 'user_id' not in st.session_state:
        st.session_state.user_id = db.create_user(
            st.session_state.user_name,
            st.session_state.get('language', 'English')
        )
    
    # Business Setup Form
    with st.form("business_setup"):
        st.markdown("### 📋 Business Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Business Type Selection
            st.markdown("#### Choose Your Business Type")
            business_type = st.selectbox(
                "Business Type",
                options=list(BUSINESS_TYPES.keys()),
                format_func=lambda x: f"{BUSINESS_TYPES[x]['icon']} {x}"
            )
            
            # Display business info
            biz_info = BUSINESS_TYPES[business_type]
            st.markdown(f"""
            <div class="business-card">
                <h3>{biz_info['icon']} {business_type}</h3>
                <p><strong>Initial Capital:</strong> ₹{biz_info['initial_capital']:,}</p>
                <p><strong>Revenue Model:</strong> {biz_info['revenue_model'].replace('_', ' ').title()}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Location
            location = st.text_input(
                "Business Location",
                value="Peerancheru Village",
                help="Enter your village or area name"
            )
            
            # Employment Mode
            employment_mode = st.radio(
                "Employment Mode",
                ["Self-operated", "Hired Labor", "Mixed (Self + Hired)"],
                help="How will you manage operations?"
            )
        
        with col2:
            st.markdown("#### Initial Resources")
            
            # Display initial resources
            st.markdown('<div class="resource-box">', unsafe_allow_html=True)
            for resource, value in biz_info['initial_resources'].items():
                if isinstance(value, list):
                    st.markdown(f"**{resource.replace('_', ' ').title()}:** {', '.join(value)}")
                else:
                    st.markdown(f"**{resource.replace('_', ' ').title()}:** {value}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Additional Capital
            additional_capital = st.number_input(
                "Additional Investment (₹)",
                min_value=0,
                max_value=500000,
                value=0,
                step=10000,
                help="Any extra capital you want to invest"
            )
            
            total_capital = biz_info['initial_capital'] + additional_capital
            st.metric("Total Starting Capital", f"₹{total_capital:,}")
            
            # Investment Strategy
            st.markdown("#### Investment Priority")
            investment_priority = st.multiselect(
                "What will you invest in first?",
                ["Expand Resources", "Marketing", "Equipment Upgrade", "Working Capital", "Staff Training"],
                default=["Working Capital"]
            )
        
        st.markdown("---")
        
        # Goals
        st.markdown("### 🎯 Business Goals")
        col3, col4 = st.columns(2)
        
        with col3:
            monthly_revenue_goal = st.number_input(
                "Monthly Revenue Target (₹)",
                min_value=10000,
                max_value=1000000,
                value=50000,
                step=10000
            )
        
        with col4:
            timeline = st.selectbox(
                "Timeline to Break Even",
                ["3 months", "6 months", "1 year", "2 years"]
            )
        
        # Submit Button
        submitted = st.form_submit_button("🚀 Start My Business", use_container_width=True)
        
        if submitted:
            # Create business in database
            business_data = {
                "business_type": business_type,
                "location": location,
                "employment_mode": employment_mode,
                "capital": total_capital,
                "resources": biz_info['initial_resources'],
                "investment_priority": investment_priority,
                "revenue_goal": monthly_revenue_goal,
                "timeline": timeline,
                "language": st.session_state.get('language', 'English')
            }
            
            business_id = db.create_business(st.session_state.user_id, business_data)
            
            # Store in session state
            st.session_state.business_id = business_id
            st.session_state.business_data = business_data
            st.session_state.game_round = 1
            st.session_state.game_score = 0
            
            st.success("✅ Business created successfully!")
            st.balloons()
            st.info("👉 Navigate to 'Game Scenarios' to start playing!")
    
    # Show existing businesses
    st.markdown("---")
    st.markdown("### 📊 Your Existing Businesses")
    
    existing_businesses = db.get_user_businesses(st.session_state.user_id)
    
    if existing_businesses:
        for biz in existing_businesses:
            with st.expander(f"{BUSINESS_TYPES.get(biz.get('business_type', 'Unknown'), {}).get('icon', '🏢')} {biz.get('business_type')} - {biz.get('location')}"):
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    st.metric("Capital", f"₹{biz.get('capital', 0):,}")
                
                with col_b:
                    st.metric("Current Round", biz.get('current_round', 1))
                
                with col_c:
                    st.metric("Status", biz.get('status', 'active').title())
                
                if st.button(f"Continue This Business", key=biz['business_id']):
                    st.session_state.business_id = biz['business_id']
                    st.session_state.business_data = biz
                    st.session_state.game_round = biz.get('current_round', 1)
                    st.success("Business loaded! Go to 'Game Scenarios' to continue.")
    else:
        st.info("No businesses created yet. Create your first business above!")

if __name__ == "__main__":
    main()
