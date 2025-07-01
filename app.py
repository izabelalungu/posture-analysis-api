from flask import Flask, request, send_file
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
import io
import cv2
import numpy as np
import mediapipe as mp
import math

app = Flask(__name__)
CORS(app)

def get_angle(p1, p2):
    # Calculează unghiul față de verticală (Ox)
    x1, y1 = p1
    x2, y2 = p2
    radians = math.atan2(y2 - y1, x2 - x1)
    degrees = math.degrees(radians)
    # Ajustează astfel încât 0° să fie pe verticală (sus-jos)
    angle = 90 - degrees
    if angle > 180:
        angle -= 360
    if angle < -180:
        angle += 360
    return round(angle, 1)

def analyze_pose(img):
    # Convertim PIL Image în numpy array pentru MediaPipe
    img_np = np.array(img)
    img_rgb = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True)
    results = pose.process(img_rgb)

    draw = ImageDraw.Draw(img)
    w, h = img.size

    # Desenează grid
    num_vert_lines = 8
    num_horiz_lines = 8
    color_grid = (160, 160, 160)
    width_grid = 2
    for i in range(num_vert_lines+1):
        x = i * w // num_vert_lines
        draw.line([(x, 0), (x, h)], fill=color_grid, width=width_grid)
    for i in range(num_horiz_lines+1):
        y = i * h // num_horiz_lines
        draw.line([(0, y), (w, y)], fill=color_grid, width=width_grid)
    # Linia verticală de mijloc
    draw.line([(w//2, 0), (w//2, h)], fill=(0, 255, 0), width=4)

    if results.pose_landmarks:
        # Extrage pozițiile pentru umeri, șolduri, genunchi, glezne
        idxs = {
            "shoulders": (11, 12), # L,R
            "hips": (23, 24),
            "knees": (25, 26),
            "feet": (27, 28),
        }
        colors = {"shoulders": (255,0,0), "hips": (0,128,255), "knees": (0,255,128), "feet": (255,128,0)}
        font = ImageFont.load_default()
        for name, (left_idx, right_idx) in idxs.items():
            left = results.pose_landmarks.landmark[left_idx]
            right = results.pose_landmarks.landmark[right_idx]
            # Convertire la coordonate imagine
            p1 = (int(left.x * w), int(left.y * h))
            p2 = (int(right.x * w), int(right.y * h))
            # Linie între puncte
            draw.line([p1, p2], fill=colors[name], width=5)
            # Puncte vizibile
            r = 10
            draw.ellipse([p1[0]-r, p1[1]-r, p1[0]+r, p1[1]+r], fill=colors[name])
            draw.ellipse([p2[0]-r, p2[1]-r, p2[0]+r, p2[1]+r], fill=colors[name])
            # Calculează unghiul față de verticală (linia verde)
            # Verticală centrală (w//2, 0)-(w//2, h)
            align_p1 = (w//2, p1[1])
            align_p2 = (w//2, p2[1])
            # Unghiul liniei reale față de verticală
            angle = get_angle(p1, p2)
            # Text cu nume și unghi
            y_label = int((p1[1]+p2[1])//2)
            txt = f"{name.title()}  {abs(angle)}°"
            draw.text((10, y_label-10), txt, fill=colors[name], font=font)
    else:
        draw.text((w//2-60, 20), "Nicio postură detectată!", fill=(255,0,0), font=ImageFont.load_default())

    return img

@app.route('/analyze', methods=['POST'])
def analyze_image():
    img = Image.open(request.files['file']).convert("RGB")
    img = analyze_pose(img)
    img_io = io.BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

if __name__ == "__main__":
    app.run()
