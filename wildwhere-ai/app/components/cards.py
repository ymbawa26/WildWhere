import streamlit as st


def metric_card(label: str, value: str, help_text: str | None = None) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-value">{value}</div>
          <div class="metric-label">{label}</div>
          {f'<div class="metric-help">{help_text}</div>' if help_text else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )
