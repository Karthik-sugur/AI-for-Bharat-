import { useState } from 'react';
import { Search, MapPin, Building, Map } from 'lucide-react';

interface PropertySearchProps {
  onSearch: (surveyNumber: string, village: string, district: string, state: string) => void;
  isLoading?: boolean;
}

export function PropertySearch({ onSearch, isLoading }: PropertySearchProps) {
  const [surveyNumber, setSurveyNumber] = useState('');
  const [village, setVillage] = useState('');
  const [district, setDistrict] = useState('');
  const [state, setState] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (surveyNumber.trim()) {
      onSearch(surveyNumber.trim(), village.trim(), district.trim(), state.trim());
    }
  };

  return (
    <div className="search-block">
      <form onSubmit={handleSubmit}>
        <div className="fields-grid">
          <div className="fcell">
            <label className="flbl">
              <MapPin size={16} />
              Survey Number <span className="req">*</span>
            </label>
            <input
              type="text"
              className="finp"
              placeholder="e.g., SY/242/23"
              value={surveyNumber}
              onChange={(e) => setSurveyNumber(e.target.value)}
              required
            />
          </div>
          <div className="fcell">
            <label className="flbl">
              <Building size={16} />
              Village / City
            </label>
            <input
              type="text"
              className="finp"
              placeholder="e.g., Indiranagar"
              value={village}
              onChange={(e) => setVillage(e.target.value)}
            />
          </div>
          <div className="fcell">
            <label className="flbl">
              <Map size={16} />
              District
            </label>
            <input
              type="text"
              className="finp"
              placeholder="e.g., Bangalore Urban"
              value={district}
              onChange={(e) => setDistrict(e.target.value)}
            />
          </div>
          <div className="fcell">
            <label className="flbl">
              <Map size={16} />
              State
            </label>
            <input
              type="text"
              className="finp"
              placeholder="e.g., Karnataka"
              value={state}
              onChange={(e) => setState(e.target.value)}
            />
          </div>
        </div>
        <div className="search-action">
          <div className="sa-l">
            <span className="sa-hint">
              Press <kbd>Enter</kbd> to search
            </span>
            <span className="req-note">* Required field</span>
          </div>
          <button type="submit" className="sa-btn" disabled={isLoading || !surveyNumber.trim()}>
            <Search size={14} />
            {isLoading ? 'Searching...' : 'Search Property'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default PropertySearch;
