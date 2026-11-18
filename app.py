# ============================================================================
# SIMULADOR INTERACTIVO: DETECCIÓN DE PSICOACTIVOS EN AGUAS RESIDUALES
# Versión Streamlit - Desplegable en Streamlit Cloud
# ============================================================================

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import time

# Configuración de la página
st.set_page_config(
    page_title="Simulador WBE - Detección de Psicoactivos",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER PRINCIPAL
# ============================================================================

st.markdown("""
<div class="main-header">
    <h1>🧪 Simulador de Laboratorio: Detección de Psicoactivos en Aguas Residuales</h1>
    <h3>Epidemiología Basada en Aguas Residuales (WBE)</h3>
    <p>Universidad de Antioquia - Práctica de Laboratorio Interactiva</p>
</div>
""", unsafe_allow_html=True)

# Sidebar con navegación
st.sidebar.title("📚 Navegación")
seccion = st.sidebar.radio(
    "Selecciona una sección:",
    ["🏠 Inicio", "🎬 Animación SPE", "📊 Cromatograma", "🧮 Cálculos", "🌍 Epidemiología"]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**Analito modelo:** Benzoilecgonina (BE)  
**Técnica:** SPE + HPLC/LC-MS  
**Contexto:** Medellín, Colombia
""")

# ============================================================================
# SECCIÓN 1: INICIO
# ============================================================================

if seccion == "🏠 Inicio":
    st.header("Bienvenido al Simulador de Laboratorio WBE")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Analito Objetivo", "Benzoilecgonina", "Metabolito de cocaína")
    
    with col2:
        st.metric("Técnica de Extracción", "SPE", "Oasis HLB")
    
    with col3:
        st.metric("Detección", "HPLC/LC-MS", "Cromatografía")
    
    st.markdown("### 📋 Objetivo de la Práctica")
    st.markdown("""
    Esta simulación interactiva te permite:
    - **Visualizar** el proceso de Extracción en Fase Sólida (SPE) paso a paso
    - **Experimentar** con parámetros cromatográficos y ver su efecto en los resultados
    - **Calcular** la recuperación del método y la concentración en muestras
    - **Estimar** el consumo poblacional de sustancias psicoactivas
    
    ### 🎯 Niveles de Aprendizaje
    - **Pregrado:** Fundamentos de WBE, técnica SPE, identificación de picos
    - **Postgrado:** Validación de métodos, análisis de incertidumbre, epidemiología cuantitativa
    """)
    
    st.markdown("### 📖 Instrucciones de Uso")
    st.info("""
    1. Navega por las secciones usando el menú lateral
    2. Ajusta los parámetros en cada simulación
    3. Observa cómo cambian los resultados en tiempo real
    4. Compara tus resultados con los estudios realizados en Colombia
    """)

# ============================================================================
# SECCIÓN 2: ANIMACIÓN SPE
# ============================================================================

elif seccion == "🎬 Animación SPE":
    st.header("🎬 Proceso de Extracción en Fase Sólida (SPE)")
    
    st.markdown("""
    <div class="info-box">
    La Extracción en Fase Sólida (SPE) es la técnica central para concentrar los analitos
    y limpiar la matriz compleja de las aguas residuales antes del análisis cromatográfico.
    </div>
    """, unsafe_allow_html=True)
    
    # Selector de paso
    paso_seleccionado = st.selectbox(
        "Selecciona el paso del proceso SPE:",
        [
            "1. Acondicionamiento",
            "2. Carga de Muestra",
            "3. Lavado",
            "4. Secado",
            "5. Elución",
            "6. Concentración"
        ]
    )
    
    # Crear visualización según el paso
    fig = go.Figure()
    
    # Cartucho SPE (fondo)
    fig.add_shape(
        type="rect",
        x0=0.3, y0=0.2, x1=0.7, y1=0.8,
        fillcolor="lightgray",
        opacity=0.3,
        line=dict(color="black", width=2)
    )
    
    # Fase estacionaria
    fig.add_shape(
        type="rect",
        x0=0.35, y0=0.25, x1=0.65, y1=0.75,
        fillcolor="beige",
        opacity=0.6,
        line=dict(color="gray", width=1)
    )
    
    # Configuración según el paso
    colores = {
        "1. Acondicionamiento": "purple",
        "2. Carga de Muestra": "brown",
        "3. Lavado": "lightblue",
        "4. Secado": "white",
        "5. Elución": "green",
        "6. Concentración": "orange"
    }
    
    alturas = {
        "1. Acondicionamiento": 0.8,
        "2. Carga de Muestra": 0.6,
        "3. Lavado": 0.4,
        "4. Secado": 0.0,
        "5. Elución": 0.5,
        "6. Concentración": 0.1
    }
    
    descripciones = {
        "1. Acondicionamiento": """
        **Solvente:** Metanol + Agua (pH 3)
        
        **Propósito:** Activar los sitios hidrofóbicos de la fase estacionaria HLB
        
        **Tiempo:** 2-3 minutos
        
        **⚠️ Importante:** No dejar secar el cartucho después de este paso
        """,
        "2. Carga de Muestra": """
        **Muestra:** Agua residual filtrada (50-100 mL, pH 3)
        
        **Propósito:** Los analitos se adsorben en la fase estacionaria por interacciones hidrofóbicas
        
        **Flujo:** 1-2 gotas/segundo (lento para máxima retención)
        
        **Analitos retenidos:** Benzoilecgonina, THC-COOH, MDMA, etc.
        """,
        "3. Lavado": """
        **Solvente:** Agua ultrapura (pH 3)
        
        **Propósito:** Eliminar sales, azúcares y compuestos hidrofílicos que interfieren
        
        **Volumen:** 5-10 mL
        
        **Resultado:** Los analitos permanecen retenidos, las interferencias se eliminan
        """,
        "4. Secado": """
        **Método:** Vacío fuerte (10-15 minutos)
        
        **Propósito:** Eliminar completamente el agua residual del cartucho
        
        **Importancia:** El agua residual diluiría el solvente de elución y reduciría la recuperación
        
        **⚠️ Crítico:** Este paso es esencial para una elución eficiente
        """,
        "5. Elución": """
        **Solvente:** Metanol + 2% NH₄OH (6 mL total)
        
        **Propósito:** Desorber los analitos de la fase estacionaria
        
        **Mecanismo:** El medio básico rompe las interacciones hidrofóbicas
        
        **Resultado:** Los analitos se recuperan en el eluato concentrado
        """,
        "6. Concentración": """
        **Método:** Evaporación bajo corriente de N₂ suave
        
        **Temperatura:** ≤ 30°C (para evitar degradación)
        
        **Reconstitución:** 1 mL de fase móvil inicial
        
        **Factor de concentración:** 50-100x (de 50-100 mL a 1 mL)
        """
    }
    
    # Líquido en el cartucho
    if alturas[paso_seleccionado] > 0:
        fig.add_shape(
            type="rect",
            x0=0.35, y0=0.25, x1=0.65, y1=0.25 + alturas[paso_seleccionado] * 0.5,
            fillcolor=colores[paso_seleccionado],
            opacity=0.7,
            line=dict(width=0)
        )
    
    # Partículas (analitos)
    if paso_seleccionado in ["2. Carga de Muestra", "3. Lavado", "5. Elución"]:
        np.random.seed(42)
        for _ in range(30):
            x = np.random.uniform(0.38, 0.62)
            y = np.random.uniform(0.3, 0.7)
            fig.add_trace(go.Scatter(
                x=[x], y=[y],
                mode='markers',
                marker=dict(size=8, color='red', symbol='circle'),
                showlegend=False
            ))
    
    # Flecha de flujo
    if paso_seleccionado in ["1. Acondicionamiento", "2. Carga de Muestra", "3. Lavado", "5. Elución"]:
        fig.add_annotation(
            x=0.5, y=0.85,
            ax=0.5, ay=0.2,
            xref='x', yref='y',
            axref='x', ayref='y',
            showarrow=True,
            arrowhead=3,
            arrowsize=2,
            arrowwidth=3,
            arrowcolor='blue'
        )
    
    # Etiquetas
    fig.add_annotation(
        x=0.1, y=0.5,
        text="Fase<br>Estacionaria<br>(HLB)",
        showarrow=False,
        font=dict(size=10)
    )
    
    fig.add_annotation(
        x=0.9, y=0.5,
        text="Analitos<br>(●)",
        showarrow=False,
        font=dict(size=10, color='red')
    )
    
    fig.update_layout(
        title=f"Paso {paso_seleccionado}",
        xaxis=dict(visible=False, range=[0, 1]),
        yaxis=dict(visible=False, range=[0, 1]),
        height=500,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(descripciones[paso_seleccionado])
    
    # Animación completa
    if st.button("🎥 Ver Animación Completa", type="primary"):
        placeholder = st.empty()
        
        for paso in ["1. Acondicionamiento", "2. Carga de Muestra", "3. Lavado", 
                     "4. Secado", "5. Elución", "6. Concentración"]:
            with placeholder.container():
                st.subheader(f"⏳ {paso}")
                st.progress(["1. Acondicionamiento", "2. Carga de Muestra", "3. Lavado", 
                            "4. Secado", "5. Elución", "6. Concentración"].index(paso) + 1)
                st.markdown(descripciones[paso].split('\n\n')[0])
                time.sleep(2)
        
        placeholder.empty()
        st.success("✅ Proceso SPE completado. La muestra está lista para análisis cromatográfico.")

# ============================================================================
# SECCIÓN 3: CROMATOGRAMA INTERACTIVO
# ============================================================================

elif seccion == "📊 Cromatograma":
    st.header("📊 Simulador de Cromatografía Interactivo")
    
    st.markdown("""
    <div class="info-box">
    Ajusta los parámetros para ver cómo afectan el cromatograma de la Benzoilecgonina.
    El tiempo de retención típico es ~7 minutos en condiciones de fase reversa.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        concentracion = st.slider(
            "Concentración (ng/mL):",
            min_value=10,
            max_value=500,
            value=100,
            step=10
        )
    
    with col2:
        ruido = st.slider(
            "Ruido de fondo:",
            min_value=0.0,
            max_value=10.0,
            value=2.0,
            step=0.5
        )
    
    with col3:
        resolucion = st.slider(
            "Resolución cromatográfica:",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1
        )
    
    # Generar datos del cromatograma
    t_r = 7.0  # Tiempo de retención
    sigma = 0.3 / resolucion  # Ancho del pico
    
    tiempo = np.linspace(0, 15, 1000)
    pico = concentracion * np.exp(-((tiempo - t_r) ** 2) / (2 * sigma ** 2))
    ruido_signal = np.random.normal(0, ruido, len(tiempo))
    senal = pico + ruido_signal + 5  # Offset de línea base
    
    # Crear figura
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=tiempo, y=senal,
        mode='lines',
        name='Señal detectada',
        line=dict(color='blue', width=2)
    ))
    
    # Marcar el pico
    fig.add_trace(go.Scatter(
        x=[t_r], y=[pico.max() + 5],
        mode='markers+text',
        marker=dict(size=12, color='red'),
        text=['BE'],
        textposition='top center',
        name='Benzoilecgonina'
    ))
    
    # Área de integración
    fig.add_shape(
        type='rect',
        x0=t_r - 3*sigma, y0=5,
        x1=t_r + 3*sigma, y1=pico.max() + 5,
        fillcolor='lightblue',
        opacity=0.3,
        line=dict(width=0)
    )
    
    # Calcular área
    area = np.trapz(pico, tiempo)
    
    fig.add_annotation(
        text=f"Área: {area:.2f}<br>Altura: {pico.max():.2f}<br>Resolución: {resolucion:.1f}",
        x=12, y=senal.max() * 0.8,
        showarrow=True,
        arrowhead=2,
        bgcolor='lightyellow',
        bordercolor='orange',
        borderwidth=2
    )
    
    fig.update_layout(
        title='Cromatograma Simulado - Benzoilecgonina (BE)',
        xaxis_title='Tiempo de Retención (min)',
        yaxis_title='Intensidad de Señal (u.a.)',
        template='plotly_white',
        height=500,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Interpretación
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Parámetros del Pico")
        st.markdown(f"""
        - **Tiempo de retención:** {t_r:.1f} min
        - **Altura del pico:** {pico.max():.2f} u.a.
        - **Área del pico:** {area:.2f} u.a.·min
        - **Ancho a media altura:** {2.355 * sigma:.3f} min
        """)
    
    with col2:
        st.markdown("### 💡 Interpretación")
        if ruido > 5:
            st.warning("⚠️ **Ruido alto:** La relación señal/ruido es baja. Considera optimizar la extracción o aumentar la concentración.")
        elif resolucion < 0.8:
            st.warning("⚠️ **Baja resolución:** Los picos son muy anchos. Verifica la columna o el gradiente de elución.")
        else:
            st.success("✅ **Buenas condiciones:** Relación señal/ruido y resolución adecuadas para cuantificación.")

# ============================================================================
# SECCIÓN 4: CÁLCULOS DE RECUPERACIÓN
# ============================================================================

elif seccion == "🧮 Cálculos":
    st.header("🧮 Calculadora de Recuperación y Concentración")
    
    st.markdown("""
    <div class="info-box">
    Ingresa los datos experimentales para calcular la concentración en la muestra original
    y el porcentaje de recuperación del método.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 Datos de Entrada")
        
        C_vial = st.number_input(
            "Concentración en vial final (ng/mL):",
            min_value=0.0,
            value=50.0,
            step=1.0
        )
        
        V_final = st.number_input(
            "Volumen final reconstituido (mL):",
            min_value=0.1,
            value=1.0,
            step=0.1
        )
        
        V_muestra = st.number_input(
            "Volumen de muestra procesada (mL):",
            min_value=1.0,
            value=50.0,
            step=1.0
        )
        
        C_espicada = st.number_input(
            "Concentración espicada (ng/L):",
            min_value=0.0,
            value=100.0,
            step=10.0
        )
        
        C_muestra_espicada = st.number_input(
            "Concentración medida en muestra espicada (ng/L):",
            min_value=0.0,
            value=150.0,
            step=10.0
        )
    
    with col2:
        st.subheader("📊 Resultados")
        
        # Cálculos
        C_agua = (C_vial * V_final * 1000) / V_muestra  # ng/L
        
        # Recuperación
        if C_espicada > 0:
            recuperacion = ((C_muestra_espicada - C_agua) / C_espicada) * 100
        else:
            recuperacion = 0
        
        # Factor de concentración
        factor_conc = V_muestra / V_final
        
        # Mostrar resultados
        st.markdown(f"""
        <div class="success-box">
        <h4>🎯 Concentración en Agua Residual</h4>
        <p style="font-size: 24px; font-weight: bold; color: #28a745;">{C_agua:.2f} ng/L</p>
        </div>
        """, unsafe_allow_html=True)
        
        if 70 <= recuperacion <= 120:
            st.markdown(f"""
            <div class="success-box">
            <h4>✅ Porcentaje de Recuperación</h4>
            <p style="font-size: 24px; font-weight: bold; color: #28a745;">{recuperacion:.1f}%</p>
            <p>Rango aceptable: 70-120%</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="warning-box">
            <h4>⚠️ Porcentaje de Recuperación</h4>
            <p style="font-size: 24px; font-weight: bold; color: #ffc107;">{recuperacion:.1f}%</p>
            <p>Fuera del rango aceptable (70-120%)</p>
            <p><strong>Posibles causas:</strong></p>
            <ul>
            <li>Cartucho SPE seco durante el proceso</li>
            <li>pH de la muestra incorrecto</li>
            <li>Volumen de elución insuficiente</li>
            <li>Degradación del analito</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="info-box">
        <h4>📐 Factor de Concentración</h4>
        <p style="font-size: 20px; font-weight: bold;">{factor_conc:.1f}x</p>
        <p>De {V_muestra:.0f} mL a {V_final:.1f} mL</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Fórmula
    st.markdown("### 📐 Fórmulas Utilizadas")
    st.latex(r"""
    C_{\text{agua}} = \frac{C_{\text{vial}} \times V_{\text{final}} \times 1000}{V_{\text{muestra}}}
    """)
    
    st.latex(r"""
    \% \text{Recuperación} = \frac{C_{\text{muestra espicada}} - C_{\text{agua}}}{C_{\text{espicada}}} \times 100
    """)

# ============================================================================
# SECCIÓN 5: EPIDEMIOLOGÍA
# ============================================================================

elif seccion == "🌍 Epidemiología":
    st.header("🌍 Calculadora de Epidemiología Basada en Aguas Residuales")
    
    st.markdown("""
    <div class="info-box">
    Estima el consumo poblacional de sustancias psicoactivas a partir de la concentración
    medida en aguas residuales, utilizando el método de retrocálculo del EMCDDA.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 Parámetros de Entrada")
        
        C_agua = st.number_input(
            "Concentración de Benzoilecgonina en agua (ng/L):",
            min_value=0.0,
            value=500.0,
            step=50.0
        )
        
        Q = st.number_input(
            "Caudal diario de la PTAR (L/día):",
            min_value=1000.0,
            value=1000000.0,
            step=100000.0,
            format="%.0f"
        )
        
        P = st.number_input(
            "Población servida (habitantes):",
            min_value=100.0,
            value=100000.0,
            step=10000.0,
            format="%.0f"
        )
        
        f_excrecion = st.number_input(
            "Fracción de excreción (BE = 0.45):",
            min_value=0.01,
            max_value=1.0,
            value=0.45,
            step=0.01,
            format="%.2f"
        )
        
        # Selector de ciudad para referencia
        ciudad_ref = st.selectbox(
            "Comparar con estudio en:",
            ["Medellín (PTAR San Fernando)", "Bogotá (PTAR Salitre)", "Pereira", "Personalizado"]
        )
    
    with col2:
        st.subheader("📈 Resultados")
        
        # Cálculo de carga másica normalizada
        consumo = (C_agua * Q * 1000) / (P * f_excrecion * 1e6)  # mg/día/1000 hab
        
        # Carga diaria total
        carga_diaria = (C_agua * Q) / 1e6  # mg/día
        
        # Mostrar resultados
        st.markdown(f"""
        <div class="success-box">
        <h4>🎯 Carga Másica Normalizada</h4>
        <p style="font-size: 28px; font-weight: bold; color: #28a745;">{consumo:.2f} mg/día/1000 hab</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="info-box">
        <h4>📊 Carga Diaria Total</h4>
        <p style="font-size: 20px; font-weight: bold;">{carga_diaria:.2f} mg/día</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Interpretación
        if consumo < 500:
            nivel = "Bajo"
            color = "#28a745"
        elif consumo < 2000:
            nivel = "Moderado"
            color = "#ffc107"
        else:
            nivel = "Alto"
            color = "#dc3545"
        
        st.markdown(f"""
        <div style="background-color: {color}; padding: 1rem; border-radius: 10px; color: white;">
        <h4>📊 Nivel de Consumo Estimado</h4>
        <p style="font-size: 24px; font-weight: bold;">{nivel}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Comparación con estudios en Colombia
    st.markdown("### 🇨🇴 Comparación con Estudios en Colombia")
    
    datos_colombia = {
        "Ciudad": ["Medellín", "Bogotá", "Pereira", "Armenia", "Manizales", "Tu muestra"],
        "Carga (mg/día/1000 hab)": [4000, 900, 4857, 2988, 645, consumo]
    }
    
    df_comparacion = pd.DataFrame(datos_colombia)
    
    fig_comparacion = px.bar(
        df_comparacion,
        x="Ciudad",
        y="Carga (mg/día/1000 hab)",
        color="Ciudad",
        color_discrete_map={
            "Medellín": "#667eea",
            "Bogotá": "#764ba2",
            "Pereira": "#f093fb",
            "Armenia": "#4facfe",
            "Manizales": "#43e97b",
            "Tu muestra": "#ff6b6b"
        },
        title="Comparación de Consumo de Cocaína (Benzoilecgonina) en Ciudades Colombianas"
    )
    
    fig_comparacion.update_layout(
        xaxis_title="Ciudad",
        yaxis_title="Carga Másica Normalizada (mg/día/1000 hab)",
        height=500,
        showlegend=False
    )
    
    st.plotly_chart(fig_comparacion, use_container_width=True)
    
    st.markdown("""
    <div class="info-box">
    <h4>📚 Referencias de Estudios en Colombia</h4>
    <ul>
    <li><strong>Medellín (2022):</strong> PTAR San Fernando - Carga promedio ~3000-5000 mg/día/1000 hab</li>
    <li><strong>Bogotá (2021):</strong> PTAR Salitre - Carga promedio ~800-1000 mg/día/1000 hab</li>
    <li><strong>Eje Cafetero (2020):</strong> Pereira mostró el mayor consumo (4857 mg/día/1000 hab)</li>
    </ul>
    <p><strong>Fuente:</strong> Ruiz Montilla, A.M. (2022). Estudio de análisis de drogas de abuso en aguas residuales Medellín 2022. Universidad de Caldas.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Fórmula
    st.markdown("### 📐 Fórmula de Retrocálculo")
    st.latex(r"""
    \text{Consumo} = \frac{C_{\text{agua}} \times Q \times 1000}{P \times f_{\text{excreción}}}
    """)
    
    st.markdown("""
    Donde:
    - $C_{\text{agua}}$ = Concentración del biomarcador en el afluente (ng/L)
    - $Q$ = Caudal diario de la PTAR (L/día)
    - $P$ = Población servida por la PTAR (habitantes)
    - $f_{\text{excreción}}$ = Fracción del compuesto original excretado como metabolito (para BE ≈ 0.45)
    """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; padding: 1rem;">
    <p>🧪 Simulador de Laboratorio WBE - Universidad de Antioquia</p>
    <p>Desarrollado para prácticas de pregrado y postgrado en Química Analítica y Ambiental</p>
    <p>© 2026 - Todos los derechos reservados</p>
</div>
""", unsafe_allow_html=True)
