import streamlit as st


def multiselect_filter(label: str, options: list[str], default_all: bool = True) -> list[str]:
    default = options if default_all else []
    return st.multiselect(label, options=options, default=default)
