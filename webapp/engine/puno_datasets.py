"""
AQUA-DAR PUNO v2.0 (Web Edition)
================================
Datasets de referencia: clima calibrado con fuentes oficiales, presets
mineros y casos reales de la region Puno con fuentes citadas.

Clima: la precipitacion de enero (mes mas lluvioso) se calibro con el
boletin climatico oficial de SENAMHI para Puno (173.72 mm/mes); el resto
de meses distribuye la precipitacion siguiendo el patron estacional
tipico del altiplano (humedo Dic-Mar, seco May-Ago), escalado de forma
proporcional. Fuente: SENAMHI, Boletin Regional de Puno.
https://www.senamhi.gob.pe/load/file/04701SENA-98.pdf

Autoras: Maria Isabel Nayde Zevallos Ttito / Arlet Maricielo Espezua Cuentas
"""

from __future__ import annotations
import numpy as np
import pandas as pd

from engine.data_models import ClimateRecord, DepositProperties, GeochemistryParams, TreatmentPlant


PUNO_CLIMATE_NORMALS = [
    {"month": 1,  "precip_mm": 173.7, "temp_c": 9.5},
    {"month": 2,  "precip_mm": 144.3, "temp_c": 9.4},
    {"month": 3,  "precip_mm": 122.3, "temp_c": 9.3},
    {"month": 4,  "precip_mm": 52.6,  "temp_c": 8.5},
    {"month": 5,  "precip_mm": 9.8,   "temp_c": 6.0},
    {"month": 6,  "precip_mm": 6.1,   "temp_c": 4.2},
    {"month": 7,  "precip_mm": 6.1,   "temp_c": 3.8},
    {"month": 8,  "precip_mm": 14.7,  "temp_c": 5.5},
    {"month": 9,  "precip_mm": 26.9,  "temp_c": 7.8},
    {"month": 10, "precip_mm": 55.0,  "temp_c": 9.3},
    {"month": 11, "precip_mm": 70.9,  "temp_c": 10.0},
    {"month": 12, "precip_mm": 133.3, "temp_c": 9.8},
]

CLIMATE_SOURCE = {
    "label": "SENAMHI - Boletin Regional de Puno / SIAR Puno (MINAM)",
    "url": "https://www.senamhi.gob.pe/load/file/04701SENA-98.pdf",
    "note": "Precipitacion de enero (mes mas lluvioso) calibrada a 173.72 mm/mes "
            "segun boletin oficial. El resto de meses distribuye la estacionalidad "
            "tipica del altiplano de forma proporcional (dataset sintetico con fines academicos).",
}


def generate_climate_series(start_year: int, n_years: int, seed: int | None = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    records: list[ClimateRecord] = []
    enso_phase = rng.normal(0.0, 0.18, size=n_years)

    for i in range(n_years):
        year = start_year + i
        wet_dry_factor = 1.0 + enso_phase[i]
        for normal in PUNO_CLIMATE_NORMALS:
            precip_noise = rng.normal(1.0, 0.20)
            precip = max(0.0, normal["precip_mm"] * wet_dry_factor * precip_noise)
            temp_noise = rng.normal(0.0, 0.6)
            temp = normal["temp_c"] + temp_noise
            records.append(ClimateRecord(year=year, month=normal["month"],
                                          precip_mm=round(precip, 2),
                                          temp_mean_c=round(temp, 2)))

    df = pd.DataFrame([r.__dict__ for r in records])
    df["date"] = pd.to_datetime(dict(year=df.year, month=df.month, day=1))
    df = df.sort_values("date").reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# Presets mineros
# ---------------------------------------------------------------------------

DEPOSIT_PRESETS = {
    "Desmonte de Mina Aurifera (tipo Ananea / La Rinconada)": DepositProperties(
        name="Desmonte de Mina Aurifera (tipo Ananea / La Rinconada)",
        area_m2=50_000.0, tonnage_material_t=500_000.0,
        runoff_coefficient=0.35, field_capacity_mm=40.0,
        initial_storage_mm=10.0, percolation_reference_mm=15.0,
    ),
    "Deposito de Relaves - Planta Concentradora Polimetalica (tipo Corani)": DepositProperties(
        name="Deposito de Relaves - Planta Concentradora Polimetalica (tipo Corani)",
        area_m2=30_000.0, tonnage_material_t=800_000.0,
        runoff_coefficient=0.15, field_capacity_mm=60.0,
        initial_storage_mm=20.0, percolation_reference_mm=20.0,
    ),
    "Pila de Lixiviacion / Ripios (Mineria Artesanal, formalizacion REINFO)": DepositProperties(
        name="Pila de Lixiviacion / Ripios (Mineria Artesanal, formalizacion REINFO)",
        area_m2=8_000.0, tonnage_material_t=60_000.0,
        runoff_coefficient=0.25, field_capacity_mm=35.0,
        initial_storage_mm=8.0, percolation_reference_mm=12.0,
    ),
}

GEOCHEMISTRY_PRESETS = {
    "Alto Riesgo DAR (Sulfuros Masivos, Bajo ANC)": GeochemistryParams(
        percent_sulfur=3.5, percent_carbonate=0.5,
    ),
    "Riesgo Moderado (Sulfuros Diseminados)": GeochemistryParams(
        percent_sulfur=1.8, percent_carbonate=1.5,
    ),
    "Bajo Riesgo (Buffer Carbonatado)": GeochemistryParams(
        percent_sulfur=0.5, percent_carbonate=5.0,
    ),
}

TREATMENT_PRESETS = {
    "Planta Pequena Minera / Formalizacion REINFO": TreatmentPlant(
        capacity_m3_dia=60.0, ore_processed_t_dia=80.0,
        fresh_water_intake_m3_dia=95.0, water_recycle_rate=0.55,
    ),
    "Planta Mediana Mineria Polimetalica": TreatmentPlant(
        capacity_m3_dia=180.0, ore_processed_t_dia=450.0,
        fresh_water_intake_m3_dia=320.0, water_recycle_rate=0.65,
    ),
    "Planta con Economia Circular (tipo San Rafael)": TreatmentPlant(
        capacity_m3_dia=260.0, ore_processed_t_dia=520.0,
        fresh_water_intake_m3_dia=140.0, water_recycle_rate=0.93,
    ),
}


def default_project_bundle():
    deposit = DEPOSIT_PRESETS["Desmonte de Mina Aurifera (tipo Ananea / La Rinconada)"]
    geochem = GEOCHEMISTRY_PRESETS["Alto Riesgo DAR (Sulfuros Masivos, Bajo ANC)"]
    plant = TREATMENT_PRESETS["Planta Pequena Minera / Formalizacion REINFO"]
    return deposit, geochem, plant


# ---------------------------------------------------------------------------
# Casos reales de mineria y medio ambiente en Puno (con fuentes citadas)
# ---------------------------------------------------------------------------

CASE_STUDIES = [
    {
        "nombre": "La Rinconada - Ananea",
        "categoria": "Contaminacion por Mercurio",
        "tipo": "Mineria artesanal / informal",
        "altitud": "~5,200 msnm (centro poblado minero mas alto del mundo)",
        "resumen": "Explotacion aurifera artesanal e informal donde el oro se recupera "
                   "por amalgamacion con mercurio. Mas del 50% del mercurio usado se "
                   "libera al ambiente; los relaves llegan a la laguna La Rinconada y "
                   "de ahi a la cuenca del rio Ramis, que desemboca en el Lago Titicaca.",
        "datos_clave": [
            "Cerca de 450 contratistas informales operan bajo la Corporacion Minera Ananea S.A.",
            "El centro poblado no cuenta con agua potable, desague ni relleno sanitario.",
            "Los relaves con mercurio afectan la cuenca alta del rio Ramis.",
        ],
        "fuente_label": "Repositorio UNAP / Redalyc / La Republica",
        "fuente_url": "https://repositorio.unap.edu.pe/handle/20.500.14082/1908",
    },
    {
        "nombre": "Corani (Bear Creek Mining)",
        "categoria": "Mineria Formal y Gestion del Agua",
        "tipo": "Mineria formal a gran escala (Ag-Pb-Zn)",
        "altitud": "~4,800 msnm",
        "resumen": "Proyecto polimetalico de plata, plomo y zinc con Estudio de Impacto "
                   "Ambiental aprobado. Contempla inversion en reservorios de agua para "
                   "comunidades vecinas y estudios de balance hidrologico para la etapa "
                   "de cierre de mina.",
        "datos_clave": [
            "EIA aprobado por Resolucion Directoral N 355-2013-MEM-AAM (set. 2013).",
            "Inversion proyectada de US$ 40 millones en reservorios de agua.",
            "Vida util proyectada de 20 anos; inicio de obras previsto para 2024.",
        ],
        "fuente_label": "MINEM / RPP / Bear Creek Mining Corp.",
        "fuente_url": "https://www.minem.gob.pe/descripcion.php?idSector=4&idTitular=5721",
    },
    {
        "nombre": "San Rafael (Minsur)",
        "categoria": "Economia Circular y Relaves",
        "tipo": "Mineria formal subterranea (estano)",
        "altitud": "Puno, operacion subterranea de gran escala",
        "resumen": "Una de las minas de estano mas importantes del mundo (12% de la "
                   "produccion global). Su Planta de Reaprovechamiento de Relaves B2 "
                   "recupera estano de relaves antiguos sin nuevas extracciones, un "
                   "ejemplo de economia circular en mineria.",
        "datos_clave": [
            "3er productor mundial de estano; produce ~12% del estano del mundo.",
            "La planta B2 recupero 18,805 toneladas de estano de relaves historicos.",
            "Recicla 93% del agua de proceso; certificada ISO 14001, 9001, 45001 y 37001.",
        ],
        "fuente_label": "Minsur / El Comercio - Peru Sostenible / Rumbo Minero",
        "fuente_url": "https://especial.elcomercio.pe/perusostenible/mina-san-rafael-transformando-residuos-en-riqueza/",
    },
    {
        "nombre": "Arasi (Aruntani S.A.C.) - Ocuviri",
        "categoria": "Drenaje Acido de Roca",
        "tipo": "Mineria formal con impactos reportados (oro)",
        "altitud": "Provincia de Lampa / Melgar, Puno",
        "resumen": "Unidad minera aurifera cuyo efluente ha sido asociado por OEFA con "
                   "aguas acidas de alto contenido de metales, afectando la cuenca del "
                   "rio Llallimayo y comunidades de varios distritos de Puno.",
        "datos_clave": [
            "OEFA certifico presencia de aluminio, cobalto, cobre, hierro y manganeso "
            "en aguas subterraneas acidas asociadas a la operacion.",
            "Impacto reportado en los distritos de Ocuviri, Llalli, Umachiri, Cupi y Ayaviri.",
            "Caso referente de conflicto socioambiental minero en el sur peruano.",
        ],
        "fuente_label": "OCMAL / Observatorio de DD.HH. Puno / Servindi",
        "fuente_url": "https://www.ocmal.org/rios-de-puno-son-contaminados-por-mina-arasi/",
    },
]

CASE_CATEGORIES = ["Todos"] + sorted({c["categoria"] for c in CASE_STUDIES})


REGULATORY_REFERENCES = [
    {
        "norma": "D.S. N 010-2010-MINAM",
        "titulo": "Limites Maximos Permisibles (LMP) para la descarga de efluentes "
                   "liquidos de actividades minero-metalurgicas",
        "detalle": "Fe disuelto 2.0 mg/L, Cu total 0.5 mg/L, Zn total 1.5 mg/L, "
                    "SST 50 mg/L, pH entre 6 y 9 (valor en cualquier momento).",
        "url": "https://sinia.minam.gob.pe/normas/aprueban-limites-maximos-permisibles-descarga-efluentes-liquidos",
    },
    {
        "norma": "D.S. N 004-2017-MINAM",
        "titulo": "Estandares de Calidad Ambiental (ECA) para Agua - Categoria 3 "
                   "(riego de vegetales y bebida de animales)",
        "detalle": "Fe 5.0 mg/L, Cu 0.2 mg/L, Zn 2.0 mg/L.",
        "url": "https://www.minam.gob.pe/disposiciones/decreto-supremo-n-004-2017-minam/",
    },
    {
        "norma": "D.S. N 038-2017-EM (Reglamento IGAFOM)",
        "titulo": "Instrumento de Gestion Ambiental para la Formalizacion de "
                   "Actividades de Pequena Mineria y Mineria Artesanal (IGAFOM)",
        "detalle": "Requisito ambiental de caracter extraordinario para culminar el "
                    "Proceso de Formalizacion Minera Integral (REINFO).",
        "url": "https://formalizacionminera.minem.gob.pe/",
    },
]
