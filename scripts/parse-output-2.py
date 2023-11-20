import re
import sys
from utils import Car, Sensor, StreetLamp, Outline
from pathlib import Path
import argparse

# Check if rich is installed, and only import it if it is.
try:
    from rich import pretty, print

    pretty.install()
except ImportError or ModuleNotFoundError:
    pass

# Parsing the arguments
# -f --file: The path to the file to be parsed
parser = argparse.ArgumentParser(description='Parse the VDM output file.')
parser.add_argument('-f', '--file', type=str, required=True, help='The path to the file to be parsed')

args = parser.parse_args()

if not args.file:
    parser.print_help()
    sys.exit(1)

file = Path(args.file).resolve()
if not file.exists():
    print(f"File {file} does not exist.")
    sys.exit(1)


# Adjusted parsing function to skip recursive elements and focus on simpler elements
def parse_vdm_output_adjusted(file_path):
    """
    Parse the VDM output from the given file path.

    Parameters:
        file_path (str): The path to the file to be parsed.

    Returns:
        Outline: An Outline object containing the parsed data.
    
    Raises:
        FileNotFoundError: If the file could not be found.
    """
    with open(file_path, 'r') as file:
        content = file.read()

    # Adjusting the regex patterns to match simpler, non-recursive structures
    # Skipping the road details in sensors
    # car_pattern = re.compile(r"Car\{[^}]*direction:=(-?\d+), progress:=(\d+(\.\d+)?), velocity=(\d+(\.\d+)?), road_id:=(\d+)[^}]*\}")
    car_pattern = re.compile(r"Car\{[^}]*direction:=(-?\d+), progress:=(\d+(\.\d+)?), velocity=(\d+(\.\d+)?), road_id:=(\d+)[^}]*\}")
    sensor_pattern = re.compile(r"Sensor\{[^}]*road:=\{[^}]*\}, position:=(\d+(\.\d+)?), cars:=\{[^}]*\}, range=(\d+(\.\d+)?), road_id:=(\d+)[^}]*\}")
    street_lamp_pattern = re.compile(r"StreetLamp.*?position:=(\d+).*?road_id:=(\d+).*?GLOBAL.*?lamp_state:=(<(OFF|ON)>)")

    # Parsing cars
    cars = set()
    for match in car_pattern.finditer(content):
        direction, progress, _, velocity, _, road_id = match.groups()
        car = Car(road_id, float(progress), int(direction), float(velocity))
        cars.add(car)

    # # Parsing sensors
    sensors = {}
    for match in sensor_pattern.finditer(content):
        position, _, cars_str, _, road_id = match.groups()
        car_ids = cars_str.split(", ")
        sensor_cars = {car for car in cars if car.road_id in car_ids}
        sensor = Sensor(road_id, float(position), sensor_cars)
        sensors[road_id] = sensor

    # Parsing street lamps
    street_lamps = set()
    for match in street_lamp_pattern.finditer(content):
        position, _, road_id, lamp_state = match.groups()
        # Using the first sensor found for the given road_id as an example
        sensor = sensors.get(road_id, None)
        street_lamp = StreetLamp(lamp_state, sensor, road_id, float(position))
        street_lamps.add(street_lamp)

    # Assuming the time is at the start of the file in the format 'Time: [value]'
    time_match = re.search(r"Time: (\d+(\.\d+)?)", content)
    time = float(time_match.group(1)) if time_match else 0

    return Outline(time, cars, street_lamps)

# Parse the file with adjusted logic
parsed_outline_adjusted = parse_vdm_output_adjusted(file)
print(parsed_outline_adjusted)

