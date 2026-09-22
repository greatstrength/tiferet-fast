"""Tests locking native FastAPI schema as the Publish surface."""

# *** imports

# ** core
import inspect
from pathlib import Path

# ** infra
from unittest import mock
from fastapi import FastAPI

# ** app
from ...contexts.fast import FastApiContext
from ..fast import build_fast_app

# *** constants

# ** constant: production_package_names
PRODUCTION_PACKAGE_NAMES = (
    'assets',
    'blueprints',
    'contexts',
)

# ** constant: forbidden_publish_identifiers
FORBIDDEN_PUBLISH_IDENTIFIERS = (
    'get_docs_spec',
    'generate_spec',
    'create_docs_handler',
)

# *** tests

# ** test: production_modules_do_not_wire_generate_publish
def test_production_modules_do_not_wire_generate_publish():
    '''
    Lock decision A: production modules do not name Generate/Publish accessors.
    '''

    # Scan top-level production modules for Generate/Publish identifiers.
    package_root = Path(__file__).resolve().parents[2]
    for package_name in PRODUCTION_PACKAGE_NAMES:
        for path in (package_root / package_name).glob('*.py'):
            text = path.read_text(encoding='utf-8')
            for identifier in FORBIDDEN_PUBLISH_IDENTIFIERS:
                assert identifier not in text, f'{path} contains {identifier}'

# ** test: fastapi_context_does_not_define_docs_factory
def test_fastapi_context_does_not_define_docs_factory():
    '''
    Lock decision A: FastApiContext does not grow a swagger/docs factory.
    '''

    # Assert FastApiContext does not define Generate/Publish accessors.
    for name in FORBIDDEN_PUBLISH_IDENTIFIERS + ('create_swagger_blueprint',):
        assert name not in FastApiContext.__dict__

    # Assert FastApiContext does not construct a FastAPI app.
    source = inspect.getsource(FastApiContext)
    assert 'FastAPI(' not in source
    assert 'FastAPIApp(' not in source

# ** test: build_fast_app_keeps_native_fastapi_docs
@mock.patch('tiferet_fast.blueprints.fast.get_routers', return_value=[])
@mock.patch('tiferet_fast.blueprints.fast.build_fast_session_context')
@mock.patch('tiferet_fast.blueprints.fast.core.get_app_session')
@mock.patch('tiferet_fast.blueprints.fast.core.build_cache')
def test_build_fast_app_keeps_native_fastapi_docs(
        mock_build_cache,
        mock_get_app_session,
        mock_build_session,
        mock_get_routers,
    ):
    '''
    Lock decision A: assemble keeps FastAPI-native docs URLs and openapi.

    :param mock_build_cache: Patch for core.build_cache.
    :type mock_build_cache: mock.Mock
    :param mock_get_app_session: Patch for core.get_app_session.
    :type mock_get_app_session: mock.Mock
    :param mock_build_session: Patch for build_fast_session_context.
    :type mock_build_session: mock.Mock
    :param mock_get_routers: Patch for get_routers.
    :type mock_get_routers: mock.Mock
    '''

    # Assemble without a consumer view so the built-in bind path still runs.
    fast_app = build_fast_app('demo')

    # Assert FastAPI's default documentation URLs were left alone.
    assert fast_app.openapi_url == '/openapi.json'
    assert fast_app.docs_url == '/docs'
    assert fast_app.redoc_url == '/redoc'

    # Assert the openapi method is still FastAPI's, not a get_docs_spec wrap.
    assert type(fast_app).openapi is FastAPI.openapi

    # Assert assemble does not override docs URLs or replace FastAPI.openapi.
    source = inspect.getsource(build_fast_app)
    assert 'openapi_url' not in source
    assert 'docs_url' not in source
    assert 'redoc_url' not in source
    assert 'openapi_schema' not in source
    assert 'fast_app.openapi' not in source
    assert 'swagger=' not in source
