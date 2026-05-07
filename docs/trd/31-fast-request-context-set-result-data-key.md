# Technical Requirements Document: FastRequestContext.set_result() Missing data_key Parameter

**Project:** Tiferet Fast  
**Repository:** https://github.com/greatstrength/tiferet-fast  
**Date:** May 07, 2026  
**Version:** 0.2.1

## 1. Overview

`FastRequestContext.set_result()` in `tiferet_fast/contexts/request.py` does not accept the `data_key` parameter defined by the parent `RequestContext.set_result(result, data_key=None)`. This causes intermediate pipeline results — those stored via `data_key` for downstream commands — to be serialized into plain dicts via `model_dump()` and written to `self.result` instead of being preserved as raw domain objects in `self.data[data_key]`. Downstream commands that access model attributes on the stored result raise `AttributeError`.

The fix adds the `data_key` parameter to the override, delegates to the parent when `data_key` is provided (preserving raw objects for downstream consumption), and restricts `BaseModel` serialization to the final-response path only.

## 2. Scope

### In Scope
- Add `data_key: str = None` parameter to `FastRequestContext.set_result()`.
- Delegate to `super().set_result(result, data_key)` when `data_key` is provided, preserving the raw result.
- Restrict `BaseModel` → `model_dump()` serialization to the final-response path (`data_key is None`).
- Add unit tests covering the `data_key` path.
- Bump version to `0.2.1`.

### Out of Scope
- Changes to the parent `tiferet.contexts.request.RequestContext`.
- Changes to `FastApiContext`, `FastRequestContext.handle_response()`, or any other context method.
- New features or configuration changes.

## 3. Components Affected

| Component | File/Path | Changes |
|-----------|-----------|---------|
| FastRequestContext | `tiferet_fast/contexts/request.py` | Add `data_key` parameter to `set_result()`, delegate to parent when `data_key` is provided. |
| Tests | `tiferet_fast/contexts/tests/test_request.py` | Add tests for `data_key` storage of raw objects (BaseModel, primitive, list). |
| Version | `tiferet_fast/__init__.py` | Bump `__version__` from `0.2.0` to `0.2.1`. |

## 4. Detailed Requirements

### 4.1 Fix `FastRequestContext.set_result()`

Update the method signature to accept `data_key` and delegate to the parent when it is provided:

```python
# * method: set_result
def set_result(self, result: Any, data_key: str = None):
    '''
    Set the result of the request context.

    :param result: The result to set.
    :type result: Any
    :param data_key: The key in the request data to set the result to.
        If provided, the raw result is stored for downstream commands.
        If None, the result is serialized for the final response.
    :type data_key: str
    '''

    # If a data key is provided, delegate to the parent to store the raw result.
    if data_key:
        super().set_result(result, data_key=data_key)
        return

    # If the response is None, return an empty response.
    if result is None:
        self.result = ''

    # Convert the response to a dictionary if it's a BaseModel.
    elif isinstance(result, BaseModel):
        self.result = result.model_dump()

    # If the response is a list containing BaseModel instances, convert each to a dictionary.
    elif isinstance(result, list) and all(isinstance(item, BaseModel) for item in result):
        self.result = [item.model_dump() for item in result]

    # If the response is a dict containing BaseModel instances, convert each to a dictionary.
    elif isinstance(result, dict) and all(isinstance(value, BaseModel) for value in result.values()):
        self.result = {key: value.model_dump() for key, value in result.items()}

    # Otherwise, set the result directly.
    else:
        self.result = result
```

### 4.2 New Tests

Add three tests to `test_request.py`:

1. **`test_fast_request_context_set_result_data_key_domain_object`** — Call `set_result(DomainObject(...), data_key='obj')`. Assert `self.data['obj']` is the original `DomainObject` (not a dict) and `self.result` is `None`.
2. **`test_fast_request_context_set_result_data_key_primitive`** — Call `set_result('raw_string', data_key='raw')`. Assert `self.data['raw']` == `'raw_string'` and `self.result` is `None`.
3. **`test_fast_request_context_set_result_data_key_list`** — Call `set_result([DomainObject(...), DomainObject(...)], data_key='items')`. Assert `self.data['items']` is the original list of `DomainObject` instances and `self.result` is `None`.

### 4.3 Version Bump

Update `tiferet_fast/__init__.py`:
```python
__version__ = "0.2.1"
```

## 5. Acceptance Criteria

1. `FastRequestContext.set_result(result, data_key='key')` stores the raw `result` in `self.data['key']` without serialization.
2. `FastRequestContext.set_result(result)` (no `data_key`) continues to serialize `BaseModel` instances via `model_dump()` as before.
3. All existing tests in `test_request.py` continue to pass.
4. Three new `data_key` tests pass.
5. `tiferet_fast.__version__` is `0.2.1`.
6. Feature branch follows naming convention: `31-fast-request-context-set-result-data-key`.
7. PR targets the `v0.2.1-release` branch.

## 6. Non-Functional Requirements

- Method signature remains backward-compatible (`data_key` defaults to `None`).
- Structured code style (artifact comments, RST docstrings, snippet spacing) is maintained.
- No new dependencies introduced.

## Related Code Style Documentation

- [code_style.md](https://github.com/greatstrength/tiferet/blob/v2.0-proto/docs/core/code_style.md) — General structured code style.
- [contexts.md](https://github.com/greatstrength/tiferet/blob/v2.0-proto/docs/core/contexts.md) — Context-specific conventions.
