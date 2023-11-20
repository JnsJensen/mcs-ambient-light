import re
import sys
filename = sys.argv[1]

# Read the file content
file_content = open(filename, 'r').read()

# Function to parse the content of the file
def parse_vdm_output(content):
    # Regular expressions for matching different objects
    car_pattern = r'Car\{[^}]*\}'
    street_lamp_pattern = r'StreetLamp\{[^}]*\}'
    sensor_pattern = r'Sensor\{[^}]*\}'

    # Parsing the content
    cars = re.findall(car_pattern, content)
    street_lamps = re.findall(street_lamp_pattern, content)
    sensors = re.findall(sensor_pattern, content)

    # Function to parse individual properties of an object
    def parse_properties(obj_str):
        properties = re.findall(r'(\w+):=([^,}]*)', obj_str)
        return {prop: val.strip() for prop, val in properties}

    # Parsing properties of cars, street lamps, and sensors
    parsed_cars = [parse_properties(car) for car in cars]
    parsed_street_lamps = [parse_properties(lamp) for lamp in street_lamps]
    parsed_sensors = [parse_properties(sensor) for sensor in sensors]

    return {
        'cars': parsed_cars,
        'street_lamps': parsed_street_lamps,
        'sensors': parsed_sensors
    }

# Parse the file content
parsed_data = parse_vdm_output(file_content)

# Display the parsed data
print("Cars:")
print(parsed_data['cars'][:5])
print("Street lamps:")
print(parsed_data['street_lamps'][:5])
print("Sensors:")
print(parsed_data['sensors'][:5])