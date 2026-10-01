"""Local-only location resolution for public job postings.

Resolution order stays strictly offline:

1. Coordinates supplied by the source itself (trusted, e.g. deterministic demo
   fixtures) are kept as-is.
2. A configured public landmark whose name/query text matches the location
   string contributes its configured coordinates.
3. The bundled city gazetteer resolves well-known place names to city-level
   centroids.

No external geocoding service is ever called, and the exact home address or
home coordinates are never part of this code path.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from app.agent.gazetteer import lookup_city


class LandmarkLike(Protocol):
    name: str
    query_text: str
    latitude: float | None
    longitude: float | None


@dataclass(frozen=True)
class ResolvedLocation:
    latitude: float
    longitude: float
    geocode_source: str


def _normalized_parts(text: str) -> tuple[str, ...]:
    normalized = " ".join(text.lower().split())
    return tuple(
        part.strip() for part in normalized.replace("/", ",").split(",") if part.strip()
    )


def _matches_landmark(location_text: str, landmark: LandmarkLike) -> bool:
    parts = _normalized_parts(location_text)
    candidates = {
        landmark.name.lower().strip(),
        landmark.query_text.lower().strip(),
    }
    candidates |= {
        candidate.replace("附近", "").strip() for candidate in candidates
    }
    candidates = {candidate for candidate in candidates if len(candidate) >= 2}
    if not candidates:
        return False
    haystack = location_text.lower()
    if any(candidate in haystack for candidate in candidates):
        return True
    return any(candidate in parts for candidate in candidates)


def resolve_job_location(
    location_text: str, landmarks: Sequence[LandmarkLike]
) -> ResolvedLocation | None:
    for landmark in landmarks:
        if (
            landmark.latitude is not None
            and landmark.longitude is not None
            and _matches_landmark(location_text, landmark)
        ):
            return ResolvedLocation(
                latitude=landmark.latitude,
                longitude=landmark.longitude,
                geocode_source=f"landmark:{landmark.name}",
            )
    place = lookup_city(location_text)
    if place is None:
        return None
    return ResolvedLocation(
        latitude=place.latitude,
        longitude=place.longitude,
        geocode_source=f"gazetteer:{place.name}",
    )
