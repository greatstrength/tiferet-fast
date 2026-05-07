"""Tests for Fast API Mappers."""

# *** imports

# ** infra
import pytest
from tiferet.assets import TiferetError

# ** app
from ...domain import FastRoute, FastRouter
from ..fast import (
    FastRouteAggregate,
    FastRouterAggregate,
    FastRouteYamlObject,
    FastRouterYamlObject,
)

# *** constants

# ** constant: route_sample_data
ROUTE_SAMPLE_DATA = dict(
    id='add',
    endpoint='calc.add',
    path='/add',
    methods=['GET', 'POST'],
    status_code=200,
)

# ** constant: router_sample_data
ROUTER_SAMPLE_DATA = dict(
    name='calc',
    prefix='/calc',
)

# ** constant: route_yaml_data
ROUTE_YAML_DATA = dict(
    path='/add',
    methods=['GET', 'POST'],
    status_code=200,
)

# ** constant: router_yaml_data
ROUTER_YAML_DATA = dict(
    name='calc',
    prefix='/calc',
    routes={
        'add': ROUTE_YAML_DATA,
    },
)

# *** fixtures

# ** fixture: route_aggregate
@pytest.fixture
def route_aggregate() -> FastRouteAggregate:
    '''
    A fixture that provides a sample FastRouteAggregate instance.

    :return: A sample FastRouteAggregate instance.
    :rtype: FastRouteAggregate
    '''

    return FastRouteAggregate(**ROUTE_SAMPLE_DATA)

# ** fixture: router_aggregate
@pytest.fixture
def router_aggregate(route_aggregate: FastRouteAggregate) -> FastRouterAggregate:
    '''
    A fixture that provides a sample FastRouterAggregate instance.

    :param route_aggregate: A sample FastRouteAggregate instance.
    :type route_aggregate: FastRouteAggregate
    :return: A sample FastRouterAggregate instance.
    :rtype: FastRouterAggregate
    '''

    return FastRouterAggregate(
        **ROUTER_SAMPLE_DATA,
        routes=[route_aggregate],
    )

# *** tests

# ** test: route_aggregate_creation
def test_route_aggregate_creation(route_aggregate: FastRouteAggregate):
    '''
    Test the creation of a FastRouteAggregate instance.

    :param route_aggregate: A sample FastRouteAggregate instance.
    :type route_aggregate: FastRouteAggregate
    '''

    assert route_aggregate.id == 'add'
    assert route_aggregate.endpoint == 'calc.add'
    assert route_aggregate.path == '/add'
    assert route_aggregate.methods == ['GET', 'POST']
    assert route_aggregate.status_code == 200

# ** test: route_aggregate_set_attribute
def test_route_aggregate_set_attribute(route_aggregate: FastRouteAggregate):
    '''
    Test setting a valid attribute on FastRouteAggregate.

    :param route_aggregate: A sample FastRouteAggregate instance.
    :type route_aggregate: FastRouteAggregate
    '''

    route_aggregate.set_attribute('path', '/add-numbers')
    assert route_aggregate.path == '/add-numbers'

# ** test: route_aggregate_set_attribute_invalid
def test_route_aggregate_set_attribute_invalid(route_aggregate: FastRouteAggregate):
    '''
    Test setting an invalid attribute raises TiferetError.

    :param route_aggregate: A sample FastRouteAggregate instance.
    :type route_aggregate: FastRouteAggregate
    '''

    with pytest.raises(TiferetError):
        route_aggregate.set_attribute('invalid_attr', 'value')

# ** test: router_aggregate_creation
def test_router_aggregate_creation(router_aggregate: FastRouterAggregate):
    '''
    Test the creation of a FastRouterAggregate instance.

    :param router_aggregate: A sample FastRouterAggregate instance.
    :type router_aggregate: FastRouterAggregate
    '''

    assert router_aggregate.name == 'calc'
    assert router_aggregate.prefix == '/calc'
    assert len(router_aggregate.routes) == 1
    assert router_aggregate.routes[0].id == 'add'

# ** test: router_aggregate_add_route
def test_router_aggregate_add_route(router_aggregate: FastRouterAggregate):
    '''
    Test adding a route to a FastRouterAggregate.

    :param router_aggregate: A sample FastRouterAggregate instance.
    :type router_aggregate: FastRouterAggregate
    '''

    new_route = router_aggregate.add_route(
        endpoint='subtract',
        path='/subtract',
        methods=['POST'],
        status_code=200,
    )

    assert len(router_aggregate.routes) == 2
    assert new_route.id == 'subtract'
    assert new_route.endpoint == 'calc.subtract'
    assert new_route.path == '/subtract'
    assert new_route.methods == ['POST']

# ** test: route_yaml_object_map
def test_route_yaml_object_map():
    '''
    Test mapping a FastRouteYamlObject to a FastRouteAggregate.
    '''

    yaml_obj = FastRouteYamlObject.model_validate(ROUTE_YAML_DATA)
    aggregate = yaml_obj.map(id='add', endpoint='calc.add')

    assert isinstance(aggregate, FastRouteAggregate)
    assert aggregate.id == 'add'
    assert aggregate.endpoint == 'calc.add'
    assert aggregate.path == '/add'
    assert aggregate.methods == ['GET', 'POST']
    assert aggregate.status_code == 200

# ** test: route_yaml_object_from_model
def test_route_yaml_object_from_model(route_aggregate: FastRouteAggregate):
    '''
    Test creating a FastRouteYamlObject from a FastRouteAggregate.

    :param route_aggregate: A sample FastRouteAggregate instance.
    :type route_aggregate: FastRouteAggregate
    '''

    yaml_obj = FastRouteYamlObject.from_model(route_aggregate)

    assert isinstance(yaml_obj, FastRouteYamlObject)
    assert yaml_obj.path == '/add'
    assert yaml_obj.methods == ['GET', 'POST']
    assert yaml_obj.status_code == 200

# ** test: router_yaml_object_map
def test_router_yaml_object_map():
    '''
    Test mapping a FastRouterYamlObject to a FastRouterAggregate.
    '''

    yaml_obj = FastRouterYamlObject.model_validate(ROUTER_YAML_DATA)
    aggregate = yaml_obj.map()

    assert isinstance(aggregate, FastRouterAggregate)
    assert aggregate.name == 'calc'
    assert aggregate.prefix == '/calc'
    assert len(aggregate.routes) == 1
    assert aggregate.routes[0].id == 'add'
    assert aggregate.routes[0].endpoint == 'calc.add'

# ** test: router_yaml_object_from_model
def test_router_yaml_object_from_model(router_aggregate: FastRouterAggregate):
    '''
    Test creating a FastRouterYamlObject from a FastRouterAggregate.

    :param router_aggregate: A sample FastRouterAggregate instance.
    :type router_aggregate: FastRouterAggregate
    '''

    yaml_obj = FastRouterYamlObject.from_model(router_aggregate)

    assert isinstance(yaml_obj, FastRouterYamlObject)
    assert yaml_obj.name == 'calc'
    assert yaml_obj.prefix == '/calc'
    assert len(yaml_obj.routes) == 1
    assert 'add' in yaml_obj.routes
    assert isinstance(yaml_obj.routes['add'], FastRouteYamlObject)

# ** test: router_yaml_object_round_trip
def test_router_yaml_object_round_trip(router_aggregate: FastRouterAggregate):
    '''
    Test round-trip: aggregate → YAML object → aggregate preserves data.

    :param router_aggregate: A sample FastRouterAggregate instance.
    :type router_aggregate: FastRouterAggregate
    '''

    # Aggregate → YAML object.
    yaml_obj = FastRouterYamlObject.from_model(router_aggregate)

    # YAML object → aggregate.
    result = yaml_obj.map()

    assert isinstance(result, FastRouterAggregate)
    assert result.name == router_aggregate.name
    assert result.prefix == router_aggregate.prefix
    assert len(result.routes) == len(router_aggregate.routes)
    assert result.routes[0].id == router_aggregate.routes[0].id
    assert result.routes[0].endpoint == router_aggregate.routes[0].endpoint
    assert result.routes[0].path == router_aggregate.routes[0].path
    assert result.routes[0].methods == router_aggregate.routes[0].methods
    assert result.routes[0].status_code == router_aggregate.routes[0].status_code
