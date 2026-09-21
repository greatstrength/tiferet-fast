**Status:** Draft · **Domain:** `tiferet-fast` · **Code:** `tiferet_fast/` · **Branch:** `v1.x-proto`

# tiferet-fast: Domain Vision Statement

## The bet: a route declared once should just run under FastAPI

tiferet-openapi lets a Tiferet application declare its routes, request/response shapes, and error mappings once, in configuration, and derive a working router, a generated specification, and documentation data from that single declaration. That bet is only real if a team can actually pick FastAPI and get all of it — for free, without writing FastAPI-specific routing or error-translation code by hand, and without that adapter silently falling behind the shared layer it sits on.

tiferet-fast's bet is that "pick FastAPI" should cost a team nothing more than choosing which framework runs underneath. Wiring a declared router into `fastapi.APIRouter.add_api_route`, translating a domain error into `ApiErrorResponse` JSON at the FastAPI exception-handler boundary, and assembling a runnable `FastAPI` app from an interface ID are FastAPI's own idioms — not places where the shared declaration's promises should have to be re-earned per framework.

## What this domain makes real

tiferet-fast is the thin FastAPI-specific adapter over tiferet-openapi's shared declaration. Given an interface ID, a view function, and a `config.yml`, it resolves the declared routers and routes, builds a real `fastapi.APIRouter` per router (Swagger metadata included) via `add_api_route`, assembles a runnable `FastAPI` application with request-context middleware, and converts a domain-level `TiferetAPIError` into `ApiErrorResponse` JSON at the FastAPI exception-handler boundary — all without a person writing FastAPI routing code for each new route.

## What we get for it

**One call to a running app.** `build_fast_app(interface_id, view_func, **parameters)` — or its `FastAPI` alias — resolves the interface, seeds a service provider, and returns a fully wired `FastAPI` instance with routers included. A consuming application supplies a `config.yml` and a view function; it does not hand-assemble `APIRouter`s itself.

**Structured API errors, not FastAPI's `{"detail": ...}` envelope.** `handle_tiferet_api_error`, registered once on the assembled FastAPI app, maps a raised `TiferetAPIError` onto `ApiErrorResponse` `{error, message}` JSON. Status-code resolution stays on the inherited OpenAPI session hub; the context does not raise `HTTPException`.

**Swagger metadata is data, not code.** `build_router` reads `summary`, `description`, `tags`, and `response_model` straight off each declared `ApiRoute` and hands them to `add_api_route`. A route's documentation text is edited in `config.yml`, not in a `tiferet_fast` source file.

## The core of the work

Every request tiferet-fast serves goes through the same short path:

> **Resolve** the interface and pre-seed a service provider from its declared constants → **assemble** a `FastAPI` app by building one `APIRouter` per declared `ApiRouter` → **serve** each request through the caller-supplied `view_func`, which asks the realized context to run the matching feature → **translate** any `TiferetAPIError` the context raises into `ApiErrorResponse` JSON before it reaches the client.

The commitment underneath all four steps: tiferet-fast introduces no second declaration and no domain logic of its own. Every fact about what a route looks like — path, methods, status code, documentation — is read from the `ApiRoute`/`ApiRouter` objects tiferet-openapi already produced from the same `config.yml`. This domain's job is narrowly to hand FastAPI what it needs to run and document those routes, not to decide what they are.

## What it deliberately does not do

tiferet-fast does not declare routes, request/response shapes, or error-to-status mappings — that vocabulary and its parsing belong entirely to tiferet-openapi (`ApiRoute`, `ApiRouter`, `OpenApiYamlRepository`, the three domain events). tiferet-fast only consumes what that layer already produced.

It does not generate or serve an OpenAPI specification of its own. Whatever a client sees at FastAPI's native `/openapi.json` and `/docs` is built entirely from the Swagger keyword arguments (`summary`, `description`, `tags`, `response_model`) that `build_router` passes to `add_api_route` — FastAPI derives its own schema from those at request time. tiferet-fast does not call, and currently has no route wired to, `OpenApiSessionContext.generate_spec` or `get_docs_spec`.

It does not decide what a route's business logic does. `view_func` is supplied by the consuming application; tiferet-fast only routes an incoming HTTP request to it and shapes the exception it might raise.

It does not own request parsing or response serialization semantics — `FastRequestContext` is a plain alias for tiferet-openapi's `OpenApiRequestContext`; tiferet-fast adds nothing to that behavior.

---

*Companion document:* `docs/core-domain-distillation.md` — the detailed walkthrough of the domain's vocabulary, behaviors, and current gaps against tiferet-openapi v1.0.0 and tiferet v2.1.0.
