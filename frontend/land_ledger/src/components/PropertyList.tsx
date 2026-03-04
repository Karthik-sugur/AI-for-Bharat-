import { MapPin, User, AlertTriangle, CheckCircle, AlertCircle } from 'lucide-react';
import type { PropertySummary } from '../types';

interface PropertyListProps {
  properties: PropertySummary[];
  onSelect: (landId: number) => void;
  selectedId?: number;
}

export function PropertyList({ properties, onSelect, selectedId }: PropertyListProps) {
  const getRiskIcon = (riskLevel: string) => {
    switch (riskLevel.toLowerCase()) {
      case 'low':
        return <CheckCircle size={14} className="risk-icon low" />;
      case 'medium':
        return <AlertCircle size={14} className="risk-icon medium" />;
      case 'high':
      case 'high risk':
        return <AlertTriangle size={14} className="risk-icon high" />;
      default:
        return <AlertCircle size={14} className="risk-icon" />;
    }
  };

  if (!properties || properties.length === 0) {
    return (
      <div className="no-data">
        <p>No properties found</p>
      </div>
    );
  }

  return (
    <div className="property-list">
      {properties.map((property) => (
        <div
          key={property.land_id}
          className={`property-card ${selectedId === property.land_id ? 'selected' : ''}`}
          onClick={() => onSelect(property.land_id)}
        >
          <div className="property-header">
            <span className="property-id">#{property.land_id}</span>
            <span className="property-risk">
              {getRiskIcon(property.risk_level)}
              {property.risk_level}
            </span>
          </div>
          <div className="property-survey">{property.survey_number}</div>
          <div className="property-details">
            <span className="property-location">
              <MapPin size={12} />
              {property.location}
            </span>
            <span className="property-type">{property.land_type}</span>
          </div>
          <div className="property-owner">
            <User size={12} />
            {property.current_owner}
          </div>
        </div>
      ))}
    </div>
  );
}

export default PropertyList;
