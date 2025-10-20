"""
AI Manager for handling API calls to different AI providers
"""

import os
import json
import requests
from typing import Dict, Any, Optional
import streamlit as st
from config import AI_PROVIDERS, SCENARIO_PROMPT_TEMPLATE, TRANSLATION_PROMPT_TEMPLATE


class AIManager:
    """Manages AI API calls for scenario generation and translation"""
    
    def __init__(self, provider: str = "huggingface"):
        self.provider = provider
        self.config = AI_PROVIDERS.get(provider, AI_PROVIDERS["huggingface"])
        self.api_key = self._get_api_key()
    
    def _get_api_key(self) -> Optional[str]:
        """Retrieve API key from environment or Streamlit secrets"""
        env_key = self.config["env_key"]
        
        # Try Streamlit secrets first
        try:
            if hasattr(st, 'secrets') and env_key in st.secrets:
                return st.secrets[env_key]
        except:
            pass
        
        # Fall back to environment variable
        return os.getenv(env_key)
    
    def generate_scenario(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a business scenario using AI"""
        
        if not self.api_key:
            return self._get_fallback_scenario(business_data)
        
        prompt = SCENARIO_PROMPT_TEMPLATE.format(
            business_type=business_data.get('business_type', 'General Business'),
            location=business_data.get('location', 'Rural Area'),
            capital=business_data.get('capital', 50000),
            resources=json.dumps(business_data.get('resources', {})),
            employment_mode=business_data.get('employment_mode', 'Self-operated'),
            round_number=business_data.get('round', 1)
        )
        
        try:
            if self.provider == "openai":
                return self._call_openai(prompt)
            elif self.provider == "huggingface":
                return self._call_huggingface(prompt)
            elif self.provider == "anthropic":
                return self._call_anthropic(prompt)
            else:
                return self._get_fallback_scenario(business_data)
        except Exception as e:
            st.error(f"AI API Error: {str(e)}")
            return self._get_fallback_scenario(business_data)
    
    def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API"""
        url = f"{self.config['api_base']}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.config["model"],
            "messages": [
                {"role": "system", "content": "You are a rural business education expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # Extract JSON from response
        return self._extract_json(content)
    
    def _call_huggingface(self, prompt: str) -> Dict[str, Any]:
        """Call Hugging Face Inference API"""
        url = f"{self.config['api_base']}/{self.config['model']}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "inputs": prompt,
            "parameters": {
                "temperature": 0.7,
                "max_new_tokens": 1000,
                "return_full_text": False
            }
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            content = result[0].get('generated_text', '')
        else:
            content = result.get('generated_text', '')
        
        return self._extract_json(content)
    
    def _call_anthropic(self, prompt: str) -> Dict[str, Any]:
        """Call Anthropic Claude API"""
        url = f"{self.config['api_base']}/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.config["model"],
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result['content'][0]['text']
        
        return self._extract_json(content)
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from AI response"""
        try:
            # Try direct JSON parse
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON in markdown code blocks
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Try to find JSON object
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            raise ValueError("Could not extract valid JSON from AI response")
    
    def translate_text(self, text: str, target_language: str) -> str:
        """Translate text to target language"""
        
        if target_language == "English" or not self.api_key:
            return text
        
        prompt = TRANSLATION_PROMPT_TEMPLATE.format(
            language=target_language,
            text=text
        )
        
        try:
            if self.provider == "openai":
                result = self._call_openai_simple(prompt)
            elif self.provider == "huggingface":
                result = self._call_huggingface_simple(prompt)
            else:
                return text
            
            return result
        except Exception as e:
            st.warning(f"Translation failed: {str(e)}")
            return text
    
    def _call_openai_simple(self, prompt: str) -> str:
        """Simple OpenAI call for translation"""
        url = f"{self.config['api_base']}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 500
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        return response.json()['choices'][0]['message']['content']
    
    def _call_huggingface_simple(self, prompt: str) -> str:
        """Simple Hugging Face call for translation"""
        url = f"{self.config['api_base']}/{self.config['model']}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "inputs": prompt,
            "parameters": {
                "temperature": 0.3,
                "max_new_tokens": 500,
                "return_full_text": False
            }
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            return result[0].get('generated_text', '')
        else:
            return result.get('generated_text', '')
    
    def _get_fallback_scenario(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return a hardcoded scenario when AI is unavailable"""
        business_type = business_data.get('business_type', 'General Business')
        
        scenarios = {
            "Dairy Farming": {
                "scenario": "Your dairy farm has been producing 40 liters of milk daily. A nearby cooperative offers to buy your entire production at ₹35/liter, but a new ice cream factory is willing to pay ₹45/liter if you can increase production to 60 liters daily. Your current setup needs investment to scale.",
                "options": [
                    "Accept the cooperative's stable offer and continue current production",
                    "Invest ₹30,000 in 2 more cows and equipment to meet factory demand",
                    "Split production: 40L to cooperative, invest slowly to scale for factory later"
                ],
                "consequences": [
                    "Steady income of ₹42,000/month but limited growth potential. Low risk, moderate reward.",
                    "Potential ₹81,000/month if successful, but ₹30,000 upfront risk and 2-month ramp-up time.",
                    "Balanced approach: ₹42,000/month now, gradual scaling. Medium risk, growing reward."
                ],
                "score_logic": {
                    "option_1": {"risk": 2, "reward": 5, "realism": 9},
                    "option_2": {"risk": 8, "reward": 9, "realism": 7},
                    "option_3": {"risk": 4, "reward": 7, "realism": 8}
                },
                "event": {
                    "description": "Monsoon forecast shows heavy rains next month which could affect fodder supply",
                    "impact": "May need to purchase additional fodder at 30% higher cost"
                }
            },
            "Solar Leasing": {
                "scenario": "You've installed 10 solar panels and are leasing to 5 households at ₹1,200/month each. A village school wants to lease 10 more panels, but you'll need ₹150,000 for expansion. A government subsidy covers 40% if you apply within 30 days.",
                "options": [
                    "Take a bank loan for full ₹150,000 at 12% interest",
                    "Apply for government subsidy, save ₹90,000, then expand",
                    "Partner with another solar entrepreneur to share costs and profits"
                ],
                "consequences": [
                    "Immediate expansion, ₹12,000/month revenue, but ₹18,000 interest annually. High debt risk.",
                    "Wait 45 days for subsidy approval, only ₹90,000 loan needed, ₹10,800/year interest. Delayed but safer.",
                    "Expand within 30 days, split revenue 50-50 (₹6,000/month each), share responsibilities and risks."
                ],
                "score_logic": {
                    "option_1": {"risk": 8, "reward": 8, "realism": 6},
                    "option_2": {"risk": 3, "reward": 7, "realism": 9},
                    "option_3": {"risk": 4, "reward": 6, "realism": 8}
                },
                "event": {
                    "description": null,
                    "impact": null
                }
            }
        }
        
        return scenarios.get(business_type, scenarios["Dairy Farming"])
