"""
Land Records Service
Handles loading and querying land records data
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from utils.data_parser import (
    find_property_by_id,
    find_property_by_survey,
    parse_property_record,
    parse_ownership_chain,
    parse_encumbrances
)
from models.property import Property
from models.owner import Owner
from models.encumbrance import Encumbrance

logger = logging.getLogger(__name__)


class LandRecordsService:
    """Service for managing land records data"""
    
    def __init__(self, data: List[Dict]):
        """
        Initialize land records service
        
        Args:
            data: List of property records
        """
        self.land_records = data
        logger.info(f"Initialized LandRecordsService with {len(data)} records")
    
    def search_property_by_id(self, land_id: int) -> Tuple[Optional[Dict], Optional[Property]]:
        """
        Search for property by land_id
        
        Args:
            land_id: ID of the land record
            
        Returns:
            Tuple of (raw_data, Property) or (None, None) if not found
        """
        property_data = find_property_by_id(self.land_records, land_id)
        if property_data:
            try:
                property_obj = parse_property_record(property_data)
                return property_data, property_obj
            except Exception as e:
                logger.error(f"Error parsing property {land_id}: {str(e)}")
                return property_data, None
        return None, None
    
    def search_property(
        self,
        survey_number: str,
        district: str,
        taluk: str,
        state: Optional[str] = None,
        village: Optional[str] = None
    ) -> Tuple[Optional[Dict], Optional[Property]]:
        """
        Search for property by survey details
        
        Args:
            survey_number: Survey number
            district: District name
            taluk: Taluk name
            state: State name (optional)
            village: Village name (optional)
            
        Returns:
            Tuple of (raw_data, Property) or (None, None) if not found
        """
        property_data = find_property_by_survey(
            self.land_records,
            survey_number,
            district,
            taluk
        )
        
        if property_data:
            try:
                property_obj = parse_property_record(property_data)
                return property_data, property_obj
            except Exception as e:
                logger.error(f"Error parsing property: {str(e)}")
                return property_data, None
        
        return None, None
    
    def get_ownership_chain(self, property_data: Dict) -> List[Owner]:
        """
        Get ownership chain for a property
        
        Args:
            property_data: Raw property data
            
        Returns:
            List of Owner objects
        """
        # Try multiple possible keys for ownership data
        owners_data = (
            property_data.get('owners') or
            property_data.get('ownership_chain') or
            property_data.get('ownership_history') or
            []
        )
        
        return parse_ownership_chain(owners_data)
    
    def get_encumbrances(self, property_data: Dict) -> List[Encumbrance]:
        """
        Get encumbrances for a property
        
        Args:
            property_data: Raw property data
            
        Returns:
            List of Encumbrance objects
        """
        encumbrances_data = property_data.get('encumbrances') or property_data.get('encumbrance') or []
        
        # Handle single encumbrance object
        if isinstance(encumbrances_data, dict):
            encumbrances_data = [encumbrances_data]
        
        return parse_encumbrances(encumbrances_data)
    
    def get_all_properties(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all land records
        
        Args:
            limit: Maximum number of records to return (optional)
            
        Returns:
            List of land records
        """
        if limit:
            return self.land_records[:limit]
        return self.land_records
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the land records
        
        Returns:
            Dictionary containing statistics
        """
        total_records = len(self.land_records)
        
        if total_records == 0:
            return {
                'total_records': 0,
                'risk_distribution': {},
                'land_types': {},
                'active_loans': 0,
                'avg_confidence_score': 0
            }
        
        # Count by risk level
        risk_counts = {'Low': 0, 'Medium': 0, 'High': 0}
        for record in self.land_records:
            risk_level = record.get('risk_level', 'Unknown')
            if risk_level in risk_counts:
                risk_counts[risk_level] += 1
        
        # Count by land type
        land_types = {}
        for record in self.land_records:
            land_type = record.get('land_type') or record.get('property_type', 'Unknown')
            land_types[land_type] = land_types.get(land_type, 0) + 1
        
        # Count active loans
        active_loans = sum(1 for r in self.land_records
                          if r.get('encumbrance', {}).get('active', False) or
                          any(e.get('status') == 'Active' for e in r.get('encumbrances', []))
                          )
        
        # Calculate average confidence score
        avg_score = sum(r.get('title_confidence_score', 0) for r in self.land_records) / total_records
        
        return {
            'total_records': total_records,
            'risk_distribution': risk_counts,
            'land_types': land_types,
            'active_loans': active_loans,
            'avg_confidence_score': round(avg_score, 2)
        }
