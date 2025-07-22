from flask import Flask, render_template, request, send_file
import os
from stegoutil import Steganography  # ✅ Corrected import

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
    password = request.form['password']
    
    image_path = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(image_path)

    output_path = os.path.join(UPLOAD_FOLDER, 'encoded_' + image.filename)
    
    # ✅ Use class method
    Steganography.encode_message(image_path, message, password, output_path)

    return send_file(output_path, as_attachment=True)

@app.route('/decode', methods=['POST'])
def decode():
    image = request.files['stego_image']
    password = request.form['password']
    
    image_path = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(image_path)

    try:
        # ✅ Use class method
        hidden_message = Steganography.decode_message(image_path, password)
        return f"<h2>Hidden Message:</h2><p>{hidden_message}</p>"
    except ValueError as e:
        return f"<h2>Error:</h2><p>{str(e)}</p>"
    



if __name__ == '__main__':
    app.run(debug=True)
