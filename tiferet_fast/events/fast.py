"""Fast API Domain Events."""

# *** imports

# ** core
from typing import List

# ** infra
from tiferet.events import DomainEvent

# ** app
from ..domain import FastRoute, FastRouter
from ..interfaces import FastApiService

# *** events

# ** event: get_routers
class GetRouters(DomainEvent):
    '''
    Event to retrieve all Fast API routers.
    '''

    # * attribute: fast_api_service
    fast_api_service: FastApiService

    # * init
    def __init__(self, fast_api_service: FastApiService):
        '''
        Initialize the GetRouters event.

        :param fast_api_service: The Fast API service for managing route configurations.
        :type fast_api_service: FastApiService
        '''

        # Set the Fast API service dependency.
        self.fast_api_service = fast_api_service

    # * method: execute
    def execute(self, **kwargs) -> List[FastRouter]:
        '''
        Retrieve all Fast API routers.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A list of FastRouter instances.
        :rtype: List[FastRouter]
        '''

        # Delegate to the Fast API service.
        return self.fast_api_service.get_routers()


# ** event: get_route
class GetRoute(DomainEvent):
    '''
    Event to retrieve a specific Fast API route by endpoint.
    '''

    # * attribute: fast_api_service
    fast_api_service: FastApiService

    # * init
    def __init__(self, fast_api_service: FastApiService):
        '''
        Initialize the GetRoute event.

        :param fast_api_service: The Fast API service for managing route configurations.
        :type fast_api_service: FastApiService
        '''

        # Set the Fast API service dependency.
        self.fast_api_service = fast_api_service

    # * method: execute
    @DomainEvent.parameters_required(['endpoint'])
    def execute(self, endpoint: str, **kwargs) -> FastRoute:
        '''
        Retrieve a Fast API route by endpoint.

        :param endpoint: The endpoint in the format 'router_name.route_id' or 'route_id'.
        :type endpoint: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The corresponding FastRoute instance.
        :rtype: FastRoute
        '''

        # Parse endpoint into router_name and route_id.
        router_name = None
        try:
            router_name, route_id = endpoint.split('.')
        except ValueError:
            route_id = endpoint

        # Retrieve the route from the service.
        route = self.fast_api_service.get_route(
            route_id=route_id,
            router_name=router_name,
        )

        # Verify the route exists.
        self.verify(
            expression=route is not None,
            error_code='FAST_ROUTE_NOT_FOUND',
            endpoint=endpoint,
        )

        # Return the found route.
        return route


# ** event: get_status_code
class GetStatusCode(DomainEvent):
    '''
    Event to retrieve the HTTP status code for a given error code.
    '''

    # * attribute: fast_api_service
    fast_api_service: FastApiService

    # * init
    def __init__(self, fast_api_service: FastApiService):
        '''
        Initialize the GetStatusCode event.

        :param fast_api_service: The Fast API service for managing route configurations.
        :type fast_api_service: FastApiService
        '''

        # Set the Fast API service dependency.
        self.fast_api_service = fast_api_service

    # * method: execute
    @DomainEvent.parameters_required(['error_code'])
    def execute(self, error_code: str, **kwargs) -> int:
        '''
        Retrieve the HTTP status code for an error code.

        :param error_code: The error code identifier.
        :type error_code: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The corresponding HTTP status code.
        :rtype: int
        '''

        # Delegate to the Fast API service.
        return self.fast_api_service.get_status_code(error_code=error_code)
