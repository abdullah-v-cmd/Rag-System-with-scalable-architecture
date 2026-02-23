from typing import List, Tuple, Optional
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import DocumentChunk
from app.openai_service import embedding_service
from loguru import logger


class VectorDBService:
    """Service for vector similarity search using pgvector"""
    
    async def search_similar_chunks(
        self,
        db: Session,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Search for similar chunks using cosine similarity
        
        Args:
            db: Database session
            query: Query text
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score (0-1)
        
        Returns:
            List of (chunk, similarity_score) tuples
        """
        try:
            # Generate embedding for query
            query_embedding = await embedding_service.get_embedding(query)
            
            # Convert to string format for SQL
            embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
            
            # Execute similarity search using pgvector's cosine similarity
            sql = text("""
                SELECT 
                    id,
                    document_id,
                    chunk_index,
                    content,
                    metadata,
                    1 - (embedding <=> :query_embedding::vector) as similarity
                FROM document_chunks
                WHERE 1 - (embedding <=> :query_embedding::vector) >= :threshold
                ORDER BY embedding <=> :query_embedding::vector
                LIMIT :limit
            """)
            
            result = db.execute(
                sql,
                {
                    "query_embedding": embedding_str,
                    "threshold": similarity_threshold,
                    "limit": top_k
                }
            )
            
            results = []
            for row in result:
                # Fetch the complete chunk object
                chunk = db.query(DocumentChunk).filter(DocumentChunk.id == row.id).first()
                if chunk:
                    results.append((chunk, float(row.similarity)))
            
            logger.info(f"Found {len(results)} similar chunks for query")
            return results
        
        except Exception as e:
            logger.error(f"Error searching similar chunks: {e}")
            raise
    
    async def add_chunks_to_db(
        self,
        db: Session,
        document_id: int,
        chunks: List[dict]
    ) -> int:
        """
        Add document chunks with embeddings to database
        
        Args:
            db: Database session
            document_id: ID of the parent document
            chunks: List of chunk dictionaries
        
        Returns:
            Number of chunks added
        """
        try:
            # Extract text from chunks
            texts = [chunk["content"] for chunk in chunks]
            
            # Generate embeddings in batch
            embeddings = await embedding_service.get_embeddings_batch(texts)
            
            # Create chunk objects
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                db_chunk = DocumentChunk(
                    document_id=document_id,
                    chunk_index=chunk["chunk_index"],
                    content=chunk["content"],
                    embedding=embedding,
                    metadata=chunk.get("metadata", {})
                )
                db.add(db_chunk)
            
            db.commit()
            logger.info(f"Added {len(chunks)} chunks to database for document {document_id}")
            return len(chunks)
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error adding chunks to database: {e}")
            raise


vector_db_service = VectorDBService()
