"""
Gemini AI Service Integration
Handles all interactions with Google's Gemini AI
"""

import google.generativeai as genai  # type: ignore
import logging
import json

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Gemini AI"""
    
    def __init__(self, api_key, model_name='gemini-pro'):
        """
        Initialize Gemini service
        
        Args:
            api_key: Google Gemini API key
            model_name: Name of the Gemini model to use
        """
        self.api_key = api_key
        self.model_name = model_name
        
        if api_key:
            genai.configure(api_key=api_key)  # type: ignore[attr-defined]
            self.model = genai.GenerativeModel(model_name)  # type: ignore[attr-defined]
            logger.info(f"Gemini AI initialized with model: {model_name}")
        else:
            logger.warning("Gemini API key not provided. AI features will be limited.")
            self.model = None
    
    def analyze_property(self, land_record, user_query=''):
        """
        Analyze property using Gemini AI
        
        Args:
            land_record: Dictionary containing land record data
            user_query: User's specific query about the property
            
        Returns:
            Dictionary containing AI analysis results
        """
        if not self.model:
            return {
                'error': 'Gemini AI not configured',
                'message': 'Please provide GEMINI_API_KEY in environment variables'
            }
        
        try:
            # Prepare context for Gemini
            prompt = self._build_analysis_prompt(land_record, user_query)
            
            # Generate analysis
            response = self.model.generate_content(prompt)
            
            return {
                'analysis': response.text,
                'confidence': 'high' if land_record.get('title_confidence_score', 0) > 850 else 'medium',
                'query': user_query
            }
            
        except Exception as e:
            logger.error(f"Error in Gemini analysis: {str(e)}")
            return {
                'error': str(e),
                'fallback_analysis': self._get_fallback_analysis(land_record)
            }
    
    def _build_analysis_prompt(self, land_record, user_query):
        """Build prompt for Gemini AI"""
        
        land_info = f"""
        You are a land title expert analyzing property records. Here's the property information:
        
        **Property Details:**
        - Land ID: {land_record.get('land_id')}
        - Location: {land_record.get('location')}
        - Type: {land_record.get('land_type')}
        - Size: {land_record.get('size_acres')} acres
        - Survey Number: {land_record.get('survey_number')}
        - Current Owner: {land_record.get('current_owner')}
        
        **Legal Status:**
        - Mutation Status: {land_record.get('legal', {}).get('mutation_status')}
        - Active Loan: {land_record.get('legal', {}).get('loan_active')}
        - Litigation: {land_record.get('legal', {}).get('litigation_status')}
        - Area Discrepancy: {land_record.get('legal', {}).get('area_recorded') != land_record.get('legal', {}).get('area_actual')}
        
        **Ownership History:**
        {json.dumps(land_record.get('ownership_history', []), indent=2)}
        
        **Risk Assessment:**
        - Risk Level: {land_record.get('risk_level')}
        - Confidence Score: {land_record.get('title_confidence_score')}/1000
        - Defects: {', '.join(land_record.get('defects', [])) if land_record.get('defects') else 'None'}
        """
        
        if user_query:
            prompt = f"{land_info}\n\n**User Question:** {user_query}\n\nProvide a detailed analysis addressing the user's question."
        else:
            prompt = f"{land_info}\n\nProvide a comprehensive analysis of this property's title, risks, and recommendations for a potential buyer."
        
        return prompt
    
    def _get_fallback_analysis(self, land_record):
        """Provide basic analysis when AI is not available"""
        
        risk_level = land_record.get('risk_level', 'Unknown')
        defects = land_record.get('defects', [])
        score = land_record.get('title_confidence_score', 0)
        
        analysis = f"Property Risk Level: {risk_level}\n"
        analysis += f"Title Confidence Score: {score}/1000\n\n"
        
        if defects:
            analysis += "Identified Issues:\n"
            for defect in defects:
                analysis += f"- {defect}\n"
        else:
            analysis += "No major defects identified.\n"
        
        if land_record.get('legal', {}).get('loan_active'):
            analysis += "\n⚠️ Active loan on property - verify clearance.\n"
        
        if land_record.get('legal', {}).get('litigation_status') != 'None':
            analysis += f"\n⚠️ Litigation Status: {land_record.get('legal', {}).get('litigation_status')}\n"
        
        return analysis
    
    def generate_ai_summary(self, property_obj, owners, encumbrances):
        """
        Generate executive summary using Gemini AI
        
        Args:
            property_obj: Property object
            owners: List of Owner objects
            encumbrances: List of Encumbrance objects
            
        Returns:
            AI-generated summary string
        """
        if not self.model:
            return self._get_fallback_summary(property_obj, owners, encumbrances)
        
        try:
            prompt = f"""
            You are a land title expert. Provide a concise 150-200 word executive summary of this property:
            
            Property: {property_obj.survey_number} in {property_obj.get_location_string()}
            Current Owner: {property_obj.current_owner}
            Property Type: {property_obj.property_type}
            
            Ownership Chain: {len(owners)} owners in history
            Active Encumbrances: {sum(1 for e in encumbrances if e.is_active())}
            
            Focus on: ownership clarity, any red flags, and overall assessment for a buyer.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating AI summary: {str(e)}")
            return self._get_fallback_summary(property_obj, owners, encumbrances)
    
    def _get_fallback_summary(self, property_obj, owners, encumbrances):
        """Generate basic summary without AI"""
        active_enc = sum(1 for e in encumbrances if e.is_active())
        
        summary = f"Property {property_obj.survey_number} in {property_obj.get_location_string()}. "
        summary += f"Current owner: {property_obj.current_owner}. "
        summary += f"Ownership history: {len(owners)} recorded owners. "
        
        if active_enc > 0:
            summary += f"⚠️ {active_enc} active encumbrance(s) present. "
        else:
            summary += "No active encumbrances. "
        
        return summary
    
    def generate_recommendations(self, property_obj, owners, encumbrances, risk_flags):
        """
        Generate AI-powered recommendations based on analysis
        
        Args:
            property_obj: Property object
            owners: List of Owner objects
            encumbrances: List of Encumbrance objects
            risk_flags: List of RiskFlag objects
            
        Returns:
            List of recommendation strings
        """
        if not self.model:
            return self._get_basic_recommendations_from_analysis(risk_flags, encumbrances)
        
        try:
            # Build context
            prompt = f"""
            Based on this property analysis, provide 3-5 specific, actionable recommendations for a buyer:
            
            Property: {property_obj.get_location_string()}
            Current Owner: {property_obj.current_owner}
            Risk Flags: {len(risk_flags)}
            Active Encumbrances: {sum(1 for e in encumbrances if e.is_active())}
            
            Risk Details:
            {chr(10).join([f"- {flag.category}: {flag.description}" for flag in risk_flags[:5]])}
            
            Provide recommendations as a numbered list. Be specific and practical.
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse recommendations from response
            recommendations = []
            for line in response.text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Clean up the line
                    clean_line = line.lstrip('0123456789.-•) ').strip()
                    if clean_line:
                        recommendations.append(clean_line)
            
            return recommendations if recommendations else [response.text]
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return self._get_basic_recommendations_from_analysis(risk_flags, encumbrances)
    
    def _get_basic_recommendations_from_analysis(self, risk_flags, encumbrances):
        """Generate basic recommendations without AI"""
        recommendations = []
        
        # Check for critical flags
        critical = [f for f in risk_flags if f.severity == 'Critical']
        if critical:
            recommendations.append("Address all critical issues before proceeding with purchase")
        
        # Check for encumbrances
        active_enc = [e for e in encumbrances if e.is_active()]
        if active_enc:
            recommendations.append("Obtain clearance certificates for all active loans and liens")
        
        # Check for missing docs
        if any(f.category == 'Missing Documents' for f in risk_flags):
            recommendations.append("Collect all missing property documents and deeds")
        
        # Check for gaps
        if any(f.category == 'Ownership Gap' for f in risk_flags):
            recommendations.append("Verify ownership continuity through legal channels")
        
        if not recommendations:
            recommendations.append("Proceed with standard due diligence")
            recommendations.append("Verify all documents with original copies")
            recommendations.append("Conduct physical site inspection")
        
        return recommendations
    
    def generate_recommendations_legacy(self, land_record):
        """Generate AI-powered recommendations for the property (legacy method)"""
        
        if not self.model:
            return self._get_basic_recommendations(land_record)
        
        try:
            prompt = f"""
            Based on this property record, provide 3-5 specific recommendations for a buyer:
            
            Risk Level: {land_record.get('risk_level')}
            Confidence Score: {land_record.get('title_confidence_score')}
            Defects: {', '.join(land_record.get('defects', []))}
            Legal Status: {json.dumps(land_record.get('legal', {}), indent=2)}
            
            Format as a numbered list.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return self._get_basic_recommendations(land_record)
    
    def _get_basic_recommendations(self, land_record):
        """Generate basic recommendations without AI (legacy method)"""
        
        recommendations = []
        
        if land_record.get('title_confidence_score', 0) < 800:
            recommendations.append("Conduct thorough title verification before purchase")
        
        if land_record.get('legal', {}).get('loan_active'):
            recommendations.append("Obtain loan clearance certificate from current owner")
        
        if land_record.get('legal', {}).get('litigation_status') != 'None':
            recommendations.append("Consult legal expert regarding ongoing litigation")
        
        if land_record.get('defects'):
            recommendations.append("Address all identified defects before finalizing transaction")
        
        if not recommendations:
            recommendations.append("Property appears to have clear title - proceed with standard due diligence")
        
        return "\n".join([f"{i+1}. {rec}" for i, rec in enumerate(recommendations)])
