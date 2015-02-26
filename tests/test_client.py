import pytest

from rabbitman import Client


@pytest.fixture
def client():
    return Client('http://localhost:15672', 'guest', 'guest')


def test_get_overview(client):
    overview = client.get_overview()
    assert overview['node'] == 'rabbit@localhost'
    assert 'management_version' in overview
    assert 'erlang_version' in overview
    assert 'rabbitmq_version' in overview


def test_get_cluster_name(client):
    # cluster_name = client.get_cluster_name()
    pass  # need newer rabbit


def test_create_cluster_name(client):
    pass


def test_get_nodes(client):
    nodes = client.get_nodes()
    assert len(nodes) > 0
    node = nodes[0]
    assert node['running']
    assert node['name'] == 'rabbit@localhost'
    assert 'disk_free' in node
    assert 'sockets_used' in node
    assert 'os_pid' in node
    assert 'uptime' in node


def test_get_nodes_by_name(client):
    node = client.get_nodes_by_name('rabbit@localhost')
    assert node['name'] == 'rabbit@localhost'
    assert 'disk_free' in node
    assert 'sockets_used' in node
    assert 'os_pid' in node
    assert 'uptime' in node


def test_get_extensions(client):
    extensions = client.get_extensions()
    assert extensions

def test_get_definitions(client):
    pass

def test_get_connections(client):
    pass

def test_get_connections_by_name(client):
    pass

def test_delete_connections_by_name(client):
    pass

def test_get_connections_channels_by_name(client):
    pass

def test_get_channels(client):
    pass

def test_get_channels_by_channel(client):
    pass

def test_get_consumers(client):
    pass

def test_get_consumers_by_vhost(client):
    pass

def test_get_exchanges(client):
    pass

def test_get_exchanges_by_vhost(client):
    pass

def test_get_exchanges_by_vhost_and_name(client):
    pass

def test_create_exchanges_by_vhost_and_name(client):
    pass

def test_delete_exchanges_by_vhost_and_name(client):
    pass

def test_get_exchanges_bindings_source_by_vhost_and_name(client):
    pass

def test_get_exchanges_bindings_destination_by_vhost_and_name(client):
    pass

def test_get_queues(client):
    pass

def test_get_queues_by_vhost(client):
    pass

def test_get_queues_by_vhost_and_name(client):
    pass

def test_create_queues_by_vhost_and_name(client):
    pass

def test_delete_queues_by_vhost_and_name(client):
    pass

def test_get_queues_bindings_by_vhost_and_name(client):
    pass

def test_delete_queues_contents_by_vhost_and_name(client):
    pass

def test_get_bindings(client):
    pass

def test_get_bindings_by_vhost(client):
    pass

def test_get_bindings_by_vhost_and_exchange_and_queue(client):
    pass

def test_get_bindings_by_vhost_and_exchange_and_queue_and_props(client):
    pass

def test_delete_bindings_by_vhost_and_exchange_and_queue_and_props(client):
    pass

def test_get_bindings_by_vhost_and_source_and_destination(client):
    pass

def test_get_bindings_by_vhost_and_source_and_destination_and_props(client):
    pass

def test_delete_bindings_by_vhost_and_source_and_destination_and_props(client):
    pass

def test_get_vhosts(client):
    pass

def test_get_vhosts_by_name(client):
    pass

def test_create_vhosts_by_name(client):
    pass

def test_delete_vhosts_by_name(client):
    pass

def test_get_vhosts_permissions_by_name(client):
    pass

def test_get_users(client):
    pass

def test_get_users_by_name(client):
    pass

def test_create_users_by_name(client):
    pass

def test_delete_users_by_name(client):
    pass

def test_get_users_permissions_by_user(client):
    pass

def test_get_whoami(client):
    pass

def test_get_permissions(client):
    pass

def test_get_permissions_by_vhost_and_user(client):
    pass

def test_create_permissions_by_vhost_and_user(client):
    pass

def test_delete_permissions_by_vhost_and_user(client):
    pass

def test_get_parameters(client):
    pass

def test_get_parameters_by_component(client):
    pass

def test_get_parameters_by_component_and_vhost(client):
    pass

def test_get_parameters_by_component_and_vhost_and_name(client):
    pass

def test_create_parameters_by_component_and_vhost_and_name(client):
    pass

def test_delete_parameters_by_component_and_vhost_and_name(client):
    pass

def test_get_policies(client):
    pass

def test_get_policies_by_vhost(client):
    pass

def test_get_policies_by_vhost_and_name(client):
    pass

def test_create_policies_by_vhost_and_name(client):
    pass

def test_delete_policies_by_vhost_and_name(client):
    pass

def test_get_aliveness_test_by_vhost(client):
    pass

