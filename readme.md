# Winamp Classic/Modern Mini Visualizer

The famous Visualizer that's been embedded in Winamp since the late naughties, now exists as a Python program.
This also includes full support for the `viscolor.txt` spec, meaning you can throw in `viscolor.txt` from any Classic Skin, you can also pass -v to use a custom viscolor.txt.
A custom format for viscolor.txt is also supported, see viscolor_16osc.txt for details and pass `-v viscolor_16osc.txt` for a visual example.

The script is primarily a CLI program, due to how the initial setup works. You *have* to run `python winamposc.py` first to get a list of devices, then you can pass `-d DeviceInt` for the device you want, under Linux "default" and "pipewire" work fine for me.

## Usage

The following command line operations are currently present:
```
-o, --oscstyle                 Lets you choose between three styles, "lines", "solid" and "dots". By default "solid" is applied.

-s, --specdraw                 Works the same as --oscstyle, "normal", "fire", "line". By default "normal" is applied.

-bw, --bandwidth               Lets you choose the bandwidth for the analyzer. "thin" and "thick". By default "thick" is applied.

-b, --blocksize                The buffer used for audio processing, higher and lower values aren't exactly recommended. Default is 576 smps (to match Winamp/WACUP behavior)

-d, --device                   The device you want to use. Only accepts integer as input. See above on how to get a list of devices present.

-v, --viscolor                 Lets you use a custom viscolor.txt or viscolor_16osc.txt.

-m, --modern                   Enables a Modern Skin like version of the visualizer.
```

## Supported OSes

So far, only Linux is properly supported, the script is known to also run on Windows but for now, only Microphone/Stereomix/Virtual Audio Cable capture works as WASAPI loopback somehow does not work, any help on getting Windows properly supported is appreciated.