import redis
import json
import hashlib
from typing import Optional, Any
from app.config import settings
from loguru import logger

# Initialize Redis client
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


class CacheService:
    """Service for caching embeddings and responses"""
    
    def __init__(self):
        self.client = redis_client
        self.default_ttl = 3600  # 1 hour
    
    def _generate_key(self, prefix: str, data: str) -> str:
        """Generate cache key using hash"""
        hash_value = hashlib.md5(data.encode()).hexdigest()
        return f"{prefix}:{hash_value}"
    
    def get_embedding(self, text: str) -> Optional[list]:
        """Get cached embedding for text"""
        key = self._generate_key("embedding", text)
        try:
            cached = self.client.get(key)
            if cached:
                logger.debug(f"Cache HIT for embedding: {key}")
                return json.loads(cached)
            logger.debug(f"Cache MISS for embedding: {key}")
            return None
        except Exception as e:
            logger.error(f"Error getting cached embedding: {e}")
            return None
    
    def set_embedding(self, text: str, embedding: list, ttl: Optional[int] = None):
        """Cache embedding for text"""
        key = self._generate_key("embedding", text)
        try:
            ttl = ttl or self.default_ttl
            self.client.setex(key, ttl, json.dumps(embedding))
            logger.debug(f"Cached embedding: {key}")
        except Exception as e:
            logger.error(f"Error caching embedding: {e}")
    
    def get_query_response(self, query: str) -> Optional[dict]:
        """Get cached query response"""
        key = self._generate_key("query", query)
        try:
            cached = self.client.get(key)
            if cached:
                logger.info(f"Cache HIT for query: {query[:50]}...")
                return json.loads(cached)
            logger.info(f"Cache MISS for query: {query[:50]}...")
            return None
        except Exception as e:
            logger.error(f"Error getting cached query: {e}")
            return None
    
    def set_query_response(self, query: str, response: dict, ttl: Optional[int] = None):
        """Cache query response"""
        key = self._generate_key("query", query)
        try:
            ttl = ttl or self.default_ttl
            self.client.setex(key, ttl, json.dumps(response))
            logger.info(f"Cached query response: {query[:50]}...")
        except Exception as e:
            logger.error(f"Error caching query response: {e}")
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern"""
        try:
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} keys matching pattern: {pattern}")
        except Exception as e:
            logger.error(f"Error invalidating cache pattern: {e}")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        try:
            info = self.client.info("stats")
            return {
                "total_keys": self.client.dbsize(),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info)
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
    
    def _calculate_hit_rate(self, info: dict) -> float:
        """Calculate cache hit rate"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        return round(hits / total * 100, 2) if total > 0 else 0.0


cache_service = CacheService()
