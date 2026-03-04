"""
Data Parser
Load and parse synthetic JSON data
"""

import json
import logging
from typing import Dict, List, Optional
from pathlib import Path

from models.property import Property
from models.owner import Owner
from models.encumbrance import Encumbrance

logger = logging.getLogger(__name__)


def load_synthetic_data(file_path: str) -> List[Dict]:
    """
    Load JSON file from disk
    
    Args:
        file_path: Path to synthetic data JSON file
        
    Returns:
        List of property records
        
    Raises:
        FileNotFoundError: If file doesn't exist
        JSONDecodeError: If JSON is invalid
    """
    try:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Synthetic data file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both array and object with 'properties' key
        if isinstance(data, dict) and 'properties' in data:
            properties = data['properties']
        elif isinstance(data, list):
            properties = data
        else:
            logger.warning("Unexpected data format, returning as-is")
            properties = data
        
        logger.info(f"Loaded {len(properties)} property records from {file_path}")
        return properties
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error loading synthetic data: {str(e)}")
        raise


def find_property_by_survey(
    data: List[Dict],
    survey_number: str,
    village: Optional[str] = None,
    district: Optional[str] = None,
    state: Optional[str] = None
) -> List[Dict]:
    """
    Search synthetic data for matching properties
    
    Args:
        data: List of property records
        survey_number: Survey number to search for (required)
        village: Village/City/Location name (optional)
        district: District name (optional)
        state: State name (optional)
        
    Returns:
        List of matching property records
    """
    survey_lower = survey_number.strip().lower()
    village_lower = village.strip().lower() if village else None
    district_lower = district.strip().lower() if district else None
    state_lower = state.strip().lower() if state else None
    
    matches = []
    
    for property_record in data:
        # Match on survey_number (required, case-insensitive)
        prop_survey = str(property_record.get('survey_number', '')).strip().lower()
        
        if survey_lower not in prop_survey:
            continue
        
        # Optional: match on location/village
        if village_lower:
            prop_location = str(property_record.get('location', '')).strip().lower()
            if village_lower not in prop_location:
                continue
        
        # Optional: match on district
        if district_lower:
            prop_district = str(property_record.get('district', property_record.get('location', ''))).strip().lower()
            if district_lower not in prop_district:
                continue
        
        # Optional: match on state
        if state_lower:
            prop_state = str(property_record.get('state', '')).strip().lower()
            if state_lower not in prop_state:
                continue
        
        matches.append(property_record)
    
    return matches


def find_property_by_id(data: List[Dict], land_id) -> Optional[Dict]:
    """
    Search synthetic data for property by land_id
    
    Args:
        data: List of property records
        land_id: Land ID to search for (int or string)
        
    Returns:
        Property record or None if not found
    """
    # Convert to int if string
    try:
        land_id_int = int(land_id)
    except (ValueError, TypeError):
        return None
    
    for property_record in data:
        if property_record.get('land_id') == land_id_int:
            return property_record
    
    return None


def get_all_properties(data: List[Dict]) -> List[Dict]:
    """
    Return list of all properties in synthetic data
    
    Args:
        data: List of property records
        
    Returns:
        List of all property records
    """
    return data


def parse_property_record(raw_data: Dict) -> Property:
    """
    Convert raw JSON record to Property model
    
    Args:
        raw_data: Raw property data dictionary
        
    Returns:
        Property instance
        
    Raises:
        ValueError: If required fields are missing
    """
    # Extract required fields
    survey_number = raw_data.get('survey_number')
    district = raw_data.get('district') or raw_data.get('location')
    taluk = raw_data.get('taluk') or district  # Fallback to district if taluk not specified
    state = raw_data.get('state', 'Karnataka')  # Default to Karnataka
    
    if not survey_number:
        raise ValueError("survey_number is required")
    if not district:
        raise ValueError("district or location is required")
    
    # Extract optional fields
    village = raw_data.get('village')
    area_sqft = raw_data.get('area_sqft') or raw_data.get('size_acres')
    property_type = raw_data.get('property_type') or raw_data.get('land_type')
    current_owner = raw_data.get('current_owner')
    
    # Extract registration info
    registration = raw_data.get('registration', {})
    registration_date = registration.get('date') if isinstance(registration, dict) else raw_data.get('registration_date')
    
    # Mutation date
    legal = raw_data.get('legal', {})
    last_mutation_date = legal.get('mutation_date') if isinstance(legal, dict) else raw_data.get('last_mutation_date')
    
    # Create Property instance with all data
    property_instance = Property(
        survey_number=survey_number,
        district=district,
        taluk=taluk,
        state=state,
        village=village,
        area_sqft=area_sqft,
        property_type=property_type,
        current_owner=current_owner,
        registration_date=registration_date,
        last_mutation_date=last_mutation_date,
        **{k: v for k, v in raw_data.items() if k not in [
            'survey_number', 'district', 'taluk', 'state', 'village',
            'area_sqft', 'property_type', 'current_owner', 'registration_date',
            'last_mutation_date'
        ]}
    )
    
    return property_instance


def parse_ownership_chain(raw_data: List[Dict]) -> List[Owner]:
    """
    Convert list of owner records to Owner models
    
    Args:
        raw_data: List of raw owner data dictionaries
        
    Returns:
        Sorted list of Owner instances (chronological by acquisition date)
    """
    if not raw_data:
        return []
    
    owners = []
    
    for i, owner_data in enumerate(raw_data):
        try:
            owner_id = owner_data.get('owner_id', f'owner_{i+1}')
            name = owner_data.get('name') or owner_data.get('owner')
            relationship = owner_data.get('relationship_to_current', owner_data.get('type', 'Unknown'))
            acquisition_date = owner_data.get('acquisition_date') or owner_data.get('year', '1900-01-01')
            
            # Convert year to date format if needed
            if isinstance(acquisition_date, int):
                acquisition_date = f"{acquisition_date}-01-01"
            
            disposal_date = owner_data.get('disposal_date')
            acquisition_method = owner_data.get('acquisition_method', owner_data.get('type', 'Unknown'))
            document_reference = owner_data.get('document_reference')
            is_current_owner = owner_data.get('is_current_owner', False)
            
            owner = Owner(
                owner_id=owner_id,
                name=name,
                relationship_to_current=relationship,
                acquisition_date=str(acquisition_date),
                disposal_date=disposal_date,
                acquisition_method=acquisition_method,
                document_reference=document_reference,
                is_current_owner=is_current_owner
            )
            
            owners.append(owner)
        except Exception as e:
            logger.warning(f"Error parsing owner record {i}: {str(e)}")
            continue
    
    # Sort chronologically by acquisition date
    try:
        owners.sort(key=lambda x: x.acquisition_date)
    except Exception as e:
        logger.warning(f"Could not sort owners chronologically: {str(e)}")
    
    return owners


def parse_encumbrances(raw_data: List[Dict], filter_discharged: bool = False) -> List[Encumbrance]:
    """
    Convert list of encumbrance records to Encumbrance models
    
    Args:
        raw_data: List of raw encumbrance data dictionaries
        filter_discharged: If True, filter out discharged encumbrances
        
    Returns:
        List of Encumbrance instances
    """
    if not raw_data:
        return []
    
    encumbrances = []
    
    for i, enc_data in enumerate(raw_data):
        try:
            enc_id = enc_data.get('encumbrance_id', f'enc_{i+1}')
            enc_type = enc_data.get('type', 'Unknown')
            creditor = enc_data.get('creditor_name', enc_data.get('creditor', 'Unknown'))
            amount = enc_data.get('amount')
            reg_date = enc_data.get('registration_date')
            status = enc_data.get('status', 'Unknown')
            doc_ref = enc_data.get('document_reference')
            risk_level = enc_data.get('risk_level', 'Medium')
            notes = enc_data.get('notes')
            
            # Filter discharged if requested
            if filter_discharged and status.lower() == 'discharged':
                continue
            
            encumbrance = Encumbrance(
                encumbrance_id=enc_id,
                type=enc_type,
                creditor_name=creditor,
                amount=amount,
                registration_date=reg_date,
                status=status,
                document_reference=doc_ref,
                risk_level=risk_level,
                notes=notes
            )
            
            encumbrances.append(encumbrance)
        except Exception as e:
            logger.warning(f"Error parsing encumbrance record {i}: {str(e)}")
            continue
    
    return encumbrances
