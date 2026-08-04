"""
AQUA-DAR PUNO v2.0 (Web Edition)
================================
Pagina Simulador: inputs de configuracion + ejecucion + outputs interactivos.

Autoras: Maria Isabel Nayde Zevallos Ttito / Arlet Maricielo Espezua Cuentas
"""

import sys
from pathlib import Path
from dataclasses import replace

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import streamlit as st

from utils.ui import inject_base_css, render_topbar, render_section_header, render_footer
from engine.data_models import SimulationConfig, RegulatoryLimits
from engine.puno_datasets import (generate_climate_series, DEPOSIT_PRESETS,
                                   GEOCHEMISTRY_PRESETS, TREATMENT_PRESETS, CLIMATE_SOURCE)
from engine.hydro_engine import run_water_balance
from engine.geochem_engine import run_geochemistry_simulation
from engine.kpi_engine import (compute_kpis, compliance_summary, formalization_recommendations,
                                fig_water_balance, fig_ard_geochem, fig_kpis_dashboard,
                                fig_water_consumption_gauge)
from engine.report_builder import build_pdf_report

st.set_page_config(page_title="Simulador | AQUA-DAR PUNO", page_icon="🧪", layout="wide")
inject_base_css()
render_topbar()

render_section_header("HERRAMIENTA INTERACTIVA", "SIMULADOR DE BALANCE HIDRICO Y DAR",
                       "Configura tu deposito minero, ejecuta la simulacion y revisa los resultados "
                       "al instante. Todos los valores se pueden ajustar en 'Parametros avanzados'.")

if "sim_results" not in st.session_state:
    st.session_state.sim_results = None

# ---------------------------------------------------------------- INPUTS --
with st.form("form_simulacion"):
    st.markdown("#### 1. Configuracion General")
    c1, c2, c3 = st.columns(3)
    with c1:
        deposit_key = st.selectbox("Tipo de deposito", list(DEPOSIT_PRESETS.keys()))
    with c2:
        geochem_key = st.selectbox("Riesgo geoquimico", list(GEOCHEMISTRY_PRESETS.keys()))
    with c3:
        plant_key = st.selectbox("Planta de tratamiento", list(TREATMENT_PRESETS.keys()))

    c4, c5 = st.columns(2)
    with c4:
        start_year = st.number_input("Ano de inicio", min_value=2000, max_value=2100, value=2024, step=1)
    with c5:
        n_years = st.slider("Numero de anos a simular", min_value=1, max_value=20, value=5)

    with st.expander("⚙️ Parametros avanzados (opcional) — ajusta valores especificos de tu caso"):
        base_deposit = DEPOSIT_PRESETS[deposit_key]
        base_geochem = GEOCHEMISTRY_PRESETS[geochem_key]
        base_plant = TREATMENT_PRESETS[plant_key]

        st.markdown("**Deposito**")
        d1, d2, d3, d4 = st.columns(4)
        area_m2 = d1.number_input("Area (m2)", min_value=100.0, value=float(base_deposit.area_m2),
                                   step=1000.0, key=f"area_{deposit_key}")
        tonnage = d2.number_input("Tonelaje (t)", min_value=100.0, value=float(base_deposit.tonnage_material_t),
                                   step=1000.0, key=f"tonnage_{deposit_key}")
        runoff_c = d3.slider("Coef. escorrentia", 0.0, 1.0, float(base_deposit.runoff_coefficient), 0.01,
                              key=f"runoff_{deposit_key}")
        field_cap = d4.number_input("Capacidad de campo (mm)", min_value=1.0, value=float(base_deposit.field_capacity_mm),
                                     key=f"fieldcap_{deposit_key}")

        st.markdown("**Geoquimica**")
        g1, g2 = st.columns(2)
        pct_s = g1.slider("% Azufre total (piritico)", 0.0, 6.0, float(base_geochem.percent_sulfur), 0.1,
                           key=f"pcts_{geochem_key}")
        pct_c = g2.slider("% Carbonato (CaCO3 eq.)", 0.0, 8.0, float(base_geochem.percent_carbonate), 0.1,
                           key=f"pctc_{geochem_key}")

        st.markdown("**Planta de tratamiento**")
        p1, p2, p3, p4 = st.columns(4)
        capacity = p1.number_input("Capacidad (m3/dia)", min_value=1.0, value=float(base_plant.capacity_m3_dia),
                                    key=f"cap_{plant_key}")
        ore_rate = p2.number_input("Mineral procesado (t/dia)", min_value=1.0, value=float(base_plant.ore_processed_t_dia),
                                    key=f"ore_{plant_key}")
        fresh_water = p3.number_input("Agua fresca (m3/dia)", min_value=1.0, value=float(base_plant.fresh_water_intake_m3_dia),
                                       key=f"fw_{plant_key}")
        recycle = p4.slider("Tasa de reciclaje", 0.0, 1.0, float(base_plant.water_recycle_rate), 0.01,
                             key=f"recycle_{plant_key}")

    submitted = st.form_submit_button("🚀 Ejecutar Simulacion")

if submitted:
    with st.spinner("Generando clima sintetico y ejecutando los 3 modulos del gemelo digital..."):
        config = SimulationConfig(start_year=int(start_year), n_years=int(n_years))
        limits = RegulatoryLimits()

        deposit = replace(base_deposit, area_m2=area_m2, tonnage_material_t=tonnage,
                           runoff_coefficient=runoff_c, field_capacity_mm=field_cap)
        geochem = replace(base_geochem, percent_sulfur=pct_s, percent_carbonate=pct_c)
        plant = replace(base_plant, capacity_m3_dia=capacity, ore_processed_t_dia=ore_rate,
                         fresh_water_intake_m3_dia=fresh_water, water_recycle_rate=recycle)

        df_climate = generate_climate_series(config.start_year, config.n_years, seed=config.random_seed)
        df_water = run_water_balance(df_climate, deposit, config.latitude_deg)
        df_sim, aba = run_geochemistry_simulation(df_water, deposit, geochem)
        df_kpi = compute_kpis(df_sim, plant)
        summary = compliance_summary(df_kpi, limits)
        recs = formalization_recommendations(aba, summary)

        st.session_state.sim_results = dict(
            config=config, deposit=deposit, geochem=geochem, plant=plant, limits=limits,
            df_sim=df_sim, df_kpi=df_kpi, aba=aba, summary=summary, recs=recs,
        )
    st.success("Simulacion completada. Revisa los resultados abajo o ve al Dashboard para el detalle completo.")

st.markdown(f"""
<div class="aqd-note">📡 Clima calibrado con <b>{CLIMATE_SOURCE['label']}</b> — {CLIMATE_SOURCE['note']}
<a href="{CLIMATE_SOURCE['url']}" target="_blank">Ver fuente</a></div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------- OUTPUTS --
results = st.session_state.sim_results
if results is None:
    st.info("👆 Configura los parametros y presiona **Ejecutar Simulacion** para ver los resultados aqui.")
else:
    df_sim, df_kpi = results["df_sim"], results["df_kpi"]
    aba, summary, recs = results["aba"], results["summary"], results["recs"]
    limits = results["limits"]
    gen = summary.get("_general", {})

    st.markdown("#### 2. Resultados")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Clasificacion ABA", aba["clasificacion"].split(" (")[0])
    m2.metric("Capacidad de planta suficiente", f"{gen.get('pct_capacidad_suficiente', 0):.0f}%")
    m3.metric("Agua fresca", f"{gen.get('consumo_agua_fresca_m3_t', 0):.2f} m3/t")
    avg_compliance = sum(summary[m]["pct_cumplimiento"] for m in ("Fe", "Cu", "Zn") if m in summary) / 3
    m4.metric("Cumplimiento LMP promedio (Fe/Cu/Zn)", f"{avg_compliance:.0f}%")

    tab1, tab2, tab3 = st.tabs(["💧 Balance Hidrico", "🧪 Drenaje Acido (DAR)", "📊 KPIs y Cumplimiento"])
    with tab1:
        st.plotly_chart(fig_water_balance(df_sim), use_container_width=True)
    with tab2:
        st.plotly_chart(fig_ard_geochem(df_sim, limits), use_container_width=True)
    with tab3:
        st.plotly_chart(fig_kpis_dashboard(df_kpi, limits), use_container_width=True)
        st.plotly_chart(fig_water_consumption_gauge(gen.get("consumo_agua_fresca_m3_t", 0),
                                                      df_kpi["tasa_reciclaje_pct"].iloc[0]),
                         use_container_width=True)

    st.markdown("#### 3. Recomendaciones para Formalizacion (IGAFOM / REINFO)")
    for r in recs:
        st.markdown(f'<div class="aqd-note">💡 {r}</div>', unsafe_allow_html=True)

    st.markdown("#### 4. Exportar resultados")
    e1, e2 = st.columns(2)
    with e1:
        csv_bytes = df_kpi.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Descargar CSV de resultados", data=csv_bytes,
                            file_name="resultados_aquadar_puno.csv", mime="text/csv",
                            use_container_width=True)
    with e2:
        if st.button("📄 Generar Informe PDF", use_container_width=True):
            with st.spinner("Generando informe ejecutivo PDF..."):
                tmp_path = "/tmp/Informe_AQUA-DAR_Puno.pdf" if Path("/tmp").exists() else "Informe_AQUA-DAR_Puno.pdf"
                build_pdf_report(tmp_path, results["config"], results["deposit"], results["geochem"],
                                  results["plant"], limits, df_sim, df_kpi, aba, summary, recs)
                with open(tmp_path, "rb") as f:
                    st.session_state["pdf_bytes"] = f.read()
            st.success("Informe generado.")
        if st.session_state.get("pdf_bytes"):
            st.download_button("⬇️ Descargar Informe PDF", data=st.session_state["pdf_bytes"],
                                file_name="Informe_AQUA-DAR_Puno.pdf", mime="application/pdf",
                                use_container_width=True)

render_footer()
