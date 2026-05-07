"""Fast API Interfaces."""

# *** imports

# ** core
from abc import abstractmethod
from typing import List

# ** infra
from tiferet.interfaces import Service

# ** app
from ..domain import FastRoute, FastRouter

# *** interfaces

# ** interface: fast_api_service
class FastApiService(Service):
    '''
    Service interface for managing Fast API route and error configurations.
    '''

    # * method: get_routers
    @abstractmethod
    def get_routers(self) -> List[FastRouter]:
        '''
        Retrieve all Fast API routers.

        :return: A list of FastRouter instances.
        :rtype: List[FastRouter]
        '''
        raise NotImplementedError()

    # * method: get_route
    @abstractmethod
    def get_route(self, route_id: str, router_name: str = None) -> FastRoute:
        '''
        Retrieve a specific Fast API route by its route ID and optional router name.

        :param route_id: The ID of the route within the router.
        :type route_id: str
        :param router_name: The name of the router (optional).
        :type router_name: str
        :return: The corresponding FastRoute instance, or None if not found.
        :rtype: FastRoute
        '''
        raise NotImplementedError()

    # * method: get_status_code
    @abstractmethod
    def get_status_code(self, error_code: str) -> int:
        '''
        Retrieve the HTTP status code for a given error code.

        :param error_code: The error code.
        :type error_code: str
        :return: The corresponding HTTP status code.
        :rtype: int
        '''
        raise NotImplementedError()
