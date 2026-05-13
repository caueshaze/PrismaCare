import logging
from collections import Counter

logger = logging.getLogger("prismacare.security")
metrics = Counter()


def audit_event(event: str, **data: object) -> None:
    metrics[event] += 1
    safe = {
        key: value
        for key, value in data.items()
        if key not in {"password", "token", "refresh_token", "access_token"}
    }
    logger.info("security_event=%s data=%s", event, safe)
