"""
AQUA-DAR PUNO v2.0 (Web Edition)
================================
Pagina Sobre el Proyecto: equipo, curso, metodologia y creditos.

Autoras: Maria Isabel Nayde Zevallos Ttito / Arlet Mariciela Espezua Cuentas
"""

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import streamlit as st

from utils.ui import (inject_base_css, render_topbar, render_section_header, render_footer,
                       logo_data_uri, AUTHORS, COURSE, FACULTY, UNIVERSITY, SEMESTER)

st.set_page_config(page_title="Sobre el Proyecto | AQUA-DAR PUNO", page_icon="🎓", layout="wide")
inject_base_css()
render_topbar()

render_section_header("QUIENES SOMOS", "SOBRE AQUA-DAR PUNO",
                       "Un proyecto academico de la Facultad de Ingenieria de Minas de la UNA - Puno.")

unap_uri = logo_data_uri("unap")
fim_uri = logo_data_uri("fim")
lcol, rcol = st.columns([1, 2])
with lcol:
    st.markdown(f"""
    <div class="aqd-card" style="text-align:center;">
        {'<img src="' + unap_uri + '" style="height:80px;margin:0.4rem;">' if unap_uri else ''}
        {'<img src="' + fim_uri + '" style="height:80px;margin:0.4rem;">' if fim_uri else ''}
        <h4 style="margin-top:1rem;">{UNIVERSITY}</h4>
        <p>{FACULTY}<br>{SEMESTER}</p>
    </div>
    """, unsafe_allow_html=True)
with rcol:
    st.markdown(f"""
    <div class="aqd-card">
        <span class="aqd-badge">Curso</span>
        <h4>{COURSE}</h4>
        <p>AQUA-DAR PUNO es el proyecto final del curso de Introduccion a la Ciencia de Datos, que
        integra hidrologia, geoquimica ambiental, normativa peruana y visualizacion interactiva de
        datos en una sola aplicacion web, con el objetivo de acercar herramientas predictivas a la
        gestion ambiental de la mineria en Puno.</p>
        <p><b>Autoras:</b> {" y ".join(AUTHORS)}</p>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# --- Objetivo -------------------------------------------------------------
render_section_header("OBJETIVO", "MODELAR EL BALANCE HIDRICO Y EL DRENAJE ACIDO DE ROCA")
st.markdown("""
<div class="aqd-card">
<p>El objetivo central es <b>modelar el flujo de agua en depositos de desmonte/relaves mineros</b>
(precipitacion, evaporacion, infiltracion) y <b>predecir la lixiviacion de metales pesados y el pH</b>
a lo largo del tiempo, combinando un balance de masa de agua con tasas de oxidacion de pirita, para
calcular tres indicadores clave:</p>
<ul style="color:var(--text-gray);">
<li>Volumen de efluente tratado vs. no tratado (m3/dia).</li>
<li>Concentracion esperada de metales pesados (mg/L de Fe, Cu, Zn).</li>
<li>Consumo de agua fresca por tonelada procesada (m3/t).</li>
</ul>
</div>
""", unsafe_allow_html=True)

st.write("")

# --- Metodologia (3 columnas) ---------------------------------------------
render_section_header("METODOLOGIA", "TRES MODULOS CIENTIFICOS INTEGRADOS")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div class="aqd-card">
        <div style="font-size:2rem;">💧</div>
        <h4>Balance Hidrico</h4>
        <p>Evapotranspiracion potencial por el metodo de <b>Thornthwaite</b>, corregida
        astronomicamente para la latitud de Puno, acoplada a un modelo de balance hidrico tipo
        "bucket" para estimar infiltracion y percolacion mensual.</p>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown("""
    <div class="aqd-card">
        <div style="font-size:2rem;">🧪</div>
        <h4>Drenaje Acido de Roca</h4>
        <p><b>Balance Acido-Base</b> (AP, ANC, NAPP) y cinetica de oxidacion de pirita de primer
        orden modulada por temperatura y humedad, con un modelo sigmoidal de pH y liberacion
        empirica de Fe, Cu y Zn.</p>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown("""
    <div class="aqd-card">
        <div style="font-size:2rem;">📊</div>
        <h4>KPIs y Normativa</h4>
        <p>Calculo automatico de KPIs ambientales y comparacion contra el <b>LMP D.S. 010-2010-MINAM</b>
        y el <b>ECA Agua D.S. 004-2017-MINAM</b>, con recomendaciones para IGAFOM/REINFO.</p>
    </div>
    """, unsafe_allow_html=True)

st.write("")

st.markdown("""
<div class="aqd-note">⚠️ Los datos climaticos y geoquimicos utilizados son sinteticos, calibrados con
fuentes oficiales (SENAMHI, MINAM, MINEM) con fines academicos. Para un instrumento de gestion
ambiental oficial (EIA / IGAFOM) deben reemplazarse por datos reales de estacion meteorologica y
resultados de laboratorio (ABA/NAG) del sitio especifico.</div>
""", unsafe_allow_html=True)

render_footer()
