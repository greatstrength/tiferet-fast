'''Calculator FastAPI entry point.'''

# *** imports

# ** infra
from tiferet_fast import build_fast_app


# *** exec

# Build the FastAPI app with the built-in view.
fast_app = build_fast_app('calc_fast_api', app_config='config.yml')
