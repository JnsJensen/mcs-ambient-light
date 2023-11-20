
class Car:
    def __init__(self, road_id, progress=0, direction=1, velocity=10):
        self.velocity = velocity
        self.road_id = road_id
        self.progress = progress
        self.direction = direction
        assert direction in {-1, 1}, "Invalid direction value"

    def __repr__(self):
        return f"Car(road_id={self.road_id}, progress={self.progress}, direction={self.direction}, velocity={self.velocity})"

class Sensor:
    RANGE = 10.0

    def __init__(self, road_id, position, cars=None):
        self.cars = cars if cars is not None else set()
        self.road_id = road_id
        self.position = position

    def __repr__(self):
        return f"Sensor(road_id={self.road_id}, position={self.position}, cars={self.cars})"

class StreetLamp:
    def __init__(self, lamp_state, sensor, road_id, position):
        self.lamp_state = lamp_state
        self.sensor = sensor
        self.road_id = road_id
        self.position = position

    def __repr__(self):
        return f"StreetLamp(lamp_state={self.lamp_state}, sensor={self.sensor}, road_id={self.road_id}, position={self.position})"

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
