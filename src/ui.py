from __future__ import annotations

import streamlit as st
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
		<section class='hero'>
			<div class='hero-content'>
				<div class='hero-badge'>Secure. Invisible. Local.</div>
				<h1>{APP_TITLE}</h1>
				<p class='hero-subtitle'>{APP_SUBTITLE}</p>
				<p class='hero-note'>
					Hide one image inside another with LSB steganography.
					Export a clean PNG now and decode it later to recover the secret image.
				</p>
				<div class='hero-pills'>
					<span class='pill'>Cover + Secret</span>
					<span class='pill'>LSB Stego</span>
					<span class='pill'>Local Download</span>
					<span class='pill'>Quick Recovery</span>
				</div>
			</div>
			<div class='hero-panel'>
				<div class='panel-title'>How it works</div>
				<div class='panel-step'>1. Upload a cover image</div>
				<div class='panel-step'>2. Upload a secret image</div>
				<div class='panel-step'>3. Download the encoded PNG</div>
				<div class='panel-step'>4. Decode anytime</div>
			</div>
		</section>
		""",
		unsafe_allow_html=True,
	)


def info_cards() -> None:
	"""Render the top info cards shown under the hero section."""
	st.markdown(
		"""
		<div class='feature-grid'>
			<div class='feature-card'>
				<div class='feature-title'>Invisible Hiding</div>
				<div class='feature-desc'>Hides PNG bytes using 2-bit LSB across RGB channels.</div>
			</div>
			<div class='feature-card'>
				<div class='feature-title'>Password Protection</div>
				<div class='feature-desc'>Optional AES-GCM encryption of the secret payload.</div>
			</div>
			<div class='feature-card'>
				<div class='feature-title'>Local Export</div>
				<div class='feature-desc'>Download encoded and recovered PNGs locally; no external DB.</div>
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
				<h2 class='section-title'>{title}</h2>
				<p class='section-subtitle'>{subtitle}</p>
			</div>
			""",
			unsafe_allow_html=True,
		)
	else:
		st.markdown(f"<h2 class='section-title'>{title}</h2>", unsafe_allow_html=True)


def image_card(title: str, caption: str = "") -> None:
	if caption:
		st.markdown(
			f"""
			<div class='panel-card'>
				<div class='panel-heading'>{title}</div>
				<div class='panel-caption'>{caption}</div>
			</div>
			""",
			unsafe_allow_html=True,
		)
	else:
		st.markdown(
			f"""
			<div class='panel-card'>
				<div class='panel-heading'>{title}</div>
			</div>
			""",
			unsafe_allow_html=True,
		)


def metric_row(
	a_label: str,
	a_value: str,
	b_label: str,
	b_value: str,
	c_label: str,
	c_value: str,
) -> None:
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
		<div class='tip-card'>
			Tip: Use PNG for the encoded image. JPEG compression can damage hidden image data.
		</div>
		""",
		unsafe_allow_html=True,
	)
