#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAP_DIR="${RADAR_MAP_DIR:-${PROJECT_DIR}/runtime-data/maps}"
MAP_FILE="${MAP_DIR}/demo-firenze.pmtiles"
MAP_URL='https://pmtiles.io/protomaps(vector)ODbL_firenze.pmtiles'
EXPECTED_SHA256='7190f3d807a62f4f012b574007c96b809f6842f45a6b0c508639331fc68fd30a'

mkdir -p "${MAP_DIR}"

if [[ -f "${MAP_FILE}" ]]; then
  CURRENT_SHA256="$(shasum -a 256 "${MAP_FILE}" | awk '{print $1}')"
  if [[ "${CURRENT_SHA256}" == "${EXPECTED_SHA256}" ]]; then
    echo "Radar demo map is ready: ${MAP_FILE}"
    exit 0
  fi
fi

TEMP_FILE="$(mktemp "${MAP_DIR}/demo-firenze.pmtiles.XXXXXX")"
trap 'rm -f "${TEMP_FILE}"' EXIT

curl --fail --location --silent --show-error "${MAP_URL}" --output "${TEMP_FILE}"
ACTUAL_SHA256="$(shasum -a 256 "${TEMP_FILE}" | awk '{print $1}')"

if [[ "${ACTUAL_SHA256}" != "${EXPECTED_SHA256}" ]]; then
  echo "Radar demo map checksum mismatch" >&2
  exit 1
fi

mv "${TEMP_FILE}" "${MAP_FILE}"
trap - EXIT
echo "Radar demo map downloaded: ${MAP_FILE}"
