#!/usr/bin/python3
"""
    Program to produce timelapse footage.

    Takes images, determines timestamp from filename,
    decides whether it is within desired timeframe and
    prepares command line tool (convert) to process a
    number of images to an averaged image, including a date and time
    After processing, ffmpeg is invoked to make the
    timelapse video.

    Depends on:
        - convert
        - ffmpeg
        - OpenSans (https://fonts.google.com)
        - tqdm (as pip module)
        - PIL
"""

# Import modules
import glob
import os
import datetime
from tqdm.contrib.concurrent import process_map
from tqdm import tqdm
from PIL import Image, ImageStat


# How much images to average
HOW_MUCH = 20


def convert_image(welke):
    """
    convert yyyy-mm-dd_HHMM.png to <timestamp>
    use convert to process it into an averaged frame and embedding the date/time
    """

    # welke is a list containing the images to process
    # To determine the timestamp, take the first image and remove its file extension
    timestamp = welke[0][1].replace('.jpg', '')
    tijdstip = datetime.datetime.strptime(
        timestamp, "%Y-%m-%d_%H%M").strftime('%d-%m-%Y %H:%M')

    # Prepare "convert" command
    command = []
    command.append('/usr/bin/convert')
    command.append('-resize 1280 -crop 1280x720+0+0')

    # Append each (HOW_MUCH) image
    for image in welke:
        command.append('{0}/{1}'.format(
            image[0], image[1]))

    # Calculate average image
    command.append('-evaluate-sequence mean')

    # Overlay the date and time
    command.append("-font Open-Sans-SemiBold")
    command.append("-pointsize 20 -fill white")
    command.append("-undercolor '#00000080'")
    command.append("-annotate +1120+715 ' {} ' ".format(tijdstip))

    # Processed image name
    command.append('processed_{}/{} '.format(welke[0][0], welke[0][1]))

    # Join command together to a single string
    command = ' '.join(command)

    result = os.system(command)
    if (result != os.EX_OK):
        print("There was an error processing 'convert' !")


def make_movie(folder, frames):
    """
    Prepare ffmpeg command and execute
    frames is the number of frames per second for the movie
    codec based on x264 and aac audio (mobile phone proof settings)
    """
    command = []
    command.append('ffmpeg')

    # Convert images into video
    command.append("-y -r {} -f image2 -pattern_type glob".format(frames))
    command.append("-i 'processed_{}/*.jpg'".format(folder, HOW_MUCH))

    # Add soundtrack
    command.append('-i muziek.mp3')

    # Set video codec
    command.append(
        '-c:v libx264 -pix_fmt yuv420p -profile:v baseline -level 3.0 -crf 22 -preset veryslow')
    command.append('-c:a aac -strict experimental -movflags +faststart')
    #command.append('-vcodec libx264 -profile:v high -preset slow')
    #command.append('-pix_fmt yuv420p')
    #command.append('-vprofile baseline -movflags +faststart')
    #command.append('-strict -2')
    # -acodec aac -b:a 128k')

    # Cut video/audio stream by the shortest one
    command.append('-shortest')

    # Filename
    command.append(
        'timelapse_{}.mp4'.format(folder))

    command = ' '.join(command)

    result = os.system(str(command))
    if (result != os.EX_OK):
        print("There was an error processing 'ffmpeg' !")
        exit(-1)


def image_ok(bestand):
    """
        Perform several checks on source image
        Only process images which are OK
    """

    # Check if processed file exists
    folder, file = os.path.split(bestand)
    if os.path.exists('processed_{}/{}'.format(folder, file)):
        return False, None

    # Check file size
    if os.path.getsize(bestand) == 0:
        return False, None

    # Now check averaged brightness, too low == dark == not OK
    im = Image.open(bestand).convert('L')
    stat = ImageStat.Stat(im)
    brightness = stat.mean[0]
    if brightness < 75:         # 50 is arbitrair gekozen
        return False, None

    # If all OK:
    return True, bestand


def main(folder, framerate):
    """
        Create a list of images and sort by image name,
        select which images to process,
        call convert_image for an averaged frame and to add a timestamp
        Finally, run ffmpeg to compile the timelapse video
    """

    # Scan img directory to find the images to process
    print("Scanning {} directory for pictures...".format(folder))
    # First, evaluate whether the image is ok (not already processed and light enough)
    images_checked = process_map(
        image_ok, glob.glob('{}/*.jpg'.format(folder)), chunksize=4)
    # Now put images to process in a queue
    images = [os.path.split(file) for flag, file in images_checked if flag]

    # Sort by number (2nd field in 'images')
    images.sort(key=lambda item: item[1])

    # Determine which images to process
    # Make slices for each image to process, each including
    # which images to use in the averaged frame
    slices = [images[i:i + HOW_MUCH]
              for i, _ in enumerate(images)]

    # Create folder for processed images
    directory = 'processed_{}'.format(folder)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Process images (using multiple processes,
    # as 'convert' is single threaded
    print("Starting convert_image for selected images...")
    process_map(convert_image, slices, chunksize=1)

    # Use images for timelapse video
    print("Invoking ffmpeg to process images into video...")
    make_movie(folder, framerate)

    print("All done...")


if __name__ == "__main__":
    main('img', 60)
    main('img_cam2', 60)
