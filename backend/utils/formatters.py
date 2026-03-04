"""
Response Formatters
Format responses for API and frontend
"""

from datetime import datetime
from typing import Dict, List, Any, Optional


def format_api_response(success: bool, data: Optional[Dict] = None, error: Optional[str] = None) -> Dict:
    """
    Create standardized API response
    
    Args:
        success: Whether the operation was successful
        data: Response data (optional)
        error: Error message (optional)
        
    Returns:
        Standardized API response dictionary
    """
    response = {
        'success': success,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    if data is not None:
        response['data'] = data
    
    if error is not None:
        response['error'] = error
    
    return response


def format_confidence_score(score: float) -> Dict:
    """
    Return score with interpretation
    
    Args:
        score: Confidence score (0-1000)
        
    Returns:
        Dictionary with score, percentage, and level
    """
    percentage = (score / 1000) * 100
    
    if score >= 900:
        level = 'Safe'
    elif score >= 850:
        level = 'Caution'
    elif score >= 700:
        level = 'High Risk'
    else:
        level = 'Critical'
    
    return {
        'score': score,
        'max': 1000,
        'percentage': round(percentage, 1),
        'level': level
    }


def format_date(date_str: str) -> str:
    """
    Convert date string to readable format
    
    Args:
        date_str: Date in YYYY-MM-DD format
        
    Returns:
        Formatted date string (e.g., "15 January 2023")
    """
    if not date_str:
        return "N/A"
    
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%d %B %Y")
    except (ValueError, TypeError):
        return date_str


def format_currency(amount: float) -> str:
    """
    Format amount as Indian currency
    
    Args:
        amount: Amount in rupees
        
    Returns:
        Formatted currency string (e.g., "₹10,00,000")
    """
    if amount is None:
        return "₹0"
    
    try:
        # Convert to Indian numbering system (lakhs, crores)
        amount_str = f"{int(amount):,}"
        
        # Indian style: place commas at thousands and then at hundreds
        # For simplicity, using standard formatting here
        return f"₹{amount_str}"
    except (ValueError, TypeError):
        return f"₹{amount}"


def format_ownership_timeline(owners: List[Any]) -> List[Dict]:
    """
    Create timeline-friendly format for frontend
    
    Args:
        owners: List of Owner objects
        
    Returns:
        List of formatted dictionaries for timeline display
    """
    timeline = []
    
    for owner in owners:
        # Handle both Owner objects and dictionaries
        if hasattr(owner, 'to_dict'):
            owner_dict = owner.to_dict()
        else:
            owner_dict = owner
        
        tenure = None
        if hasattr(owner, 'get_tenure_years'):
            tenure = owner.get_tenure_years()
        
        timeline_entry = {
            'name': owner_dict.get('name'),
            'acquisition_date': format_date(owner_dict.get('acquisition_date')),
            'disposal_date': format_date(owner_dict.get('disposal_date')) if owner_dict.get('disposal_date') else 'Current',
            'acquisition_method': owner_dict.get('acquisition_method'),
            'relationship': owner_dict.get('relationship_to_current'),
            'document_reference': owner_dict.get('document_reference'),
            'is_current_owner': owner_dict.get('is_current_owner', False)
        }
        
        if tenure:
            timeline_entry['tenure'] = tenure
        
        timeline.append(timeline_entry)
    
    return timeline


def format_analysis_result(result: Any) -> Dict:
    """
    Convert AnalysisResult to API response format
    
    Args:
        result: AnalysisResult object or dictionary
        
    Returns:
        Formatted dictionary for API response
    """
    # Handle both objects and dictionaries
    if hasattr(result, 'to_dict'):
        return result.to_dict()
    
    return result


def format_risk_summary(risk_flags: List[Any]) -> Dict:
    """
    Create summary of risk flags by severity
    
    Args:
        risk_flags: List of RiskFlag objects
        
    Returns:
        Summary dictionary
    """
    summary = {
        'total_flags': len(risk_flags),
        'by_severity': {
            'Critical': 0,
            'High': 0,
            'Medium': 0,
            'Low': 0
        },
        'by_category': {}
    }
    
    for flag in risk_flags:
        flag_dict = flag.to_dict() if hasattr(flag, 'to_dict') else flag
        
        severity = flag_dict.get('severity', 'Medium')
        if severity in summary['by_severity']:
            summary['by_severity'][severity] += 1
        
        category = flag_dict.get('category', 'Unknown')
        summary['by_category'][category] = summary['by_category'].get(category, 0) + 1
    
    return summary


def format_encumbrance_summary(encumbrances: List[Any]) -> Dict:
    """
    Create summary of encumbrances
    
    Args:
        encumbrances: List of Encumbrance objects
        
    Returns:
        Summary dictionary
    """
    total = len(encumbrances)
    active = 0
    critical = 0
    total_amount = 0
    
    for enc in encumbrances:
        enc_dict = enc.to_dict() if hasattr(enc, 'to_dict') else enc
        
        if hasattr(enc, 'is_active'):
            if enc.is_active():
                active += 1
        elif enc_dict.get('status', '').lower() in ['active', 'pending', 'disputed']:
            active += 1
        
        if enc_dict.get('risk_level') == 'Critical':
            critical += 1
        
        if enc_dict.get('amount'):
            total_amount += enc_dict.get('amount', 0)
    
    return {
        'total': total,
        'active': active,
        'critical': critical,
        'total_amount': format_currency(total_amount)
    }
