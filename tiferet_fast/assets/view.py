"""FastAPI view assets."""

# *** imports

# ** core
from typing import Any

# ** infra
from fastapi import Request

# *** functions

# ** function: view_func
async def view_func(request: Request, context: Any) -> Any:
    '''
    Unpack a FastAPI request and return the session-run response body.

    :param request: The incoming FastAPI request.
    :type request: Request
    :param context: Duck-typed session collaborator exposing ``run``.
    :type context: Any
    :return: The session-run response body.
    :rtype: Any
    '''

    # Parse the JSON body; empty and non-JSON bodies become an empty dict.
    try:
        data = await request.json()
    except Exception:
        data = {}

    # Merge query params then path params onto the body data.
    data.update(dict(request.query_params))
    data.update(request.path_params)

    # Copy the request headers for the session collaborator.
    headers = dict(request.headers)

    # Run the feature named by the FastAPI route.
    response = context.run(feature_id=request.scope['route'].name, headers=headers, data=data)

    # Unwrap the (body, status_code) pair from the collaborator.
    body, _status_code = response

    # Return the response body only.
    return body
