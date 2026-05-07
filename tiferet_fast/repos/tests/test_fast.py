"""Tests for Fast API YAML Repository."""

# *** imports

# ** core
import yaml

# ** infra
import pytest

# ** app
from ...domain import FastRoute, FastRouter
from ...repos import FastYamlRepository

# *** constants

# ** constant: sample_yaml_data
SAMPLE_YAML_DATA = {
    'fast': {
        'routers': {
            'calc': {
                'prefix': '/calc',
                'routes': {
                    'add': {
                        'path': '/add',
                        'methods': ['GET', 'POST'],
                        'status_code': 200,
                    },
                    'subtract': {
                        'path': '/subtract',
                        'methods': ['GET'],
                        'status_code': 200,
                    },
                },
            },
        },
        'errors': {
            'INVALID_INPUT': 400,
            'DIVISION_BY_ZERO': 422,
        },
    },
}

# *** fixtures

# ** fixture: fast_yaml_file
@pytest.fixture
def fast_yaml_file(tmp_path) -> str:
    '''
    Fixture to provide a temporary YAML configuration file for testing.

    :param tmp_path: The temporary directory path provided by pytest.
    :type tmp_path: pathlib.Path
    :return: The path to the temporary YAML file.
    :rtype: str
    '''

    # Create a temporary YAML file.
    config_file = tmp_path / 'fast.yml'

    # Write the sample configuration to the file.
    with open(config_file, 'w') as f:
        yaml.dump(SAMPLE_YAML_DATA, f)

    # Return the file path.
    return str(config_file)

# ** fixture: repo
@pytest.fixture
def repo(fast_yaml_file) -> FastYamlRepository:
    '''
    Fixture to create a FastYamlRepository instance.

    :param fast_yaml_file: The path to the temporary YAML file.
    :type fast_yaml_file: str
    :return: A FastYamlRepository instance.
    :rtype: FastYamlRepository
    '''

    # Create and return the repository instance.
    return FastYamlRepository(fast_yaml_file=fast_yaml_file)

# *** tests

# ** test: get_routers
def test_get_routers(repo: FastYamlRepository) -> None:
    '''
    Test retrieving all Fast API routers from the YAML configuration.

    :param repo: The FastYamlRepository instance.
    :type repo: FastYamlRepository
    '''

    # Get the routers.
    routers = repo.get_routers()

    # Assert the routers are loaded correctly.
    assert len(routers) == 1
    assert isinstance(routers[0], FastRouter)
    assert routers[0].name == 'calc'
    assert routers[0].prefix == '/calc'
    assert len(routers[0].routes) == 2

    # Assert the routes are mapped correctly.
    route_ids = [route.id for route in routers[0].routes]
    assert 'add' in route_ids
    assert 'subtract' in route_ids

# ** test: get_route
def test_get_route(repo: FastYamlRepository) -> None:
    '''
    Test retrieving a specific Fast API route from the YAML configuration.

    :param repo: The FastYamlRepository instance.
    :type repo: FastYamlRepository
    '''

    # Get the route.
    route = repo.get_route(route_id='add', router_name='calc')

    # Assert the route is loaded correctly.
    assert isinstance(route, FastRoute)
    assert route.id == 'add'
    assert route.endpoint == 'calc.add'
    assert route.path == '/add'
    assert route.methods == ['GET', 'POST']
    assert route.status_code == 200

# ** test: get_route_not_found
def test_get_route_not_found(repo: FastYamlRepository) -> None:
    '''
    Test retrieving a non-existent route returns None.

    :param repo: The FastYamlRepository instance.
    :type repo: FastYamlRepository
    '''

    # Get a non-existent route.
    route = repo.get_route(route_id='unknown', router_name='calc')

    # Assert the result is None.
    assert route is None

# ** test: get_status_code
def test_get_status_code(repo: FastYamlRepository) -> None:
    '''
    Test retrieving an HTTP status code for a given error code.

    :param repo: The FastYamlRepository instance.
    :type repo: FastYamlRepository
    '''

    # Get the status code.
    status_code = repo.get_status_code('INVALID_INPUT')

    # Assert the status code is correct.
    assert status_code == 400

# ** test: get_status_code_default
def test_get_status_code_default(repo: FastYamlRepository) -> None:
    '''
    Test retrieving the default HTTP status code for an unknown error code.

    :param repo: The FastYamlRepository instance.
    :type repo: FastYamlRepository
    '''

    # Get the status code for an unknown error.
    status_code = repo.get_status_code('UNKNOWN_ERROR')

    # Assert the default status code is returned.
    assert status_code == 500
