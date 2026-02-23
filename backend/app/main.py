from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import time
import aiofiles
from pathlib import Path
from datetime import datetime
from typing import List

from app.config import settings
from app.database import get_db, init_db
from app.models import Document, DocumentChunk, Query
from app.schemas import (
    DocumentUploadResponse,
    DocumentResponse,
    QueryRequest,
    QueryResponse,
    RelevantChunk,
    TaskStatusResponse,
    HealthResponse,
    StatsResponse
)
from app.vector_db import vector_db_service
from app.openai_service import chat_service
from app.cache import cache_service, redis_client
from app.celery_worker import celery_app, process_document_task
from loguru import logger
import sys

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.LOG_LEVEL
)
logger.add(
    "logs/app.log",
    rotation="500 MB",
    retention="10 days",
    level=settings.LOG_LEVEL
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="A scalable RAG system with vector database and document intelligence"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Starting application...")
    init_db()
    logger.info("Database initialized")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "RAG Document Intelligence Platform",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Check database
        db.execute("SELECT 1")
        db_status = "healthy"
    except:
        db_status = "unhealthy"
    
    try:
        # Check Redis
        redis_client.ping()
        redis_status = "healthy"
    except:
        redis_status = "unhealthy"
    
    # Get cache stats
    cache_stats = cache_service.get_stats()
    
    return HealthResponse(
        status="healthy" if db_status == "healthy" and redis_status == "healthy" else "unhealthy",
        version=settings.VERSION,
        database=db_status,
        redis=redis_status,
        cache_stats=cache_stats
    )


@app.post("/documents/upload", response_model=DocumentUploadResponse, tags=["Documents"])
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a document for processing
    
    Supported formats: PDF, TXT, DOC, DOCX
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower().replace(".", "")
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB"
        )
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
    
    # Save file
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        logger.info(f"Saved file: {safe_filename} ({file_size} bytes)")
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Error saving file")
    
    # Create database record
    document = Document(
        filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file_ext,
        status="pending"
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Queue background processing task
    task = process_document_task.delay(document.id)
    
    logger.info(f"Queued document processing task: {task.id}")
    
    return DocumentUploadResponse(
        id=document.id,
        filename=document.filename,
        file_size=document.file_size,
        status=document.status,
        upload_date=document.upload_date,
        task_id=task.id
    )


@app.get("/documents", response_model=List[DocumentResponse], tags=["Documents"])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all documents"""
    documents = db.query(Document).order_by(Document.upload_date.desc()).offset(skip).limit(limit).all()
    return documents


@app.get("/documents/{document_id}", response_model=DocumentResponse, tags=["Documents"])
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get document by ID"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@app.delete("/documents/{document_id}", tags=["Documents"])
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete document and its chunks"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file
    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
    
    # Delete database record (chunks will be deleted via cascade)
    db.delete(document)
    db.commit()
    
    logger.info(f"Deleted document: {document_id}")
    return {"message": "Document deleted successfully"}


@app.post("/query", response_model=QueryResponse, tags=["Query"])
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def query_documents(
    request: Request,
    query_request: QueryRequest,
    db: Session = Depends(get_db)
):
    """
    Query documents using RAG
    
    This endpoint:
    1. Generates embedding for the query
    2. Searches for similar chunks in vector database
    3. Constructs context from relevant chunks
    4. Generates response using LLM
    """
    start_time = time.time()
    
    # Check cache first
    if not query_request.stream:
        cached_response = cache_service.get_query_response(query_request.query)
        if cached_response:
            logger.info("Returning cached response")
            return QueryResponse(**cached_response)
    
    # Search for similar chunks
    try:
        results = await vector_db_service.search_similar_chunks(
            db,
            query_request.query,
            top_k=query_request.top_k,
            similarity_threshold=query_request.similarity_threshold
        )
    except Exception as e:
        logger.error(f"Error searching chunks: {e}")
        raise HTTPException(status_code=500, detail="Error searching documents")
    
    if not results:
        raise HTTPException(
            status_code=404,
            detail="No relevant documents found. Try lowering the similarity threshold."
        )
    
    # Construct context from relevant chunks
    context_parts = []
    relevant_chunks = []
    
    for chunk, similarity in results:
        context_parts.append(f"[Document: {chunk.document.filename}]\n{chunk.content}")
        relevant_chunks.append(
            RelevantChunk(
                content=chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                similarity=round(similarity, 4),
                chunk_index=chunk.chunk_index,
                document_id=chunk.document_id,
                filename=chunk.document.filename
            )
        )
    
    context = "\n\n---\n\n".join(context_parts)
    
    # Generate response
    try:
        response_text = await chat_service.generate_completion(
            query=query_request.query,
            context=context
        )
    except Exception as e:
        logger.error(f"Error generating completion: {e}")
        raise HTTPException(status_code=500, detail="Error generating response")
    
    execution_time = time.time() - start_time
    
    # Save query to database
    query_record = Query(
        query_text=query_request.query,
        response=response_text,
        relevant_chunks=[
            {"chunk_id": chunk.id, "similarity": similarity}
            for chunk, similarity in results
        ],
        execution_time=execution_time
    )
    db.add(query_record)
    db.commit()
    
    response_data = {
        "query": query_request.query,
        "response": response_text,
        "relevant_chunks": [chunk.dict() for chunk in relevant_chunks],
        "execution_time": round(execution_time, 3)
    }
    
    # Cache the response
    cache_service.set_query_response(query_request.query, response_data)
    
    logger.info(f"Query processed in {execution_time:.3f}s")
    return QueryResponse(**response_data)


@app.post("/query/stream", tags=["Query"])
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def query_documents_stream(
    request: Request,
    query_request: QueryRequest,
    db: Session = Depends(get_db)
):
    """
    Query documents with streaming response
    """
    # Search for similar chunks
    try:
        results = await vector_db_service.search_similar_chunks(
            db,
            query_request.query,
            top_k=query_request.top_k,
            similarity_threshold=query_request.similarity_threshold
        )
    except Exception as e:
        logger.error(f"Error searching chunks: {e}")
        raise HTTPException(status_code=500, detail="Error searching documents")
    
    if not results:
        raise HTTPException(
            status_code=404,
            detail="No relevant documents found"
        )
    
    # Construct context
    context_parts = []
    for chunk, similarity in results:
        context_parts.append(f"[Document: {chunk.document.filename}]\n{chunk.content}")
    
    context = "\n\n---\n\n".join(context_parts)
    
    # Stream response
    async def generate():
        try:
            async for chunk in chat_service.generate_streaming_completion(
                query=query_request.query,
                context=context
            ):
                yield chunk
        except Exception as e:
            logger.error(f"Error in streaming: {e}")
            yield f"\n\nError: {str(e)}"
    
    return StreamingResponse(generate(), media_type="text/plain")


@app.get("/tasks/{task_id}", response_model=TaskStatusResponse, tags=["Tasks"])
async def get_task_status(task_id: str):
    """Get status of background task"""
    task = celery_app.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            "task_id": task_id,
            "status": "pending",
            "result": None
        }
    elif task.state == 'PROCESSING':
        response = {
            "task_id": task_id,
            "status": "processing",
            "result": task.info
        }
    elif task.state == 'SUCCESS':
        response = {
            "task_id": task_id,
            "status": "completed",
            "result": task.result
        }
    elif task.state == 'FAILURE':
        response = {
            "task_id": task_id,
            "status": "failed",
            "error": str(task.info)
        }
    else:
        response = {
            "task_id": task_id,
            "status": task.state.lower(),
            "result": str(task.info)
        }
    
    return TaskStatusResponse(**response)


@app.get("/stats", response_model=StatsResponse, tags=["Stats"])
async def get_stats(db: Session = Depends(get_db)):
    """Get system statistics"""
    total_documents = db.query(Document).count()
    total_chunks = db.query(DocumentChunk).count()
    total_queries = db.query(Query).count()
    
    cache_stats = cache_service.get_stats()
    
    return StatsResponse(
        total_documents=total_documents,
        total_chunks=total_chunks,
        total_queries=total_queries,
        cache_hit_rate=cache_stats.get("hit_rate", 0.0)
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
