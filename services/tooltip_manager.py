"""
Tooltip management service
"""
import json
import re
from typing import Dict, Tuple, Optional, Any
from openai import OpenAI


class TooltipManager:
    """Enhanced tooltip management with better structure"""
    
    def __init__(self, config, openai_client):
        self.config = config
        self.client = openai_client
        self.prebuilt_tooltips = self._load_prebuilt_tooltips()
        self.custom_tooltip_cache = {}
        self.context_cache = {}
        self.token_usage = {"prebuilt": 0, "custom": 0, "prebuilt_dict": 0}
        self.session_stats = {"prebuilt_used": 0, "custom_generated": 0, "prebuilt_dict_used": 0}
    
    def _load_prebuilt_tooltips(self) -> Dict[str, str]:
        """Load prebuilt tooltips with error handling"""
        # Prebuilt tooltips dictionary for common concepts
        prebuilt = {
            "decision tree": "A visual tool that maps out different options and their potential outcomes to help make confident choices when faced with uncertainty.",
            "swot analysis": "A framework that helps identify strengths, weaknesses, opportunities, and threats to assess your situation comprehensively.",
            "cost-benefit analysis": "A systematic approach to compare the pros and cons of different options by weighing their advantages and disadvantages.",
            "expected utility": "A method for calculating the value of different scenarios when dealing with uncertainty and multiple possible outcomes.",
            "ooda loop": "A decision cycle (Observe, Orient, Decide, Act) that helps you stay agile and responsive in fast-changing situations.",
            "bounded rationality": "The recognition that good decisions don't require perfect information when time or information is limited.",
            "prospect theory": "Shows how people often value avoiding losses more than achieving gains when evaluating options.",
            "anchoring bias": "The tendency to rely too heavily on the first piece of information when making decisions.",
            "confirmation bias": "The tendency to seek out information that confirms existing beliefs while ignoring contradictory evidence.",
            "status quo bias": "The preference to keep things as they are rather than making changes, even when change might be beneficial.",
            "sunk cost fallacy": "The tendency to continue investing in a decision based on past investments rather than future benefits.",
            "framing effect": "How the way information is presented influences decision-making, even when the underlying facts are the same.",
            "endowment effect": "The tendency to value something more highly simply because you own it.",
            "escalation of commitment": "The tendency to continue investing in a failing course of action to justify previous investments.",
            "satisficing": "Choosing an option that is good enough rather than searching for the optimal solution.",
            "utility theory": "A framework for measuring the satisfaction or value derived from different outcomes and choices."
        }
        
        # Try to load GPT-polished frameworks
        try:
            with open("frameworks_gpt.json", "r", encoding="utf-8") as f:
                gpt_frameworks = json.load(f)
                prebuilt.update(gpt_frameworks)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # Use only built-in tooltips
        
        return prebuilt
    
    def get_tooltip(self, concept: str, context: str = "") -> Tuple[str, bool, str]:
        """Get tooltip with source tracking"""
        concept_lower = concept.lower()
        
        # Check prebuilt dictionary first (most efficient - 0 tokens)
        if concept_lower in self.prebuilt_tooltips:
            self.token_usage["prebuilt_dict"] += 1
            self.session_stats["prebuilt_dict_used"] += 1
            tooltip = self._clean_tooltip_text(self.prebuilt_tooltips[concept_lower])
            return tooltip, True, "prebuilt_dict"
        
        # Check custom cache
        if concept_lower in self.custom_tooltip_cache:
            self.token_usage["custom"] += 1
            self.session_stats["custom_generated"] += 1
            tooltip = self._clean_tooltip_text(self.custom_tooltip_cache[concept_lower])
            return tooltip, False, "cached_custom"
        
        # Generate custom tooltip only if context is unique
        if context and len(context) > 50:
            context_key = self._get_context_key(context)
            if context_key in self.context_cache:
                cached_tooltip = self.context_cache[context_key].get(concept_lower)
                if cached_tooltip:
                    self.token_usage["custom"] += 1
                    self.session_stats["custom_generated"] += 1
                    return cached_tooltip, False, "context_cached"
            
            custom_tooltip = self._generate_custom_tooltip(concept, context)
            cleaned_tooltip = self._clean_tooltip_text(custom_tooltip)
            self.custom_tooltip_cache[concept_lower] = cleaned_tooltip
            
            # Cache for similar contexts
            if context_key not in self.context_cache:
                self.context_cache[context_key] = {}
            self.context_cache[context_key][concept_lower] = cleaned_tooltip
            
            self.token_usage["custom"] += 1
            self.session_stats["custom_generated"] += 1
            return cleaned_tooltip, False, "new_custom"
        
        # Fallback
        fallback = f"Concept: {concept}."
        cleaned_fallback = self._clean_tooltip_text(fallback)
        self.token_usage["prebuilt"] += 1
        self.session_stats["prebuilt_used"] += 1
        return cleaned_fallback, True, "fallback"
    
    def _get_context_key(self, context: str) -> str:
        """Generate a key for context caching"""
        words = context.split()
        return f"{len(words)}_{context[:100].lower().replace(' ', '_')}"
    
    def _generate_custom_tooltip(self, concept: str, context: str) -> str:
        """Generate custom tooltip using GPT"""
        prompt = self.config.get_prompt_template("tooltip_generation", concept=concept, context=context[:200])
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.openai_temperature,
                max_tokens=100
            )
            content = response.choices[0].message.content
            if content is not None:
                return self._clean_tooltip_text(content.strip())
        except Exception:
            pass
        
        return f"Concept: {concept}."
    
    def _clean_tooltip_text(self, text: str, max_words: int = 50) -> str:
        """Clean and truncate tooltip text"""
        if not text:
            return ""
        
        text = text.strip()
        words = text.split()
        
        if len(words) <= max_words:
            if not text.endswith(('.', '!', '?')):
                return text + "."
            return text
        
        truncated_words = words[:max_words]
        truncated_text = " ".join(truncated_words)
        
        # Look for sentence boundaries
        sentence_endings = ['.', '!', '?']
        best_break_point = -1
        
        for ending in sentence_endings:
            last_ending = truncated_text.rfind(ending)
            if last_ending > best_break_point:
                best_break_point = last_ending
        
        if best_break_point > 0 and best_break_point > len(truncated_text) * 0.7:
            final_text = truncated_text[:best_break_point + 1]
        else:
            final_text = truncated_text
            if not final_text.endswith(('.', '!', '?', ':', ';', '...')):
                final_text += "..."
        
        return final_text
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get token usage statistics"""
        total_prebuilt = self.token_usage["prebuilt"] + self.token_usage["prebuilt_dict"]
        total_all = total_prebuilt + self.token_usage["custom"]
        
        return {
            "prebuilt_dict_used": self.token_usage["prebuilt_dict"],
            "prebuilt_gpt_used": self.token_usage["prebuilt"],
            "custom_generated": self.token_usage["custom"],
            "total_concepts": total_all,
            "efficiency": f"{total_prebuilt / total_all:.1%}" if total_all > 0 else "0%",
            "session_stats": self.session_stats
        } 