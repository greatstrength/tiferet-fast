"""Fast API Blueprint Exports."""

# *** exports

# ** app
from .fast import (
    resolve_model,
    get_routers,
    build_router,
    build_fast_app,
    build_fast_app as FastAPI,
    run,
)
