import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def mock_db(mocker):
    mocker.patch('main.db_helper.get_next_order_id', return_value=1)
    mocker.patch('main.db_helper.insert_order_item', return_value=1)
    mocker.patch('main.db_helper.insert_order_tracking')
    mocker.patch('main.db_helper.get_total_order_price', return_value=100)

def test_handle_new_order_intent(client, mock_db):
    response = client.post("/", json={
        "queryResult": {
            "intent": {"displayName": "new.order"},
            "parameters": {},
            "outputContexts": [{"name": "projects/project-id/agent/sessions/session-id/contexts/context-name"}]
        }
    })
    assert response.status_code == 200
    assert "Starting a new order" in response.json()['fulfillmentText']

def test_add_to_order_intent(client, mock_db):
    response = client.post("/", json={
        "queryResult": {
            "intent": {"displayName": "order.add - context: ongoing-order"},
            "parameters": {"food-item": ["cookie dough"], "number": [2]},
            "outputContexts": [{"name": "projects/project-id/agent/sessions/session-id/contexts/context-name"}]
        }
    })
    assert response.status_code == 200
    assert "So far you have: 2 cookie dough" in response.json()['fulfillmentText']

def test_remove_from_order_intent(client, mock_db):
    response = client.post("/", json={
        "queryResult": {
            "intent": {"displayName": "order.remove - context: ongoing-order"},
            "parameters": {"food-item": ["cookie dough"], "number": [1]},
            "outputContexts": [{"name": "projects/project-id/agent/sessions/session-id/contexts/context-name"}]
        }
    })
    assert response.status_code == 200
    assert "Removed" in response.json()['fulfillmentText']

def test_complete_order_intent(client, mock_db):
    response = client.post("/", json={
        "queryResult": {
            "intent": {"displayName": "order.complete - context: ongoing-order"},
            "parameters": {},
            "outputContexts": [{"name": "projects/project-id/agent/sessions/session-id/contexts/context-name"}]
        }
    })
    assert response.status_code == 200
    assert "Your order id is" in response.json()['fulfillmentText']

def test_track_order_intent(client, mock_db):
    response = client.post("/", json={
        "queryResult": {
            "intent": {"displayName": "track.order - context: ongoing-tracking"},
            "parameters": {"order_id": 40},
            "outputContexts": [{"name": "projects/project-id/agent/sessions/session-id/contexts/context-name"}]
        }
    })
    assert response.status_code == 200
    assert "The order status for order id: 40" in response.json()['fulfillmentText']
