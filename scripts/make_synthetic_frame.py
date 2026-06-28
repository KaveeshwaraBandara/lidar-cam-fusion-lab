#!/usr/bin/env python3
"""
make_synthetic_frame.py — generate a tiny synthetic KITTI-format frame.

Lets you smoke-test the projection math WITHOUT downloading any dataset:
creates a blank image, a calib file with sane KITTI-like matrices, and a
.bin point cloud containing a few "objects" (point blobs) at known distances.

Useful in CI and on day one before the KITTI download finishes.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image

# A representative KITTI cam2 projection + identity-ish rectification +
# a plausible velo->cam transform (90-degree-ish axis swap).
P2 = (
    "P2: 7.215377e+02 0.000000e+00 6.095593e+02 4.485728e+01 "
    "0.000000e+00 7.215377e+02 1.728540e+02 2.163791e-01 "
    "0.000000e+00 0.000000e+00 1.000000e+00 2.745884e-03"
)
R0 = (
    "R0_rect: 9.999239e-01 9.837760e-03 -7.445048e-03 "
    "-9.869795e-03 9.999421e-01 -4.278459e-03 "
    "7.402527e-03 4.351614e-03 9.999631e-01"
)
TR = (
    "Tr_velo_to_cam: 7.533745e-03 -9.999714e-01 -6.166020e-04 -4.069766e-03 "
    "1.480249e-02 7.280733e-04 -9.998902e-01 -7.631618e-02 "
    "9.998621e-01 7.523790e-03 1.480755e-02 -2.717806e-01"
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="data/synthetic")
    args = ap.parse_args()
    out = Path(args.outdir)
    (out / "image_2").mkdir(parents=True, exist_ok=True)
    (out / "velodyne").mkdir(parents=True, exist_ok=True)
    (out / "calib").mkdir(parents=True, exist_ok=True)

    # Image (KITTI-ish size).
    Image.fromarray(
        np.full((375, 1242, 3), 30, dtype=np.uint8)
    ).save(out / "image_2" / "000000.png")

    # Calib.
    (out / "calib" / "000000.txt").write_text("\n".join([P2, R0, TR]) + "\n")

    # Point cloud: ground plane + three blobs ahead of the LiDAR.
    rng = np.random.default_rng(0)
    ground = np.column_stack([
        rng.uniform(2, 30, 4000),
        rng.uniform(-8, 8, 4000),
        np.full(4000, -1.6) + rng.normal(0, 0.02, 4000),
        rng.uniform(0, 0.3, 4000),
    ])
    blobs = []
    for cx, cy in [(8, 0), (15, -3), (22, 4)]:
        b = np.column_stack([
            rng.normal(cx, 0.4, 600),
            rng.normal(cy, 0.4, 600),
            rng.uniform(-1.5, 0.2, 600),
            rng.uniform(0, 1, 600),
        ])
        blobs.append(b)
    cloud = np.vstack([ground, *blobs]).astype(np.float32)
    cloud.tofile(out / "velodyne" / "000000.bin")

    print(f"Synthetic frame written under {out}/")
    print(f"  image:  {out}/image_2/000000.png")
    print(f"  velo:   {out}/velodyne/000000.bin  ({cloud.shape[0]} pts)")
    print(f"  calib:  {out}/calib/000000.txt")


if __name__ == "__main__":
    main()
