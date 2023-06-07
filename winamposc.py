#ChatGPT wrote most of this.

import pygame
import sounddevice as sd
import numpy as np
import argparse
from viscolors import load_colors

pygame.init()
global screen, last_y, window_width, window_height
window_width = 75  # Initial desired screen width
window_height = 16  # Initial desired screen height
xs = np.linspace(0, window_width - 1, num=window_width, dtype=np.int32)
screen = np.zeros((window_width, window_height, 3), dtype=np.uint8)
gain = 2
last_y = 0
peak1 = 0
window = pygame.display.set_mode((window_width * 8, window_height * 8), pygame.RESIZABLE)
running = True
visualization_mode = 0  # 0 for oscilloscope, 1 for analyzer, 2 for grid

parser = argparse.ArgumentParser(description='Winamp Visualizer in Python')
parser.add_argument("-o", "--oscstyle", help="Oscilloscope drawing", nargs='*', type=str.lower, default=["lines"])
#parser.add_argument("-v", "--visualization", help="Visualization type: oscilloscope or analyzer", type=str.lower,
                    #choices=["oscilloscope", "analyzer", "grid"], default="analyzer")
parser.add_argument("-b", "--blocksize", help="Blocksize for audio buffer", type=int, default=576)
args = parser.parse_args()

# Load the first two colors from the viscolor.txt file
colors = load_colors("viscolor.txt")


def draw_wave(indata, frames, time, status):
    global visualization_mode

    mono_audio = indata[:, 0] + 0.03

    length = len(xs)
    blocksize_ratio = int(args.blocksize / length)
    ys = window_height // 2 * (1 - np.clip(gain * mono_audio[::blocksize_ratio], -1, 1))
    ys = ys.astype(int)

    # Draw the grid background
    for x in range(window_width):
        for y in range(window_height):
            if x % 2 == 1 or y % 2 == 0:
                screen[x, y] = colors[0]
            else:
                screen[x, y] = colors[1]

    # Draw the visualization based on the selected mode
    if visualization_mode == 1:  # Oscilloscope mode
        for x, y in zip(xs, ys):
            x = np.clip(x, 0, window_width - 1)
            y = np.clip(y, 0, window_height - 1)

            if "lines" in args.oscstyle:
                if x == 0:
                    last_y = y

                top = y
                bottom = last_y
                last_y = y

                if bottom < top:
                    [bottom, top] = [top, bottom]
                    top += 1

                for dy in range(top, bottom + 1):
                    screen[x, dy] = (255, 255, 255)

            elif "solid" in args.oscstyle:
                if x == 0:
                    last_y = y

                if y >= 8:
                    top = 8
                    bottom = y
                else:
                    top = y
                    bottom = 7

                for dy in range(top, bottom + 1):
                    screen[x, dy] = (255, 255, 255)

            elif "dots" in args.oscstyle:
                top = y
                bottom = y

                for dy in range(top, bottom + 1):
                    screen[x, dy] = (255, 255, 255)

    elif visualization_mode == 0:  # Analyzer mode
        global peak1
        # Perform FFT on the audio data
        spectrum = np.abs(np.fft.fft((mono_audio - 0.03) / 128))
        spectrum = spectrum[:window_width]

        weights = np.linspace(0.1, 1.0, num=window_width)
        weighted_spectrum = np.zeros(window_width)
        for y in range(window_width):
            start = int(y * length / window_width)
            end = int((y + 1) * length / window_width)
            weighted_spectrum[y] = np.mean(spectrum[start:end] * weights[start:end])

        for x, y in zip(xs, weighted_spectrum * window_height):
            x = np.clip(int(np.log10(x + 1) * window_width / np.log10(window_width + 1)), 0, window_width - 1)
            y = np.clip(int(y * window_height), 0, window_height - 1)
            for dy in range(-y + window_height, window_height):
                color_index = 2 + (dy % (len(colors) - 1))
                color = colors[color_index]
                screen[x, dy] = color

    elif visualization_mode == 2:  # Grid mode
        pass  # Nothing to draw, as the grid is already drawn in the background

    surface = pygame.surfarray.make_surface(screen)
    scaled_surface = pygame.transform.scale(surface, (window.get_width(), window.get_height()))
    window.blit(scaled_surface, (0, 0))
    pygame.display.flip()


def resize_window(width, height):
    global screen, window_width, window_height, xs

    window_width = width
    window_height = height

    screen = np.zeros((window_width, window_height, 3), dtype=np.uint8)
    xs = np.linspace(0, window_width - 1, num=window_width, dtype=np.int32)


with sd.InputStream(callback=draw_wave, channels=1, blocksize=args.blocksize):
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    visualization_mode = (visualization_mode + 1) % 3  # Switch to the next mode

pygame.quit()
exit()
