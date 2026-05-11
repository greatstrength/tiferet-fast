"""Tests for FastAPI Builder."""

# *** imports

# ** infra
import pytest
from unittest import mock
from functools import partial
from fastapi.routing import APIRouter
from tiferet_openapi.domain import ApiRoute, ApiRouter

# ** app
from ..fast import FastApiBuilder

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

# ** fixture: builder
@pytest.fixture
def builder() -> FastApiBuilder:
    '''
    Fixture to provide a FastApiBuilder with mocked internals.
    '''

    # Create a builder with a mocked service provider.
    builder = FastApiBuilder.__new__(FastApiBuilder)
    builder.service_provider = mock.Mock()
    builder.cache = mock.Mock()
    return builder

# *** tests

# ** test: resolve_model_none
def test_resolve_model_none():
    '''
    Test that resolve_model returns None when given None.
    '''

    # Assert None is returned for None input.
    assert FastApiBuilder.resolve_model(None) is None

# ** test: resolve_model_empty_string
def test_resolve_model_empty_string():
    '''
    Test that resolve_model returns None when given an empty string.
    '''

    # Assert None is returned for empty string input.
    assert FastApiBuilder.resolve_model('') is None

# ** test: resolve_model_valid_path
def test_resolve_model_valid_path():
    '''
    Test that resolve_model resolves a valid dotted import path.
    '''

    # Resolve pydantic.BaseModel as a smoke test.
    from pydantic import BaseModel
    result = FastApiBuilder.resolve_model('pydantic.BaseModel')

    # Assert the resolved class matches.
    assert result is BaseModel

# ** test: resolve_model_invalid_module
def test_resolve_model_invalid_module():
    '''
    Test that resolve_model raises ModuleNotFoundError for an invalid module.
    '''

    # Assert ModuleNotFoundError is raised.
    with pytest.raises(ModuleNotFoundError):
        FastApiBuilder.resolve_model('nonexistent.module.SomeClass')

# ** test: resolve_model_invalid_class
def test_resolve_model_invalid_class():
    '''
    Test that resolve_model raises AttributeError for an invalid class name.
    '''

    # Assert AttributeError is raised.
    with pytest.raises(AttributeError):
        FastApiBuilder.resolve_model('pydantic.NonExistentClass')

# ** test: build_router_plain
def test_build_router_plain(builder: FastApiBuilder, sample_router_plain: ApiRouter, mock_view_func: mock.Mock):
    '''
    Test build_router with a plain router (no Swagger metadata).

    :param builder: A FastApiBuilder instance.
    :type builder: FastApiBuilder
    :param sample_router_plain: A sample ApiRouter without Swagger metadata.
    :type sample_router_plain: ApiRouter
    :param mock_view_func: A mock view function.
    :type mock_view_func: mock.Mock
    '''

    # Build the router.
    api_router = builder.build_router(sample_router_plain, view_func=mock_view_func)

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
def test_build_router_with_swagger(builder: FastApiBuilder, sample_router_with_swagger: ApiRouter, mock_view_func: mock.Mock):
    '''
    Test build_router with Swagger metadata.

    :param builder: A FastApiBuilder instance.
    :type builder: FastApiBuilder
    :param sample_router_with_swagger: A sample ApiRouter with Swagger metadata.
    :type sample_router_with_swagger: ApiRouter
    :param mock_view_func: A mock view function.
    :type mock_view_func: mock.Mock
    '''

    # Build the router.
    api_router = builder.build_router(sample_router_with_swagger, view_func=mock_view_func)

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
