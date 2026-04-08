from __future__ import annotations
import streamlit as st
from PIL import Image

from src.config import APP_SUBTITLE, APP_TITLE


def load_css(path: str = "assets/style.css") -> None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

def hero() -> None:
    st.markdown(
        f"""
        <div class='hero-card'>
            <div class='hero-badge'>🔐 Secure Visual Hiding</div>
            <h1>{APP_TITLE}</h1>
            <p>{APP_SUBTITLE}</p>
            <div class='hero-note'>Upload a cover image and a secret image, generate the encoded PNG, then decode it later to recover the hidden image.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
def info_cards() -> None:
    st.markdown(
        """
        <div class='info-grid'>
            <div class='info-card'>
                <div class='info-title'>Encode</div>
                <div class='info-text'>Hide one image inside another using 4-bit image steganography.</div>
            </div>
            <div class='info-card'>
                <div class='info-title'>Download</div>
                <div class='info-text'>Save the encoded result as PNG for safe recovery.</div>
            </div>
            <div class='info-card'>
                <div class='info-title'>Decode</div>
                <div class='info-text'>Upload the encoded image later and recover the hidden image.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
def section_title(title: str, subtitle: str = "") -> None:
    if subtitle:
        st.markdown(
            f"""
            <div class='section-block'>
                <h2>{title}</h2>
                <p>{subtitle}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(f"## {title}")
def image_card(title: str, caption: str = "") -> None:
    if caption:
        st.markdown(
            f"""
            <div class='mini-card'>
                <div class='mini-title'>{title}</div>
                <div class='mini-caption'>{caption}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class='mini-card'>
                <div class='mini-title'>{title}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )



def metric_row(a_label: str, a_value: str, b_label: str, b_value: str, c_label: str, c_value: str) -> None:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(a_label, a_value)
    with c2:
        st.metric(b_label, b_value)
    with c3:
        st.metric(c_label, c_value)



def footer_note() -> None:
    st.markdown(
        """
        <div class='footer-note'>
            Tip: PNG is recommended because JPEG compression can damage the hidden image data.
        </div>
        """,
        unsafe_allow_html=True,
    )