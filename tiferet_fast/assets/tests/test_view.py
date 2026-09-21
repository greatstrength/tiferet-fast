"""Tests for FastAPI view assets."""

# *** imports

# ** core
import asyncio
import inspect
from unittest import mock

# ** infra
import pytest
from fastapi import HTTPException, Request
from tiferet import use_tester

# ** app
from .. import view as view_module
from ..view import view_func

# *** functions

# ** function: make_request
def make_request(
        body: bytes = b'{"a": 1}',
        query_string: bytes = b'',
        path_params: dict | None = None,
        headers: list | None = None,
        feature_id: str = 'calc.add',
    ) -> Request:
    '''
    Build a Starlette/FastAPI Request with a named route in scope.

    :param body: Raw HTTP body bytes.
    :type body: bytes
    :param query_string: Raw query string bytes.
    :type query_string: bytes
    :param path_params: Path parameters merged into feature data.
    :type path_params: dict | None
    :param headers: ASGI header tuples; defaults to JSON content-type.
    :type headers: list | None
    :param feature_id: Value exposed as ``scope['route'].name``.
    :type feature_id: str
    :return: A FastAPI Request.
    :rtype: Request
    '''

    # Expose the feature id as the FastAPI route name.
    route = mock.Mock()
    route.name = feature_id

    # Assemble a minimal HTTP scope.
    scope = {
        'type': 'http',
        'asgi': {'version': '3.0'},
        'http_version': '1.1',
        'method': 'POST',
        'scheme': 'http',
        'path': '/add',
        'raw_path': b'/add',
        'query_string': query_string,
        'headers': headers or [(b'content-type', b'application/json'), (b'x-test', b'value')],
        'client': ('testclient', 50000),
        'server': ('testserver', 80),
        'path_params': path_params or {},
        'route': route,
    }

    # Serve the body once through the ASGI receive callable.
    async def receive():
        return {'type': 'http.request', 'body': body, 'more_body': False}

    # Return the constructed request.
    return Request(scope, receive)

# *** tests

# ** test: assets_view_module_does_not_import_fast_layers
def test_assets_view_module_does_not_import_fast_layers():
    '''
    Verify the assets view module source does not name contexts, blueprints,
    or FastApiContext.
    '''

    # Read the module source once.
    source = inspect.getsource(view_module)

    # Assert the FastAPI adapter layers are not named.
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
    Generic tester for the built-in assets view_func.
    '''

    # * test: unpacks_json_query_and_path_then_unwraps_body
    def test_view_func_unpacks_and_unwraps_tuple_response(self, session) -> None:
        '''
        Verify view_func unpacks JSON, query, and path params into data,
        copies headers, calls context.run, and unwraps (body, status_code).
        '''

        # Build a request with JSON, query, and path params.
        request = make_request(
            body=b'{"a": 1}',
            query_string=b'b=2',
            path_params={'n': '3'},
            feature_id='calc.add',
        )

        # Build a mock context that returns an OpenAPI (body, status_code) pair.
        mock_context = mock.Mock()
        mock_context.run = mock.Mock(return_value=({'sum': 6}, 200))

        # Exercise view_func through the tester, wrapping the coroutine.
        result = asyncio.run(
            session.given(request=request, context=mock_context).run(target=view_func)
        )

        # Assert the unwrapped body and the session run call.
        assert result == {'sum': 6}
        mock_context.run.assert_called_once_with(
            feature_id='calc.add',
            headers=dict(request.headers),
            data={'a': 1, 'b': '2', 'n': '3'},
        )

    # * test: empty_body_becomes_empty_dict
    def test_view_func_empty_body_becomes_empty_dict(self, session) -> None:
        '''
        Verify a non-JSON body becomes {} before query and path params merge.
        '''

        # Build a request with an empty body and a query param.
        request = make_request(
            body=b'',
            query_string=b'extra=1',
            path_params={},
            feature_id='calc.ping',
        )

        # Build a mock context that returns an OpenAPI (body, status_code) pair.
        mock_context = mock.Mock()
        mock_context.run = mock.Mock(return_value=('ok', 200))

        # Exercise view_func through the tester, wrapping the coroutine.
        result = asyncio.run(
            session.given(request=request, context=mock_context).run(target=view_func)
        )

        # Assert the unwrapped body and empty-dict merge.
        assert result == 'ok'
        mock_context.run.assert_called_once_with(
            feature_id='calc.ping',
            headers=dict(request.headers),
            data={'extra': '1'},
        )

    # * test: http_exception_propagates
    def test_view_func_http_exception_propagates(self, session) -> None:
        '''
        Verify view_func does not catch HTTPException raised from context.run.
        '''

        # Build a request and a context that raises HTTPException.
        request = make_request()
        mock_context = mock.Mock()
        mock_context.run = mock.Mock(
            side_effect=HTTPException(status_code=400, detail='bad input'),
        )

        # Exercise view_func and expect the HTTPException to propagate.
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(
                session.given(request=request, context=mock_context).run(target=view_func)
            )

        # Assert the status code is preserved.
        assert exc_info.value.status_code == 400
