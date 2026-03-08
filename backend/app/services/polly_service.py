"""
Amazon Polly Service - Text-to-Speech
Generates voice output for analysis summaries in multiple Indian languages
"""

import boto3  # type: ignore
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import base64

from app.config import settings

logger = logging.getLogger(__name__)


class PollyService:
    """Service for text-to-speech using Amazon Polly"""
    
    # Available Indian voices
    INDIAN_VOICES = {
        'english_in': {
            'female': 'Aditi',  # Indian English female
            'male': 'Raveena'   # Alternative
        },
        'english_us': {
            'female': 'Joanna',
            'male': 'Matthew'
        },
        'hindi': {
            'female': 'Aditi',  # Hindi voice
            'male': 'Aditi'     # Same voice supports Hindi
        }
    }
    
    def __init__(self):
        """Initialize Polly client"""
        self.client = boto3.client(
            'polly',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.output_format = settings.POLLY_OUTPUT_FORMAT
    
    def synthesize_speech(
        self,
        text: str,
        voice_id: str = 'Joanna',
        language_code: str = 'en-US',
        engine: str = 'neural'
    ) -> Dict[str, Any]:
        """
        Synthesize speech from text
        
        Args:
            text: Text to convert to speech
            voice_id: Polly voice ID
            language_code: Language code (en-US, hi-IN, etc.)
            engine: Engine type (neural or standard)
            
        Returns:
            Audio data and metadata
        """
        
        try:
            # Check if text exceeds Polly limits
            if len(text) > 3000:
                text = text[:3000] + "... For the complete analysis, please refer to the written report."
            
            response = self.client.synthesize_speech(
                Text=text,
                OutputFormat=self.output_format,
                VoiceId=voice_id,
                LanguageCode=language_code,
                Engine=engine
            )
            
            # Read audio stream
            audio_stream = response['AudioStream'].read()
            
            # Estimate duration (rough estimate based on word count)
            word_count = len(text.split())
            estimated_duration = word_count / 150 * 60  # ~150 words per minute
            
            return {
                'audio_id': str(uuid.uuid4()),
                'audio_data': audio_stream,
                'audio_base64': base64.b64encode(audio_stream).decode('utf-8'),
                'content_type': response['ContentType'],
                'request_characters': response['RequestCharacters'],
                'duration_seconds': round(estimated_duration, 2),
                'voice_id': voice_id,
                'language_code': language_code,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except self.client.exceptions.TextLengthExceededException:
            logger.warning("Text too long, truncating...")
            return self.synthesize_speech(text[:1500], voice_id, language_code, engine)
            
        except Exception as e:
            logger.error(f"Speech synthesis failed: {str(e)}")
            raise
    
    def generate_analysis_audio(
        self,
        analysis_result: Dict[str, Any],
        include_hindi: bool = True
    ) -> Dict[str, Any]:
        """
        Generate audio summary of property analysis
        
        Args:
            analysis_result: The property analysis result
            include_hindi: Whether to generate Hindi version
            
        Returns:
            Audio URLs/data for different languages
        """
        
        # Build English summary text
        english_text = self._build_audio_summary(analysis_result, 'english')
        
        # Generate English audio
        english_audio = self.synthesize_speech(
            text=english_text,
            voice_id='Joanna',
            language_code='en-US',
            engine='neural'
        )
        
        result = {
            'audio_id': str(uuid.uuid4()),
            'english': {
                'audio_base64': english_audio['audio_base64'],
                'duration_seconds': english_audio['duration_seconds'],
                'voice': 'Joanna'
            },
            'generated_at': datetime.utcnow().isoformat()
        }
        
        # Generate Hindi version if requested
        if include_hindi:
            try:
                hindi_text = self._build_audio_summary(analysis_result, 'hindi')
                hindi_audio = self.synthesize_speech(
                    text=hindi_text,
                    voice_id='Aditi',
                    language_code='hi-IN',
                    engine='standard'  # Neural not available for Hindi
                )
                result['hindi'] = {
                    'audio_base64': hindi_audio['audio_base64'],
                    'duration_seconds': hindi_audio['duration_seconds'],
                    'voice': 'Aditi'
                }
            except Exception as e:
                logger.warning(f"Hindi audio generation failed: {e}")
                result['hindi'] = None
        
        return result
    
    def _build_audio_summary(self, analysis: Dict[str, Any], language: str = 'english') -> str:
        """Build audio-friendly summary text"""
        
        score = analysis.get('title_confidence_score', 0)
        risk_level = analysis.get('risk_level', 'unknown')
        risk_flags = analysis.get('risk_flags', [])
        recommendations = analysis.get('recommendations', [])
        
        if language == 'hindi':
            return self._build_hindi_summary(score, risk_level, risk_flags, recommendations)
        
        # English summary
        summary_parts = [
            f"Property Analysis Summary.",
            f"Title Confidence Score: {score} out of 1000.",
            f"Overall Risk Level: {risk_level.title()}.",
        ]
        
        if risk_flags:
            summary_parts.append(f"We identified {len(risk_flags)} potential issues.")
            for i, flag in enumerate(risk_flags[:3], 1):  # Limit to top 3
                summary_parts.append(f"Issue {i}: {flag.get('title', 'Unknown issue')}.")
        
        if recommendations:
            summary_parts.append("Key Recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):  # Limit to top 3
                summary_parts.append(f"{i}. {rec}")
        
        # Risk-specific advice
        if risk_level == 'high' or risk_level == 'severe':
            summary_parts.append(
                "Important: Due to the high risk level, we strongly recommend "
                "consulting with a property lawyer before proceeding with any transaction."
            )
        elif risk_level == 'medium':
            summary_parts.append(
                "Some issues need to be resolved before this property can be safely transacted. "
                "Please follow the recommendations in the detailed report."
            )
        else:
            summary_parts.append(
                "This property shows low risk indicators. However, always conduct "
                "due diligence before any property transaction."
            )
        
        summary_parts.append("For detailed analysis, please refer to the written report.")
        
        return " ".join(summary_parts)
    
    def _build_hindi_summary(
        self,
        score: int,
        risk_level: str,
        risk_flags: list,
        recommendations: list
    ) -> str:
        """Build Hindi audio summary"""
        
        risk_level_hindi = {
            'low': 'कम जोखिम',
            'medium': 'मध्यम जोखिम',
            'high': 'उच्च जोखिम',
            'severe': 'गंभीर जोखिम'
        }.get(risk_level, 'अज्ञात')
        
        summary_parts = [
            "संपत्ति विश्लेषण सारांश।",
            f"शीर्षक विश्वास स्कोर: एक हजार में से {score}।",
            f"समग्र जोखिम स्तर: {risk_level_hindi}।",
        ]
        
        if risk_flags:
            summary_parts.append(f"हमने {len(risk_flags)} संभावित समस्याएं पहचानी हैं।")
        
        if risk_level in ['high', 'severe']:
            summary_parts.append(
                "महत्वपूर्ण: उच्च जोखिम स्तर के कारण, किसी भी लेनदेन से पहले "
                "संपत्ति वकील से परामर्श करने की दृढ़ता से अनुशंसा की जाती है।"
            )
        
        summary_parts.append("विस्तृत विश्लेषण के लिए, कृपया लिखित रिपोर्ट देखें।")
        
        return " ".join(summary_parts)
    
    def list_available_voices(self, language_code: Optional[str] = None) -> list:
        """List available Polly voices"""
        
        try:
            params = {}
            if language_code:
                params['LanguageCode'] = language_code
            
            response = self.client.describe_voices(**params)
            
            return [
                {
                    'id': voice['Id'],
                    'name': voice['Name'],
                    'language': voice['LanguageCode'],
                    'gender': voice['Gender'],
                    'engine': voice.get('SupportedEngines', [])
                }
                for voice in response.get('Voices', [])
            ]
            
        except Exception as e:
            logger.error(f"Failed to list voices: {e}")
            return []


# Singleton instance
polly_service = PollyService()
