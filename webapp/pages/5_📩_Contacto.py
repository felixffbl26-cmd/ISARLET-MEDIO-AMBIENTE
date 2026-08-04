"""
AQUA-DAR PUNO v2.0 (Web Edition)
================================
Pagina Contacto: creditos, equipo y datos de referencia del curso.

Autoras: Maria Isabel Nayde Zevallos Ttito / Arlet Maricielo Espezua Cuentas
"""

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import streamlit as st

from utils.ui import (inject_base_css, render_topbar, render_section_header, render_footer,
                       AUTHORS, COURSE, FACULTY, UNIVERSITY, SEMESTER)

st.set_page_config(page_title="Contacto | AQUA-DAR PUNO", page_icon="📩", layout="wide")
inject_base_css()
render_topbar()

render_section_header("HABLEMOS", "CONTACTO Y CREDITOS",
                       "AQUA-DAR PUNO es un proyecto academico sin fines de lucro del "
                       "curso de Introduccion a la Ciencia de Datos.")

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
    <div class="aqd-card">
        <span class="aqd-badge">Equipo</span>
        <h4>Autoras del Proyecto</h4>
        <p>👩‍🎓 {AUTHORS[0]}<br>👩‍🎓 {AUTHORS[1]}</p>
        <p style="margin-top:0.8rem;">{FACULTY}<br>{UNIVERSITY}<br>{SEMESTER}</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="aqd-card">
        <span class="aqd-badge">Curso</span>
        <h4>{COURSE}</h4>
        <p>Este proyecto fue desarrollado como entregable final del curso, con enfoque en
        modelamiento predictivo, visualizacion interactiva y gestion ambiental aplicada a la
        mineria de la region Puno.</p>
    </div>
    """, unsafe_allow_html=True)

st.write("")

render_section_header("RETROALIMENTACION", "¿DUDAS, SUGERENCIAS O DATOS PARA MEJORAR EL MODELO?")
with st.form("form_contacto"):
    nombre = st.text_input("Nombre")
    correo = st.text_input("Correo electronico")
    mensaje = st.text_area("Mensaje o sugerencia (por ejemplo: datos reales de tu operacion minera)")
    enviado = st.form_submit_button("Enviar")
    if enviado:
        st.success("¡Gracias! Tu mensaje quedo registrado en esta sesion. "
                    "(Nota academica: este formulario es una demostracion de UI; para recibir "
                    "mensajes reales se recomienda conectar un servicio de correo o una hoja de calculo.)")
        st.write(f"**Nombre:** {nombre or '-'}  \n**Correo:** {correo or '-'}  \n**Mensaje:** {mensaje or '-'}")

render_footer()
