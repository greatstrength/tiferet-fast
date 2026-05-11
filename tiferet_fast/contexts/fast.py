'''FastAPI context.'''

# *** imports

# ** infra
from tiferet_openapi import OpenApiContext

# *** contexts

# ** context: fast_api_context
class FastApiContext(OpenApiContext):
    '''
    A FastAPI-specific API context extending the shared OpenAPI context.
    '''
    pass
