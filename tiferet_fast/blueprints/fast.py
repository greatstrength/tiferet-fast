"""Tiferet Fast Blueprints"""

# *** imports

# ** core
import importlib
from typing import Any, Callable, List
from functools import partial

# ** infra
from fastapi import FastAPI as FastAPIApp
from fastapi.routing import APIRouter
from starlette.middleware import Middleware
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware
from tiferet import TiferetError, assets as a
from tiferet.blueprints import core
try:
    from tiferet.blueprints.main import (
        resolve_interface,
        realize_interface,
        create_service_provider,
    )
except ImportError:
    resolve_interface = None
    realize_interface = None
    create_service_provider = None
from tiferet.contexts.app import AppSession
from tiferet.contexts.cache import CacheContext
from tiferet_openapi import ApiRouter, create_openapi_request_context

# ** app
from ..assets.core import (
    APP_FLAG,
    GET_ROUTE_EVT_SERVICE_ID,
    GET_ROUTERS_EVT_SERVICE_ID,
    GET_STATUS_CODE_EVT_SERVICE_ID,
)
from ..contexts.fast import FastApiContext

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

    # Import the model class from the dotted path.
    try:

        # Split the path into module and class name.
        module_path, class_name = model_path.rsplit('.', 1)

        # Import the module and return the class.
        module = importlib.import_module(module_path)
        return getattr(module, class_name)

    except Exception as exception:

        # Raise a structured error carrying the failing path and reason.
        TiferetError.raise_error(
            'OPENAPI_MODEL_RESOLUTION_FAILED',
            f'Failed to resolve model schema for path: {model_path}.',
            model_path=model_path,
            reason=str(exception),
        )


# ** blueprint: get_route_handler
def get_route_handler(get_dependency: Callable) -> Callable:
    '''
    Build a route-lookup closure that resolves the get-route event via DI.

    :param get_dependency: The DI resolution handler.
    :type get_dependency: Callable
    :return: A callable that retrieves a route by endpoint.
    :rtype: Callable
    '''

    # Return the handler closure bound to the resolver.
    def handler(**kwargs) -> Any:

        # Resolve and execute the get-route event.
        get_route_evt = get_dependency(GET_ROUTE_EVT_SERVICE_ID, APP_FLAG)
        return get_route_evt.execute(**kwargs)

    # Return the closure.
    return handler


# ** blueprint: get_status_code_handler
def get_status_code_handler(get_dependency: Callable) -> Callable:
    '''
    Build a status-code-lookup closure that resolves the get-status-code event via DI.

    :param get_dependency: The DI resolution handler.
    :type get_dependency: Callable
    :return: A callable that retrieves an HTTP status code by error code.
    :rtype: Callable
    '''

    # Return the handler closure bound to the resolver.
    def handler(**kwargs) -> Any:

        # Resolve and execute the get-status-code event.
        get_status_code_evt = get_dependency(GET_STATUS_CODE_EVT_SERVICE_ID, APP_FLAG)
        return get_status_code_evt.execute(**kwargs)

    # Return the closure.
    return handler


# ** blueprint: get_routers_handler
def get_routers_handler(get_dependency: Callable) -> Callable:
    '''
    Build a routers-lookup closure that resolves the get-routers event via DI.

    :param get_dependency: The DI resolution handler.
    :type get_dependency: Callable
    :return: A callable that retrieves the configured routers.
    :rtype: Callable
    '''

    # Return the handler closure bound to the resolver.
    def handler(**kwargs) -> Any:

        # Resolve and execute the get-routers event.
        get_routers_evt = get_dependency(GET_ROUTERS_EVT_SERVICE_ID, APP_FLAG)
        return get_routers_evt.execute(**kwargs)

    # Return the closure.
    return handler


# ** blueprint: build_fast_session_context
def build_fast_session_context(app_session: AppSession,
        cache: CacheContext,
        create_request_handler: Callable = None,
        **extra_kwargs) -> FastApiContext:
    '''
    Build a fully wired FastApiContext from a resolved app session.

    An omitted create_request_handler defaults to create_openapi_request_context.
    An explicit handler is assigned as-is and is not wrapped.

    :param app_session: The resolved app session definition.
    :type app_session: AppSession
    :param cache: The pre-built shared cache context.
    :type cache: CacheContext
    :param create_request_handler: Optional request-construction handler;
        defaults to create_openapi_request_context when omitted.
    :type create_request_handler: Callable
    :param extra_kwargs: Additional keyword arguments forwarded to
        core.compose_session_context.
    :type extra_kwargs: dict
    :return: The wired FastAPI session context.
    :rtype: FastApiContext
    '''

    # Build the app service container.
    app_container = core.build_app_service_container(cache, app_session)

    # Compose the feature-level resolver.
    resolver = core.build_service_resolver(app_container)

    # Delegate handler wiring, collaborator resolution, and construction.
    return core.compose_session_context(
        FastApiContext,
        app_session,
        cache,
        app_container,
        resolver,
        create_request_handler=create_request_handler or create_openapi_request_context,
        response_handler=core.response_handler,
        get_route_handler=get_route_handler(resolver.get_dependency),
        get_status_code_handler=get_status_code_handler(resolver.get_dependency),
        get_routers_handler=get_routers_handler(resolver.get_dependency),
        **extra_kwargs,
    )


# ** blueprint: get_routers
def get_routers(interface_context: FastApiContext) -> List[ApiRouter]:
    '''
    Retrieve the configured routers from the FastAPI session context.

    :param interface_context: The realized FastAPI session context.
    :type interface_context: FastApiContext
    :return: A list of ApiRouter domain objects.
    :rtype: List[ApiRouter]
    '''

    # Retrieve the routers from the interface context.
    return interface_context.get_routers()


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
