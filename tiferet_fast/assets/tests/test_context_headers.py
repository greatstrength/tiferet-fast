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
    Test that empty and missing constants maps resolve to library defaults.
    '''

    # Build the expected library-default header names.
    expected = {
        REQUEST_ID_HEADER_CONST_KEY: 'X-Request-ID',
        CORRELATION_ID_HEADER_CONST_KEY: 'X-Correlation-ID',
    }

    # Assert empty and missing maps both resolve to those defaults.
    assert parse_context_header_options({}) == expected
    assert parse_context_header_options(None) == expected

    # Assert the defaults match HeaderKeys values.
    assert expected[REQUEST_ID_HEADER_CONST_KEY] == DEFAULT_REQUEST_ID_HEADER
    assert expected[CORRELATION_ID_HEADER_CONST_KEY] == DEFAULT_CORRELATION_ID_HEADER
    assert DEFAULT_REQUEST_ID_HEADER == HeaderKeys.request_id.value
    assert DEFAULT_CORRELATION_ID_HEADER == HeaderKeys.correlation_id.value

# ** test: parse_context_header_options_overrides
def test_parse_context_header_options_overrides():
    '''
    Test that both closed keys override the library defaults.
    '''

    # Parse both closed header-name overrides.
    result = parse_context_header_options({
        REQUEST_ID_HEADER_CONST_KEY: 'X-Custom-Request-ID',
        CORRELATION_ID_HEADER_CONST_KEY: 'X-Custom-Correlation-ID',
    })

    # Assert both overrides are returned.
    assert result == {
        REQUEST_ID_HEADER_CONST_KEY: 'X-Custom-Request-ID',
        CORRELATION_ID_HEADER_CONST_KEY: 'X-Custom-Correlation-ID',
    }

# ** test: parse_context_header_options_unknown_keys_ignored
def test_parse_context_header_options_unknown_keys_ignored():
    '''
    Test that unknown keys including session_id_header are ignored.
    '''

    # Mix one closed override with unknown keys.
    result = parse_context_header_options({
        REQUEST_ID_HEADER_CONST_KEY: 'X-Trace-ID',
        'session_id_header': 'X-Session-ID',
        'timeout': '30',
    })

    # Assert only the two closed keys are returned.
    assert result == {
        REQUEST_ID_HEADER_CONST_KEY: 'X-Trace-ID',
        CORRELATION_ID_HEADER_CONST_KEY: DEFAULT_CORRELATION_ID_HEADER,
    }

# ** test: parse_context_header_options_blank_falls_back
def test_parse_context_header_options_blank_falls_back():
    '''
    Test that blank and whitespace-only values fall back to library defaults.
    '''

    # Parse blank and whitespace-only closed-key values.
    result = parse_context_header_options({
        REQUEST_ID_HEADER_CONST_KEY: '   ',
        CORRELATION_ID_HEADER_CONST_KEY: '',
    })

    # Assert both closed keys fall back to the library defaults.
    assert result == {
        REQUEST_ID_HEADER_CONST_KEY: DEFAULT_REQUEST_ID_HEADER,
        CORRELATION_ID_HEADER_CONST_KEY: DEFAULT_CORRELATION_ID_HEADER,
    }

# ** test: parse_context_header_options_strips_whitespace
def test_parse_context_header_options_strips_whitespace():
    '''
    Test that leading and trailing whitespace is stripped from overrides.
    '''

    # Parse a padded request-id override.
    result = parse_context_header_options({
        REQUEST_ID_HEADER_CONST_KEY: '  X-Padded-Request-ID  ',
    })

    # Assert the override is stripped.
    assert result[REQUEST_ID_HEADER_CONST_KEY] == 'X-Padded-Request-ID'

# ** test: parse_context_header_options_rejects_sequences
def test_parse_context_header_options_rejects_sequences():
    '''
    Test that YAML sequences fall back to the matching library default.
    '''

    # Parse a sequence value for the request-id key.
    result = parse_context_header_options({
        REQUEST_ID_HEADER_CONST_KEY: ['X-Request-ID'],
    })

    # Assert the sequence is rejected.
    assert result[REQUEST_ID_HEADER_CONST_KEY] == DEFAULT_REQUEST_ID_HEADER

# ** test: apply_context_headers_no_request_cycle
def test_apply_context_headers_no_request_cycle():
    '''
    Test that apply is a no-op outside a request-cycle context.
    '''

    # Build inbound headers that already include a client request id.
    original = {
        'content-type': 'application/json',
        'x-request-id': 'client',
    }

    # Apply headers outside a request cycle.
    result = apply_context_headers(
        original,
        parse_context_header_options({}),
    )

    # Assert an equal copy that is not the original and has no session_id.
    assert result == original
    assert result is not original
    assert 'session_id' not in result

# ** test: apply_context_headers_copies_canonical_names
def test_apply_context_headers_copies_canonical_names():
    '''
    Test that apply copies the two canonical names and drops case duplicates.
    '''

    # Build inbound headers with a lowercase request-id duplicate.
    original = {
        'x-request-id': 'client',
        'content-type': 'application/json',
    }
    request_id = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    correlation_id = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'

    # Apply headers inside a request cycle with extra context keys.
    with request_cycle_context({
        DEFAULT_REQUEST_ID_HEADER: request_id,
        DEFAULT_CORRELATION_ID_HEADER: correlation_id,
        'X-Other': 'ignored',
    }):
        result = apply_context_headers(
            original,
            parse_context_header_options({}),
        )

    # Assert canonical names are written and extras are omitted.
    assert result[DEFAULT_REQUEST_ID_HEADER] == request_id
    assert result[DEFAULT_CORRELATION_ID_HEADER] == correlation_id
    assert 'x-request-id' not in result
    assert result['content-type'] == 'application/json'
    assert 'X-Other' not in result
    assert 'session_id' not in result

    # Assert the caller's inbound map is unchanged.
    assert original == {
        'x-request-id': 'client',
        'content-type': 'application/json',
    }

# ** test: apply_context_headers_skips_none_values
def test_apply_context_headers_skips_none_values():
    '''
    Test that missing plugin values are skipped and session_id is never written.
    '''

    # Build a request cycle with only the request id set.
    request_id = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'

    # Apply headers when the correlation id is absent.
    with request_cycle_context({
        DEFAULT_REQUEST_ID_HEADER: request_id,
    }):
        result = apply_context_headers(
            {},
            parse_context_header_options({}),
        )

    # Assert only the present request id is copied.
    assert result[DEFAULT_REQUEST_ID_HEADER] == request_id
    assert DEFAULT_CORRELATION_ID_HEADER not in result
    assert 'session_id' not in result
