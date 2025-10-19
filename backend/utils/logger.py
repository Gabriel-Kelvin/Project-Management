import os
import logging
import logging.handlers
from datetime import datetime
from typing import Dict, Any, Optional
import json
import traceback
from pathlib import Path

# Create logs directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'endpoint'):
            log_entry['endpoint'] = record.endpoint
        if hasattr(record, 'client_ip'):
            log_entry['client_ip'] = record.client_ip
        if hasattr(record, 'duration'):
            log_entry['duration'] = record.duration
        
        return json.dumps(log_entry)

class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)

def setup_logging(
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
):
    """
    Setup comprehensive logging configuration
    """
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatters
    console_formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_formatter = JSONFormatter()
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # File handlers
    if log_to_file:
        # Main application log
        app_handler = logging.handlers.RotatingFileHandler(
            LOG_DIR / "app.log",
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        app_handler.setLevel(numeric_level)
        app_handler.setFormatter(file_formatter)
        root_logger.addHandler(app_handler)
        
        # Error log (only errors and above)
        error_handler = logging.handlers.RotatingFileHandler(
            LOG_DIR / "error.log",
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_handler)
        
        # Security log
        security_handler = logging.handlers.RotatingFileHandler(
            LOG_DIR / "security.log",
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        security_handler.setLevel(logging.WARNING)
        security_handler.setFormatter(file_formatter)
        
        security_logger = logging.getLogger('security')
        security_logger.addHandler(security_handler)
        security_logger.setLevel(logging.WARNING)
        security_logger.propagate = False
        
        # Audit log
        audit_handler = logging.handlers.RotatingFileHandler(
            LOG_DIR / "audit.log",
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        audit_handler.setLevel(logging.INFO)
        audit_handler.setFormatter(file_formatter)
        
        audit_logger = logging.getLogger('audit')
        audit_logger.addHandler(audit_handler)
        audit_logger.setLevel(logging.INFO)
        audit_logger.propagate = False
        
        # Performance log
        perf_handler = logging.handlers.RotatingFileHandler(
            LOG_DIR / "performance.log",
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        perf_handler.setLevel(logging.INFO)
        perf_handler.setFormatter(file_formatter)
        
        perf_logger = logging.getLogger('performance')
        perf_logger.addHandler(perf_handler)
        perf_logger.setLevel(logging.INFO)
        perf_logger.propagate = False

def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)

def log_user_action(
    action: str,
    user_id: str,
    details: Dict[str, Any] = None,
    endpoint: str = None,
    client_ip: str = None
):
    """Log user actions"""
    logger = get_logger('audit')
    
    extra = {
        'user_id': user_id,
        'action': action,
        'endpoint': endpoint,
        'client_ip': client_ip
    }
    
    if details:
        extra.update(details)
    
    logger.info(f"User action: {action}", extra=extra)

def log_security_event(
    event_type: str,
    details: Dict[str, Any] = None,
    user_id: str = None,
    client_ip: str = None
):
    """Log security events"""
    logger = get_logger('security')
    
    extra = {
        'event_type': event_type,
        'user_id': user_id,
        'client_ip': client_ip
    }
    
    if details:
        extra.update(details)
    
    logger.warning(f"Security event: {event_type}", extra=extra)

def log_performance(
    operation: str,
    duration: float,
    details: Dict[str, Any] = None,
    endpoint: str = None
):
    """Log performance metrics"""
    logger = get_logger('performance')
    
    extra = {
        'operation': operation,
        'duration': duration,
        'endpoint': endpoint
    }
    
    if details:
        extra.update(details)
    
    logger.info(f"Performance: {operation} took {duration:.3f}s", extra=extra)

def log_api_request(
    method: str,
    endpoint: str,
    user_id: str = None,
    client_ip: str = None,
    status_code: int = None,
    duration: float = None,
    request_size: int = None,
    response_size: int = None
):
    """Log API requests"""
    logger = get_logger('audit')
    
    extra = {
        'method': method,
        'endpoint': endpoint,
        'user_id': user_id,
        'client_ip': client_ip,
        'status_code': status_code,
        'duration': duration,
        'request_size': request_size,
        'response_size': response_size
    }
    
    logger.info(f"API request: {method} {endpoint}", extra=extra)

def log_database_operation(
    operation: str,
    table: str,
    duration: float = None,
    rows_affected: int = None,
    error: str = None
):
    """Log database operations"""
    logger = get_logger('performance')
    
    extra = {
        'operation': operation,
        'table': table,
        'duration': duration,
        'rows_affected': rows_affected,
        'error': error
    }
    
    if error:
        logger.error(f"Database error: {operation} on {table}", extra=extra)
    else:
        logger.info(f"Database operation: {operation} on {table}", extra=extra)

def log_error(
    error: Exception,
    context: Dict[str, Any] = None,
    user_id: str = None,
    endpoint: str = None
):
    """Log errors with full context"""
    logger = get_logger('error')
    
    extra = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'user_id': user_id,
        'endpoint': endpoint,
        'traceback': traceback.format_exc()
    }
    
    if context:
        extra.update(context)
    
    logger.error(f"Error: {type(error).__name__}: {str(error)}", extra=extra)

def log_startup():
    """Log application startup"""
    logger = get_logger('app')
    logger.info("Application starting up")
    logger.info(f"Log directory: {LOG_DIR.absolute()}")
    logger.info(f"Python version: {os.sys.version}")

def log_shutdown():
    """Log application shutdown"""
    logger = get_logger('app')
    logger.info("Application shutting down")

def log_configuration(config: Dict[str, Any]):
    """Log configuration (without sensitive data)"""
    logger = get_logger('app')
    
    # Remove sensitive configuration
    safe_config = {}
    sensitive_keys = ['password', 'secret', 'key', 'token', 'auth']
    
    for key, value in config.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            safe_config[key] = '***REDACTED***'
        else:
            safe_config[key] = value
    
    logger.info(f"Configuration loaded: {safe_config}")

# Context managers for logging
class LogContext:
    """Context manager for logging operations"""
    
    def __init__(self, operation: str, logger: logging.Logger = None, **context):
        self.operation = operation
        self.logger = logger or get_logger('app')
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"Starting {self.operation}", extra=self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type:
            self.logger.error(
                f"Error in {self.operation}: {exc_val}",
                extra={**self.context, 'duration': duration, 'error': str(exc_val)}
            )
        else:
            self.logger.info(
                f"Completed {self.operation}",
                extra={**self.context, 'duration': duration}
            )

# Decorator for logging function execution
def log_execution(operation: str = None, logger: logging.Logger = None):
    """Decorator to log function execution"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            op_name = operation or f"{func.__module__}.{func.__name__}"
            log = logger or get_logger('app')
            
            with LogContext(op_name, log):
                return func(*args, **kwargs)
        return wrapper
    return decorator

# Utility functions
def get_log_stats() -> Dict[str, Any]:
    """Get logging statistics"""
    stats = {
        'log_files': [],
        'total_size': 0
    }
    
    for log_file in LOG_DIR.glob("*.log*"):
        file_size = log_file.stat().st_size
        stats['log_files'].append({
            'name': log_file.name,
            'size': file_size,
            'size_mb': round(file_size / (1024 * 1024), 2)
        })
        stats['total_size'] += file_size
    
    stats['total_size_mb'] = round(stats['total_size'] / (1024 * 1024), 2)
    return stats

def cleanup_old_logs(days_to_keep: int = 30):
    """Clean up old log files"""
    import time
    cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
    
    cleaned_files = []
    for log_file in LOG_DIR.glob("*.log*"):
        if log_file.stat().st_mtime < cutoff_time:
            log_file.unlink()
            cleaned_files.append(log_file.name)
    
    if cleaned_files:
        logger = get_logger('app')
        logger.info(f"Cleaned up old log files: {cleaned_files}")
    
    return cleaned_files

# Initialize logging on import
if __name__ != "__main__":
    # Only setup logging if not being run directly
    setup_logging()