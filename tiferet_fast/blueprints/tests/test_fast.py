"""Tests for FastAPI Blueprints."""

# *** imports

# ** core
from functools import partial
from inspect import signature
from unittest import mock

# ** infra
import pytest
from fastapi import FastAPI, Request
from fastapi.routing import APIRouter
from starlette_context import plugins, request_cycle_context
from starlette_context.middleware import RawContextMiddleware
from tiferet import TiferetError, use_tester
from tiferet.blueprints import core
from tiferet.contexts.cache import CacheContext
from tiferet.domain import AppSession
from tiferet_openapi import ApiRoute, ApiRouter
from tiferet_openapi.contexts.request import OpenApiRequestContext

# ** app
from ...assets.context_headers import (
    CORRELATION_ID_HEADER_CONST_KEY,
    DEFAULT_CORRELATION_ID_HEADER,
    DEFAULT_REQUEST_ID_HEADER,
    REQUEST_ID_HEADER_CONST_KEY,
    parse_context_header_options,
)
from ...assets.core import (
    APP_FLAG,
    GET_ROUTE_EVT_SERVICE_ID,
    GET_ROUTERS_EVT_SERVICE_ID,
    GET_STATUS_CODE_EVT_SERVICE_ID,
)
from ...contexts.fast import FastApiContext
from ..fast import (
    build_fast_app,
    build_fast_session_context,
    build_router,
    create_fast_request_handler,
    get_route_handler,
    get_routers,
    get_routers_handler,
    get_status_code_handler,
    resolve_model,
    run,
)

# *** functions

# ** function: iter_app_routes
def iter_app_routes(app: FastAPI):
    '''
    Yield routes from a FastAPI app, including FastAPI 0.141 included routers.

    FastAPI 0.141 stores ``include_router`` results as ``_IncludedRouter``
    objects on ``app.routes`` (``path`` is None) instead of flattening
    ``APIRoute`` entries. Nested routes live on ``original_router.routes``.

    :param app: The assembled FastAPI application.
    :type app: FastAPI
    :return: Route objects that expose a ``path`` attribute.
    '''

    # Walk top-level entries, expanding included routers when present.
    for route in app.routes:
        nested = getattr(route, 'original_router', None)
        if nested is not None:
            yield from nested.routes
            continue

        # Yield flattened routes (FastAPI < 0.141) and docs routes.
        yield route

# *** fixtures

# ** fixture: sample_route_plain
@pytest.fixture
def sample_route_plain() -> ApiRoute:
    '''
    Fixture to provide a sample ApiRoute without Swagger metadata.
    '''

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

    return mock.Mock()

# ** fixture: app_session
@pytest.fixture
def app_session() -> AppSession:
    '''
    Fixture to provide the AppSession resolved by build_fast_session_context.
    '''

    return AppSession(id='test_fast', name='Test Fast API')

# ** fixture: cache
@pytest.fixture
def cache() -> CacheContext:
    '''
    Fixture to provide the bootstrap cache pre-seeded with framework defaults.
    '''

    return core.build_cache()

# ** fixture: mock_app_session
@pytest.fixture
def mock_app_session() -> mock.Mock:
    '''
    Fixture to provide a mock AppSession with an empty constants map.
    '''

    app_session = mock.Mock()
    app_session.constants = {}
    return app_session

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
        Verify resolve_model returns None when given None.
        '''

        # Exercise resolve_model with None.
        result = session.given(model_path=None).run(target=resolve_model)

        # Assert None is returned.
        assert result is None

    # * test: empty_string
    def test_resolve_model_empty_string(self, session) -> None:
        '''
        Verify resolve_model returns None when given an empty string.
        '''

        # Exercise resolve_model with an empty string.
        result = session.given(model_path='').run(target=resolve_model)

        # Assert None is returned.
        assert result is None

    # * test: valid_path
    def test_resolve_model_valid_path(self, session) -> None:
        '''
        Verify resolve_model resolves a valid dotted import path.
        '''

        # Exercise resolve_model with pydantic.BaseModel.
        from pydantic import BaseModel
        result = session.given(model_path='pydantic.BaseModel').run(target=resolve_model)

        # Assert the resolved class matches.
        assert result is BaseModel

    # * test: invalid_module
    def test_resolve_model_invalid_module(self, session) -> None:
        '''
        Verify resolve_model raises TiferetError for an invalid module.
        '''

        # Exercise resolve_model with a missing module path.
        with pytest.raises(TiferetError) as exc_info:
            session.given(model_path='nonexistent.module.SomeClass').run(target=resolve_model)

        # Assert the structured resolution error.
        assert exc_info.value.error_code == 'OPENAPI_MODEL_RESOLUTION_FAILED'

    # * test: invalid_class
    def test_resolve_model_invalid_class(self, session) -> None:
        '''
        Verify resolve_model raises TiferetError for an invalid class name.
        '''

        # Exercise resolve_model with a missing class on an existing module.
        with pytest.raises(TiferetError) as exc_info:
            session.given(model_path='pydantic.NonExistentClass').run(target=resolve_model)

        # Assert the structured resolution error.
        assert exc_info.value.error_code == 'OPENAPI_MODEL_RESOLUTION_FAILED'

# ** tester: test_build_router
@use_tester(
    type='generic',
    target_cls=build_router,
)
class TestBuildRouter:
    '''
    Generic tester for build_router.
    '''

    # * test: plain
    def test_build_router_plain(
            self,
            session,
            sample_router_plain: ApiRouter,
            mock_view_func: mock.Mock,
        ) -> None:
        '''
        Verify build_router with a plain router (no Swagger metadata).
        '''

        # Exercise build_router with a plain router.
        api_router = session.given(
            router=sample_router_plain,
            view_func=mock_view_func,
        ).run(target=build_router)

        # Assert the router is configured correctly.
        assert isinstance(api_router, APIRouter)
        assert len(api_router.routes) == 1

        # Assert the route has correct base attributes.
        route = api_router.routes[0]
        assert route.path == '/calc/add'
        assert route.methods == {'POST'}
        assert route.name == 'calc.add'

        # Assert tags fall back to the router name.
        assert route.tags == ['calc', 'calc']

        # Assert no response model is set.
        assert route.response_model is None

    # * test: with_swagger
    def test_build_router_with_swagger(
            self,
            session,
            sample_router_with_swagger: ApiRouter,
            mock_view_func: mock.Mock,
        ) -> None:
        '''
        Verify build_router with Swagger metadata.
        '''

        # Exercise build_router with a swagger-enriched router.
        api_router = session.given(
            router=sample_router_with_swagger,
            view_func=mock_view_func,
        ).run(target=build_router)

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
        Verify get_routers calls get_routers() on the interface context.
        '''

        # Build a mock interface context exposing get_routers().
        mock_context = mock.Mock()
        mock_context.get_routers = mock.Mock(return_value=[sample_router_plain])

        # Exercise get_routers against the mock interface context.
        result = session.given(interface_context=mock_context).run(target=get_routers)

        # Assert the context method was called and the router list is returned.
        mock_context.get_routers.assert_called_once_with()
        assert result == [sample_router_plain]

    # * test: empty
    def test_get_routers_empty(self, session) -> None:
        '''
        Verify get_routers returns an empty list when no routers are configured.
        '''

        # Build a mock interface context with no routers.
        mock_context = mock.Mock()
        mock_context.get_routers = mock.Mock(return_value=[])

        # Exercise get_routers against the mock interface context.
        result = session.given(interface_context=mock_context).run(target=get_routers)

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
        service id and 'app' flag, then calls execute(**kwargs).
        '''

        # Build a mock get_dependency resolver returning a mock event.
        mock_event = mock.Mock()
        mock_event.execute = mock.Mock(return_value=mock.sentinel.route)
        get_dependency = mock.Mock(return_value=mock_event)

        # Exercise get_route_handler to build the closure, then call it.
        handler = session.given(get_dependency=get_dependency).run(target=get_route_handler)
        result = handler(id='calc.add')

        # Assert the resolution shape and passthrough return value.
        get_dependency.assert_called_once_with(GET_ROUTE_EVT_SERVICE_ID, APP_FLAG)
        mock_event.execute.assert_called_once_with(id='calc.add')
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
        service id and 'app' flag, then calls execute(**kwargs).
        '''

        # Build a mock get_dependency resolver returning a mock event.
        mock_event = mock.Mock()
        mock_event.execute = mock.Mock(return_value=mock.sentinel.status_code)
        get_dependency = mock.Mock(return_value=mock_event)

        # Exercise get_status_code_handler to build the closure, then call it.
        handler = session.given(get_dependency=get_dependency).run(target=get_status_code_handler)
        result = handler(error_code='INVALID_INPUT')

        # Assert the resolution shape and passthrough return value.
        get_dependency.assert_called_once_with(GET_STATUS_CODE_EVT_SERVICE_ID, APP_FLAG)
        mock_event.execute.assert_called_once_with(error_code='INVALID_INPUT')
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
        service id and 'app' flag, then calls execute(**kwargs).
        '''

        # Build a mock get_dependency resolver returning a mock event.
        mock_event = mock.Mock()
        mock_event.execute = mock.Mock(return_value=mock.sentinel.routers)
        get_dependency = mock.Mock(return_value=mock_event)

        # Exercise get_routers_handler to build the closure, then call it.
        handler = session.given(get_dependency=get_dependency).run(target=get_routers_handler)
        result = handler()

        # Assert the resolution shape and passthrough return value.
        get_dependency.assert_called_once_with(GET_ROUTERS_EVT_SERVICE_ID, APP_FLAG)
        mock_event.execute.assert_called_once_with()
        assert result is mock.sentinel.routers

# ** tester: test_create_fast_request_handler
@use_tester(
    type='generic',
    target_cls=create_fast_request_handler,
)
class TestCreateFastRequestHandler:
    '''
    Generic tester for create_fast_request_handler (RFP-005).
    '''

    # * test: copies_context_headers
    def test_create_fast_request_handler_copies_context_headers(self, session) -> None:
        '''
        Verify the adapter copies plugin ids onto OpenApiRequestContext
        headers without setting session_id from the HTTP request id.
        '''

        # Build the adapter with library default header names.
        header_keys = parse_context_header_options({})
        handler = session.given(header_keys=header_keys).run(
            target=create_fast_request_handler,
        )
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

    # * test: without_request_cycle
    def test_create_fast_request_handler_without_request_cycle(self, session) -> None:
        '''
        Verify the adapter still constructs OpenApiRequestContext outside HTTP.
        '''

        # Construct a request with no starlette_context request cycle.
        handler = session.given(
            header_keys=parse_context_header_options({}),
        ).run(target=create_fast_request_handler)
        request_context = handler('calc_fast_api', 'calc.add', {}, {})

        # Assert construction succeeds and plugin ids are not invented.
        assert isinstance(request_context, OpenApiRequestContext)
        assert DEFAULT_REQUEST_ID_HEADER not in request_context.headers
        assert request_context.headers['interface_id'] == 'calc_fast_api'
        assert request_context.session_id

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
    def test_build_fast_session_context_constructs_context(
            self,
            session,
            app_session: AppSession,
            cache: CacheContext,
        ) -> None:
        '''
        Verify build_fast_session_context constructs a wired FastApiContext
        with the default request/response handlers.
        '''

        # Exercise build_fast_session_context with cache and session only.
        result = session.given(app_session=app_session, cache=cache).run(
            target=build_fast_session_context,
        )

        # Assert the constructed context, bound domain, and default handlers.
        assert isinstance(result, FastApiContext)
        assert result.domain is app_session
        assert callable(result._create_request)
        assert result._build_response is core.response_handler
        assert callable(result._get_route)
        assert callable(result._get_status_code)
        assert callable(result._get_routers)

    # * test: default_handler_copies_headers
    def test_build_fast_session_context_default_handler_copies_headers(
            self,
            session,
            app_session: AppSession,
            cache: CacheContext,
        ) -> None:
        '''
        Verify omitting create_request_handler defaults to the header adapter.
        '''

        # Exercise build_fast_session_context with cache and session only.
        result = session.given(app_session=app_session, cache=cache).run(
            target=build_fast_session_context,
        )
        request_id = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'

        # Exercise the default handler inside a request cycle.
        with request_cycle_context({
            DEFAULT_REQUEST_ID_HEADER: request_id,
            DEFAULT_CORRELATION_ID_HEADER: 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
        }):
            request_context = result._create_request('calc_fast_api', 'calc.add', {}, {})

        # Assert the default handler copied plugin ids and left session_id alone.
        assert isinstance(request_context, OpenApiRequestContext)
        assert request_context.headers[DEFAULT_REQUEST_ID_HEADER] == request_id
        assert request_context.session_id != request_id

    # * test: accepts_custom_request_handler
    def test_build_fast_session_context_accepts_custom_request_handler(
            self,
            session,
            app_session: AppSession,
            cache: CacheContext,
        ) -> None:
        '''
        Verify an explicit create_request_handler is not wrapped again.
        '''

        # Exercise build_fast_session_context with a custom request handler.
        custom_handler = mock.Mock()
        result = session.given(
            app_session=app_session,
            cache=cache,
            create_request_handler=custom_handler,
        ).run(target=build_fast_session_context)

        # Assert the custom request handler is wired unchanged.
        assert result._create_request is custom_handler

# ** tester: test_build_fast_app
@use_tester(
    type='generic',
    target_cls=build_fast_app,
)
class TestBuildFastApp:
    '''
    Generic tester for build_fast_app. Patches core.build_cache,
    core.get_app_session, and build_fast_session_context directly on
    tiferet_fast.blueprints.fast.
    '''

    # * test: includes_one_router_per_result
    def test_build_fast_app_includes_one_router_per_result(
            self,
            session,
            sample_router_plain: ApiRouter,
            mock_view_func: mock.Mock,
            mock_app_session: mock.Mock,
        ) -> None:
        '''
        Verify build_fast_app includes one FastAPI router per get_routers
        result and mounts RawContextMiddleware.
        '''

        # Build a mock interface context exposing the sample router.
        mock_context = mock.Mock()
        mock_context.get_routers = mock.Mock(return_value=[sample_router_plain])
        mock_cache = mock.Mock()

        # Patch the three collaborators build_fast_app composes.
        with mock.patch('tiferet_fast.blueprints.fast.core.build_cache', return_value=mock_cache), \
             mock.patch('tiferet_fast.blueprints.fast.core.get_app_session', return_value=mock_app_session) as mock_get_app_session, \
             mock.patch('tiferet_fast.blueprints.fast.build_fast_session_context', return_value=mock_context) as mock_build_session:

            # Exercise build_fast_app.
            result = session.given(
                interface_id='test_interface',
                view_func=mock_view_func,
            ).run(target=build_fast_app)

        # Assert a FastAPI app was returned with the router included.
        assert isinstance(result, FastAPI)
        assert any(getattr(route, 'path', None) == '/calc/add' for route in iter_app_routes(result))

        # Assert RawContextMiddleware is mounted.
        assert any(middleware.cls is RawContextMiddleware for middleware in result.user_middleware)

        # Assert the collaborators were composed with the header adapter.
        mock_get_app_session.assert_called_once_with('test_interface', mock_cache)
        assert mock_build_session.call_args.args == (mock_app_session, mock_cache)
        assert callable(mock_build_session.call_args.kwargs['create_request_handler'])

    # * test: extra_parameters_go_to_get_app_session
    def test_build_fast_app_extra_parameters_go_to_get_app_session(
            self,
            session,
            mock_view_func: mock.Mock,
            mock_app_session: mock.Mock,
        ) -> None:
        '''
        Verify extra **parameters route to get_app_session.
        '''

        # Build a mock interface context with no routers.
        mock_context = mock.Mock()
        mock_context.get_routers = mock.Mock(return_value=[])
        mock_cache = mock.Mock()

        # Patch the three collaborators build_fast_app composes.
        with mock.patch('tiferet_fast.blueprints.fast.core.build_cache', return_value=mock_cache), \
             mock.patch('tiferet_fast.blueprints.fast.core.get_app_session', return_value=mock_app_session) as mock_get_app_session, \
             mock.patch('tiferet_fast.blueprints.fast.build_fast_session_context', return_value=mock_context):

            # Exercise build_fast_app with an extra keyword parameter.
            session.given(
                interface_id='test_interface',
                view_func=mock_view_func,
                extra_param='should_forward',
            ).run(target=build_fast_app)

        # Assert the extra parameter reached get_app_session.
        mock_get_app_session.assert_called_once_with(
            'test_interface',
            mock_cache,
            extra_param='should_forward',
        )

    # * test: omitted_view_func_binds_request_only_wrapper
    def test_build_fast_app_omitted_view_func_binds_request_only_wrapper(
            self,
            session,
            sample_router_plain: ApiRouter,
            mock_app_session: mock.Mock,
        ) -> None:
        '''
        Verify omitting view_func binds a Request-only wrapper around the
        assets view_func.
        '''

        # Build a mock interface context exposing the sample router.
        mock_context = mock.Mock()
        mock_context.get_routers = mock.Mock(return_value=[sample_router_plain])

        # Patch the three collaborators build_fast_app composes.
        with mock.patch('tiferet_fast.blueprints.fast.core.build_cache', return_value=mock.Mock()), \
             mock.patch('tiferet_fast.blueprints.fast.core.get_app_session', return_value=mock_app_session), \
             mock.patch('tiferet_fast.blueprints.fast.build_fast_session_context', return_value=mock_context):

            # Exercise build_fast_app without a view_func.
            result = session.given(interface_id='test_interface').run(target=build_fast_app)

        # Assert the bound endpoint is a Request-only wrapper.
        route = next(item for item in iter_app_routes(result) if getattr(item, 'path', None) == '/calc/add')
        endpoint = route.endpoint
        assert isinstance(endpoint, partial)
        assert list(signature(endpoint.func).parameters) == ['request']
        assert signature(endpoint.func).parameters['request'].annotation is Request

    # * test: supplied_view_func_is_the_endpoint
    def test_build_fast_app_supplied_view_func_is_the_endpoint(
            self,
            session,
            sample_router_plain: ApiRouter,
            mock_view_func: mock.Mock,
            mock_app_session: mock.Mock,
        ) -> None:
        '''
        Verify a supplied view_func is the bound route endpoint.
        '''

        # Build a mock interface context exposing the sample router.
        mock_context = mock.Mock()
        mock_context.get_routers = mock.Mock(return_value=[sample_router_plain])

        # Patch the three collaborators build_fast_app composes.
        with mock.patch('tiferet_fast.blueprints.fast.core.build_cache', return_value=mock.Mock()), \
             mock.patch('tiferet_fast.blueprints.fast.core.get_app_session', return_value=mock_app_session), \
             mock.patch('tiferet_fast.blueprints.fast.build_fast_session_context', return_value=mock_context):

            # Exercise build_fast_app with a supplied view_func.
            result = session.given(
                interface_id='test_interface',
                view_func=mock_view_func,
            ).run(target=build_fast_app)

        # Assert the supplied callable is the bound endpoint.
        route = next(item for item in iter_app_routes(result) if getattr(item, 'path', None) == '/calc/add')
        endpoint = route.endpoint
        assert isinstance(endpoint, partial)
        assert endpoint.func is mock_view_func

    # * test: mounts_keyed_middleware_and_adapter
    def test_build_fast_app_mounts_keyed_middleware_and_adapter(
            self,
            session,
            mock_app_session: mock.Mock,
        ) -> None:
        '''
        Verify build_fast_app keys both plugins and passes the header adapter.
        '''

        # Assemble an app whose session overrides both closed header names.
        mock_app_session.constants = {
            REQUEST_ID_HEADER_CONST_KEY: 'X-Custom-Request-ID',
            CORRELATION_ID_HEADER_CONST_KEY: 'X-Custom-Correlation-ID',
        }
        mock_context = mock.Mock()
        mock_context.get_routers = mock.Mock(return_value=[])

        # Patch the three collaborators build_fast_app composes.
        with mock.patch('tiferet_fast.blueprints.fast.core.build_cache', return_value=mock.Mock()), \
             mock.patch('tiferet_fast.blueprints.fast.core.get_app_session', return_value=mock_app_session), \
             mock.patch('tiferet_fast.blueprints.fast.build_fast_session_context', return_value=mock_context) as mock_build_session:

            # Exercise build_fast_app.
            result = session.given(interface_id='calc_fast_api').run(target=build_fast_app)

        # Assert both plugins are mounted and keyed from the parsed names.
        middleware = result.user_middleware[0]
        assert middleware.cls is RawContextMiddleware
        mounted_plugins = middleware.kwargs['plugins']
        assert isinstance(mounted_plugins[0], plugins.RequestIdPlugin)
        assert isinstance(mounted_plugins[1], plugins.CorrelationIdPlugin)
        assert mounted_plugins[0].key == 'X-Custom-Request-ID'
        assert mounted_plugins[1].key == 'X-Custom-Correlation-ID'

        # Assert the composed session received the header-copying request adapter.
        passed_handler = mock_build_session.call_args.kwargs['create_request_handler']
        with request_cycle_context({
            'X-Custom-Request-ID': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            'X-Custom-Correlation-ID': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
        }):
            request_context = passed_handler('calc_fast_api', 'calc.add', {}, {})
        assert isinstance(request_context, OpenApiRequestContext)
        assert request_context.headers['X-Custom-Request-ID'] == 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        assert request_context.headers['X-Custom-Correlation-ID'] == 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
        assert request_context.session_id != 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'

# ** tester: test_run
@use_tester(
    type='generic',
    target_cls=run,
)
class TestRun:
    '''
    Generic tester for run, a thin alias for build_fast_app.
    '''

    # * test: delegates_to_build_fast_app
    def test_run_delegates_to_build_fast_app(
            self,
            session,
            mock_view_func: mock.Mock,
        ) -> None:
        '''
        Verify run delegates to build_fast_app.
        '''

        # Patch build_fast_app to a sentinel return value.
        with mock.patch(
                'tiferet_fast.blueprints.fast.build_fast_app',
                return_value=mock.sentinel.fast_app,
            ) as mock_build_fast_app:

            # Exercise run.
            result = session.given(
                interface_id='test_interface',
                view_func=mock_view_func,
                app_yaml_file='app.yml',
            ).run(target=run)

        # Assert the delegation and the passthrough return value.
        mock_build_fast_app.assert_called_once_with(
            'test_interface',
            mock_view_func,
            app_yaml_file='app.yml',
        )
        assert result is mock.sentinel.fast_app
