"""Tests for FastAPI Blueprints."""

# *** imports

# ** core
from unittest import mock

# ** infra
import pytest
from fastapi.routing import APIRouter
from tiferet import TiferetError, use_tester
from tiferet.blueprints import core
from tiferet.contexts.cache import CacheContext
from tiferet.domain import AppSession
from tiferet_openapi import create_openapi_request_context
from tiferet_openapi.domain import ApiRoute, ApiRouter

# ** app
from ...assets.core import (
    APP_FLAG,
    GET_ROUTE_EVT_SERVICE_ID,
    GET_ROUTERS_EVT_SERVICE_ID,
    GET_STATUS_CODE_EVT_SERVICE_ID,
)
from ...contexts.fast import FastApiContext
from ..fast import (
    build_fast_session_context,
    build_router,
    get_route_handler,
    get_routers,
    get_routers_handler,
    get_status_code_handler,
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

# ** fixture: app_session
@pytest.fixture
def app_session() -> AppSession:
    '''
    Provide a sample AppSession for FastAPI session composition.

    :return: An AppSession bound to the test FastAPI interface.
    :rtype: AppSession
    '''

    # Return a minimal AppSession for session composition.
    return AppSession(id='test_fast', name='Test Fast API')

# ** fixture: cache
@pytest.fixture
def cache() -> CacheContext:
    '''
    Provide the bootstrap cache pre-seeded with framework defaults.

    :return: A CacheContext seeded by core.build_cache.
    :rtype: CacheContext
    '''

    # Build the framework default cache.
    return core.build_cache()

# *** tests

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

# *** testers

# ** tester: test_resolve_model
@use_tester(
    type='generic',
    target_cls=resolve_model,
)
class TestResolveModel:
    '''
    Generic tester for resolve_model.
    '''

    # * test: none
    def test_resolve_model_none(self, session) -> None:
        '''
        Test that resolve_model returns None when given None.

        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Exercise resolve_model with no path.
        result = session.given(model_path=None).run(target=resolve_model)

        # Assert None is returned.
        assert result is None

    # * test: empty_string
    def test_resolve_model_empty_string(self, session) -> None:
        '''
        Test that resolve_model returns None when given an empty string.

        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Exercise resolve_model with an empty path.
        result = session.given(model_path='').run(target=resolve_model)

        # Assert None is returned.
        assert result is None

    # * test: valid_path
    def test_resolve_model_valid_path(self, session) -> None:
        '''
        Test that resolve_model resolves a valid dotted import path.

        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Resolve pydantic.BaseModel as a smoke test.
        from pydantic import BaseModel
        result = session.given(model_path='pydantic.BaseModel').run(target=resolve_model)

        # Assert the resolved class matches.
        assert result is BaseModel

    # * test: invalid_module
    def test_resolve_model_invalid_module(self, session) -> None:
        '''
        Test that resolve_model raises TiferetError for an invalid module.

        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Assert a structured model-resolution error is raised.
        with pytest.raises(TiferetError) as exc_info:
            session.given(model_path='nonexistent.module.SomeClass').run(target=resolve_model)

        # Assert the error code, path, and non-empty reason.
        assert exc_info.value.error_code == 'OPENAPI_MODEL_RESOLUTION_FAILED'
        assert exc_info.value.kwargs['model_path'] == 'nonexistent.module.SomeClass'
        assert isinstance(exc_info.value.kwargs['reason'], str)
        assert exc_info.value.kwargs['reason']

    # * test: invalid_class
    def test_resolve_model_invalid_class(self, session) -> None:
        '''
        Test that resolve_model raises TiferetError for an invalid class name.

        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Assert a structured model-resolution error is raised.
        with pytest.raises(TiferetError) as exc_info:
            session.given(model_path='pydantic.NonExistentClass').run(target=resolve_model)

        # Assert the error code, path, and non-empty reason.
        assert exc_info.value.error_code == 'OPENAPI_MODEL_RESOLUTION_FAILED'
        assert exc_info.value.kwargs['model_path'] == 'pydantic.NonExistentClass'
        assert isinstance(exc_info.value.kwargs['reason'], str)
        assert exc_info.value.kwargs['reason']

# ** tester: test_get_routers
@use_tester(
    type='generic',
    target_cls=get_routers,
)
class TestGetRouters:
    '''
    Generic tester for get_routers.
    '''

    # * test: returns_configured_routers
    def test_get_routers_returns_configured_routers(
            self,
            session,
            sample_router_plain: ApiRouter,
        ) -> None:
        '''
        Verify get_routers returns interface_context.get_routers().

        :param session: A fresh test session.
        :type session: TestSessionContext
        :param sample_router_plain: A sample ApiRouter without Swagger metadata.
        :type sample_router_plain: ApiRouter
        '''

        # Build a mock interface context exposing get_routers().
        interface_context = mock.Mock()
        interface_context.get_routers = mock.Mock(return_value=[sample_router_plain])

        # Exercise get_routers against the mock interface context.
        result = session.given(interface_context=interface_context).run(target=get_routers)

        # Assert the context method was called and the router list is returned.
        interface_context.get_routers.assert_called_once_with()
        assert result == [sample_router_plain]

    # * test: empty
    def test_get_routers_empty(self, session) -> None:
        '''
        Verify get_routers returns an empty list when no routers are configured.

        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Build a mock interface context with no routers.
        interface_context = mock.Mock()
        interface_context.get_routers = mock.Mock(return_value=[])

        # Exercise get_routers against the mock interface context.
        result = session.given(interface_context=interface_context).run(target=get_routers)

        # Assert the result is empty.
        assert result == []

# ** tester: test_get_route_handler
@use_tester(
    type='generic',
    target_cls=get_route_handler,
)
class TestGetRouteHandler:
    '''
    Generic tester for get_route_handler.
    '''

    # * test: resolves_service_id_and_app_flag
    def test_get_route_handler_resolves_service_id_and_app_flag(self, session) -> None:
        '''
        Verify the built closure resolves the get-route event with the
        service id and app flag, then calls execute(**kwargs).

        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Build a mock get_dependency resolver returning a mock event.
        get_route_evt = mock.Mock()
        get_route_evt.execute = mock.Mock(return_value=mock.sentinel.route)
        get_dependency = mock.Mock(return_value=get_route_evt)

        # Exercise get_route_handler to build the closure, then call it.
        handler = session.given(get_dependency=get_dependency).run(target=get_route_handler)
        result = handler(id='calc.add')

        # Assert the resolution shape and passthrough return value.
        get_dependency.assert_called_once_with(GET_ROUTE_EVT_SERVICE_ID, APP_FLAG)
        get_route_evt.execute.assert_called_once_with(id='calc.add')
        assert result is mock.sentinel.route

# ** tester: test_get_status_code_handler
@use_tester(
    type='generic',
    target_cls=get_status_code_handler,
)
class TestGetStatusCodeHandler:
    '''
    Generic tester for get_status_code_handler.
    '''

    # * test: resolves_service_id_and_app_flag
    def test_get_status_code_handler_resolves_service_id_and_app_flag(self, session) -> None:
        '''
        Verify the built closure resolves the get-status-code event with the
        service id and app flag, then calls execute(**kwargs).

        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Build a mock get_dependency resolver returning a mock event.
        get_status_code_evt = mock.Mock()
        get_status_code_evt.execute = mock.Mock(return_value=mock.sentinel.status_code)
        get_dependency = mock.Mock(return_value=get_status_code_evt)

        # Exercise get_status_code_handler to build the closure, then call it.
        handler = session.given(get_dependency=get_dependency).run(target=get_status_code_handler)
        result = handler(error_code='INVALID_REQUEST')

        # Assert the resolution shape and passthrough return value.
        get_dependency.assert_called_once_with(GET_STATUS_CODE_EVT_SERVICE_ID, APP_FLAG)
        get_status_code_evt.execute.assert_called_once_with(error_code='INVALID_REQUEST')
        assert result is mock.sentinel.status_code

# ** tester: test_get_routers_handler
@use_tester(
    type='generic',
    target_cls=get_routers_handler,
)
class TestGetRoutersHandler:
    '''
    Generic tester for get_routers_handler.
    '''

    # * test: resolves_service_id_and_app_flag
    def test_get_routers_handler_resolves_service_id_and_app_flag(self, session) -> None:
        '''
        Verify the built closure resolves the get-routers event with the
        service id and app flag, then calls execute(**kwargs).

        :param session: A fresh test session.
        :type session: TestSessionContext
        '''

        # Build a mock get_dependency resolver returning a mock event.
        get_routers_evt = mock.Mock()
        get_routers_evt.execute = mock.Mock(return_value=mock.sentinel.routers)
        get_dependency = mock.Mock(return_value=get_routers_evt)

        # Exercise get_routers_handler to build the closure, then call it.
        handler = session.given(get_dependency=get_dependency).run(target=get_routers_handler)
        result = handler()

        # Assert the resolution shape and passthrough return value.
        get_dependency.assert_called_once_with(GET_ROUTERS_EVT_SERVICE_ID, APP_FLAG)
        get_routers_evt.execute.assert_called_once_with()
        assert result is mock.sentinel.routers

# ** tester: test_build_fast_session_context
@use_tester(
    type='generic',
    target_cls=build_fast_session_context,
)
class TestBuildFastSessionContext:
    '''
    Generic tester for build_fast_session_context.
    '''

    # * test: constructs_wired_fast_api_context
    def test_build_fast_session_context_constructs_wired_fast_api_context(
            self,
            session,
            app_session: AppSession,
            cache: CacheContext,
        ) -> None:
        '''
        Verify build_fast_session_context constructs a wired FastApiContext.

        :param session: A fresh test session.
        :type session: TestSessionContext
        :param app_session: The AppSession domain object.
        :type app_session: AppSession
        :param cache: The bootstrap cache.
        :type cache: CacheContext
        '''

        # Exercise build_fast_session_context with cache and session only.
        result = session.given(app_session=app_session, cache=cache).run(
            target=build_fast_session_context
        )

        # Assert the constructed context, bound domain, and default handlers.
        assert isinstance(result, FastApiContext)
        assert result.domain is app_session
        assert result._create_request is create_openapi_request_context
        assert result._build_response is core.response_handler
        assert callable(result._get_route)
        assert callable(result._get_status_code)
        assert callable(result._get_routers)

    # * test: defaults_to_openapi_request_factory
    def test_build_fast_session_context_defaults_to_openapi_request_factory(
            self,
            session,
            app_session: AppSession,
            cache: CacheContext,
        ) -> None:
        '''
        Verify omitting create_request_handler wires create_openapi_request_context.

        :param session: A fresh test session.
        :type session: TestSessionContext
        :param app_session: The AppSession domain object.
        :type app_session: AppSession
        :param cache: The bootstrap cache.
        :type cache: CacheContext
        '''

        # Exercise build_fast_session_context without a request handler.
        result = session.given(app_session=app_session, cache=cache).run(
            target=build_fast_session_context
        )

        # Assert the OpenAPI request factory is wired without wrapping.
        assert result._create_request is create_openapi_request_context

    # * test: accepts_custom_request_handler
    def test_build_fast_session_context_accepts_custom_request_handler(
            self,
            session,
            app_session: AppSession,
            cache: CacheContext,
        ) -> None:
        '''
        Verify build_fast_session_context assigns a custom request handler as-is.

        :param session: A fresh test session.
        :type session: TestSessionContext
        :param app_session: The AppSession domain object.
        :type app_session: AppSession
        :param cache: The bootstrap cache.
        :type cache: CacheContext
        '''

        # Exercise build_fast_session_context with a custom request handler.
        custom_handler = mock.Mock()
        result = session.given(
            app_session=app_session,
            cache=cache,
            create_request_handler=custom_handler,
        ).run(target=build_fast_session_context)

        # Assert the custom request handler is wired without wrapping.
        assert result._create_request is custom_handler
