import streamlit as st
from pathlib import Path

st.title("👋 My Bio")

# ---------- TODO: Replace with your own info ----------
NAME = "Clay Griffin-Derr"
PROGRAM = "Data Science and Machine Learning"
INTRO = (
    "I specialize in Natural Language Processing such as text cleaning and information retrieval."
    "I am a member of the JRaviLab in the Anschutz Department of BioMedical Informatics."
)
FUN_FACTS = [
    "I'm learning how to run open source models locally to improve my workflow.",
    "My favorite open source model is Qwen 3.5.",
    "I want to build an LLM-based approach for standardizing biomedical metadata.",
]


PHOTO_PATH = "Profile.PNG"  # File name inside streamlit_DSML/assets/


def find_photo(filename=PHOTO_PATH):
    # Try common locations for multipage apps
    try:
        script_dir = Path(__file__).resolve().parent
    except NameError:
        script_dir = Path.cwd()

    candidates = [
        script_dir / "assets" / filename,          # pages/assets/...
        script_dir.parent / "assets" / filename,   # root/assets/... (common)
        Path("assets") / filename,                 # cwd/assets/...
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return None

photo_src = find_photo(PHOTO_PATH)

# ---------- Layout ----------
col1, col2 = st.columns([1, 2], vertical_alignment="center")

with col1:
    if photo_src:
        st.image(photo_src, caption=NAME, use_container_width=True)
    else:
        st.info(
            "📷 Place `Your_Photo.jpg` inside an `assets/` folder at the app root "
            "or update the path in `find_photo()`."
        )
        
with col2:
    st.subheader(NAME)
    st.write(PROGRAM)
    st.write(INTRO)

st.markdown("### Fun facts")
for i, f in enumerate(FUN_FACTS, start=1):
    st.write(f"- {f}")

st.divider()
st.caption("Edit `pages/1_Bio.py` to customize this page.")
