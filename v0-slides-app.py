import streamlit as st
import yaml
import os
from openai import OpenAI
from pathlib import Path

st.set_page_config(
    page_title="AI als datalek: ben jij de zwakste schakel?",
    page_icon="🔒",
    layout="wide",
)

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

    .stApp {
        font-family: 'DM Sans', sans-serif;
    }

    .page-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.3rem;
        line-height: 1.3;
    }

    .page-subtitle {
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }

    .context-box {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-top: 1rem;
        color: #334155;
        font-size: 0.95rem;
        line-height: 1.8;
        border: 1px solid #e2e8f0;
    }

    .context-box h4 {
        color: #1e293b;
        font-size: 1rem;
        margin: 0 0 0.5rem 0;
    }

    .slide-counter {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-bottom: 0.5rem;
    }

    /* Progress bar */
    .progress-container {
        display: flex;
        gap: 4px;
        margin-bottom: 1rem;
    }

    .progress-dot {
        height: 4px;
        border-radius: 2px;
        flex: 1;
        transition: background 0.3s;
    }

    .progress-active {
        background: #818cf8;
    }

    .progress-inactive {
        background: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)


# --- Slide decks ---
DECKS = {
    "Hoe AI-tools omgaan met jouw data": "slides.yaml",
    "Welke data is gevoelig?": "slides-gevoelige-data.yaml",
}

# --- LLM personalization ---
def build_prompt(context, user_name, user_intro, slide_title):
    return (
        f"Je bent een behulpzame presentatie-assistent. "
        f"Herschrijf de onderstaande begeleidende tekst bij de slide \"{slide_title}\" "
        f"zodat deze persoonlijk aansluit bij de gebruiker.\n\n"
        f"spreek de gebruiker persoonlijk aan.\n\n"
        f"Gebruiker: {user_name or 'onbekend'}\n"
        f"Over zichzelf: {user_intro}\n\n"
        f"Originele tekst:\n{context}\n\n"
        f"Regels:\n"
        f"- Behoud alle feitelijke inhoud en kernboodschappen\n"
        f"- Pas voorbeelden en toon aan zodat ze relevant zijn voor de achtergrond van de gebruiker\n"
        f"- Spreek de gebruiker aan met de naam als die is opgegeven\n"
        f"- Schrijf in het Nederlands\n"
        f"- Geef enkel de herschreven tekst terug, geen extra uitleg"
    )


def stream_personalized(context, user_name, user_intro, slide_title, deck_name, slide_idx):
    """Stream personalized text from LLM, or return cached/original text."""
    api_key = os.environ.get("OPEN_ROUTER_API", "")
    if not api_key:
        st.warning("Omgevingsvariabele OPEN_ROUTER_API is niet ingesteld.")
        return None, context
    if not user_intro:
        return None, context

    cache_key = f"personalized_{deck_name}_{slide_idx}_{user_intro}"
    if cache_key in st.session_state:
        return None, st.session_state[cache_key]

    # Return a stream generator
    prompt = build_prompt(context, user_name, user_intro, slide_title)
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        stream = client.chat.completions.create(
            model="anthropic/claude-sonnet-4",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
        return stream, cache_key
    except Exception as e:
        st.error(f"Personalisatie mislukt: {e}")
        return None, context


# --- Session state ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
if "current_slide" not in st.session_state:
    st.session_state.current_slide = 0
if "current_deck" not in st.session_state:
    st.session_state.current_deck = None
if "saved_user_name" not in st.session_state:
    st.session_state.saved_user_name = ""
if "saved_user_intro" not in st.session_state:
    st.session_state.saved_user_intro = ""


# --- Home screen ---
if st.session_state.current_page == "home":
    st.markdown("""
    <div class="context-box" style="text-align: center;">
        <h2 style="margin: 0 0 0.5rem 0; color: #1e293b;">AI als datalek: ben jij de zwakste schakel?</h2>
        <p style="color: #64748b; margin: 0;">Kies hieronder een thema om te starten.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

    st.text_input(
        "Hoe wil je aangesproken worden?",
        key="user_name",
        value=st.session_state.saved_user_name,
        placeholder="Bijv. Jan",
    )
    st.text_area(
        "Vertel iets over jezelf en waarom je hier bent",
        key="user_intro",
        value=st.session_state.saved_user_intro,
        placeholder="Bijv. Ik werk als data-analist en wil meer weten over de risico's van AI-tools op de werkvloer.",
        height=120,
    )

    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

    cols = st.columns(len(DECKS))
    for i, deck_name in enumerate(DECKS):
        with cols[i]:
            if st.button(deck_name, use_container_width=True):
                st.session_state.saved_user_name = st.session_state.get("user_name", "")
                st.session_state.saved_user_intro = st.session_state.get("user_intro", "")
                st.session_state.current_page = "slides"
                st.session_state.current_deck = deck_name
                st.session_state.current_slide = 0
                st.rerun()

    st.stop()


# --- Slides view ---

# Back to home button
if st.button("< Terug naar overzicht"):
    st.session_state.current_page = "home"
    st.session_state.current_deck = None
    st.session_state.current_slide = 0
    st.rerun()

# --- Load slides ---
slides_path = Path(__file__).parent / DECKS[st.session_state.current_deck]
with open(slides_path, encoding="utf-8") as f:
    slides = yaml.safe_load(f)

total = len(slides)
idx = st.session_state.current_slide
slide = slides[idx]


# --- Progress bar ---
progress_html = '<div class="progress-container">'
for i in range(total):
    cls = "progress-active" if i <= idx else "progress-inactive"
    progress_html += f'<div class="progress-dot {cls}"></div>'
progress_html += "</div>"
st.markdown(progress_html, unsafe_allow_html=True)


# --- Title ---
st.markdown(f'<div class="slide-counter">{idx + 1} / {total}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="page-title">{slide["title"]}</div>', unsafe_allow_html=True)
if slide.get("subtitle"):
    st.markdown(f'<div class="page-subtitle">{slide["subtitle"]}</div>', unsafe_allow_html=True)

# --- Image ---
if slide.get("image"):
    image_path = Path(__file__).parent / "images" / slide["image"]
    if image_path.exists():
        st.image(str(image_path), use_container_width=True)

# --- Context text ---
if slide.get("context"):
    stream, result = stream_personalized(
        slide["context"],
        st.session_state.get("saved_user_name", ""),
        st.session_state.get("saved_user_intro", ""),
        slide["title"],
        st.session_state.current_deck,
        idx,
    )

    if stream is None:
        # result is the final text (cached or original)
        st.markdown(
            f'<div class="context-box">{result}</div>',
            unsafe_allow_html=True,
        )
    else:
        # stream is an OpenAI stream, result is the cache_key
        cache_key = result

        def token_generator():
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        full_text = st.write_stream(token_generator())
        st.session_state[cache_key] = full_text


# --- Navigation ---
st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    if idx > 0:
        if st.button("< Vorige", use_container_width=True):
            st.session_state.current_slide -= 1
            st.rerun()

with col3:
    if idx < total - 1:
        if st.button("Volgende >", use_container_width=True):
            st.session_state.current_slide += 1
            st.rerun()

with col2:
    selected = st.select_slider(
        "Ga naar slide",
        options=list(range(total)),
        value=idx,
        format_func=lambda x: f"Slide {x + 1}",
        label_visibility="collapsed",
    )
    if selected != idx:
        st.session_state.current_slide = selected
        st.rerun()
