"""
Encumbrance Model
Represents loans, liens, and other claims on the property
"""

from typing import Optional


class Encumbrance:
    """Represent loans, liens, and other claims on the property"""
    
    # Risk level mapping to numeric scores
    RISK_LEVEL_MAP = {
        'Low': 20,
        'Medium': 50,
        'High': 75,
        'Critical': 100
    }
    
    def __init__(
        self,
        encumbrance_id: str,
        type: str,
        creditor_name: str,
        amount: Optional[float] = None,
        registration_date: Optional[str] = None,
        status: str = "Unknown",
        document_reference: Optional[str] = None,
        risk_level: str = "Medium",
        notes: Optional[str] = None,
        **kwargs
    ):
        self.encumbrance_id = encumbrance_id
        self.type = type
        self.creditor_name = creditor_name
        self.amount = amount
        self.registration_date = registration_date
        self.status = status
        self.document_reference = document_reference
        self.risk_level = risk_level
        self.notes = notes
        self.extra_data = kwargs
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'encumbrance_id': self.encumbrance_id,
            'type': self.type,
            'creditor_name': self.creditor_name,
            'amount': self.amount,
            'registration_date': self.registration_date,
            'status': self.status,
            'document_reference': self.document_reference,
            'risk_level': self.risk_level,
            'notes': self.notes,
            **self.extra_data
        }
    
    def is_active(self) -> bool:
        """Check if encumbrance is currently active"""
        return self.status.lower() in ['active', 'pending', 'disputed']
    
    def get_risk_score(self) -> int:
        """Return numeric risk score (0-100)"""
        base_score = self.RISK_LEVEL_MAP.get(self.risk_level, 50)
        
        # Increase score if active
        if self.is_active():
            base_score = min(100, base_score + 10)
        
        # Increase score for critical statuses
        if self.status.lower() in ['disputed', 'pending']:
            base_score = min(100, base_score + 15)
        
        return base_score
    
    def __repr__(self):
        return f"Encumbrance(type={self.type}, status={self.status}, risk={self.risk_level})"
