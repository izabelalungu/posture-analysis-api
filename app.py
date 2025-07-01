from flask import Flask, request, send_file
from flask_cors import CORS
from PIL import Image, ImageDraw
import io

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze_image():
    img = Image.open(request.files['file'])
    draw = ImageDraw.Draw(img)
    # Exemplu simplu: linie pe diagonală
    draw.line((0, 0) + img.size, fill="red", width=5)
    # Poți adăuga aici griduri/unghiuri...

    img_io = io.BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

if __name__ == "__main__":
    app.run()
