# AGENTS.md — Tiferet Fast (v0.2.0)

## Project Overview

**Tiferet Fast** is a FastAPI extension for the Tiferet Python framework, enabling high-performance asynchronous APIs grounded in Domain-Driven Design (DDD). It extends Tiferet's layered architecture with FastAPI-specific builders, contexts, domain events, and YAML-backed route configuration.

- **Repository:** https://github.com/greatstrength/tiferet-fast
- **Branch:** `main`
- **Python:** ≥ 3.10
- **Version:** `0.2.0`
- **Dependency:** `tiferet>=2.0.0b1`

## Architecture

### Package Layout

```
tiferet_fast/
├── builders/       # FastApiBuilder (primary entry point, aliased as FastAPI)
├── contexts/       # FastApiContext, FastRequestContext
├── domain/         # FastRoute, FastRouter (Pydantic v2 DomainObject)
├── events/         # GetRouters, GetRoute, GetStatusCode (DomainEvent subclasses)
├── interfaces/     # FastApiService (Service ABC)
├── mappers/        # Aggregates + YAML TransferObjects for routes/routers
├── repos/          # FastYamlRepository (YamlLoader-based FastApiService impl)
└── __init__.py     # Version, exports (FastApiBuilder, FastAPI alias)
```

### Key Concepts

- **FastApiBuilder** (`builders/fast.py`): Extends `tiferet.builders.AppBuilder`. Primary entry point for building FastAPI applications. Methods: `get_routers()`, `build_router()`, `build_fast_app()`, `run()`. Exported as `FastAPI` alias.
- **FastApiContext** (`contexts/fast.py`): Extends `AppInterfaceContext`. Manages request/response lifecycle. Accepts `get_route_evt` and `get_status_code_evt` domain events. Handles error formatting via `TiferetAPIError` with HTTP status codes.
- **FastRequestContext** (`contexts/request.py`): Extends `RequestContext`. Serializes `BaseModel` results via `model_dump()`.
- **FastRoute / FastRouter** (`domain/fast.py`): Pydantic v2 `DomainObject` subclasses defining route and router structure.
- **FastApiService** (`interfaces/fast.py`): `Service(ABC)` with `get_routers()`, `get_route()`, `get_status_code()`.
- **GetRouters / GetRoute / GetStatusCode** (`events/fast.py`): `DomainEvent` subclasses injected with `FastApiService`.
- **FastYamlRepository** (`repos/fast.py`): Implements `FastApiService` using `YamlLoader` for YAML file access and `FastRouterYamlObject` for mapping.
- **Mappers** (`mappers/fast.py`): `FastRouteAggregate`, `FastRouterAggregate`, `FastRouteYamlObject`, `FastRouterYamlObject`.

### Runtime Flow

1. `FastApiBuilder()` initializes cache and service provider.
2. `load_app_service()` loads app configuration.
3. `load_interface(interface_id)` resolves `FastApiContext` with injected domain events.
4. `get_routers()` resolves `get_routers_evt` from the service provider, which calls `FastYamlRepository.get_routers()`.
5. `build_fast_app()` assembles a `FastAPI` instance with middleware and routers.
6. At runtime, `FastApiContext.handle_error()` resolves HTTP status codes via `GetStatusCode` event, and `handle_response()` resolves route status codes via `GetRoute` event.

## Configuration

Applications are configured via YAML files:

- `app.yml` — Interface definitions (module_path, class_name, service dependencies)
- `fast.yml` — FastAPI routers, routes, and error-to-status-code mappings
- `container.yml` — Feature-level DI service configurations
- `feature.yml` — Feature workflows (steps with service_id, parameters)
- `error.yml` — Error definitions with multilingual messages
- `logging.yml` — Logging formatters, handlers, loggers

## Testing

- **Framework:** `pytest` (with `pytest_env` for environment variables).
- **Test location:** Co-located in `<package>/tests/` directories.
- **Run tests:** `pytest tiferet_fast/` from project root (with venv activated).
- **Test patterns:**
  - Domain event tests use `DomainEvent.handle()` with mocked `FastApiService`.
  - Repository tests use `tmp_path` fixtures with real temporary YAML files.
  - Context tests mock domain events and verify `TiferetAPIError` flow.

## Structured Code Style

Follows the Tiferet structured code style. See the [Tiferet AGENTS.md](https://github.com/greatstrength/tiferet) for full conventions:

- `# *** <section>` — Top-level (imports, exports, builders, contexts, events, etc.)
- `# ** <category>: <name>` — Mid-level (individual components)
- `# * <component>` — Low-level (attribute, init, method)
- RST docstrings with `:param`, `:type`, `:return`, `:rtype`.
- One empty line between sections and code snippets.

## Package Exports

`tiferet_fast/__init__.py` exports:

- `FastApiBuilder` — The primary application builder.
- `FastAPI` — Alias for `FastApiBuilder`.

## Migration from v0.1.x

| v0.1.x Package | v0.2.0 Package | Key Change |
|---|---|---|
| `models/` | `domain/` | Pydantic v2 `DomainObject` replaces schematics `ModelObject` |
| `contracts/` | `interfaces/` | `Service(ABC)` replaces typed contracts |
| `data/` | `mappers/` | `Aggregate` + `TransferObject` replace `DataObject` |
| `handlers/` | `events/` | `DomainEvent` subclasses replace handler classes |
| `proxies/` | `repos/` | `YamlLoader` composition replaces inheritance |
| N/A | `builders/` | New `FastApiBuilder(AppBuilder)` entry point |
