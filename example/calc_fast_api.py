'''Calculator FastAPI entry point.'''

# *** imports

# ** infra
from fastapi import Request
from tiferet_fast import FastApiBuilder


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

# Create the builder and load the app service from config.yml.
builder = FastApiBuilder()
builder.load_app_service(app_yaml_file='config.yml')

# Build the FastAPI app with routers.
fast_app = builder.run('calc_fast_api', view_func)

# Access the context for the view function closure.
context = builder.load_interface('calc_fast_api')
