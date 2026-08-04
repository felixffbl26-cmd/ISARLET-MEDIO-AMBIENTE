"""
AQUA-DAR PUNO v2.0 (Web Edition)
================================
Componentes de interfaz compartidos: CSS, topbar, hero, tarjetas, footer.
Estilo "ONG ambiental" (verde lima + verde bosque) adaptado a mineria
responsable en Puno, Peru.

Autoras: Maria Isabel Nayde Zevallos Ttito / Arlet Maricielo Espezua Cuentas
"""

from __future__ import annotations
import base64
from pathlib import Path
import streamlit as st

WEBAPP_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = WEBAPP_DIR.parent
LOGO_UNAP = REPO_ROOT / "unap.png"
LOGO_FIM = REPO_ROOT / "fim.png"
STYLE_CSS = WEBAPP_DIR / "assets" / "style.css"

AUTHORS = ["Maria Isabel Nayde Zevallos Ttito", "Arlet Maricielo Espezua Cuentas"]
COURSE = "Introduccion a la Ciencia de Datos"
FACULTY = "Facultad de Ingenieria de Minas (FIM)"
UNIVERSITY = "Universidad Nacional del Altiplano (UNA) - Puno"
SEMESTER = "VIII Semestre"


@st.cache_data(show_spinner=False)
def _b64(path_str: str) -> str | None:
    path = Path(path_str)
    if not path.exists():
        return None
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def logo_data_uri(which: str) -> str | None:
    path = LOGO_UNAP if which == "unap" else LOGO_FIM
    b64 = _b64(str(path))
    return f"data:image/png;base64,{b64}" if b64 else None


def inject_base_css():
    if STYLE_CSS.exists():
        st.markdown(f"<style>{STYLE_CSS.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
    st.markdown("""<style>.block-container{padding-top:1.6rem;}</style>""", unsafe_allow_html=True)


def render_topbar():
    unap_uri = logo_data_uri("unap")
    fim_uri = logo_data_uri("fim")
    logos_html = ""
    if unap_uri:
        logos_html += f'<img src="{unap_uri}" style="height:34px;margin-right:10px;">'
    if fim_uri:
        logos_html += f'<img src="{fim_uri}" style="height:34px;">'
    st.markdown(f"""
    <div class="aqd-topbar">
        <div class="aqd-topbar-brand">{logos_html}<span>&nbsp;AQUA-DAR&nbsp;PUNO</span></div>
        <div class="aqd-topbar-meta">
            <span>UNA - Puno | FIM</span>
            <span>Ciencia de Datos - VIII Semestre</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


_HERO_SVG_BG = """<svg viewBox="0 0 1200 500" preserveAspectRatio="xMidYMid slice"
     xmlns="http://www.w3.org/2000/svg" style="position:absolute;inset:0;width:100%;height:100%;">
  <defs>
    <linearGradient id="aqdSky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#2E6B52"/>
      <stop offset="100%" stop-color="#0F3226"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="500" fill="url(#aqdSky)"/>
  <circle cx="985" cy="115" r="65" fill="#8BC53F" opacity="0.30"/>
  <polygon points="0,500 0,320 150,190 300,340 430,220 600,360 760,230 900,350 1050,240 1200,330 1200,500"
           fill="#123A2C" opacity="0.92"/>
  <polygon points="0,500 0,400 200,300 380,400 560,300 760,410 950,300 1200,400 1200,500" fill="#0B2820"/>
  <rect x="148" y="150" width="9" height="66" fill="#8BC53F"/>
  <polygon points="128,150 178,150 153,112" fill="#8BC53F"/>
  <circle cx="290" cy="205" r="3.5" fill="#EAF3E9"/>
  <circle cx="330" cy="185" r="3.5" fill="#EAF3E9"/>
  <circle cx="370" cy="210" r="3.5" fill="#EAF3E9"/>
</svg>"""


def render_hero(tag: str, title: str, subtitle: str,
                 primary_page: str | None = None, primary_label: str = "Ir al Simulador",
                 secondary_page: str | None = None, secondary_label: str = "Ver Casos de Puno"):
    st.markdown(f"""
    <div class="aqd-hero">
        <div class="aqd-hero-bg">{_HERO_SVG_BG}</div>
        <div class="aqd-hero-overlay"></div>
        <div class="aqd-hero-content">
            <span class="aqd-hero-tag">{tag}</span>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if primary_page or secondary_page:
        cols = st.columns([1.1, 1.3, 3.6])
        if primary_page:
            with cols[0]:
                st.page_link(primary_page, label=primary_label, icon="🧪")
        if secondary_page:
            with cols[1]:
                st.page_link(secondary_page, label=secondary_label, icon="📜")


def render_section_header(eyebrow: str, title: str, subtitle: str = ""):
    st.markdown(f"""
    <div class="aqd-section-eyebrow">{eyebrow}</div>
    <h2 class="aqd-section-title">{title}</h2>
    {f'<p class="aqd-section-sub">{subtitle}</p>' if subtitle else ''}
    """, unsafe_allow_html=True)


def render_stats_row(stats: list[tuple[str, str]]):
    cols = st.columns(len(stats))
    for col, (value, label) in zip(cols, stats):
        with col:
            st.markdown(f"""
            <div class="aqd-stat">
                <div class="aqd-stat-value">{value}</div>
                <div class="aqd-stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)


def render_case_card(case: dict):
    hechos = "".join(f"<li>{h}</li>" for h in case.get("datos_clave", []))
    st.markdown(f"""
    <div class="aqd-card">
        <span class="aqd-badge">{case['categoria']}</span>
        <h4>{case['nombre']}</h4>
        <p><b>{case['tipo']}</b> &middot; {case['altitud']}</p>
        <p>{case['resumen']}</p>
        <ul style="color:var(--text-gray); font-size:0.84rem; padding-left:1.1rem; margin-top:0.6rem;">{hechos}</ul>
        <div class="aqd-card-meta">Fuente: <a href="{case['fuente_url']}" target="_blank">{case['fuente_label']}</a></div>
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    unap_uri = logo_data_uri("unap")
    fim_uri = logo_data_uri("fim")
    logos_html = ""
    if unap_uri:
        logos_html += f'<img src="{unap_uri}">'
    if fim_uri:
        logos_html += f'<img src="{fim_uri}">'
    st.markdown(f"""
    <div class="aqd-footer">
        <div>{logos_html}</div>
        <div class="aqd-footer-title">AQUA-DAR PUNO v2.0</div>
        <div>{COURSE} &middot; {FACULTY} &middot; {SEMESTER}</div>
        <div>{UNIVERSITY}</div>
        <div style="margin-top:0.5rem;">Autoras: {" &middot; ".join(AUTHORS)}</div>
        <div style="margin-top:0.8rem; font-size:0.76rem; opacity:0.8;">
            Proyecto academico sin fines de lucro &middot; Datos sinteticos calibrados con fuentes oficiales
            (SENAMHI, MINAM, MINEM) &middot; No sustituye un instrumento de gestion ambiental oficial.
        </div>
    </div>
    """, unsafe_allow_html=True)
