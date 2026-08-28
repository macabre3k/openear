"""Small, respectful client for the public ListenBrainz listens endpoint."""

from __future__ import annotations

import time
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://api.listenbrainz.org/1"
USER_AGENT = "OpenEar/0.1 (https://github.com/macabre3k/openear)"


class ListenBrainzError(RuntimeError):
    """Raised when ListenBrainz cannot provide usable data."""


def _normalise(raw: dict[str, Any]) -> dict[str, Any]:
    metadata = raw.get("track_metadata") or {}
    additional = metadata.get("additional_info") or {}
    return {
        "listened_at": int(raw.get("listened_at", 0)),
        "artist": str(metadata.get("artist_name") or "Unknown artist").strip(),
        "track": str(metadata.get("track_name") or "Unknown track").strip(),
        "release": str(metadata.get("release_name") or "Unknown release").strip(),
        "recording_mbid": additional.get("recording_mbid"),
        "artist_mbids": additional.get("artist_mbids") or [],
    }


def fetch_listens(username: str, limit: int = 500, page_size: int = 100) -> list[dict[str, Any]]:
    """Fetch up to ``limit`` public listens without storing credentials."""
    username = username.strip()
    if not username:
        raise ValueError("ListenBrainz username is required")
    if limit < 1 or limit > 5_000:
        raise ValueError("limit must be between 1 and 5000")

    listens: list[dict[str, Any]] = []
    max_ts: int | None = None

    while len(listens) < limit:
        params: dict[str, Any] = {"count": min(page_size, limit - len(listens))}
        if max_ts is not None:
            params["max_ts"] = max_ts
        url = f"{BASE_URL}/user/{username}/listens?{urlencode(params)}"
        request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        try:
            with urlopen(request, timeout=20) as response:
                payload = json.load(response)
        except HTTPError as exc:
            if exc.code == 404:
                raise ListenBrainzError("User not found or listening history is private") from exc
            raise ListenBrainzError(f"ListenBrainz request failed: {exc}") from exc
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ListenBrainzError(f"ListenBrainz request failed: {exc}") from exc

        batch = payload.get("payload", {}).get("listens", [])
        if not batch:
            break
        listens.extend(_normalise(item) for item in batch)
        next_ts = min(int(item.get("listened_at", 0)) for item in batch) - 1
        if max_ts is not None and next_ts >= max_ts:
            break
        max_ts = next_ts
        if len(batch) < params["count"]:
            break
        time.sleep(0.15)

    return listens[:limit]
