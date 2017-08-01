#!/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/games:/usr/games
export DISPLAY=:0
killall omxplayer.bin
killall python3
sleep 3
vcgencmd display_power 0
