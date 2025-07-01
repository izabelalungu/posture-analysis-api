from flask import Flask, request, send_file
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)
CORS(app)

def draw_posture_grid(img):
    draw = ImageDraw.Draw(img)
    w, h = img.size

    # Setări grid
    num_vert_lines = 8
    num_horiz_lines = 8
    color_grid = (160, 160, 160)
    color_align = (0, 200, 0)
    width_grid = 2

    # Desenează linii verticale grid
    for i in range(num_vert_lines+1):
        x = i * w // num_vert_lines
        draw.line([(x, 0), (x, h)], fill=color_grid, width=width_grid)
    
    # Desenează linii orizontale grid
    for i in range(num_horiz_lines+1):
        y = i * h // num_horiz_lines
        draw.line([(0, y), (w, y)], fill=color_grid, width=width_grid)
    
    # Linie verticală de aliniere (centrală)
    draw.line([(w//2, 0), (w//2, h)], fill=(0, 255, 0), width=4)
    
    # Exemplu: linii orizontale pentru "ears", "shoulders" etc.
    # Poziții hardcodate pe grid (ca demo, le poți ajusta)
    sections = ["Ears", "Shoulders", "ASIS", "Knees", "Feet"]
    font = None
    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except:
        font = ImageFont.load_default()

    label_y = [h//10, h//4, h//2, h*3//4, h-30]
    for label, y in zip(sections, label_y):
        draw.line([(0, y), (w, y)], fill=(0, 255, 255), width=3)
        draw.text((10, y-20), label, fill=(0, 0, 255), font=font)

    return img

@app.route('/analyze', methods=['POST'])
def analyze_image():
    img = Image.open(request.files['file']).convert("RGB")
    img = draw_posture_grid(img)
    img_io = io.BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

if __name__ == "__main__":
    app.run()
