def analyze_pose(img):
    import math
    import numpy as np
    import mediapipe as mp
    import cv2
    from PIL import ImageDraw, ImageFont

    img_np = np.array(img)
    img_rgb = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True)
    results = pose.process(img_rgb)

    draw = ImageDraw.Draw(img)
    w, h = img.size

    # Grid (rămâne la fel)
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

    def get_angle(p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        radians = math.atan2(y2 - y1, x2 - x1)
        degrees = math.degrees(radians)
        angle = 90 - degrees
        if angle > 180:
            angle -= 360
        if angle < -180:
            angle += 360
        return round(angle, 1)

    if results.pose_landmarks:
        idxs = {
            "Shoulders": (11, 12), # L, R
            "ASIS": (23, 24),
            "Knees": (25, 26),
            "Feet": (27, 28),
        }
        colors = {"Shoulders": (255,0,0), "ASIS": (0,128,255), "Knees": (0,255,128), "Feet": (255,128,0)}
        try:
            font = ImageFont.truetype("arial.ttf", 32)
        except:
            font = ImageFont.load_default()

        for name, (left_idx, right_idx) in idxs.items():
            left = results.pose_landmarks.landmark[left_idx]
            right = results.pose_landmarks.landmark[right_idx]
            p1 = (int(left.x * w), int(left.y * h))
            p2 = (int(right.x * w), int(right.y * h))

            # ---- LINIA DE REFERINȚĂ (ALBĂ, SUBȚIRE) ----
            # între punctele de la mijlocul imaginii (verticală)
            ref_x = w // 2
            ref_p1 = (ref_x, p1[1])
            ref_p2 = (ref_x, p2[1])
            draw.line([ref_p1, ref_p2], fill=(255,255,255), width=2)  # linie albă

            # ---- LINIA ACTUALĂ (COLORATĂ, MAI SUBȚIRE) ----
            draw.line([p1, p2], fill=colors[name], width=4)

            # ---- Puncte (opțional) ----
            r = 8
            draw.ellipse([p1[0]-r, p1[1]-r, p1[0]+r, p1[1]+r], fill=colors[name])
            draw.ellipse([p2[0]-r, p2[1]-r, p2[0]+r, p2[1]+r], fill=colors[name])

            # ---- UNGHI FAȚĂ DE LINIA DE REFERINȚĂ ----
            angle = get_angle(p1, p2)
            y_label = int((p1[1] + p2[1]) // 2)
            txt = f"{abs(angle):.0f}°"
            # Afișează unghiul în dreptul liniei, text mare
            draw.text((ref_x + 25, y_label - 22), txt, fill=(0,0,0), font=font, stroke_width=2, stroke_fill=(255,255,255))

    else:
        draw.text((w//2-100, 20), "Nicio postură detectată!", fill=(255,0,0), font=ImageFont.load_default())

    return img
