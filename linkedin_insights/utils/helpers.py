"""
Helper utilities and common functions
Shared utility functions across the application
"""
from datetime import datetime
from typing import Any, Dict


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO string"""
    return dt.isoformat()


def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values from dictionary"""
    return {k: v for k, v in data.items() if v is not None}

