import streamlit as st
from PIL import Image
from io import BytesIO
from .utils import pil_to_png_bytes, png_bytes_to_pil
from .stego import prepare_payload, embed_bytes_into_image, extract_bytes_from_image
from .metrics import psnr, mse, cover_score
from .config import ASSETS_DIR
import numpy as np
import matplotlib.pyplot as plt
import time


def _load_css():
    try:
        p = ASSETS_DIR / "style.css"
        css = p.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except Exception:
        pass


def _image_from_uploader(uploader) -> Image.Image:
    if uploader is None:
        return None
    try:
        img = Image.open(uploader).convert("RGBA")
        return img
    except Exception:
        return None


def _diff_heatmap(diff_arr: np.ndarray) -> bytes:
    # diff_arr is HxWx3
    gray = np.mean(diff_arr.astype(np.float32), axis=2)
    fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
    ax.imshow(gray, cmap='inferno')
    ax.axis('off')
    buf = BytesIO()
    fig.tight_layout(pad=0)
    fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def main():
    st.set_page_config(page_title="IMAGE VAULT", layout="wide")
    _load_css()

    # Top hero
    with st.container():
        col1, col2 = st.columns([3,1])
        with col1:
            st.markdown("""
            <div class="top-hero">
              <div>
                <div class="badge">🔐 Secure Visual Hiding</div>
                <div class="title">IMAGE VAULT</div>
                <div class="subtitle">Hide one image inside another using invisible steganography.</div>
              </div>
              <div style="text-align:right">
                <div class="pill">🖼 Cover + Secret</div>
                <div style="height:8px"></div>
                <div class="pill">🔒 Invisible Hiding</div>
                <div style="height:8px"></div>
                <div class="pill">⬇ PNG Export</div>
                <div style="height:8px"></div>
                <div class="pill">🔓 Recovery</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    mode = st.radio("Mode", ["Encode", "Decode"], horizontal=True)

    if mode == "Encode":
        col_main, col_side = st.columns([2,1])
        with col_main:
            st.header("Encode — Hide a secret inside a cover image")
            left, right = st.columns(2)
            with left:
                cover_up = st.file_uploader("Upload Cover Image", type=["png","jpg","jpeg"], key="cover")
                cover_img = _image_from_uploader(cover_up)
                if cover_img:
                    st.image(cover_img, caption="Cover Preview", use_column_width=True)
            with right:
                secret_up = st.file_uploader("Upload Secret Image", type=["png","jpg","jpeg"], key="secret")
                secret_img = _image_from_uploader(secret_up)
                if secret_img:
                    st.image(secret_img, caption="Secret Preview", use_column_width=True)

            st.markdown("---")
            password = st.text_input("Password (optional)", type="password")
            encode_btn = st.button("Encode and Generate PNG")

            if cover_img and secret_img:
                # metrics
                cover_bytes = pil_to_png_bytes(cover_img)
                secret_bytes = pil_to_png_bytes(secret_img)
                cover_arr = np.array(cover_img.convert('RGBA'))
                carrier_size = cover_arr[:, :, :3].size  # number of bytes
                capacity_bits = carrier_size * 2
                capacity_bytes = capacity_bits // 8
                payload_est = len(secret_bytes) + 41  # header estimate
                usage_pct = min(100.0, (payload_est / capacity_bytes) * 100)

                st.markdown("**Metrics**")
                st.write(f"- Cover Resolution: {cover_img.width} x {cover_img.height}")
                st.write(f"- Capacity: {capacity_bytes/1024:.2f} KB")
                st.write(f"- Secret Size: {len(secret_bytes)/1024:.2f} KB")
                st.write(f"- Estimated Usage: {usage_pct:.1f}%")

                score_label, score_stats = cover_score(cover_img)
                st.write(f"- Cover Suitability: {score_label} (entropy={score_stats['entropy']:.2f})")

                if payload_est > capacity_bytes:
                    st.error("Secret does not fit inside the cover image. Choose a larger cover or smaller secret.")

            if encode_btn:
                if not cover_img or not secret_img:
                    st.error("Please upload both cover and secret images.")
                else:
                    try:
                        payload = prepare_payload(secret_img, password if password else None)
                        encoded_img, diff = embed_bytes_into_image(cover_img, payload)
                        buf = BytesIO()
                        encoded_img.save(buf, format='PNG')
                        buf.seek(0)
                        st.success("Encoded image generated.")
                        st.image(encoded_img, caption="Encoded Image", use_column_width=True)
                        heat = _diff_heatmap(diff)
                        st.image(heat, caption="Visual Difference Heatmap")
                        st.write("**Results**")
                        st.write(f"- Payload Size: {len(payload)/1024:.2f} KB")
                        st.write(f"- MSE: {mse(cover_img, encoded_img):.4f}")
                        st.write(f"- PSNR: {psnr(cover_img, encoded_img):.2f} dB")
                        st.download_button("Download Encoded PNG", data=buf.getvalue(), file_name="encoded.png", mime='image/png')
                    except Exception as e:
                        st.error(f"Encoding failed: {e}")

        with col_side:
            st.markdown("""
            <div class="card">
            <h4>Methodology</h4>
            <p>Secret image → PNG bytes → optional encryption → 2-bit LSB embed into cover image RGB channels. Header contains metadata and payload length.</p>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.header("Decode — Recover a hidden secret image")
        enc_up = st.file_uploader("Upload Encoded Image (PNG)", type=["png"], key="encoded")
        password = st.text_input("Password (if used during encoding)", type="password", key="pwd2")
        decode_btn = st.button("Decode")
        if enc_up and decode_btn:
            try:
                enc_img = Image.open(enc_up).convert('RGBA')
                header, payload, dt = extract_bytes_from_image(enc_img)
                # parse header
                sig = header[0:6]
                version = header[6]
                flags = header[7]
                salt = header[9:9+16]
                nonce = header[9+16:9+16+12]
                payload_len = int.from_bytes(header[-4:], 'big')
                encrypted = bool(flags & 1)
                st.write(f"- Header Version: {version}")
                st.write(f"- Encrypted: {encrypted}")
                st.write(f"- Payload Size: {payload_len/1024:.2f} KB")
                if encrypted and not password:
                    st.error("This payload is encrypted — please provide the password.")
                else:
                    if encrypted:
                        from .security import decrypt_bytes
                        try:
                            secret_bytes = decrypt_bytes(password, salt, nonce, payload)
                        except Exception as e:
                            st.error("Decryption failed — incorrect password or corrupted payload.")
                            raise
                    else:
                        secret_bytes = payload
                    try:
                        secret_img = png_bytes_to_pil(secret_bytes)
                        st.image(secret_img, caption="Recovered Secret", use_column_width=True)
                        st.write(f"- Recovered Size: {len(secret_bytes)/1024:.2f} KB")
                        st.write(f"- Decode Time: {dt:.3f} s")
                        buf = BytesIO()
                        secret_img.save(buf, format='PNG')
                        buf.seek(0)
                        st.download_button("Download Recovered PNG", data=buf.getvalue(), file_name='recovered.png', mime='image/png')
                    except Exception as e:
                        st.error(f"Failed to reconstruct image: {e}")

    st.markdown("""
    <div class="footer">IMAGE VAULT — Secure Image Steganography • No external database • Local export</div>
    """, unsafe_allow_html=True)
