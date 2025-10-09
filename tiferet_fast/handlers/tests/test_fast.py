"""Tests for Fast API Handlers."""

# *** imports

# ** core
import pytest
from unittest import mock

# ** infra
from tiferet import ModelObject

# ** app
from ...handlers import FastApiHandler
from ...models import (
    FastRouter,
    FastRoute
)
from ...contracts import FastApiRepository

# *** fixtures

# ** fixture: fast_repo
@pytest.fixture
def fast_repo():
    '''
    Fixture to create a mock FastApiRepository.
    '''

    # Create a mock repository.
    return mock.Mock(spec=FastApiRepository)

# ** fixture: fast_api_handler
@pytest.fixture
def fast_api_handler(fast_repo):
    '''
    Fixture to create a FastApiHandler instance.
    '''

    # Create a FastApiHandler instance with the mock repository.
    return FastApiHandler(fast_repo)

# *** tests

# ** test: fast_api_handler_get_routers
def test_fast_api_handler_get_routers(fast_api_handler, fast_repo):
    '''
    Test retrieving all Fast API routers using the handler.
    '''

    # Mock the repository response.
    mock_router = ModelObject.new(
        FastRouter,
        name='calc',
        prefix='/calc',
        routes=[]
    )
    fast_repo.get_routers.return_value = [mock_router]

    # Get the routers.
    routers = fast_api_handler.get_routers()

    # Assert the repository was called and the result is correct.
    fast_repo.get_routers.assert_called_once()
    assert len(routers) == 1
    assert isinstance(routers[0], FastRouter)
    assert routers[0].name == 'calc'

# ** test: fast_api_handler_get_route
def test_fast_api_handler_get_route(fast_api_handler, fast_repo):
    '''
    Test retrieving a specific Fast API route using the handler.
    '''

    # Mock the repository response.
    mock_route = ModelObject.new(
        FastRoute,
        endpoint='calc.add',
        path='/calc/add',
        methods=['GET'],
        status_code=200
    )
    fast_repo.get_route.return_value = mock_route

    # Get the route.
    route = fast_api_handler.get_route('calc.add')

    # Assert the repository was called and the result is correct.
    fast_repo.get_route.assert_called_once_with(route_id='add', router_name='calc')
    assert isinstance(route, FastRoute)
    assert route.endpoint == 'calc.add'

# ** test: fast_api_handler_get_route_not_found
def test_fast_api_handler_get_route_not_found(fast_api_handler, fast_repo):
    '''
    Test error handling when a Fast API route is not found.
    '''

    # Mock the repository to return None.
    fast_repo.get_route.return_value = None

    # Assert that an error is raised.
    with pytest.raises(Exception) as exc_info:
        fast_api_handler.get_route('calc.unknown')
    assert 'FAST_ROUTE_NOT_FOUND' in str(exc_info.value)
    fast_repo.get_route.assert_called_once_with(route_id='unknown', router_name='calc')

# ** test: fast_api_handler_get_status_code
def test_fast_api_handler_get_status_code(fast_api_handler, fast_repo):
    '''
    Test retrieving an HTTP status code using the handler.
    '''

    # Mock the repository response.
    fast_repo.get_status_code.return_value = 400

    # Get the status code.
    status_code = fast_api_handler.get_status_code('INVALID_INPUT')

    # Assert the repository was called and the result is correct.
    fast_repo.get_status_code.assert_called_once_with(error_code='INVALID_INPUT')
    assert status_code == 400