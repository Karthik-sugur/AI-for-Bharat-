"""
LandLedger API - Main Flask Application
AI for Bharat Hackathon
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from parent directory
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from services.gemini_service import GeminiService
from services.land_records_service import LandRecordsService
from services.family_tree_service import FamilyTreeService
from services.risk_analyzer import RiskAnalyzer
from utils.validators import validate_property_query, validate_land_id
from utils.formatters import (
    format_api_response,
    format_ownership_timeline,
    format_risk_summary,
    format_encumbrance_summary
)
from utils.data_parser import load_synthetic_data
import logging

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load synthetic data
try:
    synthetic_data = load_synthetic_data(app.config['DATA_PATH'])
    logger.info(f"Loaded {len(synthetic_data)} property records")
except Exception as e:
    logger.error(f"Failed to load synthetic data: {str(e)}")
    synthetic_data = []

# Initialize services
gemini_service = GeminiService(app.config.get('GEMINI_API_KEY', ''))
land_records_service = LandRecordsService(synthetic_data)
family_tree_service = FamilyTreeService(synthetic_data)
risk_analyzer = RiskAnalyzer()


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'LandLedger API',
        'version': '1.0.0'
    }), 200


@app.route('/api/search', methods=['POST'])
def search_property():
    """
    Search for properties by survey number and location details
    
    Request Body:
    {
        "survey_number": "SY/242/23",
        "village": "Indiranagar",
        "district": "Bangalore Urban",
        "state": "Karnataka"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify(format_api_response(
                success=False,
                error="Request body is required"
            )), 400
        
        survey_number = data.get('survey_number', '').strip()
        village = data.get('village', '').strip() or None
        district = data.get('district', '').strip() or None
        state = data.get('state', '').strip() or None
        
        # Validate survey_number
        if not survey_number:
            return jsonify(format_api_response(
                success=False,
                error="Survey number is required"
            )), 400
        
        # Import the search function
        from utils.data_parser import find_property_by_survey
        
        # Search for matching properties
        matches = find_property_by_survey(
            synthetic_data,
            survey_number,
            village=village,
            district=district,
            state=state
        )
        
        if not matches:
            return jsonify(format_api_response(
                success=False,
                error=f"No properties found matching survey number '{survey_number}'"
            )), 404
        
        # Format results
        properties_summary = []
        for prop in matches[:25]:  # Limit to 25 results
            properties_summary.append({
                'land_id': prop.get('land_id'),
                'survey_number': prop.get('survey_number'),
                'location': prop.get('location'),
                'current_owner': prop.get('current_owner'),
                'land_type': prop.get('land_type') or prop.get('property_type'),
                'risk_level': prop.get('risk_level', 'Unknown'),
                'size_acres': prop.get('size_acres'),
                'price_lakhs': prop.get('price_lakhs')
            })
        
        return jsonify(format_api_response(
            success=True,
            data={
                'total_matches': len(matches),
                'showing': len(properties_summary),
                'properties': properties_summary
            }
        )), 200
        
    except Exception as e:
        logger.error(f"Error in search_property: {str(e)}", exc_info=True)
        return jsonify(format_api_response(
            success=False,
            error=f"Internal server error: {str(e)}"
        )), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_property():
    """
    Analyze property with Gemini AI
    
    Request Body:
    {
        "land_id": 1,
        "query": "What are the risks associated with this property?"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify(format_api_response(
                success=False,
                error="Request body is required"
            )), 400
        
        land_id = data.get('land_id')
        user_query = data.get('query', '')
        
        # Validate land_id
        if not land_id or not validate_land_id(land_id):
            return jsonify(format_api_response(
                success=False,
                error="Valid land_id is required"
            )), 400
        
        # Search for property
        property_data, property_obj = land_records_service.search_property_by_id(land_id)
        if not property_data or not property_obj:
            return jsonify(format_api_response(
                success=False,
                error=f"Property with land_id {land_id} not found"
            )), 404
        
        # Parse ownership and encumbrances
        owners = land_records_service.get_ownership_chain(property_data)
        encumbrances = land_records_service.get_encumbrances(property_data)
        
        # Generate AI analysis
        ai_summary = gemini_service.generate_ai_summary(property_obj, owners, encumbrances)
        
        # Analyze risks
        risk_flags = risk_analyzer.detect_all_risks(property_data, owners, encumbrances)
        
        # Calculate confidence score
        confidence_score = risk_analyzer.calculate_overall_title_risk(property_data, owners, encumbrances, risk_flags)
        risk_level = risk_analyzer.determine_risk_level(confidence_score)
        
        # Generate recommendations
        recommendations = gemini_service.generate_recommendations(property_obj, owners, encumbrances, risk_flags)
        
        return jsonify(format_api_response(
            success=True,
            data={
                'property': property_obj.to_dict(),
                'owners_chain': [o.to_dict() for o in owners],
                'encumbrances': [e.to_dict() for e in encumbrances],
                'risk_flags': [r.to_dict() for r in risk_flags],
                'title_confidence_score': confidence_score,
                'risk_level': risk_level,
                'ai_summary': ai_summary,
                'recommendations': recommendations
            }
        )), 200
        
    except Exception as e:
        logger.error(f"Error in analyze_property: {str(e)}", exc_info=True)
        return jsonify(format_api_response(
            success=False,
            error=f"Internal server error: {str(e)}"
        )), 500


@app.route('/api/family-tree', methods=['POST'])
def get_family_tree():
    """
    Get ownership lineage and family tree
    
    Request Body:
    {
        "land_id": "LAND-001"
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'land_id' not in data:
            return jsonify(format_api_response(
                success=False,
                error="land_id is required"
            )), 400
        
        land_id = data.get('land_id')
        
        # Validate land_id format
        if not validate_land_id(land_id):
            return jsonify(format_api_response(
                success=False,
                error="Invalid land_id format"
            )), 400
        
        # Search for property
        property_data, property_obj = land_records_service.search_property_by_id(land_id)
        if not property_data or not property_obj:
            return jsonify(format_api_response(
                success=False,
                error=f"Property with land_id {land_id} not found"
            )), 404
        
        # Build family tree
        family_tree = family_tree_service.build_family_tree(land_id)
        
        # Get ownership chain for timeline
        owners = land_records_service.get_ownership_chain(property_data)
        ownership_timeline = format_ownership_timeline(owners)
        
        # Identify risks related to family tree
        family_risks = family_tree_service.identify_ownership_risks(family_tree)
        
        return jsonify(format_api_response(
            success=True,
            data={
                'land_id': land_id,
                'current_owner': property_obj.current_owner,
                'family_tree': family_tree,
                'ownership_timeline': ownership_timeline,
                'family_related_risks': family_risks
            }
        )), 200
        
    except Exception as e:
        logger.error(f"Error in get_family_tree: {str(e)}", exc_info=True)
        return jsonify(format_api_response(
            success=False,
            error=f"Internal server error: {str(e)}"
        )), 500


@app.route('/api/risk-assessment', methods=['POST'])
def risk_assessment():
    """
    Calculate comprehensive title risk score
    
    Request Body:
    {
        "land_id": "LAND-001"
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'land_id' not in data:
            return jsonify(format_api_response(
                success=False,
                error="land_id is required"
            )), 400
        
        land_id = data.get('land_id')
        
        # Validate land_id format
        if not validate_land_id(land_id):
            return jsonify(format_api_response(
                success=False,
                error="Invalid land_id format"
            )), 400
        
        # Search for property
        property_data, property_obj = land_records_service.search_property_by_id(land_id)
        if not property_data or not property_obj:
            return jsonify(format_api_response(
                success=False,
                error=f"Property with land_id {land_id} not found"
            )), 404
        
        # Parse ownership and encumbrances
        owners = land_records_service.get_ownership_chain(property_data)
        encumbrances = land_records_service.get_encumbrances(property_data)
        
        # Detect all risks
        risk_flags = risk_analyzer.detect_all_risks(property_data, owners, encumbrances)
        
        # Calculate overall risk score
        confidence_score = risk_analyzer.calculate_overall_title_risk(property_data, owners, encumbrances, risk_flags)
        risk_level = risk_analyzer.determine_risk_level(confidence_score)
        
        # Generate comprehensive risk report
        risk_report = risk_analyzer.generate_risk_report(property_data, owners, encumbrances, risk_flags)
        
        # Format risk summary
        risk_summary = format_risk_summary(risk_flags)
        
        return jsonify(format_api_response(
            success=True,
            data={
                'land_id': land_id,
                'property': property_obj.to_dict(),
                'title_confidence_score': confidence_score,
                'risk_level': risk_level,
                'risk_summary': risk_summary,
                'risk_flags': [r.to_dict() for r in risk_flags],
                'risk_report': risk_report
            }
        )), 200
        
    except Exception as e:
        logger.error(f"Error in risk_assessment: {str(e)}", exc_info=True)
        return jsonify(format_api_response(
            success=False,
            error=f"Internal server error: {str(e)}"
        )), 500


@app.route('/api/encumbrances', methods=['POST'])
def check_encumbrances():
    """
    Check loans/liens on property
    
    Request Body:
    {
        "land_id": 1
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'land_id' not in data:
            return jsonify(format_api_response(
                success=False,
                error="land_id is required"
            )), 400
        
        land_id = data.get('land_id')
        
        # Search for property
        property_data, property_obj = land_records_service.search_property_by_id(land_id)
        if not property_data or not property_obj:
            return jsonify(format_api_response(
                success=False,
                error=f"Property with land_id {land_id} not found"
            )), 404
        
        # Get encumbrances
        encumbrances = land_records_service.get_encumbrances(property_data)
        
        # Analyze encumbrances
        enc_analysis = risk_analyzer.analyze_encumbrances(encumbrances)
        enc_summary = format_encumbrance_summary(encumbrances)
        
        return jsonify(format_api_response(
            success=True,
            data={
                'property_id': f"{property_obj.survey_number}-{property_obj.district}",
                'total_encumbrances': enc_summary['total'],
                'active_encumbrances': enc_summary['active'],
                'encumbrances': [e.to_dict() for e in encumbrances],
                'analysis': enc_analysis,
                'summary': enc_summary
            }
        )), 200
        
    except Exception as e:
        logger.error(f"Error in check_encumbrances: {str(e)}", exc_info=True)
        return jsonify(format_api_response(
            success=False,
            error=f"Internal server error: {str(e)}"
        )), 500


@app.route('/api/properties', methods=['GET'])
def get_properties():
    """
    Get list of all available properties (for demo/testing)
    """
    try:
        # Get limited property list
        limit = request.args.get('limit', 25, type=int)
        properties = land_records_service.get_all_properties(limit=limit)
        
        # Format summary
        properties_summary = []
        for prop in properties[:limit]:
            properties_summary.append({
                'land_id': prop.get('land_id'),
                'survey_number': prop.get('survey_number'),
                'location': prop.get('location') or prop.get('district'),
                'current_owner': prop.get('current_owner'),
                'land_type': prop.get('land_type') or prop.get('property_type'),
                'risk_level': prop.get('risk_level', 'Unknown')
            })
        
        return jsonify(format_api_response(
            success=True,
            data={
                'total_properties': len(synthetic_data),
                'showing': len(properties_summary),
                'properties': properties_summary
            }
        )), 200
        
    except Exception as e:
        logger.error(f"Error in get_properties: {str(e)}", exc_info=True)
        return jsonify(format_api_response(
            success=False,
            error=f"Internal server error: {str(e)}"
        )), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify(format_api_response(
        success=False,
        error="Endpoint not found"
    )), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {str(error)}", exc_info=True)
    return jsonify(format_api_response(
        success=False,
        error="Internal server error"
    )), 500


if __name__ == '__main__':
    logger.info(f"Starting LandLedger API on {app.config.get('HOST')}:{app.config.get('PORT')}")
    logger.info(f"Loaded {len(synthetic_data)} properties from synthetic data")
    logger.info(f"Gemini API configured: {bool(app.config.get('GEMINI_API_KEY'))}")
    
    app.run(
        host=app.config.get('HOST', '0.0.0.0'),
        port=app.config.get('PORT', 5000),
        debug=app.config.get('DEBUG', True)
    )
