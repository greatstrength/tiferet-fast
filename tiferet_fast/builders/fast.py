'''FastAPI Builder.'''

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
from tiferet.builders import AppBuilder
from tiferet_openapi import ApiRouter

# *** builders

# ** builder: fast_api_builder
class FastApiBuilder(AppBuilder):
    '''
    Specialized application builder for FastAPI applications.
    '''

    # * method: get_routers
    def get_routers(self) -> list:
        '''
        Resolve and execute the get_routers event from the service provider.

        :return: A list of ApiRouter domain objects.
        :rtype: list
        '''

        # Resolve the get_routers event and execute it.
        get_routers_evt = self.service_provider.get_service('get_routers_evt')
        return get_routers_evt.execute()

    # * method: resolve_model (static)
    @staticmethod
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

    # * method: build_router
    def build_router(self, router: ApiRouter, view_func: Callable, **kwargs) -> APIRouter:
        '''
        Build an APIRouter from an ApiRouter domain object.

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
            response_model = self.resolve_model(route.response_model)

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
        for router in routers:
            api_router = self.build_router(router, view_func=view_func, **kwargs)
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
