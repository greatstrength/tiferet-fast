"""Fast API Context for Tiferet framework."""

# *** imports

# ** core
from typing import Any, Callable
from functools import partial

# ** infra
from tiferet import TiferetError
from tiferet.contexts import (
    AppInterfaceContext,
    FeatureContext,
    ErrorContext,
    LoggingContext
)
from fastapi import FastAPI
from fastapi.routing import APIRouter
from starlette.middleware import Middleware
from starlette_context import context, plugins
from starlette_context.middleware import RawContextMiddleware

# ** app
from .request import FastRequestContext
from ..handlers import FastApiHandler
from ..models import FastRouter

# *** contexts

# ** context: fast_api_context
class FastApiContext(AppInterfaceContext):
    '''
    A context for managing Fast API interactions within the Tiferet framework.
    '''

    # * attribute: fast_app
    fast_app: FastAPI

    # * attribute: fast_api_handler
    fast_api_handler: FastApiHandler

    # * init
    def __init__(self,
            interface_id: str,
            features: FeatureContext,
            errors: ErrorContext,
            logging: LoggingContext,
            fast_api_handler: FastApiHandler
        ):
        '''
        Initialize the Fast API context.

        :param interface_id: The interface ID.
        :type interface_id: str
        :param features: The feature context.
        :type features: FeatureContext
        :param errors: The error context.
        :type errors: ErrorContext
        :param logging: The logging context.
        :type logging: LoggingContext
        :param fast_api_handler: The Fast API handler.
        :type fast_api_handler: FastApiHandler
        '''

        # Call the parent constructor.
        super().__init__(interface_id, features, errors, logging)

        # Set the attributes.
        self.fast_api_handler = fast_api_handler

    # * method: parse_request
    def parse_request(self, headers: dict = {}, data: dict = {}, feature_id: str = None, **kwargs) -> FastRequestContext:
        '''
        Parse the incoming request and return a FastRequestContext instance.

        :param headers: The request headers.
        :type headers: dict
        :param data: The request data.
        :type data: dict
        :param feature_id: The feature ID.
        :type feature_id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A FastRequestContext instance.
        :rtype: FastRequestContext
        '''

        # Return a FastRequestContext instance.
        return FastRequestContext(
            headers=headers,
            data=data,
            feature_id=feature_id
        )

    # * method: handle_error
    def handle_error(self, error: Exception) -> Any:
        '''
        Handle the error and return the response.

        :param error: The error to handle.
        :type error: Exception
        :return: The error response.
        :rtype: Any
        '''

        # Handle the error and get the response from the parent context.
        if not isinstance(error, TiferetError):
            return super().handle_error(error), 500

        # Get the status code by the error code on the exception.
        status_code = self.fast_api_handler.get_status_code(error.error_code)
        return super().handle_error(error), status_code

    # * method: handle_response
    def handle_response(self, request: FastRequestContext) -> Any:
        '''
        Handle the response from the request context.

        :param request: The request context.
        :type request: RequestContext
        :return: The response.
        :rtype: Any
        '''

        # Handle the response from the request context.
        response = super().handle_response(request)

        # Retrieve the route by the request feature id.
        route = self.fast_api_handler.get_route(request.feature_id)

        # Return the result with the specified status code.
        return response, route.status_code if route else 200

    # * method: build_router
    def build_router(self, fast_router: FastRouter, view_func: Callable, **kwargs) -> FastAPI:
        '''
        Assembles a FastAPI router from the given FastRouter model.

        :param fast_router: The FastRouter model.
        :type fast_router: FastRouter
        :param view_func: The view function to handle requests.
        :type view_func: Callable
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The created FastAPI router.
        :rtype: FastAPI
        '''

        # Create a FastAPI router instance.
        router = APIRouter(
            prefix=fast_router.prefix,
            tags=[fast_router.name]
        )

        # Add the routes to the router.
        for route in fast_router.routes:
            router.add_api_route(
                name=route.endpoint,
                path=route.path,
                endpoint=partial(view_func),
                methods=route.methods,
                status_code=route.status_code
            )

        # Return the created router.
        return router

    # * method: build_fast_app
    def build_fast_app(self, view_func: Callable, **kwargs) -> FastAPI:
        '''
        Build and return a FastAPI application instance.

        :param view_func: The view function to handle requests.
        :type view_func: Callable
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A FastAPI application instance.
        :rtype: FastAPI
        '''

        # Create middleware for context management.
        middleware = [
            Middleware(
                RawContextMiddleware, 
                plugins=(
                    plugins.RequestIdPlugin(), 
                    plugins.CorrelationIdPlugin(),
                )
            )
        ]

        # Create the FastAPI application.
        fast_app = FastAPI(title=f"{self.interface_id} API", middleware=middleware)

        # Load the FastAPI routers.
        routers = self.fast_api_handler.get_routers()

        # Create and include the routers.
        for router in routers:
            fast_router = self.build_router(router, view_func=view_func, **kwargs)
            fast_app.include_router(fast_router)

        # Set the fast_app attribute.
        self.fast_app = fast_app

        # Return the FastAPI application.
        return fast_app