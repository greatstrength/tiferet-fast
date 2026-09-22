'''FastAPI context.'''

# *** imports

# ** core
from typing import List

# ** infra
from tiferet_openapi import ApiRouter, OpenApiSessionContext

# *** contexts

# ** context: fast_api_context
class FastApiContext(OpenApiSessionContext):
    '''
    A FastAPI-specific API context extending the shared OpenAPI session hub.
    '''

    # * method: get_routers
    def get_routers(self) -> List[ApiRouter]:
        '''
        Retrieve the configured routers via the injected handler.

        :return: A list of ApiRouter domain objects.
        :rtype: List[ApiRouter]
        '''

        # Call the injected routers handler directly.

        return self._get_routers()
