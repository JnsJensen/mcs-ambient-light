import pyray as rl
from utils import parse_vdm_city
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
parser = argparse.ArgumentParser(description='Draw the city')
parser.add_argument('-cf', '--city-file', type=str, required=True, help='Path to the city file')

args = parser.parse_args()

if not args.city_file:
    parser.print_help()
    sys.exit(1)

city_file = Path(args.city_file).resolve()
if not city_file.exists():
    print(f"File {city_file} does not exist.")
    sys.exit(1)

def draw_city(intersections, roads, window_size=(800, 600), intersection_size=5):
    rl.init_window(window_size[0], window_size[1], "City Visualization")
    rl.set_target_fps(60)
    intersection_size = 5

    # Camera setup
    camera = rl.Camera2D()
    camera.offset = rl.Vector2(window_size[0] / 2, window_size[1] / 2)
    camera.rotation = 0.0
    camera.zoom = 1.0 # Initial zoom level

    # Catppuccin color palette
    colors = {
        "background": rl.Color(36, 39, 58, 255),      # Mocha
        "intersection": rl.Color(244, 219, 214, 255), # Rosewater
        "road": rl.Color(183, 189, 248, 255),         # Lavender
    }

    # previous mouse position
    prev_mouse_pos = rl.get_mouse_position()

    while not rl.window_should_close():
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

        rl.begin_mode_2d(camera)

        # Draw roads
        for road in roads:
            start = intersections[road[0] - 1]
            end = intersections[road[1] - 1]
            rl.draw_line(start[0], start[1], end[0], end[1], colors["road"])

        # Draw intersections
        for pos in intersections:
            rl.draw_circle(pos[0], pos[1], intersection_size, colors["intersection"])

        # draw debug circle in center of world
        # rl.draw_circle(0, 0, 5, rl.RED)

        rl.end_mode_2d()

        # draw debug circle in center of screen
        # print(window_size[0] / 2, window_size[1] / 2)
        # rl.draw_circle(int(window_size[0] / 2), int(window_size[1] / 2), 5, rl.RED)

        rl.end_drawing()

    rl.close_window()

# Parse the city data
city_contents = city_file.read_text()
intersections, roads = parse_vdm_city(city_contents)
print(intersections)
print(roads)

# Adjust the window size if needed
window_size = (800, 600)

# Draw the city
draw_city(intersections, roads, window_size)
