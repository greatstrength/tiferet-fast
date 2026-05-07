"""Fast API Builder."""

# *** imports

# ** core
from typing import Any, Callable, List
from functools import partial

# ** infra
from fastapi import FastAPI as FastAPIApp
from fastapi.routing import APIRouter
from starlette.middleware import Middleware
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware
from tiferet.builders import AppBuilder

# ** app
from ..domain import FastRouter
from ..contexts import FastApiContext

# *** builders

# ** builder: fast_api_builder
class FastApiBuilder(AppBuilder):
    '''
    Specialized application builder for FastAPI applications.
    '''

    # * method: get_routers
    def get_routers(self) -> List[FastRouter]:
        '''
        Resolve and execute the get_routers event from the service provider.

        :return: A list of FastRouter domain objects.
        :rtype: List[FastRouter]
        '''

        # Resolve the get_routers event and execute it.
        get_routers_evt = self.service_provider.get_service('get_routers_evt')
        return get_routers_evt.execute()

    # * method: build_router
    def build_router(self, fast_router: FastRouter, view_func: Callable, **kwargs) -> APIRouter:
        '''
        Build an APIRouter from a FastRouter domain object.

        :param fast_router: The FastRouter domain object.
        :type fast_router: FastRouter
        :param view_func: The view function to handle requests.
        :type view_func: Callable
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A configured APIRouter instance.
        :rtype: APIRouter
        '''

        # Create an APIRouter instance.
        router = APIRouter(
            prefix=fast_router.prefix,
            tags=[fast_router.name],
        )

        # Add routes from the FastRouter domain object.
        for route in fast_router.routes:
            router.add_api_route(
                name=route.endpoint,
                path=route.path,
                endpoint=partial(view_func),
                methods=route.methods,
                status_code=route.status_code,
            )

        # Return the configured router.
        return router

    # * method: build_fast_app
    def build_fast_app(self, interface_id: str, view_func: Callable, **kwargs) -> FastAPIApp:
        '''
        Build a complete FastAPI application with middleware and routers.

        :param interface_id: The interface ID to load.
        :type interface_id: str
        :param view_func: The view function to handle requests.
        :type view_func: Callable
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A configured FastAPI application instance.
        :rtype: FastAPIApp
        '''

        # Load the interface context.
        interface_context = self.load_interface(interface_id)

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

        # Load and include routers.
        routers = self.get_routers()
        for fast_router in routers:
            api_router = self.build_router(fast_router, view_func=view_func, **kwargs)
            fast_app.include_router(api_router)

        # Return the assembled FastAPI application.
        return fast_app

    # * method: run
    def run(self, interface_id: str, view_func: Callable, **kwargs) -> FastAPIApp:
        '''
        Build and return a ready-to-serve FastAPI application.

        :param interface_id: The interface ID to load.
        :type interface_id: str
        :param view_func: The view function to handle requests.
        :type view_func: Callable
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A configured FastAPI application instance.
        :rtype: FastAPIApp
        '''

        # Build and return the FastAPI application.
        return self.build_fast_app(interface_id, view_func, **kwargs)
