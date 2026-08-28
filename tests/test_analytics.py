from openear.analytics import analyse, artist_breakdown, rediscovery_queue


def row(artist: str, track: str, ts: int) -> dict[str, object]:
    return {"artist": artist, "track": track, "listened_at": ts}


def test_empty_history_is_safe() -> None:
    report = analyse([])
    assert report.total_listens == 0
    assert report.diversity_score == 0


def test_balanced_history_is_more_diverse_than_single_artist() -> None:
    balanced = [row(name, f"track-{i}", 1_700_000_000 + i) for i, name in enumerate("ABCD")]
    concentrated = [row("A", f"track-{i}", 1_700_000_000 + i) for i in range(4)]
    assert analyse(balanced).diversity_score > analyse(concentrated).diversity_score
    assert analyse(balanced).discovery_score > analyse(concentrated).discovery_score


def test_breakdown_and_rediscovery_are_explainable() -> None:
    listens = [row("A", "one", 100), row("A", "two", 200), row("B", "three", 50)]
    assert artist_breakdown(listens)[0]["artist"] == "A"
    queue = rediscovery_queue(listens)
    assert [item["artist"] for item in queue] == ["B", "A"]
