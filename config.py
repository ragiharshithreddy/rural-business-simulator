"""
Configuration file for Rural Business Simulator
"""

# Business Types Configuration
BUSINESS_TYPES = {
    "Dairy Farming": {
        "icon": "🐄",
        "initial_capital": 50000,
        "initial_resources": {
            "cows": 5,
            "land_acres": 2,
            "equipment": ["milking machine", "storage tanks"]
        },
        "revenue_model": "daily_milk_sales"
    },
    "Solar Leasing": {
        "icon": "☀️",
        "initial_capital": 200000,
        "initial_resources": {
            "solar_panels": 10,
            "land_acres": 1,
            "equipment": ["inverter", "battery storage"]
        },
        "revenue_model": "monthly_lease"
    },
    "Fishing Business": {
        "icon": "🎣",
        "initial_capital": 80000,
        "initial_resources": {
            "boats": 2,
            "nets": 5,
            "equipment": ["ice storage", "fish baskets"]
        },
        "revenue_model": "catch_sales"
    },
    "Retail Shop": {
        "icon": "🏪",
        "initial_capital": 100000,
        "initial_resources": {
            "shop_space": 1,
            "inventory": 50,
            "equipment": ["shelves", "billing system"]
        },
        "revenue_model": "daily_sales"
    },
    "Poultry Farm": {
        "icon": "🐔",
        "initial_capital": 60000,
        "initial_resources": {
            "chickens": 100,
            "land_acres": 1,
            "equipment": ["coops", "feeders", "incubator"]
        },
        "revenue_model": "egg_meat_sales"
    },
    "Organic Farming": {
        "icon": "🌱",
        "initial_capital": 40000,
        "initial_resources": {
            "land_acres": 5,
            "seeds": 100,
            "equipment": ["tractor", "irrigation system"]
        },
        "revenue_model": "harvest_sales"
    }
}

# Language Configuration
SUPPORTED_LANGUAGES = {
    "English": "en",
    "Telugu": "te",
    "Hindi": "hi",
    "Tamil": "ta"
}

# Scoring System
SCORING_WEIGHTS = {
    "risk": 0.3,
    "reward": 0.4,
    "realism": 0.3
}

SCORE_THRESHOLDS = {
    "excellent": 80,
    "good": 60,
    "average": 40,
    "poor": 20
}

# Dynamic Events
DYNAMIC_EVENTS = [
    {
        "type": "weather",
        "events": ["Heavy Rain", "Drought", "Storm", "Flood"],
        "probability": 0.2
    },
    {
        "type": "market",
        "events": ["Price Drop", "Demand Surge", "Competition Increase", "Festival Season"],
        "probability": 0.3
    },
    {
        "type": "operational",
        "events": ["Equipment Breakdown", "Worker Absence", "Supply Shortage", "Quality Issue"],
        "probability": 0.25
    },
    {
        "type": "health",
        "events": ["Livestock Illness", "Crop Disease", "Personal Illness"],
        "probability": 0.15
    }
]

# AI Model Configuration
AI_PROVIDERS = {
    "openai": {
        "model": "gpt-4",
        "api_base": "https://api.openai.com/v1",
        "env_key": "OPENAI_API_KEY"
    },
    "huggingface": {
        "model": "google/flan-t5-base",
        "api_base": "https://api-inference.huggingface.co/models",
        "env_key": "HUGGINGFACE_API_KEY"
    },
    "anthropic": {
        "model": "claude-3-sonnet-20240229",
        "api_base": "https://api.anthropic.com/v1",
        "env_key": "ANTHROPIC_API_KEY"
    }
}

# Database Configuration
DATABASE_CONFIG = {
    "type": "json",  # Can be changed to "firebase" or "supabase"
    "file_path": "data/game_data.json",
    "backup_enabled": True
}

# Game Configuration
GAME_SETTINGS = {
    "max_rounds": 10,
    "starting_score": 0,
    "time_limit_per_decision": 300,  # seconds
    "enable_hints": True,
    "enable_retry": True,
    "max_retries": 2
}

# Auction Configuration
AUCTION_SETTINGS = {
    "min_bid_increment": 100,
    "auction_duration": 60,  # seconds
    "starting_price_factor": 0.7,  # 70% of market value
    "types": ["livestock", "equipment", "land", "inventory"]
}

# UI Theme
UI_THEME = {
    "primary_color": "#4CAF50",
    "secondary_color": "#2196F3",
    "background_color": "#F5F5F5",
    "text_color": "#212121",
    "success_color": "#4CAF50",
    "warning_color": "#FF9800",
    "danger_color": "#F44336"
}

# Prompt Templates
SCENARIO_PROMPT_TEMPLATE = """
Create a realistic business simulation scenario for a student running a {business_type} in {location}.

Business Context:
- Capital: ₹{capital}
- Resources: {resources}
- Employment: {employment_mode}
- Current Round: {round_number}

Generate a scenario that includes:
1. A clear situation description (2-3 sentences)
2. Three decision options with different risk-reward profiles
3. Realistic consequences for each option
4. Score metrics (risk: 0-10, reward: 0-10, realism: 0-10)
5. Optional dynamic event that could occur

Make it educational, engaging, and reflective of real rural business challenges.

Return ONLY a valid JSON object with this exact structure:
{{
  "scenario": "scenario description",
  "options": ["option 1", "option 2", "option 3"],
  "consequences": ["consequence 1", "consequence 2", "consequence 3"],
  "score_logic": {{
    "option_1": {{"risk": X, "reward": Y, "realism": Z}},
    "option_2": {{"risk": X, "reward": Y, "realism": Z}},
    "option_3": {{"risk": X, "reward": Y, "realism": Z}}
  }},
  "event": {{
    "description": "optional event description or null",
    "impact": "impact description or null"
  }}
}}
"""

TRANSLATION_PROMPT_TEMPLATE = """
Translate the following business scenario text from English to {language}.
Keep business terms clear and culturally appropriate.

Text to translate:
{text}

Return only the translated text, no explanations.
"""
