#!/usr/bin/python3
"""
    Server side program,

    end points:
    - brightness: calculates the brightness of an image
    - average: calulates the averaged image of given set of images

    depends on:
    - flask: pip install flask
    - PIL (Pillow)
    
"""

from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageStat, ImageFont, ImageDraw
import numpy as np
from io import BytesIO
import datetime


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


@app.route("/brightness", methods=["POST"])
def process_image():
    file = request.files['image']
    # Read the image via file.stream
    img = Image.open(file.stream)

    # Try to detect if the image is black and white
    v = ImageStat.Stat(img).var
    diff = max(v) - min(v)

    # High values = color image,
    # Low values (0.0?) = black and white image
    if diff > 1000:
        # Color image

        # Now convert to only lightness (L) and
        # calculate average (=brightness)
        stat = ImageStat.Stat(img.convert('L'))
        brightness = stat.mean[0]

        return jsonify({'msg': 'success', 'brightness': brightness})
        
    # Always return something
    return jsonify({'msg': 'success', 'brightness': 0})


@app.route("/average", methods=["POST"])
def process_images():
    # Calculate averaged image
    # Based on input from: https://stackoverflow.com/questions/17291455/how-to-get-an-average-picture-from-100-pictures-using-pil

    # Get list of uploaded images
    files = request.files.getlist('image')
    
    # Get first image's filename
    result_name = files[0].filename
    app.logger.info("Processing: {}".format(result_name))

    # To determine the timestamp, take the first image name and remove its file extension
    timestamp = result_name.split('.')[0]

    # Return images as PNG
    result_name = f'{timestamp}.png'

    # Empty array to store image
    arr = np.zeros(shape=(720, 1280, 3))

    # Loop over each file, store in array created above
    for f in files:
        # Open image
        img = Image.open(f.stream)

        # Check if image needs to be resized
        if img.size != (1280, 720):
            # Resize is needed

            # First, crop image
            width, _ = img.size      # tuple width, height
            new_height = int((9 * width) / 16)
            img_crop = img.crop((0, 0, width, new_height))

            # Second, resize image
            img = img_crop.resize((1280, 720), Image.ANTIALIAS)

        # Stack images
        arr = arr + np.array(img)

    # Reduce arr to normal color levels, by dividing through amount of images
    img_avg = np.array(arr / len(files), dtype=np.uint8)

    # Convert array to an image
    img_avg = Image.fromarray(img_avg)

    # Embed timestamp in image
    tijdstip = datetime.datetime.strptime(
        timestamp, "%Y-%m-%d_%H%M").strftime('%d-%m-%Y %H:%M')
    font = ImageFont.truetype('OpenSans-Regular.ttf', 20)
    d1 = ImageDraw.Draw(img_avg)
    d1.text((1120, 694), tijdstip, font=font, fill=(255, 255, 255))

    # Prepare to send the image back to client
    app.logger.debug('Send image back to client')
    # Use BytesIO to "write" image to, seek back to start
    # in order to "read" the file for sending
    img_byte_arr = BytesIO()
    img_avg.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return send_file(img_byte_arr,
                     mimetype='image/png',
                     attachment_filename=result_name,
                     as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8000)
