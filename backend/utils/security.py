import os
import hashlib
import secrets
import time
from typing import Dict, Optional, List
from fastapi import HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from collections import defaultdict, deque
import logging

# Rate limiting storage
rate_limit_storage = defaultdict(lambda: deque())

# Security configuration
MAX_LOGIN_ATTEMPTS = 5
MAX_SIGNUP_ATTEMPTS = 3
RATE_LIMIT_WINDOW = 60  # seconds
MAX_REQUESTS_PER_MINUTE = 100

# CORS configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://yourdomain.com",  # Replace with production domain
]

def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks
    """
    if not isinstance(text, str):
        return str(text)
    
    # Remove potentially dangerous characters and patterns
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',  # JavaScript protocol
        r'on\w+\s*=',  # Event handlers
        r'<iframe[^>]*>.*?</iframe>',  # Iframe tags
        r'<object[^>]*>.*?</object>',  # Object tags
        r'<embed[^>]*>.*?</embed>',  # Embed tags
    ]
    
    import re
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove null bytes and control characters
    text = text.replace('\x00', '')
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\t\n\r')
    
    return text.strip()

def hash_password(password: str) -> str:
    """
    Hash password using SHA-256 with salt
    """
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify password against hash
    """
    try:
        salt, password_hash = hashed_password.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except ValueError:
        return False

def generate_secure_token() -> str:
    """
    Generate secure random token
    """
    return secrets.token_urlsafe(32)

def check_rate_limit(request: Request, endpoint: str, max_attempts: int = MAX_REQUESTS_PER_MINUTE) -> bool:
    """
    Check if request exceeds rate limit
    """
    client_ip = get_client_ip(request)
    current_time = time.time()
    
    # Clean old entries
    while rate_limit_storage[client_ip] and rate_limit_storage[client_ip][0] < current_time - RATE_LIMIT_WINDOW:
        rate_limit_storage[client_ip].popleft()
    
    # Check if limit exceeded
    if len(rate_limit_storage[client_ip]) >= max_attempts:
        return False
    
    # Add current request
    rate_limit_storage[client_ip].append(current_time)
    return True

def check_auth_rate_limit(request: Request, endpoint: str) -> bool:
    """
    Check rate limit for authentication endpoints
    """
    max_attempts = MAX_LOGIN_ATTEMPTS if 'login' in endpoint else MAX_SIGNUP_ATTEMPTS
    return check_rate_limit(request, endpoint, max_attempts)

def get_client_ip(request: Request) -> str:
    """
    Get client IP address
    """
    # Check for forwarded IP (behind proxy)
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    
    # Check for real IP
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    # Fallback to direct connection
    return request.client.host if request.client else 'unknown'

def validate_cors_origin(origin: str) -> bool:
    """
    Validate CORS origin
    """
    if not origin:
        return False
    
    # Allow localhost in development
    if origin.startswith('http://localhost:') or origin.startswith('http://127.0.0.1:'):
        return True
    
    # Check against allowed origins
    return origin in ALLOWED_ORIGINS

def setup_cors(app):
    """
    Setup CORS middleware
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
    )

def validate_request_size(request: Request, max_size: int = 1024 * 1024) -> bool:
    """
    Validate request body size (default 1MB)
    """
    content_length = request.headers.get('content-length')
    if content_length:
        return int(content_length) <= max_size
    return True

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal
    """
    import re
    # Remove path traversal attempts
    filename = filename.replace('..', '').replace('/', '').replace('\\', '')
    # Remove dangerous characters
    filename = re.sub(r'[^\w\-_\.]', '', filename)
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    return filename

def validate_json_payload(data: dict, required_fields: List[str]) -> bool:
    """
    Validate JSON payload has required fields
    """
    if not isinstance(data, dict):
        return False
    
    for field in required_fields:
        if field not in data or data[field] is None:
            return False
    
    return True

def log_security_event(event_type: str, details: dict, request: Request = None):
    """
    Log security-related events
    """
    logger = logging.getLogger('security')
    
    log_data = {
        'event_type': event_type,
        'timestamp': time.time(),
        'details': details
    }
    
    if request:
        log_data.update({
            'client_ip': get_client_ip(request),
            'user_agent': request.headers.get('user-agent', ''),
            'endpoint': str(request.url)
        })
    
    logger.warning(f"Security event: {log_data}")

def check_sql_injection_patterns(text: str) -> bool:
    """
    Check for common SQL injection patterns
    """
    if not isinstance(text, str):
        return False
    
    dangerous_patterns = [
        r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
        r'(\b(OR|AND)\s+\d+\s*=\s*\d+)',
        r'(\b(OR|AND)\s+\w+\s*=\s*\w+)',
        r'(;\s*(DROP|DELETE|INSERT|UPDATE))',
        r'(\b(OR|AND)\s+1\s*=\s*1)',
        r'(\b(OR|AND)\s+\'\s*=\s*\')',
        r'(\b(OR|AND)\s+"\s*=\s*")',
    ]
    
    import re
    for pattern in dangerous_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False

def validate_environment_variables():
    """
    Validate required environment variables are set
    """
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'SUPABASE_SERVICE_ROLE_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

def create_security_headers() -> Dict[str, str]:
    """
    Create security headers for responses
    """
    return {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    }

def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware
    """
    # Skip rate limiting for health checks
    if request.url.path == '/health':
        return call_next(request)
    
    # Check rate limit
    if not check_rate_limit(request, request.url.path):
        log_security_event('rate_limit_exceeded', {
            'endpoint': request.url.path,
            'client_ip': get_client_ip(request)
        }, request)
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    response = call_next(request)
    
    # Add security headers
    for header, value in create_security_headers().items():
        response.headers[header] = value
    
    return response

def validate_file_upload(filename: str, content_type: str, max_size: int = 5 * 1024 * 1024) -> bool:
    """
    Validate file upload
    """
    # Check file extension
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.doc', '.docx']
    file_ext = os.path.splitext(filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        return False
    
    # Check content type
    allowed_types = [
        'image/jpeg', 'image/png', 'image/gif',
        'application/pdf', 'text/plain',
        'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    
    if content_type not in allowed_types:
        return False
    
    # Size will be checked by the upload handler
    return True

def generate_csrf_token() -> str:
    """
    Generate CSRF token
    """
    return secrets.token_urlsafe(32)

def validate_csrf_token(token: str, session_token: str) -> bool:
    """
    Validate CSRF token
    """
    return token == session_token and len(token) > 0

# Security decorators
def require_https(func):
    """
    Decorator to require HTTPS
    """
    def wrapper(*args, **kwargs):
        # In production, check if request is HTTPS
        # For development, allow HTTP
        return func(*args, **kwargs)
    return wrapper

def validate_api_key(api_key: str) -> bool:
    """
    Validate API key (if using API keys)
    """
    # This would check against stored API keys
    # For now, return True for development
    return True

def check_permissions(user_role: str, required_permission: str) -> bool:
    """
    Check if user role has required permission
    """
    permissions = {
        'owner': ['read', 'write', 'delete', 'admin'],
        'manager': ['read', 'write'],
        'developer': ['read', 'write_own'],
        'viewer': ['read']
    }
    
    user_permissions = permissions.get(user_role, [])
    return required_permission in user_permissions

def audit_log(action: str, user: str, resource: str, details: dict = None):
    """
    Create audit log entry
    """
    logger = logging.getLogger('audit')
    
    log_entry = {
        'timestamp': time.time(),
        'action': action,
        'user': user,
        'resource': resource,
        'details': details or {}
    }
    
    logger.info(f"Audit: {log_entry}")

# Input validation helpers
def validate_email_domain(email: str, allowed_domains: List[str] = None) -> bool:
    """
    Validate email domain (optional whitelist)
    """
    if not allowed_domains:
        return True
    
    domain = email.split('@')[1].lower()
    return domain in allowed_domains

def validate_password_strength(password: str) -> dict:
    """
    Validate password strength and return details
    """
    result = {
        'is_strong': True,
        'issues': []
    }
    
    if len(password) < 8:
        result['is_strong'] = False
        result['issues'].append('Password must be at least 8 characters')
    
    if not any(c.isupper() for c in password):
        result['is_strong'] = False
        result['issues'].append('Password must contain uppercase letter')
    
    if not any(c.islower() for c in password):
        result['is_strong'] = False
        result['issues'].append('Password must contain lowercase letter')
    
    if not any(c.isdigit() for c in password):
        result['is_strong'] = False
        result['issues'].append('Password must contain number')
    
    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        result['is_strong'] = False
        result['issues'].append('Password must contain special character')
    
    return result
