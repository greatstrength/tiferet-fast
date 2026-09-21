'''FastAPI context.'''

# *** imports

# ** core
from typing import Any, List

# ** infra
from fastapi import HTTPException
from tiferet import TiferetAPIError
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

    # * method: handle_error
    def handle_error(self, error: Exception, **kwargs) -> Any:
        '''
        Handle errors by converting TiferetAPIError into a FastAPI HTTPException.

        :param error: The error to handle.
        :type error: Exception
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The error response.
        :rtype: Any
        '''

        # Delegate to the parent OpenApiSessionContext for error formatting and status code resolution.
        try:
            return super().handle_error(error, **kwargs)
        except TiferetAPIError as api_error:

            # Raise a FastAPI HTTPException with the resolved status code and error details.
            raise HTTPException(
                status_code=api_error.status_code,
                detail={'error': api_error.name, 'message': api_error.message},
            )
