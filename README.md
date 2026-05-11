# Tiferet Fast - A FastAPI Extension for the Tiferet Framework

## Introduction

Tiferet Fast elevates the Tiferet Python framework by enabling developers to build high-performance, asynchronous APIs using FastAPI, grounded in Domain-Driven Design (DDD) principles. Starting with v0.3, Tiferet Fast uses [tiferet-openapi](https://github.com/greatstrength/tiferet-openapi) as the shared domain backbone for route configuration, Swagger metadata, and error-to-status-code mappings — leaving only FastAPI-specific concerns (builder assembly and context error handling) in this package.

For a deeper understanding of Tiferet's core concepts, refer to the [Tiferet documentation](https://github.com/greatstrength/tiferet).

## Getting Started

### Requirements

- Python 3.10 or later
- [Tiferet](https://github.com/greatstrength/tiferet) >= 2.0.0b1
- [Tiferet OpenAPI](https://github.com/greatstrength/tiferet-openapi) >= 0.1.2

### Installation

```bash
pip install tiferet-fast
```

## Architecture (v0.3.0)

Tiferet Fast v0.3 is a thin adapter layer. Domain objects, service interfaces, domain events, mappers, and repositories all live in `tiferet-openapi`. This package provides only:

- **Builders** (`tiferet_fast.builders`) — `FastApiBuilder` extends `AppBuilder` to assemble FastAPI applications from `ApiRouter`/`ApiRoute` domain objects, with Swagger model resolution via `resolve_model()`.
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

Routes support Swagger metadata fields (`summary`, `description`, `tags`, `request_model`, `response_model`). The `response_model` is dynamically resolved by `FastApiBuilder.resolve_model()` and passed to FastAPI's `add_api_route()` for native Swagger schema generation.

### Building and Running the API

```python
from fastapi import Request
from tiferet_fast import FastApiBuilder

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

# Create the builder and load configuration.
builder = FastApiBuilder()
builder.load_app_service(app_yaml_file='config.yml')

# Build the FastAPI application.
fast_app = builder.run('calc_fast_api', view_func)

# Access the context for the view function closure.
context = builder.load_interface('calc_fast_api')
```

Serve with uvicorn:

```bash
uvicorn calc_fast_api:fast_app --reload
```

Swagger UI is available at `http://127.0.0.1:8000/docs`.

### Example

See the [`example/`](example/) directory for a complete calculator application demonstrating all v0.3 features.

## Migration from v0.2.x

v0.3.0 removes all domain/interface/event/mapper/repo layers from this package in favor of `tiferet-openapi`:

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
