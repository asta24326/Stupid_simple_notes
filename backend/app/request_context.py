# ContextVar: a variable whose value is separate for every request (every asyncio task)
# re: regular expressions, used to check that a header value contains only safe characters
import re

# uuid: generates unique identifiers
import uuid
from contextvars import ContextVar

# Letters, digits, "_" and "-", from 1 to 64 characters: nothing that could forge a loge line
SAFE_REQUEST_ID_PATTERN = re.compile(r"[A-Za-z0-9_-]{1,64}")

# "-" is what logs show when no request is being handled (startup, background code)
# [A-Za-z0-9_-] = one letter, digit, "_" or "-"; {1,64} = max 64 chars(could be set different amount)
request_id_var = ContextVar("request_id", default="-")


def resolve_request_id(header_value: str | None) -> str:
    """Use the id from X-Request-Id header if it is safe. otherwise generate our own id."""
    if header_value is not None and SAFE_REQUEST_ID_PATTERN.fullmatch(header_value):
        return header_value
    return uuid.uuid4().hex[:8]


# syntax hints:
#
# uuid4() = random unique id; .hex = it as 32 hex characters; [:8] = slice, the first 8 characters
# fullmatch: the WHOLE string must match the pattern; returns a match object (truthy) or None (falsy)
