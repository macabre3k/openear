"""Deterministic demo data for visitors without a ListenBrainz account."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import random


ARTISTS = {
    "Massive Attack": ["Teardrop", "Angel", "Inertia Creeps"],
    "Björk": ["Jóga", "Hyperballad", "Hidden Place"],
    "Portishead": ["Roads", "Glory Box", "Sour Times"],
    "FKA twigs": ["cellophane", "two weeks"],
    "Sevdaliza": ["Human", "Shahmaran"],
    "Arooj Aftab": ["Mohabbat", "Last Night"],
    "Nubya Garcia": ["Pace", "The Message Continues"],
    "L'Rain": ["Two Face", "Find It"],
    "Yaeji": ["For Granted", "Raingurl"],
    "Kelela": ["Rewind", "Washed Away"],
    "Mabe Fratti": ["Pantalla azul", "Cada músculo"],
    "SPELLLING": ["Little Deer", "Boys at School"],
}

RARE_ARTISTS = {
    "Derya Yıldırım & Grup Şimşek": "Nem Kaldı",
    "Ichiko Aoba": "Asleep Among Endives",
    "Júníus Meyvant": "Signals",
    "Kokoroko": "Abusey Junction",
}


def demo_listens(seed: int = 42, count: int = 240) -> list[dict[str, object]]:
    rng = random.Random(seed)
    artists = list(ARTISTS)
    weights = [20, 17, 15, 10, 9, 7, 6, 4, 4, 3, 3, 2]
    now = datetime.now(timezone.utc).replace(microsecond=0)
    rows = []
    core_count = max(0, count - len(RARE_ARTISTS))
    for index in range(core_count):
        artist = rng.choices(artists, weights=weights, k=1)[0]
        rows.append(
            {
                "listened_at": int((now - timedelta(hours=index * 3)).timestamp()),
                "artist": artist,
                "track": rng.choice(ARTISTS[artist]),
                "release": "Demo collection",
                "recording_mbid": None,
                "artist_mbids": [],
            }
        )
    for offset, (artist, track) in enumerate(RARE_ARTISTS.items(), start=core_count):
        rows.append(
            {
                "listened_at": int((now - timedelta(hours=offset * 3)).timestamp()),
                "artist": artist,
                "track": track,
                "release": "Demo discovery",
                "recording_mbid": None,
                "artist_mbids": [],
            }
        )
    return rows[:count]
