# Calculator FastAPI Example

A self-contained calculator API demonstrating the Tiferet Fast v0.3 architecture: domain events, YAML-driven configuration, OpenAPI route metadata, and native Swagger UI via FastAPI.

## Prerequisites

- Python 3.10+
- A virtual environment (recommended)

## Setup

```bash
# Create and activate a virtual environment
python3.10 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install tiferet-fast uvicorn
```

## Running

From the `example/` directory:

```bash
uvicorn calc_fast_api:fast_app --reload
```

The server starts at `http://127.0.0.1:8000`.

## Swagger UI

FastAPI's built-in Swagger UI is available at:

```
http://127.0.0.1:8000/docs
```

All routes display enriched documentation (`summary`, `description`, `tags`) and typed request/response schemas (`TwoOperandRequest`, `SingleOperandRequest`, `CalculatorResponse`) resolved from the `request_model` and `response_model` fields in `config.yml`.

## Endpoints

All endpoints accept JSON POST requests.

### Add — `POST /calc/add`

```bash
curl -X POST http://127.0.0.1:8000/calc/add \
  -H "Content-Type: application/json" \
  -d '{"a": 3, "b": 5}'
# {"result": 8.0}
```

### Subtract — `POST /calc/subtract`

```bash
curl -X POST http://127.0.0.1:8000/calc/subtract \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "b": 4}'
# {"result": 6.0}
```

### Multiply — `POST /calc/multiply`

```bash
curl -X POST http://127.0.0.1:8000/calc/multiply \
  -H "Content-Type: application/json" \
  -d '{"a": 6, "b": 7}'
# {"result": 42.0}
```

### Divide — `POST /calc/divide`

```bash
curl -X POST http://127.0.0.1:8000/calc/divide \
  -H "Content-Type: application/json" \
  -d '{"a": 20, "b": 4}'
# {"result": 5.0}
```

### Square Root — `POST /calc/sqrt`

```bash
curl -X POST http://127.0.0.1:8000/calc/sqrt \
  -H "Content-Type: application/json" \
  -d '{"a": 16}'
# {"result": 4.0}
```

## Error Handling

Errors return structured JSON with appropriate HTTP status codes:

### Division by Zero — `400`

```bash
curl -X POST http://127.0.0.1:8000/calc/divide \
  -H "Content-Type: application/json" \
  -d '{"a": 5, "b": 0}'
# {"detail": {"error": "Division By Zero", "message": "Cannot divide by zero"}}
```

### Invalid Input — `422`

Non-numeric inputs are rejected by the domain validation layer with structured error responses.

## Project Structure

```
example/
├── calc_fast_api.py        # FastAPI entry point
├── config.yml              # Consolidated configuration
├── README.md
└── app/
    ├── domain/
    │   ├── __init__.py
    │   └── request.py      # Request/response Pydantic models
    ├── events/
    │   ├── __init__.py
    │   └── calc.py         # Arithmetic domain events
    └── utils/
        ├── __init__.py
        └── calc.py         # Number validation utility
```

## Configuration

This example uses the v2 beta consolidated `config.yml` strategy — a single YAML file at the project root containing all configuration sections:

- **`interfaces`** — App interface definition pointing to `FastApiContext`
- **`openapi`** — Router/route definitions with Swagger metadata (`summary`, `description`, `request_model`, `response_model`) and error-to-status-code mappings
- **`services`** — DI container mappings for domain events
- **`errors`** — Structured error definitions with multilingual support
- **`features`** — Feature workflows mapping routes to domain event steps
