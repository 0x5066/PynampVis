#ChatGPT wrote most of this.

import sounddevice as sd
import numpy as np
import argparse
from scipy.signal import windows
from viscolors import load_colors

def get_sound_devices():
    devices = sd.query_devices()
    return devices

parser = argparse.ArgumentParser(description='Winamp Visualizer in Python')
parser.add_argument("-o", "--oscstyle", help="Oscilloscope drawing", nargs='*', type=str.lower, default=["lines"])
parser.add_argument("-s", "--specdraw", help="Coloring style", nargs='*', type=str.lower, default=["normal"])
parser.add_argument("-bw", "--bandwidth", help="Band line width", nargs='*', type=str.lower, default=["thick"])
parser.add_argument("-b", "--blocksize", help="Blocksize for audio buffer", type=int, default=576)
parser.add_argument("-d", "--device", help="Select your Device", type=int, default=None)
parser.add_argument("-v", "--viscolor", help="Define viscolor.txt", type=str, default="viscolor.txt")
parser.add_argument('-m', '--modern', help="Modern Skin mode", action='store_true')
args = parser.parse_args()
fun_mode = 0

# Check if the device argument is provided
if args.device is None:
    # If device argument is not provided, retrieve the list of sound devices
    sound_devices = get_sound_devices()

    # Print the list of sound devices
    print("Available sound devices:")
    for idx, device in enumerate(sound_devices):
        print(f"{idx}: {device['name']}")

    exit()

else:
    # If device argument is provided, use it for further processing
    selected_device = args.device

import pygame
pygame.init()

global screen, last_y, window_width, window_height
if args.modern is True:
    pygame.display.set_caption('Winamp Modern Mini Visualizer (in Python)')
    window_width = 72
else:
    pygame.display.set_caption('Winamp Mini Visualizer (in Python)')
    window_width = 75
if fun_mode == 1:
    window_height = 16*4
elif fun_mode == 2:
    window_height = 35
else:
    window_height = 35
window = pygame.display.set_mode((window_width * 8, window_height * 8), pygame.RESIZABLE)
xs = np.linspace(0, window_width - 1, num=window_width, dtype=np.int32)
screen = np.zeros((window_width, window_height, 3), dtype=np.uint8)
gain = 2
last_y = 0
peak1 = 0
running = True
visualization_mode = 0  # 0 for oscilloscope, 1 for analyzer, 2 for grid

# Set the sample rate
sd.default.samplerate = 44100

# Desired frequency range in Hz
frequency_min = 0
frequency_max = 44100

# Load the first two colors from the viscolor.txt file
colors = load_colors(args.viscolor)

def weighting_function(frequencies):
    """
    Custom weighting function to emphasize higher frequencies and reduce the magnitude of lower frequencies.
    Modify this function as needed to achieve the desired effect.
    """
    weights = np.ones_like(frequencies)  # Start with equal weights for all frequencies

    # Apply natural weighting, kind of like an equalizer...
    #               20      25     31.5    40    50     63     80    100    125    160     200   250    315   400   500  630  800 1000 1250 16002000 3000  4000  5000  6000 10000 
    A_weighting = [-10.2, -12.2, -12.2, -13.2, -13.2, -14.2, -15.2, -15.2, -14.2, -13.2, -13.2, -10.1, -6.4, -8.9, -3.6, 0.6, 1.8, 2.2, 3.9, 5, 8.0, 10.0, 13.0, 16.0, 18.0, 18.0]
    f_values = [20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 3000, 4000, 5000, 6000, 10000]
    # frequency values

    for i, freq in enumerate(frequencies):
        closest_index = np.abs(np.array(f_values) - freq).argmin()
        weights[i] *= 10 ** (A_weighting[closest_index] / 20.0)

    return weights

def OscColorsAndPeak():
    if len(colors) == 35:
        ScopeColors = [colors[18], colors[19], colors[20], colors[21], colors[22], colors[23], colors[24], colors[25], colors[26], colors[27], colors[28], colors[29], colors[30], colors[31], colors[32], colors[33]]
    else:
        ScopeColors = [colors[21], colors[21], colors[20], colors[20], colors[19], colors[19], colors[18], colors[18], colors[19], colors[19], colors[20], colors[20], colors[21], colors[21], colors[22], colors[22]]
    return ScopeColors
    # maps to 4 4 3 3 2 2 1 1 2 2 3 3 4 4 5 5

Oscicolors = OscColorsAndPeak() # inits the whole thing

def draw_wave(indata, frames, time, status):
    global visualization_mode, ys, peak1

    mono_audio = indata[:, 0] + indata[:, 1] / 2
    oscaudio = mono_audio + 0.03
    length = len(mono_audio)
    leftaudio = indata[:, 0]
    rightaudio = indata[:, 1]

    length = len(xs)
    blocksize_ratio = int(args.blocksize / length)
    fft_size = blocksize_ratio*23
    ys = 16 // 2 * (1 - np.clip(gain * leftaudio[::blocksize_ratio] + 0.03, -1, 1))
    ys = ys.astype(int)

    ys2 = 16 // 2 * (1 - np.clip(gain * rightaudio[::blocksize_ratio] + 0.03, -1, 1))
    ys2 = ys2.astype(int)

    if fun_mode >= 1:
        yx = window_height // 2 * (1 - np.clip(rightaudio[::blocksize_ratio], -1, 1))
        xy = window_width // 2 * (1 - np.clip(leftaudio[::blocksize_ratio], -1, 1))
        yx = yx.astype(int)
        xy = xy.astype(int)

    if fun_mode == 2:
        ys_flat = ys.flatten()

        f = open('output.raw', 'ab')
        ys_flat.astype(np.int8).tofile(f)

    # Draw the grid background
    for x in range(window_width):
        for y in range(window_height):
            if x % 2 == 1 or y % 2 == 0:
                screen[x, y] = colors[0]
            else:
                screen[x, y] = colors[1]

    # Draw the visualization based on the selected mode
    if visualization_mode == 1:  # Oscilloscope mode
        for x, y, y2 in zip(xs, ys, ys2):
            x = np.clip(x, 0, window_width - 1)
            y = np.clip(y, 0, 16 - 1)
            y2 = np.clip(y2, 0, 16 - 1)

            if "lines" in args.oscstyle:
                if x == 0:
                    last_y = y
                    last_y2 = y2

                top = y
                bottom = last_y
                last_y = y

                top2 = y2
                bottom2 = last_y2
                last_y2 = y2

                if bottom < top:
                    [bottom, top] = [top, bottom]
                    top += 1
                
                if bottom2 < top2:
                    [bottom2, top2] = [top2, bottom2]
                    top2 += 1

                for dy in range(top, bottom + 1):
                    color_index = (top) % len(Oscicolors)
                    ScopeColors = Oscicolors[color_index]
                    if args.modern is True:
                        screen[x, -dy+15] = ScopeColors
                    else:
                        screen[x, dy] = ScopeColors

                for dy2 in range(top2, bottom2 + 1):
                    color_index = (top2) % len(Oscicolors)
                    ScopeColors = Oscicolors[color_index]
                    if args.modern is True:
                        screen[x, -dy2-2] = ScopeColors
                    else:
                        screen[x, dy2-17] = ScopeColors

            elif "solid" in args.oscstyle:
                if x == 0:
                    last_y = y
                    last_y2 = y2

                if y >= 8:
                    top = 8
                    bottom = y
                else:
                    top = y
                    bottom = 7

                if y2 >= 8:
                    top2 = 8
                    bottom2 = y2
                else:
                    top2 = y2
                    bottom2 = 7

                for dy in range(top, bottom + 1):
                    color_index = (y) % len(Oscicolors)
                    ScopeColors = Oscicolors[color_index]
                    if args.modern is True:
                        screen[x, -dy+15] = ScopeColors
                    else:
                        screen[x, dy] = ScopeColors

                for dy2 in range(top2, bottom2 + 1):
                    color_index = (y2) % len(Oscicolors)
                    ScopeColors = Oscicolors[color_index]
                    if args.modern is True:
                        screen[x, -dy2-2] = ScopeColors
                    else:
                        screen[x, dy2-16] = ScopeColors

            elif "dots" in args.oscstyle:

                for dy in range(y):
                    color_index = (y) % len(Oscicolors)
                    ScopeColors = Oscicolors[color_index]
                    if args.modern is True:
                        screen[x, -y+15] = ScopeColors
                    else:
                        screen[x, y] = ScopeColors

                for dy2 in range(y2):
                    color_index = (y2) % len(Oscicolors)
                    ScopeColors = Oscicolors[color_index]
                    if args.modern is True:
                        screen[x, -y2-2] = ScopeColors
                    else:
                        screen[x, y2-16] = ScopeColors

    elif visualization_mode == 0:  # Analyzer mode

        window2 = windows.hann(fft_size)
        windowed_audioL = (leftaudio) / 12
        windowed_audioR = (rightaudio) / 12
        windowed_audioL = np.resize(windowed_audioL, len(window2)) * window2
        windowed_audioR = np.resize(windowed_audioR, len(window2)) * window2
        spectrum = np.abs(np.fft.fft(windowed_audioL, n=fft_size))
        spectrum2 = np.abs(np.fft.fft(windowed_audioR, n=fft_size))
        frequencies = np.fft.fftfreq(fft_size, 1 / sd.default.samplerate)

        weights = weighting_function(frequencies)
        weighted_spectrum = spectrum * weights
        weighted_spectrum2 = spectrum2 * weights

        scaled_spectrum = weighted_spectrum * 16
        scaled_spectrum2 = weighted_spectrum2 * 16

        if "thick" in args.bandwidth:
            xs2 = xs*4
        else: 
            xs2 = xs

        for x, y, y2 in zip(xs2, scaled_spectrum[np.clip(xs2, 0, len(scaled_spectrum) - 1)], scaled_spectrum2[np.clip(xs2, 0, len(scaled_spectrum2) - 1)]):
            x = np.clip(x, 0, 75 - 0)
            y = int(np.clip(-y + 17, 1, 17 - 1))
            y2 = int(np.clip(-y2 + 17, 1, 17 - 1))

            intensity = scaled_spectrum[x]
            intensity2 = scaled_spectrum2[x]

            if y >= 16:
                top = 17
                bottom = y
            else:
                top = y
                bottom = 16

            if y2 >= 16:
                top2 = 17
                bottom2 = y2
            else:
                top2 = y2
                bottom2 = 16

            if x >= 75:
                top = 17
            if x >= 75:
                top2 = 17

            for dy in range(top, bottom):
                if "normal" in args.specdraw:
                    color_index = (2 + dy) % len(colors)
                if "line" in args.specdraw:
                    if intensity > 16:
                        color_index = (1 + y) % len(colors)
                    else:
                        color_index = (2 + y) % len(colors)
                if "fire" in args.specdraw:
                    color_index = (3 + dy-y) % len(colors)

                color = colors[int(color_index)]
                if "thick" in args.bandwidth:
                    screen[np.clip(x, 0, window_width - 1), dy] = color
                    screen[np.clip((x + 1), 0, window_width - 1), dy] = color
                    screen[np.clip((x + 2), 0, window_width - 1), dy] = color
                else: 
                    screen[x, dy] = color

            for dy2 in range(top2, bottom2):
                if "normal" in args.specdraw:
                    color_index = (2 + dy2) % len(colors)
                if "line" in args.specdraw:
                    if intensity2 > 16:
                        color_index = (1 + y2) % len(colors)
                    else:
                        color_index = (2 + y2) % len(colors)
                if "fire" in args.specdraw:
                    color_index = (3 + dy2-y2) % len(colors)

                color = colors[int(color_index)]
                if "thick" in args.bandwidth:
                    screen[np.clip(x, 0, window_width - 1), -dy2-1] = color
                    screen[np.clip((x + 1), 0, window_width - 1), -dy2-1] = color
                    screen[np.clip((x + 2), 0, window_width - 1), -dy2-1] = color
                else: 
                    screen[x, -dy2-1] = color

    if fun_mode >= 1:

        for x, y in zip(xy, yx):
            x = np.clip(-x+window_width-1, 0, window_width - 1)
            y = np.clip(y, 0, window_height - 1)
            top = y
            bottom = y

            for dy in range(top, bottom + 1):
                color_index = (top) % len(Oscicolors)
                ScopeColors = Oscicolors[color_index]
                screen[x % window_width, np.clip(dy, 0, window_height - 1)] = (124,252,0)

    elif visualization_mode == 2:  # None
        pass  # Nothing to draw, as the grid is already drawn in the background

    surface = pygame.surfarray.make_surface(screen)
    scaled_surface = pygame.transform.scale(surface, (window.get_width(), window.get_height()))
    window.blit(scaled_surface, (0, 0))
    pygame.display.flip()

with sd.InputStream(dtype='float32', callback=draw_wave, channels=2, blocksize=args.blocksize*2, latency=0, device=args.device):
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    visualization_mode = (visualization_mode + 1) % 3  # Switch to the next mode

pygame.quit()
exit()
