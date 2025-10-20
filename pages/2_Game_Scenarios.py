"""
Game Scenarios Page - Play through business scenarios and make decisions
"""

import streamlit as st
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import GAME_SETTINGS, SCORING_WEIGHTS, SCORE_THRESHOLDS
from utils.database import DatabaseManager
from utils.ai_manager import AIManager

st.set_page_config(page_title="Game Scenarios", page_icon="🎮", layout="wide")

# Initialize
db = DatabaseManager()
ai = AIManager(provider="huggingface")  # Default to Hugging Face

# Custom CSS
st.markdown("""
    <style>
    .scenario-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        font-size: 1.1rem;
        margin: 1rem 0;
    }
    .option-button {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 2px solid #ddd;
        cursor: pointer;
    }
    .option-button:hover {
        border-color: #4CAF50;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .event-alert {
        background: #ff9800;
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 1rem 0;
    }
    .score-card {
        background: #4CAF50;
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

def calculate_score(risk: int, reward: int, realism: int) -> int:
    """Calculate weighted score"""
    weighted_score = (
        risk * SCORING_WEIGHTS["risk"] +
        reward * SCORING_WEIGHTS["reward"] +
        realism * SCORING_WEIGHTS["realism"]
    ) * 10
    
    return int(weighted_score)

def get_feedback(score: int) -> tuple:
    """Get feedback message and color based on score"""
    if score >= SCORE_THRESHOLDS["excellent"]:
        return "🌟 Excellent Decision!", "#4CAF50"
    elif score >= SCORE_THRESHOLDS["good"]:
        return "👍 Good Choice!", "#2196F3"
    elif score >= SCORE_THRESHOLDS["average"]:
        return "🤔 Acceptable, but could be better", "#FF9800"
    else:
        return "⚠️ Risky Decision - Review your strategy", "#F44336"

def main():
    st.title("🎮 Business Scenarios")
    
    # Check if business is set up
    if 'business_id' not in st.session_state or not st.session_state.business_id:
        st.warning("⚠️ Please set up your business first!")
        st.info("👉 Go to 'Business Setup' page to create your business.")
        return
    
    # Load business data
    business_data = db.get_business(st.session_state.business_id)
    if not business_data:
        st.error("Business not found! Please create a new business.")
        return
    
    # Header with business info
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Business", business_data.get('business_type', 'Unknown'))
    
    with col2:
        st.metric("Round", business_data.get('current_round', 1))
    
    with col3:
        st.metric("Total Score", business_data.get('total_score', 0))
    
    with col4:
        st.metric("Capital", f"₹{business_data.get('capital', 0):,}")
    
    st.markdown("---")
    
    # Initialize scenario in session state
    if 'current_scenario' not in st.session_state:
        st.session_state.current_scenario = None
    if 'scenario_completed' not in st.session_state:
        st.session_state.scenario_completed = False
    if 'selected_option' not in st.session_state:
        st.session_state.selected_option = None
    
    # Generate new scenario button
    if st.session_state.current_scenario is None or st.session_state.scenario_completed:
        if st.button("🎲 Generate New Scenario", use_container_width=True, type="primary"):
            with st.spinner("🤖 AI is creating your scenario..."):
                scenario = ai.generate_scenario(business_data)
                st.session_state.current_scenario = scenario
                st.session_state.scenario_completed = False
                st.session_state.selected_option = None
                st.rerun()
    
    # Display scenario
    if st.session_state.current_scenario:
        scenario = st.session_state.current_scenario
        
        # Scenario description
        st.markdown(f"""
        <div class="scenario-box">
            <h2>📖 Scenario</h2>
            <p>{scenario.get('scenario', 'No scenario available')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Dynamic event (if any)
        if scenario.get('event') and scenario['event'].get('description'):
            st.markdown(f"""
            <div class="event-alert">
                <h3>⚡ Dynamic Event!</h3>
                <p><strong>{scenario['event']['description']}</strong></p>
                <p><em>Impact: {scenario['event'].get('impact', 'Unknown impact')}</em></p>
            </div>
            """, unsafe_allow_html=True)
        
        # Options
        if not st.session_state.scenario_completed:
            st.markdown("### 🤔 What will you do?")
            
            options = scenario.get('options', [])
            
            for idx, option in enumerate(options, 1):
                if st.button(
                    f"Option {idx}: {option}",
                    key=f"opt_{idx}",
                    use_container_width=True
                ):
                    st.session_state.selected_option = idx - 1
                    st.session_state.scenario_completed = True
                    st.rerun()
        
        # Show result
        if st.session_state.scenario_completed and st.session_state.selected_option is not None:
            opt_idx = st.session_state.selected_option
            
            st.markdown("---")
            st.markdown("### 📊 Decision Result")
            
            # Get consequence
            consequences = scenario.get('consequences', [])
            if opt_idx < len(consequences):
                st.info(f"**Outcome:** {consequences[opt_idx]}")
            
            # Get score logic
            score_logic = scenario.get('score_logic', {})
            option_key = f"option_{opt_idx + 1}"
            
            if option_key in score_logic:
                metrics = score_logic[option_key]
                risk = metrics.get('risk', 5)
                reward = metrics.get('reward', 5)
                realism = metrics.get('realism', 5)
                
                # Calculate score
                total_score = calculate_score(risk, reward, realism)
                feedback_msg, feedback_color = get_feedback(total_score)
                
                # Display metrics
                col_a, col_b, col_c, col_d = st.columns(4)
                
                with col_a:
                    st.metric("Risk Level", f"{risk}/10")
                
                with col_b:
                    st.metric("Reward Potential", f"{reward}/10")
                
                with col_c:
                    st.metric("Realism Score", f"{realism}/10")
                
                with col_d:
                    st.metric("Total Score", total_score)
                
                # Feedback
                st.markdown(f"""
                <div class="score-card" style="background: {feedback_color}">
                    <h2>{feedback_msg}</h2>
                    <p>You earned {total_score} points this round!</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Update database
                current_round = business_data.get('current_round', 1)
                current_total = business_data.get('total_score', 0)
                
                # Save scenario result
                scenario_data = {
                    "round": current_round,
                    "option_selected": opt_idx + 1,
                    "score": total_score,
                    "risk": risk,
                    "reward": reward,
                    "realism": realism
                }
                db.save_scenario(st.session_state.business_id, scenario_data)
                
                # Update business
                db.update_business(st.session_state.business_id, {
                    "current_round": current_round + 1,
                    "total_score": current_total + total_score
                })
                
                # Update user
                db.update_user_score(st.session_state.user_id, total_score)
                
                # Update leaderboard
                db.update_leaderboard(
                    st.session_state.user_id,
                    total_score,
                    business_data.get('business_type', 'Unknown')
                )
                
                # Advice
                st.markdown("### 💡 Business Insight")
                
                if risk > 7:
                    st.warning("⚠️ High-risk decisions can lead to big rewards, but also big losses. Consider balancing with safer options.")
                elif reward < 5:
                    st.info("💭 Low reward options are safe but might limit growth. Look for opportunities to scale up.")
                
                if realism < 6:
                    st.warning("🤔 This decision might not be very realistic in rural contexts. Always consider local conditions and resources.")
                
                # Progress check
                if current_round >= GAME_SETTINGS["max_rounds"]:
                    st.success("🎉 Congratulations! You've completed the game!")
                    st.balloons()
                    
                    analytics = db.get_business_analytics(st.session_state.business_id)
                    
                    st.markdown("### 📈 Final Report")
                    col_x, col_y, col_z = st.columns(3)
                    
                    with col_x:
                        st.metric("Total Rounds", analytics['total_rounds'])
                    
                    with col_y:
                        st.metric("Average Score", f"{analytics['average_score']:.1f}")
                    
                    with col_z:
                        st.metric("Total Score", analytics['total_score'])
                    
                    if st.button("🔄 Start New Game"):
                        st.session_state.current_scenario = None
                        st.session_state.scenario_completed = False
                        db.update_business(st.session_state.business_id, {
                            "status": "completed"
                        })
                        st.info("Create a new business from the Business Setup page!")

if __name__ == "__main__":
    main()
