from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    status: str
    upload_date: datetime
    task_id: Optional[str] = None


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    file_type: str
    status: str
    upload_date: datetime
    processed_at: Optional[datetime] = None
    metadata: Optional[dict] = None
    
    class Config:
        from_attributes = True


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    stream: bool = Field(default=False)


class RelevantChunk(BaseModel):
    content: str
    similarity: float
    chunk_index: int
    document_id: int
    filename: str


class QueryResponse(BaseModel):
    query: str
    response: str
    relevant_chunks: List[RelevantChunk]
    execution_time: float


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    redis: str
    cache_stats: dict


class StatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    total_queries: int
    cache_hit_rate: float
