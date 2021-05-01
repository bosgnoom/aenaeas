#!/bin/sh

# Get images from remote raspberry pi

rsync -av pi@192.168.178.15:/home/pi/webcam/img . 
rsync -av pi@192.168.178.15:/home/pi/webcam/img_cam2 . 
