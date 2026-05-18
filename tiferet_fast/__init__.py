"""Tiferet Fast - A FastAPI Framework"""

# *** exports

# ** app
# Export the main application contexts and blueprint functions.
# Use a try-except block to avoid import errors on build systems.
try:
    from .contexts import FastApiContext, FastRequestContext
    from .blueprints import build_fast_app, build_fast_app as FastAPI
except Exception as e:
    import os, sys
    if not os.getenv('TIFERET_SILENT_IMPORTS'):
        print(f"Warning: Failed to import Tiferet Fast modules: {e}", file=sys.stderr)
    pass

# *** version

__version__ = "1.0.0b1"
