import { User, ArrowDown } from 'lucide-react';
import type { Owner } from '../types';

interface OwnershipTimelineProps {
  owners: Owner[];
}

export function OwnershipTimeline({ owners }: OwnershipTimelineProps) {
  if (!owners || owners.length === 0) {
    return (
      <div className="no-data">
        <p>No ownership history available</p>
      </div>
    );
  }

  const sortedOwners = [...owners].sort((a, b) => {
    const dateA = new Date(a.acquisition_date).getTime();
    const dateB = new Date(b.acquisition_date).getTime();
    return dateA - dateB;
  });

  return (
    <div className="ownership-timeline">
      <div className="timeline-header">
        <span className="blbl">
          Ownership Chain
          <span className="owner-count">{owners.length} owners</span>
        </span>
      </div>
      <div className="timeline-items">
        {sortedOwners.map((owner, index) => {
          const isLast = index === sortedOwners.length - 1;
          const year = owner.acquisition_date 
            ? new Date(owner.acquisition_date).getFullYear() 
            : 'Unknown';
          
          return (
            <div key={owner.owner_id || index} className="timeline-item">
              <div className="timeline-spine">
                <div className={`timeline-node ${isLast ? 'current' : ''}`}>
                  <User size={12} />
                </div>
                {!isLast && (
                  <div className="timeline-line">
                    <ArrowDown size={10} className="timeline-arrow" />
                  </div>
                )}
              </div>
              <div className="timeline-year">{year}</div>
              <div className="timeline-content">
                <div className="owner-name">
                  {owner.name}
                  {owner.is_current_owner && <span className="current-badge">Current</span>}
                </div>
                <div className="owner-method">
                  {owner.acquisition_method !== 'Unknown' && owner.acquisition_method}
                </div>
                {owner.document_reference && (
                  <div className="owner-doc">Doc: {owner.document_reference}</div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default OwnershipTimeline;
