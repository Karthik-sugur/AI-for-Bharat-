# LandLedger Backend

AI-powered Land Title Intelligence Platform for India

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        LandLedger Backend                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   FastAPI    │───▶│   Services   │───▶│  AWS Cloud   │      │
│  │   (REST)     │    │   Layer      │    │  Services    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Pydantic   │    │  Bedrock AI  │    │   Textract   │      │
│  │   Models     │    │  (Claude 3)  │    │   (OCR)      │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                            │                   │               │
│                            ▼                   ▼               │
│                      ┌──────────────┐    ┌──────────────┐      │
│                      │    Polly     │    │    S3 +      │      │
│                      │   (TTS)      │    │  DynamoDB    │      │
│                      └──────────────┘    └──────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry
│   ├── config.py            # Configuration settings
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py       # Request/Response models
│   │   └── responses.py     # API response models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── bedrock_service.py      # AI analysis (Claude 3)
│   │   ├── textract_service.py     # Document OCR
│   │   ├── polly_service.py        # Text-to-Speech
│   │   ├── s3_service.py           # Document storage
│   │   ├── dynamo_service.py       # Result caching
│   │   └── land_records_service.py # Core business logic
│   └── utils/
│       ├── __init__.py
│       ├── logger.py        # Logging utilities
│       └── exceptions.py    # Custom exceptions
├── data/
│   └── synthetic_data.json  # Sample property records
├── requirements.txt
├── Dockerfile
├── application.py           # Elastic Beanstalk entry
├── .ebextensions/
│   └── python.config
└── .env.example
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- AWS Account with configured credentials
- AWS CLI installed and configured

### 1. Clone and Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit with your AWS credentials
notepad .env   # Windows
# or
nano .env      # Linux/Mac
```

Required environment variables:
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=landledger-documents
DYNAMODB_TABLE_NAME=landledger-cache
```

### 3. Run Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 5000
```

API will be available at: `http://localhost:5000`

## 📚 API Endpoints

### Health Check
```
GET /api/health
```

### Property Analysis (Main Endpoint)
```
POST /api/analyze
Content-Type: application/json

{
  "query": "123, MG Road, Bangalore",
  "query_type": "address"  // or "survey_number", "property_id"
}
```

### Property Analysis with Audio
```
POST /api/analyze-with-audio
Content-Type: application/json

{
  "query": "Survey No. 234, Hoskote",
  "query_type": "survey_number",
  "language": "hi"  // "en" for English, "hi" for Hindi
}
```

### Document OCR Extraction
```
POST /api/extract-document
Content-Type: multipart/form-data

file: <document_image.jpg>
```

### Family Tree / Ownership Lineage
```
GET /api/family-tree/{property_id}
```

### Legal Query
```
POST /api/legal-query
Content-Type: application/json

{
  "query": "What is the process for property mutation in Maharashtra?",
  "context": "Property purchase"
}
```

## 🧠 AWS Services Used

| Service | Purpose | Free Tier Limit |
|---------|---------|-----------------|
| **Amazon Bedrock** | AI analysis using Claude 3 Sonnet | Pay per token |
| **Amazon Textract** | OCR for scanned documents | 100 pages/month |
| **Amazon Polly** | Text-to-Speech in Hindi/English | 5M characters/month |
| **Amazon S3** | Document & audio storage | 5GB + 20K requests |
| **Amazon DynamoDB** | Analysis result caching | 25GB + 25 WCU/RCU |

### Cost Estimation (Hackathon Scale)

| Service | Estimated Usage | Cost |
|---------|----------------|------|
| Bedrock (Claude 3 Sonnet) | ~100 analyses | ~$5-10 |
| Textract | ~50 documents | Free tier |
| Polly | ~500 audio clips | Free tier |
| S3 | ~100MB storage | Free tier |
| DynamoDB | Light caching | Free tier |
| **Total** | | **~$10-15** |

## 🐳 Docker Deployment

### Build and Run Locally

```bash
docker build -t landledger-backend .
docker run -p 5000:5000 --env-file .env landledger-backend
```

### Using Docker Compose

```bash
# From project root
docker-compose up -d
```

## ☁️ AWS Elastic Beanstalk Deployment

### 1. Install EB CLI

```bash
pip install awsebcli
```

### 2. Initialize EB Application

```bash
cd backend
eb init -p python-3.11 landledger-backend
```

### 3. Create Environment

```bash
eb create landledger-prod --instance-type t3.micro
```

### 4. Configure Environment Variables

```bash
eb setenv AWS_REGION=us-east-1 S3_BUCKET_NAME=landledger-documents
```

### 5. Deploy

```bash
eb deploy
```

## 🔒 Security Best Practices

1. **Never commit `.env` file** - Use AWS Secrets Manager in production
2. **IAM Roles** - Use IAM roles instead of access keys in production
3. **CORS Configuration** - Update `ALLOWED_ORIGINS` for production domain
4. **API Rate Limiting** - Consider adding rate limiting for production
5. **Input Validation** - All inputs are validated with Pydantic schemas

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

## 📈 Monitoring

- **Health endpoint**: `/api/health` for uptime monitoring
- **CloudWatch Logs**: Automatically captured in Elastic Beanstalk
- **X-Ray Tracing**: Can be enabled for request tracing

## 🛠️ Development

### Code Style

```bash
# Format code
black app/

# Lint
flake8 app/
```

### Adding New Services

1. Create service file in `app/services/`
2. Implement singleton pattern with `_instance` class variable
3. Add error handling with fallback logic
4. Register in `app/services/__init__.py`

## 📋 API Response Format

All API responses follow this structure:

```json
{
  "success": true,
  "message": "Analysis complete",
  "data": {
    // Response data here
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Error responses:

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "VALIDATION_ERROR",
  "details": {}
}
```

## 🤝 Contributing

1. Create feature branch
2. Make changes with tests
3. Submit pull request

## 📄 License

MIT License - See LICENSE file for details

---

**Built for Hackathon 2024** 🏆

*LandLedger - Making Property Verification Intelligent*
