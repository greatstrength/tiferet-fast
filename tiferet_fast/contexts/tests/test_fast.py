"""Tests for Fast API Context."""

# *** imports

# ** infra
import pytest
from unittest import mock
from tiferet import TiferetError
from tiferet.assets.exceptions import TiferetAPIError
from tiferet.events import DomainEvent
from tiferet.contexts.error import ErrorContext
from tiferet.contexts.feature import FeatureContext
from tiferet.contexts.logging import LoggingContext

# ** app
from ...contexts.fast import FastApiContext
from ...contexts.request import FastRequestContext
from ...domain import FastRoute, FastRouter

# *** fixtures

# ** fixture: sample_route
@pytest.fixture
def sample_route() -> FastRoute:
    '''
    Fixture to provide a sample FastRoute instance for testing.
    '''

    # Create a FastRoute instance.
    return FastRoute(
        id='add',
        endpoint='calc.add',
        path='/add',
        methods=['GET', 'POST'],
        status_code=200,
    )

# ** fixture: fast_api_context
@pytest.fixture
def fast_api_context(sample_route: FastRoute) -> FastApiContext:
    '''
    Fixture to provide a FastApiContext instance for testing.
    '''

    # Create a mock feature context.
    mock_features = mock.Mock(spec=FeatureContext)

    # Create a mock error context.
    mock_errors = mock.Mock(spec=ErrorContext)
    mock_errors.handle_error.return_value = {
        'error_code': 'APP_ERROR',
        'name': 'Application Error',
        'message': 'An error occurred.',
    }

    # Create a mock logging context.
    mock_logging = mock.Mock(spec=LoggingContext)

    # Create a mock get_route_evt.
    mock_get_route_evt = mock.Mock(spec=DomainEvent)
    mock_get_route_evt.execute = mock.Mock(return_value=sample_route)

    # Create a mock get_status_code_evt.
    mock_get_status_code_evt = mock.Mock(spec=DomainEvent)
    mock_get_status_code_evt.execute = mock.Mock(return_value=400)

    # Create and return the FastApiContext instance.
    return FastApiContext(
        interface_id='test_fast',
        features=mock_features,
        errors=mock_errors,
        logging=mock_logging,
        get_route_evt=mock_get_route_evt,
        get_status_code_evt=mock_get_status_code_evt,
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
    Test the handle_error method of FastApiContext with a generic exception.

    :param fast_api_context: A FastApiContext instance.
    :type fast_api_context: FastApiContext
    '''

    # Create a sample exception.
    sample_exception = Exception('Sample error')

    # Call the handle_error method and expect TiferetAPIError.
    with pytest.raises(TiferetAPIError) as exc_info:
        fast_api_context.handle_error(sample_exception)

    # Assert the status code is 500 for non-TiferetError.
    assert exc_info.value.status_code == 500

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
        'name': 'Invalid Input',
        'message': 'Invalid input provided.',
    }

    # Call the handle_error method and expect TiferetAPIError.
    with pytest.raises(TiferetAPIError) as exc_info:
        fast_api_context.handle_error(sample_tiferet_error)

    # Assert the status code is 400 (from mock get_status_code_evt).
    assert exc_info.value.status_code == 400
    assert exc_info.value.error_code == 'INVALID_INPUT'

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
