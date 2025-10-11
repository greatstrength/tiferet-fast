"""Fast API Data Transfer Objects (DTOs)."""

# *** imports

# ** core
from typing import Dict, Any

# ** infra
from tiferet.data import (
    DataObject,
    StringType,
    DictType,
    ModelType
)

# ** app
from ..models import (
    FastRoute,
    FastRouter
)
from ..contracts import (
    FastRouteContract,
    FastRouterContract
)

# *** data

# ** data: fast_route_yaml_data
class FastRouteYamlData(DataObject, FastRoute):
    '''
    A data object for Fast API route model from YAML.
    '''

    class Options:
        '''
        Options for the data object.
        '''
        serialize_when_none = False
        roles = {
            'to_model': DataObject.allow(),
            'to_data': DataObject.deny('endpoint')
        }

    # * attribute: endpoint
    endpoint = StringType(
        metadata=dict(
            description='The unique identifier of the route endpoint.'
        )
    )

    # * method: map
    def map(self, id: str, endpoint: str) -> FastRouteContract:
        '''
        Map the data object to a FastRouteContract instance.

        :param id: The unique identifier of the route.
        :type id: str
        :param endpoint: The name of the route endpoint.
        :type endpoint: str
        :return: A FastRouteContract instance.
        :rtype: FastRouteContract
        '''

        # Map the data object to a model instance.
        return super().map(
            FastRoute,
            id=id,
            endpoint=endpoint
        )

# ** data: fast_router_yaml_data
class FastRouterYamlData(DataObject, FastRouter):
    '''
    A data object for Fast API router model from YAML.
    '''

    class Options:
        '''
        Options for the data object.
        '''
        serialize_when_none = False
        roles = {
            'to_model': DataObject.deny('routes'),
            'to_data': DataObject.deny('name')
        }

    # * attribute: name
    name = StringType(
        metadata=dict(
            description='The name of the router.'
        )
    )

    # * attribute: routes
    routes = DictType(
        ModelType(FastRouteYamlData),
        default={},
        metadata=dict(
            description='A dictionary of route endpoint to FastRouteYamlData instances.'
        )
    )

    # * method: from_data
    @staticmethod
    def from_data(routes: Dict[str, Any] = {}, **kwargs) -> 'FastRouterYamlData':
        '''
        Create a FastRouterYamlData instance from raw data.

        :param routes: A dictionary of route endpoint to route data.
        :type routes: Dict[str, Any]
        :return: A FastRouterYamlData instance.
        :rtype: FastRouterYamlData
        '''

        # Convert each route in the routes dictionary to a FastRouteYamlData instance.
        route_objs = {endpoint: DataObject.from_data(
            FastRouteYamlData,
            endpoint=endpoint,
            **data
        ) for endpoint, data in routes.items()}

        # Create and return a FastRouterYamlData instance.
        return DataObject.from_data(
            FastRouterYamlData,
            routes=route_objs,
            **kwargs
        )

    # * method: map
    def map(self) -> FastRouterContract:
        '''
        Map the data object to a FastRouterContract instance.

        :return: A FastRouterContract instance.
        :rtype: FastRouterContract
        '''

        # Map each route in the routes dictionary.
        return super().map(
            FastRouter,
            routes=[
                route.map(id=id, endpoint=f'{self.name}.{id}') 
                for id, route 
                in self.routes.items()
            ]
        )