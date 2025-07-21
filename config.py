"""
Configuration management for GPTTutor
"""
import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class Config:
    """Centralized configuration management"""
    
    def __init__(self):
        self.load_env()
        self.load_user_profile()
        self.load_model_config()
        self.load_prompt_templates()
    
    def load_env(self):
        """Load environment variables"""
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
        self.openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in environment variables")
    
    def load_user_profile(self):
        """Load user profile with defaults"""
        self.user_profile = {
            "role": "helpful tutor",
            "tone": "encouraging and clear",
            "thinking_style": "step-by-step reasoning",
            "preferred_frameworks": ["decision tree", "swot analysis", "cost-benefit analysis"],
            "interaction_history": []
        }
        
        try:
            with open("user_profile.json", "r", encoding="utf-8") as f:
                profile_data = json.load(f)
                for key in ["role", "tone", "thinking_style", "preferred_frameworks"]:
                    if key in profile_data:
                        self.user_profile[key] = profile_data[key]
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # Use defaults
    
    def load_model_config(self):
        """Load model-specific configuration"""
        self.model_config = {
            "embedding_model": "all-MiniLM-L6-v2",
            "faiss_index_path": "vector_index.faiss",
            "metadata_path": "metadata.json",
            "frameworks_gpt_path": "frameworks_gpt.json"
        }
    
    def load_prompt_templates(self):
        """Load prompt templates"""
        self.prompt_templates = {
            "base_instruction": """You are a Decision Coach GPT. Your role is to help students make better decisions by thinking clearly, strategically, and—when appropriate—analytically.\n\nFor each question:\n**How to Strategize Your Decision**: Identify the decision type and key challenge.\n**Story in Action**: Use a short narrative (with a named character like Yin or Sarah) to illustrate the situation.\n**Analytical Tools (When Appropriate)**: If the decision involves uncertainty, trade-offs, optimization, or forecasting, introduce 1–2 relevant tools from our course (e.g., decision trees, Monte Carlo simulation, optimization, expected value, sensitivity analysis, predictive analysis, term sheet, behavior awareness, strategic analysis, financial analysis, competitive advantage). Explain how and why the tool helps.\n**Reflection Prompts**: Offer 2–3 thoughtful questions to help the student apply the strategy and/or tools to their context.\n**Concepts/Tools/Practice Reference**: Briefly list any tools or terms mentioned with a short definition or reminder.\n\nIf the question is more emotional, ethical, or about personal values, prioritize clarity, empathy, and structured reflection. Only include tools if they truly support the student's thinking.\n\nAvoid generic motivational advice. Focus on insight, structure, and practical application.\n\nIf the question is vague, help the student clarify the decision frame (alternatives, objectives, uncertainties, etc.).\n""",
            "tooltip_generation": "Given this context about {concept} in decision-making, provide a clear explanation in student-friendly terms. Keep it under 50 words and end with a period.\n\nContext: {context}\n\n{concept}:"
        }
    
    def get_prompt_template(self, template_name: str, **kwargs) -> str:
        """Get a prompt template with substitutions"""
        template = self.prompt_templates.get(template_name, "")
        return template.format(**kwargs)
    
    def get_personalized_instruction(self, user_id: Optional[str] = None) -> str:
        """Generate personalized instruction based on user profile"""
        base_instruction = self.prompt_templates["base_instruction"]
        
        # Add personalization
        personalization = f"Your role: {self.user_profile['role']}. Tone: {self.user_profile['tone']}. Thinking style: {self.user_profile['thinking_style']}."
        
        return f"{base_instruction}\n\n{personalization}\nAlways use this structure and do not skip any part."
    
    def update_user_profile(self, updates: Dict[str, Any]):
        """Update user profile and save to file"""
        self.user_profile.update(updates)
        
        try:
            with open("user_profile.json", "w", encoding="utf-8") as f:
                json.dump(self.user_profile, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save user profile: {e}")
    
    def get_framework_preferences(self) -> list:
        """Get user's preferred frameworks"""
        return self.user_profile.get("preferred_frameworks", [])
    
    def adapt_tone(self, query_type: str) -> str:
        """Adapt tone based on query type"""
        base_tone = self.user_profile["tone"]
        
        # Simple tone adaptation based on query keywords
        if any(word in query_type.lower() for word in ["urgent", "crisis", "emergency"]):
            return "calm and reassuring"
        elif any(word in query_type.lower() for word in ["complex", "difficult", "challenging"]):
            return "patient and thorough"
        elif any(word in query_type.lower() for word in ["simple", "basic", "quick"]):
            return "concise and direct"
        else:
            return base_tone 