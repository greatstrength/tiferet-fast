# Tiferet Fast - A FastAPI Extension for the Tiferet Framework

## Introduction

Tiferet Fast elevates the Tiferet Python framework by enabling developers to build high-performance, asynchronous APIs using FastAPI, grounded in Domain-Driven Design (DDD) principles. It uses [tiferet-openapi](https://github.com/greatstrength/tiferet-openapi) as the shared domain backbone for route configuration, Swagger metadata, and error-to-status-code mappings — leaving only FastAPI-specific concerns in this package.

Composable **blueprint functions** (`build_fast_app`, `build_fast_session_context`, `build_router`, `get_routers`, `resolve_model`) assemble a FastAPI app from a tiferet `AppSession` and tiferet-openapi's declared routers.

For a deeper understanding of Tiferet's core concepts, refer to the [Tiferet documentation](https://github.com/greatstrength/tiferet).

## Getting Started

### Requirements

- Python 3.10 or later
- [Tiferet](https://github.com/greatstrength/tiferet) >= 2.1.0
- [Tiferet OpenAPI](https://github.com/greatstrength/tiferet-openapi) >= 1.0.0

### Installation

```bash
pip install tiferet-fast
```

## Architecture

Tiferet Fast is a thin adapter layer. Domain objects, service interfaces, domain events, mappers, and repositories all live in `tiferet-openapi`. This package provides only:

- **Assets** (`tiferet_fast.assets`) — A built-in `view_func(request, context)` that unpacks a FastAPI `Request` and calls `context.run`. The view never imports `FastApiContext`.
- **Blueprints** (`tiferet_fast.blueprints`) — Composable functions for assembling FastAPI applications from `ApiRouter`/`ApiRoute` domain objects:
  - `build_fast_app(interface_id, view_func=None, **parameters)` — One-call assembly of a complete FastAPI app. Loads the session via `core.build_cache` / `core.get_app_session`, composes `FastApiContext` via `build_fast_session_context`, and binds the built-in view when `view_func` is omitted.
  - `build_fast_session_context(app_session, cache, ...)` — Composes a `FastApiContext` through `core.compose_session_context`.
  - `build_router(router, view_func)` — Builds a single `APIRouter` from an `ApiRouter` domain object with Swagger metadata.
  - `get_routers(interface_context)` — Returns routers from `FastApiContext.get_routers()`.
  - `resolve_model(model_path)` — Dynamically imports a Pydantic model class by dotted path. A bad path raises `TiferetError` with `OPENAPI_MODEL_RESOLUTION_FAILED`.
  - `FastAPI` — Alias for `build_fast_app`.
- **Contexts** (`tiferet_fast.contexts`) — `FastApiContext` extends `OpenApiSessionContext` with FastAPI-specific error handling (converts `TiferetAPIError` to `HTTPException`). `FastRequestContext` is an alias for `OpenApiRequestContext`.

All domain-layer concerns (routes, routers, request/response models, events, repos) are imported directly from `tiferet_openapi`.

## Usage

### Configuration

Tiferet v2 beta supports a consolidated `config.yml` at the project root:

```yaml
sessions:
  calc_fast_api:
    name: Calculator FastAPI
    description: Arithmetic operations via FastAPI with Swagger docs
    services:
      get_routers_evt:
        module_path: tiferet_openapi.events.openapi
        class_name: GetRouters
      get_route_evt:
        module_path: tiferet_openapi.events.openapi
        class_name: GetRoute
      get_status_code_evt:
        module_path: tiferet_openapi.events.openapi
        class_name: GetStatusCode
      openapi_service:
        module_path: tiferet_openapi.repos.openapi
        class_name: OpenApiYamlRepository
        params:
          openapi_yaml_file: config.yml

openapi:
  routers:
    calc:
      prefix: /calc
      routes:
        add:
          path: /add
          methods: [POST]
          status_code: 200
          summary: Add two numbers
          description: Adds two numbers and returns the result.
          request_model: app.domain.request.TwoOperandRequest
          response_model: app.domain.request.CalculatorResponse
  errors:
    DIVISION_BY_ZERO: 400
    INVALID_INPUT: 422
```

Routes support Swagger metadata fields (`summary`, `description`, `tags`, `request_model`, `response_model`). The `response_model` is dynamically resolved by `resolve_model()` and passed to FastAPI's `add_api_route()` for native Swagger schema generation.

### Building and Running the API

```python
from tiferet_fast import FastAPI

# Build the FastAPI application in one call. The built-in view is used when
# view_func is omitted; pass an optional request-only view to override it.
fast_app = FastAPI('calc_fast_api', app_config='config.yml')
```

Serve with uvicorn:

```bash
uvicorn calc_fast_api:fast_app --reload
```

Swagger UI is available at `http://127.0.0.1:8000/docs`.

### Example

See the [`example/`](example/) directory for a complete calculator application demonstrating all features.

## Migration from v0.3.x / v0.4.x

The class-based `FastApiBuilder` was replaced by composable blueprint functions. Session composition now goes through tiferet 2.1.0 (`core.build_cache` / `core.get_app_session` / `build_fast_session_context`). A consumer `view_func` is optional; omit it to use the built-in asset view.

```python
from tiferet_fast import FastAPI

fast_app = FastAPI('calc_fast_api', app_config='config.yml')
```

## Migration from v0.2.x

v0.3.0 removed all domain/interface/event/mapper/repo layers from this package in favor of `tiferet-openapi`:

- **`tiferet_fast.domain`** — Removed. Use `tiferet_openapi.domain` (`ApiRoute`, `ApiRouter`, `ApiRequestModel`, `ApiResponseModel`).
- **`tiferet_fast.interfaces`** — Removed. Use `tiferet_openapi.interfaces` (`OpenApiService`).
- **`tiferet_fast.events`** — Removed. Use `tiferet_openapi.events` (`GetRouters`, `GetRoute`, `GetStatusCode`).
- **`tiferet_fast.mappers`** — Removed. Use `tiferet_openapi.mappers`.
- **`tiferet_fast.repos`** — Removed. Use `tiferet_openapi.repos` (`OpenApiYamlRepository`).
- **`fast.yml`** config with `fast:` root key — Replaced by `openapi.yml` or consolidated `config.yml` with `openapi:` root key.
- **`FastApiContext`** — Extends `OpenApiSessionContext` (from `tiferet_openapi`) with `handle_error()` converting `TiferetAPIError` to `HTTPException`.
- **`FastRequestContext`** — Now an alias for `OpenApiRequestContext`.

## License

MIT
