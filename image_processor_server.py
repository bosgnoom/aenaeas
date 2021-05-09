#!/usr/bin/python3
"""
    Server side program,

    end points:
    - brightness: calculates the brightness of an image
    - average: calulates the averaged image of given set of images

    depends on:
    - flask: pip install flask
    - PIL
    
"""

from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageStat
import numpy as np
from io import BytesIO


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


@app.route("/brightness", methods=["POST"])
def process_image():
    file = request.files['image']
    # Read the image via file.stream
    img = Image.open(file.stream).convert('L')
    stat = ImageStat.Stat(img)
    brightness = stat.mean[0]

    return jsonify({'msg': 'success', 'brightness': brightness})


@app.route("/average", methods=["POST"])
def process_images():
    # Calculate averaged image
    # Based on input from: https://stackoverflow.com/questions/17291455/how-to-get-an-average-picture-from-100-pictures-using-pil

    # Get list of uploaded images
    files = request.files.getlist('image')
    app.logger.info("Amount of images in list: {}".format(len(files)))

    # Empty array to store image
    arr = np.zeros(shape=(720, 1280, 3))

    # Get first image's filename
    result_name = files[0].filename
    app.logger.debug('Filename: {}'.format(result_name))

    # Loop over each file
    for f in files:
        # Open image
        img = Image.open(f.stream)

        # Check if image needs to be resized
        if img.size != (1280, 720):
            # Resize is needed

            # First, crop image
            width, _ = img.size
            new_height = int((16 * width) / 9)
            img = img.crop((0, 0, width, new_height))

            # Second, resize image
            img = img.resize((1280, 720), Image.ANTIALIAS)

        # Stack images
        arr = arr + np.array(img)

    # Reduce arr to normal color levels, by dividing through amount of images
    img_avg = np.array(arr / len(files), dtype=np.uint8)

    # From array to an image
    img_avg = Image.fromarray(img_avg)

    # Prepare to send the image back to client
    img_byte_arr = BytesIO()
    img_avg.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return send_file(img_byte_arr,
                     mimetype='image/png',
                     attachment_filename=result_name,
                     as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
