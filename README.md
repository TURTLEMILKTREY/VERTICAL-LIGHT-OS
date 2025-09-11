# VERTICAL LIGHT OS - AI Marketing Platform

A modern AI-powered marketing platform with FastAPI backend and Next.js frontend, featuring enterprise-grade dynamic configuration management and production-ready deployment capabilities.

## 📚 Documentation

For comprehensive technical documentation, see our [**Enterprise Documentation Structure**](./docs/README.md):

- **📊 [System Analysis](./docs/analysis/)** - Technical audits and hardcoded value analysis
- **⚙️ [Configuration System](./docs/configuration/)** - Dynamic configuration management  
- **🚀 [Production Readiness](./docs/production-readiness/)** - Deployment roadmaps and implementation tracking
- **📈 [Development Progress](./docs/development-progress/)** - Daily progress and milestone tracking

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### Development Setup

#### Option 1: Manual Setup

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Frontend Setup**
   ```bash
   cd frontend-new
   npm install
   npm run dev
   ```

#### Option 2: Docker Setup

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run in detached mode
docker-compose up -d
```

### Access Points

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🏗️ Architecture

### Backend (FastAPI)
- **Location**: `/backend`
- **Port**: 8000
- **Features**:
  - RESTful API endpoints
  - CORS enabled for frontend communication
  - Pydantic models for data validation
  - Mock data for development

### Frontend (Next.js)
- **Location**: `/frontend-new`
- **Port**: 3000
- **Features**:
  - Modern React dashboard
  - Real-time backend connectivity
  - Responsive design with Tailwind CSS
  - TypeScript support

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/parse-goal` | Parse business goals |
| GET | `/api/campaigns` | Get all campaigns |
| POST | `/api/campaigns` | Create new campaign |
| GET | `/api/campaigns/{id}` | Get specific campaign |
| GET | `/api/leads` | Get all leads |
| GET | `/api/leads/{id}` | Get specific lead |
| GET | `/api/analytics` | Get dashboard analytics |

## 🔧 Features

### Current Features
- ✅ Backend-Frontend connection established
- ✅ CORS configured for cross-origin requests
- ✅ Health monitoring and connection status
- ✅ Campaign management system
- ✅ Lead tracking
- ✅ Analytics dashboard
- ✅ Mock data for development

### Dashboard Features
- Real-time connection status indicator
- Analytics cards showing key metrics
- Campaign and lead management
- Test campaign creation
- Responsive design

## 🧪 Testing the Connection

1. Start both services (backend on :8000, frontend on :3000)
2. Visit http://localhost:3000
3. Look for the green "Backend Connected" indicator
4. Click "Create Test Campaign" to test API communication
5. Check that data appears in the dashboard

## 📁 Project Structure

```
VERTICAL LIGHT OS/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # API endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic models
│   ├── services/              # Business logic
│   ├── main.py               # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend-new/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx      # Main dashboard
│   │   │   └── layout.tsx
│   │   └── lib/
│   │       ├── api.ts        # Axios configuration
│   │       └── services.ts   # API service functions
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml        # Development setup
```

## 🔜 Next Steps

1. **Database Integration**: Replace mock data with real database
2. **Authentication**: Add user authentication and authorization
3. **AI Services**: Implement actual AI-powered features
4. **Real Campaign Management**: Connect to advertising platforms
5. **Enhanced Analytics**: Add charts and visualizations
6. **Testing**: Add unit and integration tests

## 🛟 Troubleshooting

### Backend Not Starting
- Check Python version (3.9+)
- Ensure all dependencies are installed
- Verify port 8000 is available

### Frontend Not Connecting
- Ensure backend is running on port 8000
- Check CORS configuration
- Verify API URL in frontend environment

### CORS Issues
- Backend is configured to allow `localhost:3000`
- If using different ports, update CORS origins in `backend/main.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the backend-frontend connection
5. Submit a pull request

---

**Status**: ✅ Frontend and Backend Successfully Linked!
