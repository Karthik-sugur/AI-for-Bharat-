import { Users, User, CircleDot } from 'lucide-react';
import type { FamilyTree } from '../types';

interface FamilyTreeViewProps {
  familyTree: FamilyTree;
}

export function FamilyTreeView({ familyTree }: FamilyTreeViewProps) {
  if (!familyTree) {
    return (
      <div className="no-data">
        <p>No family tree data available</p>
      </div>
    );
  }

  const { generation_1, generation_2, generation_3 } = familyTree;

  return (
    <div className="family-tree">
      <div className="tree-header">
        <Users size={16} />
        <span>Inheritance Tree</span>
      </div>

      {/* Generation 1 - Original Owner */}
      {generation_1 && (
        <div className="generation gen-1">
          <div className="gen-label">Gen 1 - Original</div>
          <div className="gen-members">
            <div className="member primary">
              <div className="member-icon">
                <User size={16} />
              </div>
              <div className="member-info">
                <span className="member-name">{generation_1.owner}</span>
                <span className="member-meta">
                  Acquired {generation_1.acquired_year} via {generation_1.acquisition_type}
                </span>
                {generation_1.spouse && (
                  <span className="member-spouse">Spouse: {generation_1.spouse}</span>
                )}
                {generation_1.death_year && (
                  <span className="member-death">Deceased: {generation_1.death_year}</span>
                )}
              </div>
            </div>
          </div>
          {generation_1.children && generation_1.children.length > 0 && (
            <div className="gen-children">
              <span className="children-label">Children:</span>
              <div className="children-list">
                {generation_1.children.map((child, idx) => (
                  <span key={idx} className="child-tag">{child}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Generation 2 */}
      {generation_2 && generation_2.length > 0 && (
        <div className="generation gen-2">
          <div className="gen-label">Gen 2 - Heirs</div>
          <div className="gen-members-grid">
            {generation_2.map((member, idx) => (
              <div key={idx} className={`member ${member.alive ? '' : 'deceased'}`}>
                <div className="member-header">
                  <CircleDot size={10} className={member.alive ? 'alive' : 'deceased'} />
                  <span className="member-name">{member.name}</span>
                </div>
                <div className="member-details">
                  <span>{member.relation} • Born {member.birth_year}</span>
                  <span className="member-status">
                    {member.alive ? member.whereabouts : 'Deceased'}
                  </span>
                  {member.dispute && (
                    <span className="member-dispute">⚠️ {member.dispute}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Generation 3 */}
      {generation_3 && generation_3.length > 0 && (
        <div className="generation gen-3">
          <div className="gen-label">Gen 3 - Current</div>
          <div className="gen-members-grid">
            {generation_3.map((member, idx) => (
              <div key={idx} className={`member ${member.alive ? '' : 'deceased'}`}>
                <div className="member-header">
                  <CircleDot size={10} className={member.alive ? 'alive' : 'deceased'} />
                  <span className="member-name">{member.name}</span>
                </div>
                <div className="member-details">
                  <span>{member.relation} • Born {member.birth_year}</span>
                  {member.dispute && (
                    <span className="member-dispute">⚠️ {member.dispute}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default FamilyTreeView;
