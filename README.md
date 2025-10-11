# Tiferet Fast - A FastAPI Extension for the Tiferet Framework

## Introduction

Tiferet Fast elevates the Tiferet Python framework by enabling developers to build high-performance, asynchronous APIs using FastAPI, grounded in Domain-Driven Design (DDD) principles. Inspired by the concept of beauty in harmony, this extension integrates Tiferet’s command-driven architecture with FastAPI’s modern, declarative routing and automatic OpenAPI documentation. The result is a robust, modular platform for crafting scalable web services that transform complex business logic into elegant, extensible API designs.

This tutorial guides you through creating a streamlined calculator API, leveraging Tiferet’s commands and configurations while introducing FastAPI-specific interfaces and endpoints. For a deeper understanding of Tiferet’s core concepts, refer to the [Tiferet documentation](https://github.com/greatstrength/tiferet).

## Getting Started with Tiferet Fast

Begin your Tiferet Fast journey by setting up your development environment. This guide assumes familiarity with Tiferet’s core setup.

### Installing Python

Tiferet Fast requires Python 3.10 or later. Follow the detailed [Python installation instructions](https://github.com/greatstrength/tiferet?tab=readme-ov-file#installing-python) in the Tiferet README for your platform (Windows, macOS, or Linux). Verify your installation with:

```bash
python3.10 --version
```

### Setting Up a Virtual Environment

Create a dedicated virtual environment named `tiferet_fast_app` to manage dependencies:

```bash
# Create the Environment
# Windows
python -m venv tiferet_fast_app

# macOS/Linux
python3.10 -m venv tiferet_fast_app

# Activate the Environment
# Windows (Command Prompt)
tiferet_fast_app\Scripts\activate

# Windows (PowerShell)
.\tiferet_fast_app\Scripts\Activate.ps1

# macOS/Linux
source tiferet_fast_app/bin/activate
```

Exit the environment with `deactivate` when finished.

## Your First Calculator API

With your environment ready, install dependencies and configure the project structure to build a dynamic calculator API using Tiferet Fast.

### Installing Tiferet Fast

In your activated virtual environment, install the Tiferet Fast extension using pip:

```bash
# Windows
pip install tiferet_fast

# macOS/Linux
pip3 install tiferet_fast
```

Note: If developing locally, replace with the appropriate local installation command.

### Project Structure

Adapt Tiferet’s project structure to incorporate FastAPI, adding a dedicated API script:

```plaintext
project_root/
├── basic_calc.py
├── calc_cli.py
├── calc_fast_api.py
├── app/
    ├── commands/
    │   ├── __init__.py
    │   ├── calc.py
    │   └── settings.py
    └── configs/
        ├── __init__.py
        ├── app.yml
        ├── container.yml
        ├── error.yml
        ├── feature.yml
        ├── fast.yml
        └── logging.yml
```

The `app/commands/` and `app/configs/` directories align with Tiferet’s structure (see [Tiferet README](https://github.com/greatstrength/tiferet?tab=readme-ov-file#project-structure)). The `calc_fast_api.py` script initializes and runs the FastAPI application, while `fast.yml` defines router and routing configurations.

## Crafting the Calculator API

Extend Tiferet’s calculator application into a powerful API by reusing its commands and configurations, enhanced with FastAPI-specific functionality.

### Defining Base and Arithmetic Command Classes

Leverage Tiferet’s `BasicCalcCommand` (`app/commands/settings.py`) for input validation and arithmetic commands (`AddNumber`, `SubtractNumber`, `MultiplyNumber`, `DivideNumber`, `ExponentiateNumber` in `app/commands/calc.py`) for core operations. These remain unchanged from the original calculator app; refer to the [Tiferet README](https://github.com/greatstrength/tiferet?tab=readme-ov-file#defining-base-and-arithmetic-command-classes) for details.

### Configuring the Calculator API

Reuse Tiferet’s `container.yml` ([here](https://github.com/greatstrength/tiferet?tab=readme-ov-file#configuring-the-container-in-configscontaineryml)), `error.yml` ([here](https://github.com/greatstrength/tiferet?tab=readme-ov-file#configuring-the-errors-in-configserroryml)), and `feature.yml` ([here](https://github.com/greatstrength/tiferet?tab=readme-ov-file#configuring-the-features-in-configsfeatureyml)) for command mappings, error handling, and feature workflows. Introduce a FastAPI-specific interface in `app.yml` and routing configurations in `fast.yml`.

#### Configuring the App Interface in `configs/app.yml`

Enhance `app/configs/app.yml` with the `calc_fast_api` interface:

```yaml
interfaces:
  calc_fast_api:
    name: Basic Calculator API
    description: Perform basic calculator operations via FastAPI
    module_path: tiferet_fast.contexts.fast
    class_name: FastApiContext
    attrs:
      fast_api_handler:
        module_path: tiferet_fast.handlers.fast
        class_name: FastApiHandler
      fast_repo:
        module_path: tiferet_fast.proxies.yaml.fast
        class_name: FastYamlProxy
        params:
          fast_config_file: app/configs/fast.yml
```

#### Configuring Routers, Routes, and Error Status Codes in `configs/fast.yml`

Define FastAPI routers, routes, and error mappings in `app/configs/fast.yml`:

```yaml
fast:
  routers:
    calc:
      name: calc
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
        multiply:
          path: /multiply
          methods: [POST, GET]
          status_code: 200
        divide:
          path: /divide
          methods: [POST, GET]
          status_code: 200
        sqrt:
          path: /sqrt
          methods: [POST, GET]
          status_code: 200
  errors:
    DIVIDE_BY_ZERO: 400
```

The `prefix` ensures all routes are prefixed with `/calc`. Each route’s endpoint (e.g., `calc.add`) aligns with the corresponding feature ID in `feature.yml`. Routes specify a `path`, supported HTTP `methods`, and a default `status_code` of 200. The `errors` section maps error codes from `error.yml` to HTTP status codes, ensuring proper error handling.

This configuration enables `FastApiContext` to orchestrate FastAPI operations seamlessly.

### Initializing and Demonstrating the API in `calc_fast_api.py`

Create `calc_fast_api.py` to initialize the API and define endpoints:

```python
"""Tiferet Fast Calculator Initialization Script"""

# *** imports

# ** infra
from tiferet import App
from tiferet_fast.contexts.fast import FastApiContext
from starlette.requests import Request
from starlette.responses import JSONResponse
import uvicorn

# *** functions

# * function: view_func
async def view_func(request: Request):
    '''
    Call the view function whenever a route endpoint is invoked.

    :param context: The Fast API context.
    :type context: FastApiContext
    :param kwargs: Additional keyword arguments.
    :type kwargs: dict
    :return: The result of the view function.
    :rtype: Any
    '''

    data = await request.json() if request.headers.get('content-type') == 'application/json' else {}
    data.update(dict(request.query_params))
    data.update(dict(request.path_params))

    # Format header data from the request headers.
    headers = dict(request.headers)

    # Execute the feature from the request endpoint.
    response, status_code = context.run(
        feature_id=request.scope['route'].name,
        headers=headers,
        data=data,
    )

    # Return the response.
    return JSONResponse(response, status_code=status_code)

# *** exec

# Create the Fast API context.
context: FastApiContext = App().load_interface('calc_fast_api')

# Build the FastAPI app.
context.build_fast_app(view_func=view_func)

# Define the fast_app for external use (e.g., for FastAPI CLI or ASGI servers).
def fast_app():
    '''
    Create and return the FastAPI app for testing.

    :return: The FastAPI app.
    :rtype: FastAPI
    '''

    return context.fast_app

# Run the FastAPI app if this script is executed directly.
if __name__ == '__main__':
    uvicorn.run(context.fast_app, host='127.0.0.1', port=8000)
```

This script initializes the Tiferet application, loads the `calc_fast_api` interface, and dynamically handles RESTful endpoints for arithmetic operations using FastAPI’s asynchronous routing.

### Demonstrating the Calculator API

Launch the API:

```bash
python3 calc_fast_api.py
```

Test endpoints using curl or tools like Postman:

```bash
# Add two numbers
curl -X POST http://127.0.0.1:8000/calc/add -H "Content-Type: application/json" -d '{"a": 1, "b": 2}'
# Output: 3

# Calculate square root
curl -X POST http://127.0.0.1:8000/calc/sqrt -H "Content-Type: application/json" -d '{"a": 16}'
# Output: 4.0

# Division by zero
curl -X POST http://127.0.0.1:8000/calc/divide -H "Content-Type: application/json" -d '{"a": 5, "b": 0}'
# Output: {"error_code": "DIVIDE_BY_ZERO", "text": "Cannot divide by zero"}
```

## Conclusion

Tiferet Fast empowers developers to craft high-performance, asynchronous FastAPI applications within Tiferet’s DDD framework, as demonstrated in this calculator tutorial. By reusing Tiferet’s commands and configurations and introducing a FastAPI interface, you’ve built a scalable, intuitive API with minimal effort. Expand its capabilities by integrating authentication, advanced features like trigonometric operations, or combining with Tiferet’s CLI or TUI contexts. Explore the [Tiferet documentation](https://github.com/greatstrength/tiferet) for advanced DDD techniques, and experiment with `app/configs/` to customize your API, transforming complex web applications into clear, purposeful solutions.