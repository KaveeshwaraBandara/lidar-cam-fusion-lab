#!/usr/bin/env python3
"""Minimal YOLO experiment — detect objects in any image and print them."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "fusion_lab"))

import cv2
from fusion_lab import YoloDetector

img_path = sys.argv[1] if len(sys.argv) > 1 else "test.jpg"
image = cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2RGB)

detector = YoloDetector(conf=0.35)
detections = detector.detect(image)

print(f"\nFound {len(detections)} objects in {img_path}:")
for d in detections:
    x1, y1, x2, y2 = d.bbox.astype(int)
    print(f"  {d.label:12s} conf={d.score:.2f}  box=({x1},{y1})-({x2},{y2})")

# draw and save
for d in detections:
    x1, y1, x2, y2 = d.bbox.astype(int)
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(image, f"{d.label} {d.score:.2f}", (x1, y1 - 6),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
cv2.imwrite("yolo_out.jpg", cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
print("\nAnnotated image -> yolo_out.jpg")
