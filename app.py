from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from rembg import remove
from PIL import Image, ImageOps
from PIL import ImageColor
import re
import os
import urllib.request
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)
app.secret_key = 'background'
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/file-upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        resp = jsonify({'message':'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message':'No file selected for uploading'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        input_file_path = app.config['UPLOAD_FOLDER']+filename
        input = Image.open(input_file_path)
        output = remove(input)
        output_file_name = 'static/uploads/'+filename+'_new.png'
        output.save(output_file_name)
        # Adding border of 10px around image
        output_file_path = output_file_name
        # Crop the image to the bounding box of the object
        bbox = output.getbbox()
        cropped_output = output.crop(bbox)
        # Add a border of 10px around the cropped image
        output_border_extended = ImageOps.expand(cropped_output, border=3, fill='black')
        output_extended_filename = 'static/uploads/'+filename+'_ext.png'
        output_border_extended.save(output_extended_filename)
        resp = jsonify({'message':'File successfully uploaded','image_url':output_extended_filename})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify({'message':'Allowed file types are png, jpg, jpeg, gif'})
        resp.status_code = 400
        return resp