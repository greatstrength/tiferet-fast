# *** imports

# ** infra
import pytest

# ** app
from ..fast import (
    ModelObject,
    FastRoute,
    FastRouter,
)

# *** fixtures

# ** fixture: fast_route
@pytest.fixture
def fast_route() -> FastRoute:
    '''
    A fixture that provendpointes a sample FastRoute instance for testing.

    :return: A sample FastRoute instance.
    :rtype: FastRoute
    '''

    return ModelObject.new(
        FastRoute,
        id="sample_route",
        endpoint='sample_router.sample_route',
        path='/sample',
        methods=['GET', 'POST'],
        status_code=200
    )

# ** fixture: fast_router
@pytest.fixture
def fast_router(fast_route: FastRoute) -> FastRouter: 
    '''
    A fixture that provendpointes a sample FastRouter instance for testing.

    :param fast_route: A sample FastRoute instance.
    :type fast_route: FastRoute
    :return: A sample FastRouter instance.
    :rtype: FastRouter
    '''

    return ModelObject.new(
        FastRouter,
        name='sample_router',
        routes=[fast_route]
    )

# *** tests

# ** test: fast_route_creation
def test_fast_route_creation(fast_route: FastRoute):
    '''
    Test the creation of a FastRoute instance.

    :param fast_route: A sample FastRoute instance.
    :type fast_route: FastRoute
    '''

    assert fast_route.id == 'sample_route'
    assert fast_route.endpoint == 'sample_router.sample_route'
    assert fast_route.path == '/sample'
    assert fast_route.methods == ['GET', 'POST']
    assert fast_route.status_code == 200

# ** test: fast_router_creation
def test_fast_router_creation(fast_router: FastRouter, fast_route: FastRoute):
    '''
    Test the creation of a FastRouter instance.

    :param fast_router: A sample FastRouter instance.
    :type fast_router: FastRouter
    :param fast_route: A sample FastRoute instance.
    :type fast_route: FastRoute
    '''

    assert fast_router.name == 'sample_router'
    assert len(fast_router.routes) == 1
    assert fast_router.routes[0] == fast_route

# ** test: fast_router_add_route
def test_fast_router_add_route(fast_router: FastRouter):
    '''
    Test adding a new route to the FastRouter instance.

    :param fast_router: A sample FastRouter instance.
    :type fast_router: FastRouter
    '''

    fast_router.add_route(
        endpoint='new_route',
        path='/new',
        methods=['GET'],
        status_code=201
    )

    assert len(fast_router.routes) == 2
    new_route = fast_router.routes[1]
    assert new_route.id == 'new_route'
    assert new_route.endpoint == 'sample_router.new_route'
    assert new_route.path == '/new'
    assert new_route.methods == ['GET']
    assert new_route.status_code == 201