"""Tests for the projection math and association helpers.

These run without any dataset download (they build matrices inline), so they
work in CI. Run: pytest -q
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "fusion_lab"))

from fusion_lab.association_utils import iou_2d, hungarian_match  # noqa: E402
from fusion_lab.calibration import Calibration  # noqa: E402


def _make_calib(tmp_path: Path) -> Calibration:
    text = (
        "P2: 7.215377e+02 0 6.095593e+02 0 "
        "0 7.215377e+02 1.728540e+02 0 "
        "0 0 1 0\n"
        "R0_rect: 1 0 0 0 1 0 0 0 1\n"
        "Tr_velo_to_cam: 0 -1 0 0  0 0 -1 0  1 0 0 0\n"
    )
    p = tmp_path / "calib.txt"
    p.write_text(text)
    return Calibration.from_kitti(p)


def test_calib_loads(tmp_path):
    calib = _make_calib(tmp_path)
    assert calib.P_rect.shape == (3, 4)
    assert calib.R0_rect.shape == (4, 4)
    assert calib.Tr_velo_to_cam.shape == (4, 4)


def test_point_in_front_projects_inside(tmp_path):
    calib = _make_calib(tmp_path)
    # A point 10m ahead, centered -> should land near the principal point.
    pt = np.array([[10.0, 0.0, 0.0, 1.0]])
    uv, depth = calib.project_velo_to_image(pt)
    assert uv.shape == (1, 2)
    assert depth[0] > 0
    # principal point is (609.5, 172.8); centered point should be close in u.
    assert abs(uv[0, 0] - 609.5) < 1.0


def test_point_behind_is_dropped(tmp_path):
    calib = _make_calib(tmp_path)
    behind = np.array([[-10.0, 0.0, 0.0, 1.0]])  # behind the LiDAR
    uv, depth = calib.project_velo_to_image(behind)
    assert uv.shape[0] == 0  # nothing in front


def test_fov_mask_roundtrip(tmp_path):
    calib = _make_calib(tmp_path)
    pts = np.array([
        [10.0, 0.0, 0.0, 1.0],     # in front, central -> inside
        [-5.0, 0.0, 0.0, 1.0],     # behind -> outside
        [10.0, 50.0, 0.0, 1.0],    # far to the side -> outside FoV
    ])
    uv, depth, mask = calib.points_in_image_fov(pts, 1242, 375)
    assert mask[0]
    assert not mask[1]
    assert uv.shape[0] == mask.sum()


def test_iou():
    a = np.array([0, 0, 10, 10])
    b = np.array([5, 5, 15, 15])
    assert abs(iou_2d(a, b) - (25 / 175)) < 1e-6
    assert iou_2d(a, np.array([20, 20, 30, 30])) == 0.0


def test_hungarian_identity():
    cost = np.array([[0.1, 0.9], [0.9, 0.1]])
    rows, cols = hungarian_match(cost)
    pairs = dict(zip(rows.tolist(), cols.tolist()))
    assert pairs[0] == 0 and pairs[1] == 1
