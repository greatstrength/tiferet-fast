"""Tiferet Fast Blueprints"""

# *** imports

# ** core
import importlib
from functools import partial
from typing import Any, Callable, List

# ** infra
from fastapi import FastAPI as FastAPIApp, Request
from fastapi.routing import APIRouter
from starlette.middleware import Middleware
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware
from tiferet import TiferetError
from tiferet.blueprints import core
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
from ..assets.view import view_func as default_view_func
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

    Parallel to tiferet_openapi.blueprints.openapi.build_openapi_session_context,
    but realizes FastApiContext directly so FastAPI-specific methods such as
    get_routers and handle_error remain available on the composed context.

    :param app_session: The resolved app session definition.
    :type app_session: AppSession
    :param cache: The pre-built shared cache context.
    :type cache: CacheContext
    :param create_request_handler: Optional request-construction handler;
        defaults to create_openapi_request_context when omitted.
    :type create_request_handler: Callable
    :param extra_kwargs: Additional keyword arguments forwarded to the
        context constructor.
    :type extra_kwargs: dict
    :return: The wired FastAPI context.
    :rtype: FastApiContext
    '''

    # Build the app service container and compose the feature-level resolver.
    app_container = core.build_app_service_container(cache, app_session)
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
    Retrieve the configured routers from the composed FastAPI context.

    :param interface_context: The realized FastAPI context.
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
def build_fast_app(interface_id: str,
        view_func: Callable = None,
        **parameters) -> FastAPIApp:
    '''
    Build a complete FastAPI application with middleware and routers.

    Loads the app session via core.build_cache/core.get_app_session, composes
    the FastApiContext via build_fast_session_context, binds the built-in view
    when view_func is omitted, and includes one FastAPI router per declared
    ApiRouter.

    :param interface_id: The interface ID to load.
    :type interface_id: str
    :param view_func: Optional request-only view function. When omitted, the
        built-in asset view is bound to the composed context.
    :type view_func: Callable
    :param parameters: Additional keyword arguments passed to core.get_app_session.
    :type parameters: dict
    :return: A configured FastAPI application instance.
    :rtype: FastAPIApp
    '''

    # Build the bootstrap cache and resolve the app session.
    cache = core.build_cache()
    app_session = core.get_app_session(interface_id, cache, **parameters)

    # Compose the FastAPI context from the resolved app session.
    interface_context = build_fast_session_context(app_session, cache)

    # Bind the built-in asset view when the consumer does not supply one.
    if view_func is None:

        async def bound_view(request: Request) -> Any:

            # Delegate to the asset view with the composed context.
            return await default_view_func(request, interface_context)

    else:
        bound_view = view_func

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

    # Load and include routers using the composed context.
    routers = get_routers(interface_context)
    for router in routers:
        api_router = build_router(router, view_func=bound_view)
        fast_app.include_router(api_router)

    # Return the assembled FastAPI application.
    return fast_app

# ** blueprint: run
def run(interface_id: str, view_func: Callable = None, **parameters) -> FastAPIApp:
    '''
    Build and return a ready-to-serve FastAPI application.

    Convenience alias for build_fast_app.

    :param interface_id: The interface ID to load.
    :type interface_id: str
    :param view_func: Optional request-only view function.
    :type view_func: Callable
    :param parameters: Additional keyword arguments.
    :type parameters: dict
    :return: A configured FastAPI application instance.
    :rtype: FastAPIApp
    '''

    # Build and return the FastAPI application.
    return build_fast_app(interface_id, view_func, **parameters)
