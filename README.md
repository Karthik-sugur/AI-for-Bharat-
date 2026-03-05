# 🏛️ Lineage - AI-Powered Land Title Intelligence System

**AI for Bharat Hackathon**

An intelligent system for analyzing land titles, detecting risks, and providing AI-powered insights using Google Gemini.

## 🌟 Features

- **AI-Powered Analysis**: Gemini AI integration for intelligent property assessment
- **Modern React Frontend**: Beautiful, responsive UI built with React + Vite + TypeScript
- **Risk Detection**: Comprehensive title risk scoring (0-1000 scale)
- **Family Tree Mapping**: Visualize ownership lineage and inheritance patterns
- **Encumbrance Tracking**: Monitor loans, liens, and legal claims
- **RESTful API**: Complete API for property intelligence

## 📋 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/search` | POST | Search properties by survey number |
| `/api/analyze` | POST | Complete AI property analysis |
| `/api/family-tree` | POST | Ownership lineage & family tree |
| `/api/risk-assessment` | POST | Comprehensive risk scoring |
| `/api/encumbrances` | POST | Active loans/liens check |
| `/api/properties` | GET | List all properties |

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- Google Gemini API key

### Backend Setup

```powershell
cd "c:\Users\Admin\Documents\Railway_sprint_1\Land ledger"

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Start backend server
cd backend
python main.py
```

Backend runs at: `http://localhost:5000`

### Frontend Setup

```powershell
cd frontend/land_ledger

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at: `http://localhost:3000`

## 📊 Data Structure

- **1000+ property records** in `backend/data/synthetic_data.json`
- Each property includes:
  - Ownership chain (multi-generational)
  - Family tree structure
  - Encumbrance history
  - Legal status & documentation
  - Risk indicators

## 🔍 Example API Calls

### Analyze Property
```bash
POST /api/analyze
{
  "land_id": "LAND-001",
  "query": "What are the risks?"
}
```

### Get Family Tree
```bash
POST /api/family-tree
{
  "land_id": "LAND-001"
}
```

### Risk Assessment
```bash
POST /api/risk-assessment
{
  "land_id": "LAND-001"
}
```

## 🏗️ Architecture

```
LandLedger/
├── backend/
│   ├── main.py              # Flask API server
│   ├── config.py            # Environment config
│   ├── requirements.txt     # Python dependencies
│   ├── models/              # Data models (Property, Owner, etc.)
│   ├── services/            # Business logic
│   │   ├── gemini_service.py      # AI integration
│   │   ├── land_records_service.py
│   │   ├── family_tree_service.py
│   │   └── risk_analyzer.py
│   ├── utils/              # Utilities
│   │   ├── validators.py
│   │   ├── formatters.py
│   │   └── data_parser.py
│   └── data/               # Property dataset
├── frontend/
│   └── land_ledger/        # React + Vite + TypeScript app
│       ├── src/
│       │   ├── components/  # React components
│       │   ├── services/    # API client
│       │   ├── types/       # TypeScript types
│       │   └── App.tsx      # Main app
│       └── package.json
├── docs/                   # Documentation
└── lineage-data/           # Data generation scripts
```

## 🎯 Risk Scoring System

Title confidence score (0-1000):
- **900-1000**: Low Risk - Clear title
- **850-899**: Medium Risk - Minor issues
- **700-849**: High Risk - Significant concerns
- **<700**: Critical Risk - Major defects

### Weighting:
- Encumbrances: 40%
- Ownership Gaps: 35%
- Missing Documents: 15%
- Legal Flags: 10%

## 🧪 Testing

Sample property IDs for testing:
- `LAND-001` to `LAND-1000`

Example locations:
- Mumbai, Maharashtra
- Bangalore, Karnataka
- Hyderabad, Telangana
- Chennai, Tamil Nadu

## 📚 Documentation

Detailed docs in `/docs`:
- [API Documentation](docs/API_DOCUMENTATION.md)
- [Setup Guide](docs/SETUP_GUIDE.md)
- [Gemini Integration](docs/GEMINI_INTEGRATION.md)
- [Data Format](docs/DATA_FORMAT.md)

## 🛠️ Tech Stack

- **Backend**: Flask 3.0 + Python 3.x
- **Frontend**: React 18 + Vite + TypeScript
- **AI**: Google Gemini (gemini-pro)
- **Styling**: CSS with custom design system
- **Data**: JSON-based property dataset

## 🔑 Environment Variables

```env
GEMINI_API_KEY=your_key_here
DATA_PATH=./backend/data/synthetic_data.json
FLASK_ENV=development
PORT=5000
```

## 👥 Team

Developed for AI for Bharat Hackathon

## 📄 License

MIT License

## 🤝 Contributing

This is a hackathon project. Contributions welcome!

---

**Status**: ✅ All API endpoints implemented and functional
