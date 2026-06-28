# lidar-cam-fusion-lab

A hands-on lab for learning **LiDAR + camera object association** from first
principles — detect objects in an image, find them in a point cloud, and fuse
the two so every object carries both a **semantic label** and a **3D position**.

Built to run entirely inside Docker (ROS 2 Jazzy / Ubuntu 24.04) so anyone can
`git clone` and run without fighting dependencies. Experiments use public
datasets (KITTI, nuScenes); the learnings are meant to port back to a real
robot (e.g. a Unitree Go2 with onboard LiDAR + camera).

> Status: scaffolding + a working Phase 3/4 demo on synthetic and KITTI data.
> This is a learning repo — code favours clarity over performance.

---

## Quickstart

```bash
# 1. Build the container (ROS 2 Jazzy + perception stack)
docker compose build

# 2. Allow the container to open GUI windows (RViz, Open3D), then start it
xhost +local:docker
docker compose up -d
docker compose exec fusion bash

# 3. Inside the container: smoke-test with a SYNTHETIC frame (no download)
python scripts/make_synthetic_frame.py
python scripts/demo_projection.py \
  --image data/synthetic/image_2/000000.png \
  --velo  data/synthetic/velodyne/000000.bin \
  --calib data/synthetic/calib/000000.txt --no-detect
# -> writes outputs/projection.png  (LiDAR points colored by depth on the image)

# 4. Run the tests
pytest tests/ -q
```

To use real data, see `scripts/download_kitti.sh`, then drop `--no-detect` to
run YOLO + frustum fusion end-to-end.

---

## The core idea (read this first)

Everything hinges on one transform chain — projecting a 3D LiDAR point into the
2D image. In KITTI convention:

```
X_cam   = Tr_velo_to_cam @ [X_velo; 1]   # LiDAR frame -> camera frame
X_rect  = R0_rect @ X_cam                # stereo rectification
x_img   = P_rect @ [X_rect; 1]           # project to homogeneous pixels
(u, v)  = x_img[:2] / x_img[2]           # normalize
```

`P_rect` already folds in the camera **intrinsics** (focal length, principal
point). `Tr_velo_to_cam` is the **extrinsic** calibration between the two
sensors. Get these right and association is mostly bookkeeping; get them wrong
and nothing downstream works. This logic lives in
[`src/fusion_lab/fusion_lab/calibration.py`](src/fusion_lab/fusion_lab/calibration.py).

---

## Roadmap

| Phase | Goal | Key files |
|------|------|-----------|
| **0** | Environment + coordinate frames | `docker/`, this README |
| **1** | Camera-only 2D detection (YOLO) | `detection.py` |
| **2** | LiDAR-only proposals (ground removal + clustering) | `lidar.py` |
| **3** | **Calibration & projection** (the heart) | `calibration.py`, `demo_projection.py` |
| **4** | Association (frustum + IoU/Hungarian) | `association.py` |
| **5** | Deep fusion (PointPainting / Frustum-PointNet) | _your reimplementations_ |
| **6** | Tracking over time (Kalman / SORT) | _uses `filterpy`_ |
| **7** | Port to live ROS 2 / Go2 | `ros2_ws/src/fusion_ros/` |

### Phase details

**Phase 0 — Foundations.** Learn the frames cold: LiDAR (x-fwd, y-left, z-up),
camera (x-right, y-down, z-fwd), the rigid transform between them, and the
intrinsics. Most fusion bugs are frame bugs.

**Phase 1 — Camera detection.** Run YOLO on images, understand boxes,
confidence, NMS. Output: labelled 2D boxes.

**Phase 2 — LiDAR processing.** RANSAC ground removal, DBSCAN/Euclidean
clustering, 3D box fitting. Output: unlabelled 3D clusters.

**Phase 3 — Projection.** Project the cloud onto the image and colour it by
depth. The single most important exercise — `demo_projection.py` does this.

**Phase 4 — Association.** Two strategies, both implemented:
- *Frustum:* project points into each 2D box, cluster, take the nearest
  cluster's centroid as the object's 3D position.
- *IoU matching:* detect in 3D and 2D independently, project 3D boxes to 2D,
  match with Hungarian assignment.

**Phase 5 — Deep fusion.** Reimplement pieces of PointPainting (paint points
with segmentation scores) or Frustum-PointNet. This is the real deep dive.

**Phase 6 — Tracking.** Add a Kalman filter so objects persist with stable IDs
across frames.

**Phase 7 — Live robot.** Wrap the pipeline in the ROS 2 node under
`ros2_ws/`, subscribe to real camera + LiDAR topics, calibrate real extrinsics,
run live.

---

## Datasets

Start with **KITTI** — it ships calibration files with every matrix
pre-computed, so it's the best teacher for Phase 3. Then graduate to
**nuScenes** (360° LiDAR, harder) and optionally **Waymo Open**.

Data is **never committed** (see `.gitignore`). Use `scripts/download_kitti.sh`
for instructions, or `scripts/make_synthetic_frame.py` to experiment with zero
download.

---

## Repository layout

```
.
├── docker/                 # Dockerfile, requirements, entrypoint
├── docker-compose.yml      # X11 GUI passthrough + optional GPU
├── .devcontainer/          # VS Code "Reopen in Container"
├── src/fusion_lab/         # the core Python package (framework-agnostic)
│   └── fusion_lab/
│       ├── calibration.py  # <- projection math (Phase 3)
│       ├── datasets.py     # KITTI loaders
│       ├── detection.py    # YOLO wrapper (Phase 1)
│       ├── lidar.py        # ground removal + clustering (Phase 2)
│       ├── association.py  # frustum + IoU fusion (Phase 4)
│       └── visualization.py
├── ros2_ws/src/fusion_ros/ # ROS 2 node stub (Phase 7)
├── scripts/                # demos + dataset helpers
├── tests/                  # dataset-free unit tests (run in CI)
├── notebooks/              # exploratory work
└── data/  weights/         # git-ignored, bind-mounted into the container
```

---

## GPU notes

YOLO + deep fusion want a GPU. The compose file has a commented `deploy:` block
for NVIDIA — uncomment it and install `nvidia-container-toolkit` on the host.
For a CUDA-specific torch build, override the torch wheel during image build.
CPU-only works for projection, clustering, and small-model YOLO inference.

---

## License

MIT — see [LICENSE](LICENSE).
