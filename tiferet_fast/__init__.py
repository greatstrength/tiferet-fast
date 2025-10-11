"""Tiferet Fast - A FastAPI Framework"""

# *** exports

# ** app
# Export the main application context and related modules.
# Use a try-except block to avoid import errors on build systems.
try:
    from .contexts import FastApiContext
except:
    pass

# *** version

__version__ = "0.1.0"