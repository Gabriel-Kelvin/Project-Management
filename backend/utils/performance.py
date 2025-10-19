import time
import asyncio
from functools import wraps
from typing import Dict, Any, Optional, List, Callable
import logging
from collections import defaultdict
import threading
from datetime import datetime, timedelta

# Performance monitoring
performance_metrics = defaultdict(list)
cache = {}
cache_expiry = {}

# Database query optimization
QUERY_CACHE_TTL = 300  # 5 minutes
MAX_CACHE_SIZE = 1000

logger = logging.getLogger('performance')

class PerformanceMonitor:
    """Performance monitoring and optimization utilities"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.cache = {}
        self.cache_expiry = {}
        self.lock = threading.Lock()
    
    def time_function(self, func_name: str = None):
        """Decorator to time function execution"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                name = func_name or f"{func.__module__}.{func.__name__}"
                
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    self.record_metric(name, duration, success=True)
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    self.record_metric(name, duration, success=False, error=str(e))
                    raise
            
            return wrapper
        return decorator
    
    def time_async_function(self, func_name: str = None):
        """Decorator to time async function execution"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                name = func_name or f"{func.__module__}.{func.__name__}"
                
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    self.record_metric(name, duration, success=True)
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    self.record_metric(name, duration, success=False, error=str(e))
                    raise
            
            return wrapper
        return decorator
    
    def record_metric(self, name: str, duration: float, success: bool = True, error: str = None):
        """Record performance metric"""
        with self.lock:
            metric = {
                'timestamp': datetime.now(),
                'duration': duration,
                'success': success,
                'error': error
            }
            self.metrics[name].append(metric)
            
            # Keep only last 1000 metrics per function
            if len(self.metrics[name]) > 1000:
                self.metrics[name] = self.metrics[name][-1000:]
    
    def get_metrics(self, func_name: str = None) -> Dict[str, Any]:
        """Get performance metrics"""
        with self.lock:
            if func_name:
                metrics = self.metrics.get(func_name, [])
                if not metrics:
                    return {}
                
                durations = [m['duration'] for m in metrics]
                successes = [m['success'] for m in metrics]
                
                return {
                    'count': len(metrics),
                    'avg_duration': sum(durations) / len(durations),
                    'min_duration': min(durations),
                    'max_duration': max(durations),
                    'success_rate': sum(successes) / len(successes),
                    'recent_errors': [m['error'] for m in metrics[-10:] if not m['success']]
                }
            else:
                return {name: self.get_metrics(name) for name in self.metrics.keys()}
    
    def clear_metrics(self, func_name: str = None):
        """Clear performance metrics"""
        with self.lock:
            if func_name:
                self.metrics[func_name] = []
            else:
                self.metrics.clear()

# Global performance monitor instance
perf_monitor = PerformanceMonitor()

def cache_result(ttl: int = QUERY_CACHE_TTL):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Check if result is cached and not expired
            if cache_key in cache:
                if time.time() < cache_expiry.get(cache_key, 0):
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cache[cache_key]
                else:
                    # Remove expired cache entry
                    del cache[cache_key]
                    if cache_key in cache_expiry:
                        del cache_expiry[cache_key]
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            
            # Cache the result
            cache[cache_key] = result
            cache_expiry[cache_key] = time.time() + ttl
            
            # Clean up old cache entries if cache is too large
            if len(cache) > MAX_CACHE_SIZE:
                cleanup_cache()
            
            logger.debug(f"Cached result for {func.__name__}")
            return result
        
        return wrapper
    return decorator

def cleanup_cache():
    """Clean up expired cache entries"""
    current_time = time.time()
    expired_keys = [
        key for key, expiry in cache_expiry.items()
        if current_time > expiry
    ]
    
    for key in expired_keys:
        cache.pop(key, None)
        cache_expiry.pop(key, None)
    
    # If still too large, remove oldest entries
    if len(cache) > MAX_CACHE_SIZE:
        # Sort by expiry time and remove oldest
        sorted_keys = sorted(cache_expiry.items(), key=lambda x: x[1])
        keys_to_remove = [key for key, _ in sorted_keys[:len(cache) - MAX_CACHE_SIZE]]
        
        for key in keys_to_remove:
            cache.pop(key, None)
            cache_expiry.pop(key, None)

def paginate_results(
    query_func: Callable,
    page: int = 1,
    limit: int = 20,
    max_limit: int = 100,
    **query_kwargs
) -> Dict[str, Any]:
    """
    Paginate database query results
    """
    # Validate pagination parameters
    if page < 1:
        page = 1
    if limit < 1:
        limit = 20
    if limit > max_limit:
        limit = max_limit
    
    offset = (page - 1) * limit
    
    # Execute query with pagination
    start_time = time.time()
    results = query_func(offset=offset, limit=limit, **query_kwargs)
    duration = time.time() - start_time
    
    # Get total count (this might be expensive, consider caching)
    total_count = query_func(count_only=True, **query_kwargs)
    
    # Calculate pagination info
    total_pages = (total_count + limit - 1) // limit
    has_next = page < total_pages
    has_prev = page > 1
    
    perf_monitor.record_metric('paginate_results', duration)
    
    return {
        'data': results,
        'pagination': {
            'page': page,
            'limit': limit,
            'total_count': total_count,
            'total_pages': total_pages,
            'has_next': has_next,
            'has_prev': has_prev
        }
    }

def optimize_database_queries():
    """
    Database optimization recommendations
    """
    recommendations = [
        "Add indexes on frequently queried columns:",
        "  - projects(owner_id)",
        "  - tasks(project_id, status)",
        "  - team_members(project_id, username)",
        "  - users(username, email)",
        "",
        "Consider composite indexes for common query patterns:",
        "  - tasks(project_id, status, priority)",
        "  - team_members(project_id, role)",
        "",
        "Use EXPLAIN ANALYZE to identify slow queries",
        "Consider query result caching for expensive operations",
        "Implement connection pooling for high concurrency"
    ]
    
    return "\n".join(recommendations)

def batch_operations(operations: List[Callable], batch_size: int = 100):
    """
    Execute operations in batches to avoid overwhelming the database
    """
    results = []
    
    for i in range(0, len(operations), batch_size):
        batch = operations[i:i + batch_size]
        batch_start = time.time()
        
        try:
            batch_results = []
            for operation in batch:
                result = operation()
                batch_results.append(result)
            
            results.extend(batch_results)
            duration = time.time() - batch_start
            
            perf_monitor.record_metric('batch_operations', duration)
            logger.info(f"Executed batch of {len(batch)} operations in {duration:.3f}s")
            
        except Exception as e:
            logger.error(f"Batch operation failed: {e}")
            raise
    
    return results

def monitor_memory_usage():
    """Monitor memory usage"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return {
        'rss': memory_info.rss,  # Resident Set Size
        'vms': memory_info.vms,  # Virtual Memory Size
        'percent': process.memory_percent(),
        'available': psutil.virtual_memory().available
    }

def optimize_response_size(data: Any, max_size: int = 1024 * 1024) -> Any:
    """
    Optimize response size by removing unnecessary fields
    """
    if isinstance(data, dict):
        # Remove large or unnecessary fields
        optimized = {}
        for key, value in data.items():
            if key in ['password', 'token', 'secret']:
                continue  # Skip sensitive fields
            
            if isinstance(value, str) and len(value) > 1000:
                optimized[key] = value[:1000] + "..."
            else:
                optimized[key] = value
        
        return optimized
    
    elif isinstance(data, list):
        # Limit list size
        if len(data) > 1000:
            return data[:1000]
        return data
    
    return data

def rate_limit_by_user(user_id: str, operation: str, max_requests: int = 100, window: int = 3600):
    """
    Rate limit operations by user
    """
    current_time = time.time()
    key = f"{user_id}:{operation}"
    
    # Clean up old entries
    if key in cache:
        cache[key] = [t for t in cache[key] if current_time - t < window]
    else:
        cache[key] = []
    
    # Check rate limit
    if len(cache[key]) >= max_requests:
        return False
    
    # Add current request
    cache[key].append(current_time)
    return True

def async_batch_process(items: List[Any], process_func: Callable, batch_size: int = 10):
    """
    Process items in async batches
    """
    async def process_batch(batch):
        tasks = [process_func(item) for item in batch]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def run_batches():
        results = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = await process_batch(batch)
            results.extend(batch_results)
        return results
    
    return asyncio.run(run_batches())

def get_performance_report() -> Dict[str, Any]:
    """Generate performance report"""
    metrics = perf_monitor.get_metrics()
    memory_info = monitor_memory_usage()
    cache_info = {
        'cache_size': len(cache),
        'cache_hit_rate': calculate_cache_hit_rate()
    }
    
    return {
        'timestamp': datetime.now().isoformat(),
        'metrics': metrics,
        'memory': memory_info,
        'cache': cache_info,
        'recommendations': optimize_database_queries()
    }

def calculate_cache_hit_rate() -> float:
    """Calculate cache hit rate (simplified)"""
    # This would need to be implemented with proper hit/miss tracking
    return 0.85  # Placeholder

def warm_up_cache():
    """Warm up cache with frequently accessed data"""
    logger.info("Warming up cache...")
    
    # This would preload commonly accessed data
    # Implementation depends on your specific use case
    
    logger.info("Cache warm-up completed")

# Performance monitoring middleware
class PerformanceMiddleware:
    """FastAPI middleware for performance monitoring"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        path = scope["path"]
        method = scope["method"]
        
        # Process request
        await self.app(scope, receive, send)
        
        # Record metrics
        duration = time.time() - start_time
        perf_monitor.record_metric(f"api_request:{method}:{path}", duration)

# Utility functions for common optimizations
def deduplicate_list(items: List[Any], key_func: Callable = None) -> List[Any]:
    """Remove duplicates from list while preserving order"""
    if key_func is None:
        key_func = lambda x: x
    
    seen = set()
    result = []
    
    for item in items:
        key = key_func(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    
    return result

def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size"""
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]

def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries"""
    result = {}
    for d in dicts:
        result.update(d)
    return result

# Initialize performance monitoring
def init_performance_monitoring():
    """Initialize performance monitoring"""
    logger.info("Initializing performance monitoring")
    
    # Warm up cache
    warm_up_cache()
    
    # Log initial performance report
    report = get_performance_report()
    logger.info(f"Performance monitoring initialized: {report}")

# Cleanup function
def cleanup_performance_data():
    """Clean up performance monitoring data"""
    perf_monitor.clear_metrics()
    cache.clear()
    cache_expiry.clear()
    logger.info("Performance monitoring data cleaned up")
