from celery import Celery
from app.config import settings
from app.database import SessionLocal
from app.models import Document
from app.document_processor import document_processor
from app.vector_db import vector_db_service
from datetime import datetime
from loguru import logger
import asyncio

# Initialize Celery
celery_app = Celery(
    "rag_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)


@celery_app.task(bind=True, name="process_document")
def process_document_task(self, document_id: int):
    """
    Background task to process uploaded document
    
    Steps:
    1. Extract text from document
    2. Chunk the text
    3. Generate embeddings
    4. Store in vector database
    """
    db = SessionLocal()
    try:
        # Update task status
        self.update_state(state='PROCESSING', meta={'status': 'Starting document processing'})
        
        # Get document from database
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        logger.info(f"Processing document: {document.filename}")
        
        # Update document status
        document.status = "processing"
        db.commit()
        
        # Step 1: Extract text
        self.update_state(state='PROCESSING', meta={'status': 'Extracting text'})
        text = document_processor.process_file(document.file_path)
        
        if not text:
            raise ValueError("No text extracted from document")
        
        # Step 2: Chunk text
        self.update_state(state='PROCESSING', meta={'status': 'Chunking text'})
        chunks = document_processor.chunk_text(
            text,
            metadata={
                "filename": document.filename,
                "document_id": document_id
            }
        )
        
        # Step 3 & 4: Generate embeddings and store
        self.update_state(state='PROCESSING', meta={'status': 'Generating embeddings'})
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        chunk_count = loop.run_until_complete(
            vector_db_service.add_chunks_to_db(db, document_id, chunks)
        )
        loop.close()
        
        # Update document status
        document.status = "completed"
        document.processed_at = datetime.utcnow()
        document.metadata = {
            "text_length": len(text),
            "chunk_count": chunk_count
        }
        db.commit()
        
        logger.info(f"Successfully processed document {document_id}: {chunk_count} chunks")
        
        return {
            "status": "success",
            "document_id": document_id,
            "chunk_count": chunk_count
        }
    
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {e}")
        
        # Update document status to failed
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = "failed"
            document.metadata = {"error": str(e)}
            db.commit()
        
        raise
    
    finally:
        db.close()


@celery_app.task(name="cleanup_old_documents")
def cleanup_old_documents():
    """Periodic task to cleanup old documents"""
    # Implement cleanup logic here
    logger.info("Running cleanup task")
    return {"status": "completed"}
