import pygame
import sounddevice as sd
import numpy as np

pygame.init()
window_width = 75  # Initial desired screen width
window_height = 16  # Initial desired screen height
blocksize = 576  # Blocksize for the audio buffer
xs = np.linspace(0, window_width - 1, num=window_width, dtype=np.int32)
screen = np.zeros((window_width, window_height, 3), dtype=np.uint8)
gain = 2
last_y = 0  # Initialize last_y
window = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
running = True  # Variable to control the main loop

def draw_wave(indata, frames, time, status):
    global screen, last_y, window_width, window_height  # Declare 'screen', 'last_y', 'window_width', and 'window_height' as global

    mono_audio = indata[:, 0]  # Extract mono audio from the input data

    screen *= 0  # Clear the screen

    length = len(xs)
    blocksize_ratio = int(blocksize / length)
    ys = window_height // 2 * (1 - np.clip(gain * mono_audio[::blocksize_ratio], -1, 1))
    ys = ys.astype(int)  # Convert ys to integer

    for x, y in zip(xs, ys):
        x = np.clip(x, 0, window_width - 1)  # Clip x value to the valid range
        y = np.clip(y, 0, window_height - 1)  # Clip y value to the valid range

        if x == 0:
            last_y = y

        top = y
        bottom = last_y
        last_y = y

        if bottom < top:
            [bottom, top] = [top, bottom]
            top += 1

        for dy in range(top, bottom + 1):
            screen[x, dy] = (255, 255, 255)  # Fill the range with the pixel color

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

with sd.InputStream(callback=draw_wave, channels=1, blocksize=1152):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
