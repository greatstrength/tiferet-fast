"""Tests for FastAPI request-context header assets."""

# *** imports

# ** infra
from starlette_context import request_cycle_context
from starlette_context.header_keys import HeaderKeys

# ** app
from ..context_headers import (
    CORRELATION_ID_HEADER_CONST_KEY,
    DEFAULT_CORRELATION_ID_HEADER,
    DEFAULT_REQUEST_ID_HEADER,
    REQUEST_ID_HEADER_CONST_KEY,
    apply_context_headers,
    parse_context_header_options,
)

# *** tests

# ** test: parse_context_header_options_empty_constants
def test_parse_context_header_options_empty_constants():
    '''
    Test that an empty constants map returns both library default header names.
    '''

    # Parse an empty constants map.
    result = parse_context_header_options({})

    # Assert both closed keys resolve to the verified HeaderKeys values.
    assert result == {
        REQUEST_ID_HEADER_CONST_KEY: 'X-Request-ID',
        CORRELATION_ID_HEADER_CONST_KEY: 'X-Correlation-ID',
    }
    assert result[REQUEST_ID_HEADER_CONST_KEY] == DEFAULT_REQUEST_ID_HEADER
    assert result[CORRELATION_ID_HEADER_CONST_KEY] == DEFAULT_CORRELATION_ID_HEADER
    assert DEFAULT_REQUEST_ID_HEADER == HeaderKeys.request_id.value
    assert DEFAULT_CORRELATION_ID_HEADER == HeaderKeys.correlation_id.value

# ** test: parse_context_header_options_overrides
def test_parse_context_header_options_overrides():
    '''
    Test that set request_id_header and correlation_id_header override defaults.
    '''

    # Parse constants that override both closed keys.
    result = parse_context_header_options({
        REQUEST_ID_HEADER_CONST_KEY: 'X-Custom-Request-ID',
        CORRELATION_ID_HEADER_CONST_KEY: 'X-Custom-Correlation-ID',
    })

    # Assert the overrides are returned.
    assert result == {
        REQUEST_ID_HEADER_CONST_KEY: 'X-Custom-Request-ID',
        CORRELATION_ID_HEADER_CONST_KEY: 'X-Custom-Correlation-ID',
    }

# ** test: parse_context_header_options_unknown_keys_ignored
def test_parse_context_header_options_unknown_keys_ignored():
    '''
    Test that unknown keys, including other *_header names, are ignored.
    '''

    # Parse constants that mix a valid override with unrecognized keys.
    result = parse_context_header_options({
        REQUEST_ID_HEADER_CONST_KEY: 'X-Trace-ID',
        'session_id_header': 'X-Session-ID',
        'timeout': '30',
    })

    # Assert only the closed keys are present and correlation keeps the default.
    assert result == {
        REQUEST_ID_HEADER_CONST_KEY: 'X-Trace-ID',
        CORRELATION_ID_HEADER_CONST_KEY: DEFAULT_CORRELATION_ID_HEADER,
    }

# ** test: parse_context_header_options_blank_falls_back
def test_parse_context_header_options_blank_falls_back():
    '''
    Test that blank and whitespace-only values fall back to the defaults.
    '''

    # Parse constants with empty and whitespace-only closed keys.
    result = parse_context_header_options({
        REQUEST_ID_HEADER_CONST_KEY: '   ',
        CORRELATION_ID_HEADER_CONST_KEY: '',
    })

    # Assert both keys fall back to the library defaults.
    assert result == {
        REQUEST_ID_HEADER_CONST_KEY: DEFAULT_REQUEST_ID_HEADER,
        CORRELATION_ID_HEADER_CONST_KEY: DEFAULT_CORRELATION_ID_HEADER,
    }

# ** test: parse_context_header_options_strips_whitespace
def test_parse_context_header_options_strips_whitespace():
    '''
    Test that leading and trailing whitespace is stripped from overrides.
    '''

    # Parse constants with padded header names.
    result = parse_context_header_options({
        REQUEST_ID_HEADER_CONST_KEY: '  X-Padded-Request-ID  ',
    })

    # Assert the override is stripped.
    assert result[REQUEST_ID_HEADER_CONST_KEY] == 'X-Padded-Request-ID'

# ** test: parse_context_header_options_rejects_sequences
def test_parse_context_header_options_rejects_sequences():
    '''
    Test that non-string values such as YAML sequences fall back to defaults.
    '''

    # Parse a sequence value for a closed key.
    result = parse_context_header_options({
        REQUEST_ID_HEADER_CONST_KEY: ['X-Request-ID'],
    })

    # Assert the sequence is rejected in favor of the default.
    assert result[REQUEST_ID_HEADER_CONST_KEY] == DEFAULT_REQUEST_ID_HEADER

# ** test: apply_context_headers_no_request_cycle
def test_apply_context_headers_no_request_cycle():
    '''
    Test that apply returns an unchanged copy when no request cycle exists.
    '''

    # Apply against inbound headers outside a request cycle.
    original = {'content-type': 'application/json', 'x-request-id': 'client'}
    result = apply_context_headers(
        original,
        parse_context_header_options({}),
    )

    # Assert the copy is unchanged and is not the caller's map.
    assert result == original
    assert result is not original
    assert 'session_id' not in result

# ** test: apply_context_headers_copies_canonical_names
def test_apply_context_headers_copies_canonical_names():
    '''
    Test that apply copies only the two resolved names and canonicalizes case.
    '''

    # Apply against a request-cycle context that includes extra keys.
    original = {'x-request-id': 'client', 'content-type': 'application/json'}
    header_keys = parse_context_header_options({})
    with request_cycle_context({
        DEFAULT_REQUEST_ID_HEADER: 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        DEFAULT_CORRELATION_ID_HEADER: 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
        'X-Other': 'ignored',
    }):
        result = apply_context_headers(original, header_keys)

    # Assert only the two canonical names are copied and lowercase duplicates drop.
    assert result[DEFAULT_REQUEST_ID_HEADER] == 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    assert result[DEFAULT_CORRELATION_ID_HEADER] == 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
    assert 'x-request-id' not in result
    assert result['content-type'] == 'application/json'
    assert 'X-Other' not in result
    assert 'session_id' not in result
    assert original == {'x-request-id': 'client', 'content-type': 'application/json'}

# ** test: apply_context_headers_skips_none_values
def test_apply_context_headers_skips_none_values():
    '''
    Test that a missing plugin value is not written onto headers.
    '''

    # Apply when only the request-id plugin populated context.
    with request_cycle_context({
        DEFAULT_REQUEST_ID_HEADER: 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
    }):
        result = apply_context_headers({}, parse_context_header_options({}))

    # Assert the missing correlation id is not invented.
    assert result[DEFAULT_REQUEST_ID_HEADER] == 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    assert DEFAULT_CORRELATION_ID_HEADER not in result
    assert 'session_id' not in result
