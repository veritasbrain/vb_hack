import streamlit as st

import requests
from datetime import date
# BASE_URL = "https://pokeapi.co/api/v2/pokemon"

# def fetch_pokemon(name_or_id: str, timeout: float = 6) -> dict:
#     """Raise requests.HTTPError if the name/id doesn't exist (404) or on network errors."""
#     r = requests.get(f"{BASE_URL}/{str(name_or_id).strip().lower()}", timeout=timeout)
#     r.raise_for_status()
#     return r.json()


# def parse(data: dict) -> dict:
#     """Pull out just what the screen needs. Built name-keyed, not positional -
#     the API does not promise stats/types come back in a fixed order."""
#     sprites = data.get("sprites") or {}
#     artwork = ((sprites.get("other") or {}).get("official-artwork") or {}).get("front_default")
#     stats = {s["stat"]["name"]: s["base_stat"] for s in data.get("stats", [])}
#     types = [t["type"]["name"] for t in sorted(data.get("types", []), key=lambda t: t["slot"])]
#     return {
#         "id": data["id"],
#         "name": data["name"].capitalize(),
#         "height_m": data["height"] / 10,      # API gives decimetres
#         "weight_kg": data["weight"] / 10,      # API gives hectograms
#         "sprite": artwork or sprites.get("front_default"),
#         "types": types,
#         "stats": stats,
#     }




# name = st.text_input("Pokemon name or number", value="pikachu")

# if st.button("Search") or name:
#     try:
#         info = parse(fetch_pokemon(name))
#     except requests.exceptions.HTTPError:
#         st.error(f"No Pokemon found for '{name}'.")
#     except requests.exceptions.RequestException:
#         st.error("Couldn't reach PokeAPI - check your internet connection.")
#     else:
#         c1, c2 = st.columns([1, 2])
#         if info["sprite"]:
#             c1.image(info["sprite"], width=150)
#         with c2:
#             st.subheader(f"#{info['id']} {info['name']}")
#             st.write("Type: " + " / ".join(t.capitalize() for t in info["types"]))
#             st.write(f"Height: {info['height_m']:.1f} m   Weight: {info['weight_kg']:.1f} kg")

#         st.subheader("Base stats")
#         cols = st.columns(6)
#         order = ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]
#         for col, key in zip(cols, order):
#             col.metric(key.replace("-", " ").title(), info["stats"].get(key, "-"))


BASE_URL = "https://science.nasa.gov/wp-json/wp/v2/apod-basic"
EARLIEST = date(1995, 6, 16)   # the API has no pictures before this date


def fetch_apod(pick_date: date, timeout: float = 8) -> dict:
    """Date goes in the path as YYMMDD, e.g. 2026-09-29 -> 260929. 404 if no entry."""
    r = requests.get(f"{BASE_URL}/{pick_date.strftime('%y%m%d')}", timeout=timeout)
    r.raise_for_status()
    return r.json()


def _text(s: str | None) -> str:
    """Fields now contain HTML (links, <strong>, &amp;) - strip it to plain text."""
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def parse(data: dict) -> dict:
    return {
        "title": data.get("title", "(untitled)"),
        "date": data.get("date"),
        "explanation": _text(data.get("explanation")).removeprefix("Explanation:").strip(),
        "media_type": data.get("media_type", "image"),
        "image_url": data.get("hdurl"),          # the picture (url is the article page!)
        "page_url": data.get("permalink") or data.get("url"),
        "copyright": _text(data.get("copyright")) or None,
    }

st.set_page_config(page_title="Space Picture of the Day", page_icon="🔭")
st.title("🔭 Space Picture of the Day")
st.caption("Source: NASA APOD (api.nasa.gov)")

pick_date = st.date_input("Date", value=date.today(), min_value=EARLIEST, max_value=date.today())
api_key = st.text_input("NASA API key (optional)", value="DEMO_KEY",
                        help="DEMO_KEY is shared and rate-limited (30/hour, 50/day). "
                             "Get your own free key at api.nasa.gov if it stops working.")

if st.button("Show picture"):
    try:
        info = parse(fetch_apod(pick_date, api_key))
    except requests.exceptions.HTTPError:
        st.error("No picture found for that date, or the API key was rejected.")
    except requests.exceptions.RequestException:
        st.error("Couldn't reach NASA's API - check your internet connection.")
    else:
        st.subheader(f"{info['title']}  ({info['date']})")
        if info["media_type"] == "image" and info["image_url"]:
            st.image(info["image_url"], width="stretch")
        elif info["video_url"]:
            st.write(f"Today's APOD is a video: {info['video_url']}")
        st.write(info["explanation"])
        st.caption("© " + info["copyright"] if info["copyright"] else "Public domain (NASA)")