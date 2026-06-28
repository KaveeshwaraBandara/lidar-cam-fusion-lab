#!/usr/bin/env bash
# =============================================================================
# download_kitti.sh — fetch a small slice of KITTI for the demos.
#
# KITTI requires accepting their terms; we don't bundle data. This script
# pulls the object-detection mini sample (left color images, velodyne, calib)
# which is enough for Phases 1-4.
#
# Usage: scripts/download_kitti.sh
# Data lands in data/kitti/ (git-ignored).
# =============================================================================
set -euo pipefail

DATA_DIR="${1:-data/kitti}"
mkdir -p "$DATA_DIR"

cat <<'EOF'
-------------------------------------------------------------------------------
KITTI is not redistributed here. To get the data:

1. Register / accept terms at:
     https://www.cvlibs.net/datasets/kitti/eval_object.php?obj_benchmark=3d

2. Download these three zips from the "Object" benchmark (left color):
     - data_object_image_2.zip   (left color images)
     - data_object_velodyne.zip  (Velodyne point clouds)
     - data_object_calib.zip     (calibration)

3. Unzip them so you end up with:
     data/kitti/training/image_2/000000.png ...
     data/kitti/training/velodyne/000000.bin ...
     data/kitti/training/calib/000000.txt ...

Then run:
     python scripts/demo_projection.py \
       --image data/kitti/training/image_2/000010.png \
       --velo  data/kitti/training/velodyne/000010.bin \
       --calib data/kitti/training/calib/000010.txt

TIP: Until you have KITTI, use the synthetic frame instead:
     python scripts/make_synthetic_frame.py
     python scripts/demo_projection.py \
       --image data/synthetic/image_2/000000.png \
       --velo  data/synthetic/velodyne/000000.bin \
       --calib data/synthetic/calib/000000.txt --no-detect
-------------------------------------------------------------------------------
EOF
