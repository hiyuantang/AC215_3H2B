from api.utils.optimize_utils import (
    _calculate_distance,
    _get_lat_long,
    _find_shortest_path,
    _get_reranked_locations_perday,
    get_reranked_locations_all,
)


def test_get_lat_long_success():
    """
    Test the _get_lat_long function to ensure it returns a tuple of floats for a valid location.

    This test checks the following:
    - The first element of the response is a float.
    - The second element of the response is a float.
    - The response is a tuple.

    Returns:
        None
    """
    response = _get_lat_long("Beijing")
    assert isinstance(response[0], float)
    assert isinstance(response[1], float)
    assert isinstance(response, tuple)


def test_get_lat_long_fail():
    """
    Test case for the _get_lat_long function with an invalid input.

    This test verifies that the _get_lat_long function returns None when provided
    with an invalid address string.

    Assertions:
        - The response from _get_lat_long with an invalid address should be None.
    """
    response = _get_lat_long("xxxxxxxxxxxxxxxx")
    assert response is None


def test_calculate_distance_success():
    """
    Test the _calculate_distance function to ensure it returns a float when given two tuples representing coordinates.

    Test case:
    - Input: (2, 2), (1, 1)
    - Expected output: A float representing the distance between the two points.
    """
    response = _calculate_distance((2, 2), (1, 1))
    assert isinstance(response, float)


def test_find_shortest_path_one_location():
    """
    Test the _find_shortest_path function with a single location.

    This test case checks if the function correctly handles the scenario
    where only one location is provided. It verifies that the response
    is a list.

    Assertions:
        - The response should be an instance of list.
    """
    response = _find_shortest_path([(0, 0)])
    assert isinstance(response, list)


def test_find_shortest_path_two_locations():
    """
    Test the _find_shortest_path function with two locations.

    This test checks if the _find_shortest_path function correctly returns a list
    when given two locations as input.

    Tested input:
    - A list of two tuples representing coordinates: [(0, 0), (1, 1)]

    Expected behavior:
    - The function should return a list.

    Assertions:
    - The response should be an instance of the list class.
    """
    response = _find_shortest_path([(0, 0), (1, 1)])
    assert isinstance(response, list)


def test_get_reranked_locations_perday_onw_location():
    """
    Test the _get_reranked_locations_perday function with a single location.

    This test case checks the behavior of the _get_reranked_locations_perday function
    when provided with a list containing one location ("beijing"). It asserts that the
    response is None, indicating that the function should return None for this input.

    Returns:
        None
    """
    response = _get_reranked_locations_perday(["beijing"])
    assert response is None


def test_get_reranked_locations_perday_two_locations():
    """
    Test the _get_reranked_locations_perday function with two locations.

    This test verifies that the _get_reranked_locations_perday function returns
    two lists when provided with two location names ("beijing" and "shanghai").

    Assertions:
        - The first response is a list.
        - The second response is a list.
    """
    response_0, response_1 = _get_reranked_locations_perday(["beijing", "shanghai"])
    assert isinstance(response_0, list)
    assert isinstance(response_1, list)


INPUT_1 = {
    "chat_id": "973c833a-7aaa-45f1-ad03-5c96fb467488",
    "title": "2-Day Friends' Itinerary in Seoul for November",
    "dts": 1732164442,
    "messages": [
        {"city": "Seoul", "days": "1", "type": "friends", "month": "November"},
        {
            "message_id": "474ead7a-e955-4fee-ac4e-d2e9191bb977",
            "kind": "sf_response",
            "days_locations": {
                "1": [
                    "Gyeongbokgung Palace",
                ]
            },
            "days_themes": {
                "1": "Historical Charm and Urban Vibes",
            },
        },
    ],
}

INPUT_2 = {
    "chat_id": "973c833a-7aaa-45f1-ad03-5c96fb467488",
    "title": "2-Day Friends' Itinerary in Seoul for November",
    "dts": 1732164442,
    "messages": [
        {"city": "Seoul", "days": "1", "type": "friends", "month": "November"},
        {
            "message_id": "474ead7a-e955-4fee-ac4e-d2e9191bb977",
            "kind": "sf_response",
            "days_locations": {
                "1": [
                    "Gyeongbokgung Palace",
                    "Bukchon Hanok Village",
                ]
            },
            "days_themes": {
                "1": "Historical Charm and Urban Vibes",
            },
        },
    ],
}


def test_get_reranked_locations_all_fail():
    """
    Test case for the get_reranked_locations_all function when all inputs fail.

    This test verifies that the get_reranked_locations_all function returns
    two empty dictionaries when provided with a specific input that causes
    all locations to fail the reranking process.

    Expected Result:
    - The function should return a tuple of two empty dictionaries.

    Assertions:
    - Asserts that the response is equal to ({}, {}).
    """
    response = get_reranked_locations_all(INPUT_1)
    assert response == ({}, {})


def test_get_reranked_locations_all_success():
    """
    Test the `get_reranked_locations_all` function to ensure it returns two dictionaries.

    This test verifies that the `get_reranked_locations_all` function correctly processes
    the input and returns two dictionaries as expected.

    Assertions:
        - The first returned value is a dictionary.
        - The second returned value is a dictionary.
    """
    response_0, response_1 = get_reranked_locations_all(INPUT_2)
    assert isinstance(response_0, dict)
    assert isinstance(response_1, dict)
