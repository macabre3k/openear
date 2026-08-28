"""Streamlit interface for OpenEar."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from openear.analytics import analyse, artist_breakdown, rediscovery_queue
from openear.listenbrainz import ListenBrainzError, fetch_listens
from openear.sample import demo_listens

st.set_page_config(page_title="OpenEar", page_icon="🎧", layout="wide")
st.title("🎧 OpenEar")
st.caption("Discover beyond the algorithm — private, transparent music-diversity analytics.")

with st.sidebar:
    st.header("Your listening history")
    username = st.text_input("ListenBrainz username", placeholder="e.g. rob")
    limit = st.slider("Recent listens", 100, 2_000, 500, 100)
    load_live = st.button("Analyse public history", type="primary", use_container_width=True)
    demo = st.button("Try the privacy-safe demo", use_container_width=True)
    st.info("OpenEar reads public listens only. It stores no username, token or listening history.")

if "listens" not in st.session_state:
    st.session_state.listens = demo_listens()
    st.session_state.source = "Synthetic demo"

if load_live:
    try:
        with st.spinner("Listening carefully…"):
            st.session_state.listens = fetch_listens(username, limit=limit)
            st.session_state.source = f"ListenBrainz: {username}"
    except (ListenBrainzError, ValueError) as exc:
        st.error(str(exc))
if demo:
    st.session_state.listens = demo_listens()
    st.session_state.source = "Synthetic demo"

listens = st.session_state.listens
report = analyse(listens)
st.subheader(st.session_state.source)

cols = st.columns(5)
cols[0].metric("Diversity", f"{report.diversity_score}/100")
cols[1].metric("Discovery", f"{report.discovery_score}/100")
cols[2].metric("Artists", report.unique_artists)
cols[3].metric("Tracks", report.unique_tracks)
cols[4].metric("Long-tail listens", f"{report.long_tail_share}%")

left, right = st.columns([3, 2])
with left:
    st.subheader("Who gets your attention?")
    artists = pd.DataFrame(artist_breakdown(listens)[:15]).set_index("artist")
    st.bar_chart(artists["listens"], horizontal=True)
with right:
    st.subheader("How the scores work")
    st.markdown(
        "**Diversity** combines the evenness of artist plays with resistance to "
        "single-artist dominance. **Discovery** combines artist breadth with the "
        "share of artists heard only once or twice. No opaque recommendation model."
    )
    st.progress(report.diversity_score / 100, text="Listening diversity")
    st.progress(report.discovery_score / 100, text="Discovery behaviour")
    st.metric("Top artist concentration", f"{report.top_artist_share}%")

st.subheader("Rediscovery queue")
st.write("Artists already present at the edge of your history — worth another listen.")
queue = pd.DataFrame(rediscovery_queue(listens))
if queue.empty:
    st.success("Your recent history has no underplayed artists. Increase the history window.")
else:
    st.dataframe(queue, hide_index=True, use_container_width=True)

with st.expander("Privacy and methodology"):
    st.markdown(
        "OpenEar processes data in the active session and does not persist it. The demo "
        "contains synthetic records. Scores are descriptive, not judgments about taste."
    )
