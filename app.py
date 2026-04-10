from __future__ import annotations

import streamlit as st
from PIL import Image

from src.config import DECODED_DOWNLOAD_NAME, DEFAULT_DOWNLOAD_NAME
from src.stego import StegoError, capacity_bytes, decode_image_bytes, encode_image_bytes
from src.ui import footer_note, hero, image_card, info_cards, load_css, metric_row, section_title
from src.utils import create_diff_image, image_to_png_bytes, open_image, png_bytes_to_image


st.set_page_config(page_title="Image Vault", page_icon="🔐", layout="wide")
load_css()
hero()
info_cards()

mode = st.radio("Choose mode", ["Encode", "Decode"], horizontal=True)

if mode == "Encode":
    section_title(
        "Encode secret image",
        "Upload both images and generate a downloadable encoded PNG."
    )

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
        try:
            cover_img = open_image(cover_file)
            cap = capacity_bytes(cover_img)

            metric_row(
                "Cover size",
                f"{cover_img.size[0]} × {cover_img.size[1]}",
                "Estimated capacity",
                f"{cap // 1024} KB",
                "Method",
                "1-bit LSB",
            )
        except Exception as e:
            st.error(f"Error reading cover image: {e}")

    if cover_file and secret_file:
        try:
            cover_img = open_image(cover_file)
            secret_img = open_image(secret_file)

            secret_bytes = image_to_png_bytes(secret_img)

            if len(secret_bytes) > capacity_bytes(cover_img):
                st.error(
                    f"Secret image is too large for this cover image.\n\n"
                    f"Secret size: {len(secret_bytes)} bytes\n"
                    f"Capacity: {capacity_bytes(cover_img)} bytes\n\n"
                    f"Use a larger cover image or a smaller secret image."
                )
            else:
                encoded_img = encode_image_bytes(cover_img, secret_bytes)
                diff_img = create_diff_image(cover_img, encoded_img)

                c1, c2, c3 = st.columns(3)

                with c1:
                    image_card("Cover image", "Visible image that carries the hidden content.")
                    st.image(cover_img, use_container_width=True)

                with c2:
                    image_card("Secret image", "This image will be hidden inside the cover image.")
                    st.image(secret_img, use_container_width=True)

                with c3:
                    image_card("Encoded output", "Looks almost the same as the cover image but contains hidden data.")
                    st.image(encoded_img, use_container_width=True)

                section_title(
                    "Visual difference",
                    "The difference map is boosted so very tiny pixel changes become visible."
                )
                st.image(diff_img, use_container_width=True)

                st.success("Encoded image ready. Download it as PNG and use it later in decode mode.")
                st.download_button(
                    label="Download encoded PNG",
                    data=image_to_png_bytes(encoded_img),
                    file_name=DEFAULT_DOWNLOAD_NAME,
                    mime="image/png",
                    type="primary",
                )

        except StegoError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Unexpected error during encoding: {e}")

    footer_note()

else:
    section_title(
        "Decode hidden image",
        "Upload the encoded image and recover the secret image."
    )

    encoded_file = st.file_uploader(
        "Upload encoded image",
        type=["png", "jpg", "jpeg", "bmp"],
        key="encoded_file",
    )

    if encoded_file:
        try:
            encoded_img = open_image(encoded_file)
            secret_bytes = decode_image_bytes(encoded_img)
            decoded_img = png_bytes_to_image(secret_bytes)

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
                image_card("Recovered secret image", "Recovered by extracting hidden bits and rebuilding the PNG.")
                st.image(decoded_img, use_container_width=True)

            st.success("Hidden image recovered successfully.")
            st.download_button(
                label="Download recovered image",
                data=secret_bytes,
                file_name=DECODED_DOWNLOAD_NAME,
                mime="image/png",
                type="primary",
            )

        except StegoError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Unexpected error during decoding: {e}")

    footer_note()