#!/bin/sh
cd /home/pi/voicecount
python voicecounter.py &> output.log &
exit 0