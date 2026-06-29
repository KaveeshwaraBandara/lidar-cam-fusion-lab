#!/usr/bin/env bash
set -euo pipefail
DEST="${1:-data/kitti_sample}"
TMP="$(mktemp -d)"
REPO="https://github.com/azureology/kitti-velo2cam.git"
FRAME="000007"
echo "Cloning KITTI sample frame ${FRAME} ..."
git clone --depth 1 "${REPO}" "${TMP}/repo" >/dev/null 2>&1
mkdir -p "${DEST}/image_2" "${DEST}/velodyne" "${DEST}/calib"
cp "${TMP}/repo/data_object_image_2/testing/image_2/${FRAME}.png" "${DEST}/image_2/"
cp "${TMP}/repo/data_object_velodyne/testing/velodyne/${FRAME}.bin" "${DEST}/velodyne/"
cp "${TMP}/repo/testing/calib/${FRAME}.txt" "${DEST}/calib/"
rm -rf "${TMP}"
echo "Done. Sample frame at ${DEST}/"
