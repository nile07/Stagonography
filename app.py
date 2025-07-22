from flask import Flask, render_template, request, send_file
import os
from stegoutil import encode_message, decode_message

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encode', methods=['POST'])
def encode():
    image = request.files['image']
    message = request.form['message']
    image_path = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(image_path)

    output_path = os.path.join(UPLOAD_FOLDER, 'encoded_' + image.filename)
    encode_message(image_path, message, output_path)

    return send_file(output_path, as_attachment=True)

@app.route('/decode', methods=['POST'])
def decode():
    image = request.files['stego_image']
    image_path = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(image_path)

    hidden_message = decode_message(image_path)
    return f"<h2>Hidden Message:</h2><p>{hidden_message}</p>"

if __name__ == '__main__':
    app.run(debug=True)
