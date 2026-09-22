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
    Provide a sample AppSession for FastApiContext construction.

    :return: An AppSession bound to the test FastAPI interface.
    :rtype: AppSession
    '''

    # Return a minimal AppSession for from_domain construction.
    return AppSession(id='test_fast', name='Test Fast API')

# ** fixture: get_dependency
@pytest.fixture
def get_dependency() -> Callable:
    '''
    Provide a mock get_dependency handler.

    :return: A mock callable.
    :rtype: Callable
    '''

    # Return a mock DI resolution handler.
    return mock.Mock()

# ** fixture: get_route_handler
@pytest.fixture
def get_route_handler() -> Callable:
    '''
    Provide a mock get_route handler.

    :return: A mock callable.
    :rtype: Callable
    '''

    # Return a mock route handler.
    return mock.Mock()

# ** fixture: get_status_code_handler
@pytest.fixture
def get_status_code_handler() -> Callable:
    '''
    Provide a mock get_status_code handler.

    :return: A mock callable.
    :rtype: Callable
    '''

    # Return a mock status-code handler.
    return mock.Mock()

# ** fixture: get_routers_handler
@pytest.fixture
def get_routers_handler() -> Callable:
    '''
    Provide a mock get_routers handler.

    :return: A mock callable.
    :rtype: Callable
    '''

    # Return a mock routers handler.
    return mock.Mock()

# ** fixture: fast_api_context
@pytest.fixture
def fast_api_context(app_session: AppSession,
                     get_dependency: Callable,
                     get_route_handler: Callable,
                     get_status_code_handler: Callable,
                     get_routers_handler: Callable) -> FastApiContext:
    '''
    Bind FastApiContext via from_domain using the OpenApiSessionContext constructor kwargs.

    :param app_session: The bound AppSession domain object.
    :type app_session: AppSession
    :param get_dependency: The required DI resolution handler.
    :type get_dependency: Callable
    :param get_route_handler: The injected route handler.
    :type get_route_handler: Callable
    :param get_status_code_handler: The injected status-code handler.
    :type get_status_code_handler: Callable
    :param get_routers_handler: The injected routers handler.
    :type get_routers_handler: Callable
    :return: A FastApiContext bound to app_session.
    :rtype: FastApiContext
    '''

    # Construct FastApiContext via inherited from_domain.
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
    Provide a sample ApiRouter with one route.

    :return: An ApiRouter named calc with a POST /add route.
    :rtype: ApiRouter
    '''

    # Return a sample ApiRouter with one route.
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
    Verify FastApiContext declares no domain_type, does not steal the AppSession
    registry slot from AppSessionContext, subclasses OpenApiSessionContext, and
    does not declare handle_error.
    '''

    # Assert FastApiContext does not declare domain_type in its own namespace.
    assert 'domain_type' not in FastApiContext.__dict__

    # Assert FastApiContext is not registered in ContextMeta.
    assert FastApiContext not in ContextMeta.registry.values()

    # Assert AppSession remains mapped to AppSessionContext.
    assert BaseContext.for_domain(AppSession) is AppSessionContext

    # Assert FastApiContext subclasses OpenApiSessionContext.
    assert issubclass(FastApiContext, OpenApiSessionContext)

    # Assert FastApiContext does not declare handle_error.
    assert 'handle_error' not in FastApiContext.__dict__

# *** testers

# ** tester: test_fast_api_context
@use_tester(type='generic', target_cls=FastApiContext)
class TestFastApiContext:
    '''
    Generic tester covering the FastApiContext method get_routers.
    '''

    # * test: get_routers_calls_handler_directly
    def test_get_routers_calls_handler_directly(self,
            session,
            fast_api_context: FastApiContext,
            get_routers_handler: Callable,
            sample_router: ApiRouter) -> None:
        '''
        Verify get_routers returns whatever the injected get_routers_handler
        mock returns when _get_routers() is called directly, not .execute().

        :param session: The injected TestSessionContext.
        :type session: TestSessionContext
        :param fast_api_context: The FastApiContext bound via from_domain.
        :type fast_api_context: FastApiContext
        :param get_routers_handler: The injected routers handler mock.
        :type get_routers_handler: Callable
        :param sample_router: A sample ApiRouter with one route.
        :type sample_router: ApiRouter
        '''

        # Configure the injected handler to return a known router list.
        get_routers_handler.return_value = [sample_router]

        # Exercise get_routers as a bound-method target.
        result = session.run(target=fast_api_context.get_routers)

        # Assert the result and the direct call shape.
        assert result == [sample_router]
        get_routers_handler.assert_called_once_with()
