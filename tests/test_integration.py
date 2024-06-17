import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    """Provides a test client for the FastAPI app."""
    return TestClient(app)

def test_complete_order_process(client):
    """
    Tests the completion of an order through the chatbot to ensure the system processes
    it correctly and returns the expected success message.
    """
    # Define a payload that mimics a typical user request to complete an order
    completion_payload = {
        "queryResult": {
            "intent": {"displayName": "order.complete - context: ongoing-order"},
            "parameters": {"order_details": "Complete this order"},
            "outputContexts": [{"name": "session123456789/context"}]
        }
    }


    response = client.post("/", json=completion_payload)


    assert response.status_code == 200, "Expecting HTTP 200 status code for successful order completion"


    response_data = response.json()
    assert "Your order id is" in response_data['fulfillmentText'], "Order completion message should confirm the order ID"
