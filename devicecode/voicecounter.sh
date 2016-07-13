#!/bin/sh
cd /home/pi/voicecount

export GST_PLUGIN_PATH=/usr/local/lib/gstreamer-1.0
export PKG_CONFIG_PATH=/usr/local/lib/pkgconfig

## reset the USB microphone by disabling it and reenabling it.
sudo sh -c "echo 0 > /sys/bus/usb/devices/1-1.5/authorized"
sudo sh -c "echo 1 > /sys/bus/usb/devices/1-1.5/authorized"

## run the voice counter and pipe output to a logfile.
##python voicecounter.py &> output.log &

## run the voice counter.
python voicecounter.py
