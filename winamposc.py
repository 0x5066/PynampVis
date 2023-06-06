import pygame
import sounddevice as sd
import numpy as np
import argparse
from viscolors import range_by_amplitude, load_colors
import os

pygame.init()
window_width = 75  # Initial desired screen width
window_height = 16  # Initial desired screen height
blocksize = 576  # Blocksize for the audio buffer
xs = np.linspace(0, window_width - 1, num=window_width, dtype=np.int32)
screen = np.zeros((window_width, window_height, 3), dtype=np.uint8)
gain = 2
last_y = 0  # Initialize last_y
window = pygame.display.set_mode((window_width*8, window_height*16), pygame.RESIZABLE)
running = True  # Variable to control the main loop

parser = argparse.ArgumentParser(description='Winamp Visualizer in Python')
parser.add_argument("-o", "--oscstyle", help="Oscilloscope drawing", nargs='*', type=str.lower, default=["lines"])
args = parser.parse_args()
#print(args.oscstyle)

filename = 'viscolor.txt'

if os.path.exists(filename):
    osc_colors = load_colors(filename)
else:
    filename_lower = filename.lower()
    if os.path.exists(filename_lower):
        osc_colors = load_colors(filename_lower)
    else:
        osc_colors = load_colors(filename.upper())

def draw_wave(indata, frames, time, status):
    global screen, last_y, window_width, window_height, osc_colors  # Declare 'osc_colors' as global

    mono_audio = indata[:, 0] + 0.03  # Extract mono audio from the input data

    screen *= 0  # Clear the screen

    length = len(xs)
    blocksize_ratio = int(blocksize / length)
    ys = window_height // 2 * (1 - np.clip(gain * mono_audio[::blocksize_ratio], -1, 1))
    ys = ys.astype(int)  # Convert ys to integer

    # Define the thresholds for color assignments
    thresholds = [0.1, 0.3, 0.5, 0.7, 0.9]
    num_thresholds = len(thresholds)
    num_colors = len(osc_colors)

    for x, y in zip(xs, ys):
        x = np.clip(x, 0, window_width - 1)  # Clip x value to the valid range
        y = np.clip(y, 0, window_height - 1)  # Clip y value to the valid range

        if args.oscstyle == ["lines"]:
            if x == 0:
                last_y = y

            top = y
            bottom = last_y
            last_y = y

            if bottom < top:
                [bottom, top] = [top, bottom]
                top += 1

            # Calculate the color index based on the amplitude
            amplitude = abs(y + 0.2 - window_height / 2) / (window_height / 2)

            if amplitude < thresholds[0]:
                color_index = 0
            elif amplitude < thresholds[1]:
                color_index = 1
            elif amplitude < thresholds[2]:
                color_index = 2
            elif amplitude < thresholds[3]:
                color_index = 3
            elif amplitude < thresholds[4]:
                color_index = 4
            else:
                color_index = 5

            if top == 0:
                color_index = 5

            if top == 0 and color_index == 5:
                color_index = 4

            color_top = osc_colors[color_index % num_colors]

            for dy in range(top, bottom + 1):
                screen[x, dy] = color_top

        if args.oscstyle == ["solid"]:
            if x == 0:
                last_y = y

            if y >= 8:
                top = 8
                bottom = y
            else:
                top = y
                bottom = 7

            # Calculate the color index based on the amplitude
            amplitude = abs(y + 0.2 - window_height / 2) / (window_height / 2)

            if amplitude < thresholds[0]:
                color_index = 0
            elif amplitude < thresholds[1]:
                color_index = 1
            elif amplitude < thresholds[2]:
                color_index = 2
            elif amplitude < thresholds[3]:
                color_index = 3
            elif amplitude < thresholds[4]:
                color_index = 4
            else:
                color_index = 5

            if top == 0:
                color_index = 5

            if top == 0 and color_index == 5:
                color_index = 4

            color_top = osc_colors[color_index % num_colors]

            for dy in range(top, bottom + 1):
                screen[x, dy] = color_top

        if args.oscstyle == ["dots"]:
            top = y
            bottom = y

            # Calculate the color index based on the amplitude
            amplitude = abs(y + 0.2 - window_height / 2) / (window_height / 2)
            color_index = int(amplitude * num_thresholds)

            if top == 0 and color_index == 5:
                color_index = 4

            color_top = osc_colors[color_index % num_colors]

            for dy in range(top, bottom + 1):
                screen[x, dy] = color_top

    # Convert the screen array to a pygame.Surface object
    surface = pygame.surfarray.make_surface(screen)

    # Rescale the surface to match the window size
    scaled_surface = pygame.transform.scale(surface, (window.get_width(), window.get_height()))

    # Blit the scaled surface onto the window
    window.blit(scaled_surface, (0, 0))
    pygame.display.flip()

def resize_window(width, height):
    global screen, window_width, window_height, xs

    window_width = width
    window_height = height

    # Resize the screen array
    screen = np.zeros((window_width, window_height, 3), dtype=np.uint8)

    # Update xs with the new window width
    xs = np.linspace(0, window_width - 1, num=window_width, dtype=np.int32)

with sd.InputStream(callback=draw_wave, channels=1, blocksize=blocksize):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()