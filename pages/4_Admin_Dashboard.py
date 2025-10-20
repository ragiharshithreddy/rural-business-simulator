"""
Admin Dashboard - Control panel for managing game data, scenarios, and settings
"""

import streamlit as st
import sys
from pathlib import Path
import json
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import BUSINESS_TYPES, DYNAMIC_EVENTS, AI_PROVIDERS
from utils.database import DatabaseManager

st.set_page_config(page_title="Admin Dashboard", page_icon="⚙️", layout="wide")

# Initialize
db = DatabaseManager()

# Admin password (in production, use proper authentication)
ADMIN_PASSWORD = "admin123"

# Custom CSS
st.markdown("""
    <style>
    .admin-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stat-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #4CAF50;
    }
    .data-table {
        background: white;
        padding: 1rem;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

def check_admin_access():
    """Check if user has admin access"""
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        st.markdown('<div class="admin-header"><h1>🔐 Admin Access Required</h1></div>', unsafe_allow_html=True)
        
        password = st.text_input("Enter Admin Password", type="password")
        
        if st.button("Login"):
            if password == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.success("✅ Access granted!")
                st.rerun()
            else:
                st.error("❌ Invalid password!")
        
        st.stop()

def main():
    check_admin_access()
    
    st.markdown('<div class="admin-header"><h1>⚙️ Admin Dashboard</h1><p>Manage game data, scenarios, and settings</p></div>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Admin Menu")
    admin_section = st.sidebar.radio(
        "Select Section",
        ["📊 Overview", "🎮 Scenario Manager", "💰 Market Prices", "📝 Custom Templates", "🔧 AI Settings", "📈 Analytics"]
    )
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state.admin_authenticated = False
        st.rerun()
    
    # Main content based on selection
    if admin_section == "📊 Overview":
        show_overview()
    
    elif admin_section == "🎮 Scenario Manager":
        show_scenario_manager()
    
    elif admin_section == "💰 Market Prices":
        show_market_prices()
    
    elif admin_section == "📝 Custom Templates":
        show_custom_templates()
    
    elif admin_section == "🔧 AI Settings":
        show_ai_settings()
    
    elif admin_section == "📈 Analytics":
        show_analytics()

def show_overview():
    """Display overview statistics"""
    st.markdown("### 📊 System Overview")
    
    stats = db.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("Total Users", stats['total_users'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("Active Businesses", stats['total_businesses'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("Scenarios Played", stats['total_scenarios'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("Active Auctions", stats['active_auctions'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent activity
    st.markdown("### 📝 Recent Activity")
    
    # Get recent users
    data = db._read_data()
    recent_users = sorted(
        data.get('users', {}).items(),
        key=lambda x: x[1].get('created_at', ''),
        reverse=True
    )[:10]
    
    if recent_users:
        st.markdown('<div class="data-table">', unsafe_allow_html=True)
        for user_id, user in recent_users:
            col_a, col_b, col_c = st.columns([2, 1, 1])
            
            with col_a:
                st.write(f"👤 {user['name']}")
            
            with col_b:
                st.write(f"Score: {user.get('total_score', 0)}")
            
            with col_c:
                st.write(f"Games: {user.get('games_played', 0)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Database backup
    st.markdown("---")
    st.markdown("### 💾 Database Management")
    
    col_x, col_y = st.columns(2)
    
    with col_x:
        if st.button("📥 Export Database", use_container_width=True):
            data = db._read_data()
            
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"game_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col_y:
        uploaded_file = st.file_uploader("📤 Import Database", type=['json'])
        
        if uploaded_file and st.button("Import"):
            try:
                imported_data = json.load(uploaded_file)
                db._write_data(imported_data)
                st.success("✅ Database imported successfully!")
            except Exception as e:
                st.error(f"❌ Import failed: {str(e)}")

def show_scenario_manager():
    """Manage game scenarios"""
    st.markdown("### 🎮 Scenario Manager")
    
    tab1, tab2 = st.tabs(["View Scenarios", "Add Scenario"])
    
    with tab1:
        # Get all scenarios
        data = db._read_data()
        scenarios = data.get('scenarios', {})
        
        st.markdown(f"**Total Scenarios:** {len(scenarios)}")
        
        if scenarios:
            for scenario_id, scenario in list(scenarios.items())[:20]:
                with st.expander(f"Scenario {scenario_id}"):
                    st.json(scenario)
                    
                    if st.button(f"Delete", key=f"del_{scenario_id}"):
                        del scenarios[scenario_id]
                        data['scenarios'] = scenarios
                        db._write_data(data)
                        st.success("Deleted!")
                        st.rerun()
    
    with tab2:
        st.markdown("#### Add Custom Scenario")
        
        with st.form("add_scenario"):
            business_type = st.selectbox("Business Type", list(BUSINESS_TYPES.keys()))
            
            scenario_text = st.text_area("Scenario Description", height=100)
            
            st.markdown("**Options:**")
            option1 = st.text_input("Option 1")
            option2 = st.text_input("Option 2")
            option3 = st.text_input("Option 3")
            
            st.markdown("**Consequences:**")
            cons1 = st.text_input("Consequence 1")
            cons2 = st.text_input("Consequence 2")
            cons3 = st.text_input("Consequence 3")
            
            st.markdown("**Scoring (0-10):**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("Option 1")
                risk1 = st.slider("Risk", 0, 10, 5, key="r1")
                reward1 = st.slider("Reward", 0, 10, 5, key="rw1")
                realism1 = st.slider("Realism", 0, 10, 5, key="rl1")
            
            with col2:
                st.markdown("Option 2")
                risk2 = st.slider("Risk", 0, 10, 5, key="r2")
                reward2 = st.slider("Reward", 0, 10, 5, key="rw2")
                realism2 = st.slider("Realism", 0, 10, 5, key="rl2")
            
            with col3:
                st.markdown("Option 3")
                risk3 = st.slider("Risk", 0, 10, 5, key="r3")
                reward3 = st.slider("Reward", 0, 10, 5, key="rw3")
                realism3 = st.slider("Realism", 0, 10, 5, key="rl3")
            
            if st.form_submit_button("Add Scenario"):
                template = {
                    "business_type": business_type,
                    "scenario": scenario_text,
                    "options": [option1, option2, option3],
                    "consequences": [cons1, cons2, cons3],
                    "score_logic": {
                        "option_1": {"risk": risk1, "reward": reward1, "realism": realism1},
                        "option_2": {"risk": risk2, "reward": reward2, "realism": realism2},
                        "option_3": {"risk": risk3, "reward": reward3, "realism": realism3}
                    }
                }
                
                db.add_scenario_template(template)
                st.success("✅ Scenario added!")

def show_market_prices():
    """Manage market prices"""
    st.markdown("### 💰 Market Price Manager")
    
    current_prices = db.get_market_prices()
    
    st.markdown("#### Update Market Prices")
    
    with st.form("update_prices"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Livestock Prices**")
            cow_price = st.number_input("Dairy Cow (₹)", value=current_prices.get('dairy_cow', 35000), step=1000)
            goat_price = st.number_input("Goat (₹)", value=current_prices.get('goat', 8000), step=500)
            chicken_price = st.number_input("Chickens (10) (₹)", value=current_prices.get('chickens_10', 2000), step=100)
        
        with col2:
            st.markdown("**Agricultural Prices**")
            seed_price = st.number_input("Seeds (50kg) (₹)", value=current_prices.get('seeds_50kg', 5000), step=500)
            fertilizer_price = st.number_input("Fertilizer (100kg) (₹)", value=current_prices.get('fertilizer_100kg', 3000), step=500)
            feed_price = st.number_input("Animal Feed (500kg) (₹)", value=current_prices.get('feed_500kg', 8000), step=500)
        
        if st.form_submit_button("Update Prices"):
            prices = {
                'dairy_cow': cow_price,
                'goat': goat_price,
                'chickens_10': chicken_price,
                'seeds_50kg': seed_price,
                'fertilizer_100kg': fertilizer_price,
                'feed_500kg': feed_price
            }
            
            db.update_market_prices(prices)
            st.success("✅ Prices updated!")
            st.rerun()
    
    # Display current prices
    st.markdown("---")
    st.markdown("#### Current Market Prices")
    
    if current_prices:
        for item, price in current_prices.items():
            st.write(f"**{item.replace('_', ' ').title()}:** ₹{price:,}")
    else:
        st.info("No prices set yet")

def show_custom_templates():
    """Manage custom scenario templates"""
    st.markdown("### 📝 Custom Scenario Templates")
    
    templates = db.get_scenario_templates()
    
    if templates:
        st.markdown(f"**Total Templates:** {len(templates)}")
        
        for template in templates:
            with st.expander(f"Template {template.get('id')} - {template.get('business_type')}"):
                st.markdown(f"**Scenario:** {template.get('scenario')}")
                st.markdown("**Options:**")
                for i, opt in enumerate(template.get('options', []), 1):
                    st.write(f"{i}. {opt}")
                
                st.json(template.get('score_logic', {}))
    else:
        st.info("No custom templates created yet")

def show_ai_settings():
    """Configure AI settings"""
    st.markdown("### 🔧 AI Configuration")
    
    current_settings = db.get_admin_settings()
    
    # AI Provider selection
    st.markdown("#### AI Provider Settings")
    
    provider = st.selectbox(
        "Select AI Provider",
        list(AI_PROVIDERS.keys()),
        index=1  # Default to Hugging Face
    )
    
    provider_config = AI_PROVIDERS[provider]
    
    st.info(f"**Model:** {provider_config['model']}")
    st.info(f"**API Base:** {provider_config['api_base']}")
    
    st.markdown("#### API Key Configuration")
    st.markdown(f"Set the `{provider_config['env_key']}` in your Streamlit secrets or environment variables.")
    
    api_key_input = st.text_input(
        f"{provider} API Key",
        type="password",
        help="This will be stored in the database"
    )
    
    if st.button("Save API Key"):
        settings = {
            'ai_provider': provider,
            'api_key_set': bool(api_key_input)
        }
        db.update_admin_settings(settings)
        st.success("✅ Settings saved!")
    
    st.markdown("---")
    
    # Test AI connection
    st.markdown("#### Test AI Connection")
    
    if st.button("Test Connection"):
        from utils.ai_manager import AIManager
        
        try:
            ai = AIManager(provider=provider)
            test_data = {
                'business_type': 'Dairy Farming',
                'location': 'Test Village',
                'capital': 50000,
                'resources': {},
                'employment_mode': 'Self-operated',
                'round': 1
            }
            
            with st.spinner("Testing AI connection..."):
                result = ai.generate_scenario(test_data)
            
            if result:
                st.success("✅ AI connection successful!")
                with st.expander("View Test Scenario"):
                    st.json(result)
            else:
                st.error("❌ No response from AI")
        
        except Exception as e:
            st.error(f"❌ Connection failed: {str(e)}")

def show_analytics():
    """Show detailed analytics"""
    st.markdown("### 📈 Analytics Dashboard")
    
    data = db._read_data()
    
    # Business type distribution
    st.markdown("#### Business Type Distribution")
    
    businesses = data.get('businesses', {})
    business_types = {}
    
    for biz in businesses.values():
        biz_type = biz.get('business_type', 'Unknown')
        business_types[biz_type] = business_types.get(biz_type, 0) + 1
    
    if business_types:
        col1, col2 = st.columns(2)
        
        with col1:
            for biz_type, count in business_types.items():
                st.metric(biz_type, count)
        
        with col2:
            # Create simple bar chart data
            st.bar_chart(business_types)
    
    st.markdown("---")
    
    # Top performers
    st.markdown("#### 🏆 Leaderboard")
    
    leaderboard = db.get_leaderboard(20)
    
    if leaderboard:
        for idx, entry in enumerate(leaderboard, 1):
            col_a, col_b, col_c, col_d = st.columns([1, 3, 2, 2])
            
            with col_a:
                if idx == 1:
                    st.markdown("🥇")
                elif idx == 2:
                    st.markdown("🥈")
                elif idx == 3:
                    st.markdown("🥉")
                else:
                    st.write(f"{idx}.")
            
            with col_b:
                st.write(entry['user_name'])
            
            with col_c:
                st.write(entry['business_type'])
            
            with col_d:
                st.write(f"Score: {entry['score']}")

if __name__ == "__main__":
    main()
