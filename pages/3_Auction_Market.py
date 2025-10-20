"""
Auction Market Page - Buy and sell resources through auctions
"""

import streamlit as st
import sys
from pathlib import Path
import time
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import AUCTION_SETTINGS
from utils.database import DatabaseManager

st.set_page_config(page_title="Auction Market", page_icon="🔨", layout="wide")

# Initialize
db = DatabaseManager()

# Custom CSS
st.markdown("""
    <style>
    .auction-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin: 1rem 0;
    }
    .auction-card:hover {
        border-color: #4CAF50;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .live-badge {
        background: #4CAF50;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
    }
    .closed-badge {
        background: #9e9e9e;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
    }
    .bid-btn {
        background: #2196F3;
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 5px;
        border: none;
        font-size: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Auction items database
AUCTION_ITEMS = {
    "livestock": [
        {"name": "Dairy Cow", "base_price": 35000, "description": "Healthy milking cow, 3 years old"},
        {"name": "Goat", "base_price": 8000, "description": "Breeding goat, 2 years old"},
        {"name": "Chickens (10)", "base_price": 2000, "description": "Layer chickens, 6 months old"},
        {"name": "Buffalo", "base_price": 50000, "description": "Strong buffalo for milk and farming"}
    ],
    "equipment": [
        {"name": "Tractor (Used)", "base_price": 150000, "description": "Working condition, 5 years old"},
        {"name": "Irrigation Pump", "base_price": 12000, "description": "Electric pump, 2HP"},
        {"name": "Milking Machine", "base_price": 25000, "description": "Automatic milking machine"},
        {"name": "Solar Panel Set", "base_price": 45000, "description": "500W solar panel with inverter"}
    ],
    "land": [
        {"name": "1 Acre Farmland", "base_price": 200000, "description": "Fertile land with water access"},
        {"name": "0.5 Acre Plot", "base_price": 100000, "description": "Near village center"},
        {"name": "2 Acre Field", "base_price": 350000, "description": "Suitable for crops"}
    ],
    "inventory": [
        {"name": "50kg Seeds", "base_price": 5000, "description": "Wheat/Rice seeds, quality assured"},
        {"name": "Fertilizer (100kg)", "base_price": 3000, "description": "Organic fertilizer"},
        {"name": "Animal Feed (500kg)", "base_price": 8000, "description": "Nutritious cattle feed"},
        {"name": "Fishing Nets (5)", "base_price": 6000, "description": "Professional fishing nets"}
    ]
}

def create_sample_auctions():
    """Create sample auctions if none exist"""
    active_auctions = db.get_active_auctions()
    
    if len(active_auctions) < 3:
        import random
        
        for category in ["livestock", "equipment", "inventory"]:
            items = AUCTION_ITEMS[category]
            item = random.choice(items)
            
            auction_data = {
                "item_name": item["name"],
                "description": item["description"],
                "category": category,
                "starting_price": int(item["base_price"] * AUCTION_SETTINGS["starting_price_factor"]),
                "current_bid": int(item["base_price"] * AUCTION_SETTINGS["starting_price_factor"]),
                "market_value": item["base_price"],
                "highest_bidder": None,
                "ends_at": (datetime.now() + timedelta(seconds=AUCTION_SETTINGS["auction_duration"])).isoformat()
            }
            
            db.create_auction(auction_data)

def main():
    st.title("🔨 Auction Market")
    st.markdown("### Buy and sell resources through live auctions!")
    
    # Check if user is logged in
    if 'user_id' not in st.session_state:
        st.warning("⚠️ Please log in from the home page first!")
        return
    
    # Check business
    if 'business_id' not in st.session_state:
        st.info("💡 Set up a business first to participate in auctions!")
        return
    
    # Get business data
    business_data = db.get_business(st.session_state.business_id)
    available_capital = business_data.get('capital', 0)
    
    # Header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("#### 💰 Your Available Capital")
        st.metric("Balance", f"₹{available_capital:,}")
    
    with col2:
        if st.button("🔄 Refresh Auctions", use_container_width=True):
            st.rerun()
    
    # Create sample auctions
    create_sample_auctions()
    
    st.markdown("---")
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["🔴 Live Auctions", "✅ Your Bids", "📦 Sell Items"])
    
    with tab1:
        st.markdown("### 🔴 Active Auctions")
        
        active_auctions = db.get_active_auctions()
        
        if not active_auctions:
            st.info("No active auctions at the moment. Check back later!")
        else:
            for auction in active_auctions:
                auction_id = auction['auction_id']
                
                with st.container():
                    st.markdown('<div class="auction-card">', unsafe_allow_html=True)
                    
                    col_a, col_b, col_c = st.columns([2, 1, 1])
                    
                    with col_a:
                        st.markdown(f"### {auction['item_name']}")
                        st.markdown(f"**Category:** {auction['category'].title()}")
                        st.markdown(f"📝 {auction['description']}")
                        st.markdown(f"💎 Market Value: ₹{auction['market_value']:,}")
                    
                    with col_b:
                        st.markdown('<span class="live-badge">🔴 LIVE</span>', unsafe_allow_html=True)
                        st.markdown(f"**Starting Price**")
                        st.markdown(f"₹{auction['starting_price']:,}")
                        st.markdown(f"**Current Bid**")
                        st.markdown(f"₹{auction['current_bid']:,}")
                    
                    with col_c:
                        # Bid form
                        with st.form(f"bid_form_{auction_id}"):
                            min_bid = auction['current_bid'] + AUCTION_SETTINGS['min_bid_increment']
                            
                            bid_amount = st.number_input(
                                "Your Bid (₹)",
                                min_value=min_bid,
                                max_value=available_capital,
                                value=min_bid,
                                step=AUCTION_SETTINGS['min_bid_increment'],
                                key=f"bid_{auction_id}"
                            )
                            
                            submit_bid = st.form_submit_button("Place Bid 🔨", use_container_width=True)
                            
                            if submit_bid:
                                if bid_amount > available_capital:
                                    st.error("Insufficient capital!")
                                elif bid_amount < min_bid:
                                    st.error(f"Minimum bid is ₹{min_bid:,}")
                                else:
                                    # Place bid
                                    db.place_bid(auction_id, st.session_state.user_id, bid_amount)
                                    
                                    # Update capital
                                    db.update_business(st.session_state.business_id, {
                                        "capital": available_capital - bid_amount
                                    })
                                    
                                    st.success(f"✅ Bid placed: ₹{bid_amount:,}")
                                    time.sleep(1)
                                    st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### ✅ Your Bidding History")
        
        # Get all auctions and filter user's bids
        all_auctions = db.get_active_auctions()
        user_bids = []
        
        for auction in all_auctions:
            for bid in auction.get('bids', []):
                if bid['user_id'] == st.session_state.user_id:
                    user_bids.append({
                        'auction': auction,
                        'bid': bid
                    })
        
        if not user_bids:
            st.info("You haven't placed any bids yet!")
        else:
            for item in user_bids:
                auction = item['auction']
                bid = item['bid']
                
                is_winning = auction.get('highest_bidder') == st.session_state.user_id
                
                col_x, col_y, col_z = st.columns([2, 1, 1])
                
                with col_x:
                    st.markdown(f"**{auction['item_name']}**")
                    st.caption(auction['description'])
                
                with col_y:
                    st.metric("Your Bid", f"₹{bid['amount']:,}")
                
                with col_z:
                    if is_winning:
                        st.success("🏆 Winning!")
                    else:
                        st.warning("⏳ Outbid")
    
    with tab3:
        st.markdown("### 📦 Sell Your Items")
        st.markdown("Create an auction to sell your resources and equipment")
        
        with st.form("create_auction"):
            col_p, col_q = st.columns(2)
            
            with col_p:
                item_category = st.selectbox(
                    "Item Category",
                    ["livestock", "equipment", "land", "inventory"]
                )
                
                item_name = st.text_input("Item Name", placeholder="e.g., Dairy Cow")
                
                description = st.text_area(
                    "Description",
                    placeholder="Describe your item in detail...",
                    height=100
                )
            
            with col_q:
                market_value = st.number_input(
                    "Market Value (₹)",
                    min_value=1000,
                    max_value=1000000,
                    value=10000,
                    step=1000
                )
                
                starting_price = st.number_input(
                    "Starting Price (₹)",
                    min_value=500,
                    max_value=market_value,
                    value=int(market_value * 0.7),
                    step=500
                )
                
                duration = st.selectbox(
                    "Auction Duration",
                    ["1 minute", "5 minutes", "10 minutes", "30 minutes"],
                    index=1
                )
            
            create_auction_btn = st.form_submit_button("🚀 Create Auction", use_container_width=True)
            
            if create_auction_btn:
                if not item_name or not description:
                    st.error("Please fill all fields!")
                else:
                    # Parse duration
                    duration_map = {
                        "1 minute": 60,
                        "5 minutes": 300,
                        "10 minutes": 600,
                        "30 minutes": 1800
                    }
                    
                    auction_data = {
                        "item_name": item_name,
                        "description": description,
                        "category": item_category,
                        "starting_price": starting_price,
                        "current_bid": starting_price,
                        "market_value": market_value,
                        "seller_id": st.session_state.user_id,
                        "highest_bidder": None,
                        "ends_at": (datetime.now() + timedelta(seconds=duration_map[duration])).isoformat()
                    }
                    
                    auction_id = db.create_auction(auction_data)
                    
                    st.success(f"✅ Auction created successfully!")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
        
        st.markdown("---")
        st.markdown("#### 📊 Quick Sell Options")
        
        col_r, col_s, col_t = st.columns(3)
        
        with col_r:
            if st.button("🐄 Sell Livestock", use_container_width=True):
                st.info("Select livestock from your inventory to sell")
        
        with col_s:
            if st.button("🔧 Sell Equipment", use_container_width=True):
                st.info("Select equipment from your inventory to sell")
        
        with col_t:
            if st.button("📦 Sell Inventory", use_container_width=True):
                st.info("Select inventory items to sell")

if __name__ == "__main__":
    main()
