"""Redact credentials from server log lines.

Browsers can't set headers on WebSocket connections, so the collaboration
endpoint receives `token` / `share_token` in the query string, and uvicorn
logs WebSocket paths including the query string.
"""

import logging
import re

_TOKEN_PARAM = re.compile(r"((?:^|[?&])(?:share_)?token=)[^&\s\"]+")
REDACTED = "[REDACTED]"


def redact(text: str) -> str:
    return _TOKEN_PARAM.sub(rf"\1{REDACTED}", text)


class TokenRedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = redact(record.msg)
        if isinstance(record.args, tuple):
            record.args = tuple(redact(a) if isinstance(a, str) else a for a in record.args)
        return True


def install() -> None:
    """Attach the filter to uvicorn's loggers (idempotent)."""
    for name in ("uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(name)
        if not any(isinstance(f, TokenRedactingFilter) for f in logger.filters):
            logger.addFilter(TokenRedactingFilter())
