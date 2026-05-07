"""Fast API domain models."""

# *** imports

# ** core
from typing import List

# ** infra
from pydantic import Field

# ** app
from tiferet.domain import DomainObject

# *** models

# ** model: fast_route
class FastRoute(DomainObject):
    '''
    A Fast route model.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='The unique identifier of the route.',
    )

    # * attribute: endpoint
    endpoint: str = Field(
        ...,
        description='The unique identifier of the route endpoint.',
    )

    # * attribute: path
    path: str = Field(
        ...,
        description='The URL path as string.',
    )

    # * attribute: methods
    methods: List[str] = Field(
        ...,
        description='A list of HTTP methods this rule should be limited to.',
    )

    # * attribute: status_code
    status_code: int = Field(
        default=200,
        description='The default HTTP status code for the route response.',
    )

# ** model: fast_router
class FastRouter(DomainObject):
    '''
    A Fast router model.
    '''

    # * attribute: name
    name: str = Field(
        ...,
        description='The name of the router.',
    )

    # * attribute: prefix
    prefix: str | None = Field(
        default=None,
        description='The URL prefix for all routes in this router.',
    )

    # * attribute: routes
    routes: List[FastRoute] = Field(
        default_factory=list,
        description='A list of routes associated with this router.',
    )
