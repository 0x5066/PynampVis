#ChatGPT wrote most of this.

import pygame
import sounddevice as sd
import numpy as np
import argparse
from viscolors import load_colors

pygame.init()
pygame.display.set_caption('Winamp Mini Visualizer (in Python)')
global screen, last_y, window_width, window_height
window_width = 75  # Initial desired screen width
window_height = 16  # Initial desired screen height
window = pygame.display.set_mode((window_width * 8, window_height * 8), pygame.RESIZABLE)
xs = np.linspace(0, window_width - 1, num=window_width, dtype=np.int32)
screen = np.zeros((window_width, window_height, 3), dtype=np.uint8)
gain = 2
last_y = 0
running = True
visualization_mode = 0  # 0 for oscilloscope, 1 for analyzer, 2 for grid

# Set the sample rate
sd.default.samplerate = 44100

# Desired frequency range in Hz
frequency_min = 0
frequency_max = 19000

parser = argparse.ArgumentParser(description='Winamp Visualizer in Python')
parser.add_argument("-o", "--oscstyle", help="Oscilloscope drawing", nargs='*', type=str.lower, default=["lines"])
#parser.add_argument("-v", "--visualization", help="Visualization type: oscilloscope or analyzer", type=str.lower,
                    #choices=["oscilloscope", "analyzer", "grid"], default="analyzer")
parser.add_argument("-b", "--blocksize", help="Blocksize for audio buffer", type=int, default=576)
args = parser.parse_args()

# Load the first two colors from the viscolor.txt file
colors = load_colors("viscolor.txt")

def weighting_function(frequencies):
    """
    Custom weighting function to emphasize higher frequencies and reduce the magnitude of lower frequencies.
    Modify this function as needed to achieve the desired effect.
    """
    weights = np.ones_like(frequencies)  # Start with equal weights for all frequencies

    # Apply natural weighting, kind of like an equalizer...
    A_weighting = [-18.2, -18.2, -18.2, -18.2, -18.2, -18.2, -18.2, -18.2, -17.2, -17.2, -16.2, -16.1, -13.4, -8.9, -3.6, 0.6, 1.8, 2.2, 3.9, 5, 8.0]
    f_values = [20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000]
    # frequency values

    for i, freq in enumerate(frequencies):
        closest_index = np.abs(np.array(f_values) - freq).argmin()
        weights[i] *= 10 ** (A_weighting[closest_index] / 20.0)

    return weights

def draw_wave(indata, frames, time, status):
    global visualization_mode

    mono_audio = indata[:, 0] + 0.03
    length = len(mono_audio)
    fft_size = length

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

        spectrum = np.abs(np.fft.fft((mono_audio - 0.03) / 18 , n=fft_size))
        frequencies = np.fft.fftfreq(fft_size, 1 / sd.default.samplerate)
        valid_indices = np.logical_and(frequencies >= frequency_min, frequencies <= frequency_max)
        valid_frequencies = frequencies[valid_indices]
        valid_spectrum = spectrum[valid_indices]

        weights = weighting_function(valid_frequencies)
        weighted_spectrum = valid_spectrum * weights

        scaled_spectrum = weighted_spectrum * window_height

        for x in range(len(valid_frequencies)):
            frequency = valid_frequencies[x]
            intensity = scaled_spectrum[x]

            # Skip drawing if intensity is below threshold
            if intensity < 1:
                continue

            x_norm = (frequency - frequency_min) / (frequency_max - frequency_min)
            x_coord = int(x_norm * window_width)
            x_coord = np.clip(x_coord, 0, window_width - 1)  # Clip x_coord within the valid range

            y = int(window_height - intensity) + 1  # Shift down by 1 pixel
            y = np.clip(y, 1, window_height - 1)  # Clip y within the valid range

            for dy in range(y, window_height):
                color_index = (2 + dy) % len(colors)
                color = colors[color_index]
                screen[x_coord, dy] = color

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
