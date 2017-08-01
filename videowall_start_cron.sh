#!/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/games:/usr/games
export DISPLAY=:0
vcgencmd display_power 1
killall omxplayer.bin
killall python3 
cd /home/pi/videowall 
sleep 5
/usr/bin/python3 /home/pi/videowall/videowall.py

