# LandLedger Frontend

React-based user interface for the LandLedger AI-powered land title intelligence platform.

## Features

- Property search and analysis
- AI-generated title confidence scores
- Ownership lineage visualization
- Risk assessment display
- Document upload with OCR
- Audio narration (English/Hindi)

## Setup

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
npm install
```

### Environment Variables

Create a `.env` file:

```env
REACT_APP_API_URL=http://localhost:8000
```

For production (Netlify), set this in environment variables.

### Development

```bash
npm start
```

Opens at [http://localhost:3000](http://localhost:3000)

### Production Build

```bash
npm run build
```

Output in `build/` folder, ready for deployment.

## Deployment

### Netlify

1. Connect your GitHub repository
2. Build command: `npm run build`
3. Publish directory: `build`
4. Add environment variable:
   - Key: `REACT_APP_API_URL`
   - Value: Your backend URL

## Project Structure

```
src/
├── api.js          # API service layer
├── App.js          # Main application component
├── App.css         # Global styles
└── index.js        # Entry point
```
