"""Fast API domain models."""

# *** imports

# ** infra
from tiferet.models import (
    ModelObject,
    StringType,
    IntegerType,
    ListType,
    ModelType
)

# *** models

# ** model: fast_route
class FastRoute(ModelObject):
    '''
    A Fast route model.
    '''

    # * attribute: id
    id = StringType(
        required=True,
        metadata=dict(
            description='The unique identifier of the route.'
        )
    )

    # * attribute: endpoint
    endpoint = StringType(
        required=True,
        metadata=dict(
            description='The unique identifier of the route endpoint.'
        )
    )

    # * attribute: path
    path = StringType(
        required=True,
        metadata=dict(
            description='The URL path as string.'
        )
    )

    # * attribute: methods
    methods = ListType(
        StringType,
        required=True,
        metadata=dict(
            description='A list of HTTP methods this rule should be limited to.'
        )
    )

    # * attribute: status_code
    status_code = IntegerType(
        default=200,
        metadata=dict(
            description='The default HTTP status code for the route response.'
        )
    )

# ** model: fast_router
class FastRouter(ModelObject):
    '''
    A Flask blueprint model.
    '''

    # * attribute: name
    name = StringType(
        required=True,
        metadata=dict(
            description='The name of the blueprint.'
        )
    )

    # * attribute: url_prefix
    prefix = StringType(
        metadata=dict(
            description='The URL prefix for all routes in this blueprint.'
        )
    )

    # * attribute: routes
    routes = ListType(
        ModelType(FastRoute),
        default=[],
        metadata=dict(
            description='A list of routes associated with this blueprint.'
        )
    )

    # * method: add_route
    def add_route(self, endpoint: str, path: str, methods: list[str], status_code: int = 200, **kwargs):
        '''
        Add a new route to the router.

        :param endpoint: The unique identifier of the route endpoint.
        :type endpoint: str
        :param path: The URL path as string.
        :type path: str
        :param methods: A list of HTTP methods this rule should be limited to.
        :type methods: list[str]
        :param status_code: The default HTTP status code for the route response, defaults to 200.
        :type status_code: int, optional
        :param kwargs: Additional keyword arguments for route configuration.
        :type kwargs: dict
        '''

        route = ModelObject.new(
            FastRoute,
            id=endpoint,
            endpoint=f'{self.name}.{endpoint}',
            path=path,
            methods=methods,
            status_code=status_code
        )

        self.routes.append(route)