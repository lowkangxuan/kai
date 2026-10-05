from slowapi import Limiter
from slowapi.util import get_remote_address
from app.settings import settings

# Initialize limiter based on client IP
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL.get_secret_value(),
)

# A constant key makes every visitor share this quota.
daily_budget = limiter.shared_limit(
    "30/day", # 30 for now, shall modify when more people use it
    scope="kai-generation",
    key_func=lambda: "all-visitors",
    error_message="Kai has reached its daily limit. Please try again later.",
)