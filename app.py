from __future__ import annotations

import streamlit as st

from src.config import DECODED_DOWNLOAD_NAME, DEFAULT_DOWNLOAD_NAME
from src.stego import (
    StegoError,
    build_payload,
    capacity_bytes,
    decode_image_bytes,
    encode_image_bytes,
    extract_payload,
    payload_overhead,
)
from src.utils import (
    calculate_psnr,
    create_diff_image,
    fit_image_to_capacity,
    image_to_png_bytes,
    open_image,
    png_bytes_to_image,
)

st.set_page_config(page_title="Image Vault", page_icon="🔐", layout="wide")
st.title("Image Vault")
st.caption("Hide one image inside another using LSB steganography. Encode now, decode later.")

mode = st.radio("Choose mode", ["Encode", "Decode"], horizontal=True)

if mode == "Encode":
    st.subheader("Encode secret image")
    st.write("Upload both images and generate a downloadable encoded PNG.")

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

    password_input = st.text_input(
        "Password (optional)",
        type="password",
        key="encode_password",
    )

    if cover_file:
        try:
            cover_img = open_image(cover_file)
            cap = capacity_bytes(cover_img)

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Cover size", f"{cover_img.size[0]} × {cover_img.size[1]}")
            with c2:
                st.metric("Estimated capacity", f"{cap // 1024} KB")
            with c3:
                st.metric("Method", "2-bit LSB")
        except Exception as e:
            st.error(f"Error reading cover image: {e}")

    if cover_file and secret_file:
        try:
            password = password_input.strip() or None
            cover_img = open_image(cover_file)
            secret_img = open_image(secret_file)
            cap = capacity_bytes(cover_img)
            secret_capacity = max(0, cap - payload_overhead(password))
            secret_img, secret_bytes, resized = fit_image_to_capacity(
                secret_img,
                secret_capacity,
            )

            payload = build_payload(secret_bytes, password)

            if len(payload) > cap:
                st.error(
                    f"Secret image is too large for this cover image.\n\n"
                    f"Secret size: {len(secret_bytes)} bytes\n"
                    f"Capacity: {cap} bytes\n\n"
                    f"Use a larger cover image or a smaller secret image."
                )
            else:
                if resized:
                    st.warning(
                        "Secret image was resized to fit the available capacity. "
                        f"New size: {secret_img.size[0]} × {secret_img.size[1]}"
                    )

                encoded_img = encode_image_bytes(cover_img, payload)
                diff_img = create_diff_image(cover_img, encoded_img, boost=40)

                c1, c2, c3 = st.columns(3)

                with c1:
                    st.write("Cover image")
                    st.image(cover_img, use_container_width=True)

                with c2:
                    st.write("Secret image")
                    st.image(secret_img, use_container_width=True)

                with c3:
                    st.write("Encoded output")
                    st.image(encoded_img, use_container_width=True)

                st.subheader("Visual difference")
                st.caption("The difference map is boosted so tiny pixel changes become visible.")
                st.image(diff_img, use_container_width=True)
                try:
                    psnr_value = calculate_psnr(cover_img, encoded_img)
                    st.metric("PSNR (Cover vs Encoded)", f"{psnr_value:.2f} dB")
                except Exception as e:
                    st.warning(f"Could not compute PSNR: {e}")

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

    st.info("Tip: Use PNG for the encoded image. JPEG compression can damage hidden image data.")
  
else:
    st.subheader("Decode hidden image")
    st.write("Upload the encoded image and recover the secret image.")

    encoded_file = st.file_uploader(
        "Upload encoded image",
        type=["png", "jpg", "jpeg", "bmp"],
        key="encoded_file",
    )

    password_input = st.text_input(
        "Password (optional)",
        type="password",
        key="decode_password",
    )

    cover_file = st.file_uploader(
        "Upload original cover image (optional, for comparison)",
        type=["png", "jpg", "jpeg", "bmp"],
        key="cover_compare_file",
    )

    if encoded_file:
        try:
            password = password_input.strip() or None
            encoded_img = open_image(encoded_file)
            payload = decode_image_bytes(encoded_img)
            secret_bytes = extract_payload(payload, password)
            decoded_img = png_bytes_to_image(secret_bytes)

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Encoded size", f"{encoded_img.size[0]} × {encoded_img.size[1]}")
            with c2:
                st.metric("Recovered output", f"{decoded_img.size[0]} × {decoded_img.size[1]}")
            with c3:
                st.metric("Recovery", "Instant")

            c1, c2 = st.columns(2)

            with c1:
                st.write("Encoded image")
                st.image(encoded_img, use_container_width=True)

            with c2:
                st.write("Recovered secret image")
                st.image(decoded_img, use_container_width=True)

            if cover_file:
                try:
                    cover_img = open_image(cover_file)
                    diff_img = create_diff_image(cover_img, encoded_img, boost=40)
                    st.subheader("Visual difference")
                    st.caption("The difference map is boosted so tiny pixel changes become visible.")
                    st.image(diff_img, use_container_width=True)
                    try:
                        psnr_value = calculate_psnr(cover_img, encoded_img)
                        st.metric("PSNR (Cover vs Encoded)", f"{psnr_value:.2f} dB")
                    except Exception as e:
                        st.warning(f"Could not compute PSNR: {e}")
                except Exception as e:
                    st.warning(f"Could not compare images: {e}")

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

    st.info("Tip: Use PNG for the encoded image. JPEG compression can damage hidden image data.")