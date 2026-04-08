from __future__ import annotations

import streamlit as st
from PIL import Image

from src.config import DECODED_DOWNLOAD_NAME, DEFAULT_DOWNLOAD_NAME
from src.stego import decode_image, encode_image
from src.ui import footer_note, hero, image_card, info_cards, load_css, metric_row, section_title
from src.utils import create_diff_image, estimate_capacity, image_to_png_bytes, open_image


st.set_page_config(page_title="Image Vault", page_icon="🔐", layout="wide")
load_css()
hero()
info_cards()

mode = st.radio("Choose mode", ["Encode", "Decode"], horizontal=True)

if mode == "Encode":
    section_title("Encode secret image", "Upload both images and generate a downloadable encoded PNG.")

    left, right = st.columns([1, 1])

    with left:
        cover_file = st.file_uploader(
            "Upload cover image",
            type=["png", "jpg", "jpeg", "bmp"],
            key="cover_file",
        )
    with right:
        secret_file = st.file_uploader(
            "Upload secret image",
            type=["png", "jpg", "jpeg", "bmp"],
            key="secret_file",
        )

    if cover_file:
        cover_img = open_image(cover_file)
        cap_bytes, cap_kb = estimate_capacity(cover_img)
        metric_row(
            "Cover size",
            f"{cover_img.size[0]} × {cover_img.size[1]}",
            "Estimated capacity",
            f"{cap_kb} KB",
            "Method",
            "4-bit LSB",
        )

    if cover_file and secret_file:
        cover_img = open_image(cover_file)
        secret_img = open_image(secret_file)
        encoded_img = encode_image(cover_img, secret_img)
        diff_img = create_diff_image(cover_img, encoded_img)

        c1, c2, c3 = st.columns(3)
        with c1:
            image_card("Cover image", "Visible image that carries the hidden content.")
            st.image(cover_img, use_container_width=True)
        with c2:
            image_card("Secret image", "This image will be hidden inside the cover image.")
            st.image(secret_img, use_container_width=True)
        with c3:
            image_card("Encoded output", "Looks close to the cover image but contains hidden data.")
            st.image(encoded_img, use_container_width=True)

        section_title("Visual difference", "The difference map is boosted so tiny pixel changes become visible.")
        st.image(diff_img, use_container_width=True)

        st.success("Encoded image ready. Download it as PNG and use it later in decode mode.")
        st.download_button(
            label="Download encoded PNG",
            data=image_to_png_bytes(encoded_img),
            file_name=DEFAULT_DOWNLOAD_NAME,
            mime="image/png",
            type="primary",
        )

    footer_note()

else:
    section_title("Decode hidden image", "Upload the encoded image and recover the secret image.")

    encoded_file = st.file_uploader(
        "Upload encoded image",
        type=["png", "jpg", "jpeg", "bmp"],
        key="encoded_file",
    )

    if encoded_file:
        encoded_img = open_image(encoded_file)
        decoded_img = decode_image(encoded_img)

        metric_row(
            "Encoded size",
            f"{encoded_img.size[0]} × {encoded_img.size[1]}",
            "Recovered output",
            f"{decoded_img.size[0]} × {decoded_img.size[1]}",
            "Recovery",
            "Instant",
        )

        c1, c2 = st.columns(2)
        with c1:
            image_card("Encoded image", "Image received or downloaded after encoding.")
            st.image(encoded_img, use_container_width=True)
        with c2:
            image_card("Recovered secret image", "Extracted by reading the lower 4 bits and shifting back.")
            st.image(decoded_img, use_container_width=True)

        st.success("Hidden image recovered successfully.")
        st.download_button(
            label="Download recovered image",
            data=image_to_png_bytes(decoded_img),
            file_name=DECODED_DOWNLOAD_NAME,
            mime="image/png",
            type="primary",
        )

    footer_note()