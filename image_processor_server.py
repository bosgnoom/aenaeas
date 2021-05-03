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

from flask import Flask, request, jsonify
from PIL import Image, ImageStat

app = Flask(__name__)


@app.route("/brightness", methods=["POST"])
def process_image():
    file = request.files['image']
    # Read the image via file.stream
    img = Image.open(file.stream).convert('L')
    stat = ImageStat.Stat(img)
    brightness = stat.mean[0]

    return jsonify({'msg': 'success', 'brightness': brightness})


if __name__ == "__main__":
    app.run(debug=True)
