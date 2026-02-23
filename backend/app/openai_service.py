from openai import OpenAI
from typing import List, Optional, AsyncGenerator
import tiktoken
from app.config import settings
from app.cache import cache_service
from loguru import logger

client = OpenAI(api_key=settings.OPENAI_API_KEY)


class EmbeddingService:
    """Service for generating embeddings using OpenAI"""
    
    def __init__(self):
        self.model = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION
        self.encoding = tiktoken.encoding_for_model(self.model)
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
    async def get_embedding(self, text: str, use_cache: bool = True) -> List[float]:
        """Get embedding for text with optional caching"""
        # Check cache first
        if use_cache:
            cached_embedding = cache_service.get_embedding(text)
            if cached_embedding:
                return cached_embedding
        
        try:
            # Generate embedding
            response = client.embeddings.create(
                input=text,
                model=self.model
            )
            embedding = response.data[0].embedding
            
            # Cache the embedding
            if use_cache:
                cache_service.set_embedding(text, embedding)
            
            logger.debug(f"Generated embedding for text ({self.count_tokens(text)} tokens)")
            return embedding
        
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    async def get_embeddings_batch(self, texts: List[str], use_cache: bool = True) -> List[List[float]]:
        """Get embeddings for multiple texts"""
        embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        # Check cache for each text
        if use_cache:
            for i, text in enumerate(texts):
                cached = cache_service.get_embedding(text)
                if cached:
                    embeddings.append(cached)
                else:
                    embeddings.append(None)
                    uncached_texts.append(text)
                    uncached_indices.append(i)
        else:
            uncached_texts = texts
            uncached_indices = list(range(len(texts)))
            embeddings = [None] * len(texts)
        
        # Generate embeddings for uncached texts
        if uncached_texts:
            try:
                response = client.embeddings.create(
                    input=uncached_texts,
                    model=self.model
                )
                
                # Fill in the uncached embeddings
                for i, embedding_data in enumerate(response.data):
                    embedding = embedding_data.embedding
                    idx = uncached_indices[i]
                    embeddings[idx] = embedding
                    
                    # Cache the embedding
                    if use_cache:
                        cache_service.set_embedding(uncached_texts[i], embedding)
                
                logger.info(f"Generated {len(uncached_texts)} embeddings")
            
            except Exception as e:
                logger.error(f"Error generating batch embeddings: {e}")
                raise
        
        return embeddings


class ChatService:
    """Service for chat completions using OpenAI"""
    
    def __init__(self):
        self.model = settings.CHAT_MODEL
    
    async def generate_completion(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate completion based on query and context"""
        
        if system_prompt is None:
            system_prompt = (
                "You are a helpful AI assistant that answers questions based on the provided context. "
                "If the context doesn't contain enough information to answer the question, "
                "say so honestly. Always cite relevant information from the context."
            )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ]
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            raise
    
    async def generate_streaming_completion(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> AsyncGenerator[str, None]:
        """Generate streaming completion"""
        
        if system_prompt is None:
            system_prompt = (
                "You are a helpful AI assistant that answers questions based on the provided context. "
                "If the context doesn't contain enough information to answer the question, "
                "say so honestly. Always cite relevant information from the context."
            )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ]
        
        try:
            stream = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            logger.error(f"Error generating streaming completion: {e}")
            raise


embedding_service = EmbeddingService()
chat_service = ChatService()
