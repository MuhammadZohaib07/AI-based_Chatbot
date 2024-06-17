import pytest
import db_helper


@pytest.fixture
def mock_db_connection(mocker):
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mocker.patch('mysql.connector.connect', return_value=mock_conn)
    return mock_conn, mock_cursor

def test_insert_order_item_success(mock_db_connection):
    conn, cursor = mock_db_connection
    cursor.callproc.return_value = True
    cursor.rowcount = 1
    assert db_helper.insert_order_item('cake', 2, 1) == 1
    cursor.callproc.assert_called_once_with('insert_order_item', ('cake', 2, 1))
    conn.commit.assert_called_once()

def test_insert_order_item_failure(mock_db_connection):
    conn, cursor = mock_db_connection
    cursor.callproc.side_effect = Exception("DB Error")
    assert db_helper.insert_order_item('cake', 2, 1) == -1
    conn.rollback.assert_called_once()

def test_get_next_order_id(mock_db_connection):
    conn, cursor = mock_db_connection
    cursor.fetchone.return_value = [10]
    assert db_helper.get_next_order_id() == 10
    cursor.execute.assert_called_with("SELECT MAX(order_id) + 1 FROM orders")

def test_get_order_status(mock_db_connection):
    conn, cursor = mock_db_connection
    cursor.fetchone.return_value = ["In Progress"]
    assert db_helper.get_order_status(1) == "In Progress"
    cursor.execute.assert_called_with("SELECT status FROM order_tracking WHERE order_id = %s", (1,))

@pytest.mark.parametrize("order_id, expected_result", [
    (1, 50),
    (2, 0),
])
def test_get_total_order_price(mock_db_connection, order_id, expected_result):
    conn, cursor = mock_db_connection
    cursor.fetchone.return_value = [expected_result]
    assert db_helper.get_total_order_price(order_id) == expected_result
    cursor.execute.assert_called_with("SELECT SUM(total_price) FROM orders WHERE order_id = %s", (order_id,))
