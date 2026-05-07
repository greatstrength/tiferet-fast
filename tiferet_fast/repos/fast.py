"""Fast API YAML Repository."""

# *** imports

# ** core
from typing import List

# ** infra
from tiferet.utils import YamlLoader

# ** app
from ..domain import FastRoute, FastRouter
from ..interfaces import FastApiService
from ..mappers import FastRouterYamlObject

# *** repos

# ** repo: fast_yaml_repository
class FastYamlRepository(FastApiService):
    '''
    A YAML-backed repository for Fast API route and error configurations.
    '''

    # * attribute: fast_yaml_file
    fast_yaml_file: str

    # * attribute: encoding
    encoding: str

    # * init
    def __init__(self, fast_yaml_file: str, encoding: str = 'utf-8'):
        '''
        Initialize the FastYamlRepository.

        :param fast_yaml_file: The path to the Fast API configuration YAML file.
        :type fast_yaml_file: str
        :param encoding: The file encoding.
        :type encoding: str
        '''

        # Set the YAML file path and encoding.
        self.fast_yaml_file = fast_yaml_file
        self.encoding = encoding

    # * method: get_routers
    def get_routers(self) -> List[FastRouter]:
        '''
        Retrieve all Fast API routers from the YAML configuration.

        :return: A list of FastRouter instances.
        :rtype: List[FastRouter]
        '''

        # Load routers section from the YAML file.
        loader = YamlLoader(path=self.fast_yaml_file, mode='r', encoding=self.encoding)
        data = loader.load(
            start_node=lambda d: d.get('fast', {}).get('routers', {}),
        )

        # Map each router entry to a domain object via FastRouterYamlObject.
        return [
            FastRouterYamlObject.model_validate(dict(name=name, **router_data)).map()
            for name, router_data in data.items()
        ]

    # * method: get_route
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

        # Load all routers.
        routers = self.get_routers()

        # Search for the route across routers.
        for router in routers:
            if router_name and router.name != router_name:
                continue
            for route in router.routes:
                if route.id == route_id:
                    return route

        # Return None if not found.
        return None

    # * method: get_status_code
    def get_status_code(self, error_code: str) -> int:
        '''
        Retrieve the HTTP status code for a given error code.

        :param error_code: The error code.
        :type error_code: str
        :return: The corresponding HTTP status code.
        :rtype: int
        '''

        # Load the errors section from the YAML file.
        loader = YamlLoader(path=self.fast_yaml_file, mode='r', encoding=self.encoding)
        data = loader.load(
            start_node=lambda d: d.get('fast', {}).get('errors', {}),
        )

        # Return the status code if found, otherwise default to 500.
        return data.get(error_code, 500)
