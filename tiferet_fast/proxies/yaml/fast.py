"""Fast API YAML Configuration Proxy."""

# *** imports

# ** core
from typing import List, Any

# ** infra
from tiferet import (
    TiferetError,
    raise_error
)
from tiferet.proxies.yaml import (
    YamlConfigurationProxy
)

# ** app
from ...contracts import (
    FastApiRepository,
    FastRouterContract,
    FastRouteContract
)
from ...data import (
    FastRouterYamlData
)

# *** proxies

# ** proxy: fast_yaml_proxy
class FastYamlProxy(FastApiRepository, YamlConfigurationProxy):
    '''
    A YAML configuration proxy for Fast API settings.
    '''

    # * init
    def __init__(self, fast_config_file: str):
        '''
        Initialize the FastYamlProxy with the given YAML file path.

        :param fast_config_file: The path to the Fast API configuration YAML file.
        :type fast_config_file: str
        '''

        # Set the configuration file within the base class.
        super().__init__(fast_config_file)

    # * method: load_yaml
    def load_yaml(self, start_node: callable = lambda data: data, create_data: callable = lambda data: data) -> Any:
        '''
        Load data from the YAML configuration file.

        :param start_node: The starting node in the YAML file.
        :type start_node: callable
        :param create_data: A callable to create data objects from the loaded data.
        :type create_data: callable
        :return: The loaded data.
        :rtype: Any
        '''

        # Load the YAML file contents using the yaml config proxy.
        try:
            return super().load_yaml(
                start_node=start_node,
                create_data=create_data
            )

        # Raise an error if the loading fails.
        except (Exception, TiferetError) as e:
            raise_error.execute(
                'FAST_CONFIG_LOADING_FAILED',
                f'Unable to load Fast API configuration file {self.config_file}: {e}.',
                self.config_file,
                str(e)
            )

    # * method: get_routers
    def get_routers(self) -> List[FastRouterContract]:
        '''
        Retrieve all Fast API routers from the YAML configuration.

        :return: A list of FastRouterContract instances.
        :rtype: List[FastRouterContract]
        '''

        # Load the routers section from the YAML file.
        data = self.load_yaml(
            create_data=lambda data: [FastRouterYamlData.from_data(
                name=name,
                **router
            ) for name, router in data.items()],
            start_node=lambda d: d.get('fast', {}).get('routers', {})
        )

        # Map the loaded data to FastRouterContract instances.
        return [router.map() for router in data]

    # * method: get_route
    def get_route(self, route_id: str, router_name: str = None) -> FastRouteContract:
        '''
        Retrieve a specific Fast API route by its router and route IDs from the YAML configuration.

        :param route_id: The route identifier.
        :type route_id: str
        :param router_name: The name of the router (optional).
        :type router_name: str
        :return: The corresponding FastRouteContract instance.
        :rtype: FastRouteContract
        '''

        # Load the routers section from the YAML file.
        routers = self.get_routers()

        # Search for the specified router.
        for router in routers:
            if router_name and router.name != router_name:
                continue

            # Search for the route within the router.
            for route in router.routes:
                if route.id == route_id:
                    return route

        # If not found, return None.
        return None

    # * method: get_status_code
    def get_status_code(self, error_code: str) -> int:
        '''
        Retrieve the HTTP status code for a given error code from the YAML configuration.

        :param error_code: The error code identifier.
        :type error_code: str
        :return: The corresponding HTTP status code.
        :rtype: int
        '''

        # Load the error code from the errors section of the YAML file.
        data = self.load_yaml(
            start_node=lambda d: d.get('fast').get('errors', {})
        )

        # Return the status code if found, otherwise default to 500.
        return data.get(error_code, 500)