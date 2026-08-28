"""Transparent music-diversity metrics with no black-box model."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from math import log
from typing import Any, Iterable


@dataclass(frozen=True)
class DiversityReport:
    total_listens: int
    unique_artists: int
    unique_tracks: int
    diversity_score: float
    discovery_score: float
    top_artist_share: float
    long_tail_share: float
    active_days: int


def _normalised_entropy(counts: Iterable[int]) -> float:
    values = [value for value in counts if value > 0]
    total = sum(values)
    if total == 0 or len(values) <= 1:
        return 0.0
    entropy = -sum((value / total) * log(value / total) for value in values)
    return entropy / log(len(values))


def analyse(listens: list[dict[str, Any]]) -> DiversityReport:
    """Calculate explainable 0–100 diversity and discovery scores."""
    if not listens:
        return DiversityReport(0, 0, 0, 0.0, 0.0, 0.0, 0.0, 0)

    artists = Counter(str(row.get("artist") or "Unknown artist") for row in listens)
    tracks = {
        (str(row.get("artist") or ""), str(row.get("track") or "")) for row in listens
    }
    total = len(listens)
    entropy = _normalised_entropy(artists.values())
    unique_ratio = min(1.0, len(artists) / max(1.0, total * 0.35))
    long_tail = sum(count for count in artists.values() if count <= 2) / total
    concentration = max(artists.values()) / total

    # Diversity rewards an even spread; discovery rewards breadth and long-tail listening.
    diversity = 100 * (0.75 * entropy + 0.25 * (1 - concentration))
    discovery = 100 * (0.55 * unique_ratio + 0.45 * long_tail)
    days = {
        datetime.fromtimestamp(int(row["listened_at"]), tz=timezone.utc).date()
        for row in listens
        if int(row.get("listened_at") or 0) > 0
    }
    return DiversityReport(
        total_listens=total,
        unique_artists=len(artists),
        unique_tracks=len(tracks),
        diversity_score=round(diversity, 1),
        discovery_score=round(discovery, 1),
        top_artist_share=round(100 * concentration, 1),
        long_tail_share=round(100 * long_tail, 1),
        active_days=len(days),
    )


def artist_breakdown(listens: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts = Counter(str(row.get("artist") or "Unknown artist") for row in listens)
    total = max(1, len(listens))
    return [
        {"artist": artist, "listens": count, "share_pct": round(100 * count / total, 1)}
        for artist, count in counts.most_common()
    ]


def rediscovery_queue(listens: list[dict[str, Any]], size: int = 12) -> list[dict[str, Any]]:
    """Surface artists heard only once or twice instead of inventing recommendations."""
    counts = Counter(str(row.get("artist") or "Unknown artist") for row in listens)
    last_seen: dict[str, int] = {}
    sample_track: dict[str, str] = {}
    for row in listens:
        artist = str(row.get("artist") or "Unknown artist")
        last_seen[artist] = max(last_seen.get(artist, 0), int(row.get("listened_at") or 0))
        sample_track.setdefault(artist, str(row.get("track") or ""))
    candidates = [artist for artist, count in counts.items() if count <= 2]
    candidates.sort(key=lambda artist: (last_seen.get(artist, 0), artist.casefold()))
    return [
        {
            "artist": artist,
            "heard": counts[artist],
            "try_again": sample_track[artist],
            "last_heard": datetime.fromtimestamp(last_seen[artist], tz=timezone.utc).date().isoformat()
            if last_seen[artist]
            else "unknown",
        }
        for artist in candidates[:size]
    ]
