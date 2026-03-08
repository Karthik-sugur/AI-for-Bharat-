// LandLedger API Service
// Handles all communication with the backend

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Analyze a property and get title confidence score with AI analysis
 * @param {Object} formData - Property details from the form
 * @returns {Promise<Object>} Analysis results
 */
export async function analyzeProperty(formData) {
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      survey_number: formData.survey,
      district: formData.district,
      taluk: formData.taluk,
      village: formData.village || '',
      state: formData.state || 'Karnataka',
      owner_name: formData.owner || '',
      property_type: formData.propType || '',
      area: formData.area || '',
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || error.message || `API error: ${response.status}`);
  }

  return response.json();
}

/**
 * Analyze property with audio narration
 * @param {Object} formData - Property details
 * @param {string} language - Language code ('en' or 'hi')
 * @returns {Promise<Object>} Analysis with audio URL
 */
export async function analyzeWithAudio(formData, language = 'en') {
  const includeHindi = language === 'hi';

  const response = await fetch(`${API_BASE_URL}/api/analyze-with-audio?include_hindi=${includeHindi}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      survey_number: formData.survey,
      district: formData.district,
      taluk: formData.taluk,
      village: formData.village || '',
      state: formData.state || 'Karnataka',
      owner_name: formData.owner || '',
      property_type: formData.propType || '',
      area: formData.area || '',
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || error.message || `API error: ${response.status}`);
  }

  return response.json();
}

/**
 * Get family tree / ownership lineage for a property
 * @param {string} propertyId - Property identifier
 * @returns {Promise<Object>} Family tree data
 */
export async function getFamilyTree(propertyId) {
  const response = await fetch(`${API_BASE_URL}/api/family-tree/${encodeURIComponent(propertyId)}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || `API error: ${response.status}`);
  }

  return response.json();
}

/**
 * Extract text from a scanned document using OCR
 * @param {File} file - Document file (image or PDF)
 * @returns {Promise<Object>} Extracted document data
 */
export async function extractDocument(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/extract-document`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || `API error: ${response.status}`);
  }

  return response.json();
}

/**
 * Ask a legal question with optional context
 * @param {string} query - Legal question
 * @param {string} context - Optional context
 * @returns {Promise<Object>} Legal explanation
 */
export async function askLegalQuery(query, context = '') {
  const response = await fetch(`${API_BASE_URL}/api/legal-query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      context: context,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || `API error: ${response.status}`);
  }

  return response.json();
}

/**
 * Check API health status
 * @returns {Promise<Object>} Health status
 */
export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/api/health`, {
    method: 'GET',
  });

  if (!response.ok) {
    throw new Error('API is not healthy');
  }

  return response.json();
}

// Helper functions - kept for potential future use
// eslint-disable-next-line no-unused-vars
function buildSearchQuery(formData) {
  const parts = [];
  if (formData.survey) parts.push(`Survey: ${formData.survey}`);
  if (formData.village) parts.push(formData.village);
  if (formData.taluk) parts.push(formData.taluk);
  if (formData.district) parts.push(formData.district);
  if (formData.state) parts.push(formData.state);
  return parts.join(', ');
}

/**
 * Transform API response to match frontend data structure
 * This maps the backend response to what the ResultsView expects
 */
export function transformApiResponse(apiResponse) {
  // Backend wraps data in a 'data' property
  const data = apiResponse.data || apiResponse;
  
  // Get score from backend response
  const score = data.title_confidence_score || data.risk_score || 500;
  const riskLevel = data.risk_level || (score >= 700 ? 'low' : score >= 400 ? 'medium' : 'high');
  
  // Get ownership history from backend's ownership_chain
  const ownershipHistory = data.ownership_chain?.ownership_history || [];
  
  // Transform ownership history to lineage format for frontend
  const lineage = ownershipHistory.map((owner, index, arr) => {
    const isLast = index === arr.length - 1;
    const nodeClass = index === 0 ? 'tn1' : 
                      index === 1 ? 'tn2' : 
                      index === 2 ? 'tn3' : 'tn4';
    const lineColor = index === 0 ? 'var(--g)' : 
                      index === 1 ? 'var(--o)' : 'var(--gr)';
    
    return {
      cls: nodeClass,
      lnClr: isLast ? null : lineColor,
      yr: owner.year || owner.from_date?.split('-')[0] || owner.acquisition_year || '—',
      nm: owner.name || owner.owner_name || 'Unknown',
      ty: owner.transfer_type || owner.acquisition_type || owner.type || 'Transfer',
      last: isLast,
    };
  });

  // Transform risk_flags from backend to frontend format
  const riskFlags = data.risk_flags || [];
  const flags = riskFlags.map(flag => {
    if (typeof flag === 'string') {
      return [flag, ''];
    }
    return [flag.title || flag.type || flag.flag || 'Issue', flag.description || flag.details || ''];
  });

  // Transform recommendations
  const recommendations = data.recommendations || [];

  // Transform family tree from backend format
  let familyTree = null;
  if (data.family_tree) {
    const ft = data.family_tree;
    familyTree = {
      originalOwner: ft.original_owner || ft.root_owner || 'Unknown',
      heirs: (ft.heirs || ft.legal_heirs || []).map(h => ({
        name: h.name || h.heir_name,
        relation: h.relation || h.relationship || 'Heir'
      })),
      partitionStatus: ft.partition_status || (ft.partition_filed ? 'Partition Filed' : 'Partition Record Missing')
    };
  }

  return {
    score: score,
    riskLevel: riskLevel,
    lineage: lineage.length > 0 ? lineage : null,
    flags: flags,
    aiAnalysis: data.ai_summary || data.ai_analysis || '',
    recommendations: recommendations,
    propertyDetails: {
      propertyId: data.property?.property_id || data.analysis_id || '',
      address: `${data.property?.village || ''}, ${data.property?.taluk || ''}, ${data.property?.district || ''}`,
      area: data.property?.area || '',
      propertyType: data.property?.property_type || '',
      currentOwner: data.ownership_chain?.current_owner?.name || '',
      state: data.property?.state || 'Karnataka',
    },
    familyTree: familyTree,
    encumbrances: data.encumbrances || [],
    audioUrl: data.audio_url || null,
    analyzedAt: data.analyzed_at || new Date().toISOString(),
    cached: apiResponse.cached || false,
  };
}

const api = {
  analyzeProperty,
  analyzeWithAudio,
  getFamilyTree,
  extractDocument,
  askLegalQuery,
  checkHealth,
  transformApiResponse,
};

export default api;
