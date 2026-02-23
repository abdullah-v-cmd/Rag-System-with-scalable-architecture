# 🚀 RAG Document Intelligence Platform

A production-ready, scalable **Retrieval-Augmented Generation (RAG)** system with advanced document intelligence capabilities. Built with FastAPI, React, PostgreSQL with pgvector, Redis, and Celery.

![Architecture](https://img.shields.io/badge/Architecture-Microservices-blue)
![Python](https://img.shields.io/badge/Python-3.11-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-blue)
![React](https://img.shields.io/badge/React-18.2-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)

## ✨ Features

### Core Features ✅
- **📄 Document Processing**: Upload and process PDF, TXT, DOC, DOCX files
- **🔍 Semantic Search**: Vector similarity search using pgvector
- **🤖 AI-Powered Q&A**: GPT-3.5 powered question answering
- **⚡ Streaming Responses**: Real-time streaming of AI responses
- **💾 Embedding Cache**: Redis-based caching for embeddings and responses
- **🔄 Background Processing**: Celery workers for async document processing
- **📊 Beautiful UI**: Modern React interface with TailwindCSS

### Advanced Features 🎯
- **📐 Smart Chunking**: Intelligent text splitting with overlap strategy
- **🔒 Rate Limiting**: API rate limiting with SlowAPI
- **📝 Comprehensive Logging**: Structured logging with Loguru
- **📈 Real-time Stats**: System metrics and cache statistics
- **🐳 Docker Support**: Full containerization with Docker Compose
- **🔄 CI/CD Pipeline**: GitHub Actions for automated testing and deployment
- **🗄️ Vector Database**: PostgreSQL with pgvector extension for fast similarity search

## 🏗️ Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   React UI      │─────▶│  FastAPI Backend│─────▶│   PostgreSQL    │
│   (Port 3000)   │      │   (Port 8000)   │      │   (pgvector)    │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                 │                         ▲
                                 │                         │
                                 ▼                         │
                         ┌─────────────┐          ┌───────┴────────┐
                         │    Redis    │          │ Celery Workers │
                         │   (Cache)   │          │  (Background)  │
                         └─────────────┘          └────────────────┘
                                                          │
                                                          ▼
                                                  ┌──────────────┐
                                                  │  OpenAI API  │
                                                  │ (Embeddings) │
                                                  └──────────────┘
```

## 📋 Currently Completed Features

### Backend ✅
- ✅ FastAPI REST API with comprehensive endpoints
- ✅ PostgreSQL database with pgvector extension
- ✅ Document upload and processing pipeline
- ✅ PDF/TXT/DOC/DOCX text extraction
- ✅ Smart text chunking with overlap strategy
- ✅ OpenAI embeddings generation with caching
- ✅ Vector similarity search with pgvector
- ✅ RAG-based query answering
- ✅ Streaming response support
- ✅ Redis caching for embeddings and responses
- ✅ Celery background job processing
- ✅ Rate limiting with SlowAPI
- ✅ Structured logging with Loguru
- ✅ Health checks and system stats

### Frontend ✅
- ✅ Beautiful React UI with TailwindCSS
- ✅ Document upload with drag-and-drop
- ✅ Real-time task status tracking
- ✅ Query interface with streaming support
- ✅ Document library management
- ✅ System statistics dashboard
- ✅ Responsive design
- ✅ Error handling and loading states

### DevOps ✅
- ✅ Docker Compose orchestration
- ✅ Multi-container setup (backend, frontend, postgres, redis, celery)
- ✅ GitHub Actions CI/CD pipeline
- ✅ Automated testing workflow
- ✅ Helper scripts for development

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API key

### Setup & Run

1. **Clone the repository**
```bash
git clone <repository-url>
cd webapp
```

2. **Setup environment**
```bash
./scripts/setup.sh
```

3. **Configure OpenAI API Key**
Edit `.env` file and add your OpenAI API key:
```env
OPENAI_API_KEY=your-api-key-here
```

4. **Start all services**
```bash
./scripts/start.sh
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Stop Services
```bash
./scripts/stop.sh
```

### View Logs
```bash
./scripts/logs.sh [service_name]
```

## 📊 API Endpoints

### Documents
- `POST /documents/upload` - Upload document for processing
- `GET /documents` - List all documents
- `GET /documents/{id}` - Get document details
- `DELETE /documents/{id}` - Delete document

### Query
- `POST /query` - Query documents (RAG)
- `POST /query/stream` - Query with streaming response

### Tasks
- `GET /tasks/{task_id}` - Get background task status

### System
- `GET /health` - Health check
- `GET /stats` - System statistics

## 🗄️ Data Models

### Document
```python
{
  "id": int,
  "filename": str,
  "file_size": int,
  "file_type": str,
  "status": str,  # pending, processing, completed, failed
  "upload_date": datetime,
  "processed_at": datetime,
  "metadata": {
    "text_length": int,
    "chunk_count": int
  }
}
```

### Document Chunk
```python
{
  "id": int,
  "document_id": int,
  "chunk_index": int,
  "content": str,
  "embedding": vector(1536),  # OpenAI embedding
  "metadata": dict
}
```

### Query
```python
{
  "query": str,
  "response": str,
  "relevant_chunks": list,
  "execution_time": float
}
```

## 🎯 RAG Workflow

1. **Document Upload** → User uploads document via UI
2. **Background Processing** → Celery worker extracts text and creates chunks
3. **Embedding Generation** → OpenAI generates embeddings for each chunk
4. **Vector Storage** → Embeddings stored in PostgreSQL with pgvector
5. **Query** → User asks question
6. **Vector Search** → Find similar chunks using cosine similarity
7. **Context Building** → Top chunks combined as context
8. **AI Response** → GPT generates answer based on context
9. **Caching** → Response cached in Redis for future queries

## 🛠️ Chunking Strategy

- **Chunk Size**: 1000 characters
- **Chunk Overlap**: 200 characters
- **Boundary Detection**: Attempts to break at sentence/word boundaries
- **Metadata Preservation**: Each chunk maintains document metadata

## 💾 Storage Services

### PostgreSQL with pgvector
- **Documents table**: Document metadata
- **Document chunks table**: Text chunks with vector embeddings
- **Queries table**: Query history and responses
- **Vector index**: IVFFlat index for fast similarity search

### Redis
- **Embedding cache**: Cached embeddings for reuse
- **Query response cache**: Cached responses for frequently asked questions
- **Session storage**: User session data

## 📈 System Statistics

The platform tracks:
- Total documents processed
- Total document chunks
- Total queries handled
- Cache hit rate
- System health status

## 🔐 Rate Limiting

- **Per Minute**: 60 requests
- **Per Hour**: 1000 requests
- Applied to document upload and query endpoints

## 📝 Logging

Structured logging with Loguru:
- Console output with colors
- File rotation (500 MB, 10 days retention)
- Different log levels (DEBUG, INFO, WARNING, ERROR)

## 🧪 Testing

Run backend tests:
```bash
cd backend
pytest
```

Run frontend build:
```bash
cd frontend
npm run build
```

## 🚀 Deployment

### Docker Deployment
The entire application is containerized and can be deployed to any Docker-compatible environment:
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- DigitalOcean App Platform
- Your own server with Docker

### Environment Variables
Required environment variables for production:
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
OPENAI_API_KEY=your-key
CELERY_BROKER_URL=redis://host:6379/1
CELERY_RESULT_BACKEND=redis://host:6379/2
SECRET_KEY=your-secret-key
ENVIRONMENT=production
```

## 🔄 CI/CD Pipeline

GitHub Actions workflow includes:
1. **Test Backend**: Run Python tests with pytest
2. **Test Frontend**: Build React application
3. **Build & Push**: Build Docker images and push to registry
4. **Deploy**: Automated deployment (configure as needed)

## 📚 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database with pgvector extension
- **Redis** - Caching and message broker
- **Celery** - Background task processing
- **OpenAI** - Embeddings and completions
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation

### Frontend
- **React** - UI framework
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **Axios** - HTTP client
- **React Dropzone** - File upload

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **GitHub Actions** - CI/CD
- **Loguru** - Logging

## 🎨 UI Features

- **Modern Design**: Gradient backgrounds, shadows, animations
- **Responsive**: Works on desktop and mobile
- **Real-time Updates**: Task status polling
- **Drag & Drop**: Easy file upload
- **Streaming**: Live response streaming
- **Source Citations**: View relevant document chunks
- **Statistics Dashboard**: Real-time system metrics

## ⚙️ Configuration

### Chunking Settings
```env
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Rate Limiting
```env
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### File Upload
```env
MAX_UPLOAD_SIZE_MB=50
ALLOWED_EXTENSIONS=pdf,txt,doc,docx
```

### OpenAI Settings
```env
EMBEDDING_MODEL=text-embedding-ada-002
CHAT_MODEL=gpt-3.5-turbo
EMBEDDING_DIMENSION=1536
```

## 🐛 Troubleshooting

### Services not starting
```bash
# Check Docker status
docker ps

# View logs
./scripts/logs.sh

# Restart services
./scripts/stop.sh
./scripts/start.sh
```

### Database connection issues
```bash
# Check PostgreSQL container
docker-compose logs postgres

# Check if pgvector extension is loaded
docker-compose exec postgres psql -U raguser -d ragdb -c "SELECT * FROM pg_extension WHERE extname='vector';"
```

### OpenAI API errors
- Verify API key in `.env` file
- Check API quota and billing
- Review logs for specific error messages

## 🔮 Features Not Yet Implemented

- [ ] User authentication and authorization
- [ ] Multi-user support with isolated document spaces
- [ ] Advanced document preview
- [ ] Support for more file formats (Excel, PowerPoint)
- [ ] Document tagging and categorization
- [ ] Custom embedding models
- [ ] Export query history
- [ ] Admin dashboard
- [ ] Prometheus metrics
- [ ] Grafana dashboards

## 🎯 Recommended Next Steps

1. **Add Authentication**: Implement JWT-based authentication
2. **Multi-tenancy**: Add user isolation and workspace management
3. **More File Formats**: Add support for Excel, PowerPoint, images (OCR)
4. **Advanced Search**: Add filters, facets, and advanced query options
5. **Analytics**: Add usage analytics and insights
6. **API Rate Plans**: Implement tiered rate limiting
7. **Document Versioning**: Track document versions and changes
8. **Collaboration**: Add sharing and collaboration features

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check documentation at `/docs`
- Review API documentation at `/docs` (Swagger UI)

## 🙏 Acknowledgments

- OpenAI for embeddings and completions API
- pgvector for vector similarity search
- FastAPI for the excellent web framework
- React and TailwindCSS for the beautiful UI

---

**Built with ❤️ using FastAPI, React, PostgreSQL, Redis, and Celery**
