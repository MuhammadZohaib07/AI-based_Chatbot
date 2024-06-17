import pytest
from fastapi.testclient import TestClient
from main import app  # Make sure this import matches the filename where your FastAPI app is initialized

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(autouse=True)
def clear_session_data():
    from main import inprogress_orders
    inprogress_orders.clear()

def test_add_to_order(client, mocker):

    mock_insert_order_item = mocker.patch('main.db_helper.insert_order_item', return_value=1)
    mock_get_next_order_id = mocker.patch('main.db_helper.get_next_order_id', return_value=1)


    payload = {
        "queryResult": {
            "intent": {
                "displayName": "order.add - context: ongoing-order"
            },
            "parameters": {
                "food-item": ["cookie dough"],
                "number": ["2"]
            },
            "outputContexts": [{
                "name": "session123456789/context"
            }]
        }
    }


    response = client.post("/", json=payload)
    response_data = response.json()

    assert response.status_code == 200
    assert "cookie dough" in response_data['fulfillmentText']
    mock_insert_order_item.assert_not_called()
    mock_get_next_order_id.assert_not_called()
