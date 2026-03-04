# 📖 LandLedger API Documentation

Complete API reference for the LandLedger Land Title Intelligence System.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently no authentication required (development mode).

## Response Format

All endpoints return JSON with the following structure:

```json
{
  "success": true|false,
  "data": { ... },
  "error": "error message if applicable",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

---

## Endpoints

### 1. Health Check

Check if the API is running.

**Endpoint:** `GET /api/health`

**Parameters:** None

**Response:**
```json
{
  "success": true,
  "message": "LandLedger API is running",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

**Status Codes:**
- `200` - API is healthy

---

### 2. Analyze Property

Comprehensive AI-powered property analysis with Gemini.

**Endpoint:** `POST /api/analyze`

**Request Body:**
```json
{
  "land_id": "LAND-001",
  "query": "What are the main risks with this property?"
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| land_id | string | Yes | Unique property identifier |
| query | string | No | Specific question for AI analysis |

**Response:**
```json
{
  "success": true,
  "data": {
    "property": {
      "land_id": "LAND-001",
      "survey_number": "SY-123/45",
      "district": "Mumbai",
      "state": "Maharashtra",
      "village": "Andheri",
      "current_owner": "Rajesh Kumar",
      "property_type": "Residential",
      "area_acres": 0.25
    },
    "owners_chain": [
      {
        "owner_name": "Rajesh Kumar",
        "from_year": 2015,
        "to_year": null,
        "transfer_type": "Inheritance",
        "documents_available": true
      }
    ],
    "encumbrances": [
      {
        "type": "Home Loan",
        "amount": 5000000,
        "lender": "HDFC Bank",
        "start_date": "2015-06-01",
        "status": "Active"
      }
    ],
    "risk_flags": [
      {
        "category": "Encumbrance",
        "severity": "Medium",
        "description": "Active home loan of ₹50,00,000"
      }
    ],
    "title_confidence_score": 875,
    "risk_level": "Medium",
    "ai_summary": "This is a residential property...",
    "recommendations": [
      "Obtain loan clearance certificate from HDFC Bank",
      "Verify all inheritance documents are properly registered"
    ]
  }
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid land_id
- `404` - Property not found
- `500` - Server error

---

### 3. Family Tree

Build ownership lineage and family tree visualization.

**Endpoint:** `POST /api/family-tree`

**Request Body:**
```json
{
  "land_id": "LAND-001"
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| land_id | string | Yes | Unique property identifier |

**Response:**
```json
{
  "success": true,
  "data": {
    "land_id": "LAND-001",
    "current_owner": "Rajesh Kumar",
    "family_tree": {
      "property_id": "LAND-001",
      "current_owner": "Rajesh Kumar",
      "nodes": [
        {
          "id": 0,
          "name": "Shyam Kumar",
          "generation": 1,
          "owned_property": true,
          "relation": "grandfather",
          "from_year": 1975
        },
        {
          "id": 1,
          "name": "Ram Kumar",
          "generation": 2,
          "owned_property": true,
          "relation": "father",
          "transfer_type": "Inheritance"
        },
        {
          "id": 2,
          "name": "Rajesh Kumar",
          "generation": 3,
          "owned_property": true,
          "relation": "son",
          "transfer_type": "Inheritance"
        }
      ],
      "relationships": [
        {
          "from": 0,
          "to": 1,
          "type": "father"
        },
        {
          "from": 1,
          "to": 2,
          "type": "son"
        }
      ],
      "inheritance_patterns": {
        "total_transfers": 2,
        "inheritance_count": 2,
        "sale_count": 0,
        "inheritance_percentage": 100.0,
        "is_family_succession": true
      },
      "generation_count": 3,
      "total_members": 3
    },
    "ownership_timeline": [
      {
        "period": "1975-2000",
        "owner": "Shyam Kumar",
        "duration_years": 25,
        "transfer_type": "Original Owner"
      },
      {
        "period": "2000-2015",
        "owner": "Ram Kumar",
        "duration_years": 15,
        "transfer_type": "Inheritance"
      },
      {
        "period": "2015-Present",
        "owner": "Rajesh Kumar",
        "duration_years": 9,
        "transfer_type": "Inheritance"
      }
    ],
    "family_related_risks": [
      {
        "type": "Multiple Generations",
        "severity": "Low",
        "description": "Property passed through 3 generations - verify all inheritance documents"
      }
    ]
  }
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid land_id
- `404` - Property not found
- `500` - Server error

---

### 4. Risk Assessment

Comprehensive title risk calculation and breakdown.

**Endpoint:** `POST /api/risk-assessment`

**Request Body:**
```json
{
  "land_id": "LAND-001"
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| land_id | string | Yes | Unique property identifier |

**Response:**
```json
{
  "success": true,
  "data": {
    "land_id": "LAND-001",
    "property": {
      "land_id": "LAND-001",
      "survey_number": "SY-123/45",
      "current_owner": "Rajesh Kumar"
    },
    "title_confidence_score": 875,
    "risk_level": "Medium",
    "risk_summary": {
      "total_flags": 3,
      "by_severity": {
        "Critical": 0,
        "High": 0,
        "Medium": 2,
        "Low": 1
      },
      "by_category": {
        "Encumbrance": 1,
        "Missing Documents": 1,
        "Ownership Gap": 1
      }
    },
    "risk_flags": [
      {
        "category": "Encumbrance",
        "severity": "Medium",
        "description": "Active home loan of ₹50,00,000",
        "impact": "Medium"
      },
      {
        "category": "Missing Documents",
        "severity": "Medium",
        "description": "Sale deed for 2000 transfer not available",
        "impact": "Medium"
      }
    ],
    "risk_report": {
      "overall_score": 875,
      "risk_level": "Medium",
      "score_breakdown": {
        "encumbrance_score": 840,
        "ownership_continuity_score": 900,
        "documentation_score": 850,
        "legal_status_score": 950
      },
      "weighted_scores": {
        "encumbrance_weight": 0.40,
        "ownership_weight": 0.35,
        "documentation_weight": 0.15,
        "legal_weight": 0.10
      },
      "key_findings": [
        "Clear ownership chain through inheritance",
        "Active encumbrance needs clearance",
        "Some historical documents missing"
      ],
      "recommendations": [
        "Obtain loan clearance certificate",
        "Request missing sale deed",
        "Verify inheritance documents"
      ]
    }
  }
}
```

**Risk Scoring:**
- **900-1000**: Low Risk - Clear title
- **850-899**: Medium Risk - Minor issues
- **700-849**: High Risk - Significant concerns
- **<700**: Critical Risk - Major defects

**Status Codes:**
- `200` - Success
- `400` - Invalid land_id
- `404` - Property not found
- `500` - Server error

---

### 5. Check Encumbrances

Get all loans, liens, and legal claims on property.

**Endpoint:** `POST /api/encumbrances`

**Request Body:**
```json
{
  "land_id": "LAND-001"
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| land_id | string | Yes | Unique property identifier |

**Response:**
```json
{
  "success": true,
  "data": {
    "land_id": "LAND-001",
    "property": {
      "land_id": "LAND-001",
      "survey_number": "SY-123/45",
      "current_owner": "Rajesh Kumar"
    },
    "encumbrances": [
      {
        "type": "Home Loan",
        "amount": 5000000,
        "lender": "HDFC Bank",
        "start_date": "2015-06-01",
        "end_date": null,
        "status": "Active",
        "registration_number": "HL/2015/12345"
      },
      {
        "type": "Property Tax Lien",
        "amount": 25000,
        "lender": "Municipal Corporation",
        "start_date": "2023-04-01",
        "status": "Cleared",
        "cleared_date": "2023-05-15"
      }
    ],
    "summary": {
      "total_encumbrances": 2,
      "active_count": 1,
      "cleared_count": 1,
      "total_active_amount": 5000000,
      "by_type": {
        "Home Loan": 1,
        "Property Tax Lien": 1
      }
    }
  }
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid land_id
- `404` - Property not found
- `500` - Server error

---

### 6. List Properties

Get a list of all available properties in the database.

**Endpoint:** `GET /api/properties`

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | integer | 50 | Max properties to return |
| offset | integer | 0 | Number to skip (pagination) |
| state | string | - | Filter by state |
| district | string | - | Filter by district |

**Example:**
```
GET /api/properties?limit=10&state=Maharashtra
```

**Response:**
```json
{
  "success": true,
  "data": {
    "properties": [
      {
        "land_id": "LAND-001",
        "survey_number": "SY-123/45",
        "district": "Mumbai",
        "state": "Maharashtra",
        "village": "Andheri",
        "current_owner": "Rajesh Kumar",
        "property_type": "Residential",
        "area_acres": 0.25
      }
    ],
    "total_properties": 1000,
    "returned_count": 10,
    "offset": 0,
    "limit": 10
  }
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid parameters
- `500` - Server error

---

## Error Responses

All errors follow this format:

```json
{
  "success": false,
  "error": "Detailed error message",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Common Error Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 400 | Bad Request | Missing required fields, invalid format |
| 404 | Not Found | Property ID doesn't exist |
| 500 | Server Error | Database issues, AI service down |

---

## Rate Limiting

Currently no rate limiting in development mode.

For production deployment, recommended limits:
- 100 requests per minute per IP
- 1000 requests per hour per IP

---

## Sample Test Data

Use these property IDs for testing:

| Land ID | Location | Type | Special Features |
|---------|----------|------|------------------|
| LAND-001 | Mumbai, Maharashtra | Residential | Family succession |
| LAND-002 | Bangalore, Karnataka | Commercial | Multiple sales |
| LAND-050 | Hyderabad, Telangana | Agricultural | Active disputes |
| LAND-100 | Chennai, Tamil Nadu | Residential | Clear title |

---

## SDK / Client Libraries

### PowerShell Example

```powershell
# Analyze property
$body = @{
    land_id = "LAND-001"
    query = "Check risks"
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "http://localhost:5000/api/analyze" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"

$response.data
```

### Python Example

```python
import requests

# Analyze property
response = requests.post(
    'http://localhost:5000/api/analyze',
    json={
        'land_id': 'LAND-001',
        'query': 'Check risks'
    }
)

data = response.json()
print(data['data']['title_confidence_score'])
```

### JavaScript Example

```javascript
// Analyze property
fetch('http://localhost:5000/api/analyze', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        land_id: 'LAND-001',
        query: 'Check risks'
    })
})
.then(response => response.json())
.then(data => console.log(data.data));
```

---

## Changelog

### Version 1.0.0 (Current)
- Initial release
- 6 API endpoints
- Gemini AI integration
- Risk assessment system
- Family tree visualization

---

## Support

For issues or questions:
- Check [Setup Guide](SETUP_GUIDE.md)
- Review [Troubleshooting](SETUP_GUIDE.md#troubleshooting)
- Check server logs for detailed errors

---

**Base URL:** `http://localhost:5000/api`

**API Status:** ✅ All endpoints operational
