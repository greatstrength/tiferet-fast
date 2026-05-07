"""Tiferet Fast - A FastAPI Framework"""

# *** exports

# ** app
# Export the main application builder and related modules.
# Use a try-except block to avoid import errors on build systems.
try:
    from .builders import FastApiBuilder, FastApiBuilder as FastAPI
except Exception:
    pass

# *** version

__version__ = "0.2.1"
