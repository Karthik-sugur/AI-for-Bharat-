"""
Land Records Service - Core Business Logic
Handles property search, ownership reconstruction, and risk analysis
"""

import json
import logging
import random
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import uuid

from app.config import settings

logger = logging.getLogger(__name__)


class LandRecordsService:
    """Service for land records and property analysis"""
    
    def __init__(self):
        """Initialize land records service"""
        self.records_list = []  # Raw list of 1000 records
        self.by_land_id = {}    # Index by land_id
        self.by_survey = {}     # Index by survey_number
        self.by_location = {}   # Index by location
        self._load_synthetic_data()
    
    def _load_synthetic_data(self) -> None:
        """Load and index the 1000 synthetic property records"""
        data_path = Path(__file__).parent.parent.parent / 'data' / 'synthetic_data.json'
        
        try:
            if data_path.exists():
                with open(data_path, 'r', encoding='utf-8') as f:
                    self.records_list = json.load(f)
                
                # Build indexes for fast lookup
                for record in self.records_list:
                    land_id = record.get('land_id')
                    survey = record.get('survey_number', '').lower().strip()
                    location = record.get('location', '').lower().strip()
                    
                    if land_id:
                        self.by_land_id[land_id] = record
                    if survey:
                        self.by_survey[survey] = record
                    if location:
                        if location not in self.by_location:
                            self.by_location[location] = []
                        self.by_location[location].append(record)
                
                logger.info(f"Loaded {len(self.records_list)} property records")
        except Exception as e:
            logger.warning(f"Could not load synthetic data: {e}")
            self.records_list = []
    
    def search_property(
        self,
        survey_number: str,
        district: str,
        taluk: str,
        village: Optional[str] = None,
        state: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for property in land records
        Uses the 1000-record synthetic dataset with multiple lookup strategies
        """
        
        # Strategy 1: Exact survey number match
        survey_key = survey_number.lower().strip()
        if survey_key in self.by_survey:
            return self._transform_record(self.by_survey[survey_key], survey_number, district, taluk, village, state)
        
        # Strategy 2: Location-based match (district/taluk/village)
        for loc_key in [village, taluk, district]:
            if loc_key:
                loc_lower = loc_key.lower().strip()
                if loc_lower in self.by_location:
                    record = self.by_location[loc_lower][0]  # Use first match
                    return self._transform_record(record, survey_number, district, taluk, village, state)
        
        # Strategy 3: Use seed-based selection from the 1000 records
        property_id = self._generate_property_id(survey_number, district, taluk, village)
        seed = int(property_id, 16) % 1000
        
        if self.records_list:
            # Map seed 0-999 to land_id 1-1000
            land_id = (seed % len(self.records_list)) + 1
            record = self.by_land_id.get(land_id)
            if record:
                return self._transform_record(record, survey_number, district, taluk, village, state)
        
        # Fallback: Generate synthetic property
        return self._generate_synthetic_property(
            property_id=property_id,
            survey_number=survey_number,
            district=district,
            taluk=taluk,
            village=village,
            state=state or 'Karnataka'
        )
    
    def _transform_record(self, record: Dict[str, Any], survey: str, district: str, taluk: str, village: Optional[str], state: Optional[str]) -> Dict[str, Any]:
        """
        Transform a synthetic data record to the API response format
        Preserves user's search input while using real data values
        """
        
        # Build ownership chain from record's ownership_chain
        ownership_chain = record.get('ownership_chain', [])
        owners = []
        for i, owner in enumerate(ownership_chain):
            owners.append({
                'owner_id': f"OWN-{record.get('land_id', 0):08d}-{i+1:03d}",
                'name': owner.get('owner', ''),
                'acquisition_date': f"{owner.get('year', 2000)}-01-01",
                'acquisition_method': owner.get('transaction_type', 'Transfer'),
                'document_number': f"DOC/{owner.get('year', 2000)}/{random.randint(1000, 9999)}",
                'document_status': owner.get('document_status', 'Registered'),
                'verified': owner.get('verified', True),
                'is_current': i == len(ownership_chain) - 1
            })
        
        # Build encumbrances
        enc_data = record.get('encumbrance', {})
        encumbrances = []
        if enc_data.get('active') or enc_data.get('type') not in ['None', None]:
            encumbrances.append({
                'encumbrance_id': f"ENC-{record.get('land_id', 0):08d}-001",
                'type': enc_data.get('type', 'Loan'),
                'holder': enc_data.get('lender', 'Bank'),
                'amount': (enc_data.get('amount_lakhs') or 0) * 100000,
                'currency': 'INR',
                'status': 'active' if enc_data.get('active') else 'discharged',
                'year_created': enc_data.get('year_created'),
                'year_closed': enc_data.get('year_closed'),
                'ec_certificate_available': enc_data.get('ec_certificate_available', True),
                'ec_period_covered': enc_data.get('ec_period_covered', '')
            })
        
        # Build risk flags from defects, disputes, and lineage analysis
        risk_flags = []
        
        for defect in record.get('defects', []):
            risk_flags.append({
                'category': 'documentation',
                'severity': 'medium',
                'title': defect.replace('_', ' ').title(),
                'description': f"Property has {defect.replace('_', ' ')} issue detected.",
                'impact': 'May affect clear title transfer',
                'recommended_action': 'Consult legal advisor'
            })
        
        for dispute in record.get('disputes', []):
            risk_flags.append({
                'category': 'legal',
                'severity': 'high' if dispute.get('active') else 'low',
                'title': f"{dispute.get('type', 'Dispute')} - {dispute.get('dispute_nature', 'Unknown')}",
                'description': f"{dispute.get('court', 'Court')}: {dispute.get('summary', '')}",
                'impact': dispute.get('resolution', 'Pending resolution'),
                'recommended_action': 'Review court case documents'
            })
        
        # Add lineage risk flags
        lineage_analysis = record.get('lineage_analysis', {})
        for flag in lineage_analysis.get('lineage_risk_flags', []):
            risk_flags.append({
                'category': 'ownership',
                'severity': 'medium',
                'title': 'Lineage Issue',
                'description': flag,
                'impact': 'May complicate ownership verification',
                'recommended_action': 'Verify with sub-registrar office'
            })
        
        # Add legal flags
        legal = record.get('legal', {})
        if legal.get('mutation_delay_flag'):
            risk_flags.append({
                'category': 'documentation',
                'severity': 'medium',
                'title': 'Mutation Delay',
                'description': f"Mutation delayed by {legal.get('mutation_delay_months', 0)} months",
                'impact': 'Revenue records may not reflect current ownership',
                'recommended_action': 'Follow up at taluk office'
            })
        if legal.get('area_mismatch_flag'):
            risk_flags.append({
                'category': 'documentation',
                'severity': 'high',
                'title': 'Area Mismatch',
                'description': f"Recorded: {legal.get('area_recorded_acres')} acres, Actual: {legal.get('area_actual_acres')} acres",
                'impact': 'May lead to boundary disputes',
                'recommended_action': 'Get fresh survey done'
            })
        if legal.get('undervaluation_flag'):
            risk_flags.append({
                'category': 'documentation',
                'severity': 'medium',
                'title': 'Undervaluation Detected',
                'description': f"Registered: ₹{legal.get('registration_value_lakhs', 0)}L, Market: ₹{legal.get('market_value_lakhs', 0)}L",
                'impact': 'May attract scrutiny from revenue department',
                'recommended_action': 'Review valuation documents'
            })
        if legal.get('loan_active'):
            risk_flags.append({
                'category': 'encumbrance',
                'severity': 'high',
                'title': 'Active Loan',
                'description': 'Property has an active loan encumbrance',
                'impact': 'Cannot transfer without loan clearance',
                'recommended_action': 'Obtain NOC from lender'
            })
        if legal.get('litigation_status') not in ['None', None, '']:
            risk_flags.append({
                'category': 'legal',
                'severity': 'high',
                'title': 'Litigation Status',
                'description': f"Property under litigation: {legal.get('litigation_status')}",
                'impact': 'Title transfer may be blocked',
                'recommended_action': 'Review case details in court'
            })
        
        # Build family tree
        family_tree_data = record.get('family_tree', {})
        gen1 = family_tree_data.get('generation_1', {})
        heirs = []
        for gen in ['generation_2', 'generation_3']:
            for heir in family_tree_data.get(gen, []):
                if isinstance(heir, dict):
                    heirs.append({
                        'name': heir.get('name', ''),
                        'relation': heir.get('relation', 'Heir'),
                        'gender': heir.get('gender', ''),
                        'alive': heir.get('alive', True),
                        'inheritance_share': heir.get('inheritance_share', '')
                    })
        
        # Build score breakdown
        score_breakdown = record.get('score_breakdown', {})
        
        return {
            'property_id': str(record.get('land_id', '')),
            'survey_number': survey,  # Use user's input
            'district': district,
            'taluk': taluk,
            'village': village or record.get('location', ''),
            'state': state or 'Karnataka',
            'property_type': record.get('land_type', 'Residential'),
            'area': f"{record.get('size_acres', 0)} acres" if record.get('size_acres') else '',
            'price_lakhs': record.get('price_lakhs'),
            'zoning': record.get('zoning', ''),
            'registration_info': record.get('registration', {}),
            'legal_info': legal,
            'owners': owners,
            'encumbrances': encumbrances,
            'risk_score': record.get('title_confidence_score', 500),
            'risk_level': record.get('risk_level', 'Medium'),
            'risk_color': record.get('risk_color', 'Yellow'),
            'risk_tier': record.get('risk_tier', 'medium'),
            'risk_flags': risk_flags,
            'score_breakdown': score_breakdown,
            'family_tree': {
                'original_owner': gen1.get('owner', ''),
                'original_spouse': gen1.get('spouse', ''),
                'acquired_year': gen1.get('acquired_year'),
                'acquisition_type': gen1.get('acquisition_type', ''),
                'heirs': heirs,
                'partition_status': 'Filed' if legal.get('partition_record_present') else 'Not Filed',
                'noc_required_from': lineage_analysis.get('noc_required_from', [])
            },
            'heirs_in_line': record.get('heirs_in_line', []),
            'lineage_analysis': lineage_analysis,
            'soil_and_terrain': record.get('soil_and_terrain', {}),
            'infrastructure': record.get('infrastructure', {}),
            'govt_approvals': record.get('govt_approvals', {}),
            'mutation_status': 'current' if legal.get('mutation_status') == 'Updated' else 'outdated',
            'data_source': 'synthetic_database',
            'record_land_id': record.get('land_id'),
            'record_location': record.get('location', '')
        }
    
    def _generate_property_id(
        self,
        survey_number: str,
        district: str,
        taluk: str,
        village: Optional[str] = None
    ) -> str:
        """Generate unique property ID from inputs"""
        key_parts = [
            survey_number.lower().strip(),
            district.lower().strip(),
            taluk.lower().strip()
        ]
        if village:
            key_parts.append(village.lower().strip())
        
        key_string = '|'.join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]
    
    def _generate_synthetic_property(
        self,
        property_id: str,
        survey_number: str,
        district: str,
        taluk: str,
        village: Optional[str],
        state: str
    ) -> Dict[str, Any]:
        """Generate synthetic property data for prototyping"""
        
        # Use property_id as seed for deterministic generation
        seed = int(property_id, 16) % 1000
        random.seed(seed)
        
        # Property type based on seed
        property_types = ['Residential', 'Agricultural', 'Commercial', 'Industrial']
        property_type = property_types[seed % len(property_types)]
        
        # Area based on property type
        if property_type == 'Agricultural':
            area = f"{random.uniform(0.5, 10):.2f} acres"
        elif property_type == 'Industrial':
            area = f"{random.randint(2000, 20000)} sq ft"
        else:
            area = f"{random.randint(600, 5000)} sq ft"
        
        # Generate ownership chain
        owners = self._generate_ownership_chain(seed)
        
        # Generate encumbrances
        encumbrances = self._generate_encumbrances(seed, property_type)
        
        # Calculate risk score
        risk_data = self._calculate_risk_score(owners, encumbrances, property_type)
        
        return {
            'property_id': property_id,
            'survey_number': survey_number,
            'district': district,
            'taluk': taluk,
            'village': village,
            'state': state,
            'property_type': property_type,
            'area': area,
            'boundaries': {
                'north': self._generate_boundary(),
                'south': self._generate_boundary(),
                'east': self._generate_boundary(),
                'west': self._generate_boundary()
            },
            'registration_info': {
                'sub_registrar_office': f"{taluk} Sub-Registrar Office",
                'last_registered_date': self._generate_date(-365, -30),
                'book_number': f"I/{random.randint(1000, 9999)}/{random.randint(2018, 2024)}"
            },
            'owners': owners,
            'encumbrances': encumbrances,
            'risk_score': risk_data['score'],
            'risk_level': risk_data['level'],
            'risk_flags': risk_data['flags'],
            'mutation_status': 'current' if seed % 3 != 0 else 'outdated',
            'ec_issued_date': self._generate_date(-180, -7),
            'data_source': 'synthetic',
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _generate_ownership_chain(self, seed: int) -> List[Dict[str, Any]]:
        """Generate synthetic ownership chain"""
        
        # Indian names for synthetic data
        first_names = [
            'Ramesh', 'Suresh', 'Mahesh', 'Rajesh', 'Dinesh',
            'Arun', 'Vijay', 'Kumar', 'Mohan', 'Ravi',
            'Priya', 'Kavitha', 'Lakshmi', 'Anita', 'Sunita'
        ]
        last_names = [
            'Kumar', 'Patel', 'Sharma', 'Reddy', 'Nair',
            'Iyer', 'Das', 'Murthy', 'Rao', 'Singh'
        ]
        
        random.seed(seed)
        chain_length = random.randint(2, 5)
        
        owners = []
        current_year = datetime.now().year
        start_year = current_year - random.randint(20, 50)
        
        transfer_methods = ['Sale Deed', 'Inheritance', 'Gift Deed', 'Partition', 'Government Allotment']
        
        for i in range(chain_length):
            first = random.choice(first_names)
            last = random.choice(last_names)
            name = f"{first} {last}"
            
            # Calculate dates
            acquisition_year = start_year + (i * random.randint(3, 12))
            if acquisition_year > current_year:
                acquisition_year = current_year - random.randint(1, 3)
            
            acquisition_date = f"{acquisition_year}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
            
            # Determine transfer method
            if i == 0:
                method = 'Government Allotment'
            elif random.random() < 0.4:
                method = 'Inheritance'
            else:
                method = random.choice(transfer_methods[:3])
            
            owner = {
                'owner_id': f"OWN-{seed:08d}-{i+1:03d}",
                'name': name,
                'acquisition_date': acquisition_date,
                'disposal_date': None if i == chain_length - 1 else f"{acquisition_year + random.randint(3, 10)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                'acquisition_method': method,
                'document_number': f"DOC/{acquisition_year}/{random.randint(1000, 9999)}",
                'share_percentage': 100.0 if i == chain_length - 1 else 100.0,
                'is_current': i == chain_length - 1
            }
            
            # Add heirs for inheritance cases
            if method == 'Inheritance' and i == chain_length - 1:
                owner['heirs'] = [
                    {'name': f"{random.choice(first_names)} {last}", 'relation': 'Son'},
                    {'name': f"{random.choice(first_names)} {last}", 'relation': 'Daughter'},
                ]
            
            owners.append(owner)
        
        return owners
    
    def _generate_encumbrances(self, seed: int, property_type: str) -> List[Dict[str, Any]]:
        """Generate synthetic encumbrances with more varied risk levels"""
        
        random.seed(seed + 1000)
        
        encumbrances = []
        
        # Use modular arithmetic for more varied distribution
        # This produces a wider spread of risk levels
        seed_factor = (seed * 7 + 13) % 100  # Better distribution
        
        if seed_factor < 15:
            num_encumbrances = 0  # Clean title (15%)
        elif seed_factor < 35:
            num_encumbrances = 1  # Minor issues (20%)
        elif seed_factor < 60:
            num_encumbrances = 2  # Moderate issues (25%)
        elif seed_factor < 80:
            num_encumbrances = 3  # Significant issues (20%)
        else:
            num_encumbrances = random.randint(3, 5)  # Severe issues (20%)
        
        banks = ['SBI', 'HDFC Bank', 'ICICI Bank', 'Axis Bank', 'Bank of Baroda', 'Canara Bank']
        
        for i in range(num_encumbrances):
            # Weight towards more impactful encumbrance types
            enc_choices = ['Loan', 'Loan', 'Mortgage', 'Mortgage', 'Lien', 'Court Order']
            enc_type = random.choice(enc_choices)
            
            if enc_type == 'Loan':
                holder = f"{random.choice(banks)} Home Loan"
                amount = random.randint(15, 80) * 100000  # 15L to 80L
                # Make active status more likely (70% active)
                status = random.choices(['active', 'discharged'], weights=[70, 30])[0]
            elif enc_type == 'Mortgage':
                holder = f"{random.choice(banks)} Mortgage"
                amount = random.randint(10, 50) * 100000
                # 60% active
                status = random.choices(['active', 'discharged'], weights=[60, 40])[0]
            else:
                holder = 'Court Registry' if enc_type == 'Court Order' else 'Revenue Department'
                amount = None
                # 65% active for court orders/liens
                status = random.choices(['active', 'resolved'], weights=[65, 35])[0]
            
            encumbrance = {
                'encumbrance_id': f"ENC-{seed:08d}-{i+1:03d}",
                'type': enc_type,
                'holder': holder,
                'amount': amount,
                'currency': 'INR',
                'registration_date': self._generate_date(-1825, -365),
                'status': status,
                'document_number': f"ENC/{random.randint(2015, 2023)}/{random.randint(1000, 9999)}",
                'description': self._generate_encumbrance_description(enc_type, holder)
            }
            
            encumbrances.append(encumbrance)
        
        return encumbrances
    
    def _generate_encumbrance_description(self, enc_type: str, holder: str) -> str:
        """Generate description for encumbrance"""
        
        descriptions = {
            'Loan': f"Housing loan from {holder}. Monthly EMI pending.",
            'Mortgage': f"Property mortgaged to {holder} as collateral for business loan.",
            'Lien': "Lien registered by revenue department for pending property tax.",
            'Court Order': "Interim stay order from civil court regarding ownership dispute."
        }
        
        return descriptions.get(enc_type, f"{enc_type} registered by {holder}")
    
    def _calculate_risk_score(
        self,
        owners: List[Dict],
        encumbrances: List[Dict],
        property_type: str
    ) -> Dict[str, Any]:
        """Calculate risk score based on property data"""
        
        score = 1000  # Start with perfect score
        flags = []
        
        # Check ownership chain
        if len(owners) == 0:
            score -= 300
            flags.append({
                'category': 'ownership',
                'severity': 'high',
                'title': 'No ownership records found',
                'description': 'Unable to trace ownership chain for this property.',
                'impact': 'Cannot verify legal ownership status',
                'recommended_action': 'Obtain certified copies from sub-registrar office'
            })
        
        # Check for inheritance without partition
        current_owner = next((o for o in owners if o.get('is_current')), None)
        if current_owner and current_owner.get('acquisition_method') == 'Inheritance':
            if current_owner.get('heirs'):
                score -= 100
                flags.append({
                    'category': 'documentation',
                    'severity': 'medium',
                    'title': 'Partition record missing',
                    'description': f"{len(current_owner['heirs'])} legal heirs identified but no partition deed filed.",
                    'impact': 'Multiple claimants may dispute ownership',
                    'recommended_action': 'File formal partition deed co-signed by all legal heirs'
                })
        
        # Check encumbrances
        active_loans = [e for e in encumbrances if e.get('status') == 'active' and e.get('type') in ['Loan', 'Mortgage']]
        if active_loans:
            for loan in active_loans:
                score -= 80
                amount_str = f"₹{loan['amount']:,}" if loan.get('amount') else 'Unknown amount'
                flags.append({
                    'category': 'encumbrance',
                    'severity': 'medium',
                    'title': f"Active {loan['type'].lower()} encumbrance",
                    'description': f"{loan['holder']} - {amount_str} outstanding",
                    'impact': 'Property cannot be transferred without clearing this encumbrance',
                    'recommended_action': f"Obtain release deed from {loan['holder']}"
                })
        
        # Check for court orders
        court_orders = [e for e in encumbrances if e.get('status') == 'active' and e.get('type') == 'Court Order']
        if court_orders:
            score -= 200
            flags.append({
                'category': 'legal',
                'severity': 'high',
                'title': 'Active court order on property',
                'description': 'Interim stay order from civil court regarding ownership dispute.',
                'impact': 'Property transfer may be blocked until court case is resolved',
                'recommended_action': 'Consult lawyer and review court case status'
            })
        
        # Check mutation status (randomly based on previous generation)
        if random.random() < 0.4:  # Increased from 0.3
            score -= 80  # Increased from 60
            flags.append({
                'category': 'documentation',
                'severity': 'medium',
                'title': 'Missing mutation record',
                'description': 'Mutation record not updated since last transfer.',
                'impact': 'Ownership status may not be current in revenue records',
                'recommended_action': 'Apply for mutation at taluk office'
            })
        
        # Agricultural land specific checks
        if property_type == 'Agricultural':
            if random.random() < 0.35:  # Increased from 0.2
                score -= 60  # Increased from 40
                flags.append({
                    'category': 'compliance',
                    'severity': 'low',
                    'title': 'Agricultural land ceiling compliance',
                    'description': 'Verify compliance with state Agricultural Land Ceiling Act.',
                    'impact': 'Non-compliance may lead to government acquisition',
                    'recommended_action': 'Obtain NOC from revenue department'
                })
        
        # Additional risk factors for variety
        if random.random() < 0.25:
            score -= 70
            flags.append({
                'category': 'documentation',
                'severity': 'medium',
                'title': 'Outdated survey records',
                'description': 'Survey records have not been updated in over 10 years.',
                'impact': 'Boundary disputes may arise due to outdated measurements',
                'recommended_action': 'Request fresh survey from revenue department'
            })
        
        if random.random() < 0.2:
            score -= 90
            flags.append({
                'category': 'legal',
                'severity': 'medium',
                'title': 'Pending tax assessment',
                'description': 'Property tax reassessment notice pending review.',
                'impact': 'May result in additional tax liability or penalties',
                'recommended_action': 'Clear pending tax assessment with municipal office'
            })
        
        if len(owners) > 3 and random.random() < 0.3:
            score -= 50
            flags.append({
                'category': 'ownership',
                'severity': 'low',
                'title': 'Complex ownership history',
                'description': f'Property has changed hands {len(owners)} times.',
                'impact': 'Higher due diligence required to verify chain',
                'recommended_action': 'Obtain certified copies of all transfer deeds'
            })
        
        # Determine risk level
        if score >= 850:
            risk_level = 'low'
        elif score >= 650:
            risk_level = 'medium'
        elif score >= 450:
            risk_level = 'high'
        else:
            risk_level = 'severe'
        
        return {
            'score': max(0, min(1000, score)),
            'level': risk_level,
            'flags': flags
        }
    
    def _generate_boundary(self) -> str:
        """Generate boundary description"""
        
        types = ['Property of', 'Land owned by', 'Survey No.', 'Road', 'Lane', 'Nala', 'Government land']
        names = ['Krishnamurthy', 'Patel', 'Sharma', 'Naidu', 'Reddy']
        
        boundary_type = random.choice(types)
        
        if boundary_type in ['Property of', 'Land owned by']:
            return f"{boundary_type} {random.choice(names)}"
        elif boundary_type == 'Survey No.':
            return f"Survey No. {random.randint(1, 500)}/{random.randint(1, 9)}"
        else:
            return f"{random.randint(10, 50)} ft {boundary_type}"
    
    def _generate_date(self, days_min: int, days_max: int) -> str:
        """Generate random date within range"""
        
        days_ago = random.randint(abs(days_min), abs(days_max))
        date = datetime.now() - timedelta(days=days_ago)
        return date.strftime('%Y-%m-%d')
    
    def get_ownership_chain(self, property_id: str) -> Dict[str, Any]:
        """Get ownership chain for property by land_id"""
        
        # Try to get record by land_id
        try:
            land_id = int(property_id)
            record = self.by_land_id.get(land_id)
        except (ValueError, TypeError):
            record = None
        
        if record:
            ownership_chain = record.get('ownership_chain', [])
            owners = []
            for i, owner in enumerate(ownership_chain):
                owners.append({
                    'owner_id': f"OWN-{land_id:08d}-{i+1:03d}",
                    'name': owner.get('owner', ''),
                    'acquisition_date': f"{owner.get('year', 2000)}-01-01",
                    'acquisition_method': owner.get('transaction_type', 'Transfer'),
                    'document_status': owner.get('document_status', 'Registered'),
                    'verified': owner.get('verified', True),
                    'is_current': i == len(ownership_chain) - 1
                })
            
            return {
                'property_id': property_id,
                'chain_length': len(owners),
                'original_owner': owners[0] if owners else None,
                'current_owner': owners[-1] if owners else None,
                'ownership_history': owners,
                'gaps_detected': record.get('lineage_analysis', {}).get('chain_issues', [])
            }
        
        return {
            'property_id': property_id,
            'error': 'Property not found',
            'ownership_history': []
        }
    
    def get_encumbrances(self, property_id: str) -> List[Dict[str, Any]]:
        """Get encumbrances for property by land_id"""
        
        try:
            land_id = int(property_id)
            record = self.by_land_id.get(land_id)
        except (ValueError, TypeError):
            record = None
        
        if record:
            enc_data = record.get('encumbrance', {})
            encumbrances = []
            if enc_data.get('type') not in ['None', None]:
                encumbrances.append({
                    'encumbrance_id': f"ENC-{land_id:08d}-001",
                    'type': enc_data.get('type', 'Loan'),
                    'holder': enc_data.get('lender', 'Bank'),
                    'amount': (enc_data.get('amount_lakhs') or 0) * 100000,
                    'currency': 'INR',
                    'status': 'active' if enc_data.get('active') else 'discharged',
                    'ec_certificate_available': enc_data.get('ec_certificate_available', True),
                    'ec_period_covered': enc_data.get('ec_period_covered', '')
                })
            return encumbrances
        
        return []
    
    def get_family_tree(self, property_id: str) -> Dict[str, Any]:
        """Generate family tree data for visualization from 1000-record dataset"""
        
        # Try to get record by land_id
        try:
            land_id = int(property_id)
            record = self.by_land_id.get(land_id)
        except (ValueError, TypeError):
            record = None
        
        if not record:
            return {'nodes': [], 'edges': [], 'root': None}
        
        nodes = []
        edges = []
        
        family_tree = record.get('family_tree', {})
        gen1 = family_tree.get('generation_1', {})
        
        # Root node (original owner)
        if gen1.get('owner'):
            root_id = f"owner-gen1-{land_id}"
            nodes.append({
                'id': root_id,
                'label': gen1.get('owner'),
                'year': str(gen1.get('acquired_year', '')),
                'method': gen1.get('acquisition_type', 'Original'),
                'is_current': False,
                'generation': 1
            })
            
            # Add spouse if exists
            if gen1.get('spouse'):
                spouse_id = f"spouse-gen1-{land_id}"
                nodes.append({
                    'id': spouse_id,
                    'label': gen1.get('spouse'),
                    'relation': 'Spouse',
                    'is_heir': False,
                    'generation': 1
                })
                edges.append({
                    'from': root_id,
                    'to': spouse_id,
                    'label': 'Married',
                    'is_marriage': True
                })
            
            # Add generation 2 (children)
            for i, child in enumerate(family_tree.get('generation_2', [])):
                if isinstance(child, dict):
                    child_id = f"heir-gen2-{land_id}-{i}"
                    nodes.append({
                        'id': child_id,
                        'label': child.get('name', ''),
                        'relation': child.get('relation', 'Child'),
                        'gender': child.get('gender', ''),
                        'is_heir': True,
                        'alive': child.get('alive', True),
                        'whereabouts': child.get('whereabouts', ''),
                        'generation': 2
                    })
                    edges.append({
                        'from': root_id,
                        'to': child_id,
                        'label': child.get('relation', 'Child'),
                        'is_inheritance': True
                    })
            
            # Add generation 3 (grandchildren)
            for i, grandchild in enumerate(family_tree.get('generation_3', [])):
                if isinstance(grandchild, dict):
                    grandchild_id = f"heir-gen3-{land_id}-{i}"
                    parent_name = grandchild.get('parent', '')
                    
                    nodes.append({
                        'id': grandchild_id,
                        'label': grandchild.get('name', ''),
                        'relation': grandchild.get('relation', 'Grandchild'),
                        'gender': grandchild.get('gender', ''),
                        'is_heir': True,
                        'alive': grandchild.get('alive', True),
                        'inheritance_share': grandchild.get('inheritance_share', ''),
                        'generation': 3
                    })
                    
                    # Find parent node
                    parent_id = None
                    for node in nodes:
                        if node.get('label') == parent_name:
                            parent_id = node['id']
                            break
                    
                    if parent_id:
                        edges.append({
                            'from': parent_id,
                            'to': grandchild_id,
                            'label': grandchild.get('relation', 'Child'),
                            'is_inheritance': True
                        })
        
        # Also add ownership chain as lineage
        ownership_chain = record.get('ownership_chain', [])
        for i, owner in enumerate(ownership_chain):
            owner_id = f"chain-{land_id}-{i}"
            nodes.append({
                'id': owner_id,
                'label': owner.get('owner', ''),
                'year': str(owner.get('year', '')),
                'method': owner.get('transaction_type', 'Transfer'),
                'document_status': owner.get('document_status', ''),
                'verified': owner.get('verified', True),
                'is_current': i == len(ownership_chain) - 1,
                'is_ownership_chain': True
            })
            
            if i > 0:
                edges.append({
                    'from': f"chain-{land_id}-{i-1}",
                    'to': owner_id,
                    'label': owner.get('transaction_type', 'Transfer'),
                    'date': str(owner.get('year', '')),
                    'is_ownership': True
                })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'root': nodes[0]['id'] if nodes else None,
            'original_owner': gen1.get('owner', ''),
            'heirs': record.get('heirs_in_line', []),
            'lineage_analysis': record.get('lineage_analysis', {}),
            'partition_status': 'Filed' if record.get('legal', {}).get('partition_record_present') else 'Not Filed'
        }


# Singleton instance
land_records_service = LandRecordsService()
