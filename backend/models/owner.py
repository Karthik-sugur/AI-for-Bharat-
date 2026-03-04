"""
Owner Model
Represents a property owner/family member in the ownership chain
"""

from datetime import datetime
from typing import Optional


class Owner:
    """Represent a property owner/family member in the ownership chain"""
    
    def __init__(
        self,
        owner_id: str,
        name: str,
        relationship_to_current: str,
        acquisition_date: str,
        disposal_date: Optional[str] = None,
        acquisition_method: str = "Unknown",
        document_reference: Optional[str] = None,
        is_current_owner: bool = False,
        **kwargs
    ):
        self.owner_id = owner_id
        self.name = name
        self.relationship_to_current = relationship_to_current
        self.acquisition_date = acquisition_date
        self.disposal_date = disposal_date
        self.acquisition_method = acquisition_method
        self.document_reference = document_reference
        self.is_current_owner = is_current_owner
        self.extra_data = kwargs
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'owner_id': self.owner_id,
            'name': self.name,
            'relationship_to_current': self.relationship_to_current,
            'acquisition_date': self.acquisition_date,
            'disposal_date': self.disposal_date,
            'acquisition_method': self.acquisition_method,
            'document_reference': self.document_reference,
            'is_current_owner': self.is_current_owner,
            **self.extra_data
        }
    
    def get_tenure_years(self) -> dict:
        """Calculate how long they owned the property"""
        try:
            start = datetime.strptime(self.acquisition_date, "%Y-%m-%d")
            if self.disposal_date:
                end = datetime.strptime(self.disposal_date, "%Y-%m-%d")
            else:
                end = datetime.now()
            
            delta = end - start
            years = delta.days // 365
            remaining_days = delta.days % 365
            months = remaining_days // 30
            days = remaining_days % 30
            
            return {
                'years': years,
                'months': months,
                'days': days,
                'total_days': delta.days
            }
        except (ValueError, TypeError):
            return {'years': 0, 'months': 0, 'days': 0, 'total_days': 0}
    
    def is_valid_ownership(self) -> bool:
        """Check if ownership record is complete"""
        if not self.name or not self.owner_id:
            return False
        if not self.acquisition_date:
            return False
        if not self.acquisition_method:
            return False
        return True
    
    def __repr__(self):
        return f"Owner(name={self.name}, date={self.acquisition_date})"
