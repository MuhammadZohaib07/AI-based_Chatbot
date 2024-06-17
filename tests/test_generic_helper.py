from generic_helper import get_str_from_food_dict, extract_session_id

def test_get_str_from_food_dict():
    food_dict = {"cake": 2, "cookie": 5}
    assert get_str_from_food_dict(food_dict) == "2 cake, 5 cookie"


def test_extract_session_id_found():
    session_str = "/sessions/12345/contexts/example_context"
    assert extract_session_id(session_str) == "12345"

def test_extract_session_id_not_found():
    session_str = "/no_session_here/contexts/missing_context"
    assert extract_session_id(session_str) == ""


