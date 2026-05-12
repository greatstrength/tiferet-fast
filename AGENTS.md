# AGENTS.md — Tiferet Fast (v0.4.0)

## Project Overview

**Tiferet Fast** is a thin FastAPI adapter for the Tiferet Python framework. Starting with v0.3, all domain objects, service interfaces, domain events, mappers, and repositories live in [tiferet-openapi](https://github.com/greatstrength/tiferet-openapi). In v0.4, the class-based `FastApiBuilder` is replaced by composable **blueprint functions**, aligning with the Tiferet core blueprint pattern.

- **Repository:** https://github.com/greatstrength/tiferet-fast
- **Branch:** `main`
- **Python:** ≥ 3.10
- **Version:** `0.4.0`
- **Dependencies:** `tiferet-openapi>=0.1.3`, `fastapi>=0.118.0`, `starlette-context>=0.4.0`

## Architecture

### Package Layout

```
tiferet_fast/
├── blueprints/     # Blueprint functions (build_fast_app, build_router, get_routers, resolve_model)
├── contexts/       # FastApiContext (extends OpenApiContext), FastRequestContext (alias)
└── __init__.py     # Version, exports
```

All domain-layer packages (`domain/`, `interfaces/`, `events/`, `mappers/`, `repos/`) were removed in v0.3. The `builders/` package was removed in v0.4 in favor of `blueprints/`. Consumers import domain types directly from `tiferet_openapi`.

### Key Concepts

- **Blueprint Functions** (`blueprints/fast.py`): Composable functions that replace the `FastApiBuilder` class.
  - `build_fast_app(interface_id, view_func, **parameters)` — One-call assembly of a complete FastAPI app with middleware and routers. Uses `resolve_interface()` and `realize_interface()` from `tiferet.blueprints.main`.
  - `build_router(router, view_func)` — Builds a single `APIRouter` from an `ApiRouter` domain object, passing Swagger metadata (`summary`, `description`, `tags`, `response_model`) to `add_api_route()`.
  - `get_routers(service_provider)` — Resolves the `get_routers_evt` from the service provider and executes it.
  - `resolve_model(model_path)` — Dynamically imports a Pydantic model class by dotted path for Swagger schema generation.
  - `FastAPI` — Alias for `build_fast_app`.
- **FastApiContext** (`contexts/fast.py`): Extends `OpenApiContext` (from `tiferet_openapi`). Overrides `handle_error()` to convert `TiferetAPIError` into FastAPI's `HTTPException` with proper HTTP status codes and structured error details.
- **FastRequestContext** (`contexts/request.py`): Alias for `OpenApiRequestContext`. Serializes `BaseModel` results via `model_dump()`.

### Runtime Flow

1. `build_fast_app(interface_id, view_func, **parameters)` is called with the interface ID, view function, and config parameters.
2. `resolve_interface()` (from `tiferet.blueprints.main`) loads the interface definition and default services from YAML config.
3. `realize_interface()` instantiates the `FastApiContext` with injected domain events (`GetRouters`, `GetRoute`, `GetStatusCode` from `tiferet_openapi`).
4. A `ServiceProvider` is created and seeded with default service dependencies.
5. `get_routers()` resolves `get_routers_evt`, which calls `OpenApiYamlRepository.get_routers()`.
6. `build_router()` resolves `response_model` via `resolve_model()` and passes Swagger metadata to `add_api_route()`.
7. A `FastAPI` instance is assembled with middleware and routers, then returned.
8. At runtime, `FastApiContext.handle_error()` converts domain errors to `HTTPException` with status codes resolved via `GetStatusCode`, and `handle_response()` resolves route status codes via `GetRoute`.

## Configuration

v0.4 uses the tiferet v2 beta consolidated `config.yml` strategy — a single YAML file at the project root containing all sections:

- `interfaces` — App interface definitions (module_path, class_name, service dependencies)
- `openapi` — Routers, routes (with Swagger metadata: `summary`, `description`, `tags`, `request_model`, `response_model`), and error-to-status-code mappings
- `services` — Feature-level DI service configurations
- `features` — Feature workflows (steps with `service_id`, `params`)
- `errors` — Error definitions with multilingual messages

The `openapi_yaml_file` parameter in the interface config can point to the same `config.yml`.

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
