from openear.listenbrainz import _normalise


def test_normalise_listenbrainz_payload() -> None:
    raw = {
        "listened_at": 1_700_000_000,
        "track_metadata": {
            "artist_name": "Björk",
            "track_name": "Jóga",
            "release_name": "Homogenic",
            "additional_info": {"recording_mbid": "abc", "artist_mbids": ["def"]},
        },
    }
    assert _normalise(raw) == {
        "listened_at": 1_700_000_000,
        "artist": "Björk",
        "track": "Jóga",
        "release": "Homogenic",
        "recording_mbid": "abc",
        "artist_mbids": ["def"],
    }
