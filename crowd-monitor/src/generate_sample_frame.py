"""
Sample Frame & Snapshot Generator
Generates realistic annotated camera frames with zone polygons, bounding boxes,
and timestamp watermarks. Writes atomically to prevent partial-read artifacts.
"""

import os
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont

def generate_annotated_frame(output_path: str, is_alert: bool = False, frame_title: str = "CAM-01 [NORTH GATE]"):
    """Creates a high-contrast tactical annotated frame and writes it atomically."""
    width, height = 1280, 720
    # Create dark surveillance hall canvas
    img = Image.new("RGB", (width, height), color=(18, 24, 38))
    draw = ImageDraw.Draw(img)

    # Draw architectural floor grid lines
    for x in range(0, width, 80):
        draw.line([(x, 0), (x, height)], fill=(28, 38, 55), width=1)
    for y in range(0, height, 80):
        draw.line([(0, y), (width, y)], fill=(28, 38, 55), width=1)

    # Zones definition
    zones = [
        {"id": "Z1", "name": "Security Check", "pts": [(50, 320), (420, 310), (430, 690), (40, 700)], "color": (239, 68, 68) if is_alert else (6, 182, 212), "count": 52 if is_alert else 38},
        {"id": "Z2", "name": "Escalator Lobby", "pts": [(440, 280), (790, 275), (780, 680), (450, 685)], "color": (245, 158, 11), "count": 34},
        {"id": "Z3", "name": "East Corridor", "pts": [(810, 250), (1240, 240), (1250, 670), (800, 675)], "color": (16, 185, 129), "count": 28},
        {"id": "Z4", "name": "Concourse", "pts": [(380, 100), (860, 95), (840, 260), (400, 265)], "color": (16, 185, 129), "count": 14}
    ]

    for z in zones:
        pts = z["pts"]
        col = z["color"]
        # Draw polygon boundary
        draw.polygon(pts, outline=col, width=3)
        # Draw translucent fill effect by hatching
        cx = sum(p[0] for p in pts) // len(pts)
        cy = sum(p[1] for p in pts) // len(pts)
        draw.rectangle([(cx - 70, cy - 25), (cx + 70, cy + 25)], fill=(11, 15, 23), outline=col, width=2)
        draw.text((cx - 60, cy - 18), f"{z['id']}: {z['name']}", fill=(255, 255, 255))
        draw.text((cx - 60, cy + 2), f"EST: ~{z['count']} pers", fill=col)

    # Draw synthetic detected person bounding boxes
    sample_bboxes = [
        (120, 480, 155, 560), (180, 420, 215, 500), (240, 510, 275, 590),
        (310, 460, 345, 540), (370, 520, 405, 600), (520, 390, 555, 470),
        (610, 440, 645, 520), (720, 360, 755, 440), (880, 380, 915, 460),
        (1020, 420, 1055, 500), (1140, 390, 1175, 470)
    ]
    for b in sample_bboxes:
        draw.rectangle(b, outline=(34, 211, 238), width=2)
        # Dot at feet (centroid bottom)
        feet_x = (b[0] + b[2]) // 2
        feet_y = b[3]
        draw.ellipse([(feet_x - 3, feet_y - 3), (feet_x + 3, feet_y + 3)], fill=(239, 68, 68))

    # Tactical HUD Watermark in corner
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " UTC"
    draw.rectangle([(15, 15), (420, 75)], fill=(11, 15, 23, 220), outline=(56, 189, 248), width=1)
    draw.text((25, 22), f"LIVE TELEMETRY // {frame_title}", fill=(6, 182, 212))
    draw.text((25, 40), f"TIMESTAMP: {now_utc}", fill=(248, 250, 252))
    draw.text((25, 55), "AI HYBRID INFERENCE: YOLOv8s + DM-Count (ACTIVE)", fill=(16, 185, 129))

    # Crosshair HUD marks
    draw.line([(width//2 - 20, height//2), (width//2 + 20, height//2)], fill=(56, 189, 248), width=1)
    draw.line([(width//2, height//2 - 20), (width//2, height//2 + 20)], fill=(56, 189, 248), width=1)

    # Atomic write pattern: save to temp then replace
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_file.with_suffix(".tmp.jpg")
    img.save(tmp_path, "JPEG", quality=85)
    if os.path.exists(out_file):
        os.remove(out_file)
    os.rename(tmp_path, out_file)

if __name__ == "__main__":
    base = Path(__file__).resolve().parent.parent / "data" / "outputs"
    generate_annotated_frame(str(base / "latest_annotated.jpg"))
    generate_annotated_frame(str(base / "snapshots" / "alert_101_sample.jpg"), is_alert=True)
    print("Sample tactical frames generated.")
