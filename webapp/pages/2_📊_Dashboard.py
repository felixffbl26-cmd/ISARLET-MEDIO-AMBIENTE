"""
AQUA-DAR PUNO v2.0 (Web Edition)
================================
Pagina Dashboard: vista ampliada de KPIs, semaforo de cumplimiento y
recomendaciones de formalizacion, a partir de la ultima simulacion
ejecutada en la pagina Simulador.

Autoras: Maria Isabel Nayde Zevallos Ttito / Arlet Maricielo Espezua Cuentas
"""

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import streamlit as st

from utils.ui import inject_base_css, render_topbar, render_section_header, render_footer
from engine.kpi_engine import fig_water_balance, fig_ard_geochem, fig_kpis_dashboard

st.set_page_config(page_title="Dashboard | AQUA-DAR PUNO", page_icon="📊", layout="wide")
inject_base_css()
render_topbar()

render_section_header("VISTA AMPLIADA", "DASHBOARD DE CUMPLIMIENTO AMBIENTAL",
                       "Semaforo normativo, balance acido-base y recomendaciones detalladas.")

results = st.session_state.get("sim_results")
if results is None:
    st.warning("Aun no has ejecutado ninguna simulacion.")
    st.page_link("pages/1_🧪_Simulador.py", label="Ir al Simulador para generar resultados", icon="🧪")
    render_footer()
    st.stop()

df_sim, df_kpi = results["df_sim"], results["df_kpi"]
aba, summary, recs = results["aba"], results["summary"], results["recs"]
limits, deposit, geochem, plant = results["limits"], results["deposit"], results["geochem"], results["plant"]
gen = summary.get("_general", {})

st.markdown(f"##### Proyecto: {results['config'].project_name} &middot; Deposito: {deposit.name}")
st.write("")

# --- Semaforo de cumplimiento ------------------------------------------
st.markdown("#### 🚦 Semaforo de Cumplimiento Normativo (LMP D.S. 010-2010-MINAM)")
cols = st.columns(3)
for col, metal in zip(cols, ("Fe", "Cu", "Zn")):
    if metal not in summary:
        continue
    s = summary[metal]
    pct = s["pct_cumplimiento"]
    color = "#2F9E44" if pct == 100 else ("#F08C00" if pct >= 50 else "#E03131")
    estado = "Cumple todo el periodo" if pct == 100 else ("Cumplimiento parcial" if pct >= 50 else "Incumplimiento frecuente")
    with col:
        st.markdown(f"""
        <div class="aqd-card" style="border-top: 6px solid {color};">
            <span class="aqd-badge">{metal}</span>
            <h4>{pct:.0f}% de cumplimiento</h4>
            <p>{estado}<br>Limite LMP: {s['limite_lmp_mgL']} mg/L &middot;
            Maximo simulado: {s['concentracion_max_mgL']} mg/L<br>
            Meses excedidos: {s['meses_excedidos']} de {s['meses_totales']}</p>
        </div>
        """, unsafe_allow_html=True)

st.write("")
cap_color = "#2F9E44" if gen.get("pct_capacidad_suficiente", 0) == 100 else "#F08C00"
st.markdown(f"""
<div class="aqd-card" style="border-top: 6px solid {cap_color};">
    <span class="aqd-badge">Capacidad de Planta</span>
    <h4>{gen.get('pct_capacidad_suficiente', 0):.0f}% de los meses con tratamiento suficiente</h4>
    <p>Meses con efluente NO tratado: {gen.get('meses_con_efluente_no_tratado', 0)} de {gen.get('meses_totales', 0)}
    &middot; Capacidad de planta: {plant.capacity_m3_dia:.0f} m3/dia</p>
</div>
""", unsafe_allow_html=True)

st.write("")

# --- Balance Acido-Base detallado ---------------------------------------
render_section_header("GEOQUIMICA", "BALANCE ACIDO-BASE (ABA) DEL MATERIAL")
a1, a2, a3, a4 = st.columns(4)
a1.metric("Potencial Acido (AP)", f"{aba['AP_kg_CaCO3_t']:.1f} kg CaCO3-eq/t")
a2.metric("Cap. Neutralizacion (ANC)", f"{aba['ANC_kg_CaCO3_t']:.1f} kg CaCO3-eq/t")
a3.metric("Potencial Neto (NAPP)", f"{aba['NAPP_kg_CaCO3_t']:.1f} kg CaCO3-eq/t")
a4.metric("Relacion ANC/AP", f"{aba['ratio_ANC_AP']:.2f}")
st.markdown(f'<div class="aqd-note">🧭 Clasificacion geoquimica: <b>{aba["clasificacion"]}</b></div>',
            unsafe_allow_html=True)

st.write("")

# --- Graficos completos ---------------------------------------------------
render_section_header("SERIES DE TIEMPO", "RESULTADOS COMPLETOS DE LA SIMULACION")
st.plotly_chart(fig_water_balance(df_sim), use_container_width=True)
st.plotly_chart(fig_ard_geochem(df_sim, limits), use_container_width=True)
st.plotly_chart(fig_kpis_dashboard(df_kpi, limits), use_container_width=True)

st.write("")

# --- Tabla de datos ---------------------------------------------------------
with st.expander("📋 Ver tabla de datos mensuales completa"):
    cols_to_show = ["date", "precip_mm", "temp_mean_c", "etp_mm", "percolation_mm",
                     "pH_lixiviado", "Fe_mgL", "Cu_mgL", "Zn_mgL",
                     "efluente_tratado_m3_dia", "efluente_no_tratado_m3_dia"]
    cols_present = [c for c in cols_to_show if c in df_kpi.columns]
    st.dataframe(df_kpi[cols_present], use_container_width=True, hide_index=True)

st.write("")

# --- Recomendaciones -------------------------------------------------------
render_section_header("SIGUIENTE PASO", "RECOMENDACIONES PARA FORMALIZACION (IGAFOM / REINFO)")
for r in recs:
    st.markdown(f'<div class="aqd-note">💡 {r}</div>', unsafe_allow_html=True)

render_footer()
