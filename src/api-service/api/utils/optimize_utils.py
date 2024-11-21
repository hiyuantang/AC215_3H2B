from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import random 

def _get_lat_long(location_name):
    geolocator = Nominatim(user_agent="location-finder")
    location = geolocator.geocode(location_name)
    if location:
        return (location.latitude, location.longitude)
    else:
        print(f"Could not find coordinates for {location_name}")
        return None

def _calculate_distance(coord1, coord2):
    return geodesic(coord1, coord2).kilometers

# Greedy
def _find_shortest_path(locations):
    if len(locations) <= 1:
        return locations

    first_location = random.choice(locations)
    path = [first_location]
    locations.remove(first_location)

    while locations:
        last_location = path[-1]
        next_location = min(locations, key=lambda loc: _calculate_distance(last_location, loc))
        path.append(next_location)
        locations.remove(next_location)

    return path

def _get_reranked_locations_perday(locations):
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
        locations = [loc+f",{city}" for loc in locations]
        result = _get_reranked_locations_perday(locations)
        if result:
            ordered_locs, ordered_coords = result
            ordered_locs = [loc.replace(f",{city}", '') for loc in ordered_locs]
            # Store the results in the dictionaries
            ordered_locations[day] = ordered_locs
            ordered_coordinates[day] = ordered_coords
        else:
            print(f"Unable to rerank locations for day {day} due to insufficient locations.")

    return ordered_locations, ordered_coordinates
