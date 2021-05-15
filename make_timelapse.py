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
from tqdm.contrib.concurrent import process_map
import requests


# How much images to average
HOW_MUCH = 12

# Image processor URL
IMG_PROC = 'http://192.168.178.202:6000'
#IMG_PROC = 'http://localhost:8000'  # Run img processor locally


def image_ok(bestand):
    """
        Perform several checks on source image
        Only process images which are OK
    """

    # Check file size, skip empty files
    if os.path.getsize(bestand) == 0:
        return False, None

    # Check averaged brightness, too low == dark == not OK
    url = '{}/brightness'.format(IMG_PROC)
    image = {'image': open(bestand, 'rb')}

    r = requests.post(url, files=image)

    brightness = r.json()["brightness"]
    if brightness < 90:         # 50 is arbitrair gekozen
        return False, None

    # If all OK:
    return True, bestand


def convert_image(image_set):
    """
    process list of images into an averaged frame,
    embedding the date/time from the first image

    Ideas from:
    https://jdhao.github.io/2020/04/12/build_webapi_with_flask_s2/
    """

    # Open each image to a list, to be send to image_processor_server
    images = [('image', open('{}/{}'.format(folder, filename), 'rb'))
              for folder, filename in image_set]

    # Request to image processor
    url = '{}/average'.format(IMG_PROC)
    r = requests.post(url, files=images)

    # Save the processed image
    result_filename = image_set[0][1].replace('.jpg', '.png')
    with open('processed_{}/{}'.format(image_set[0][0], result_filename), 'wb') as f:
        f.write(r.content)


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
    command.append("-i 'processed_{}/*.png'".format(folder, HOW_MUCH))

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
        image_ok, glob.glob('{}/*.jpg'.format(folder)), chunksize=1)

    # Now put images to process in a new list
    images = [os.path.split(file) for flag, file in images_checked if flag]

    # Sort by number (2nd field in 'images')
    images.sort(key=lambda item: item[1])

    # Determine which images to process
    # Make slices for each image to process, each including
    # which images to use in the averaged frame
    frames_needed = 60 * framerate + HOW_MUCH  # Now 60 seconds of animation
    step_size = max(int(round(len(images) / frames_needed)), 1)
    print("Amount of raw images: {}".format(len(images_checked)))
    print("Amount of frames available: {}".format(len(images)))
    print("Amount of frames needed: {}".format(frames_needed))
    print("Step size: {}".format(step_size))

    # Make a new list of images, which does not contain skipped images
    selected_images = []
    for i in range(0, len(images), step_size):
        selected_images.append(images[i])
    print("Amount of selected images: {}".format(len(selected_images)))

    slices = [selected_images[i:i + HOW_MUCH]
              for i, _ in enumerate(selected_images)]

    # Create folder for processed images
    directory = 'processed_{}'.format(folder)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Clear all old images
    old_files = glob.glob('{}/*.png'.format(directory))
    for f in old_files:
        os.remove(f)

    # Process images
    print("Start converting images for selected images...")
    # Only for testing below:
    # convert_image(slices[0])

    # Single threaded, no feedback
    # for slice in slices:
    #     convert_image(slice)

    # Multi process, using feedback tqdm
    process_map(convert_image, slices, chunksize=4)

    # Use images for timelapse video
    print("Invoking ffmpeg to process images into video...")
    make_movie(folder, framerate)

    print("All done...")


if __name__ == "__main__":
    main('test', 10)
    main('img', 20)
    main('img_cam2', 20)
