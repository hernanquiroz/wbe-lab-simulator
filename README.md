# 🧪 Simulador WBE v3.0: Detección de Psicoactivos en Aguas Residuales

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.36+-red.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.20+-orange.svg)](https://plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Aplicación web interactiva para prácticas de laboratorio de **pregrado y posgrado** en Química Analítica, Toxicología e Ingeniería Ambiental. Simula el proceso completo de **Epidemiología Basada en Aguas Residuales (WBE)**, con animación realista de extracción en fase sólida, multi-analitos, calibración con incertidumbre, gestión de datos CSV y generación de reportes PDF.

> 🇨🇴 **Contexto:** Basado en protocolos y estudios de Colombia (PTAR San Fernando – Medellín, PTAR Salitre – Bogotá, Eje Cafetero).

---

## 🚀 Módulos

1. **🎬 SPE Realista:** Cartucho cilíndrico, manifold de vacío, gotas animadas y partículas de analito que se adsorben/lavan/eluyen. Modos automático y manual.
2. **📊 Cromatograma Multi-Analito:** 5 analitos (BE, THC-COOH, MDMA, Cotinina, Etanol) con colores y tiempos de retención propios.
3. **📈 Calibración e Incertidumbre:** Regresión lineal, R², incertidumbre combinada y expandida (EMCDDA).
4. **📂 Gestión CSV:** Subir, visualizar, analizar (estadística + histograma) y eliminar archivos.
5. **🌍 Epidemiología:** Retrocálculo de carga másica normalizada y comparación con ciudades colombianas.
6. **📄 Reporte PDF:** Descarga automática con portada, resultados, gráficos embebidos y referencias.

---

## 🛠️ Tecnologías

Python 3.11 · Streamlit · Plotly · NumPy · Pandas · SciPy · Matplotlib · fpdf2

---

## 💻 Instalación Local

```bash
git clone https://github.com/TU_USUARIO/wbe-lab-simulator.git
cd wbe-lab-simulator
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
