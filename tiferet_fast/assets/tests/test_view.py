"""Tests for FastAPI view assets."""

# *** imports

# ** core
import asyncio
import inspect
from unittest import mock

# ** infra
import pytest
from fastapi import HTTPException, Request

# ** app
from tiferet import use_tester
from .. import view as view_module
from ..view import view_func

# *** fixtures

# ** fixture: make_request
@pytest.fixture
def make_request():
    '''
    Build a FastAPI Request from a Starlette ASGI HTTP scope.

    :return: A factory that returns a FastAPI Request.
    :rtype: Callable
    '''

    # Return a factory that constructs a Request from the given ASGI fields.
    def _make_request(
            body: bytes = b'{"a": 1}',
            query_string: bytes = b'',
            path_params: dict | None = None,
            headers: list | None = None,
            feature_id: str = 'calc.add') -> Request:
        '''
        Construct a FastAPI Request for view tests.

        :param body: The HTTP request body bytes.
        :type body: bytes
        :param query_string: The raw query string bytes.
        :type query_string: bytes
        :param path_params: Path parameters for the request scope.
        :type path_params: dict | None
        :param headers: ASGI header tuples, or None for JSON defaults.
        :type headers: list | None
        :param feature_id: The FastAPI route name used as the feature id.
        :type feature_id: str
        :return: A FastAPI Request bound to the constructed scope.
        :rtype: Request
        '''

        # Build a mock route whose name is the feature id.
        route = mock.Mock()
        route.name = feature_id

        # Default path params and JSON headers when omitted.
        if path_params is None:
            path_params = {}

        if headers is None:
            headers = [
                (b'content-type', b'application/json'),
                (b'x-test', b'value'),
            ]

        # Assemble the ASGI HTTP scope.
        scope = {
            'type': 'http',
            'asgi': {'version': '3.0'},
            'http_version': '1.1',
            'method': 'POST',
            'scheme': 'http',
            'path': '/add',
            'raw_path': b'/add',
            'query_string': query_string,
            'headers': headers,
            'path_params': path_params,
            'client': ('testclient', 50000),
            'server': ('testserver', 80),
            'route': route,
        }

        # Receive the request body once.
        async def receive():
            return {
                'type': 'http.request',
                'body': body,
                'more_body': False,
            }

        # Return the FastAPI Request.
        return Request(scope, receive)

    return _make_request

# *** tests

# ** test: assets_view_module_does_not_import_fast_layers
def test_assets_view_module_does_not_import_fast_layers():
    '''
    Test that the view module does not import FastAPI adapter layers.
    '''

    # Read the view module source.
    source = inspect.getsource(view_module)

    # Assert FastAPI adapter layers are not named.
    assert 'tiferet_fast.contexts' not in source
    assert 'tiferet_fast.blueprints' not in source
    assert 'FastApiContext' not in source

# *** testers

# ** tester: test_view_func
@use_tester(
    type='generic',
    target_cls=view_func,
)
class TestViewFunc:
    '''
    Tests for the FastAPI request view function.
    '''

    # * test: view_func_unpacks_and_unwraps_tuple_response
    def test_view_func_unpacks_and_unwraps_tuple_response(self, session, make_request):
        '''
        Test JSON, query, and path merge, then unwrap the run tuple.

        :param session: A fresh test session.
        :type session: TestSessionContext
        :param make_request: Factory for a FastAPI Request.
        :type make_request: Callable
        '''

        # Build a request with JSON body, query, and path params.
        request = make_request(
            body=b'{"a": 1}',
            query_string=b'b=2',
            path_params={'n': '3'},
            feature_id='calc.add',
        )
        context = mock.Mock()
        context.run.return_value = ({'sum': 6}, 200)

        # Execute the view through the generic tester session.
        result = asyncio.run(
            session.given(
                request=request,
                context=context,
            ).run(target=view_func)
        )

        # Assert the body is returned and run received the merged payload.
        assert result == {'sum': 6}
        context.run.assert_called_once_with(
            feature_id='calc.add',
            headers=dict(request.headers),
            data={'a': 1, 'b': '2', 'n': '3'},
        )

    # * test: view_func_empty_body_becomes_empty_dict
    def test_view_func_empty_body_becomes_empty_dict(self, session, make_request):
        '''
        Test that an empty body starts merged data from an empty dict.

        :param session: A fresh test session.
        :type session: TestSessionContext
        :param make_request: Factory for a FastAPI Request.
        :type make_request: Callable
        '''

        # Build a request with an empty body and a query param.
        request = make_request(
            body=b'',
            query_string=b'extra=1',
            path_params={},
            feature_id='calc.ping',
        )
        context = mock.Mock()
        context.run.return_value = ('ok', 200)

        # Execute the view through the generic tester session.
        result = asyncio.run(
            session.given(
                request=request,
                context=context,
            ).run(target=view_func)
        )

        # Assert the body is returned and data started from {}.
        assert result == 'ok'
        context.run.assert_called_once_with(
            feature_id='calc.ping',
            headers=dict(request.headers),
            data={'extra': '1'},
        )

    # * test: view_func_http_exception_propagates
    def test_view_func_http_exception_propagates(self, session, make_request):
        '''
        Test that HTTPException from context.run propagates uncaught.

        :param session: A fresh test session.
        :type session: TestSessionContext
        :param make_request: Factory for a FastAPI Request.
        :type make_request: Callable
        '''

        # Build a default request and a collaborator that raises HTTPException.
        request = make_request()
        context = mock.Mock()
        context.run.side_effect = HTTPException(status_code=400, detail='bad input')

        # Assert the HTTPException propagates from the view.
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(
                session.given(
                    request=request,
                    context=context,
                ).run(target=view_func)
            )

        # Assert the status code is preserved.
        assert exc_info.value.status_code == 400
