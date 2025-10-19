"""
Production configuration for the Project Management API
"""
import os
from typing import List

# Environment
DEBUG = False
ENVIRONMENT = "production"

# Database Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# CORS Configuration
CORS_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
    "https://app.yourdomain.com"
]

# Rate Limiting
RATE_LIMIT_ENABLED = True
MAX_REQUESTS_PER_MINUTE = 100
MAX_LOGIN_ATTEMPTS = 5
MAX_SIGNUP_ATTEMPTS = 3

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_TO_FILE = True
LOG_TO_CONSOLE = True
LOG_FILE_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_FILE_BACKUP_COUNT = 5

# Performance Configuration
CACHE_ENABLED = True
CACHE_TTL = 300  # 5 minutes
MAX_CACHE_SIZE = 1000
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 30

# Email Configuration (if using email notifications)
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_USE_TLS = True

# File Upload Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = [
    "image/jpeg",
    "image/png",
    "image/gif",
    "application/pdf",
    "text/plain",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
]

# Redis Configuration (if using Redis for caching)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Monitoring and Analytics
SENTRY_DSN = os.getenv("SENTRY_DSN")
ENABLE_METRICS = True
METRICS_PORT = 9090

# API Configuration
API_V1_STR = "/api/v1"
PROJECT_NAME = "Project Management API"
VERSION = "1.0.0"
DESCRIPTION = "A comprehensive project management API"

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Validation
MAX_USERNAME_LENGTH = 20
MIN_USERNAME_LENGTH = 3
MAX_EMAIL_LENGTH = 254
MIN_PASSWORD_LENGTH = 6
MAX_PROJECT_NAME_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 500
MAX_TASK_TITLE_LENGTH = 150

# Security Headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
}

# Health Check Configuration
HEALTH_CHECK_ENABLED = True
HEALTH_CHECK_INTERVAL = 30  # seconds

# Backup Configuration
BACKUP_ENABLED = True
BACKUP_INTERVAL = 24  # hours
BACKUP_RETENTION_DAYS = 30

# Feature Flags
FEATURE_FLAGS = {
    "analytics": True,
    "file_uploads": True,
    "email_notifications": True,
    "real_time_updates": True,
    "advanced_search": True,
    "export_functionality": True
}

# Performance Monitoring
PERFORMANCE_MONITORING = {
    "enabled": True,
    "sample_rate": 0.1,  # 10% of requests
    "slow_query_threshold": 1.0,  # seconds
    "memory_threshold": 0.8,  # 80% memory usage
    "cpu_threshold": 0.8  # 80% CPU usage
}

# Error Handling
ERROR_HANDLING = {
    "detailed_errors": False,  # Don't expose internal errors in production
    "log_errors": True,
    "notify_admins": True,
    "admin_emails": os.getenv("ADMIN_EMAILS", "").split(",")
}

# Database Optimization
DATABASE_OPTIMIZATION = {
    "connection_pooling": True,
    "query_timeout": 30,  # seconds
    "max_connections": 100,
    "statement_timeout": 30,  # seconds
    "idle_in_transaction_session_timeout": 60  # seconds
}

# Cache Configuration
CACHE_CONFIG = {
    "default_ttl": 300,  # 5 minutes
    "max_size": 1000,
    "cleanup_interval": 600,  # 10 minutes
    "compression": True
}

# Session Configuration
SESSION_CONFIG = {
    "cookie_name": "pm_session",
    "cookie_secure": True,
    "cookie_httponly": True,
    "cookie_samesite": "strict",
    "max_age": 86400  # 24 hours
}

# API Documentation
API_DOCS = {
    "enabled": True,
    "title": "Project Management API",
    "description": "A comprehensive project management API",
    "version": "1.0.0",
    "contact": {
        "name": "API Support",
        "email": "support@yourdomain.com"
    },
    "license": {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
}

# WebSocket Configuration (if using real-time features)
WEBSOCKET_CONFIG = {
    "enabled": True,
    "ping_interval": 25,  # seconds
    "ping_timeout": 60,  # seconds
    "max_connections": 1000
}

# Background Tasks
BACKGROUND_TASKS = {
    "enabled": True,
    "max_workers": 4,
    "queue_size": 1000,
    "task_timeout": 300  # 5 minutes
}

# Data Retention
DATA_RETENTION = {
    "user_data": 365,  # days
    "project_data": 1095,  # 3 years
    "task_data": 1095,  # 3 years
    "audit_logs": 2555,  # 7 years
    "error_logs": 90  # days
}

# Compliance
COMPLIANCE = {
    "gdpr_enabled": True,
    "data_encryption": True,
    "audit_logging": True,
    "data_anonymization": True,
    "right_to_deletion": True
}

# Load Balancing
LOAD_BALANCING = {
    "enabled": True,
    "health_check_path": "/health",
    "sticky_sessions": False,
    "session_affinity": False
}

# SSL/TLS Configuration
SSL_CONFIG = {
    "enabled": True,
    "cert_file": os.getenv("SSL_CERT_FILE"),
    "key_file": os.getenv("SSL_KEY_FILE"),
    "redirect_http": True,
    "hsts_max_age": 31536000  # 1 year
}

# Environment-specific overrides
if os.getenv("ENVIRONMENT") == "staging":
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    CORS_ORIGINS.extend([
        "https://staging.yourdomain.com",
        "http://localhost:3000"
    ])

# Validation
def validate_config():
    """Validate required configuration"""
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "SUPABASE_SERVICE_ROLE_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Validate URLs
    if not SUPABASE_URL.startswith("https://"):
        raise ValueError("SUPABASE_URL must use HTTPS in production")
    
    # Validate CORS origins
    for origin in CORS_ORIGINS:
        if not origin.startswith("https://"):
            raise ValueError(f"CORS origin must use HTTPS in production: {origin}")

# Run validation on import
validate_config()
