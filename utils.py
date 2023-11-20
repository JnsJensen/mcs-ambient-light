
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