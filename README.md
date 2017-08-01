# Videowall
Python script for viewing RTSP streams from Hikvision (not only) cameras in grid on Raspberry Pi 3.
Our NVR is installed in a separate room in the server rack. We applied the Raspberry Pi 3 with our script to view cameras streams. The script takes RTSP streams from NVR channels and displays on the TV in the form of a grid.
Cron launches the script in the morning and stops in the evening, also turns off the HDMI output of Raspberry Pi, so if you even forget to turn off the TV - it will turn off automatically.

## Dependencies
This script uses Python 3 and Qt4, so please install dependencies first.

## How it looks
![banch](https://user-images.githubusercontent.com/1162284/28826180-c6764b82-76d1-11e7-8ef4-366f541669bd.jpg)
![screen](https://user-images.githubusercontent.com/1162284/28826218-f316d116-76d1-11e7-813c-14258b0d958f.jpg)
