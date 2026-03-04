import { useState } from 'react';
import { PropertySearch, PropertyList, AnalysisView } from './components';
import { landLedgerApi } from './services/api';
import type { AnalyzeResponse, PropertySummary } from './types';
import './App.css';

type ViewState = 'search' | 'results' | 'analysis';

function App() {
  const [view, setView] = useState<ViewState>('search');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchResults, setSearchResults] = useState<PropertySummary[]>([]);
  const [analysisData, setAnalysisData] = useState<AnalyzeResponse | null>(null);
  const [selectedPropertyId, setSelectedPropertyId] = useState<number | undefined>();
  const [searchQuery, setSearchQuery] = useState<string>('');

  const handleSearch = async (surveyNumber: string, village: string, district: string, state: string) => {
    setIsLoading(true);
    setError(null);
    setSearchQuery(surveyNumber);

    try {
      console.log('Searching for:', { surveyNumber, village, district, state });
      const response = await landLedgerApi.searchProperties(surveyNumber, village, district, state);
      console.log('Search response:', response);
      
      if (response.success) {
        console.log('Found properties:', response.data.properties);
        setSearchResults(response.data.properties);
        if (response.data.properties.length === 1) {
          // If only one result, go directly to analysis
          handlePropertySelect(response.data.properties[0].land_id);
        } else {
          setView('results');
        }
      } else {
        console.log('Search error:', response.error);
        setError(response.error || 'No properties found');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Search failed';
      console.error('Search exception:', err);
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePropertySelect = async (landId: number) => {
    setIsLoading(true);
    setError(null);
    setSelectedPropertyId(landId);

    try {
      const response = await landLedgerApi.analyzeProperty(landId);
      if (response.success) {
        setAnalysisData(response.data);
        setView('analysis');
      } else {
        setError(response.error || 'Analysis failed');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to analyze property';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => {
    if (view === 'analysis' && searchResults.length > 1) {
      setView('results');
    } else {
      setView('search');
      setSearchResults([]);
    }
    setAnalysisData(null);
    setError(null);
  };

  return (
    <div className="app">
      {/* Background Effects */}
      <div className="scene">
        <div className="orb o1" />
        <div className="orb o2" />
        <div className="orb o3" />
      </div>
      <div className="gridlines" />

      {/* Navigation */}
      <nav>
        <div className="nav-logo">
          Land<b>Ledger</b>
        </div>
        <div className="nav-links">
          <button onClick={() => { setView('search'); setSearchResults([]); setError(null); }}>Home</button>
          <a href="#about">About</a>
        </div>
      </nav>

      {/* Main Content */}
      <main>
        {view === 'search' && (
          <section id="home" className="hero">
            <div className="hero-content">
              <span className="hero-kicker">AI-Powered Title Intelligence</span>
              <h1>
                Verify Land Titles
                <em>with Confidence</em>
                <span className="sw">AI for Bharat Hackathon</span>
              </h1>
              <p className="hero-desc">
                Enter property details below to get comprehensive AI analysis of land ownership, 
                encumbrances, and title risks.
              </p>

              <PropertySearch onSearch={handleSearch} isLoading={isLoading} />

              {error && (
                <div className="error-message">
                  <span>⚠️ {error}</span>
                </div>
              )}

              {/* Stats */}
              <div className="stats-row">
                <div className="stat">
                  <div className="stat-num">1000<span className="u">+</span></div>
                  <div className="stat-lbl">Properties</div>
                </div>
                <div className="stat">
                  <div className="stat-num">AI</div>
                  <div className="stat-lbl">Powered</div>
                </div>
                <div className="stat">
                  <div className="stat-num">100<span className="u">%</span></div>
                  <div className="stat-lbl">Transparent</div>
                </div>
              </div>
            </div>
          </section>
        )}

        {view === 'results' && (
          <section id="results" className="results-section">
            <div className="results-header">
              <button className="back-btn" onClick={handleBack}>
                ← Back to Search
              </button>
              <h2>Search Results for "{searchQuery}"</h2>
              <p>{searchResults.length} properties found</p>
            </div>

            {error && (
              <div className="error-message">
                <span>⚠️ {error}</span>
              </div>
            )}

            <PropertyList
              properties={searchResults}
              onSelect={handlePropertySelect}
              selectedId={selectedPropertyId}
            />
          </section>
        )}

        {view === 'analysis' && analysisData && (
          <section id="analysis" className="results-section">
            <AnalysisView data={analysisData} onBack={handleBack} />
          </section>
        )}
      </main>

      {/* Loading Overlay */}
      {isLoading && (
        <div className="loader on">
          <div className="l-cross">
            <div className="l-ring" />
          </div>
          <div className="l-text">{view === 'search' ? 'Searching Properties' : 'Analyzing Property'}</div>
          <div className="l-step">{view === 'search' ? 'Looking up records...' : 'Generating AI insights...'}</div>
        </div>
      )}
    </div>
  );
}

export default App;
