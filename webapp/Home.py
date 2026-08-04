"""
AQUA-DAR PUNO v2.0 (Web Edition)
================================
Pagina de inicio (landing page).

Curso: Introduccion a la Ciencia de Datos - FIM - VIII Semestre
Universidad Nacional del Altiplano (UNA) - Puno
Autoras: Maria Isabel Nayde Zevallos Ttito / Arlet Mariciela Espezua Cuentas
"""

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import streamlit as st
from utils.ui import (inject_base_css, render_topbar, render_hero, render_section_header,
                       render_stats_row, render_case_card, render_footer)
from engine.puno_datasets import CASE_STUDIES, CASE_CATEGORIES

st.set_page_config(page_title="AQUA-DAR PUNO | Gemelo Digital Ambiental Minero",
                    page_icon="💧", layout="wide", initial_sidebar_state="expanded")

inject_base_css()
render_topbar()

render_hero(
    tag="Gemelo Digital para Mineria Responsable",
    title="Balance Hidrico y Drenaje Acido de Roca en la Mineria de Puno",
    subtitle="AQUA-DAR PUNO simula el flujo de agua y predice la calidad del efluente "
             "de depositos mineros del altiplano, para apoyar la formalizacion y la "
             "gestion ambiental responsable en la region.",
    primary_page="pages/1_🧪_Simulador.py", primary_label="Ir al Simulador",
    secondary_page="pages/3_📜_Normativa_y_Casos.py", secondary_label="Ver Casos de Puno",
)

st.write("")
render_stats_row([
    ("4+", "Casos reales de mineria en Puno documentados"),
    ("3", "Modulos cientificos: Hidrologia, Geoquimica y KPIs"),
    ("2", "Normas ambientales peruanas verificadas (LMP / ECA)"),
    ("20", "Anos de operacion simulables mes a mes"),
])

st.write("")
st.write("")

# --- Sobre el proyecto (preview 60/40) --------------------------------
col_text, col_visual = st.columns([1.3, 1])
with col_text:
    st.markdown('<span class="aqd-badge">SOBRE AQUA-DAR PUNO</span>', unsafe_allow_html=True)
    st.markdown("## GEMELO DIGITAL AMBIENTAL PARA EL ALTIPLANO")
    st.markdown("""
    <p style="color:var(--text-gray); font-size:1rem; line-height:1.6;">
    Este proyecto academico integra hidrologia, geoquimica y ciencia de datos para modelar
    el <b>balance hidrico</b> (precipitacion, evapotranspiracion, infiltracion) y predecir la
    <b>lixiviacion de metales pesados y pH</b> de un deposito de desmonte o relaves mineros,
    calibrado con datos climaticos y normativos reales de Puno.
    </p>
    <p style="color:var(--text-gray); font-size:1rem; line-height:1.6;">
    Su objetivo es servir como herramienta educativa y de apoyo para procesos de
    <b>formalizacion minera (IGAFOM / REINFO)</b>, mostrando de forma clara si un
    deposito cumple con los <b>Limites Maximos Permisibles</b> peruanos.
    </p>
    """, unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        st.page_link("pages/4_🎓_Sobre_el_Proyecto.py", label="Conoce el Proyecto", icon="🎓")
    with b2:
        st.page_link("pages/1_🧪_Simulador.py", label="Probar el Simulador", icon="🧪")
with col_visual:
    st.markdown("""
    <div class="aqd-card" style="text-align:center; padding:2.2rem 1.2rem;">
        <div style="font-size:3.2rem;">💧⛏️🌱</div>
        <h4 style="margin-top:0.8rem;">Mineria + Agua + Ambiente</h4>
        <p>Un modelo, tres dimensiones: hidrologia, geoquimica y cumplimiento normativo,
        integradas en un solo gemelo digital.</p>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.write("")

# --- Modulos / servicios (3 columnas) -----------------------------------
render_section_header("QUE HACE AQUA-DAR PUNO", "TRES MODULOS, UN SOLO GEMELO DIGITAL",
                       "Cada modulo resuelve una parte del ciclo ambiental de un deposito minero altoandino.")

c1, c2, c3 = st.columns(3)
modules = [
    ("💧", "Balance Hidrico", "Precipitacion, evapotranspiracion (Thornthwaite) e infiltracion "
     "mensual, calibradas con el clima real del altiplano puneno."),
    ("🧪", "Drenaje Acido de Roca", "Balance Acido-Base, cinetica de oxidacion de pirita y "
     "prediccion de pH y metales pesados (Fe, Cu, Zn) en el lixiviado."),
    ("📊", "KPIs y Cumplimiento", "Efluente tratado vs. no tratado, consumo de agua fresca por "
     "tonelada y comparacion automatica contra el LMP/ECA peruano."),
]
for col, (icon, title, desc) in zip((c1, c2, c3), modules):
    with col:
        st.markdown(f"""
        <div class="aqd-card">
            <div style="font-size:2.2rem;">{icon}</div>
            <h4>{title}</h4>
            <p>{desc}</p>
        </div>
        """, unsafe_allow_html=True)

st.write("")
st.write("")

# --- Casos recientes (grid con filtro) -----------------------------------
render_section_header("CASOS REALES", "MINERIA Y MEDIO AMBIENTE EN PUNO",
                       "Casos documentados con fuentes oficiales que inspiran los parametros del simulador.")

filtro = st.radio("Filtrar por categoria", CASE_CATEGORIES, index=0, horizontal=True,
                   label_visibility="collapsed")
casos_filtrados = CASE_STUDIES if filtro == "Todos" else [c for c in CASE_STUDIES if c["categoria"] == filtro]

st.write("")
grid_cols = st.columns(2)
for i, case in enumerate(casos_filtrados):
    with grid_cols[i % 2]:
        render_case_card(case)
        st.write("")

st.write("")
st.markdown("""
<div class="aqd-card" style="text-align:center; background: linear-gradient(120deg,#1B4D3E,#23604D); border:none;">
    <h3 style="color:white; text-transform:uppercase;">Listo para simular tu propio deposito minero?</h3>
    <p style="color:#E7F1E9;">Configura el clima, la geoquimica y la planta de tratamiento, y obten un
    informe ejecutivo en PDF en minutos.</p>
</div>
""", unsafe_allow_html=True)
st.write("")
_, cta_col, _ = st.columns([2, 1.4, 2])
with cta_col:
    st.page_link("pages/1_🧪_Simulador.py", label="Comenzar Simulacion", icon="🚀")

render_footer()
