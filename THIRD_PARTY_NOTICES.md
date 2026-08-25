# Third-Party Notices

## FastAPI Full Stack Template

- Upstream: <https://github.com/fastapi/full-stack-fastapi-template>
- Pinned commit: `162344da111e833b30892728372ab95331f06873`
- Snapshot date: 2026-08-18
- License: MIT; preserved at `third_party/licenses/fastapi-template-MIT.txt`
- Imported paths: backend, frontend, root workspace manifests, Docker Compose skeleton, and selected test/client scripts
- Excluded: upstream Git history, `.agents`, cloud deployment files, editor settings, images, release tooling, and `.env` files

The imported template is used as an engineering scaffold. MiniWorld's product intent, privacy constraints, and implementation authority come from this repository's `goal.md` and `AGENTS.md`.

## Local Job Radar Stack

- MapLibre GL JS `6.4.1` — <https://maplibre.org/> — BSD-3-Clause.
- PMTiles JavaScript `4.5.0` — <https://github.com/protomaps/PMTiles> — BSD-3-Clause.
- Protomaps Basemaps `5.7.2` — <https://github.com/protomaps/basemaps> — BSD-3-Clause.
- Tauri JavaScript API `2.11.1`, CLI `2.11.4`, Rust `tauri 2.11.3` and `tauri-build 2.6.3` — <https://tauri.app/> — Apache-2.0 OR MIT.
- Firenze demonstration PMTiles — OpenStreetMap-derived public map data; © OpenStreetMap contributors, licensed under ODbL. The runtime file is downloaded by checksum-verified script and remains outside Git.

The radar never uses the OpenStreetMap Foundation standard tile service. It reads the local PMTiles package through a localhost Range endpoint and keeps visible OpenStreetMap attribution in the window.
