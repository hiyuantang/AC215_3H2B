import argparse
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import random 

def get_lat_long(location_name):
    geolocator = Nominatim(user_agent="location-finder")
    location = geolocator.geocode(location_name)
    if location:
        return (location.latitude, location.longitude)
    else:
        print(f"Could not find coordinates for {location_name}")
        return None

def calculate_distance(coord1, coord2):
    return geodesic(coord1, coord2).kilometers

# Greedy
def find_shortest_path(locations):
    if len(locations) <= 1:
        return locations

    first_location = random.choice(locations)
    path = [first_location]
    locations.remove(first_location)

    while locations:
        last_location = path[-1]
        next_location = min(locations, key=lambda loc: calculate_distance(last_location, loc))
        path.append(next_location)
        locations.remove(next_location)

    return path

def main():
    parser = argparse.ArgumentParser(description="Get lat/long for locations and optimize routes")
    parser.add_argument('locations', type=str, nargs='+', help='Location names')
    args = parser.parse_args()

    location_coords = []
    for loc_name in args.locations:
        coords = get_lat_long(loc_name)
        if coords:
            location_coords.append((loc_name, coords))

    if len(location_coords) < 2:
        print("Please provide at least two locations...")
        return
    
    print("\nLocations ordered by the shortest distance:")
    locations_to_visit = [coord for _, coord in location_coords]
    ordered_coords = find_shortest_path(locations_to_visit)

    for coord in ordered_coords:
        loc_name = next(name for name, loc in location_coords if loc == coord)
        print(f"{loc_name} -> {coord}")

if __name__ == "__main__":
    main()
