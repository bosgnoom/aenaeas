#!/bin/sh

# Get images from remote raspberry pi

rsync -av pi@192.168.178.15:/home/pi/webcam/img/* img/
rsync -av pi@192.168.178.15:/home/pi/webcam/img_cam2/* img_cam2/
