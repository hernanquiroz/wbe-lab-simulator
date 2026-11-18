# 🧪 Simulador de Laboratorio WBE: Detección de Psicoactivos en Aguas Residuales

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.36+-red.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.20+-orange.svg)](https://plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Aplicación web interactiva diseñada para apoyar prácticas de laboratorio de **pregrado y posgrado** en Química Analítica, Toxicología e Ingeniería Ambiental. Simula el proceso completo de la **Epidemiología Basada en Aguas Residuales (WBE)**, desde la extracción de la muestra hasta el retrocálculo del consumo poblacional.

> 🇨🇴 **Contexto:** Desarrollado con base en los protocolos y estudios realizados en Colombia (PTAR San Fernando en Medellín, PTAR Salitre en Bogotá y ciudades del Eje Cafetero).

---

## 🚀 Características Principales

1. **🎬 Animación del Proceso SPE:** Visualización animada paso a paso de la Extracción en Fase Sólida con cartuchos HLB (acondicionamiento, carga, lavado, secado, elución y concentración). Incluye modo automático y manual.
2. **📊 Cromatograma Interactivo:** Simulador de cromatografía (HPLC-UV / LC-MS) donde se ajustan concentración, ruido y resolución para observar su efecto en el pico de la Benzoilecgonina.
3. **🧮 Calculadora de Recuperación:** Ingreso de datos experimentales para calcular automáticamente la concentración final y el porcentaje de recuperación del método.
4. **🌍 Retrocálculo Epidemiológico:** Estimación de la carga másica normalizada (mg/día/1000 habitantes) con la fórmula del EMCDDA, comparada gráficamente con datos reales de ciudades colombianas.

---

## 🛠️ Tecnologías

- **Python 3.11+**
- **Streamlit** (interfaz web)
- **Plotly** (gráficos interactivos y animaciones)
- **NumPy & Pandas** (cálculos y datos)

---

## 💻 Instalación Local

```bash
git clone https://github.com/TU_USUARIO/wbe-lab-simulator.git
cd wbe-lab-simulator
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
