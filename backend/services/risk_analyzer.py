"""
Risk Analyzer Service - Comprehensive Implementation
Calculate title risk scores and identify potential issues
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

from models.owner import Owner
from models.encumbrance import Encumbrance
from models.risk_flag import RiskFlag

logger = logging.getLogger(__name__)


class RiskAnalyzer:
    """Service for analyzing title risks"""
    
    # Risk score thresholds (inverted - higher is better)
    SAFE_THRESHOLD = 900
    CAUTION_THRESHOLD = 850
    HIGH_RISK_THRESHOLD = 700
    
    def __init__(self):
        """Initialize risk analyzer"""
        pass
    
    def analyze_encumbrances(self, encumbrances: List[Encumbrance]) -> Dict:
        """
        Analyze all encumbrances
        
        Args:
            encumbrances: List of Encumbrance objects
            
        Returns:
            Dictionary with total, active, critical counts and risk score
        """
        total = len(encumbrances)
        active = sum(1 for e in encumbrances if e.is_active())
        critical = sum(1 for e in encumbrances if e.risk_level == 'Critical')
        
        risk_score = self.calculate_encumbrance_risk_score(encumbrances)
        
        return {
            'total': total,
            'active': active,
            'critical': critical,
            'risk_score': risk_score
        }
    
    def calculate_encumbrance_risk_score(self, encumbrances: List[Encumbrance]) -> float:
        """
        Calculate overall risk from encumbrances (0-100, higher is worse)
        
        Args:
            encumbrances: List of Encumbrance objects
            
        Returns:
            Numeric risk score
        """
        if not encumbrances:
            return 0
        
        total_risk = 0
        for enc in encumbrances:
            total_risk += enc.get_risk_score()
        
        # Average and normalize
        avg_risk = total_risk / len(encumbrances)
        
        # Add penalty for multiple encumbrances
        if len(encumbrances) > 2:
            avg_risk = min(100, avg_risk + (len(encumbrances) - 2) * 5)
        
        return round(avg_risk, 2)
    
    def detect_ownership_gaps(self, owners: List[Owner]) -> List[Dict]:
        """
        Find periods without clear ownership record
        
        Args:
            owners: List of Owner objects
            
        Returns:
            List of gaps with start_date, end_date, duration, severity
        """
        gaps = []
        
        if len(owners) < 2:
            return gaps
        
        # Sort by acquisition date
        sorted_owners = sorted(owners, key=lambda x: x.acquisition_date)
        
        for i in range(len(sorted_owners) - 1):
            current = sorted_owners[i]
            next_owner = sorted_owners[i + 1]
            
            # If current owner has disposal date
            if current.disposal_date:
                try:
                    disposal = datetime.strptime(current.disposal_date, "%Y-%m-%d")
                    acquisition = datetime.strptime(next_owner.acquisition_date, "%Y-%m-%d")
                    
                    gap_days = (acquisition - disposal).days
                    
                    if gap_days > 0:
                        severity = 'Low' if gap_days < 365 else ('Medium' if gap_days < 1825 else 'High')
                        
                        gaps.append({
                            'start_date': current.disposal_date,
                            'end_date': next_owner.acquisition_date,
                            'duration_days': gap_days,
                            'duration_years': round(gap_days / 365, 1),
                            'severity': severity,
                            'between': f"{current.name} and {next_owner.name}"
                        })
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing dates for gap detection: {str(e)}")
        
        return gaps
    
    def calculate_gap_risk_score(self, gaps: List[Dict]) -> float:
        """
        Calculate risk from ownership gaps (0-100, higher is worse)
        
        Args:
            gaps: List of gap dictionaries
            
        Returns:
            Numeric risk score
        """
        if not gaps:
            return 0
        
        total_risk = 0
        
        for gap in gaps:
            duration_years = gap.get('duration_years', 0)
            
            # Base risk on duration
            if duration_years < 1:
                risk = 10
            elif duration_years < 3:
                risk = 25
            elif duration_years < 5:
                risk = 50
            else:
                risk = 75
            
            total_risk += risk
        
        # Average and cap at 100
        avg_risk = total_risk / len(gaps)
        return min(100, round(avg_risk, 2))
    
    def identify_missing_documents(self, owners: List[Owner]) -> List[Dict]:
        """
        Check each owner has document_reference
        
        Args:
            owners: List of Owner objects
            
        Returns:
            List of owners with missing documents
        """
        missing = []
        
        for owner in owners:
            if not owner.document_reference:
                missing.append({
                    'owner_name': owner.name,
                    'acquisition_date': owner.acquisition_date,
                    'acquisition_method': owner.acquisition_method,
                    'missing_doc_type': 'Deed/Document Reference'
                })
        
        return missing
    
    def calculate_documentation_risk_score(self, owners: List[Owner]) -> float:
        """
        Calculate risk from missing documents (0-100, higher is worse)
        
        Args:
            owners: List of Owner objects
            
        Returns:
            Numeric risk score
        """
        if not owners:
            return 0
        
        missing = self.identify_missing_documents(owners)
        
        if not missing:
            return 0
        
        # Risk scales with percentage of missing docs
        missing_pct = (len(missing) / len(owners)) * 100
        
        return min(100, round(missing_pct, 2))
    
    def detect_all_risks(
        self,
        property_data: Dict,
        owners: List[Owner],
        encumbrances: List[Encumbrance]
    ) -> List[RiskFlag]:
        """
        Detect all types of risks for a property
        
        Args:
            property_data: Raw property data
            owners: List of Owner objects
            encumbrances: List of Encumbrance objects
            
        Returns:
            List of RiskFlag objects
        """
        risk_flags = []
        flag_id = 1
        
        # Check for ownership gaps
        gaps = self.detect_ownership_gaps(owners)
        for gap in gaps:
            risk_flags.append(RiskFlag(
                flag_id=f"flag_{flag_id}",
                category="Ownership Gap",
                severity=gap['severity'],
                description=f"Ownership gap of {gap['duration_years']} years between {gap['between']}",
                affected_period=f"{gap['start_date']} to {gap['end_date']}",
                recommendation="Verify ownership continuity with legal documents"
            ))
            flag_id += 1
        
        # Check for missing documents
        missing_docs = self.identify_missing_documents(owners)
        if missing_docs:
            risk_flags.append(RiskFlag(
                flag_id=f"flag_{flag_id}",
                category="Missing Documents",
                severity='Medium' if len(missing_docs) < 3 else 'High',
                description=f"{len(missing_docs)} owners without document references",
                recommendation="Obtain copies of all transfer deeds and documents"
            ))
            flag_id += 1
        
        # Check for active encumbrances
        active_enc = [e for e in encumbrances if e.is_active()]
        if active_enc:
            for enc in active_enc:
                risk_flags.append(RiskFlag(
                    flag_id=f"flag_{flag_id}",
                    category="Active Encumbrance",
                    severity=enc.risk_level,
                    description=f"{enc.type} with {enc.creditor_name}",
                    recommendation=f"Obtain clearance certificate or NOC from {enc.creditor_name}"
                ))
                flag_id += 1
        
        # Check property defects
        defects = property_data.get('defects', [])
        if defects:
            for defect in defects:
                risk_flags.append(RiskFlag(
                    flag_id=f"flag_{flag_id}",
                    category="Title Defect",
                    severity='High',
                    description=defect,
                    recommendation="Consult legal expert to resolve title defect"
                ))
                flag_id += 1
        
        # Check disputes
        disputes = property_data.get('disputes', [])
        if disputes:
            risk_flags.append(RiskFlag(
                flag_id=f"flag_{flag_id}",
                category="Legal Dispute",
                severity='Critical',
                description=f"{len(disputes)} active disputes on property",
                recommendation="Resolve all legal disputes before transaction"
            ))
            flag_id += 1
        
        return risk_flags
    
    def calculate_overall_title_risk(
        self,
        property_data: Dict,
        owners: List[Owner],
        encumbrances: List[Encumbrance],
        risk_flags: List[RiskFlag]
    ) -> float:
        """
        Calculate overall title confidence score (0-1000, higher is better)
        Varies based on property data, encumbrances, defects, and disputes
        
        Args:
            property_data: Raw property data
            owners: List of Owner objects
            encumbrances: List of Encumbrance objects
            risk_flags: List of RiskFlag objects
            
        Returns:
            Overall confidence score
        """
        # Start with perfect score
        base_score = 1000
        
        # Deduct based on property risk level from data
        property_risk_level = property_data.get('risk_level', 'Unknown')
        if property_risk_level == 'High':
            base_score -= 250
        elif property_risk_level == 'Medium':
            base_score -= 120
        elif property_risk_level == 'Low':
            base_score -= 30
        
        # Deduct for defects (weighted by count)
        defects = property_data.get('defects', [])
        if defects:
            num_defects = len(defects)
            base_score -= min(150, num_defects * 25)
        
        # Deduct for disputes (critical)
        disputes = property_data.get('disputes', [])
        if disputes:
            num_disputes = len(disputes)
            base_score -= min(300, num_disputes * 150)
        
        # Deduct for encumbrances (40% weight of remaining)
        enc_risk = self.calculate_encumbrance_risk_score(encumbrances)
        base_score -= (enc_risk * 0.4)
        
        # Deduct for ownership gaps (35% weight)
        gaps = self.detect_ownership_gaps(owners)
        gap_risk = self.calculate_gap_risk_score(gaps)
        base_score -= (gap_risk * 0.35)
        
        # Deduct for missing documentation (15% weight)
        doc_risk = self.calculate_documentation_risk_score(owners)
        base_score -= (doc_risk * 0.15)
        
        # Deduct for risk flags
        for flag in risk_flags:
            if flag.severity == 'Critical':
                base_score -= 100
            elif flag.severity == 'High':
                base_score -= 50
            elif flag.severity == 'Medium':
                base_score -= 25
            else:
                base_score -= 10
        
        # Ensure within bounds
        final_score = max(0, min(1000, base_score))
        
        return round(final_score, 0)
    
    def determine_risk_level(self, score: float) -> str:
        """
        Convert numeric score to risk level
        
        Args:
            score: Confidence score (0-1000)
            
        Returns:
            Risk level string
        """
        if score >= self.SAFE_THRESHOLD:
            return 'Safe'
        elif score >= self.CAUTION_THRESHOLD:
            return 'Caution'
        elif score >= self.HIGH_RISK_THRESHOLD:
            return 'High Risk'
        else:
            return 'Critical'
    
    def generate_risk_report(
        self,
        property_data: Dict,
        owners: List[Owner],
        encumbrances: List[Encumbrance],
        risk_flags: List[RiskFlag]
    ) -> Dict:
        """
        Create comprehensive risk report
        
        Args:
            property_data: Raw property data
            owners: List of Owner objects
            encumbrances: List of Encumbrance objects
            risk_flags: List of RiskFlag objects
            
        Returns:
            Formatted report dictionary
        """
        score = self.calculate_overall_title_risk(property_data, owners, encumbrances, risk_flags)
        risk_level = self.determine_risk_level(score)
        
        # Calculate individual risk components
        enc_analysis = self.analyze_encumbrances(encumbrances)
        gaps = self.detect_ownership_gaps(owners)
        missing_docs = self.identify_missing_documents(owners)
        
        report = {
            'overall_score': score,
            'risk_level': risk_level,
            'risk_breakdown': {
                'encumbrance_risk': enc_analysis['risk_score'],
                'gap_risk': self.calculate_gap_risk_score(gaps),
                'documentation_risk': self.calculate_documentation_risk_score(owners),
                'total_flags': len(risk_flags)
            },
            'encumbrances_summary': enc_analysis,
            'ownership_gaps': gaps,
            'missing_documents': missing_docs,
            'risk_flags': [flag.to_dict() for flag in risk_flags],
            'recommendations': self._generate_report_recommendations(risk_level, risk_flags)
        }
        
        return report
    
    def _generate_report_recommendations(self, risk_level: str, risk_flags: List[RiskFlag]) -> List[str]:
        """Generate recommendations based on risk level"""
        recommendations = []
        
        if risk_level == 'Critical':
            recommendations.append("⚠️ CRITICAL: Do not proceed with transaction until all critical issues are resolved")
            recommendations.append("Engage experienced property lawyer immediately")
        
        if risk_level in ['Critical', 'High Risk']:
            recommendations.append("Conduct thorough title search and verification")
            recommendations.append("Obtain title insurance if proceeding")
        
        if any(f.category == 'Legal Dispute' for f in risk_flags):
            recommendations.append("Resolve all legal disputes before purchase")
        
        if any(f.category == 'Active Encumbrance' for f in risk_flags):
            recommendations.append("Obtain clearance certificates for all active encumbrances")
        
        if not recommendations:
            recommendations.append("Property appears to have clear title")
            recommendations.append("Proceed with standard due diligence")
        
        return recommendations
