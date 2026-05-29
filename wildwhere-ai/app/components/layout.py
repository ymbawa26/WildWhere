from pathlib import Path

import streamlit as st


def configure_page(title: str = "WildWhere AI") -> None:
    st.set_page_config(page_title=title, page_icon="🌲", layout="wide")
    css_path = Path(__file__).resolve().parents[1] / "styles" / "custom.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def page_header(title: str, subtitle: str) -> None:
    st.markdown(f"<div class='eyebrow'>WildWhere AI</div><h1>{title}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='subtitle'>{subtitle}</p>", unsafe_allow_html=True)


def caveat() -> None:
    st.info(
        "WildWhere AI uses reported observations and public datasets. It does not provide confirmed wildlife presence, "
        "real-time tracking, or true population density."
    )
