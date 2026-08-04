# AQUA-DAR PUNO v2.0 (Web Edition)

**Gemelo Digital de Balance Hídrico y Predicción de Drenaje Ácido de Roca (DAR)**
para depósitos mineros del altiplano de Puno — versión web interactiva (Streamlit).

| | |
|---|---|
| **Curso** | Introducción a la Ciencia de Datos |
| **Facultad** | Facultad de Ingeniería de Minas (FIM) |
| **Universidad** | Universidad Nacional del Altiplano (UNA) – Puno |
| **Semestre** | VIII Semestre |
| **Autoras** | Maria Isabel Nayde Zevallos Ttito · Arlet Mariciela Espezua Cuentas |

## Estructura

```
webapp/
├── Home.py                       -> Landing page (hero, stats, casos de Puno)
├── pages/
│   ├── 1_🧪_Simulador.py          -> Inputs + ejecucion + outputs interactivos
│   ├── 2_📊_Dashboard.py           -> KPIs ampliados, semaforo de cumplimiento
│   ├── 3_📜_Normativa_y_Casos.py    -> LMP/ECA, IGAFOM/REINFO, casos reales de Puno
│   ├── 4_🎓_Sobre_el_Proyecto.py     -> Equipo, metodologia, creditos
│   └── 5_📩_Contacto.py               -> Formulario de contacto
├── engine/                          -> Motores de calculo (hidrologia, geoquimica, KPIs, PDF)
├── utils/ui.py                       -> Componentes de interfaz (CSS, hero, cards, footer)
├── assets/style.css                   -> Sistema de diseno (verde lima + verde bosque)
├── .streamlit/config.toml              -> Tema de Streamlit
└── requirements.txt
```

Los logos institucionales (`fim.png`, `unap.png`) se leen desde la raíz del repositorio
(un nivel arriba de `webapp/`), para no duplicar archivos binarios.

## Ejecutar en local

```bash
cd webapp
pip install -r requirements.txt
streamlit run Home.py
```

## Desplegar en Streamlit Community Cloud (gratis)

1. Sube este repositorio completo a GitHub (incluyendo la carpeta `webapp/` y los
   archivos `fim.png` / `unap.png` en la raíz).
2. Entra a [share.streamlit.io](https://share.streamlit.io) con tu cuenta de GitHub.
3. Click en **"New app"**, selecciona el repositorio y la rama.
4. En **"Main file path"** escribe: `webapp/Home.py`
5. Click en **"Deploy"**. En 1-2 minutos tendrás una URL pública para compartir con el docente.

## Fuentes de datos y normativa citadas

- Clima: SENAMHI – Boletín Regional de Puno.
- LMP efluentes minero-metalúrgicos: D.S. N° 010-2010-MINAM.
- ECA Agua (Categoría 3): D.S. N° 004-2017-MINAM.
- IGAFOM: D.S. N° 038-2017-EM.
- Casos de Puno: repositorios UNAP, MINEM, Minsur, OCMAL (ver citas dentro de la app).
