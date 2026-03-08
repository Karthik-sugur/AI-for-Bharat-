"""
Amazon Textract Service - Document OCR
Extracts text and structured data from scanned land documents
"""

import boto3  # type: ignore
import json
import logging
from typing import Dict, Any, List, Optional, BinaryIO
from datetime import datetime
import uuid

from app.config import settings

logger = logging.getLogger(__name__)


class TextractService:
    """Service for document OCR using Amazon Textract"""
    
    def __init__(self):
        """Initialize Textract client"""
        self.client = boto3.client(
            'textract',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
    
    def extract_text_from_bytes(self, document_bytes: bytes) -> Dict[str, Any]:
        """
        Extract text from document bytes
        
        Args:
            document_bytes: Document content as bytes (PDF or image)
            
        Returns:
            Extracted text and metadata
        """
        
        try:
            response = self.client.detect_document_text(
                Document={'Bytes': document_bytes}
            )
            
            return self._process_text_response(response)
            
        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            raise
    
    def extract_text_from_s3(self, bucket: str, key: str) -> Dict[str, Any]:
        """
        Extract text from document stored in S3
        
        Args:
            bucket: S3 bucket name
            key: S3 object key
            
        Returns:
            Extracted text and metadata
        """
        
        try:
            response = self.client.detect_document_text(
                Document={
                    'S3Object': {
                        'Bucket': bucket,
                        'Name': key
                    }
                }
            )
            
            return self._process_text_response(response)
            
        except Exception as e:
            logger.error(f"S3 text extraction failed: {str(e)}")
            raise
    
    def analyze_document(self, document_bytes: bytes) -> Dict[str, Any]:
        """
        Analyze document for forms and tables
        
        Args:
            document_bytes: Document content as bytes
            
        Returns:
            Structured data including forms and tables
        """
        
        try:
            response = self.client.analyze_document(
                Document={'Bytes': document_bytes},
                FeatureTypes=['FORMS', 'TABLES']
            )
            
            return self._process_analysis_response(response)
            
        except Exception as e:
            logger.error(f"Document analysis failed: {str(e)}")
            raise
    
    def extract_land_document_data(self, document_bytes: bytes, document_type: str) -> Dict[str, Any]:
        """
        Extract structured data from land-related documents
        
        Args:
            document_bytes: Document content
            document_type: Type of document (sale_deed, mutation, encumbrance_cert, etc.)
            
        Returns:
            Structured land document data
        """
        
        # First, extract basic text
        text_result = self.extract_text_from_bytes(document_bytes)
        
        # Then analyze for forms
        try:
            analysis_result = self.analyze_document(document_bytes)
        except Exception:
            analysis_result = {"forms": {}, "tables": []}
        
        # Extract document-specific fields
        extracted_fields = self._extract_land_fields(
            text_result['extracted_text'],
            document_type,
            analysis_result.get('forms', {})
        )
        
        return {
            "extraction_id": str(uuid.uuid4()),
            "document_type": document_type,
            "extracted_text": text_result['extracted_text'],
            "confidence_score": text_result['average_confidence'],
            "structured_data": extracted_fields,
            "form_data": analysis_result.get('forms', {}),
            "tables": analysis_result.get('tables', []),
            "line_count": text_result['line_count'],
            "word_count": text_result['word_count'],
            "processed_at": datetime.utcnow().isoformat()
        }
    
    def _process_text_response(self, response: Dict) -> Dict[str, Any]:
        """Process Textract text detection response"""
        
        lines = []
        words = []
        total_confidence = 0
        confidence_count = 0
        
        for block in response.get('Blocks', []):
            if block['BlockType'] == 'LINE':
                lines.append({
                    'text': block['Text'],
                    'confidence': block['Confidence'],
                    'geometry': block.get('Geometry', {})
                })
                total_confidence += block['Confidence']
                confidence_count += 1
                
            elif block['BlockType'] == 'WORD':
                words.append({
                    'text': block['Text'],
                    'confidence': block['Confidence']
                })
        
        extracted_text = '\n'.join([line['text'] for line in lines])
        avg_confidence = total_confidence / confidence_count if confidence_count > 0 else 0
        
        return {
            'extracted_text': extracted_text,
            'lines': lines,
            'words': words,
            'line_count': len(lines),
            'word_count': len(words),
            'average_confidence': round(avg_confidence, 2)
        }
    
    def _process_analysis_response(self, response: Dict) -> Dict[str, Any]:
        """Process Textract document analysis response"""
        
        forms = {}
        tables = []
        
        # Build block ID map
        block_map = {block['Id']: block for block in response.get('Blocks', [])}
        
        # Extract key-value pairs (forms)
        for block in response.get('Blocks', []):
            if block['BlockType'] == 'KEY_VALUE_SET':
                if 'KEY' in block.get('EntityTypes', []):
                    key_text = self._get_text_from_relationships(block, block_map)
                    
                    # Find associated value
                    for relationship in block.get('Relationships', []):
                        if relationship['Type'] == 'VALUE':
                            for value_id in relationship['Ids']:
                                value_block = block_map.get(value_id, {})
                                value_text = self._get_text_from_relationships(value_block, block_map)
                                if key_text:
                                    forms[key_text] = value_text
        
        # Extract tables
        for block in response.get('Blocks', []):
            if block['BlockType'] == 'TABLE':
                table = self._extract_table(block, block_map)
                tables.append(table)
        
        return {
            'forms': forms,
            'tables': tables
        }
    
    def _get_text_from_relationships(self, block: Dict, block_map: Dict) -> str:
        """Extract text from block relationships"""
        
        text_parts = []
        
        for relationship in block.get('Relationships', []):
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    child_block = block_map.get(child_id, {})
                    if child_block.get('BlockType') == 'WORD':
                        text_parts.append(child_block.get('Text', ''))
        
        return ' '.join(text_parts)
    
    def _extract_table(self, table_block: Dict, block_map: Dict) -> Dict[str, Any]:
        """Extract table data from table block"""
        
        rows = []
        
        for relationship in table_block.get('Relationships', []):
            if relationship['Type'] == 'CHILD':
                for cell_id in relationship['Ids']:
                    cell_block = block_map.get(cell_id, {})
                    if cell_block.get('BlockType') == 'CELL':
                        row_index = cell_block.get('RowIndex', 0) - 1
                        col_index = cell_block.get('ColumnIndex', 0) - 1
                        
                        # Ensure row exists
                        while len(rows) <= row_index:
                            rows.append([])
                        
                        # Ensure cells exist
                        while len(rows[row_index]) <= col_index:
                            rows[row_index].append('')
                        
                        cell_text = self._get_text_from_relationships(cell_block, block_map)
                        rows[row_index][col_index] = cell_text
        
        return {
            'rows': len(rows),
            'columns': max(len(row) for row in rows) if rows else 0,
            'data': rows
        }
    
    def _extract_land_fields(self, text: str, document_type: str, form_data: Dict) -> Dict[str, Any]:
        """Extract land document specific fields"""
        
        # Common patterns for Indian land documents
        patterns = {
            'survey_number': [
                r'Survey\s*(?:No|Number|#)?[:\s]*([A-Za-z0-9\/\-]+)',
                r'Sy\s*(?:No)?[:\s]*([A-Za-z0-9\/\-]+)',
                r'सर्वे\s*नं[:\s]*([A-Za-z0-9\/\-]+)'
            ],
            'district': [
                r'District[:\s]*([A-Za-z\s]+)',
                r'जिला[:\s]*([A-Za-z\s]+)'
            ],
            'taluk': [
                r'Taluk[:\s]*([A-Za-z\s]+)',
                r'Tehsil[:\s]*([A-Za-z\s]+)',
                r'तालुक[:\s]*([A-Za-z\s]+)'
            ],
            'village': [
                r'Village[:\s]*([A-Za-z\s]+)',
                r'गांव[:\s]*([A-Za-z\s]+)'
            ],
            'area': [
                r'Area[:\s]*([0-9.,]+\s*(?:sq\s*ft|acres?|hectares?|guntas?))',
                r'Extent[:\s]*([0-9.,]+\s*(?:sq\s*ft|acres?|hectares?|guntas?))',
                r'क्षेत्रफल[:\s]*([0-9.,]+)'
            ],
            'document_number': [
                r'Document\s*(?:No|Number)?[:\s]*([A-Za-z0-9\/\-]+)',
                r'Deed\s*(?:No|Number)?[:\s]*([A-Za-z0-9\/\-]+)',
                r'Registration\s*(?:No|Number)?[:\s]*([A-Za-z0-9\/\-]+)'
            ],
            'date': [
                r'Date[:\s]*([0-9]{1,2}[\/-][0-9]{1,2}[\/-][0-9]{2,4})',
                r'Dated[:\s]*([0-9]{1,2}[\/-][0-9]{1,2}[\/-][0-9]{2,4})'
            ],
            'owner_name': [
                r'(?:Vendee|Buyer|Purchaser)[:\s]*([A-Za-z\s]+)',
                r'(?:Owner|Pattadar)[:\s]*([A-Za-z\s]+)'
            ],
            'seller_name': [
                r'(?:Vendor|Seller)[:\s]*([A-Za-z\s]+)'
            ],
            'consideration_amount': [
                r'Consideration[:\s]*(?:Rs\.?|₹)?\s*([0-9,]+)',
                r'Sale\s*(?:Value|Amount|Consideration)[:\s]*(?:Rs\.?|₹)?\s*([0-9,]+)'
            ]
        }
        
        import re
        
        extracted = {}
        text_upper = text.upper()
        
        for field, field_patterns in patterns.items():
            for pattern in field_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    extracted[field] = match.group(1).strip()
                    break
        
        # Merge with form data
        for key, value in form_data.items():
            normalized_key = key.lower().replace(' ', '_').replace('-', '_')
            if normalized_key not in extracted:
                extracted[normalized_key] = value
        
        # Add document type
        extracted['document_type'] = document_type
        
        return extracted


# Singleton instance
textract_service = TextractService()
