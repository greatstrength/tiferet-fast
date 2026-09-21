"""FastAPI Assets."""

# *** exports

# ** app
from .core import (
    APP_FLAG,
    GET_ROUTE_EVT_SERVICE_ID,
    GET_ROUTERS_EVT_SERVICE_ID,
    GET_STATUS_CODE_EVT_SERVICE_ID,
)
from .context_headers import (
    CORRELATION_ID_HEADER_CONST_KEY,
    DEFAULT_CORRELATION_ID_HEADER,
    DEFAULT_REQUEST_ID_HEADER,
    REQUEST_ID_HEADER_CONST_KEY,
    apply_context_headers,
    parse_context_header_options,
)
from .errors import handle_tiferet_api_error
from .view import view_func
