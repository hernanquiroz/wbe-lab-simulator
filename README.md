# 🧪 Simulador de Laboratorio WBE: Detección de Psicoactivos en Aguas Residuales

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.36+-red.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.20+-orange.svg)](https://plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Aplicación web interactiva diseñada para apoyar prácticas de laboratorio de **pregrado y posgrado** en Química Analítica, Toxicología y Ingeniería Ambiental. La herramienta simula el proceso completo de la **Epidemiología Basada en Aguas Residuales (WBE, por sus siglas en inglés)**, desde la extracción de la muestra hasta el retrocálculo del consumo poblacional.

> 🇨🇴 **Contexto:** Desarrollado con base en los protocolos y estudios realizados en Colombia (ej. PTAR San Fernando en Medellín, PTAR Salitre en Bogotá y ciudades del Eje Cafetero).

---

## 🚀 Características Principales

La aplicación está dividida en 4 módulos interactivos:

1. **🎬 Animación del Proceso SPE:** Visualización paso a paso de la Extracción en Fase Sólida (SPE) con cartuchos HLB, explicando el acondicionamiento, carga, lavado, secado, elución y concentración.
2. **📊 Cromatograma Interactivo:** Simulador de cromatografía (HPLC-UV / LC-MS) donde el usuario puede ajustar la concentración, el ruido de fondo y la resolución para observar su efecto en el pico de la Benzoilecgonina (metabolito de la cocaína).
3. **🧮 Calculadora de Recuperación:** Herramienta para que los estudiantes ingresen sus datos experimentales (volúmenes, concentraciones) y calculen automáticamente la concentración final en la muestra y el porcentaje de recuperación del método.
4. **🌍 Retrocálculo Epidemiológico:** Estimación de la carga másica normalizada (mg/día/1000 habitantes) utilizando la fórmula del Observatorio Europeo de las Drogas y las Toxicomanías (EMCDDA), con comparación gráfica frente a datos reales de ciudades colombianas.

---

## 🛠️ Tecnologías Utilizadas

- **Python 3.11+**: Lenguaje de programación principal.
- **Streamlit**: Framework para la creación de la interfaz web interactiva.
- **Plotly**: Generación de gráficos y cromatogramas interactivos.
- **NumPy & Pandas**: Cálculos numéricos y manejo de datos.

---

## 💻 Instalación y Ejecución Local

Si deseas ejecutar este simulador en tu computadora, sigue estos pasos:

### 1. Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO/wbe-lab-simulator.git
cd wbe-lab-simulator
