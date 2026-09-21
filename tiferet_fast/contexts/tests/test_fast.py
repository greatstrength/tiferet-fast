"""Tests for Fast API Context."""

# *** imports

# ** core
from typing import Callable
from unittest import mock

# ** infra
import pytest
from tiferet import use_tester
from tiferet.contexts.app import AppSessionContext
from tiferet.contexts.core import BaseContext, ContextMeta
from tiferet.domain import AppSession
from tiferet_openapi import ApiRoute, ApiRouter, OpenApiSessionContext

# ** app
from ..fast import FastApiContext

# *** fixtures

# ** fixture: app_session
@pytest.fixture
def app_session() -> AppSession:
    '''
    Fixture to provide the AppSession bound to the FastApiContext under test.
    '''

    return AppSession(id='test_fast', name='Test Fast API')

# ** fixture: get_dependency
@pytest.fixture
def get_dependency() -> Callable:
    '''
    Fixture to provide a mock DI resolution handler.
    '''

    return mock.Mock()

# ** fixture: get_route_handler
@pytest.fixture
def get_route_handler() -> Callable:
    '''
    Fixture to provide a mock route-lookup handler.
    '''

    return mock.Mock()

# ** fixture: get_status_code_handler
@pytest.fixture
def get_status_code_handler() -> Callable:
    '''
    Fixture to provide a mock status-code-lookup handler.
    '''

    return mock.Mock()

# ** fixture: get_routers_handler
@pytest.fixture
def get_routers_handler() -> Callable:
    '''
    Fixture to provide a mock routers-lookup handler.
    '''

    return mock.Mock()

# ** fixture: fast_api_context
@pytest.fixture
def fast_api_context(
        app_session: AppSession,
        get_dependency: Callable,
        get_route_handler: Callable,
        get_status_code_handler: Callable,
        get_routers_handler: Callable,
    ) -> FastApiContext:
    '''
    Fixture to provide a FastApiContext bound via from_domain, mirroring the
    cut tiferet-openapi==1.0.0 OpenApiSessionContext constructor shape.
    '''

    return FastApiContext.from_domain(
        app_session,
        get_dependency=get_dependency,
        get_route_handler=get_route_handler,
        get_status_code_handler=get_status_code_handler,
        get_routers_handler=get_routers_handler,
    )

# ** fixture: sample_router
@pytest.fixture
def sample_router() -> ApiRouter:
    '''
    Fixture to provide a sample ApiRouter with one route.
    '''

    return ApiRouter(
        name='calc',
        prefix='/calc',
        routes=[
            ApiRoute(id='add', endpoint='calc.add', path='/add', methods=['POST'], status_code=200),
        ],
    )

# *** tests

# ** test: fast_api_context_not_registered
def test_fast_api_context_not_registered():
    '''
    Verify FastApiContext declares no domain_type, does not steal the
    AppSession registry slot from AppSessionContext, and subclasses
    OpenApiSessionContext.
    '''

    # Verify domain_type is not declared in FastApiContext's own namespace.
    assert 'domain_type' not in FastApiContext.__dict__

    # Verify FastApiContext never registered itself in the context registry.
    assert FastApiContext not in ContextMeta.registry.values()

    # Verify AppSession still resolves to the base application session hub.
    assert BaseContext.for_domain(AppSession) is AppSessionContext

    # Verify FastApiContext is a subclass of OpenApiSessionContext.
    assert issubclass(FastApiContext, OpenApiSessionContext)

    # Verify the RFP-001 handle_error override is gone after RFP-002.
    assert 'handle_error' not in FastApiContext.__dict__

# *** testers

# ** tester: test_fast_api_context
@use_tester(
    type='generic',
    target_cls=FastApiContext,
)
class TestFastApiContext:
    '''
    Generic tester covering the FastApiContext method get_routers.
    '''

    # * test: get_routers_calls_handler_directly
    def test_get_routers_calls_handler_directly(
            self,
            session,
            fast_api_context: FastApiContext,
            get_routers_handler: Callable,
            sample_router: ApiRouter,
        ) -> None:
        '''
        Verify get_routers returns whatever the injected get_routers_handler
        mock returns when _get_routers() is called directly, not .execute().
        '''

        # Configure the injected handler to return a known router list.
        get_routers_handler.return_value = [sample_router]

        # Exercise get_routers as a bound-method target.
        result = session.run(target=fast_api_context.get_routers)

        # Assert the result and the direct call shape.
        assert result == [sample_router]
        get_routers_handler.assert_called_once_with()
