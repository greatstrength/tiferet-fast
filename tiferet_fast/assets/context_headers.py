"""FastAPI Request-Context Header Assets

Closed request/correlation header constant keys and the stateless
parse/apply helpers that copy plugin ids onto Tiferet Request headers
(RFP-005).
"""

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
def _resolve_header_name(constants: Dict[str, str],
        const_key: str,
        default: str) -> str:
    '''
    Resolve a closed header-name constant, stripping whitespace.

    :param constants: The AppSession constants map.
    :type constants: Dict[str, str]
    :param const_key: The closed constant key.
    :type const_key: str
    :param default: The library default header name.
    :type default: str
    :return: The resolved header name.
    :rtype: str
    '''

    # Read the raw constant value.
    raw_value = constants.get(const_key)

    # Reject missing, non-string, and blank values (YAML sequences are not accepted).
    if not isinstance(raw_value, str):
        return default

    # Strip whitespace; empty after strip falls back to the default.
    stripped_value = raw_value.strip()
    if not stripped_value:
        return default

    # Return the resolved header name.
    return stripped_value

# ** function: parse_context_header_options
def parse_context_header_options(constants: Dict[str, str]) -> dict:
    '''
    Parse the closed request/correlation header names from session constants.

    Always returns both resolved names. Unknown keys are ignored. Blank or
    whitespace-only values fall back to the library defaults.

    :param constants: The resolved AppSession constants map.
    :type constants: Dict[str, str]
    :return: Both ``request_id_header`` and ``correlation_id_header`` values.
    :rtype: dict
    '''

    # Treat a missing constants map as empty.
    constants = constants or {}

    # Resolve each closed header-name key, falling back to library defaults.
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
    Copy request and correlation ids from starlette_context onto headers.

    Returns a new dict. When no request-cycle context exists, the copy is
    unchanged. Does not write ``session_id``.

    :param headers: The inbound request headers.
    :type headers: Dict[str, str]
    :param header_keys: The resolved header names from
        ``parse_context_header_options``.
    :type header_keys: dict
    :return: A new headers dict with canonical plugin ids applied.
    :rtype: Dict[str, str]
    '''

    # Copy the inbound map so the caller is not mutated.
    merged = dict(headers or {})

    # Return the copy unchanged when no request-cycle context exists.
    try:
        if not context.exists():
            return merged
    except ContextDoesNotExistError:
        return merged

    # Resolve only the two closed header names; unknown header_keys are ignored.
    header_keys = header_keys or {}
    canonical_names = (
        header_keys.get(REQUEST_ID_HEADER_CONST_KEY) or DEFAULT_REQUEST_ID_HEADER,
        header_keys.get(CORRELATION_ID_HEADER_CONST_KEY) or DEFAULT_CORRELATION_ID_HEADER,
    )

    # Copy each non-None context value onto the canonical header name.
    for canonical_name in canonical_names:

        # Look up the plugin value; a vanished context is a no-op.
        try:
            value = context.get(canonical_name)
        except ContextDoesNotExistError:
            return merged

        # Skip missing plugin values; do not invent ids here.
        if value is None:
            continue

        # Drop case-insensitive duplicates so Serve carries one canonical key.
        for existing_key in list(merged):
            if existing_key.lower() == canonical_name.lower():
                del merged[existing_key]

        # Write the plugin value under the canonical header name.
        merged[canonical_name] = str(value)

    # Return the merged headers.
    return merged
