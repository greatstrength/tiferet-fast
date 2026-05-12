"""Tiferet Fast Blueprints"""

# *** imports

# ** core
import importlib
from typing import Callable
from functools import partial

# ** infra
from fastapi import FastAPI as FastAPIApp
from fastapi.routing import APIRouter
from starlette.middleware import Middleware
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware
from tiferet.di import ServiceProvider
from tiferet_openapi import ApiRouter
from tiferet.blueprints.main import (
    resolve_interface,
    realize_interface,
    create_service_provider,
)
from tiferet import assets as a

# *** blueprints

# ** blueprint: resolve_model
def resolve_model(model_path: str | None) -> type | None:
    '''
    Dynamically import a Pydantic model class by its dotted import path.

    :param model_path: The dotted import path (e.g., 'app.domain.request.AddNumberRequest').
    :type model_path: str | None
    :return: The resolved model class, or None if no path provided.
    :rtype: type | None
    '''

    # Return None if no model path is provided.
    if not model_path:
        return None

    # Split the path into module and class name.
    module_path, class_name = model_path.rsplit('.', 1)

    # Import the module and return the class.
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


# ** blueprint: get_routers
def get_routers(service_provider: ServiceProvider) -> list:
    '''
    Resolve and execute the get_routers event from the service provider.

    :param service_provider: The service provider to resolve the event from.
    :type service_provider: ServiceProvider
    :return: A list of ApiRouter domain objects.
    :rtype: list
    '''

    # Resolve the get_routers event and execute it.
    get_routers_evt = service_provider.get_service('get_routers_evt')
    return get_routers_evt.execute()


# ** blueprint: build_router
def build_router(router: ApiRouter, view_func: Callable, **kwargs) -> APIRouter:
    '''
    Build a FastAPI APIRouter from an ApiRouter domain object.

    :param router: The ApiRouter domain object.
    :type router: ApiRouter
    :param view_func: The view function to handle requests.
    :type view_func: Callable
    :param kwargs: Additional keyword arguments.
    :type kwargs: dict
    :return: A configured APIRouter instance.
    :rtype: APIRouter
    '''

    # Create an APIRouter instance.
    api_router = APIRouter(
        prefix=router.prefix,
        tags=[router.name],
    )

    # Add routes from the ApiRouter domain object.
    for route in router.routes:

        # Resolve the response model if specified.
        response_model = resolve_model(route.response_model)

        # Add the route with Swagger metadata.
        api_router.add_api_route(
            name=route.endpoint,
            path=route.path,
            endpoint=partial(view_func),
            methods=route.methods,
            status_code=route.status_code,
            response_model=response_model,
            summary=route.summary,
            description=route.description,
            tags=route.tags or [router.name],
        )

    # Return the configured router.
    return api_router


# ** blueprint: build_fast_app
def build_fast_app(interface_id: str, view_func: Callable, **parameters) -> FastAPIApp:
    '''
    Build a complete FastAPI application with middleware and routers.

    Resolves the interface via tiferet.blueprints.main.resolve_interface,
    realizes it via realize_interface, builds middleware, and assembles
    a FastAPI app with routers.

    :param interface_id: The interface ID to load.
    :type interface_id: str
    :param view_func: The view function to handle requests.
    :type view_func: Callable
    :param parameters: Additional parameters for interface resolution.
    :type parameters: dict
    :return: A configured FastAPI application instance.
    :rtype: FastAPIApp
    '''

    # Resolve the interface definition.
    app_interface, default_services = resolve_interface(interface_id, **parameters)

    # Realize the app interface context.
    interface_context = realize_interface(app_interface, interface_id)

    # Create middleware.
    middleware = [
        Middleware(
            RawContextMiddleware,
            plugins=(
                plugins.RequestIdPlugin(),
                plugins.CorrelationIdPlugin(),
            ),
        )
    ]

    # Create the FastAPI app.
    fast_app = FastAPIApp(
        title=f'{interface_id} API',
        middleware=middleware,
    )

    # Build a service provider seeded with default service dependencies
    # so get_routers can resolve the routers event.
    service_provider = create_service_provider(
        type_map={dep.service_id: dep.get_service_type() for dep in default_services},
        **{k: v for dep in default_services for k, v in dep.parameters.items()},
        **(app_interface.constants or {}),
        **parameters,
    )

    # Load and include routers.
    routers = get_routers(service_provider)
    for router in routers:
        api_router = build_router(router, view_func=view_func)
        fast_app.include_router(api_router)

    # Return the assembled FastAPI application.
    return fast_app


# ** blueprint: run
def run(interface_id: str, view_func: Callable, **parameters) -> FastAPIApp:
    '''
    Build and return a ready-to-serve FastAPI application.

    Convenience alias for build_fast_app.

    :param interface_id: The interface ID to load.
    :type interface_id: str
    :param view_func: The view function to handle requests.
    :type view_func: Callable
    :param parameters: Additional parameters for interface resolution.
    :type parameters: dict
    :return: A configured FastAPI application instance.
    :rtype: FastAPIApp
    '''

    # Build and return the FastAPI application.
    return build_fast_app(interface_id, view_func, **parameters)
