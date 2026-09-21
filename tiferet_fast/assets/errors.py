'''FastAPI error assets.'''

# *** imports

# ** infra
from fastapi import Request
from fastapi.responses import JSONResponse
from tiferet import TiferetAPIError
from tiferet_openapi import ApiErrorResponse

# *** functions

# ** function: handle_tiferet_api_error
def handle_tiferet_api_error(request: Request, exc: TiferetAPIError) -> JSONResponse:
    '''
    Map a raised TiferetAPIError into an ApiErrorResponse JSON response.

    :param request: The incoming request (unused; required by Starlette ExceptionHandler).
    :type request: Request
    :param exc: The raised TiferetAPIError carrying the resolved status code.
    :type exc: TiferetAPIError
    :return: A JSONResponse with {error, message} and the mapped HTTP status.
    :rtype: JSONResponse
    '''

    # Build the ApiErrorResponse body from the raised error.
    payload = ApiErrorResponse(error=exc.name, message=exc.message or '')

    # Return JSON with the mapped HTTP status; request is unused by design.
    return JSONResponse(
        content=payload.model_dump(),
        status_code=getattr(exc, 'status_code', 500),
    )
