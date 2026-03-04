"""
Input Validators
Validate user input and data integrity
"""

import re
from typing import Tuple

# List of Indian states
INDIAN_STATES = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
    'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
    'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
    'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
    'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
    'Andaman and Nicobar Islands', 'Chandigarh', 'Dadra and Nagar Haveli and Daman and Diu',
    'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry'
]


def validate_survey_number(survey_number: str) -> bool:
    """
    Check survey number format (alphanumeric with optional slashes)
    
    Args:
        survey_number: Survey number to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not survey_number or not isinstance(survey_number, str):
        return False
    
    # Allow alphanumeric characters, slashes, hyphens, and spaces
    pattern = r'^[A-Za-z0-9/\-\s]+$'
    return bool(re.match(pattern, survey_number.strip()))


def validate_district(district: str) -> bool:
    """
    Check district name is not empty and valid length
    
    Args:
        district: District name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not district or not isinstance(district, str):
        return False
    
    district = district.strip()
    return 3 <= len(district) <= 50


def validate_taluk(taluk: str) -> bool:
    """
    Check taluk name is not empty and valid length
    
    Args:
        taluk: Taluk name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not taluk or not isinstance(taluk, str):
        return False
    
    taluk = taluk.strip()
    return 3 <= len(taluk) <= 50


def validate_state(state: str) -> bool:
    """
    Check if state is in predefined list of Indian states
    
    Args:
        state: State name to validate
        
    Returns:
        True if valid or empty (optional field), False otherwise
    """
    if not state:
        return True  # Optional field
    
    if not isinstance(state, str):
        return False
    
    # Case-insensitive match
    state_lower = state.strip().lower()
    return any(s.lower() == state_lower for s in INDIAN_STATES)


def validate_owner_name(name: str) -> bool:
    """
    Check owner name is not empty and valid length
    
    Args:
        name: Owner name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not name or not isinstance(name, str):
        return False
    
    name = name.strip()
    return 3 <= len(name) <= 100


def validate_search_query(survey: str, district: str, taluk: str) -> Tuple[bool, str]:
    """
    Validate all required fields for property search
    
    Args:
        survey: Survey number
        district: District name
        taluk: Taluk name
        
    Returns:
        Tuple of (is_valid, error_message)
        (True, "") if valid
        (False, error_message) if invalid
    """
    if not survey:
        return False, "survey_number is required"
    
    if not validate_survey_number(survey):
        return False, "survey_number format is invalid"
    
    if not district:
        return False, "district is required"
    
    if not validate_district(district):
        return False, "district must be between 3-50 characters"
    
    if not taluk:
        return False, "taluk is required"
    
    if not validate_taluk(taluk):
        return False, "taluk must be between 3-50 characters"
    
    return True, ""


def validate_property_query(data: dict) -> str:
    """
    Validate property analysis query data
    
    Args:
        data: Request data dictionary
        
    Returns:
        Error message if invalid, empty string if valid
    """
    if not data:
        return "Request body is required"
    
    # Check for required field (at least land_id or survey details)
    if 'land_id' not in data and 'survey_number' not in data:
        return "Either land_id or survey_number is required"
    
    # If survey details provided, validate them
    if 'survey_number' in data:
        is_valid, error = validate_search_query(
            data.get('survey_number', ''),
            data.get('district', ''),
            data.get('taluk', '')
        )
        if not is_valid:
            return error
    
    return ""


def validate_land_id(land_id) -> bool:
    """
    Validate land ID format
    
    Args:
        land_id: Land ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    if land_id is None:
        return False
    
    # Accept both int and string representations
    if isinstance(land_id, int):
        return land_id > 0
    
    if isinstance(land_id, str):
        try:
            return int(land_id) > 0
        except ValueError:
            return False
    
    return False
