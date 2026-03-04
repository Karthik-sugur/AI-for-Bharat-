// Property Types
export interface Property {
  land_id: number;
  survey_number: string;
  district: string;
  taluk?: string;
  village?: string;
  location?: string;
  land_type: string;
  area_sqft: number;
  current_owner: string;
  risk_level: string;
  defects: string[];
  disputes: string[];
  encumbrance: Encumbrance;
  family_tree?: FamilyTree;
  legal?: LegalInfo;
}

export interface Encumbrance {
  type: string;
  active: boolean;
  lender: string | null;
  amount_lakhs: number | null;
  year_created: number | null;
  year_closed: number | null;
  ec_certificate_available: boolean;
  ec_period_covered?: string;
}

export interface Owner {
  owner_id: string;
  name: string;
  acquisition_date: string;
  acquisition_method: string;
  disposal_date: string | null;
  document_reference: string | null;
  relationship_to_current: string;
  is_current_owner: boolean;
}

export interface FamilyTree {
  generation_1?: Generation1;
  generation_2?: FamilyMember[];
  generation_3?: FamilyMember[];
}

export interface Generation1 {
  owner: string;
  spouse: string;
  acquired_year: number;
  acquisition_type: string;
  death_year: number | null;
  children: string[];
}

export interface FamilyMember {
  name: string;
  gender: string;
  relation: string;
  birth_year: number;
  alive: boolean;
  whereabouts: string;
  dispute: string | null;
}

export interface LegalInfo {
  mutation_status: string;
  mutation_delay_flag: boolean;
  loan_active: boolean;
  litigation_status: string;
  area_mismatch_flag: boolean;
  undervaluation_flag: boolean;
  coparcenary_property: boolean;
  huf_undivided: boolean;
  will_present: boolean;
  will_registered: boolean;
  will_contested: boolean;
}

export interface RiskFlag {
  flag_id: string;
  flag_type: string;
  severity: 'High' | 'Medium' | 'Low';
  description: string;
  recommendation: string;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  timestamp: string;
  error?: string;
}

export interface AnalyzeResponse {
  property: Property;
  owners_chain: Owner[];
  encumbrances: EncumbranceDetail[];
  risk_level: string;
  title_confidence_score: number;
  ai_summary: string;
  recommendations?: string[];
}

export interface EncumbranceDetail {
  encumbrance_id: string;
  type: string;
  creditor_name: string;
  amount: number | null;
  registration_date: string | null;
  status: string;
  risk_level: string;
}

export interface RiskAssessmentResponse {
  land_id: string;
  property: Property;
  risk_flags: RiskFlag[];
  risk_level: string;
  title_confidence_score: number;
  risk_summary: {
    total_flags: number;
    by_severity: Record<string, number>;
    by_category: Record<string, number>;
  };
  risk_report?: string;
}

export interface FamilyTreeResponse {
  land_id: string;
  property: Property;
  family_tree: FamilyTree;
  ownership_chain: Owner[];
  timeline: TimelineEvent[];
}

export interface TimelineEvent {
  year: number;
  event_type: string;
  description: string;
  persons_involved: string[];
}

export interface PropertiesListResponse {
  properties: PropertySummary[];
  total_properties: number;
  showing: number;
}

export interface PropertySummary {
  land_id: number;
  survey_number: string;
  location: string;
  land_type: string;
  current_owner: string;
  risk_level: string;
}
