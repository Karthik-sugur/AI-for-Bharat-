# 🏛️ Lineage
### AI-Powered Land Title Intelligence for India

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react" />
  <img src="https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi" />
  <img src="https://img.shields.io/badge/AWS-Bedrock%20%7C%20Textract%20%7C%20Polly-FF9900?style=flat-square&logo=amazon-aws" />
</p>

---

# 🌏 Vision

Land ownership in India is one of the **most legally complex systems in the world**.

Every property carries decades of history —  
sale deeds, inheritance transfers, mutation records, encumbrances, court disputes and family partitions.

Despite increasing digitization, **understanding whether a title is actually safe is still extremely difficult**.

Citizens rely on lawyers.  
Banks rely on manual verification.  
Government portals only show **documents — not insights**.

**Lineage transforms fragmented land records into actionable intelligence.**

Instead of reading hundreds of legal documents, users receive:

• Ownership lineage reconstruction  
• Legal risk detection  
• AI-generated explanations  
• A **Title Confidence Score**

Our goal is to make land ownership **transparent, verifiable, and trustworthy**.

---

# 🎯 Problem

Property verification in India suffers from five structural issues:

### 1. Fragmented Land Systems
India has **28 state land registries**, each with different formats, rules, and record systems.

### 2. Broken Ownership Chains
Decades of undocumented transfers or missing mutation entries can break the ownership timeline.

### 3. Hidden Encumbrances
Loans, liens, or litigation may exist but are buried across multiple registries.

### 4. Complex Inheritance Laws
Joint family ownership, coparcenary rights, and partition deeds complicate title verification.

### 5. Legal Language Barriers
Land records are often written in regional languages or dense legal terminology.

Even a **single missing record can block a property sale for years.**

---

# 💡 Our Solution

Lineage introduces a new concept:

## **Title Intelligence**

Instead of simply displaying documents, the platform **analyzes ownership history using AI**.

### Core Capabilities

1️⃣ **Ownership Lineage Reconstruction**

Rebuilds the complete ownership chain across generations.

2️⃣ **Legal Risk Detection**

Identifies encumbrances, disputes, mutation gaps, and structural issues.

3️⃣ **Title Confidence Score**

A **0–1000 trust score** inspired by credit scoring models like CIBIL.

4️⃣ **Plain-Language Legal Explanation**

AI summarizes complex legal situations into understandable insights.

5️⃣ **Multilingual Accessibility**

Users can listen to analysis through **Hindi and English voice narration**.

6️⃣ **Document OCR**

Automatically extracts data from scanned land records.

---

# 🧠 Synthetic Dataset

To demonstrate real-world complexity, the prototype uses a **synthetic dataset of 1000 simulated land records**.

Each record includes:

• ownership transfers  
• inheritance events  
• mutation records  
• encumbrances  
• legal complications  

### Risk Gradient

The dataset intentionally increases in complexity.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              Lineage Architecture                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   ┌─────────────┐         ┌─────────────────────────────────────────────┐    │
│   │   React     │   API   │              Python Backend (FastAPI)        │    │
│   │   Frontend  │◄───────►│  ┌─────────┐  ┌──────────┐  ┌───────────┐   │    │
│   │             │         │  │ Routes  │──│ Services │──│ AWS SDK   │   │    │
│   └─────────────┘         │  └─────────┘  └──────────┘  └───────────┘   │    │
│                           └──────────────────┬──────────────────────────┘    │
│                                              │                                │
│   ┌──────────────────────────────────────────┼──────────────────────────────┐│
│   │                        AWS Cloud Services│                              ││
│   │                                          ▼                              ││
│   │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐            ││
│   │  │ Amazon Bedrock │  │ Amazon Textract│  │ Amazon Polly   │            ││
│   │  │ (Claude 3)     │  │ (Document OCR) │  │ (Text-to-Speech)│           ││
│   │  │                │  │                │  │                │            ││
│   │  │ • Legal Analysis│ │ • Scanned Deeds│  │ • English Voice│            ││
│   │  │ • Risk Assessment│ │ • Mutation Forms│ │ • Hindi Voice  │            ││
│   │  │ • Recommendations│ │ • 7/12 Extracts│  │                │            ││
│   │  └────────────────┘  └────────────────┘  └────────────────┘            ││
│   │                                                                         ││
│   │  ┌────────────────┐  ┌────────────────┐                                ││
│   │  │ Amazon S3      │  │ Amazon DynamoDB│                                ││
│   │  │ (Storage)      │  │ (Caching)      │                                ││
│   │  │                │  │                │                                ││
│   │  │ • Documents    │  │ • Analysis Cache│                               ││
│   │  │ • Audio Files  │  │ • Session Data │                                ││
│   │  └────────────────┘  └────────────────┘                                ││
│   └─────────────────────────────────────────────────────────────────────────┘│
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend development)
- AWS Account with credentials
- AWS CLI configured

### 1. Clone & Setup Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
cp .env.example .env
# Edit .env with your AWS credentials
```

### 2. Run Backend

```bash
uvicorn app.main:app --reload --port 8000
```

### 3. Run Frontend

```bash
cd frontend
npm install
npm start
```

### 4. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Deployment

### Backend (AWS Elastic Beanstalk)

```bash
cd backend
pip install awsebcli
eb init landledger-backend --platform "Python 3.11" --region ap-south-1
eb create landledger-env --instance-type t3.small
eb setenv AWS_REGION=ap-south-1 \
  S3_BUCKET_NAME=landledger-documents \
  DYNAMODB_TABLE_NAME=landledger-cache \
  DYNAMODB_LAND_RECORDS_TABLE=landledger-land-records \
  BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
eb deploy
```

### Frontend (Netlify)

1. Connect GitHub repository to Netlify
2. Build command: `npm run build`
3. Publish directory: `frontend/build`
4. Environment variable: `REACT_APP_API_URL=<your-backend-url>`

### Seed DynamoDB

```bash
cd backend
python seed_dynamodb.py
```

---

## 📁 Project Structure

```
Lineage/
├── frontend/                    # React Application
│   ├── src/
│   │   ├── App.js              # Main application component
│   │   ├── api.js              # API service layer
│   │   └── ...
│   ├── public/
│   └── package.json
│
├── backend/                     # Python FastAPI Backend
│   ├── app/
│   │   ├── main.py             # FastAPI application
│   │   ├── config.py           # Configuration settings
│   │   ├── api/
│   │   │   └── routes.py       # REST API endpoints
│   │   ├── services/
│   │   │   ├── bedrock_service.py    # AI analysis (Claude 3)
│   │   │   ├── textract_service.py   # Document OCR
│   │   │   ├── polly_service.py      # Text-to-Speech
│   │   │   ├── s3_service.py         # Storage service
│   │   │   ├── dynamo_service.py     # Caching service
│   │   │   └── land_records_service.py # Core business logic
│   │   ├── models/
│   │   │   ├── schemas.py      # Pydantic request models
│   │   │   └── responses.py    # API response models
│   │   └── utils/
│   │       ├── logger.py       # Logging utilities
│   │       └── exceptions.py   # Custom exceptions
│   ├── data/
│   │   └── synthetic_data.json # Sample property records
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── docker-compose.yml           # Local development setup
└── README.md                    # This file
```

---

# ⚙️ Technology Stack

### Frontend

• React 18  
• Interactive property analysis dashboard  
• Ownership lineage visualization  

### Backend

• Python  
• REST API architecture  
• Risk scoring engine  

### AI Infrastructure

| Service | Purpose |
|-------|--------|
| Amazon Bedrock | AI reasoning and explanation |
| Amazon Textract | Document OCR |
| Amazon Polly | Voice narration |

### Cloud Infrastructure

| Service | Role |
|-------|-------|
| Amazon S3 | Document storage |
| Amazon DynamoDB | Metadata and caching |

---

# 🚀 Quick Start

### Backend Setup

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/analyze` | Analyze property, get title score |
| `POST` | `/api/analyze-with-audio` | Analysis + Hindi/English audio |
| `POST` | `/api/extract-document` | OCR for scanned documents |
| `GET` | `/api/family-tree/{id}` | Ownership lineage visualization |
| `POST` | `/api/legal-query` | Ask legal questions |

### Example Request

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "survey_number": "84/3B",
    "district": "Bengaluru Urban",
    "taluk": "Whitefield",
    "state": "Karnataka"
  }'
```

---

## 🧠 AI Services

### Amazon Bedrock (Claude 3 Sonnet)
- **Property Risk Analysis**: Evaluates ownership chain, encumbrances, litigation
- **Legal Explanations**: Plain-language summaries of complex legal issues
- **Recommendations**: Actionable steps to clear title issues
- **Language Translation**: Hindi translations for regional users

### Amazon Textract
- **Document Types**: Sale deeds, mutation forms, 7/12 extracts, Patta, RTC
- **Structured Extraction**: Automatically identifies fields like survey numbers, dates, areas
- **Handwriting Support**: Handles scanned documents with handwritten annotations

### Amazon Polly
- **Voices**: Joanna (English), Aditi (Hindi)
- **Neural TTS**: Natural-sounding audio summaries
- **Accessibility**: Audio playback for visually impaired users

---

## 💰 Cost Estimation (Hackathon Scale)

| Service | Usage | Estimated Cost |
|---------|-------|----------------|
| Bedrock (Claude 3 Sonnet) | ~100 analyses | $5-10 |
| Textract | ~50 documents | Free tier |
| Polly | ~500 audio clips | Free tier |
| S3 | ~100MB | Free tier |
| DynamoDB | Light caching | Free tier |
| **Total** | | **~$10-15** |

*Well within $100 AWS free credits budget*

---

## 🔒 Security

- Environment variables for all secrets
- IAM roles for AWS service access
- CORS configuration for API security
- Input validation with Pydantic
- No credentials in code

---

## 🎯 Demo Scenarios

### Scenario 1: Clean Title (Score: 850+)
```
Survey: 84/3B, Whitefield, Bengaluru
Result: Clear ownership chain, no encumbrances, all mutations updated
```

### Scenario 2: Medium Risk (Score: 400-700)
```
Survey: 221/1A, Mysuru (Agricultural)
Result: Active bank loan, pending mutation update since 2018
```

### Scenario 3: High Risk (Score: <400)
```
Premises: 12/A, Shyambazar, Kolkata (HUF Property)
Result: Pending partition suit, multiple coparceners, protected tenant
```

---
---

# 🚀 Future Roadmap

Lineage can evolve into a **national land intelligence infrastructure layer**.

Potential integrations include:

• State land registries (Bhulekh, Bhoomi, Dharani)  
• Court case databases  
• Bank collateral verification systems  
• Property tax registries  
• National property transaction networks  

The long-term goal is to build **India's first AI-driven land title verification layer.**

---

# 👥 Team

**Iterium**

AI for Bharat Hackathon Submission

---

<p align="center">
<strong>Lineage</strong> — Making Land Ownership Transparent 🏛️
</p>
