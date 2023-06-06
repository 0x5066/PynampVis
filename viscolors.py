import os

def load_colors(file_path):
    # Convert the file_path to lowercase for case-insensitive matching
    lower_file_path = file_path.lower()

    # Check if the lower_file_path exists
    if os.path.exists(lower_file_path):
        file_path = lower_file_path

    colors = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('//'):
                color_values = line.split(',')
                color = [int(value) for value in color_values[:3]]
                colors.append(color)
    osc_colors = colors[18:23]  # Extract the oscilloscope colors only
    return osc_colors

def range_by_amplitude(amplitude, osc_colors):
    #amplitude = abs(amplitude)  # Apply the absolute value to ensure positive amplitudes
    if amplitude >= 0:
        return [0, 3]
    elif amplitude >= 1:
        return [1, 3]
    elif amplitude >= 2:
        return [2, 2]
    elif amplitude >= 3:
        return [3, 2]
    elif amplitude >= 4:
        return [4, 1]
    elif amplitude >= 5:
        return [5, 1]
    elif amplitude >= 6:
        return [6, 0]
    elif amplitude >= 7:
        return [7, 0]
    elif amplitude >= 8:
        return [8, 1]
    elif amplitude >= 9:
        return [9, 1]
    elif amplitude >= 10:
        return [10, 2]
    elif amplitude >= 11:
        return [11, 2]
    elif amplitude >= 12:
        return [12, 3]
    elif amplitude >= 13:
        return [13, 3]
    elif amplitude >= 14:
        return [14, 4]
    else:
        return [15, 4]