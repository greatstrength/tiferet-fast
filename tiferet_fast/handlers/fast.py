"""Fast API Handlers."""

# *** imports

# ** core
from typing import List

# ** infra
from tiferet.commands import raise_error

# ** app
from ..contracts import (
    FastRouterContract,
    FastRouteContract,
    FastApiRepository
)

# *** handlers

# ** handler: fast_api_handler
class FastApiHandler(object):
    '''
    A handler for managing Fast API entities.
    '''

    # * init
    def __init__(self, fast_repo: FastApiRepository):
        '''
        Initialize the FastApiHandler with the given repository.

        :param fast_repo: An instance of FastApiRepository.
        :type fast_repo: FastApiRepository
        '''

        # Store the repository instance.
        self.fast_repo = fast_repo

    # * method: get_routers
    def get_routers(self) -> List[FastRouterContract]:
        '''
        Retrieve all Fast API routers using the repository.

        :return: A list of FastRouterContract instances.
        :rtype: List[FastRouterContract]
        '''

        # Delegate the call to the repository.
        return self.fast_repo.get_routers()

    # * method: get_route
    def get_route(self, endpoint: str) -> FastRouteContract:
        '''
        Retrieve a specific Fast API route by its router and route IDs.

        :param endpoint: The endpoint in the format 'router_name.route_id'.
        :type endpoint: str
        :return: The corresponding FastRouteContract instance.
        :rtype: FastRouteContract
        '''

        # Split the endpoint into router and route IDs.
        router_name = None
        try:
            router_name, route_id = endpoint.split('.')
        except ValueError:
            route_id = endpoint

        # Delegate the call to the repository.
        route = self.fast_repo.get_route(
            route_id=route_id,
            router_name=router_name
        )

        # Raise an error if the route is not found.
        if route is None:
            raise_error.execute(
                'FAST_ROUTE_NOT_FOUND',
                f'Fast API route not found for endpoint: {endpoint}',
                endpoint
            )

        # Return the found route.
        return route

    # * method: get_status_code
    def get_status_code(self, error_code: str) -> int:
        '''
        Retrieve the HTTP status code for a given error code using the repository.

        :param error_code: The error code identifier.
        :type error_code: str
        :return: The corresponding HTTP status code.
        :rtype: int
        '''

        # Delegate the call to the repository.
        return self.fast_repo.get_status_code(
            error_code=error_code
        )