#!/usr/bin/env python3
"""
try_lidar.py — Phase 2 experiment: crop -> ground removal -> clustering.

Runs the full LiDAR-only pipeline on a .bin scan and opens an interactive
Open3D window. Ground points are gray, each cluster gets its own color, and
a box is drawn around every cluster.

Usage:
    python3 scripts/try_lidar.py data/synthetic/velodyne/000000.bin
    python3 scripts/try_lidar.py data/kitti/training/velodyne/000010.bin

Controls in the window: drag to rotate, scroll to zoom, 'q' to quit.

If you're running headless (no display), pass --no-show to skip the window
and just print cluster stats.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "fusion_lab"))

import numpy as np  # noqa: E402

from fusion_lab import (  # noqa: E402
    cluster_dbscan,
    crop_range,
    load_velodyne_bin,
    remove_ground_ransac,
)


# A few distinct colors to cycle through for clusters.
PALETTE = np.array([
    [0.9, 0.1, 0.1], [0.1, 0.6, 0.9], [0.1, 0.8, 0.3],
    [0.9, 0.6, 0.1], [0.7, 0.2, 0.9], [0.9, 0.2, 0.6],
    [0.2, 0.8, 0.8], [0.6, 0.8, 0.1],
])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("velo")
    ap.add_argument("--eps", type=float, default=0.5,
                    help="DBSCAN neighborhood radius (m)")
    ap.add_argument("--min-points", type=int, default=10,
                    help="DBSCAN min neighbors for a core point")
    ap.add_argument("--ground-thresh", type=float, default=0.2,
                    help="RANSAC ground distance threshold (m)")
    ap.add_argument("--no-show", action="store_true")
    args = ap.parse_args()

    # 1. Load
    points = load_velodyne_bin(args.velo)
    print(f"Loaded {points.shape[0]} points from {args.velo}")

    # 2. Crop to region of interest
    cropped = crop_range(points)
    print(f"After crop_range: {cropped.shape[0]} points")

    # 3. Remove ground
    non_ground, ground_mask = remove_ground_ransac(
        cropped, distance_threshold=args.ground_thresh
    )
    print(f"Ground points removed: {ground_mask.sum()}")
    print(f"Remaining (object) points: {non_ground.shape[0]}")

    # 4. Cluster
    clusters = cluster_dbscan(
        non_ground, eps=args.eps, min_points=args.min_points
    )
    print(f"\nFound {len(clusters)} clusters:")
    for i, c in enumerate(clusters):
        cx, cy, cz = c.centroid
        dist = float(np.linalg.norm(c.centroid))
        dims = c.bbox_max - c.bbox_min
        print(f"  cluster {i:2d}: {c.size:4d} pts  "
              f"center=({cx:5.1f},{cy:5.1f},{cz:5.1f})  "
              f"dist={dist:5.1f}m  size={dims[0]:.1f}x{dims[1]:.1f}x{dims[2]:.1f}m")

    if args.no_show:
        return

    # 5. Visualize
    import open3d as o3d

    geoms = []

    # Ground (gray)
    ground_pts = cropped[ground_mask][:, :3]
    g = o3d.geometry.PointCloud()
    g.points = o3d.utility.Vector3dVector(ground_pts)
    g.paint_uniform_color([0.6, 0.6, 0.6])
    geoms.append(g)

    # Each cluster in its own color + a bounding box
    for i, c in enumerate(clusters):
        color = PALETTE[i % len(PALETTE)]
        pc = o3d.geometry.PointCloud()
        pc.points = o3d.utility.Vector3dVector(c.points)
        pc.paint_uniform_color(color.tolist())
        geoms.append(pc)

        box = o3d.geometry.AxisAlignedBoundingBox(c.bbox_min, c.bbox_max)
        box.color = color.tolist()
        geoms.append(box)

    print("\nOpening Open3D window — drag to rotate, scroll to zoom, 'q' to quit.")
    o3d.visualization.draw_geometries(geoms)


if __name__ == "__main__":
    main()