import { ArrowLeft, MapPin, User, FileText, Sparkles } from 'lucide-react';
import type { AnalyzeResponse } from '../types';
import { RiskMeter, RiskFlags } from './RiskMeter';
import { OwnershipTimeline } from './OwnershipTimeline';
import { FamilyTreeView } from './FamilyTreeView';

interface AnalysisViewProps {
  data: AnalyzeResponse;
  onBack: () => void;
}

export function AnalysisView({ data, onBack }: AnalysisViewProps) {
  const { property, owners_chain, title_confidence_score, risk_level, ai_summary } = data;

  // Extract risk flags from property defects
  const riskFlags = property.defects?.map((defect) => ({
    flag_type: defect.replace(/_/g, ' '),
    severity: 'High' as const,
    description: defect.replace(/_/g, ' '),
  })) || [];

  return (
    <div className="analysis-view">
      {/* Header */}
      <div className="analysis-header">
        <button className="back-btn" onClick={onBack}>
          <ArrowLeft size={16} />
          <span>Back to Search</span>
        </button>
        <span className="property-id-badge">Land #{property.land_id}</span>
      </div>

      {/* Score Hero */}
      <div className="score-hero">
        <div className="hero-corners">
          <div className="corner tl" />
          <div className="corner tr" />
          <div className="corner bl" />
          <div className="corner br" />
        </div>
        <div className="score-label">Title Confidence Score</div>
        <div className="score-value">{title_confidence_score}</div>
        <RiskMeter score={title_confidence_score} riskLevel={risk_level} showLabel={false} />
        <div className="score-meta">
          Survey: {property.survey_number} • {property.district}
        </div>
      </div>

      {/* AI Summary */}
      {ai_summary && (
        <div className="result-block ai-block">
          <div className="block-stripe ai" />
          <div className="block-label">
            <Sparkles size={14} />
            AI Analysis
          </div>
          <p className="ai-summary">{ai_summary}</p>
        </div>
      )}

      {/* Property Details */}
      <div className="result-block">
        <div className="block-stripe property" />
        <div className="block-label">
          <FileText size={14} />
          Property Details
        </div>
        <div className="property-grid">
          <div className="detail-item">
            <span className="detail-label">Survey Number</span>
            <span className="detail-value">{property.survey_number}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Location</span>
            <span className="detail-value">
              <MapPin size={12} />
              {property.district}, {property.location || property.taluk}
            </span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Land Type</span>
            <span className="detail-value">{property.land_type}</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Area</span>
            <span className="detail-value">{property.area_sqft} acres</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Current Owner</span>
            <span className="detail-value">
              <User size={12} />
              {property.current_owner}
            </span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Encumbrance</span>
            <span className="detail-value">
              {property.encumbrance?.active ? 'Active' : 'None'}
              {property.encumbrance?.type !== 'None' && ` (${property.encumbrance?.type})`}
            </span>
          </div>
        </div>
      </div>

      {/* Risk Flags */}
      {riskFlags.length > 0 && (
        <div className="result-block">
          <div className="block-stripe risk" />
          <div className="block-label">Risk Flags</div>
          <RiskFlags flags={riskFlags} />
        </div>
      )}

      {/* Ownership Timeline */}
      {owners_chain && owners_chain.length > 0 && (
        <div className="result-block">
          <div className="block-stripe ownership" />
          <OwnershipTimeline owners={owners_chain} />
        </div>
      )}

      {/* Family Tree */}
      {property.family_tree && (
        <div className="result-block">
          <div className="block-stripe family" />
          <FamilyTreeView familyTree={property.family_tree} />
        </div>
      )}
    </div>
  );
}

export default AnalysisView;
