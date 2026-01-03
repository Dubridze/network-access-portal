from datetime import datetime, timedelta
import uuid
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def generate_request_number() -> str:
    """Generate unique request number"""
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    unique_id = str(uuid.uuid4()).split('-')[0].upper()
    return f"REQ-{timestamp}-{unique_id}"


def format_timestamp(dt: Optional[datetime]) -> Optional[str]:
    """Format datetime to ISO format string"""
    if dt:
        return dt.isoformat()
    return None


def get_ip_from_request(request) -> str:
    """Extract client IP from request"""
    if request.client:
        return request.client.host
    return "unknown"


def get_user_agent(request) -> str:
    """Extract user agent from request"""
    return request.headers.get("user-agent", "unknown")
