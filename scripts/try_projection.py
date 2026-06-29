#!/usr/bin/env python3
"""
try_projection.py — Phase 2 + Phase 3 together.

Clusters the LiDAR cloud (Phase 2), then projects each cluster's points onto
the camera image (Phase 3), drawing each cluster in its own color. This is the
"aha" view: 3D object proposals landing on the 2D photo, no camera detection
involved yet.

Usage:
    python3 scripts/try_projection.py \
        --image data/synthetic/image_2/000000.png \
        --velo  data/synthetic/velodyne/000000.bin \
        --calib data/synthetic/calib/000000.txt
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "fusion_lab"))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from fusion_lab import (  # noqa: E402
    KittiFrame,
    cluster_dbscan,
    crop_range,
    remove_ground_ransac,
)

PALETTE = [
    (60, 60, 230), (230, 150, 30), (60, 200, 80),
    (30, 160, 230), (180, 50, 230), (230, 50, 150),
    (200, 200, 30), (50, 220, 220),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--velo", required=True)
    ap.add_argument("--calib", required=True)
    ap.add_argument("--out", default="cluster_projection.png")
    args = ap.parse_args()

    frame = KittiFrame.load(args.image, args.velo, args.calib)
    print(f"Image {frame.width}x{frame.height}, {frame.points.shape[0]} points")

    # Phase 2: cluster
    cropped = crop_range(frame.points)
    non_ground, _ = remove_ground_ransac(cropped)
    clusters = cluster_dbscan(non_ground)
    print(f"Phase 2 found {len(clusters)} clusters")

    canvas = cv2.cvtColor(frame.image, cv2.COLOR_RGB2BGR).copy()

    # Phase 3: project each cluster's points onto the image
    for i, c in enumerate(clusters):
        color = PALETTE[i % len(PALETTE)]
        # c.points is (n, 3); project needs the same velo frame
        uv, depth = frame.calib.project_velo_to_image(c.points)
        # keep only those landing inside the image
        inside = (
            (uv[:, 0] >= 0) & (uv[:, 0] < frame.width)
            & (uv[:, 1] >= 0) & (uv[:, 1] < frame.height)
        )
        uv = uv[inside]
        for u, v in uv.astype(int):
            cv2.circle(canvas, (u, v), 3, color, -1)

        # label the cluster at its mean pixel
        if len(uv) > 0:
            cu, cv_ = uv.mean(axis=0).astype(int)
            dist = float(np.linalg.norm(c.centroid))
            cv2.putText(canvas, f"#{i} {dist:.0f}m", (cu, cv_),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        print(f"  cluster {i}: {len(uv)} of {c.size} points landed in image")

    cv2.imwrite(args.out, canvas)
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()