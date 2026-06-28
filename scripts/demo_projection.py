#!/usr/bin/env python3
"""
demo_projection.py — Phase 3 + Phase 4 end-to-end on a single KITTI frame.

Day-one runnable target. Given an image, a velodyne scan, and a calib file,
it will:
  1. project the LiDAR cloud onto the image (Phase 3),
  2. run YOLO 2D detection (Phase 1),
  3. fuse via frustum association (Phase 4),
  4. save two annotated images to outputs/.

Usage:
    python scripts/demo_projection.py \
        --image data/kitti/.../image_2/000010.png \
        --velo  data/kitti/.../velodyne/000010.bin \
        --calib data/kitti/.../calib/000010.txt

If --no-detect is passed, only the projection overlay is produced (so you can
verify calibration before pulling YOLO weights).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running from repo root without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "fusion_lab"))

import cv2  # noqa: E402

from fusion_lab import KittiFrame  # noqa: E402
from fusion_lab.visualization import draw_fused_objects, draw_projected_points  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--velo", required=True)
    ap.add_argument("--calib", required=True)
    ap.add_argument("--outdir", default="outputs")
    ap.add_argument("--no-detect", action="store_true",
                    help="skip YOLO; only render the projection overlay")
    args = ap.parse_args()

    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)

    frame = KittiFrame.load(args.image, args.velo, args.calib)
    print(f"Loaded image {frame.width}x{frame.height}, "
          f"{frame.points.shape[0]} LiDAR points")

    # --- Phase 3: projection overlay ---------------------------------------
    uv, depth, _ = frame.calib.points_in_image_fov(
        frame.points, frame.width, frame.height
    )
    print(f"{uv.shape[0]} points fall inside the image FoV")
    overlay = draw_projected_points(frame.image, uv, depth)
    cv2.imwrite(str(out / "projection.png"), overlay)
    print(f"  -> wrote {out / 'projection.png'}")

    if args.no_detect:
        return

    # --- Phase 1 + 4: detect then fuse -------------------------------------
    from fusion_lab import YoloDetector, frustum_association

    detector = YoloDetector()
    detections = detector.detect(frame.image)
    print(f"YOLO found {len(detections)} detections")

    fused = frustum_association(
        frame.points, detections, frame.calib, frame.width, frame.height
    )
    print(f"Fused {len(fused)} objects with 3D positions:")
    for o in fused:
        d = (o.centroid_velo**2).sum() ** 0.5
        print(f"  {o.label:12s} score={o.score:.2f} "
              f"dist={d:5.1f}m pts={o.num_points}")

    annotated = draw_fused_objects(frame.image, fused, frame.calib)
    cv2.imwrite(str(out / "fused.png"), annotated)
    print(f"  -> wrote {out / 'fused.png'}")


if __name__ == "__main__":
    main()
