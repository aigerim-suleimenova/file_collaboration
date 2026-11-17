import logging

from app.core.log_redaction import TokenRedactingFilter


def test_uvicorn_websocket_log_line_is_redacted():
    record = logging.LogRecord(
        "uvicorn.error", logging.INFO, __file__, 1,
        '%s - "WebSocket %s" [accepted]',
        ("127.0.0.1:5000", "/api/v1/collab/abc?token=eyJhbGci.secret.sig&x=1"),
        None,
    )
    TokenRedactingFilter().filter(record)
    line = record.getMessage()
    assert "eyJhbGci" not in line
    assert "token=[REDACTED]&x=1" in line


def test_share_token_is_redacted():
    record = logging.LogRecord(
        "uvicorn.access", logging.INFO, __file__, 1, "%s", ("/x?share_token=abc.def.ghi",), None
    )
    TokenRedactingFilter().filter(record)
    assert record.getMessage() == "/x?share_token=[REDACTED]"
