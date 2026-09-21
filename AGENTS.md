# AGENTS.md — Tiferet Fast

## Project Overview

**Tiferet Fast** is a thin FastAPI adapter for the Tiferet Python framework. All domain objects, service interfaces, domain events, mappers, and repositories live in [tiferet-openapi](https://github.com/greatstrength/tiferet-openapi). Composable **blueprint functions** assemble a FastAPI app from a tiferet 2.1.0 session and tiferet-openapi's declared routers.

- **Repository:** https://github.com/greatstrength/tiferet-fast
- **Branch:** `v1.x-proto`
- **Python:** ≥ 3.10
- **Version:** `1.0.0b2`
- **Dependencies:** `tiferet>=2.1.0`, `tiferet-openapi>=1.0.0`, `fastapi>=0.118.0`, `starlette-context>=0.4.0`

## Architecture

### Package Layout

```
tiferet_fast/
├── assets/         # Built-in view_func and handler service-id constants
├── blueprints/     # Blueprint functions (build_fast_app, build_fast_session_context, build_router, get_routers, resolve_model)
├── contexts/       # FastApiContext (extends OpenApiSessionContext), FastRequestContext (alias)
└── __init__.py     # Version, exports
```

All domain-layer packages (`domain/`, `interfaces/`, `events/`, `mappers/`, `repos/`) live in `tiferet-openapi`. Consumers import domain types directly from `tiferet_openapi`.

### Key Concepts

- **Blueprint Functions** (`blueprints/fast.py`): Composable functions that assemble a FastAPI app.
  - `build_fast_app(interface_id, view_func=None, **parameters)` — One-call assembly of a complete FastAPI app with middleware and routers. Loads the session via `core.build_cache` / `core.get_app_session` and composes `FastApiContext` via `build_fast_session_context`. Omitting `view_func` binds the built-in asset view.
  - `build_fast_session_context(app_session, cache, ...)` — Composes a `FastApiContext` through `core.compose_session_context`, defaulting the request handler to `create_openapi_request_context`.
  - `build_router(router, view_func)` — Builds a single `APIRouter` from an `ApiRouter` domain object, passing Swagger metadata (`summary`, `description`, `tags`, `response_model`) to `add_api_route()`.
  - `get_routers(interface_context)` — Returns routers from `FastApiContext.get_routers()`.
  - `resolve_model(model_path)` — Dynamically imports a Pydantic model class by dotted path for Swagger schema generation. A bad path raises `TiferetError` with `OPENAPI_MODEL_RESOLUTION_FAILED`.
  - `FastAPI` — Alias for `build_fast_app`.
- **FastApiContext** (`contexts/fast.py`): Extends `OpenApiSessionContext` (from `tiferet_openapi`). Adds `get_routers()` wrapping the injected handler callable. Overrides `handle_error()` to convert `TiferetAPIError` into FastAPI's `HTTPException` with proper HTTP status codes and structured error details.
- **FastRequestContext** (`contexts/request.py`): Alias for `OpenApiRequestContext`. Serializes `BaseModel` results via `model_dump()`.
- **Built-in view** (`assets/view.py`): Async `view_func(request, context)` that unpacks a FastAPI `Request` and calls `context.run`. Assets never import `FastApiContext`.

### Runtime Flow

1. `build_fast_app(interface_id, view_func=None, **parameters)` is called with the interface ID and config parameters (`app_config` for the YAML file).
2. `core.build_cache()` and `core.get_app_session()` load the `AppSession`.
3. `build_fast_session_context()` composes a `FastApiContext` with OpenAPI handler closures (`get_route_handler`, `get_status_code_handler`, `get_routers_handler`) and `create_openapi_request_context`.
4. If `view_func` is omitted, blueprints bind the asset view to the composed context as a request-only FastAPI endpoint.
5. `get_routers(interface_context)` returns declared `ApiRouter` objects via `FastApiContext.get_routers()`.
6. `build_router()` resolves `response_model` via `resolve_model()` and passes Swagger metadata to `add_api_route()`.
7. A `FastAPI` instance is assembled with `starlette_context` middleware and routers, then returned.
8. At runtime, `FastApiContext.handle_error()` converts domain errors to `HTTPException` with status codes resolved via the injected status-code handler. `OpenApiSessionContext.build_response` returns `(body, status_code)`.

## Configuration

A consolidated `config.yml` at the project root contains all sections:

- `sessions` — App session definitions (`services` / `constants` for OpenAPI events and the OpenAPI repository)
- `openapi` — Routers, routes (with Swagger metadata: `summary`, `description`, `tags`, `request_model`, `response_model`), and error-to-status-code mappings
- `services` — Feature-level DI service configurations
- `features` — Feature workflows (steps with `service_id`, `params`)
- `errors` — Error definitions with multilingual messages

The `openapi_yaml_file` parameter on `openapi_service` can point to the same `config.yml`. Pass `app_config='config.yml'` to `build_fast_app` / `core.get_app_session`.

## Testing

- **Framework:** `pytest` (with `pytest_env` for environment variables).
- **Test location:** Co-located in `<package>/tests/` directories.
- **Run tests:** `pytest tiferet_fast/` from project root (with venv activated).
- **Test patterns:**
  - Blueprint tests verify `resolve_model()` and Swagger-enriched `build_router()`.
  - Context tests mock domain events and verify `HTTPException` flow.
  - Request context tests verify `BaseModel` serialization.

## Structured Code Style

Follows the Tiferet structured code style. See the [Tiferet AGENTS.md](https://github.com/greatstrength/tiferet) for full conventions:

- `# *** <section>` — Top-level (imports, exports, blueprints, contexts)
- `# ** <category>: <name>` — Mid-level (individual components)
- `# * <component>` — Low-level (attribute, init, method)
- RST docstrings with `:param`, `:type`, `:return`, `:rtype`.
- One empty line between sections and code snippets.

## Package Exports

`tiferet_fast/__init__.py` exports:

- `FastApiContext` — The FastAPI-specific API context.
- `FastRequestContext` — Alias for `OpenApiRequestContext`.
- `build_fast_app` — The primary blueprint function for assembling a FastAPI app.
- `FastAPI` — Alias for `build_fast_app`.
