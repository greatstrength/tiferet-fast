# Tiferet Fast - A FastAPI Extension for the Tiferet Framework

## Introduction

Tiferet Fast elevates the Tiferet Python framework by enabling developers to build high-performance, asynchronous APIs using FastAPI, grounded in Domain-Driven Design (DDD) principles. Starting with v0.3, Tiferet Fast uses [tiferet-openapi](https://github.com/greatstrength/tiferet-openapi) as the shared domain backbone for route configuration, Swagger metadata, and error-to-status-code mappings — leaving only FastAPI-specific concerns in this package.

In v0.4, the class-based `FastApiBuilder` is replaced by a set of composable **blueprint functions** (`build_fast_app`, `build_router`, `get_routers`, `resolve_model`), aligning with the Tiferet core blueprint pattern for a simpler, more functional API.

For a deeper understanding of Tiferet's core concepts, refer to the [Tiferet documentation](https://github.com/greatstrength/tiferet).

## Getting Started

### Requirements

- Python 3.10 or later
- [Tiferet OpenAPI](https://github.com/greatstrength/tiferet-openapi) >= 0.1.3 (pulls in [Tiferet](https://github.com/greatstrength/tiferet) transitively)

### Installation

```bash
pip install tiferet-fast
```

## Architecture (v0.4.0)

Tiferet Fast v0.4 is a thin adapter layer. Domain objects, service interfaces, domain events, mappers, and repositories all live in `tiferet-openapi`. This package provides only:

- **Blueprints** (`tiferet_fast.blueprints`) — Composable functions for assembling FastAPI applications from `ApiRouter`/`ApiRoute` domain objects:
  - `build_fast_app(interface_id, view_func, **parameters)` — One-call assembly of a complete FastAPI app with middleware and routers.
  - `build_router(router, view_func)` — Builds a single `APIRouter` from an `ApiRouter` domain object with Swagger metadata.
  - `get_routers(service_provider)` — Resolves routers via the service provider.
  - `resolve_model(model_path)` — Dynamically imports a Pydantic model class by dotted path.
  - `FastAPI` — Alias for `build_fast_app`.
- **Contexts** (`tiferet_fast.contexts`) — `FastApiContext` extends `OpenApiContext` with FastAPI-specific error handling (converts `TiferetAPIError` to `HTTPException`). `FastRequestContext` is an alias for `OpenApiRequestContext`.

All domain-layer concerns (routes, routers, request/response models, events, repos) are imported directly from `tiferet_openapi`.

## Usage

### Configuration

Tiferet v2 beta supports a consolidated `config.yml` at the project root:

```yaml
interfaces:
  calc_fast_api:
    name: Calculator FastAPI
    description: Arithmetic operations via FastAPI with Swagger docs
    module_path: tiferet_fast.contexts.fast
    class_name: FastApiContext
    attrs:
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
from fastapi import Request
from tiferet_fast import FastAPI, FastApiContext
from tiferet_openapi.blueprints.main import realize_interface, resolve_interface

# Define the view function.
async def view_func(request: Request):
    data = await request.json() if request.headers.get('content-type') == 'application/json' else {}
    data.update(dict(request.query_params))
    headers = dict(request.headers)

    response, status_code = context.run(
        feature_id=request.scope['route'].name,
        headers=headers,
        data=data,
    )
    return {'result': response}

# Build the FastAPI application in one call.
fast_app = FastAPI('calc_fast_api', view_func, app_yaml_file='config.yml')

# Realize the context for the view function closure.
app_interface, _ = resolve_interface('calc_fast_api', app_yaml_file='config.yml')
context = realize_interface(app_interface, 'calc_fast_api')
```

Serve with uvicorn:

```bash
uvicorn calc_fast_api:fast_app --reload
```

Swagger UI is available at `http://127.0.0.1:8000/docs`.

### Example

See the [`example/`](example/) directory for a complete calculator application demonstrating all features.

## Migration from v0.3.x

v0.4.0 replaces the class-based `FastApiBuilder` with composable blueprint functions:

- **`FastApiBuilder` class** — Removed. Use `build_fast_app()` (or its alias `FastAPI`) from `tiferet_fast.blueprints`.
- **`FastApiBuilder().load_app_service()`** — No longer needed. Pass `app_yaml_file` as a keyword argument to `build_fast_app()`.
- **`FastApiBuilder().run(interface_id, view_func)`** — Replace with `build_fast_app(interface_id, view_func, app_yaml_file='config.yml')`.
- **`FastApiBuilder().load_interface(interface_id)`** — Use `resolve_interface()` and `realize_interface()` from `tiferet_openapi.blueprints.main`.
- **Direct `tiferet` dependency** — Removed from `pyproject.toml`. Tiferet is now pulled in transitively via `tiferet-openapi>=0.1.3`.

### Before (v0.3.x)

```python
from tiferet_fast import FastApiBuilder

builder = FastApiBuilder()
builder.load_app_service(app_yaml_file='config.yml')
fast_app = builder.run('calc_fast_api', view_func)
context = builder.load_interface('calc_fast_api')
```

### After (v0.4.0)

```python
from tiferet_fast import FastAPI

fast_app = FastAPI('calc_fast_api', view_func, app_yaml_file='config.yml')
```

## Migration from v0.2.x

v0.3.0 removed all domain/interface/event/mapper/repo layers from this package in favor of `tiferet-openapi`:

- **`tiferet_fast.domain`** — Removed. Use `tiferet_openapi.domain` (`ApiRoute`, `ApiRouter`, `ApiRequestModel`, `ApiResponseModel`).
- **`tiferet_fast.interfaces`** — Removed. Use `tiferet_openapi.interfaces` (`OpenApiService`).
- **`tiferet_fast.events`** — Removed. Use `tiferet_openapi.events` (`GetRouters`, `GetRoute`, `GetStatusCode`).
- **`tiferet_fast.mappers`** — Removed. Use `tiferet_openapi.mappers`.
- **`tiferet_fast.repos`** — Removed. Use `tiferet_openapi.repos` (`OpenApiYamlRepository`).
- **`fast.yml`** config with `fast:` root key — Replaced by `openapi.yml` or consolidated `config.yml` with `openapi:` root key.
- **`FastApiContext`** — Now extends `OpenApiContext` (from `tiferet_openapi`) with `handle_error()` converting `TiferetAPIError` to `HTTPException`.
- **`FastRequestContext`** — Now an alias for `OpenApiRequestContext`.

## License

MIT
