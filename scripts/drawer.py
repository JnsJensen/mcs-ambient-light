import argparse
import sys
import pyray as rl
from pathlib import Path
from utils import parse_vdm_city, parse_vdm_output, Outline, Car, StreetLamp
from drawing_utils import draw_car, draw_street_lamp
import time

# Check if rich is installed, and only import it if it is.
try:
    from rich import pretty, print

    pretty.install()
except ImportError or ModuleNotFoundError:
    pass

# Parsing the arguments
# -f --file: The path to the file to be parsed
parser = argparse.ArgumentParser(description='Draw the city')
parser.add_argument('-cf', '--city-file', type=str, required=True, help='Path to the VDM city file')
parser.add_argument('-of', '--outlines-file', type=str, required=True, help='Path to the VDM outlines file')

args = parser.parse_args()

if not args.city_file:
    parser.print_help()
    sys.exit(1)

city_file = Path(args.city_file).resolve()
if not city_file.exists():
    print(f"File {city_file} does not exist.")
    sys.exit(1)

if not args.outlines_file:
    parser.print_help()
    sys.exit(1)

outlines_file = Path(args.outlines_file).resolve()
if not outlines_file.exists():
    print(f"File {outlines_file} does not exist.")
    sys.exit(1)

def draw_city(intersections: [(int, int)], roads: [(int, int)], outlines: [Outline], window_size=(800, 600), intersection_size=5):
    rl.init_window(window_size[0], window_size[1], "City Visualization")
    rl.set_target_fps(60)
    intersection_size = 5

    # Camera setup
    camera = rl.Camera2D()
    camera.offset = rl.Vector2(window_size[0] / 2, window_size[1] / 2)
    camera.rotation = 0.0
    camera.zoom = 2.0 # Initial zoom level
    camera.target = rl.Vector2(-30.0, -50.0)

    # Catppuccin color palette
    colors = {
        "background": rl.Color(36, 39, 58, 255),        # Mocha base
        "intersection": rl.Color(73, 77, 100, 255),     # surface1
        "road": rl.Color(54, 58, 79, 255),              # surface0
        "street_lamp_on": rl.Color(223, 142, 29, 255),  # Yellow
        "street_lamp_off": rl.Color(82, 75, 65, 255),   # Muted yellow
        "car": rl.Color(238, 153, 160, 255),            # maroon
        "car_reverse": rl.Color(198, 160, 246, 255),    # mauve
    }

    # previous mouse position
    prev_mouse_pos = rl.get_mouse_position()
    start_time = time.time()
    last_time = time.time()
    while not rl.window_should_close():
        new_time = time.time()

        total_delta_time = new_time - start_time
        # print(f"Total time: {total_delta_time}")

        delta_time = new_time - last_time
        if delta_time > 0.1:
            last_time = new_time
            # print(f"outline lenght: {len(outlines)}")
            if len(outlines) > 1:
                outlines.pop(0)
            else:
                print("Continuing to draw last outline")

        rl.begin_drawing()
        rl.clear_background(colors["background"])

        # move camera with arrow keys
        # or the wasd keys if you're a cool kid
        if (rl.is_key_down(rl.KEY_LEFT) or rl.is_key_down(rl.KEY_A)):
            camera.target.x -= 10.0 / camera.zoom
        if (rl.is_key_down(rl.KEY_RIGHT) or rl.is_key_down(rl.KEY_D)):
            camera.target.x += 10.0 / camera.zoom
        if (rl.is_key_down(rl.KEY_UP) or rl.is_key_down(rl.KEY_W)):
            camera.target.y -= 10.0 / camera.zoom
        if (rl.is_key_down(rl.KEY_DOWN) or rl.is_key_down(rl.KEY_S)):
            camera.target.y += 10.0 / camera.zoom

        mouse_pos = rl.get_mouse_position()
        if (rl.is_mouse_button_down(rl.MOUSE_LEFT_BUTTON) or rl.is_mouse_button_down(rl.MOUSE_MIDDLE_BUTTON)):
            camera.target.x -= (mouse_pos.x - prev_mouse_pos.x) / camera.zoom
            camera.target.y -= (mouse_pos.y - prev_mouse_pos.y) / camera.zoom

        prev_mouse_pos = mouse_pos

        # zoom camera with mouse wheel
        camera.zoom += (float(rl.get_mouse_wheel_move()) * 0.05 * camera.zoom)
        # clamp camera zoom between 0.1 and 3.0
        if (camera.zoom > 3.0):
            camera.zoom = 3.0
        elif (camera.zoom < 0.1):
            camera.zoom = 0.1

        # ╭--------------------------------------------------------------------╮
        # │                          🏙️ 2D World Drawing                       ▕
        # ╰--------------------------------------------------------------------╯
        rl.begin_mode_2d(camera)

        # Draw roads
        for road in roads:
            start = intersections[road[0] - 1]
            end = intersections[road[1] - 1]
            # rl.draw_line(start[0], start[1], end[0], end[1], colors["road"])
            rl.draw_line_ex(start, end, 8, colors["road"])
            # draw the road as a rectangle
            # rl.draw_rectangle_lines(start[0], start[1], end[0] - start[0], end[1] - start[1], colors["road"])

        # Draw intersections
        for pos in intersections:
            rl.draw_circle(pos[0], pos[1], intersection_size, colors["intersection"])

        o = outlines[0]
        
        # Draw street lamps
        for lamp in o.street_lamps:
            draw_street_lamp(
                lamp,
                intersections,
                roads,
                size = intersection_size/2,
                on_color = colors["street_lamp_on"],
                off_color = colors["street_lamp_off"]
            )
        # Draw cars
        for car in o.cars:
            # last car draw with a different color
            color = colors["car"]
            if car.direction == -1:
                color = colors["car_reverse"]
            draw_car(
                car,
                intersections,
                roads,
                size = intersection_size/2,
                color = color
            )

        # o = outlines[0]
        # cars = o.cars
        # for car in cars:
            
        # draw debug circle in center of world
        # rl.draw_circle(0, 0, 5, rl.RED)

        rl.end_mode_2d()
        rl.end_drawing()
    # keep window open until user closes it
    # rl.close_window()

# Parse the city data
city_contents = city_file.read_text()
intersections, roads = parse_vdm_city(city_contents)
print(intersections)
print(roads)

# Parse the outlines
outlines_contents = outlines_file.read_text()
outlines = parse_vdm_output(outlines_contents)
# print(outlines)

# Adjust the window size if needed
window_size = (800, 600)

# Draw the city
draw_city(intersections, roads, outlines, window_size)
