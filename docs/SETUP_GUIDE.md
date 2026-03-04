# 🚀 LandLedger Setup Guide

Complete guide for setting up and running the LandLedger application.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Backend Installation](#backend-installation)
- [Frontend Installation](#frontend-installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required
- **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
- **Node.js 18+**: [Download Node.js](https://nodejs.org/)
- **Google Gemini API Key**: [Get API Key](https://makersuite.google.com/app/apikey)

### Optional
- **Git**: For version control
- **VS Code**: Recommended IDE

## Backend Installation

### Step 1: Setup Project

```powershell
# Navigate to project directory
cd "c:\Users\Admin\Documents\Railway_sprint_1\Land ledger"

# Verify Python installation
python --version  # Should show 3.8 or higher
```

### Step 2: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# You should see (.venv) in your prompt
```

**Troubleshooting activation issues:**
```powershell
# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Install Dependencies

```powershell
# Install all required packages
pip install -r backend/requirements.txt

# Verify installation
pip list
```

**Key dependencies:**
- Flask 3.0+
- Flask-CORS 4.0+
- google-generativeai 0.8+
- python-dotenv 1.0+

## Frontend Installation

### Step 1: Navigate to Frontend

```powershell
cd frontend/land_ledger
```

### Step 2: Install Dependencies

```powershell
npm install
```

### Step 3: Verify Installation

```powershell
npm list --depth=0
```

**Key dependencies:**
- React 18
- Vite
- TypeScript
- Axios
- Lucide React (icons)

## Configuration

### Step 1: Environment Variables

```powershell
# Copy example config
cp .env.example .env

# Edit .env file (use notepad or your preferred editor)
notepad .env
```

### Step 2: Required Configuration

**Minimum required in `.env`:**
```env
# CRITICAL: Add your Gemini API key
GEMINI_API_KEY=your_actual_key_here

# Data path (default should work)
DATA_PATH=./backend/data/synthetic_data.json
```

**Full configuration options:**
```env
# Flask Configuration
FLASK_ENV=development
DEBUG=True
HOST=0.0.0.0
PORT=5000
SECRET_KEY=change-this-in-production

# Google Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-pro
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2000

# Data Configuration
DATA_PATH=./backend/data/synthetic_data.json
SAMPLE_QUERIES_PATH=./backend/data/sample_queries.json

# CORS Configuration
CORS_ORIGINS=*

# Risk Assessment Thresholds
RISK_SCORE_HIGH=700
RISK_SCORE_MEDIUM=850
RISK_SCORE_LOW=900

# Logging
LOG_LEVEL=INFO
```

### Step 3: Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key
5. Paste into `.env` file

## Running the Application

### Backend Server

```powershell
# Terminal 1 - Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Navigate to backend
cd backend

# Start Flask server
python main.py
```

**Expected Output:**
```
INFO:werkzeug:Loaded 1000 property records
 * Running on http://0.0.0.0:5000
```

✅ Backend runs at `http://localhost:5000`

### Frontend Development Server

```powershell
# Terminal 2 - Navigate to frontend
cd frontend/land_ledger

# Start Vite dev server
npm run dev
```

**Expected Output:**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
```

✅ Frontend runs at `http://localhost:3000`

### Running Both

Open two terminals:
1. **Terminal 1**: Run backend (`python main.py`)
2. **Terminal 2**: Run frontend (`npm run dev`)

Or use the start script:
```powershell
.\start.ps1
```

### Option 2: Manual Start (Backend Only)

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Navigate to backend
cd backend

# Start Flask server
python main.py
```

### Expected Output

```
INFO:werkzeug:Loaded 1000 property records
INFO:__main__:Loaded 1000 property records
 * Running on http://0.0.0.0:5000
 * Running on http://127.0.0.1:5000
```

✅ Server is now running at `http://localhost:5000`

## Testing

### Test 1: Health Check

```powershell
# In a new PowerShell window
curl http://localhost:5000/api/health
```

**Expected Response:**
```json
{
  "success": true,
  "message": "LandLedger API is running",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Test 2: Run Full Test Suite

```powershell
# Run automated tests
.\test_api.ps1
```

This will test all 6 API endpoints:
1. ✅ Health Check
2. ✅ Get Properties
3. ✅ Analyze Property
4. ✅ Family Tree
5. ✅ Risk Assessment
6. ✅ Encumbrances

### Test 3: Manual API Calls

**Test Property Analysis:**
```powershell
$body = @{
    land_id = "LAND-001"
    query = "What are the risks?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/analyze" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
```

## Opening the Frontend

### Option 1: Open in Browser
```powershell
# Open index.html
start frontend/index.html
```

### Option 2: Use Simple Server
```powershell
# Install http-server globally (if not installed)
npm install -g http-server

# Navigate to frontend
cd frontend

# Start server
http-server -p 8080
```

Then open: `http://localhost:8080`

## Troubleshooting

### Issue: "Port 5000 already in use"

**Solution 1: Kill existing process**
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Solution 2: Change port**
```env
# In .env file
PORT=5001
```

### Issue: "ModuleNotFoundError: No module named 'flask'"

**Solution:**
```powershell
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Issue: "API key not found"

**Symptoms:**
- AI analysis returns "Gemini AI unavailable"
- No AI recommendations

**Solution:**
```powershell
# Verify .env file exists
Test-Path .env

# Check if API key is set (should NOT show actual key)
Select-String -Path .env -Pattern "GEMINI_API_KEY"

# Make sure there are no extra spaces or quotes around the key
```

### Issue: "Data file not found"

**Solution:**
```powershell
# Verify data file exists
Test-Path backend\data\synthetic_data.json

# Check file size (should be ~10.7 MB)
(Get-Item backend\data\synthetic_data.json).length / 1MB
```

### Issue: "Could not find synthetic_data.json"

**Solution:**
```powershell
# Make sure you're running from the correct directory
# Should be in: "Railway_sprint_1\Land ledger\"
pwd

# If in wrong directory, navigate to correct one
cd "c:\Users\Admin\Documents\Railway_sprint_1\Land ledger"
```

## Development Workflow

### Making Changes

```powershell
# 1. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 2. Make your changes to Python files

# 3. Restart the server
# Press Ctrl+C in the terminal running Flask
# Then run: python backend/main.py
```

### Adding New Dependencies

```powershell
# Install new package
pip install package-name

# Update requirements file
pip freeze > backend/requirements.txt
```

## Production Deployment

### Security Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` in .env
- [ ] Set `DEBUG=False`
- [ ] Restrict `CORS_ORIGINS` to your domain
- [ ] Secure your Gemini API key
- [ ] Use environment variables (don't commit .env)
- [ ] Set up HTTPS

### Recommended Changes

```env
# Production .env
FLASK_ENV=production
DEBUG=False
SECRET_KEY=generate-strong-random-key-here
CORS_ORIGINS=https://yourdomain.com
LOG_LEVEL=WARNING
```

## Additional Resources

- [API Documentation](API_DOCUMENTATION.md)
- [Gemini Integration Guide](GEMINI_INTEGRATION.md)
- [Data Format Specification](DATA_FORMAT.md)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Google Gemini API Docs](https://ai.google.dev/docs)

## Support

If you encounter issues not covered here:

1. Check the logs in the terminal
2. Verify all configuration settings
3. Review error messages carefully
4. Check file paths are correct
5. Ensure virtual environment is activated

---

**Ready to start?**
```powershell
.\start.ps1
```

Then open: `http://localhost:5000/api/health`
