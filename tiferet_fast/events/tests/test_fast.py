"""Tests for Fast API Domain Events."""

# *** imports

# ** core
import pytest
from unittest import mock

# ** infra
from tiferet import TiferetError
from tiferet.events import DomainEvent

# ** app
from ...domain import FastRoute, FastRouter
from ...interfaces import FastApiService
from ...events import GetRouters, GetRoute, GetStatusCode

# *** fixtures

# ** fixture: mock_fast_api_service
@pytest.fixture
def mock_fast_api_service() -> FastApiService:
    '''
    Mock FastApiService for testing.
    '''

    # Create a mock service.
    return mock.Mock(spec=FastApiService)

# ** fixture: sample_route
@pytest.fixture
def sample_route() -> FastRoute:
    '''
    Sample FastRoute instance for testing.
    '''

    # Create a sample route.
    return FastRoute(
        id='add',
        endpoint='calc.add',
        path='/add',
        methods=['GET'],
        status_code=200,
    )

# ** fixture: sample_router
@pytest.fixture
def sample_router(sample_route) -> FastRouter:
    '''
    Sample FastRouter instance for testing.
    '''

    # Create a sample router.
    return FastRouter(
        name='calc',
        prefix='/calc',
        routes=[sample_route],
    )

# *** tests

# ** test: get_routers_success
def test_get_routers_success(mock_fast_api_service: FastApiService, sample_router: FastRouter) -> None:
    '''
    Test successful retrieval of all routers via GetRouters.

    :param mock_fast_api_service: The mock Fast API service.
    :type mock_fast_api_service: FastApiService
    :param sample_router: The sample router instance.
    :type sample_router: FastRouter
    '''

    # Arrange the service to return the sample router.
    mock_fast_api_service.get_routers.return_value = [sample_router]

    # Execute the event via the static DomainEvent.handle interface.
    result = DomainEvent.handle(
        GetRouters,
        dependencies={'fast_api_service': mock_fast_api_service},
    )

    # Assert the result and service call.
    assert result == [sample_router]
    mock_fast_api_service.get_routers.assert_called_once()

# ** test: get_route_success
def test_get_route_success(mock_fast_api_service: FastApiService, sample_route: FastRoute) -> None:
    '''
    Test successful retrieval of a route via GetRoute.

    :param mock_fast_api_service: The mock Fast API service.
    :type mock_fast_api_service: FastApiService
    :param sample_route: The sample route instance.
    :type sample_route: FastRoute
    '''

    # Arrange the service to return the sample route.
    mock_fast_api_service.get_route.return_value = sample_route

    # Execute the event via the static DomainEvent.handle interface.
    result = DomainEvent.handle(
        GetRoute,
        dependencies={'fast_api_service': mock_fast_api_service},
        endpoint='calc.add',
    )

    # Assert the result and service call.
    assert result is sample_route
    mock_fast_api_service.get_route.assert_called_once_with(
        route_id='add',
        router_name='calc',
    )

# ** test: get_route_not_found
def test_get_route_not_found(mock_fast_api_service: FastApiService) -> None:
    '''
    Test that GetRoute raises TiferetError when route is not found.

    :param mock_fast_api_service: The mock Fast API service.
    :type mock_fast_api_service: FastApiService
    '''

    # Arrange the service to return None.
    mock_fast_api_service.get_route.return_value = None

    # Execute the event and assert TiferetError is raised.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            GetRoute,
            dependencies={'fast_api_service': mock_fast_api_service},
            endpoint='calc.unknown',
        )

    # Verify the error code.
    assert exc_info.value.error_code == 'FAST_ROUTE_NOT_FOUND'

    # Verify the service was called.
    mock_fast_api_service.get_route.assert_called_once_with(
        route_id='unknown',
        router_name='calc',
    )

# ** test: get_status_code_success
def test_get_status_code_success(mock_fast_api_service: FastApiService) -> None:
    '''
    Test successful retrieval of a status code via GetStatusCode.

    :param mock_fast_api_service: The mock Fast API service.
    :type mock_fast_api_service: FastApiService
    '''

    # Arrange the service to return a status code.
    mock_fast_api_service.get_status_code.return_value = 400

    # Execute the event via the static DomainEvent.handle interface.
    result = DomainEvent.handle(
        GetStatusCode,
        dependencies={'fast_api_service': mock_fast_api_service},
        error_code='INVALID_INPUT',
    )

    # Assert the result and service call.
    assert result == 400
    mock_fast_api_service.get_status_code.assert_called_once_with(
        error_code='INVALID_INPUT',
    )
