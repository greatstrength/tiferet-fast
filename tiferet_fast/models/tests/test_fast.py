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

# ** fixture: flask_route
@pytest.fixture
def flask_route() -> FastRoute:
    '''
    A fixture that provendpointes a sample FastRoute instance for testing.

    :return: A sample FastRoute instance.
    :rtype: FastRoute
    '''

    return ModelObject.new(
        FastRoute,
        endpoint='sample_router.sample_route',
        path='/sample',
        methods=['GET', 'POST'],
        status_code=200
    )

# ** fixture: flask_blueprint
@pytest.fixture
def fast_router(flask_route: FastRoute) -> FastRouter: 
    '''
    A fixture that provendpointes a sample FastRouter instance for testing.

    :param flask_route: A sample FastRoute instance.
    :type flask_route: FastRoute
    :return: A sample FastRouter instance.
    :rtype: FastRouter
    '''

    return ModelObject.new(
        FastRouter,
        name='sample_router',
        routes=[flask_route]
    )

# *** tests

# ** test: flask_route_creation
def test_flask_route_creation(flask_route: FastRoute):
    '''
    Test the creation of a FastRoute instance.

    :param flask_route: A sample FastRoute instance.
    :type flask_route: FastRoute
    '''

    assert flask_route.endpoint == 'sample_router.sample_route'
    assert flask_route.path == '/sample'
    assert flask_route.methods == ['GET', 'POST']
    assert flask_route.status_code == 200

# ** test: flask_blueprint_creation
def test_flask_blueprint_creation(fast_router: FastRouter, flask_route: FastRoute):
    '''
    Test the creation of a FastRouter instance.

    :param flask_blueprint: A sample FastRouter instance.
    :type flask_blueprint: FastRouter
    :param flask_route: A sample FastRoute instance.
    :type flask_route: FastRoute
    '''

    assert fast_router.name == 'sample_router'
    assert len(fast_router.routes) == 1
    assert fast_router.routes[0] == flask_route

# ** test: flask_blueprint_add_route
def test_flask_blueprint_add_route(fast_router: FastRouter):
    '''
    Test adding a new route to the FastRouter instance.

    :param flask_blueprint: A sample FastRouter instance.
    :type flask_blueprint: FastRouter
    '''

    fast_router.add_route(
        endpoint='new_route',
        path='/new',
        methods=['GET'],
        status_code=201
    )

    assert len(fast_router.routes) == 2
    new_route = fast_router.routes[1]
    assert new_route.endpoint == 'sample_router.new_route'
    assert new_route.path == '/new'
    assert new_route.methods == ['GET']
    assert new_route.status_code == 201
