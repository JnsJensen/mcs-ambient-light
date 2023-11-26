from utils import parse_vdm_city, parse_vdm_output, Outline, Car, StreetLamp
import pyray as rl
import math
# Check if rich is installed, and only import it if it is.
try:
    from rich import pretty, print

    pretty.install()
except ImportError or ModuleNotFoundError:
    pass

def draw_street_lamp(
        lamp: StreetLamp,
        intersections: [(int, int)],
        roads: [(int, int)],
        on_color: rl.Color = rl.YELLOW,
        off_color: rl.Color = rl.GREEN,
        size: int = 5
    ):
    start = intersections[roads[lamp.road_id - 1][0] - 1]
    start = rl.Vector2(start[0], start[1])
    end = intersections[roads[lamp.road_id - 1][1] - 1]
    end = rl.Vector2(end[0], end[1])
    

    road_length = rl.vector_2distance(start, end)
    position_normalized = lamp.position / road_length
    # interpolate between the two points based on the street lamp's position
    pos = rl.vector2_lerp(start, end, position_normalized)

    # perpendicular vector
    normal = rl.vector2_subtract(end, start)
    normal = rl.vector2_rotate(normal, math.pi / 2)
    normal = rl.vector2_normalize(normal)
    # move lamp slightly to the side
    pos = rl.vector2_add(pos, rl.vector2_scale(normal, 10))
    
    color = on_color if lamp.lamp_state else off_color

    # print(f"Drawing car at ({pos.x}, {pos.y})")
    rl.draw_circle(int(pos.x), int(pos.y), size, color)

def draw_car(
        car: Car,
        intersections: [(int, int)],
        roads: [(int, int)],
        color: rl.Color = rl.RED,
        size: int = 5
    ):
    start = intersections[roads[car.road_id - 1][0] - 1]
    start = rl.Vector2(start[0], start[1])
    end = intersections[roads[car.road_id - 1][1] - 1]
    end = rl.Vector2(end[0], end[1])
    
    road_length = rl.vector_2distance(start, end)
    progress_normalized = car.progress / road_length
    # interpolate between the two points based on the car's progress
    # pos = rl.Vector2(0, 0)
    # if car.direction == 1:
    #     pos = rl.vector2_lerp(start, end, progress_normalized)
    # else:
    #     pos = rl.vector2_lerp(end, start, progress_normalized)
    pos = rl.vector2_lerp(start, end, progress_normalized)

    # move car slightly to the side
    # depending on the direction of the car
    offset_magnitude = size
    normal = rl.vector2_subtract(end, start)
    normal = rl.vector2_rotate(normal, math.pi / 2)
    normal = rl.vector2_normalize(normal)
    pos = rl.vector2_add(pos, rl.vector2_scale(normal, offset_magnitude * car.direction))

    # print(f"Dawing car at ({pos.x}, {pos.y})")

    # print(f"Drawing car at ({pos.x}, {pos.y})")
    rl.draw_circle(int(pos.x), int(pos.y), size, color)