"""Tests for FastAPI Blueprints."""

# *** imports

# ** infra
import pytest
from unittest import mock
from functools import partial
from fastapi.routing import APIRouter
from starlette_context import plugins, request_cycle_context
from starlette_context.middleware import RawContextMiddleware
from tiferet_openapi.contexts.request import OpenApiRequestContext
from tiferet_openapi.domain import ApiRoute, ApiRouter

# ** app
from ...assets.context_headers import (
    CORRELATION_ID_HEADER_CONST_KEY,
    DEFAULT_CORRELATION_ID_HEADER,
    DEFAULT_REQUEST_ID_HEADER,
    REQUEST_ID_HEADER_CONST_KEY,
    parse_context_header_options,
)
from ..fast import (
    build_fast_app,
    build_fast_session_context,
    build_router,
    create_fast_request_handler,
    get_routers,
    resolve_model,
)

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

# ** test: create_fast_request_handler_copies_context_headers
def test_create_fast_request_handler_copies_context_headers():
    '''
    Test that the adapter copies plugin ids onto OpenApiRequestContext headers
    without setting session_id from the HTTP request id.
    '''

    # Build the adapter with library default header names.
    header_keys = parse_context_header_options({})
    handler = create_fast_request_handler(header_keys)
    request_id = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    correlation_id = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'

    # Construct a request inside a request-cycle context.
    with request_cycle_context({
        DEFAULT_REQUEST_ID_HEADER: request_id,
        DEFAULT_CORRELATION_ID_HEADER: correlation_id,
    }):
        request_context = handler(
            'calc_fast_api',
            'calc.add',
            {'content-type': 'application/json'},
            {'a': 1},
        )

    # Assert the constructed type remains OpenApiRequestContext.
    assert isinstance(request_context, OpenApiRequestContext)
    assert request_context.headers[DEFAULT_REQUEST_ID_HEADER] == request_id
    assert request_context.headers[DEFAULT_CORRELATION_ID_HEADER] == correlation_id
    assert request_context.headers['interface_id'] == 'calc_fast_api'
    assert request_context.feature_id == 'calc.add'
    assert request_context.data == {'a': 1}

    # Assert session_id is derived separately and is not the HTTP request id.
    assert 'session_id' not in request_context.headers
    assert request_context.session_id != request_id
    assert '-' in request_context.session_id

# ** test: create_fast_request_handler_without_request_cycle
def test_create_fast_request_handler_without_request_cycle():
    '''
    Test that the adapter still constructs OpenApiRequestContext outside HTTP.
    '''

    # Construct a request with no starlette_context request cycle.
    handler = create_fast_request_handler(parse_context_header_options({}))
    request_context = handler('calc_fast_api', 'calc.add', {}, {})

    # Assert construction succeeds and plugin ids are not invented.
    assert isinstance(request_context, OpenApiRequestContext)
    assert DEFAULT_REQUEST_ID_HEADER not in request_context.headers
    assert request_context.headers['interface_id'] == 'calc_fast_api'
    assert request_context.session_id

# ** test: build_fast_session_context_default_handler_copies_headers
@mock.patch('tiferet_fast.blueprints.fast.core.compose_session_context')
@mock.patch('tiferet_fast.blueprints.fast.core.build_service_resolver')
@mock.patch('tiferet_fast.blueprints.fast.core.build_app_service_container')
def test_build_fast_session_context_default_handler_copies_headers(
        mock_build_container: mock.Mock,
        mock_build_resolver: mock.Mock,
        mock_compose: mock.Mock):
    '''
    Test that omitting create_request_handler defaults to the header adapter.
    '''

    # Compose a session context without an explicit request handler.
    build_fast_session_context(mock.Mock(), mock.Mock())
    handler = mock_compose.call_args.kwargs['create_request_handler']
    request_id = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'

    # Exercise the default handler inside a request cycle.
    with request_cycle_context({
        DEFAULT_REQUEST_ID_HEADER: request_id,
        DEFAULT_CORRELATION_ID_HEADER: 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
    }):
        request_context = handler('calc_fast_api', 'calc.add', {}, {})

    # Assert the default handler copied plugin ids and left session_id alone.
    assert isinstance(request_context, OpenApiRequestContext)
    assert request_context.headers[DEFAULT_REQUEST_ID_HEADER] == request_id
    assert request_context.session_id != request_id

# ** test: build_fast_session_context_does_not_wrap_explicit_handler
@mock.patch('tiferet_fast.blueprints.fast.core.compose_session_context')
@mock.patch('tiferet_fast.blueprints.fast.core.build_service_resolver')
@mock.patch('tiferet_fast.blueprints.fast.core.build_app_service_container')
def test_build_fast_session_context_does_not_wrap_explicit_handler(
        mock_build_container: mock.Mock,
        mock_build_resolver: mock.Mock,
        mock_compose: mock.Mock):
    '''
    Test that an explicit create_request_handler is not wrapped again.
    '''

    # Compose a session context with a caller-supplied request handler.
    explicit_handler = mock.Mock(name='explicit_handler')
    build_fast_session_context(
        mock.Mock(),
        mock.Mock(),
        create_request_handler=explicit_handler,
    )

    # Assert the explicit handler is passed through unchanged.
    assert mock_compose.call_args.kwargs['create_request_handler'] is explicit_handler

# ** test: build_fast_app_mounts_keyed_middleware_and_adapter
@mock.patch('tiferet_fast.blueprints.fast.get_routers', return_value=[])
@mock.patch('tiferet_fast.blueprints.fast.build_fast_session_context')
@mock.patch('tiferet_fast.blueprints.fast.core.get_app_session')
@mock.patch('tiferet_fast.blueprints.fast.core.build_cache')
def test_build_fast_app_mounts_keyed_middleware_and_adapter(
        mock_build_cache: mock.Mock,
        mock_get_app_session: mock.Mock,
        mock_build_session_context: mock.Mock,
        mock_get_routers: mock.Mock):
    '''
    Test that build_fast_app keys both plugins and passes the header adapter.
    '''

    # Assemble an app whose session overrides both closed header names.
    app_session = mock.Mock()
    app_session.constants = {
        REQUEST_ID_HEADER_CONST_KEY: 'X-Custom-Request-ID',
        CORRELATION_ID_HEADER_CONST_KEY: 'X-Custom-Correlation-ID',
    }
    mock_get_app_session.return_value = app_session
    fast_app = build_fast_app('calc_fast_api')

    # Assert both plugins are mounted and keyed from the parsed names.
    middleware = fast_app.user_middleware[0]
    assert middleware.cls is RawContextMiddleware
    mounted_plugins = middleware.kwargs['plugins']
    assert isinstance(mounted_plugins[0], plugins.RequestIdPlugin)
    assert isinstance(mounted_plugins[1], plugins.CorrelationIdPlugin)
    assert mounted_plugins[0].key == 'X-Custom-Request-ID'
    assert mounted_plugins[1].key == 'X-Custom-Correlation-ID'

    # Assert the composed session received the header-copying request adapter.
    passed_handler = mock_build_session_context.call_args.kwargs['create_request_handler']
    with request_cycle_context({
        'X-Custom-Request-ID': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'X-Custom-Correlation-ID': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
    }):
        request_context = passed_handler('calc_fast_api', 'calc.add', {}, {})
    assert isinstance(request_context, OpenApiRequestContext)
    assert request_context.headers['X-Custom-Request-ID'] == 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    assert request_context.headers['X-Custom-Correlation-ID'] == 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
    assert request_context.session_id != 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
