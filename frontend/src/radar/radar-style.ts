import { DARK } from "@protomaps/basemaps"
import type { StyleSpecification } from "maplibre-gl"

const SOURCE_ID = "protomaps"

export function createRadarStyle(pmtilesUrl: string): StyleSpecification {
  return {
    version: 8,
    name: "MiniWorld Radar Dark",
    sources: {
      [SOURCE_ID]: {
        type: "vector",
        url: `pmtiles://${pmtilesUrl}`,
        attribution: "© OpenStreetMap contributors",
      },
    },
    layers: [
      {
        id: "radar-background",
        type: "background",
        paint: { "background-color": "#090b08" },
      },
      {
        id: "radar-earth",
        type: "fill",
        source: SOURCE_ID,
        "source-layer": "earth",
        paint: { "fill-color": DARK.earth },
      },
      {
        id: "radar-landuse",
        type: "fill",
        source: SOURCE_ID,
        "source-layer": "landuse",
        paint: {
          "fill-color": "#171c16",
          "fill-opacity": 0.72,
        },
      },
      {
        id: "radar-water",
        type: "fill",
        source: SOURCE_ID,
        "source-layer": "water",
        paint: { "fill-color": "#0c191a" },
      },
      {
        id: "radar-buildings",
        type: "fill",
        source: SOURCE_ID,
        "source-layer": "buildings",
        minzoom: 12,
        paint: {
          "fill-color": "#23291f",
          "fill-outline-color": "#343b2d",
          "fill-opacity": 0.82,
        },
      },
      {
        id: "radar-road-casing",
        type: "line",
        source: SOURCE_ID,
        "source-layer": "roads",
        paint: {
          "line-color": "#080a07",
          "line-opacity": 0.95,
          "line-width": [
            "interpolate",
            ["exponential", 1.55],
            ["zoom"],
            11,
            1,
            15,
            5,
            18,
            18,
          ],
        },
      },
      {
        id: "radar-roads",
        type: "line",
        source: SOURCE_ID,
        "source-layer": "roads",
        paint: {
          "line-color": "#4a5140",
          "line-opacity": 0.9,
          "line-width": [
            "interpolate",
            ["exponential", 1.55],
            ["zoom"],
            11,
            0.35,
            15,
            2.1,
            18,
            10,
          ],
        },
      },
      {
        id: "radar-transit",
        type: "line",
        source: SOURCE_ID,
        "source-layer": "transit",
        minzoom: 10,
        paint: {
          "line-color": "#697057",
          "line-dasharray": [1.5, 1.5],
          "line-opacity": 0.45,
          "line-width": 1,
        },
      },
    ],
  }
}
