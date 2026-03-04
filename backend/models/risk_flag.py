"""
Risk Flag Model
Represents identified legal/title risks
"""

from typing import Optional


class RiskFlag:
    """Represent identified legal/title risks"""
    
    # Severity mapping to numeric values
    SEVERITY_MAP = {
        'Low': 25,
        'Medium': 50,
        'High': 75,
        'Critical': 100
    }
    
    def __init__(
        self,
        flag_id: str,
        category: str,
        severity: str,
        description: str,
        affected_period: Optional[str] = None,
        recommendation: Optional[str] = None,
        ai_explanation: Optional[str] = None,
        confidence_score: float = 0.8,
        **kwargs
    ):
        self.flag_id = flag_id
        self.category = category
        self.severity = severity
        self.description = description
        self.affected_period = affected_period
        self.recommendation = recommendation
        self.ai_explanation = ai_explanation
        self.confidence_score = confidence_score
        self.extra_data = kwargs
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'flag_id': self.flag_id,
            'category': self.category,
            'severity': self.severity,
            'description': self.description,
            'affected_period': self.affected_period,
            'recommendation': self.recommendation,
            'ai_explanation': self.ai_explanation,
            'confidence_score': self.confidence_score,
            **self.extra_data
        }
    
    def get_numeric_severity(self) -> int:
        """Return numeric severity (0-100)"""
        return self.SEVERITY_MAP.get(self.severity, 50)
    
    def __repr__(self):
        return f"RiskFlag(category={self.category}, severity={self.severity})"
