"""
Answer processing module for structured output
"""
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class AnswerSection:
    """Represents a section of the answer"""
    title: str
    content: str
    emoji: str


class AnswerProcessor:
    """Process and structure answers for frontend consumption"""
    
    def __init__(self):
        self.sections = {
            "strategic_thinking": {"emoji": "🧠", "title": "Strategic Thinking Lens"},
            "story_action": {"emoji": "📘", "title": "Story in Action"},
            "followup_prompts": {"emoji": "💬", "title": "Follow-up Prompts"},
            "concepts_tools": {"emoji": "🔧", "title": "Concepts/Tools"}
        }
    
    def parse_answer(self, answer: str) -> Dict[str, Any]:
        """Parse markdown answer into structured JSON"""
        parsed_sections = {}
        
        # Extract each section
        for section_key, section_info in self.sections.items():
            content = self._extract_section(answer, section_info["emoji"])
            if content:
                parsed_sections[section_key] = {
                    "title": section_info["title"],
                    "content": content.strip(),
                    "emoji": section_info["emoji"]
                }
        
        # Extract tooltips
        tooltips = self._extract_tooltips(answer)
        
        # Extract metadata
        metadata = self._extract_metadata(answer)
        
        return {
            "sections": parsed_sections,
            "tooltips": tooltips,
            "metadata": metadata,
            "raw_answer": answer
        }
    
    def _extract_section(self, answer: str, emoji: str) -> Optional[str]:
        """Extract content from a specific section"""
        # Find the section title based on emoji
        section_title = None
        for section_key, section_info in self.sections.items():
            if section_info["emoji"] == emoji:
                section_title = section_info["title"]
                break
        
        if not section_title:
            return None
        
        # Pattern 1: With emoji (old format)
        pattern1 = rf'\*\*{emoji}\s*([^*]+)\*\*(.*?)(?=\*\*[^🧠📘💬🔧]|$)'
        match1 = re.search(pattern1, answer, re.DOTALL | re.IGNORECASE)
        
        # Pattern 2: Without emoji (current format)
        pattern2 = rf'\*\*{section_title}\*\*(.*?)(?=\*\*[^🧠📘💬🔧]|$)'
        match2 = re.search(pattern2, answer, re.DOTALL | re.IGNORECASE)
        
        if match1:
            return match1.group(2).strip()
        elif match2:
            return match2.group(1).strip()
        return None
    
    def _extract_tooltips(self, answer: str) -> Dict[str, str]:
        """Extract tooltip definitions from answer"""
        tooltips = {}
        
        # Look for bold text that might be tooltips
        bold_pattern = r'\*\*([^*]+)\*\*'
        bold_matches = re.findall(bold_pattern, answer)
        
        for match in bold_matches:
            # Check if this looks like a tooltip (framework name)
            if any(framework.lower() in match.lower() for framework in [
                "decision tree", "swot", "cost-benefit", "expected utility",
                "bounded rationality", "prospect theory"
            ]):
                tooltips[match] = ""  # Placeholder for tooltip content
        
        return tooltips
    
    def _extract_metadata(self, answer: str) -> Dict[str, Any]:
        """Extract metadata from answer"""
        word_count = len(answer.split())
        section_count = len([s for s in self.sections.keys() if self._extract_section(answer, self.sections[s]["emoji"])])
        
        return {
            "word_count": word_count,
            "section_count": section_count,
            "has_tooltips": len(self._extract_tooltips(answer)) > 0,
            "structure_complete": section_count >= 2  # At least 2 sections
        }
    
    def validate_answer_structure(self, answer: str) -> Dict[str, Any]:
        """Validate answer structure and return issues"""
        issues = []
        warnings = []
        
        # Check for required sections
        for section_key, section_info in self.sections.items():
            content = self._extract_section(answer, section_info["emoji"])
            if not content:
                issues.append(f"Missing {section_info['title']} section")
            elif len(content.split()) < 10:
                warnings.append(f"{section_info['title']} section is very short")
        
        # Check answer length
        word_count = len(answer.split())
        if word_count < 50:
            issues.append("Answer too short (less than 50 words)")
        elif word_count > 800:
            warnings.append("Answer very long (over 800 words)")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "word_count": word_count
        } 