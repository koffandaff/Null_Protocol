"""
Cache management service for scan results
"""
import time
import json
from typing import Dict, Optional, List, Any
from datetime import datetime

from utils.cache_tools import cache_tools
from model.Auth_Model import db
from config.settings import settings

class CacheService:
    def __init__(self):
        self.db = db
    
    def get_cache_stats(self, user_id: str) -> Dict:
        """Get cache statistics"""
        # Check if user has admin access
        user = self.db.get_userby_id(user_id)
        if not user or user.get('role') != 'admin':
            raise ValueError("Admin access required")
        
        return cache_tools.get_stats()
    
    def clear_cache(self, user_id: str, cache_type: str = None) -> Dict:
        """Clear cache entries"""
        # Check if user has admin access
        user = self.db.get_userby_id(user_id)
        if not user or user.get('role') != 'admin':
            raise ValueError("Admin access required")
        
        result = cache_tools.clear(cache_type)
        
        # Log activity
        self.db.log_activity(
            user_id=user_id,
            action="cache_clear",
            details={
                'cache_type': cache_type or 'all',
                'entries_cleared': result['cleared']
            }
        )
        
        return result
    
    def get_cache_entries(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get cache entries for inspection"""
        # Check if user has admin access
        user = self.db.get_userby_id(user_id)
        if not user or user.get('role') != 'admin':
            raise ValueError("Admin access required")
        
        return cache_tools.get_entries(limit)
    
    def cache_scan_result(self, scan_type: str, target: str, params: Dict, result: Dict) -> str:
        """Cache a scan result"""
        cache_key = cache_tools.get_key(scan_type, target, params)
        cache_tools.set(cache_key, result)
        return cache_key
    
    def get_cached_result(self, scan_type: str, target: str, params: Dict = None) -> Optional[Dict]:
        """Get cached scan result"""
        cache_key = cache_tools.get_key(scan_type, target, params)
        cached = cache_tools.get(cache_key)
        
        if cached:
            cached['cache_hit'] = True
            cached['cache_key'] = cache_key
            return cached
        
        return None
    
    def invalidate_cache(self, pattern: str = None) -> Dict:
        """Invalidate cache entries matching pattern"""
        if not pattern:
            return cache_tools.clear()
        
        # Get all cache entries
        entries = cache_tools.get_entries(limit=1000)
        cleared = 0
        
        for entry in entries:
            if pattern in entry['key']:
                if cache_tools.delete(entry['key']):
                    cleared += 1
        
        return {
            'cleared': cleared,
            'pattern': pattern,
            'message': f'Cleared {cleared} cache entries matching pattern: {pattern}'
        }
    
    def get_cache_performance(self) -> Dict:
        """Get cache performance metrics"""
        stats = cache_tools.get_stats()
        
        # Calculate cache efficiency
        hit_rate = stats.get('hit_rate', 0)
        efficiency = "Excellent" if hit_rate > 0.8 else "Good" if hit_rate > 0.5 else "Poor"
        
        # Memory usage analysis
        memory_bytes = stats.get('memory_bytes', 0)
        memory_mb = memory_bytes / (1024 * 1024)
        memory_status = "Low" if memory_mb < 10 else "Moderate" if memory_mb < 50 else "High"
        
        return {
            'stats': stats,
            'analysis': {
                'efficiency': efficiency,
                'hit_rate_percentage': round(hit_rate * 100, 1),
                'memory_usage_mb': round(memory_mb, 2),
                'memory_status': memory_status,
                'cache_enabled': settings.CACHE_ENABLED,
                'recommendation': self._get_cache_recommendation(stats)
            }
        }
    
    def _get_cache_recommendation(self, stats: Dict) -> str:
        """Get cache optimization recommendations"""
        hit_rate = stats.get('hit_rate', 0)
        size_percentage = stats.get('size_percentage', 0)
        
        recommendations = []
        
        if hit_rate < 0.3:
            recommendations.append("Consider disabling cache as hit rate is low")
        
        if size_percentage > 80:
            recommendations.append("Cache is nearly full, consider increasing max_size")
        
        if stats.get('total_entries', 0) > 500 and stats.get('ttl_seconds', 3600) > 7200:
            recommendations.append("Consider reducing TTL for better cache freshness")
        
        return "; ".join(recommendations) if recommendations else "Cache settings are optimal"

# Global instance
cache_service = CacheService()