"""Tests for Fast API Data Transfer Objects."""

# *** imports

# ** infra
import pytest

# ** app
from ...data import (
    DataObject,
    FastRouteYamlData,
    FastRouterYamlData
)
from ...models.fast import (
    FastRoute,
    FastRouter
)

# *** fixtures

# ** fixture: fast_route_yaml_data
@pytest.fixture
def fast_route_yaml_data():
    '''
    Fixture to create a FastRouteYamlData instance.
    '''

    # Create a FastRouteYamlData instance.
    return DataObject.from_data(
        FastRouteYamlData,
        endpoint='calc.add',
        path='/calc/add',
        methods=['GET', 'POST'],
        status_code=200
    )

# ** fixture: fast_router_yaml_data
@pytest.fixture
def fast_router_yaml_data(fast_route_yaml_data):
    '''
    Fixture to create a FastRouterYamlData instance.
    '''

    # Create a FastRouterYamlData instance.
    return DataObject.from_data(
        FastRouterYamlData,
        name='calc',
        prefix='/calc',
        routes={'calc.add': fast_route_yaml_data}
    )

# *** tests

# ** test: fast_route_yaml_data_from_data
def test_fast_route_yaml_data_from_data(fast_route_yaml_data):
    '''
    Test the creation of FastRouteYamlData from a dictionary.
    '''

    # Assert the DTO is an instance of FastRouteYamlData.
    assert isinstance(fast_route_yaml_data, FastRouteYamlData)

    # Assert the attributes are correctly set.
    assert fast_route_yaml_data.endpoint == 'calc.add'
    assert fast_route_yaml_data.path == '/calc/add'
    assert fast_route_yaml_data.methods == ['GET', 'POST']
    assert fast_route_yaml_data.status_code == 200

# ** test: fast_route_yaml_data_map
def test_fast_route_yaml_data_map(fast_route_yaml_data):
    '''
    Test mapping FastRouteYamlData to a FastRoute instance.
    '''

    # Map the YAML data to a FastRoute object.
    fast_route = fast_route_yaml_data.map(endpoint='calc.add')

    # Assert the mapped object is valid.
    assert isinstance(fast_route, FastRoute)
    assert fast_route.endpoint == 'calc.add'
    assert fast_route.path == '/calc/add'
    assert fast_route.methods == ['GET', 'POST']
    assert fast_route.status_code == 200

# ** test: fast_router_yaml_data_from_data
def test_fast_router_yaml_data_from_data(fast_router_yaml_data):
    '''
    Test the creation of FastRouterYamlData from a dictionary.
    '''

    # Assert the DTO is an instance of FastRouterYamlData.
    assert isinstance(fast_router_yaml_data, FastRouterYamlData)

    # Assert the attributes are correctly set.
    assert fast_router_yaml_data.name == 'calc'
    assert fast_router_yaml_data.prefix == '/calc'
    assert len(fast_router_yaml_data.routes) == 1
    assert fast_router_yaml_data.routes['calc.add'].endpoint == 'calc.add'

# ** test: fast_router_yaml_data_map
def test_fast_router_yaml_data_map(fast_router_yaml_data):
    '''
    Test mapping FastRouterYamlData to a FastRouter instance.
    '''

    # Map the YAML data to a FastRouter object.
    fast_router = fast_router_yaml_data.map()

    # Assert the mapped object is valid.
    assert isinstance(fast_router, FastRouter)
    assert fast_router.name == 'calc'
    assert fast_router.prefix == '/calc'
    assert len(fast_router.routes) == 1
    assert fast_router.routes[0].endpoint == 'calc.add'
