"""
Property Model
Represents a land property with all its attributes
"""

from datetime import datetime
from typing import Optional


class Property:
    """Represent a land property with all its attributes"""
    
    def __init__(
        self,
        survey_number: str,
        district: str,
        taluk: str,
        state: str,
        village: Optional[str] = None,
        area_sqft: Optional[float] = None,
        property_type: Optional[str] = None,
        current_owner: Optional[str] = None,
        registration_date: Optional[str] = None,
        last_mutation_date: Optional[str] = None,
        **kwargs
    ):
        self.survey_number = survey_number
        self.district = district
        self.taluk = taluk
        self.state = state
        self.village = village
        self.area_sqft = area_sqft
        self.property_type = property_type
        self.current_owner = current_owner
        self.registration_date = registration_date
        self.last_mutation_date = last_mutation_date
        # Store any additional fields
        self.extra_data = kwargs
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        result = {
            'survey_number': self.survey_number,
            'district': self.district,
            'taluk': self.taluk,
            'state': self.state,
            'village': self.village,
            'area_sqft': self.area_sqft,
            'property_type': self.property_type,
            'current_owner': self.current_owner,
            'registration_date': self.registration_date,
            'last_mutation_date': self.last_mutation_date
        }
        # Add any extra data
        result.update(self.extra_data)
        return result
    
    def validate(self) -> bool:
        """Check all required fields are present and valid"""
        if not self.survey_number or not isinstance(self.survey_number, str):
            return False
        if not self.district or not isinstance(self.district, str):
            return False
        if not self.taluk or not isinstance(self.taluk, str):
            return False
        if not self.state or not isinstance(self.state, str):
            return False
        return True
    
    def get_location_string(self) -> str:
        """Return formatted location string"""
        parts = []
        if self.village:
            parts.append(self.village)
        parts.extend([self.taluk, self.district, self.state])
        return ", ".join(parts)
    
    def __repr__(self):
        return f"Property(survey={self.survey_number}, location={self.get_location_string()})"
