# AGENTS.md — Tiferet Fast (v0.3.0)

## Project Overview

**Tiferet Fast** is a thin FastAPI adapter for the Tiferet Python framework. Starting with v0.3, all domain objects, service interfaces, domain events, mappers, and repositories live in [tiferet-openapi](https://github.com/greatstrength/tiferet-openapi). This package provides only FastAPI-specific builder assembly and context error handling.

- **Repository:** https://github.com/greatstrength/tiferet-fast
- **Branch:** `main`
- **Python:** ≥ 3.10
- **Version:** `0.3.0`
- **Dependencies:** `tiferet>=2.0.0b1`, `tiferet-openapi>=0.1.2`, `fastapi>=0.118.0`, `starlette-context>=0.4.0`

## Architecture

### Package Layout

```
tiferet_fast/
├── builders/       # FastApiBuilder (extends AppBuilder, aliased as FastAPI)
├── contexts/       # FastApiContext (extends OpenApiContext), FastRequestContext (alias)
└── __init__.py     # Version, exports
```

All domain-layer packages (`domain/`, `interfaces/`, `events/`, `mappers/`, `repos/`) were removed in v0.3. Consumers import directly from `tiferet_openapi`.

### Key Concepts

- **FastApiBuilder** (`builders/fast.py`): Extends `tiferet.builders.AppBuilder`. Primary entry point. Methods: `resolve_model()` (static, dynamic Pydantic model import), `get_routers()`, `build_router()` (passes Swagger metadata to FastAPI), `build_fast_app()`, `run()`.
- **FastApiContext** (`contexts/fast.py`): Extends `OpenApiContext` (from `tiferet_openapi`). Overrides `handle_error()` to convert `TiferetAPIError` into FastAPI's `HTTPException` with proper HTTP status codes and structured error details.
- **FastRequestContext** (`contexts/request.py`): Alias for `OpenApiRequestContext`. Serializes `BaseModel` results via `model_dump()`.

### Runtime Flow

1. `FastApiBuilder()` initializes cache and service provider.
2. `load_app_service(app_yaml_file='config.yml')` loads app configuration.
3. `load_interface(interface_id)` resolves `FastApiContext` with injected domain events (`GetRouters`, `GetRoute`, `GetStatusCode` from `tiferet_openapi`).
4. `get_routers()` resolves `get_routers_evt`, which calls `OpenApiYamlRepository.get_routers()`.
5. `build_router()` resolves `response_model` via `resolve_model()` and passes Swagger metadata (`summary`, `description`, `tags`, `response_model`) to `add_api_route()`.
6. `build_fast_app()` assembles a `FastAPI` instance with middleware and routers.
7. At runtime, `FastApiContext.handle_error()` converts domain errors to `HTTPException` with status codes resolved via `GetStatusCode`, and `handle_response()` resolves route status codes via `GetRoute`.

## Configuration

v0.3 uses the tiferet v2 beta consolidated `config.yml` strategy — a single YAML file at the project root containing all sections:

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
  - Builder tests verify `resolve_model()` and Swagger-enriched `build_router()`.
  - Context tests mock domain events and verify `HTTPException` flow.
  - Request context tests verify `BaseModel` serialization.

## Structured Code Style

Follows the Tiferet structured code style. See the [Tiferet AGENTS.md](https://github.com/greatstrength/tiferet) for full conventions:

- `# *** <section>` — Top-level (imports, exports, builders, contexts)
- `# ** <category>: <name>` — Mid-level (individual components)
- `# * <component>` — Low-level (attribute, init, method)
- RST docstrings with `:param`, `:type`, `:return`, `:rtype`.
- One empty line between sections and code snippets.

## Package Exports

`tiferet_fast/__init__.py` exports:

- `FastApiContext` — The FastAPI-specific API context.
- `FastRequestContext` — Alias for `OpenApiRequestContext`.
- `FastApiBuilder` — The primary application builder.
- `FastAPI` — Alias for `FastApiBuilder`.
