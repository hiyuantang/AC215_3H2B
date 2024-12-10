from geopy.distance import geodesic
import random
import requests

def _get_lat_long(address):
    """
    Get the latitude and longitude for a given address using Google Maps Geocoding API.

    Args:
        address (str): The address or location name to geocode.
        api_key (str): Your Google Maps API key.

    Returns:
        tuple: A tuple containing the latitude and longitude of the location if found,
               otherwise None if the location could not be found.
    """
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": "AIzaSyBPKHWNSuhbQwuQmmCZiLZfHjl4NgfBnNU"
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            return (location['lat'], location['lng'])
        else:
            print(f"Error: {data['status']}")
            return None
    else:
        print(f"HTTP Error: {response.status_code}")
        return None


def _calculate_distance(coord1, coord2):
    """
    Calculate the geodesic distance between two coordinates.

    Args:
        coord1 (tuple): A tuple representing the first coordinate (latitude, longitude).
        coord2 (tuple): A tuple representing the second coordinate (latitude, longitude).

    Returns:
        float: The distance between the two coordinates in kilometers.
    """
    return geodesic(coord1, coord2).kilometers


# Greedy
def _find_shortest_path(locations):
    """
    Finds the shortest path visiting all given locations using a greedy algorithm.

    This function takes a list of locations and returns a path that visits each location
    exactly once, starting from a randomly chosen location and always moving to the
    nearest unvisited location.

    Args:
        locations (list): A list of locations where each location is represented by a coordinate or an object.

    Returns:
        list: A list of locations representing the shortest path found.
    """
    if len(locations) <= 1:
        return locations

    first_location = random.choice(locations)
    path = [first_location]
    locations.remove(first_location)

    while locations:
        last_location = path[-1]
        next_location = min(
            locations, key=lambda loc: _calculate_distance(last_location, loc)
        )
        path.append(next_location)
        locations.remove(next_location)

    return path


def _get_reranked_locations_perday(locations):
    """
    Re-ranks a list of location names based on the shortest path between them.
    This function takes a list of location names, retrieves their coordinates,
    and reorders them to minimize the travel distance between them. It returns
    the ordered list of location names and their corresponding coordinates.
    Args:
        locations (list of str): A list of location names to be re-ranked.
    Returns:
        tuple: A tuple containing two lists:
            - ordered_locations (list of str): The re-ranked list of location names.
            - ordered_coordinates (list of tuple): The coordinates of the re-ranked locations.
    Notes:
        - If fewer than two locations are provided, the function prints a message
          and returns None.
        - The function assumes the existence of helper functions `_get_lat_long`
          and `_find_shortest_path` to retrieve coordinates and compute the shortest path.
    """
    location_coords = []
    for loc_name in locations:
        coords = _get_lat_long(loc_name)
        if coords:
            location_coords.append((loc_name, coords))

    if len(location_coords) < 2:
        print("Please provide at least two locations...")
        return

    print("\nLocations ordered by the shortest distance:")
    locations_to_visit = [coord for _, coord in location_coords]
    ordered_coords = _find_shortest_path(locations_to_visit)

    ordered_locations = []
    ordered_coordinates = []
    for coord in ordered_coords:
        loc_name = next(name for name, loc in location_coords if loc == coord)
        ordered_locations.append(loc_name)
        ordered_coordinates.append(coord)

    return ordered_locations, ordered_coordinates


def get_reranked_locations_all(iti_first_draft):
    """
    Reranks locations for each day based on the initial itinerary draft.

    Args:
        iti_first_draft (dict): A dictionary containing the initial itinerary draft.
            The dictionary should have a "messages" key, where the first message contains
            the "city" and the second message contains "days_locations", a dictionary
            mapping each day to a list of location names.

    Returns:
        tuple: A tuple containing two dictionaries:
            - ordered_locations (dict): A dictionary mapping each day to a list of reranked location names.
            - ordered_coordinates (dict): A dictionary mapping each day to a list of coordinates for the reranked locations.

    Notes:
        - If reranking fails for a particular day due to insufficient locations, a message will be printed.
    """
    # Access the second message in the messages list
    second_message = iti_first_draft["messages"][1]
    city = iti_first_draft["messages"][0]["city"]

    # Retrieve the days_locations from the second message
    days_locations = second_message["days_locations"]

    # Initialize dictionaries to store ordered locations and coordinates per day
    ordered_locations = {}
    ordered_coordinates = {}

    # Iterate over each day and its locations
    for day, locations in days_locations.items():
        # Get the ordered locations and coordinates for the day
        locations = [loc + f",{city}" for loc in locations]
        result = _get_reranked_locations_perday(locations)
        if result:
            ordered_locs, ordered_coords = result
            ordered_locs = [loc.replace(f",{city}", "") for loc in ordered_locs]
            # Store the results in the dictionaries
            ordered_locations[day] = ordered_locs
            ordered_coordinates[day] = ordered_coords
        else:
            print(
                f"Unable to rerank locations for day {day} due to insufficient locations."
            )

    return ordered_locations, ordered_coordinates
