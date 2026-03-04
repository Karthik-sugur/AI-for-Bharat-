import { AlertTriangle, CheckCircle, AlertCircle, Info } from 'lucide-react';

interface RiskMeterProps {
  score: number;
  riskLevel: string;
  showLabel?: boolean;
}

export function RiskMeter({ score, riskLevel, showLabel = true }: RiskMeterProps) {
  const normalizedScore = Math.max(0, Math.min(1000, score));
  const percentage = (normalizedScore / 1000) * 100;
  
  const getRiskColor = () => {
    if (percentage >= 85) return 'var(--green)';
    if (percentage >= 70) return 'var(--gold)';
    return 'var(--red)';
  };

  const getRiskIcon = () => {
    if (percentage >= 85) return <CheckCircle size={16} />;
    if (percentage >= 70) return <AlertCircle size={16} />;
    return <AlertTriangle size={16} />;
  };

  return (
    <div className="risk-meter">
      {showLabel && (
        <div className="risk-header">
          <span className="risk-label">Title Confidence Score</span>
          <span className="risk-value" style={{ color: getRiskColor() }}>
            {getRiskIcon()}
            {normalizedScore}/1000
          </span>
        </div>
      )}
      <div className="risk-bar">
        <div 
          className="risk-fill" 
          style={{ 
            width: `${percentage}%`,
            background: `linear-gradient(90deg, var(--red) 0%, var(--gold) 50%, var(--green) 100%)`,
          }}
        />
        <div 
          className="risk-indicator"
          style={{ left: `${percentage}%` }}
        />
      </div>
      <div className="risk-level" style={{ color: getRiskColor() }}>
        {riskLevel}
      </div>
    </div>
  );
}

interface RiskFlagProps {
  flags: Array<{
    flag_type: string;
    severity: 'High' | 'Medium' | 'Low';
    description: string;
  }>;
}

export function RiskFlags({ flags }: RiskFlagProps) {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'High': return 'var(--red)';
      case 'Medium': return 'var(--gold)';
      case 'Low': return 'var(--green)';
      default: return 'var(--gr)';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'High': return <AlertTriangle size={14} />;
      case 'Medium': return <AlertCircle size={14} />;
      case 'Low': return <Info size={14} />;
      default: return <Info size={14} />;
    }
  };

  if (!flags || flags.length === 0) {
    return (
      <div className="no-flags">
        <CheckCircle size={20} />
        <span>No risk flags identified</span>
      </div>
    );
  }

  return (
    <div className="risk-flags">
      {flags.map((flag, index) => (
        <div key={index} className="risk-flag" style={{ borderLeftColor: getSeverityColor(flag.severity) }}>
          <div className="flag-header">
            <span className="flag-severity" style={{ color: getSeverityColor(flag.severity) }}>
              {getSeverityIcon(flag.severity)}
              {flag.severity}
            </span>
            <span className="flag-type">{flag.flag_type}</span>
          </div>
          <p className="flag-description">{flag.description}</p>
        </div>
      ))}
    </div>
  );
}

export default RiskMeter;
