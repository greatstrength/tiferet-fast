"""Fast API Contracts."""

# *** imports

# ** core
from typing import List

# ** infra
from tiferet import (
    ModelContract,
    Repository,
    abstractmethod
)

# *** contracts

# ** contract: fast_route_contract
class FastRouteContract(ModelContract):
    '''
    A contract for Fast route models.
    '''

    # * attribute: endpoint
    endpoint: str

    # * attribute: status_code
    status_code: int

# ** contract: fast_blueprint_contract
class FastRouterContract(ModelContract):
    '''
    A contract for Fast blueprint models.
    '''

    # * attribute: name
    name: str

    # * attribute: routes
    routes: List[FastRouteContract]

# ** contract: fast_api_repository
class FastApiRepository(Repository):
    '''
    A repository contract for managing Fast API entities.
    '''

    # * method: get_routers
    @abstractmethod
    def get_routers(self) -> List[FastRouterContract]:
        '''
        Retrieve all Fast routers.

        :return: A list of FastRouterContract instances.
        :rtype: List[FastRouterContract]
        '''
        raise NotImplementedError('get_routers method not implemented.')

    # * method: get_route
    @abstractmethod
    def get_route(self, route_id: str, router_name: str = None) -> FastRouteContract:
        '''
        Retrieve a specific Fast route by its router and route IDs.

        :param route_id: The ID of the route within the router.
        :type route_id: str
        :param router_name: The name of the router (optional).
        :type router_name: str
        :return: The corresponding FastRouteContract instance.
        :rtype: FastRouteContract
        '''
        raise NotImplementedError('get_route method not implemented.')

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
        raise NotImplementedError('get_status_code method not implemented.')