from ipaddress import ip_address

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.settings import settings


def get_client_ip(request: Request) -> str:
    if settings.TRUST_RAILWAY_PROXY:
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            try:
                return str(ip_address(real_ip.strip()))
            except ValueError:
                pass

    return get_remote_address(request)


limiter = Limiter(
    key_func=get_client_ip,
    storage_uri=settings.REDIS_URL.get_secret_value(),
)

# A constant key makes every visitor share this quota.
daily_budget = limiter.shared_limit(
    "30/day", # 30 for now, shall modify when more people use it
    scope="kai-generation",
    key_func=lambda: "all-visitors",
    error_message="Kai has reached its daily limit. Please try again later.",
)