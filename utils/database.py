"""
Database Manager for storing and retrieving game data
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class DatabaseManager:
    """Manages data persistence for the game"""
    
    def __init__(self, db_path: str = "data/game_data.json"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize database file if it doesn't exist"""
        if not self.db_path.exists():
            initial_data = {
                "users": {},
                "businesses": {},
                "scenarios": {},
                "leaderboard": [],
                "auctions": {},
                "admin_settings": {
                    "scenario_templates": [],
                    "market_prices": {},
                    "event_probabilities": {}
                }
            }
            self._write_data(initial_data)
    
    def _read_data(self) -> Dict[str, Any]:
        """Read data from JSON file"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading database: {e}")
            return {}
    
    def _write_data(self, data: Dict[str, Any]):
        """Write data to JSON file"""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error writing database: {e}")
    
    # User Management
    def create_user(self, user_name: str, language: str = "English") -> str:
        """Create a new user and return user_id"""
        data = self._read_data()
        
        user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_name.replace(' ', '_')}"
        
        data["users"][user_id] = {
            "name": user_name,
            "language": language,
            "created_at": datetime.now().isoformat(),
            "total_score": 0,
            "games_played": 0,
            "achievements": []
        }
        
        self._write_data(data)
        return user_id
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data"""
        data = self._read_data()
        return data["users"].get(user_id)
    
    def update_user_score(self, user_id: str, score: int):
        """Update user's total score"""
        data = self._read_data()
        if user_id in data["users"]:
            data["users"][user_id]["total_score"] += score
            data["users"][user_id]["games_played"] += 1
            self._write_data(data)
    
    # Business Management
    def create_business(self, user_id: str, business_data: Dict[str, Any]) -> str:
        """Create a new business"""
        data = self._read_data()
        
        business_id = f"biz_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        data["businesses"][business_id] = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "current_round": 1,
            "total_score": 0,
            "status": "active",
            **business_data
        }
        
        self._write_data(data)
        return business_id
    
    def get_business(self, business_id: str) -> Optional[Dict[str, Any]]:
        """Get business data"""
        data = self._read_data()
        return data["businesses"].get(business_id)
    
    def update_business(self, business_id: str, updates: Dict[str, Any]):
        """Update business data"""
        data = self._read_data()
        if business_id in data["businesses"]:
            data["businesses"][business_id].update(updates)
            data["businesses"][business_id]["updated_at"] = datetime.now().isoformat()
            self._write_data(data)
    
    def get_user_businesses(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all businesses for a user"""
        data = self._read_data()
        return [
            {**biz, "business_id": biz_id}
            for biz_id, biz in data["businesses"].items()
            if biz.get("user_id") == user_id
        ]
    
    # Scenario Management
    def save_scenario(self, business_id: str, scenario_data: Dict[str, Any]) -> str:
        """Save a scenario result"""
        data = self._read_data()
        
        scenario_id = f"scen_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        data["scenarios"][scenario_id] = {
            "business_id": business_id,
            "timestamp": datetime.now().isoformat(),
            **scenario_data
        }
        
        self._write_data(data)
        return scenario_id
    
    def get_business_scenarios(self, business_id: str) -> List[Dict[str, Any]]:
        """Get all scenarios for a business"""
        data = self._read_data()
        return [
            {**scen, "scenario_id": scen_id}
            for scen_id, scen in data["scenarios"].items()
            if scen.get("business_id") == business_id
        ]
    
    # Leaderboard
    def update_leaderboard(self, user_id: str, score: int, business_type: str):
        """Update leaderboard with new score"""
        data = self._read_data()
        user = data["users"].get(user_id, {})
        
        entry = {
            "user_id": user_id,
            "user_name": user.get("name", "Unknown"),
            "score": score,
            "business_type": business_type,
            "timestamp": datetime.now().isoformat()
        }
        
        data["leaderboard"].append(entry)
        
        # Keep only top 100 entries
        data["leaderboard"] = sorted(
            data["leaderboard"],
            key=lambda x: x["score"],
            reverse=True
        )[:100]
        
        self._write_data(data)
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top leaderboard entries"""
        data = self._read_data()
        return data["leaderboard"][:limit]
    
    # Auction Management
    def create_auction(self, auction_data: Dict[str, Any]) -> str:
        """Create a new auction"""
        data = self._read_data()
        
        auction_id = f"auct_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        data["auctions"][auction_id] = {
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "bids": [],
            **auction_data
        }
        
        self._write_data(data)
        return auction_id
    
    def place_bid(self, auction_id: str, user_id: str, bid_amount: float):
        """Place a bid on an auction"""
        data = self._read_data()
        
        if auction_id in data["auctions"]:
            data["auctions"][auction_id]["bids"].append({
                "user_id": user_id,
                "amount": bid_amount,
                "timestamp": datetime.now().isoformat()
            })
            
            # Update highest bid
            data["auctions"][auction_id]["current_bid"] = bid_amount
            data["auctions"][auction_id]["highest_bidder"] = user_id
            
            self._write_data(data)
    
    def get_active_auctions(self) -> List[Dict[str, Any]]:
        """Get all active auctions"""
        data = self._read_data()
        return [
            {**auct, "auction_id": auct_id}
            for auct_id, auct in data["auctions"].items()
            if auct.get("status") == "active"
        ]
    
    def close_auction(self, auction_id: str):
        """Close an auction"""
        data = self._read_data()
        if auction_id in data["auctions"]:
            data["auctions"][auction_id]["status"] = "closed"
            data["auctions"][auction_id]["closed_at"] = datetime.now().isoformat()
            self._write_data(data)
    
    # Admin Settings
    def get_admin_settings(self) -> Dict[str, Any]:
        """Get admin settings"""
        data = self._read_data()
        return data.get("admin_settings", {})
    
    def update_admin_settings(self, settings: Dict[str, Any]):
        """Update admin settings"""
        data = self._read_data()
        data["admin_settings"].update(settings)
        self._write_data(data)
    
    def add_scenario_template(self, template: Dict[str, Any]):
        """Add a custom scenario template"""
        data = self._read_data()
        if "scenario_templates" not in data["admin_settings"]:
            data["admin_settings"]["scenario_templates"] = []
        
        data["admin_settings"]["scenario_templates"].append({
            "id": f"tmpl_{len(data['admin_settings']['scenario_templates']) + 1}",
            "created_at": datetime.now().isoformat(),
            **template
        })
        
        self._write_data(data)
    
    def get_scenario_templates(self) -> List[Dict[str, Any]]:
        """Get all scenario templates"""
        data = self._read_data()
        return data.get("admin_settings", {}).get("scenario_templates", [])
    
    def update_market_prices(self, prices: Dict[str, float]):
        """Update market prices"""
        data = self._read_data()
        if "market_prices" not in data["admin_settings"]:
            data["admin_settings"]["market_prices"] = {}
        
        data["admin_settings"]["market_prices"].update(prices)
        data["admin_settings"]["price_updated_at"] = datetime.now().isoformat()
        self._write_data(data)
    
    def get_market_prices(self) -> Dict[str, float]:
        """Get current market prices"""
        data = self._read_data()
        return data.get("admin_settings", {}).get("market_prices", {})
    
    # Analytics
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics"""
        data = self._read_data()
        
        return {
            "total_users": len(data.get("users", {})),
            "total_businesses": len(data.get("businesses", {})),
            "total_scenarios": len(data.get("scenarios", {})),
            "active_auctions": len([a for a in data.get("auctions", {}).values() if a.get("status") == "active"]),
            "total_games_played": sum(u.get("games_played", 0) for u in data.get("users", {}).values())
        }
    
    def get_business_analytics(self, business_id: str) -> Dict[str, Any]:
        """Get analytics for a specific business"""
        scenarios = self.get_business_scenarios(business_id)
        
        if not scenarios:
            return {
                "total_rounds": 0,
                "average_score": 0,
                "decisions_made": 0,
                "best_round": None,
                "worst_round": None
            }
        
        scores = [s.get("score", 0) for s in scenarios]
        
        return {
            "total_rounds": len(scenarios),
            "average_score": sum(scores) / len(scores),
            "decisions_made": len(scenarios),
            "best_round": max(scores) if scores else 0,
            "worst_round": min(scores) if scores else 0,
            "total_score": sum(scores)
        }
