"""Tests for Fast API Request Context"""

# *** imports

# ** infra
import pytest
from pydantic import Field
from tiferet.domain import DomainObject

# ** app
from ...contexts.request import FastRequestContext

# *** fixtures

# ** fixture: fast_request_context
@pytest.fixture
def fast_request_context():
    '''
    Fixture to provide a mock FastRequestContext.
    '''

    # Create a mock FastRequestContext.
    request_context = FastRequestContext(
        data=dict(
            key='value',
            another_key='another_value'
        ),
        headers=dict(
            interface_id='test_interface'
        ),
        feature_id='calc.add'
    )

    # Return the mock FastRequestContext.
    return request_context

# *** tests

# ** test: fast_request_context_handle_response_none
def test_fast_request_context_handle_response_none(fast_request_context):
    '''
    Test handling a response that is None in the FastRequestContext.

    :param fast_request_context: The FastRequestContext instance.
    :type fast_request_context: FastRequestContext
    '''

    # Set the request context result to None.
    fast_request_context.set_result(None)

    # Handle a None response.
    response = fast_request_context.handle_response()

    # Check that the response is empty.
    assert response == ''

# ** test: fast_request_context_handle_response_primitive
def test_fast_request_context_handle_response_primitive(fast_request_context):
    '''
    Test handling a response that is a primitive type in the FastRequestContext.

    :param fast_request_context: The FastRequestContext instance.
    :type fast_request_context: FastRequestContext
    '''

    # Set the request context result to a primitive type.
    fast_request_context.set_result('test_string')

    # Handle the response with a primitive type.
    response = fast_request_context.handle_response()

    # Check that the response is as expected.
    assert response == 'test_string'

# ** test: fast_request_context_handle_response_data
def test_fast_request_context_handle_response_data(fast_request_context):
    '''
    Test handling a response with data in the FastRequestContext.

    :param fast_request_context: The FastRequestContext instance.
    :type fast_request_context: FastRequestContext
    '''

    # Set the request context result to some data.
    fast_request_context.result = {'key': 'value'}

    # Handle the response with data.
    response = fast_request_context.handle_response()

    # Check that the response is as expected.
    assert response == {'key': 'value'}

# ** test: fast_request_context_handle_response_domain_object
def test_fast_request_context_handle_response_domain_object(fast_request_context):
    '''
    Test handling a response that is a DomainObject in the FastRequestContext.

    :param fast_request_context: The FastRequestContext instance.
    :type fast_request_context: FastRequestContext
    '''

    # Create a DomainObject to simulate a response.
    class Data(DomainObject):
        key: str = Field(default='default_value', description='A key field.')

    # Set the request context result to a DomainObject.
    fast_request_context.set_result(Data(key='value'))

    # Handle the response with a DomainObject.
    response = fast_request_context.handle_response()

    # Check that the response is a dictionary with expected data.
    assert isinstance(response, dict)
    assert response.get('key') == 'value'

# ** test: fast_request_context_handle_response_domain_list
def test_fast_request_context_handle_response_domain_list(fast_request_context):
    '''
    Test handling a response that is a list of DomainObjects in the FastRequestContext.

    :param fast_request_context: The FastRequestContext instance.
    :type fast_request_context: FastRequestContext
    '''

    # Create a DomainObject to simulate a response.
    class Item(DomainObject):
        name: str = Field(default='default_name', description='A name field.')

    # Set the request context result to a list of DomainObjects.
    fast_request_context.set_result([
        Item(name='item1'),
        Item(name='item2'),
    ])

    # Handle the response with a list of DomainObjects.
    response = fast_request_context.handle_response()

    # Check that the response is a list and contains expected data.
    assert isinstance(response, list)
    assert len(response) == 2
    assert response[0].get('name') == 'item1'
    assert response[1].get('name') == 'item2'

# ** test: fast_request_context_handle_response_domain_dict
def test_fast_request_context_handle_response_domain_dict(fast_request_context):
    '''
    Test handling a response that is a dict of DomainObjects in the FastRequestContext.

    :param fast_request_context: The FastRequestContext instance.
    :type fast_request_context: FastRequestContext
    '''

    # Create a DomainObject to simulate a response.
    class Item(DomainObject):
        name: str = Field(default='default_name', description='A name field.')

    # Set the request context result to a dict of DomainObjects.
    fast_request_context.set_result({
        'item1': Item(name='item1'),
        'item2': Item(name='item2'),
    })

    # Handle the response with a dict of DomainObjects.
    response = fast_request_context.handle_response()

    # Check that the response is a dict and contains expected data.
    assert isinstance(response, dict)
    assert len(response) == 2
    assert response['item1'].get('name') == 'item1'
    assert response['item2'].get('name') == 'item2'
