from api.utils.optimize_utils import (
    _calculate_distance,
    _get_lat_long,
    _find_shortest_path,
    _get_reranked_locations_perday,
    get_reranked_locations_all,
)


def test_get_lat_long_success():
    response = _get_lat_long("Beijing")
    assert isinstance(response[0], float)
    assert isinstance(response[1], float)
    assert isinstance(response, tuple)


def test_get_lat_long_fail():
    response = _get_lat_long("xxxxxxxxxxxxxxxx")
    assert response is None


def test_calculate_distance_success():
    response = _calculate_distance((2, 2), (1, 1))
    assert isinstance(response, float)


def test_find_shortest_path_one_location():
    response = _find_shortest_path([(0, 0)])
    assert isinstance(response, list)


def test_find_shortest_path_two_locations():
    response = _find_shortest_path([(0, 0), (1, 1)])
    assert isinstance(response, list)


def test_get_reranked_locations_perday_onw_location():
    response = _get_reranked_locations_perday(["beijing"])
    assert response is None


def test_get_reranked_locations_perday_two_locations():
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
    response = get_reranked_locations_all(INPUT_1)
    assert response == ({}, {})


def test_get_reranked_locations_all_success():
    response_0, response_1 = get_reranked_locations_all(INPUT_2)
    assert isinstance(response_0, dict)
    assert isinstance(response_1, dict)
