"""Tests for FastAPI Blueprints."""

# *** imports

# ** infra
import pytest
from unittest import mock
from functools import partial
from fastapi.routing import APIRouter
from tiferet_openapi.domain import ApiRoute, ApiRouter

# ** app
from ..fast import resolve_model, get_routers, build_router

# *** fixtures

# ** fixture: sample_route_plain
@pytest.fixture
def sample_route_plain() -> ApiRoute:
    '''
    Fixture to provide a sample ApiRoute without Swagger metadata.
    '''

    # Create an ApiRoute instance without Swagger fields.
    return ApiRoute(
        id='add',
        endpoint='calc.add',
        path='/add',
        methods=['POST'],
        status_code=200,
    )

# ** fixture: sample_route_with_swagger
@pytest.fixture
def sample_route_with_swagger() -> ApiRoute:
    '''
    Fixture to provide a sample ApiRoute with Swagger metadata.
    '''

    # Create an ApiRoute instance with Swagger fields.
    return ApiRoute(
        id='add',
        endpoint='calc.add',
        path='/add',
        methods=['POST'],
        status_code=201,
        summary='Add two numbers',
        description='Adds two numbers and returns the result.',
        tags=['calculator', 'math'],
        response_model='pydantic.BaseModel',
    )

# ** fixture: sample_router_plain
@pytest.fixture
def sample_router_plain(sample_route_plain: ApiRoute) -> ApiRouter:
    '''
    Fixture to provide a sample ApiRouter without Swagger metadata.
    '''

    # Create an ApiRouter instance.
    return ApiRouter(
        name='calc',
        prefix='/calc',
        routes=[sample_route_plain],
    )

# ** fixture: sample_router_with_swagger
@pytest.fixture
def sample_router_with_swagger(sample_route_with_swagger: ApiRoute) -> ApiRouter:
    '''
    Fixture to provide a sample ApiRouter with Swagger metadata.
    '''

    # Create an ApiRouter instance.
    return ApiRouter(
        name='calc',
        prefix='/calc',
        routes=[sample_route_with_swagger],
    )

# ** fixture: mock_view_func
@pytest.fixture
def mock_view_func() -> mock.Mock:
    '''
    Fixture to provide a mock view function.
    '''

    # Create a mock view function.
    return mock.Mock()

# ** fixture: mock_service_provider
@pytest.fixture
def mock_service_provider() -> mock.Mock:
    '''
    Fixture to provide a mock service provider.
    '''

    # Create a mock service provider.
    return mock.Mock()

# *** tests

# ** test: resolve_model_none
def test_resolve_model_none():
    '''
    Test that resolve_model returns None when given None.
    '''

    # Assert None is returned for None input.
    assert resolve_model(None) is None

# ** test: resolve_model_empty_string
def test_resolve_model_empty_string():
    '''
    Test that resolve_model returns None when given an empty string.
    '''

    # Assert None is returned for empty string input.
    assert resolve_model('') is None

# ** test: resolve_model_valid_path
def test_resolve_model_valid_path():
    '''
    Test that resolve_model resolves a valid dotted import path.
    '''

    # Resolve pydantic.BaseModel as a smoke test.
    from pydantic import BaseModel
    result = resolve_model('pydantic.BaseModel')

    # Assert the resolved class matches.
    assert result is BaseModel

# ** test: resolve_model_invalid_module
def test_resolve_model_invalid_module():
    '''
    Test that resolve_model raises ModuleNotFoundError for an invalid module.
    '''

    # Assert ModuleNotFoundError is raised.
    with pytest.raises(ModuleNotFoundError):
        resolve_model('nonexistent.module.SomeClass')

# ** test: resolve_model_invalid_class
def test_resolve_model_invalid_class():
    '''
    Test that resolve_model raises AttributeError for an invalid class name.
    '''

    # Assert AttributeError is raised.
    with pytest.raises(AttributeError):
        resolve_model('pydantic.NonExistentClass')

# ** test: get_routers
def test_get_routers(mock_service_provider: mock.Mock):
    '''
    Test that get_routers resolves and executes the event from the service provider.

    :param mock_service_provider: A mock service provider.
    :type mock_service_provider: mock.Mock
    '''

    # Arrange the mock to return a list of routers.
    mock_evt = mock.Mock()
    mock_evt.execute.return_value = ['router1', 'router2']
    mock_service_provider.get_service.return_value = mock_evt

    # Execute the blueprint function.
    result = get_routers(mock_service_provider)

    # Assert the event was resolved and executed correctly.
    mock_service_provider.get_service.assert_called_once_with('get_routers_evt')
    mock_evt.execute.assert_called_once()
    assert result == ['router1', 'router2']

# ** test: build_router_plain
def test_build_router_plain(sample_router_plain: ApiRouter, mock_view_func: mock.Mock):
    '''
    Test build_router with a plain router (no Swagger metadata).

    :param sample_router_plain: A sample ApiRouter without Swagger metadata.
    :type sample_router_plain: ApiRouter
    :param mock_view_func: A mock view function.
    :type mock_view_func: mock.Mock
    '''

    # Build the router.
    api_router = build_router(sample_router_plain, view_func=mock_view_func)

    # Assert the router is configured correctly.
    assert isinstance(api_router, APIRouter)
    assert len(api_router.routes) == 1

    # Assert the route has correct base attributes.
    route = api_router.routes[0]
    assert route.path == '/calc/add'
    assert route.methods == {'POST'}
    assert route.name == 'calc.add'

    # Assert tags fall back to the router name (router-level 'calc' + route-level 'calc').
    assert route.tags == ['calc', 'calc']

    # Assert no response model is set.
    assert route.response_model is None

# ** test: build_router_with_swagger
def test_build_router_with_swagger(sample_router_with_swagger: ApiRouter, mock_view_func: mock.Mock):
    '''
    Test build_router with Swagger metadata.

    :param sample_router_with_swagger: A sample ApiRouter with Swagger metadata.
    :type sample_router_with_swagger: ApiRouter
    :param mock_view_func: A mock view function.
    :type mock_view_func: mock.Mock
    '''

    # Build the router.
    api_router = build_router(sample_router_with_swagger, view_func=mock_view_func)

    # Assert the router is configured correctly.
    assert isinstance(api_router, APIRouter)
    assert len(api_router.routes) == 1

    # Assert the route has correct Swagger attributes.
    route = api_router.routes[0]
    assert route.path == '/calc/add'
    assert route.summary == 'Add two numbers'
    assert route.description == 'Adds two numbers and returns the result.'
    assert route.tags == ['calc', 'calculator', 'math']

    # Assert the response model is resolved.
    from pydantic import BaseModel
    assert route.response_model is BaseModel
