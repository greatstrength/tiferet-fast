'''FastAPI view assets.'''

# *** imports

# ** core
from typing import Any

# ** infra
from fastapi import Request

# *** functions

# ** function: view_func
async def view_func(request: Request, context: Any) -> Any:
    '''
    Unpack a FastAPI request and run the matching feature on the composed session.

    :param request: The incoming FastAPI request.
    :type request: Request
    :param context: The composed session context collaborator.
    :type context: Any
    :return: The response body produced by the session run.
    :rtype: Any
    '''

    # Parse the JSON body when present; an empty or non-JSON body is an empty dict.
    try:
        data = await request.json()
    except Exception:
        data = {}

    # Merge query parameters and path parameters into the feature data.
    data.update(dict(request.query_params))
    data.update(request.path_params)

    # Copy request headers for the session run.
    headers = dict(request.headers)

    # Execute the feature named by the FastAPI route.
    response = context.run(
        feature_id=request.scope['route'].name,
        headers=headers,
        data=data,
    )

    # Unwrap the (body, status_code) pair from OpenApiSessionContext.build_response.
    body, _status_code = response

    # Return the response body; route status_code stays on add_api_route.
    return body
