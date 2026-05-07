# Tiferet Fast - A FastAPI Extension for the Tiferet Framework

## Introduction

Tiferet Fast elevates the Tiferet Python framework by enabling developers to build high-performance, asynchronous APIs using FastAPI, grounded in Domain-Driven Design (DDD) principles. Inspired by the concept of beauty in harmony, this extension integrates Tiferet's domain-event-driven architecture with FastAPI's modern, declarative routing and automatic OpenAPI documentation. The result is a robust, modular platform for crafting scalable web services that transform complex business logic into elegant, extensible API designs.

For a deeper understanding of Tiferet's core concepts, refer to the [Tiferet documentation](https://github.com/greatstrength/tiferet).

## Getting Started

### Requirements

- Python 3.10 or later
- [Tiferet](https://github.com/greatstrength/tiferet) >= 2.0.0b1

### Installation

```bash
pip install tiferet-fast
```

### Project Structure

```plaintext
project_root/
├── calc_fast_api.py
├── app/
│   ├── events/
│   │   ├── __init__.py
│   │   ├── calc.py
│   │   └── settings.py
│   └── configs/
│       ├── __init__.py
│       ├── app.yml
│       ├── container.yml
│       ├── error.yml
│       ├── feature.yml
│       ├── fast.yml
│       └── logging.yml
```

The `app/events/` directory holds domain event classes for arithmetic operations. The `app/configs/` directory contains YAML configuration files for application interfaces, dependency injection, error handling, feature workflows, FastAPI routing, and logging. The `calc_fast_api.py` script initializes and serves the FastAPI application using `FastApiBuilder`.

## Architecture (v0.2.0)

Tiferet Fast v0.2.0 aligns with the Tiferet v2.0 layered architecture:

- **Domain** (`tiferet_fast.domain`) — `FastRoute`, `FastRouter` domain objects (Pydantic v2).
- **Interfaces** (`tiferet_fast.interfaces`) — `FastApiService` abstract service contract.
- **Mappers** (`tiferet_fast.mappers`) — Aggregates and YAML TransferObjects for routes/routers.
- **Events** (`tiferet_fast.events`) — `GetRouters`, `GetRoute`, `GetStatusCode` domain events.
- **Repos** (`tiferet_fast.repos`) — `FastYamlRepository` (YamlLoader-based service implementation).
- **Contexts** (`tiferet_fast.contexts`) — `FastApiContext`, `FastRequestContext`.
- **Builders** (`tiferet_fast.builders`) — `FastApiBuilder` (primary entry point, aliased as `FastAPI`).

## Usage

### Configuring Routes in `fast.yml`

```yaml
fast:
  routers:
    calc:
      prefix: /calc
      routes:
        add:
          path: /add
          methods: [POST, GET]
          status_code: 200
        subtract:
          path: /subtract
          methods: [POST, GET]
          status_code: 200
  errors:
    INVALID_INPUT: 400
    DIVISION_BY_ZERO: 422
```

### Configuring the App Interface in `app.yml`

```yaml
interfaces:
  calc_fast_api:
    name: Basic Calculator API
    description: Perform basic calculator operations via FastAPI
    module_path: tiferet_fast.contexts.fast
    class_name: FastApiContext
    attrs:
      get_route_evt:
        module_path: tiferet_fast.events.fast
        class_name: GetRoute
      get_status_code_evt:
        module_path: tiferet_fast.events.fast
        class_name: GetStatusCode
      fast_api_service:
        module_path: tiferet_fast.repos.fast
        class_name: FastYamlRepository
        params:
          fast_yaml_file: app/configs/fast.yml
```

### Building and Running the API

```python
from tiferet_fast import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse

# Create the builder and load the app service.
app = FastAPI()
app.load_app_service()

# Load the interface context.
context = app.load_interface('calc_fast_api')

# Define a view function for handling requests.
async def view_func(request: Request):
    data = await request.json() if request.headers.get('content-type') == 'application/json' else {}
    data.update(dict(request.query_params))
    headers = dict(request.headers)

    response, status_code = context.run(
        feature_id=request.scope['route'].name,
        headers=headers,
        data=data,
    )
    return JSONResponse(response, status_code=status_code)

# Build the FastAPI application.
fast_app = app.build_fast_app('calc_fast_api', view_func=view_func)

# Serve with uvicorn.
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(fast_app, host='127.0.0.1', port=8000)
```

### Testing the API

```bash
# Add two numbers
curl -X POST http://127.0.0.1:8000/calc/add -H "Content-Type: application/json" -d '{"a": 1, "b": 2}'
# Output: 3

# Calculate square root
curl -X POST http://127.0.0.1:8000/calc/sqrt -H "Content-Type: application/json" -d '{"a": 16}'
# Output: 4.0
```

## Migration from v0.1.x

v0.2.0 is a breaking release that aligns with Tiferet v2.0:

- **`models/`** → `domain/` (Pydantic v2 `DomainObject` replaces schematics `ModelObject`)
- **`contracts/`** → `interfaces/` (`Service(ABC)` replaces typed contracts)
- **`data/`** → `mappers/` (`Aggregate` + `TransferObject` replace `DataObject`)
- **`handlers/`** → `events/` (`DomainEvent` subclasses replace handler classes)
- **`proxies/`** → `repos/` (`YamlLoader` composition replaces `YamlConfigurationProxy` inheritance)
- **`FastApiContext.build_fast_app()`** → `FastApiBuilder.build_fast_app()` (builder pattern)
- **Top-level export**: `from tiferet_fast import FastAPI` (alias for `FastApiBuilder`)

## License

MIT
