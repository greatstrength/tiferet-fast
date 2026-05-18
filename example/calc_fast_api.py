'''Calculator FastAPI entry point.'''

# *** imports

# ** infra
from fastapi import Request
from tiferet_fast import build_fast_app
from tiferet.blueprints.main import (
    resolve_interface,
    realize_interface,
    create_service_provider,
)


# *** functions

# ** function: view_func
async def view_func(request: Request):
    '''
    Handle incoming requests by executing the corresponding feature.

    :param request: The FastAPI request object.
    :type request: Request
    :return: JSON response.
    :rtype: dict
    '''

    # Parse the request body if present.
    try:
        data = await request.json()
    except Exception:
        data = {}

    # Merge query parameters and path parameters.
    data.update(dict(request.query_params))
    data.update(request.path_params)

    # Format header data from the request headers.
    headers = dict(request.headers)

    # Execute the feature from the request endpoint.
    response, status_code = context.run(
        feature_id=request.scope['route'].name,
        headers=headers,
        data=data,
    )

    # Wrap the result in the response model format.
    return {'result': response}


# *** exec

# Resolve the interface definition and extract constants for pre-seeding.
# NOTE: Workaround for DynamicServiceProvider eager wiring — constants must
# be registered before the types that depend on them.
app_interface, default_services = resolve_interface('calc_fast_api', app_yaml_file='config.yml')
type_map = app_interface.get_service_type_mapping()
constants = {k: v for k, v in type_map.items() if not isinstance(v, type)}

# Load the app interface context with a pre-seeded service provider.
context = realize_interface(
    app_interface,
    'calc_fast_api',
    service_provider=create_service_provider(**constants),
)

# Build the FastAPI app with middleware and routers.
fast_app = build_fast_app('calc_fast_api', view_func, app_yaml_file='config.yml')
