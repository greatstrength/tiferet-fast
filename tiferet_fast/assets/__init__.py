"""FastAPI Assets."""

# *** exports

# ** app
from .core import (
    APP_FLAG,
    GET_ROUTE_EVT_SERVICE_ID,
    GET_ROUTERS_EVT_SERVICE_ID,
    GET_STATUS_CODE_EVT_SERVICE_ID,
)
from .errors import handle_tiferet_api_error
from .view import view_func
