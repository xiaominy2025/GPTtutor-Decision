"""
API Response structure for frontend integration
"""
from datetime import datetime
from typing import Dict, Any, Optional


class APIResponse:
    """Structured API response for frontend consumption"""
    
    def __init__(self, success: bool, data: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        self.success = success
        self.data = data or {}
        self.error = error
        self.timestamp = datetime.now().isoformat()
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def success_response(cls, data: Dict[str, Any]) -> 'APIResponse':
        """Create a successful response"""
        return cls(success=True, data=data)
    
    @classmethod
    def error_response(cls, error: str) -> 'APIResponse':
        """Create an error response"""
        return cls(success=False, error=error)


class AnswerData:
    """Structured answer data for frontend consumption"""
    
    def __init__(self, answer: str, tooltips: Dict[str, str], metadata: Dict[str, Any]):
        self.answer = answer
        self.tooltips = tooltips
        self.metadata = metadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "answer": self.answer,
            "tooltips": self.tooltips,
            "metadata": self.metadata
        } 