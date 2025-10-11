"""Tests for Fast API Context."""

# *** imports

# ** infra
import pytest
from unittest import mock
from fastapi import FastAPI
from fastapi.routing import APIRouter
from tiferet import (
    ModelObject,
    TiferetError
)

# ** app
from ...contexts.fast import FastApiContext
from ...contexts.request import FastRequestContext
from ...models.fast import (
    FastRouter,
    FastRoute
)
from ...handlers.fast import FastApiHandler
from tiferet.contexts.error import ErrorContext
from tiferet.contexts.feature import FeatureContext
from tiferet.contexts.logging import LoggingContext

# *** fixtures

# ** fixture: fast_router
@pytest.fixture
def fast_router() -> FastRouter:
    '''
    Fixture to provide a sample FastRouter instance for testing.
    '''

    # Create a FastRouter instance.
    return ModelObject.new(
        FastRouter,
        name='calc',
        prefix='/calc',
        routes=[
            ModelObject.new(
                FastRoute,
                id='add',
                endpoint='calc.add',
                path='/add',
                methods=['GET', 'POST'],
                status_code=200
            )
        ]
    )

# ** fixture: fast_api_context
@pytest.fixture
def fast_api_context(fast_router: FastRouter) -> FastApiContext:
    '''
    Fixture to provide a FastApiContext instance for testing.
    '''

    # Create a mock feature context.
    mock_features = mock.Mock(spec=FeatureContext)

    # Create a mock error context.
    mock_errors = mock.Mock(spec=ErrorContext)
    mock_errors.handle_error.return_value = {'message': 'An error occurred.'}

    # Create a mock logging context.
    mock_logging = mock.Mock(spec=LoggingContext)

    # Create a mock FastApiHandler.
    mock_handler = mock.Mock(spec=FastApiHandler)
    mock_handler.get_routers.return_value = [fast_router]
    mock_handler.get_status_code.return_value = 400
    mock_handler.get_route.return_value = ModelObject.new(
        FastRoute,
        id='add',
        endpoint='calc.add',
        path='/add',
        methods=['GET', 'POST'],
        status_code=200
    )

    # Create and return the FastApiContext instance.
    return FastApiContext(
        interface_id='test_fast',
        features=mock_features,
        errors=mock_errors,
        logging=mock_logging,
        fast_api_handler=mock_handler
    )

# *** tests

# ** test: fast_api_context_parse_request
def test_fast_api_context_parse_request(fast_api_context: FastApiContext):
    '''
    Test the parse_request method of FastApiContext.

    :param fast_api_context: A FastApiContext instance.
    :type fast_api_context: FastApiContext
    '''

    # Sample headers and data.
    sample_headers = {'Content-Type': 'application/json'}
    sample_data = {'key': 'value'}

    # Parse the request.
    request_context = fast_api_context.parse_request(
        headers=sample_headers,
        data=sample_data,
        feature_id='calc.add'
    )

    # Assert that the returned object is a FastRequestContext instance.
    assert isinstance(request_context, FastRequestContext)
    assert request_context.headers == sample_headers
    assert request_context.data == sample_data
    assert request_context.feature_id == 'calc.add'

# ** test: fast_api_context_handle_error
def test_fast_api_context_handle_error(fast_api_context: FastApiContext):
    '''
    Test the handle_error method of FastApiContext.

    :param fast_api_context: A FastApiContext instance.
    :type fast_api_context: FastApiContext
    '''

    # Create a sample exception.
    sample_exception = Exception('Sample error')

    # Call the handle_error method.
    response, status_code = fast_api_context.handle_error(sample_exception)

    # Assert that the response is a tuple of (response, status_code).
    assert isinstance(response, dict)
    assert status_code == 500

# ** test: fast_api_context_handle_tiferet_error
def test_fast_api_context_handle_tiferet_error(fast_api_context: FastApiContext):
    '''
    Test the handle_error method of FastApiContext with a TiferetError.

    :param fast_api_context: A FastApiContext instance.
    :type fast_api_context: FastApiContext
    '''

    # Create a sample TiferetError.
    sample_tiferet_error = TiferetError('INVALID_INPUT', 'Invalid input provided.')

    # Mock the error handler to return a specific response.
    fast_api_context.errors.handle_error.return_value = {
        'error_code': 'INVALID_INPUT',
        'text': 'Invalid input provided.'
    }

    # Call the handle_error method.
    response, status_code = fast_api_context.handle_error(sample_tiferet_error)

    # Assert that the response is a tuple of (response, status_code).
    assert response == {
        'error_code': 'INVALID_INPUT',
        'text': 'Invalid input provided.'
    }
    assert status_code == 400

# ** test: fast_api_context_handle_response
def test_fast_api_context_handle_response(fast_api_context: FastApiContext):
    '''
    Test the handle_response method of FastApiContext.

    :param fast_api_context: A FastApiContext instance.
    :type fast_api_context: FastApiContext
    '''

    # Create a new request context from the fast_api_context.
    request_context = fast_api_context.parse_request(
        headers={'Content-Type': 'application/json'},
        data={'key': 'value'},
        feature_id='calc.add'
    )

    # Set a sample result in the request context.
    request_context.set_result({'result_key': 'result_value'})

    # Handle the response.
    response, status_code = fast_api_context.handle_response(request_context)

    # Assert that the response is as expected.
    assert response == {'result_key': 'result_value'}
    assert status_code == 200

# ** test: fast_api_context_build_router
def test_fast_api_context_build_router(fast_api_context: FastApiContext, fast_router: FastRouter):
    '''
    Test the build_router method of FastApiContext.

    :param fast_api_context: A FastApiContext instance.
    :type fast_api_context: FastApiContext
    :param fast_router: A FastRouter instance.
    :type fast_router: FastRouter
    '''

    # Create a sample view function.
    def sample_view_func():
        return 'Sample Response'

    # Build a sample router.
    router = fast_api_context.build_router(
        fast_router=fast_router,
        view_func=sample_view_func
    )

    # Assert that the returned object is a FastAPI instance.
    assert isinstance(router, APIRouter)
    assert router.tags == ['calc']
    assert router.prefix == '/calc'

# ** test: fast_api_context_build_fast_app
def test_fast_api_context_build_fast_app(fast_api_context: FastApiContext):
    '''
    Test the build_fast_app method of FastApiContext.

    :param fast_api_context: A FastApiContext instance.
    :type fast_api_context: FastApiContext
    '''

    # Create a sample view function.
    def sample_view_func():
        return 'Sample Response'

    # Build a sample FastAPI app.
    fast_app = fast_api_context.build_fast_app(
        view_func=sample_view_func
    )

    # Assert that the returned object is a FastAPI instance.
    assert isinstance(fast_api_context.fast_app, FastAPI)
    assert fast_app.title == 'test_fast API'