"""
AQUA-DAR PUNO v2.0 (Web Edition)
================================
Pagina Normativa y Casos: marco legal ambiental peruano aplicado a la
mineria, formalizacion (IGAFOM/REINFO) y casos reales documentados de
mineria y medio ambiente en la region Puno.

Autoras: Maria Isabel Nayde Zevallos Ttito / Arlet Maricielo Espezua Cuentas
"""

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import streamlit as st

from utils.ui import inject_base_css, render_topbar, render_section_header, render_case_card, render_footer
from engine.data_models import RegulatoryLimits
from engine.puno_datasets import CASE_STUDIES, CASE_CATEGORIES, REGULATORY_REFERENCES

st.set_page_config(page_title="Normativa y Casos | AQUA-DAR PUNO", page_icon="📜", layout="wide")
inject_base_css()
render_topbar()

render_section_header("MARCO AMBIENTAL PERUANO", "NORMATIVA, FORMALIZACION Y CASOS DE PUNO",
                       "El fin ultimo de AQUA-DAR PUNO: acercar la ciencia de datos a la gestion "
                       "ambiental responsable de la mineria en el altiplano.")

# --- Limites normativos --------------------------------------------------
st.markdown("#### 📐 Limites de Referencia para Metales Pesados en Agua")
limits = RegulatoryLimits()
tabla = [
    {"Parametro": "Hierro (Fe)", "LMP Efluente Minero (mg/L)": limits.lmp_fe_mgL,
     "ECA Agua Cat. 3 - Riego (mg/L)": limits.eca_cat3_fe_mgL},
    {"Parametro": "Cobre (Cu)", "LMP Efluente Minero (mg/L)": limits.lmp_cu_mgL,
     "ECA Agua Cat. 3 - Riego (mg/L)": limits.eca_cat3_cu_mgL},
    {"Parametro": "Zinc (Zn)", "LMP Efluente Minero (mg/L)": limits.lmp_zn_mgL,
     "ECA Agua Cat. 3 - Riego (mg/L)": limits.eca_cat3_zn_mgL},
]
st.dataframe(tabla, use_container_width=True, hide_index=True)
st.caption("LMP = Limite Maximo Permisible (punto de descarga). ECA = Estandar de Calidad Ambiental "
           "(cuerpo receptor de agua). Se recomienda verificar vigencia normativa en la fuente oficial.")

st.write("")

# --- Referencias normativas ------------------------------------------------
render_section_header("BASE LEGAL", "NORMAS CITADAS EN EL SIMULADOR")
cols = st.columns(len(REGULATORY_REFERENCES))
for col, ref in zip(cols, REGULATORY_REFERENCES):
    with col:
        st.markdown(f"""
        <div class="aqd-card">
            <span class="aqd-badge">{ref['norma']}</span>
            <h4 style="font-size:0.98rem;">{ref['titulo']}</h4>
            <p>{ref['detalle']}</p>
            <div class="aqd-card-meta"><a href="{ref['url']}" target="_blank">Ver fuente oficial</a></div>
        </div>
        """, unsafe_allow_html=True)

st.write("")

# --- IGAFOM / REINFO -------------------------------------------------------
render_section_header("FORMALIZACION MINERA", "¿QUE ES EL IGAFOM Y EL REINFO?")
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("""
    <div class="aqd-card">
        <h4>REINFO</h4>
        <p>El <b>Registro Integral de Formalizacion Minera</b> es el padron donde se inscriben los
        mineros artesanales y de pequena escala que buscan formalizar sus operaciones en Peru.
        Mantenerse activo en el REINFO exige cumplir progresivamente con requisitos tecnicos,
        ambientales y legales.</p>
    </div>
    """, unsafe_allow_html=True)
with col_b:
    st.markdown("""
    <div class="aqd-card">
        <h4>IGAFOM</h4>
        <p>El <b>Instrumento de Gestion Ambiental y Fiscalizacion para la Formalizacion</b> es el
        requisito ambiental de caracter extraordinario que deben aprobar los pequenos mineros y
        mineros artesanales para culminar su formalizacion. Incluye medidas correctivas y
        preventivas frente a los impactos ya generados.</p>
    </div>
    """, unsafe_allow_html=True)
st.markdown("""
<div class="aqd-note">🎯 AQUA-DAR PUNO busca apoyar este proceso: al simular el balance hidrico y el
DAR de un deposito, el minero o estudiante puede anticipar si su operacion cumpliria los LMP antes
de presentar su IGAFOM, y que medidas correctivas priorizar.</div>
""", unsafe_allow_html=True)

st.write("")
st.write("")

# --- Casos reales -----------------------------------------------------------
render_section_header("CASOS DOCUMENTADOS", "MINERIA Y MEDIO AMBIENTE EN PUNO",
                       "Cuatro operaciones reales de la region que ilustran distintos escenarios "
                       "ambientales: desde la mineria informal hasta la economia circular.")

filtro = st.radio("Filtrar por categoria", CASE_CATEGORIES, index=0, horizontal=True,
                   label_visibility="collapsed", key="filtro_casos_normativa")
casos_filtrados = CASE_STUDIES if filtro == "Todos" else [c for c in CASE_STUDIES if c["categoria"] == filtro]

grid_cols = st.columns(2)
for i, case in enumerate(casos_filtrados):
    with grid_cols[i % 2]:
        render_case_card(case)
        st.write("")

render_footer()
