import axios from 'axios';
import type {
  ApiResponse,
  AnalyzeResponse,
  RiskAssessmentResponse,
  FamilyTreeResponse,
  PropertiesListResponse,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Improve error handling - return error response data instead of throwing
api.interceptors.response.use(
  response => response,
  error => {
    if (axios.isAxiosError(error) && error.response?.data) {
      // Return the actual error response data from the server
      return Promise.resolve({
        data: error.response.data,
        status: error.response.status,
      } as any);
    }
    throw error;
  }
);

export const landLedgerApi = {
  // Health check
  async healthCheck(): Promise<{ status: string; service: string; version: string }> {
    const response = await api.get('/health');
    return response.data;
  },

  // Get all properties
  async getProperties(limit?: number, offset?: number): Promise<ApiResponse<PropertiesListResponse>> {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit.toString());
    if (offset) params.append('offset', offset.toString());
    
    const response = await api.get(`/properties?${params.toString()}`);
    return response.data;
  },

  // Search properties by survey number and location
  async searchProperties(
    surveyNumber: string,
    village?: string,
    district?: string,
    state?: string
  ): Promise<ApiResponse<PropertiesListResponse>> {
    const response = await api.post('/search', {
      survey_number: surveyNumber,
      village: village || '',
      district: district || '',
      state: state || '',
    });
    return response.data;
  },

  // Analyze a property
  async analyzeProperty(landId: string | number, query?: string): Promise<ApiResponse<AnalyzeResponse>> {
    const response = await api.post('/analyze', {
      land_id: landId.toString(),
      query: query || 'Provide a comprehensive analysis',
    });
    return response.data;
  },

  // Get risk assessment
  async getRiskAssessment(landId: string | number): Promise<ApiResponse<RiskAssessmentResponse>> {
    const response = await api.post('/risk-assessment', {
      land_id: landId.toString(),
    });
    return response.data;
  },

  // Get family tree
  async getFamilyTree(landId: string | number): Promise<ApiResponse<FamilyTreeResponse>> {
    const response = await api.post('/family-tree', {
      land_id: landId.toString(),
    });
    return response.data;
  },

  // Get encumbrances
  async getEncumbrances(landId: string | number): Promise<ApiResponse<{ encumbrances: unknown[]; summary: unknown }>> {
    const response = await api.post('/encumbrances', {
      land_id: landId.toString(),
    });
    return response.data;
  },
};

export default landLedgerApi;
