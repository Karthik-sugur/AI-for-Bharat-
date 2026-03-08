"""
Amazon Bedrock Service - AI Analysis Engine
Uses Claude model for legal analysis and risk assessment
"""

import boto3  # type: ignore
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)


class BedrockService:
    """Service for AI-powered analysis using Amazon Bedrock"""
    
    def __init__(self):
        """Initialize Bedrock client"""
        self.client = boto3.client(
            'bedrock-runtime',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.model_id = settings.BEDROCK_MODEL_ID
        self.max_tokens = settings.BEDROCK_MAX_TOKENS
    
    def analyze_property(
        self,
        property_data: Dict[str, Any],
        owners_data: list,
        encumbrances_data: list
    ) -> Dict[str, Any]:
        """
        Perform comprehensive AI analysis of property data
        
        Args:
            property_data: Property information
            owners_data: List of ownership records
            encumbrances_data: List of encumbrances/liens
            
        Returns:
            AI analysis result with risk assessment
        """
        
        prompt = self._build_analysis_prompt(property_data, owners_data, encumbrances_data)
        
        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": self.max_tokens,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,
                    "top_p": 0.9
                })
            )
            
            result = json.loads(response['body'].read())
            analysis_text = result['content'][0]['text']
            
            # Parse structured response
            return self._parse_analysis_response(analysis_text)
            
        except Exception as e:
            logger.error(f"Bedrock analysis failed: {str(e)}")
            # Return fallback analysis
            return self._generate_fallback_analysis(property_data, owners_data, encumbrances_data)
    
    def _build_analysis_prompt(
        self,
        property_data: Dict[str, Any],
        owners_data: list,
        encumbrances_data: list
    ) -> str:
        """Build comprehensive analysis prompt"""
        
        return f"""You are an expert legal analyst specializing in Indian land law and property title verification. You have deep knowledge of:
- Indian property law (Transfer of Property Act, 1882)
- State-specific land revenue codes (Karnataka, Maharashtra, Tamil Nadu, etc.)
- Mutation and registration procedures
- Encumbrance analysis
- Family succession and inheritance laws (Hindu Succession Act, Indian Succession Act)
- Agricultural land ceiling laws

Analyze the following property and ownership data:

## PROPERTY DETAILS
{json.dumps(property_data, indent=2)}

## OWNERSHIP CHAIN
{json.dumps(owners_data, indent=2)}

## ENCUMBRANCES AND LIENS
{json.dumps(encumbrances_data, indent=2)}

## REQUIRED ANALYSIS

Provide a comprehensive analysis in the following JSON format:

{{
    "title_confidence_score": <integer 0-1000, where 1000 is perfect title>,
    "risk_level": "<low|medium|high|severe>",
    "executive_summary": "<2-3 sentence overview>",
    "ownership_analysis": {{
        "chain_validity": "<valid|gaps_found|disputed>",
        "total_transfers": <number>,
        "suspicious_transfers": [<list any suspicious transfers>],
        "inheritance_issues": [<list any inheritance issues>],
        "mutation_status": "<current|outdated|missing>"
    }},
    "risk_flags": [
        {{
            "category": "<ownership|encumbrance|documentation|legal|compliance>",
            "severity": "<low|medium|high>",
            "title": "<short title>",
            "description": "<detailed description>",
            "impact": "<potential impact on buyer/owner>",
            "recommended_action": "<specific action to resolve>"
        }}
    ],
    "encumbrance_analysis": {{
        "total_encumbrances": <number>,
        "active_loans": <number>,
        "total_outstanding": <amount in INR or null>,
        "blocking_issues": [<list issues that block transfer>]
    }},
    "legal_compliance": {{
        "registration_valid": <true|false>,
        "stamp_duty_paid": <true|false|unknown>,
        "agricultural_ceiling_check": "<applicable|not_applicable|violation_found>",
        "fema_compliance": "<applicable|not_applicable|check_required>"
    }},
    "recommendations": [
        "<actionable recommendation 1>",
        "<actionable recommendation 2>",
        ...
    ],
    "ai_summary": "<detailed 3-4 paragraph legal analysis explaining the overall situation, key risks, and path forward>"
}}

Be thorough but practical. Focus on issues that would actually impact a property transaction in India.
Respond ONLY with valid JSON, no additional text."""

    def _parse_analysis_response(self, analysis_text: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        
        try:
            # Clean up the response
            cleaned = analysis_text.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.startswith('```'):
                cleaned = cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            
            return json.loads(cleaned.strip())
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse AI response as JSON: {e}")
            # Try to extract key information
            return self._extract_fallback_data(analysis_text)
    
    def _extract_fallback_data(self, text: str) -> Dict[str, Any]:
        """Extract data from non-JSON response"""
        
        return {
            "title_confidence_score": 650,
            "risk_level": "medium",
            "executive_summary": "Analysis completed with partial data extraction.",
            "ownership_analysis": {
                "chain_validity": "requires_verification",
                "total_transfers": 0,
                "suspicious_transfers": [],
                "inheritance_issues": [],
                "mutation_status": "unknown"
            },
            "risk_flags": [],
            "encumbrance_analysis": {
                "total_encumbrances": 0,
                "active_loans": 0,
                "total_outstanding": None,
                "blocking_issues": []
            },
            "legal_compliance": {
                "registration_valid": True,
                "stamp_duty_paid": "unknown",
                "agricultural_ceiling_check": "not_applicable",
                "fema_compliance": "not_applicable"
            },
            "recommendations": [
                "Verify ownership chain with local sub-registrar",
                "Obtain latest encumbrance certificate",
                "Cross-verify with revenue department records"
            ],
            "ai_summary": text[:1000] if len(text) > 1000 else text
        }
    
    def _generate_fallback_analysis(
        self,
        property_data: Dict[str, Any],
        owners_data: list,
        encumbrances_data: list
    ) -> Dict[str, Any]:
        """Generate rule-based fallback analysis when AI is unavailable"""
        
        # Calculate basic risk score
        risk_score = 800  # Start with good score
        risk_flags = []
        
        # Check ownership chain
        if len(owners_data) == 0:
            risk_score -= 200
            risk_flags.append({
                "category": "ownership",
                "severity": "high",
                "title": "No ownership records found",
                "description": "Unable to locate ownership chain for this property.",
                "impact": "Cannot verify legal ownership",
                "recommended_action": "Obtain certified copies from sub-registrar office"
            })
        
        # Check encumbrances
        active_encumbrances = [e for e in encumbrances_data if e.get('status') == 'active']
        if len(active_encumbrances) > 0:
            risk_score -= 50 * len(active_encumbrances)
            for enc in active_encumbrances:
                risk_flags.append({
                    "category": "encumbrance",
                    "severity": "medium",
                    "title": f"Active {enc.get('type', 'encumbrance')}",
                    "description": f"{enc.get('holder', 'Unknown holder')} - {enc.get('description', '')}",
                    "impact": "Must be cleared before transfer",
                    "recommended_action": f"Obtain release deed from {enc.get('holder', 'the holder')}"
                })
        
        # Determine risk level
        if risk_score >= 700:
            risk_level = "low"
        elif risk_score >= 400:
            risk_level = "medium"
        elif risk_score >= 200:
            risk_level = "high"
        else:
            risk_level = "severe"
        
        return {
            "title_confidence_score": max(0, min(1000, risk_score)),
            "risk_level": risk_level,
            "executive_summary": f"Fallback analysis generated. {len(risk_flags)} potential issues identified.",
            "ownership_analysis": {
                "chain_validity": "requires_verification",
                "total_transfers": len(owners_data),
                "suspicious_transfers": [],
                "inheritance_issues": [],
                "mutation_status": "requires_verification"
            },
            "risk_flags": risk_flags,
            "encumbrance_analysis": {
                "total_encumbrances": len(encumbrances_data),
                "active_loans": len(active_encumbrances),
                "total_outstanding": None,
                "blocking_issues": []
            },
            "legal_compliance": {
                "registration_valid": True,
                "stamp_duty_paid": "unknown",
                "agricultural_ceiling_check": "not_applicable",
                "fema_compliance": "not_applicable"
            },
            "recommendations": [
                "Verify current ownership status at sub-registrar office",
                "Obtain latest encumbrance certificate (EC)",
                "Check for pending mutations in revenue records",
                "Verify property boundaries with licensed surveyor"
            ],
            "ai_summary": "This analysis was generated using rule-based fallback logic. For comprehensive AI-powered analysis, please ensure AWS Bedrock is properly configured."
        }
    
    def generate_legal_explanation(self, risk_flag: Dict[str, Any]) -> str:
        """Generate detailed legal explanation for a risk flag"""
        
        prompt = f"""You are an expert in Indian property law. Explain this legal risk in simple terms that a property buyer can understand:

Risk: {risk_flag.get('title', 'Unknown Risk')}
Category: {risk_flag.get('category', 'Unknown')}
Severity: {risk_flag.get('severity', 'Unknown')}
Description: {risk_flag.get('description', 'No description')}

Provide:
1. What this means in plain language
2. Why it's a problem for property buyers
3. Step-by-step actions to resolve it
4. Estimated time and cost to resolve (if applicable)

Keep the explanation under 250 words and use simple language."""

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 500,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.4
                })
            )
            
            result = json.loads(response['body'].read())
            return result['content'][0]['text']
            
        except Exception as e:
            logger.error(f"Failed to generate explanation: {e}")
            return f"This risk requires attention before proceeding with any property transaction. Please consult a legal professional for detailed guidance."
    
    def translate_to_language(self, text: str, target_language: str = "Hindi") -> str:
        """Translate text to target language using AI"""
        
        prompt = f"""Translate the following English text to {target_language}. 
Provide only the translation, no other text.

Text to translate:
{text}"""

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType='application/json',
                accept='application/json',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2
                })
            )
            
            result = json.loads(response['body'].read())
            return result['content'][0]['text']
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text  # Return original text if translation fails


# Singleton instance
bedrock_service = BedrockService()
