import argparse
import sys
import pyray as rl
from pathlib import Path
from utils import parse_vdm_city, parse_vdm_output, Outline
from drawing_utils import draw_car, draw_street_lamp
import time

# Check if rich is installed, and only import it if it is.
try:
    from rich import pretty, print

    pretty.install()
except ImportError or ModuleNotFoundError:
    pass

# Parsing the arguments
parser = argparse.ArgumentParser(description='Draw the city')
parser.add_argument(
    '-cf',
    '--city-file',
    type=str,
    required=True,
    help='Path to the VDM city file'
)
parser.add_argument(
    '-of',
    '--outlines-file',
    type=str,
    required=True,
    help='Path to the VDM outlines file'
)
parser.add_argument(
    '-fd',
    '--font-dir',
    type=str,
    required=True,
    help='Path to the font directory'
)

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

if not args.font_dir:
    parser.print_help()
    sys.exit(1)

font_dir = Path(args.font_dir).resolve()
if not font_dir.exists():
    print(f"Directory {font_dir} does not exist.")
    sys.exit(1)

def draw_city(
    intersections: [(int, int)],
    roads: [(int, int)],
    outlines: [Outline],
    window_size=(800, 600),
    intersection_size=5
):
    rl.init_window(window_size[0], window_size[1], "City Visualization")
    rl.set_target_fps(60)
    intersection_size = 5

    # Camera setup
    camera = rl.Camera2D()
    camera.offset = rl.Vector2(window_size[0] / 2, window_size[1] / 2)
    camera.rotation = 0.0
    camera.zoom = 2.5 # Initial zoom level
    camera.target = rl.Vector2(-30.0, -100.0)

    paused = True

    # Load your custom font
    fonts = {
        "jetbrains-mono": {
            "regular": rl.load_font((font_dir / "JetBrainsMono-Regular.ttf").__str__()),
            "bold": rl.load_font((font_dir / "JetBrainsMono-Bold.ttf").__str__()),
            "italic": rl.load_font((font_dir / "JetBrainsMono-Italic.ttf").__str__()),
            "bold_italic": rl.load_font((font_dir / "JetBrainsMono-BoldItalic.ttf").__str__()),
        }
    }

    # Catppuccin color palette
    themes = {
        "macchiato": {
            "background": rl.Color(36, 39, 58, 255),        # base
            "intersection": rl.Color(73, 77, 100, 255),     # surface1
            "road": rl.Color(54, 58, 79, 255),              # surface0
            "street_lamp_on": rl.Color(223, 142, 29, 255),  # Yellow
            "street_lamp_off": rl.Color(82, 75, 65, 255),   # Muted yellow
            "car": rl.Color(238, 153, 160, 255),            # maroon
            "car_reverse": rl.Color(198, 160, 246, 255),    # mauve
            "text": rl.Color(202, 211, 245, 255)            # text
        },
        "latte": {
            "background": rl.Color(239, 241, 245, 255),     # base
            "intersection": rl.Color(188, 192, 204, 255),   # surface1
            "road": rl.Color(204, 208, 218, 255),           # surface0
            "street_lamp_on": rl.Color(223, 142, 29, 255),  # Yellow -- left
            "street_lamp_off": rl.Color(82, 75, 65, 255),   # Muted yellow -- left
            "car": rl.Color(230, 69, 83, 255),              # maroon
            "car_reverse": rl.Color(136, 57, 239, 255),     # mauve
            "text": rl.Color(76, 79, 105, 255)              # text
        }
    }
    theme = "latte"

    # previous mouse position
    prev_mouse_pos = rl.get_mouse_position()
    # start_time = time.time()
    last_time = time.time()
    last = False
    while not rl.window_should_close():
        colors = themes[theme]
        new_time = time.time()

        # total_delta_time = new_time - start_time

        delta_time = new_time - last_time
        if delta_time > 0.1:
            last_time = new_time
            # print(f"outline lenght: {len(outlines)}")
            if len(outlines) > 1 and not paused:
                outlines.pop(0)
            elif paused:
                print("Paused")
            elif not last:
                last = True
                print("Continuing to draw last outline")

        rl.begin_drawing()
        rl.clear_background(colors["background"])

        # get current window size
        window_size = rl.get_screen_width(), rl.get_screen_height()

        font_size = 25
        kerning = 1
        spacing_x = 150
        start_x = 20
        spacing_y = font_size
        start_y = 10
        # draw total time in top left corner
        rl.draw_text_ex(
            fonts["jetbrains-mono"]["bold"],
            f"Time:",
            rl.Vector2(start_x, start_y),
            font_size,
            kerning,
            colors["text"]
        )
        rl.draw_text_ex(
            fonts["jetbrains-mono"]["bold"],
            f"{outlines[0].time:.2f}",
            rl.Vector2(start_x + spacing_x, start_y),
            font_size,
            kerning,
            colors["text"]
        )
        # draw current power usage in top left corner
        rl.draw_text_ex(
            fonts["jetbrains-mono"]["bold"],
            f"Power:",
            rl.Vector2(start_x, start_y + spacing_y),
            font_size,
            kerning,
            colors["text"]
        )
        rl.draw_text_ex(
            fonts["jetbrains-mono"]["bold"],
            f"{outlines[0].power_usage * 100:.2f}%",
            rl.Vector2(start_x + spacing_x, start_y + spacing_y),
            font_size,
            kerning,
            colors["text"]
        )
        # draw current traffic density in top left corner
        rl.draw_text_ex(
            fonts["jetbrains-mono"]["bold"],
            f"Density:",
            rl.Vector2(start_x, start_y + spacing_y * 2),
            font_size,
            kerning,
            colors["text"]
        )
        rl.draw_text_ex(
            fonts["jetbrains-mono"]["bold"],
            f"{outlines[0].traffic_density * 1000:.2f} cars/km",
            rl.Vector2(start_x + spacing_x, start_y + spacing_y * 2),
            font_size,
            kerning,
            colors["text"]
        )

        # button top left to change theme
        if rl.is_key_pressed(rl.KEY_T):
            if theme == "latte":
                theme = "macchiato"
            else:
                theme = "latte"

        if rl.is_key_pressed(rl.KEY_P):
            paused = not paused

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
        if (rl.is_mouse_button_down(rl.MOUSE_LEFT_BUTTON)
            or rl.is_mouse_button_down(rl.MOUSE_MIDDLE_BUTTON)):
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
            rl.draw_line_ex(start, end, 8, colors["road"])

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

        rl.end_mode_2d()
        rl.end_drawing()

# Parse the city data
city_contents = city_file.read_text()
intersections, roads = parse_vdm_city(city_contents)
print(intersections)
print(roads)

# Parse the outlines
outlines_contents = outlines_file.read_text()
outlines = parse_vdm_output(outlines_contents)
# print(outlines)
print(outlines[60].cars)

# Adjust the window size if needed
window_size = (1200, 900)

# Draw the city
draw_city(intersections, roads, outlines, window_size)
