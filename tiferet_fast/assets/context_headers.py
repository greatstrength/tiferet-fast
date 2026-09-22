"""Closed request/correlation header constant keys. Stateless parse/apply helpers copy plugin ids onto Tiferet Request headers."""

# *** imports

# ** core
from typing import Dict

# ** infra
from starlette_context import context
from starlette_context.errors import ContextDoesNotExistError
from starlette_context.header_keys import HeaderKeys

# *** constants

# ** constant: request_id_header_const_key
REQUEST_ID_HEADER_CONST_KEY = 'request_id_header'

# ** constant: correlation_id_header_const_key
CORRELATION_ID_HEADER_CONST_KEY = 'correlation_id_header'

# ** constant: default_request_id_header
DEFAULT_REQUEST_ID_HEADER = HeaderKeys.request_id.value

# ** constant: default_correlation_id_header
DEFAULT_CORRELATION_ID_HEADER = HeaderKeys.correlation_id.value

# *** functions

# ** function: _resolve_header_name
def _resolve_header_name(constants: Dict[str, str], const_key: str, default: str) -> str:
    '''
    Resolve a closed header-name constant, stripping whitespace.

    :param constants: AppSession constants map.
    :type constants: Dict[str, str]
    :param const_key: Closed constant key.
    :type const_key: str
    :param default: Library default header name.
    :type default: str
    :return: The stripped header name, or the library default.
    :rtype: str
    '''

    # Read the closed-key value from the constants map.
    raw_value = constants.get(const_key)

    # Reject missing, None, sequence, and any other non-string values.
    if not isinstance(raw_value, str):
        return default

    # Strip whitespace; empty values fall back to the default.
    stripped_value = raw_value.strip()
    if not stripped_value:
        return default

    # Return the stripped header name.
    return stripped_value

# ** function: parse_context_header_options
def parse_context_header_options(constants: Dict[str, str]) -> dict:
    '''
    Parse the closed request/correlation header names from session constants.

    Always returns both resolved names. Unknown keys are ignored. Blank or
    whitespace-only values fall back to the library defaults.

    :param constants: Resolved AppSession constants map. ``None`` is accepted at runtime.
    :type constants: Dict[str, str]
    :return: The two resolved header names keyed by the closed constant keys.
    :rtype: dict
    '''

    # Treat a missing constants map as empty.
    if constants is None:
        constants = {}

    # Return only the two closed header names.
    return {
        REQUEST_ID_HEADER_CONST_KEY: _resolve_header_name(
            constants,
            REQUEST_ID_HEADER_CONST_KEY,
            DEFAULT_REQUEST_ID_HEADER,
        ),
        CORRELATION_ID_HEADER_CONST_KEY: _resolve_header_name(
            constants,
            CORRELATION_ID_HEADER_CONST_KEY,
            DEFAULT_CORRELATION_ID_HEADER,
        ),
    }

# ** function: apply_context_headers
def apply_context_headers(headers: Dict[str, str], header_keys: dict) -> Dict[str, str]:
    '''
    Copy request and correlation ids from ``starlette_context`` onto headers.

    Returns a new dict. When no request-cycle context exists, the copy is
    unchanged. Does not write ``session_id``.

    :param headers: Inbound request headers. ``None`` is treated as empty.
    :type headers: Dict[str, str]
    :param header_keys: Resolved names from ``parse_context_header_options``. ``None`` is treated as empty.
    :type header_keys: dict
    :return: A new headers dict with canonical request and correlation ids applied.
    :rtype: Dict[str, str]
    '''

    # Copy inbound headers so the caller's map is never mutated.
    result = dict(headers or {})

    # Return the copy unchanged when no request-cycle context exists.
    try:
        if not context.exists():
            return result
    except ContextDoesNotExistError:
        return result

    # Treat a missing header-key map as empty; unknown keys are ignored.
    header_keys = header_keys or {}

    # Resolve the two closed canonical names, falling back to library defaults.
    request_id_header = header_keys.get(REQUEST_ID_HEADER_CONST_KEY) or DEFAULT_REQUEST_ID_HEADER
    correlation_id_header = header_keys.get(CORRELATION_ID_HEADER_CONST_KEY) or DEFAULT_CORRELATION_ID_HEADER

    # Copy each plugin value under its canonical name.
    for canonical_name in (
            request_id_header,
            correlation_id_header,
    ):

        # Look up the plugin value; stop if the request-cycle context vanished.
        try:
            value = context.get(canonical_name)
        except ContextDoesNotExistError:
            return result

        # Skip missing plugin values; do not invent an id.
        if value is None:
            continue

        # Drop case-insensitive duplicates, then write the canonical name.
        result = {
            key: existing
            for key, existing in result.items()
            if key.lower() != canonical_name.lower()
        }
        result[canonical_name] = str(value)

    # Return the adapted headers copy.
    return result
