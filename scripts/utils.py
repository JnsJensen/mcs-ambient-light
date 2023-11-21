import re

class Car:
    def __init__(self, road_id, progress=0, direction=1):
        self.road_id = road_id
        self.progress = progress
        self.direction = direction
        assert direction in {-1, 1}, "Invalid direction value"

    def __repr__(self):
        return f"Car(road_id={self.road_id}, progress={self.progress}, direction={self.direction})"

class Sensor:
    RANGE = 10.0

    def __init__(self, road_id, position, cars=None):
        self.cars = cars if cars is not None else set()
        self.road_id = road_id
        self.position = position

    def __repr__(self):
        return f"Sensor(road_id={self.road_id}, position={self.position}, cars={self.cars})"

class StreetLamp:
    def __init__(self, lamp_state, road_id, position):
        self.lamp_state = lamp_state
        self.road_id = road_id
        self.position = position

    def __repr__(self):
        return f"StreetLamp(lamp_state={self.lamp_state}, road_id={self.road_id}, position={self.position})"

class Outline:
    def __init__(self, time, cars, street_lamps):
        self.time = time
        self.cars = set(cars)
        self.street_lamps = set(street_lamps)

    def __repr__(self):
        return f"Outline(time={self.time}, cars={self.cars}, street_lamps={self.street_lamps})"

def parse_vdm_city(content):
    """
    Parse the VDMSL city data to extract intersections and roads.

    Args:
    content (str): The content of the VDMSL file.

    Returns:
    tuple: A tuple containing two lists, one for intersections and one for roads.
    """
    intersections = []
    roads = []

    lines = content.splitlines()
    for line in lines:
        if "new Position" in line:
            parts = line.split('(')[1].split(')')[0].split(',')
            x, y = float(parts[0].strip()), float(parts[1].strip())
            intersections.append((int(x), int(y)))
        elif "mk_Edge" in line:
            parts = line.split('(')[1].split(')')[0].split(',')
            start, end = int(parts[0].strip()), int(parts[1].strip())
            roads.append((start, end))

    return intersections, roads

def parse_vdm_output(output: str):

    outline_pattern = re.compile(r"(mk_\(.*?\))")

    # splitting for each outline
    outlines = outline_pattern.findall(output)

    outlines = [parse_vdm_outline(outline) for outline in outlines if outline != ""]
    return outlines


def parse_vdm_outline(output: str):
    """
    Parse the VDM output from the given file path.

    Parameters:
        file_path (str): The path to the file to be parsed.

    Returns:
        Outline: An Outline object containing the parsed data.
    
    Raises:
        FileNotFoundError: If the file could not be found.
    """
    car_pattern = re.compile(r"Car.*?direction:=(?P<direction>\d+(.\d+)?).*?progress:=(?P<progress>\d+(.\d+)?).*?road_id:=(?P<road_id>\d+(.\d+)?)")
    street_lamp_pattern = re.compile(r"StreetLamp.*?position:=(?P<position>\d+(.\d+)?).*?road_id:=(?P<road_id>\d+(.\d+)?).*?lamp_state:=(?P<state><ON>|<OFF>)")

    # Parsing cars
    cars = set()
    for match in car_pattern.finditer(output):
        match_dict = match.groupdict()

        direction = match.groupdict()["direction"]
        progress = match.groupdict()["progress"]
        road_id = match.groupdict()["road_id"]

        car = Car(road_id, float(progress), int(direction))
        cars.add(car)

    # Parsing street lamps
    street_lamps = set()
    for match in street_lamp_pattern.finditer(output):
        match_dict = match.groupdict()

        lamp_state = match_dict["state"]
        position = match_dict["position"]
        road_id = match_dict["road_id"]
        
        street_lamp = StreetLamp(lamp_state, road_id, float(position))
        street_lamps.add(street_lamp)

    # Assuming the time is at the start of the file in the format 'Time: [value]'
    time_match = re.search(r"\((?P<time>\d+(\.\d+)?),", output)
    if time_match is None:
        raise ValueError("Could not find the time in the file.")
    match_dict = time_match.groupdict()
    time = match_dict["time"]

    return Outline(time, cars, street_lamps)