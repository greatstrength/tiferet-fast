"""Tests for Fast API YAML Configuration Proxy."""

# *** imports

# ** core
import yaml

# ** infra
import pytest

# ** app
from ....models.fast import (
    FastRoute,
    FastRouter
)
from ....proxies.yaml import FastYamlProxy

# *** fixtures

# ** fixture: fast_config_file
@pytest.fixture
def fast_config_file(tmp_path):
    '''
    Fixture to provide a temporary YAML configuration file for testing.
    '''

    # Create a temporary YAML file.
    config_file = tmp_path / 'fast.yml'
    config_data = {
        'fast': {
            'routers': {
                'calc': {
                    'prefix': '/calc',
                    'routes': {
                        'add': {
                            'path': '/add',
                            'methods': ['GET', 'POST'],
                            'status_code': 200
                        }
                    }
                }
            },
            'errors': {
                'INVALID_INPUT': 400
            }
        }
    }

    # Write the configuration to the file.
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)

    # Return the file path.
    return str(config_file)

# ** fixture: fast_yaml_proxy
@pytest.fixture
def fast_yaml_proxy(fast_config_file):
    '''
    Fixture to create a FastYamlProxy instance.
    '''

    # Create a FastYamlProxy instance.
    return FastYamlProxy(fast_config_file)

# *** tests

# ** test: fast_yaml_proxy_load_yaml
def test_fast_yaml_proxy_load_yaml(fast_yaml_proxy):
    '''
    Test loading the YAML configuration file.
    '''

    # Load the YAML file.
    data = fast_yaml_proxy.load_yaml()

    # Check the loaded data.
    assert data
    assert data.get('fast')
    assert data['fast'].get('routers')
    assert data['fast']['routers'].get('calc')

# ** test: fast_yaml_proxy_get_routers
def test_fast_yaml_proxy_get_routers(fast_yaml_proxy):
    '''
    Test retrieving all Fast API routers from the YAML configuration.
    '''

    # Get the routers.
    routers = fast_yaml_proxy.get_routers()

    # Check the routers.
    assert len(routers) == 1
    assert isinstance(routers[0], FastRouter)
    assert routers[0].name == 'calc'
    assert routers[0].prefix == '/calc'
    assert len(routers[0].routes) == 1
    assert routers[0].routes[0].endpoint == 'calc.add'

# ** test: fast_yaml_proxy_get_route
def test_fast_yaml_proxy_get_route(fast_yaml_proxy):
    '''
    Test retrieving a specific Fast API route from the YAML configuration.
    '''

    # Get the route.
    route = fast_yaml_proxy.get_route(route_id='add', router_name='calc')

    # Check the route.
    assert isinstance(route, FastRoute)
    assert route.id == 'add'
    assert route.endpoint == 'calc.add'
    assert route.path == '/add'
    assert route.methods == ['GET', 'POST']
    assert route.status_code == 200

# ** test: fast_yaml_proxy_get_status_code
def test_fast_yaml_proxy_get_status_code(fast_yaml_proxy):
    '''
    Test retrieving an HTTP status code for a given error code.
    '''

    # Get the status code.
    status_code = fast_yaml_proxy.get_status_code('INVALID_INPUT')

    # Check the status code.
    assert status_code == 400

# ** test: fast_yaml_proxy_get_status_code_default
def test_fast_yaml_proxy_get_status_code_default(fast_yaml_proxy):
    '''
    Test retrieving the default HTTP status code for an unknown error code.
    '''

    # Get the status code for an unknown error.
    status_code = fast_yaml_proxy.get_status_code('UNKNOWN_ERROR')

    # Check the default status code.
    assert status_code == 500