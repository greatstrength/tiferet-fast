"""Tests for Fast API domain models."""

# *** imports

# ** infra
import pytest

# ** app
from ..fast import (
    FastRoute,
    FastRouter,
)

# *** fixtures

# ** fixture: fast_route
@pytest.fixture
def fast_route() -> FastRoute:
    '''
    A fixture that provides a sample FastRoute instance for testing.

    :return: A sample FastRoute instance.
    :rtype: FastRoute
    '''

    return FastRoute(
        id='sample_route',
        endpoint='sample_router.sample_route',
        path='/sample',
        methods=['GET', 'POST'],
        status_code=200,
    )

# ** fixture: fast_router
@pytest.fixture
def fast_router(fast_route: FastRoute) -> FastRouter:
    '''
    A fixture that provides a sample FastRouter instance for testing.

    :param fast_route: A sample FastRoute instance.
    :type fast_route: FastRoute
    :return: A sample FastRouter instance.
    :rtype: FastRouter
    '''

    return FastRouter(
        name='sample_router',
        prefix='/sample',
        routes=[fast_route],
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

# ** test: fast_route_default_status_code
def test_fast_route_default_status_code():
    '''
    Test that FastRoute defaults status_code to 200.
    '''

    route = FastRoute(
        id='test',
        endpoint='router.test',
        path='/test',
        methods=['GET'],
    )

    assert route.status_code == 200

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
    assert fast_router.prefix == '/sample'
    assert len(fast_router.routes) == 1
    assert fast_router.routes[0] == fast_route

# ** test: fast_router_default_routes
def test_fast_router_default_routes():
    '''
    Test that FastRouter defaults to an empty routes list.
    '''

    router = FastRouter(
        name='empty_router',
    )

    assert router.routes == []
    assert router.prefix is None
