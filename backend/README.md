# Central Brain - FastAPI Backend

An AI-powered RAG (Retrieval-Augmented Generation) application backend for the hackathon.

## Tech Stack

- **Framework**: FastAPI + Uvicorn
- **Database**: MongoDB (async via Motor)
- **Vector Store**: Pinecone
- **LLM/Embeddings**: Google Gemini
- **File Storage**: Cloudflare R2 (S3-compatible)
- **Environment**: Python-dotenv, Pydantic

## Project Structure

```
app/
├── main.py                      # FastAPI entry point & CORS config
├── core/
│   └── config.py               # Pydantic BaseSettings for env vars
├── api/
│   └── routes/
│       ├── upload.py           # POST /api/upload
│       ├── chat.py             # POST /api/chat
│       └── status.py           # POST /api/status
├── services/
│   ├── db_service.py           # MongoDB operations
│   ├── llm_service.py          # Google Gemini integration
│   ├── vector_service.py       # Pinecone operations
│   └── storage_service.py      # Cloudflare R2 operations
└── models/
    └── schemas.py              # Pydantic request/response schemas
```

## Setup Instructions

### 1. Install Dependencies

Create a Python virtual environment (Python 3.10+):

```bash
python -m venv venv
source venv/Scripts/activate  # On Windows
# or
source venv/bin/activate      # On macOS/Linux
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Fill in your credentials in `.env`:

```
MONGODB_URI=mongodb+srv://...
PINECONE_API_KEY=...
GOOGLE_API_KEY=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_ENDPOINT_URL=...
```

**Server Configuration (optional):**
```
HOST=127.0.0.1      # 0.0.0.0 for production
PORT=8000
LOG_LEVEL=info
RELOAD=true         # false for production
```

### 3. Run the Application

**Local Development:**
```bash
python run.py
```

Or with uvicorn directly:
```bash
uvicorn app.main:app --reload
```

**Production (Render):**
All configuration is handled via environment variables in render.yaml or the Render dashboard.

The API will be available at `http://127.0.0.1:8000`

### 4. Access API Documentation

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## API Endpoints

### Upload File

```
POST /api/upload
```

Upload a PDF or TXT file. The backend will:
1. Upload to Cloudflare R2
2. Extract text content
3. Generate embeddings via Gemini
4. Store vectors in Pinecone
5. Save metadata to MongoDB

**Request**: Form data with `file` field

**Response**:
```json
{
  "file_name": "document.pdf",
  "file_size": 12345,
  "r2_path": "uploads/2024-01-01T00:00:00.000000_document.pdf",
  "vector_count": 1,
  "status": "success"
}
```

### Chat (RAG Query)

```
POST /api/chat
```

Ask a question. The backend will:
1. Generate question embedding
2. Search Pinecone for relevant context
3. Send context + question to Gemini
4. Return AI-generated answer

**Request**:
```json
{
  "question": "What is the main topic?",
  "context_limit": 5
}
```

**Response**:
```json
{
  "answer": "The main topic is...",
  "sources": ["document.pdf"],
  "confidence": 0.87
}
```

### Status Update

```
POST /api/status
```

Post a developer status update:

**Request**:
```json
{
  "developer_name": "John Doe",
  "update_text": "Completed feature X, working on feature Y..."
}
```

**Response**:
```json
{
  "status_id": "507f1f77bcf86cd799439011",
  "summary": "John made progress on features X and Y...",
  "stored_at": "2024-01-01T00:00:00.000000"
}
```

### Get Daily Summary

```
GET /api/status/daily-summary
```

Get consolidated AI summary of all status updates for the day.

### Health Check

```
GET /health
```

Check service health and connectivity.

## Development Notes

### Key Features

- ✅ Modular service architecture with Dependency Injection
- ✅ Async/await throughout for performance
- ✅ Comprehensive error handling
- ✅ CORS enabled for frontend integration
- ✅ Pydantic validation on all inputs
- ✅ Detailed docstrings and comments

### TODO Items

1. **PDF Text Extraction**: Implement using PyPDF2 or pdfplumber
2. **Document Chunking**: Split large documents into smaller chunks for better embeddings
3. **Daily Summary Aggregation**: Filter status updates by date range
4. **Error Recovery**: Implement retry logic for external API calls
5. **Logging**: Add structured logging throughout the application
6. **Unit Tests**: Create comprehensive test suite
7. **Rate Limiting**: Implement rate limiting for API endpoints
8. **Authentication**: Add API key or JWT authentication

### Important Customization Points

- **LLM Model**: Change in `llm_service.py` (default: `gemini-pro`)
- **Embedding Model**: Change in `llm_service.py` (default: `models/embedding-001`)
- **Vector Dimension**: Ensure Pinecone index is configured to match Gemini embeddings
- **Chunk Size**: Modify in `upload.py` when implementing chunking
- **Context Limit**: Default is 5, adjustable per request

## Deployment

### Quick Deploy to Render

**[📖 Full Render Deployment Guide](./RENDER_DEPLOYMENT.md)**

TL;DR:
1. Push to GitHub
2. Go to render.com → Create Web Service → Connect repo
3. Add environment variables (use values from `.env`)
4. Deploy!

**Server automatically reads from `run.py` with config from `.env` or Render environment variables.**

---

## Debugging

### MongoDB Connection Issues
- Verify `MONGODB_URI` in `.env`
- Check IP whitelist in MongoDB Atlas
- Ensure database name exists or auto-create is enabled

### Pinecone Issues
- Verify API key and environment in `.env`
- Ensure index exists and has correct dimension
- Check Pinecone console for quota/limits

### Google Gemini API Issues
- Verify API key is enabled for Generative AI
- Check Google Cloud project quotas
- Ensure API key has necessary permissions

### R2/Boto3 Issues
- Verify AWS credentials and endpoint URL
- Check bucket permissions
- Ensure bucket exists and is accessible

## Deployment

For production deployment:

1. Set `DEBUG=false` and `ENVIRONMENT=production` in `.env`
2. Use production CORS origins
3. Deploy with production-grade ASGI server (e.g., Gunicorn + Uvicorn)
4. Use environment-specific configurations
5. Enable proper logging and monitoring

