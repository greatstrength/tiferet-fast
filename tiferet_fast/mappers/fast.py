"""Fast API Mappers."""

# *** imports

# ** core
from typing import Any, ClassVar, Dict, List

# ** infra
from pydantic import Field

# ** app
from ..domain import (
    FastRoute,
    FastRouter,
)
from tiferet.mappers import (
    Aggregate,
    TransferObject,
)

# *** mappers

# ** mapper: fast_route_aggregate
class FastRouteAggregate(FastRoute, Aggregate):
    '''
    Aggregate for the FastRoute domain object.
    '''

    pass

# ** mapper: fast_router_aggregate
class FastRouterAggregate(FastRouter, Aggregate):
    '''
    Aggregate for the FastRouter domain object.
    '''

    # * method: add_route
    def add_route(self,
            endpoint: str,
            path: str,
            methods: List[str],
            status_code: int = 200,
        ) -> FastRouteAggregate:
        '''
        Add a new route to the router.

        :param endpoint: The unique identifier of the route endpoint.
        :type endpoint: str
        :param path: The URL path as string.
        :type path: str
        :param methods: A list of HTTP methods this rule should be limited to.
        :type methods: List[str]
        :param status_code: The default HTTP status code for the route response.
        :type status_code: int
        :return: The created route aggregate.
        :rtype: FastRouteAggregate
        '''

        # Create the route aggregate.
        route = FastRouteAggregate(
            id=endpoint,
            endpoint=f'{self.name}.{endpoint}',
            path=path,
            methods=methods,
            status_code=status_code,
        )

        # Copy routes to a local list, append, and reassign.
        routes = list(self.routes)
        routes.append(route)
        self.routes = routes

        # Return the created route.
        return route

# ** mapper: fast_route_yaml_object
class FastRouteYamlObject(FastRoute, TransferObject):
    '''
    A YAML data representation of a FastRoute object.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data.yaml': {'exclude': {'id', 'endpoint'}},
    }

    # * attribute: id
    id: str | None = Field(
        default=None,
        description='The unique identifier of the route (provided via dict key during mapping).',
    )

    # * attribute: endpoint
    endpoint: str | None = Field(
        default=None,
        description='The unique identifier of the route endpoint.',
    )

    # * method: map
    def map(self, id: str = None, endpoint: str = None, **overrides) -> FastRouteAggregate:
        '''
        Map the YAML data to a FastRouteAggregate.

        :param id: The route identifier override.
        :type id: str
        :param endpoint: The endpoint override.
        :type endpoint: str
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new FastRouteAggregate.
        :rtype: FastRouteAggregate
        '''

        # Map to the route aggregate with overrides.
        return super().map(
            FastRouteAggregate,
            id=id,
            endpoint=endpoint,
            **overrides,
        )

    # * method: from_model
    @classmethod
    def from_model(cls, route: FastRoute, **overrides) -> 'FastRouteYamlObject':
        '''
        Create a FastRouteYamlObject from a FastRoute model.

        :param route: The FastRoute model.
        :type route: FastRoute
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new FastRouteYamlObject.
        :rtype: FastRouteYamlObject
        '''

        # Create from the model.
        return super().from_model(route, **overrides)

# ** mapper: fast_router_yaml_object
class FastRouterYamlObject(FastRouter, TransferObject):
    '''
    A YAML data representation of a FastRouter object.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {'exclude': {'routes'}},
        'to_data.yaml': {'by_alias': True, 'exclude': {'name'}},
    }

    # * attribute: name
    name: str | None = Field(
        default=None,
        description='The name of the router.',
    )

    # * attribute: routes
    routes: Dict[str, FastRouteYamlObject] = Field(
        default_factory=dict,
        description='A dictionary of route endpoint ID to FastRouteYamlObject instances.',
    )

    # * method: map
    def map(self, **overrides) -> FastRouterAggregate:
        '''
        Map the YAML data to a FastRouterAggregate.

        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new FastRouterAggregate.
        :rtype: FastRouterAggregate
        '''

        # Map to the router aggregate with nested route conversion.
        return super().map(
            FastRouterAggregate,
            routes=[
                route.map(id=id, endpoint=f'{self.name}.{id}')
                for id, route in self.routes.items()
            ],
            **overrides,
        )

    # * method: from_model
    @classmethod
    def from_model(cls, router: FastRouter, **overrides) -> 'FastRouterYamlObject':
        '''
        Create a FastRouterYamlObject from a FastRouter model.

        :param router: The FastRouter model.
        :type router: FastRouter
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new FastRouterYamlObject.
        :rtype: FastRouterYamlObject
        '''

        # Create from the model, converting nested routes list to dict.
        return super().from_model(
            router,
            routes={
                route.id: FastRouteYamlObject.from_model(route)
                for route in router.routes
            },
            **overrides,
        )
