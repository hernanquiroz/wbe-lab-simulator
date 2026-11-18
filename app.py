# ============================================================================
# SIMULADOR INTERACTIVO: DETECCIÓN DE PSICOACTIVOS EN AGUAS RESIDUALES
# Versión Streamlit - Desplegable en Streamlit Cloud
# Universidad de Antioquia - Práctica de Laboratorio WBE
# ============================================================================

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import time

# Alias compatible con NumPy 1.x y 2.x
trapz = getattr(np, 'trapezoid', None) or np.trapz

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
# SECCIÓN 2: ANIMACIÓN SPE (con animación real de Plotly)
# ============================================================================

elif seccion == "🎬 Animación SPE":
    st.header("🎬 Proceso de Extracción en Fase Sólida (SPE)")

    st.markdown("""
    <div class="info-box">
    Animación real en el navegador: el solvente baja gota a gota,
    los analitos (●) se adsorben, se lavan o se eluyen según el paso.
    Usa los controles para reproducir, pausar o avanzar manualmente.
    </div>
    """, unsafe_allow_html=True)

    # Datos por paso
    PASOS = [
        "1. Acondicionamiento", "2. Carga de Muestra", "3. Lavado",
        "4. Secado", "5. Elución", "6. Concentración"
    ]

    INFO = {
        "1. Acondicionamiento": {
            "color": "#8e44ad", "vol": 5, "solv": "Metanol + Agua (pH 3)",
            "tiempo": 3, "particulas": False, "flujo": True, "nivel": [0.78, 0.30],
            "desc": "**Propósito:** Activar sitios hidrofóbicos HLB.\n\n⚠️ **No dejar secar el cartucho después de este paso.**"
        },
        "2. Carga de Muestra": {
            "color": "#7f5539", "vol": 50, "solv": "Agua residual filtrada (pH 3)",
            "tiempo": 8, "particulas": True, "flujo": True, "nivel": [0.78, 0.45],
            "desc": "**Propósito:** Los analitos se adsorben en la fase estacionaria.\n\n**Flujo:** 1–2 gotas/segundo."
        },
        "3. Lavado": {
            "color": "#74b9ff", "vol": 5, "solv": "Agua ultrapura (pH 3)",
            "tiempo": 3, "particulas": True, "flujo": True, "nivel": [0.70, 0.45],
            "desc": "**Propósito:** Eliminar sales e interferencias hidrofílicas.\n\nLos analitos (●) **permanecen retenidos**."
        },
        "4. Secado": {
            "color": "#ecf0f1", "vol": 0, "solv": "Vacío (aire)",
            "tiempo": 12, "particulas": True, "flujo": True, "nivel": [0.0, 0.0],
            "desc": "**Propósito:** Eliminar toda el agua del cartucho (10–15 min).\n\nCrítico para una elución eficiente."
        },
        "5. Elución": {
            "color": "#00b894", "vol": 6, "solv": "Metanol + 2% NH₄OH",
            "tiempo": 4, "particulas": True, "flujo": True, "nivel": [0.65, 0.45],
            "desc": "**Propósito:** Desorber los analitos.\n\nEl medio básico rompe las interacciones hidrofóbicas."
        },
        "6. Concentración": {
            "color": "#e17055", "vol": 1, "solv": "Evaporación N₂ → reconstitución",
            "tiempo": 10, "particulas": False, "flujo": False, "nivel": [0.15, 0.10],
            "desc": "**Propósito:** Concentrar 50–100x.\n\nEvaporar ≤ 30°C y reconstituir en 1 mL de fase móvil."
        },
    }

    # Función que dibuja UN frame
    def _fig_paso(paso, f, total_frames):
        d = INFO[paso]
        prog = f / max(total_frames - 1, 1)
        fig = go.Figure()

        # Cartucho exterior
        fig.add_shape(type="rect", x0=0.30, y0=0.18, x1=0.70, y1=0.82,
                      fillcolor="#dfe6e9", opacity=0.5,
                      line=dict(color="#2d3436", width=2))
        # Fase estacionaria HLB
        fig.add_shape(type="rect", x0=0.35, y0=0.30, x1=0.65, y1=0.70,
                      fillcolor="#f5e6c8", opacity=0.85,
                      line=dict(color="#b2bec3", width=1))
        # Embudo superior
        fig.add_shape(type="rect", x0=0.27, y0=0.82, x1=0.73, y1=0.88,
                      fillcolor="#b2bec3", opacity=0.6,
                      line=dict(color="#2d3436", width=1))
        # Tubo de salida + vial receptor
        fig.add_shape(type="rect", x0=0.47, y0=0.10, x1=0.53, y1=0.18,
                      fillcolor="#b2bec3", opacity=0.6)
        fig.add_shape(type="rect", x0=0.42, y0=0.02, x1=0.58, y1=0.10,
                      fillcolor="#ffffff", opacity=0.9,
                      line=dict(color="#2d3436", width=1.5))

        # Nivel de líquido en el cartucho (baja con el progreso)
        top = d["nivel"][0]
        bot = d["nivel"][1]
        y_liq = top - (top - bot) * prog
        if y_liq > bot + 0.01:
            fig.add_shape(type="rect", x0=0.35, y0=bot, x1=0.65, y1=y_liq,
                          fillcolor=d["color"], opacity=0.75, line=dict(width=0))

        # Gotas cayendo (flujo animado)
        if d["flujo"]:
            n_gotas = 6
            for i in range(n_gotas):
                fase = (prog * 3 + i / n_gotas) % 1.0
                yg = 0.82 - fase * 0.74
                if 0.05 < yg < 0.82:
                    fig.add_trace(go.Scatter(
                        x=[0.5], y=[yg], mode="markers",
                        marker=dict(size=7, color=d["color"], symbol="circle"),
                        showlegend=False, opacity=0.9))

        # Partículas (analitos) según el paso
        if d["particulas"]:
            rng = np.random.default_rng(7)
            xs = rng.uniform(0.38, 0.62, 22)
            ys = rng.uniform(0.32, 0.68, 22)
            if paso == "2. Carga de Muestra":
                ys_now = np.maximum(0.32, ys + (1 - prog) * 0.5)
                fig.add_trace(go.Scatter(x=xs, y=ys_now, mode="markers",
                    marker=dict(size=6, color="#d63031"), showlegend=False))
            elif paso == "3. Lavado":
                fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers",
                    marker=dict(size=6, color="#d63031"), showlegend=False))
                xg = rng.uniform(0.38, 0.62, 15)
                yg2 = 0.32 + (1 - prog) * 0.4
                fig.add_trace(go.Scatter(x=xg, y=[yg2]*15, mode="markers",
                    marker=dict(size=4, color="#636e72", symbol="x"),
                    showlegend=False, opacity=0.6))
            elif paso == "5. Elución":
                ys_now = ys - prog * 0.55
                fig.add_trace(go.Scatter(x=xs, y=ys_now, mode="markers",
                    marker=dict(size=6, color="#d63031"), showlegend=False))
            else:
                fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers",
                    marker=dict(size=6, color="#d63031"), showlegend=False))

        # Líquido en el vial receptor
        if paso in ("2. Carga de Muestra", "3. Lavado", "5. Elución"):
            vial_top = 0.02 + prog * 0.07
            fig.add_shape(type="rect", x0=0.42, y0=0.02, x1=0.58, y1=vial_top,
                          fillcolor=d["color"], opacity=0.8, line=dict(width=0))

        # Etiquetas
        fig.add_annotation(x=0.10, y=0.50, text="Fase<br>HLB", showarrow=False,
                           font=dict(size=10, color="#2d3436"))
        fig.add_annotation(x=0.90, y=0.50, text="Analitos ●", showarrow=False,
                           font=dict(size=10, color="#d63031"))
        fig.add_annotation(x=0.5, y=0.95,
            text=f"<b>{paso}</b>  |  Solvente: {d['solv']}  |  "
                 f"Volumen restante: {d['vol']*(1-prog):.1f} mL",
            showarrow=False, font=dict(size=12),
            bgcolor="#fff3cd", bordercolor="#e17055", borderwidth=2)

        fig.update_layout(
            xaxis=dict(visible=False, range=[0, 1]),
            yaxis=dict(visible=False, range=[0, 1.02]),
            height=520, margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="white", paper_bgcolor="white",
        )
        return fig

    # ---- MODO AUTOMÁTICO (animación fluida con frames Plotly) ----
    st.subheader("🎞️ Modo Automático (animación fluida)")

    paso_auto = st.selectbox("Paso a animar:", PASOS, key="paso_auto")
    fps = st.slider("Velocidad (frames/seg)", 5, 30, 15, key="fps_auto")

    d = INFO[paso_auto]
    total = 60
    frames = []
    for f in range(total):
        fr = _fig_paso(paso_auto, f, total)
        frames.append(go.Frame(data=fr.data, layout=fr.layout, name=str(f)))

    fig_anim = _fig_paso(paso_auto, 0, total)
    fig_anim.frames = frames
    fig_anim.update(
        layout=dict(
            updatemenus=[dict(
                type="buttons", direction="left", x=0.02, y=1.12,
                buttons=[
                    dict(label="▶️ Reproducir", method="animate",
                         args=[None, dict(frame=dict(duration=1000//fps, redraw=False),
                                          fromcurrent=True)]),
                    dict(label="⏸️ Pausar", method="animate",
                         args=[[None], dict(mode="immediate",
                                            frame=dict(duration=0, redraw=False))])
                ]
            )],
            sliders=[dict(
                active=0, x=0.1, xanchor="left", y=-0.12, yanchor="top",
                currentvalue=dict(prefix="Frame: ", font=dict(size=11)),
                pad=dict(t=40), len=0.8,
                steps=[dict(method="animate", label=str(i),
                            args=[[str(i)], dict(mode="immediate",
                                                 frame=dict(duration=0, redraw=False))])
                       for i in range(total)]
            )]
        )
    )
    st.plotly_chart(fig_anim, use_container_width=True)
    st.markdown(d["desc"])

    # ---- MODO MANUAL (paso a paso con fragment) ----
    st.subheader("🎮 Modo Manual (avanza tú mismo)")

    if "frame_manual" not in st.session_state:
        st.session_state.frame_manual = 0
    if "paso_manual" not in st.session_state:
        st.session_state.paso_manual = 0
    if "play" not in st.session_state:
        st.session_state.play = False

    paso_sel = st.select_slider(
        "Paso actual:", options=list(range(6)),
        value=st.session_state.paso_manual,
        format_func=lambda i: PASOS[i], key="sel_paso_manual"
    )
    st.session_state.paso_manual = paso_sel

    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 3])
    with c1:
        if st.button("⏮️", key="b_prev"):
            st.session_state.frame_manual = 0
    with c2:
        if st.button("◀️", key="b_back"):
            st.session_state.frame_manual = max(0, st.session_state.frame_manual - 1)
    with c3:
        if st.button("⏯️ Play/Pausa", key="b_play"):
            st.session_state.play = not st.session_state.play
    with c4:
        if st.button("▶️", key="b_fwd"):
            st.session_state.frame_manual = min(59, st.session_state.frame_manual + 1)
    with c5:
        velocidad = st.slider("Velocidad (ms/frame)", 50, 500, 150, key="vel_man")

    st.progress(st.session_state.frame_manual / 59)

    @st.fragment(run_every=velocidad/1000 if st.session_state.play else None)
    def _render_manual():
        if st.session_state.play:
            st.session_state.frame_manual = (st.session_state.frame_manual + 1) % 60
        fig = _fig_paso(PASOS[st.session_state.paso_manual],
                        st.session_state.frame_manual, 60)
        st.plotly_chart(fig, use_container_width=True, key=f"man_{st.session_state.frame_manual}")

    _render_manual()
    st.markdown(INFO[PASOS[st.session_state.paso_manual]]["desc"])

    # ---- Recorrido completo ----
    if st.button("🎥 Recorrido completo (todos los pasos)", type="primary"):
        for p in PASOS:
            st.markdown(f"### ⏳ {p}")
            st.write(INFO[p]["solv"])
            fig_p = _fig_paso(p, 30, 60)
            st.plotly_chart(fig_p, use_container_width=True, key=f"rc_{p}")
        st.success("✅ Proceso SPE completado. La muestra está lista para inyección.")

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
        concentracion = st.slider("Concentración (ng/mL):", 10, 500, 100, 10)
    with col2:
        ruido = st.slider("Ruido de fondo:", 0.0, 10.0, 2.0, 0.5)
    with col3:
        resolucion = st.slider("Resolución cromatográfica:", 0.5, 2.0, 1.0, 0.1)

    t_r = 7.0
    sigma = 0.3 / resolucion
    tiempo = np.linspace(0, 15, 1000)
    pico = concentracion * np.exp(-((tiempo - t_r) ** 2) / (2 * sigma ** 2))
    ruido_signal = np.random.normal(0, ruido, len(tiempo))
    senal = pico + ruido_signal + 5

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=tiempo, y=senal, mode='lines',
        name='Señal detectada', line=dict(color='blue', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=[t_r], y=[pico.max() + 5],
        mode='markers+text', marker=dict(size=12, color='red'),
        text=['BE'], textposition='top center', name='Benzoilecgonina'
    ))
    fig.add_shape(
        type='rect', x0=t_r - 3*sigma, y0=5,
        x1=t_r + 3*sigma, y1=pico.max() + 5,
        fillcolor='lightblue', opacity=0.3, line=dict(width=0)
    )

    area = trapz(pico, tiempo)

    fig.add_annotation(
        text=f"Área: {area:.2f}<br>Altura: {pico.max():.2f}<br>Resolución: {resolucion:.1f}",
        x=12, y=senal.max() * 0.8, showarrow=True, arrowhead=2,
        bgcolor='lightyellow', bordercolor='orange', borderwidth=2
    )
    fig.update_layout(
        title='Cromatograma Simulado - Benzoilecgonina (BE)',
        xaxis_title='Tiempo de Retención (min)',
        yaxis_title='Intensidad de Señal (u.a.)',
        template='plotly_white', height=500, showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)

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
            st.warning("⚠️ **Ruido alto:** Relación señal/ruido baja. Optimiza la extracción o aumenta la concentración.")
        elif resolucion < 0.8:
            st.warning("⚠️ **Baja resolución:** Picos muy anchos. Verifica la columna o el gradiente.")
        else:
            st.success("✅ **Buenas condiciones:** Relación señal/ruido y resolución adecuadas.")

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
        C_vial = st.number_input("Concentración en vial final (ng/mL):", 0.0, value=50.0, step=1.0)
        V_final = st.number_input("Volumen final reconstituido (mL):", 0.1, value=1.0, step=0.1)
        V_muestra = st.number_input("Volumen de muestra procesada (mL):", 1.0, value=50.0, step=1.0)
        C_espicada = st.number_input("Concentración espicada (ng/L):", 0.0, value=100.0, step=10.0)
        C_muestra_espicada = st.number_input("Concentración medida en muestra espicada (ng/L):", 0.0, value=150.0, step=10.0)

    with col2:
        st.subheader("📊 Resultados")
        C_agua = (C_vial * V_final * 1000) / V_muestra
        if C_espicada > 0:
            recuperacion = ((C_muestra_espicada - C_agua) / C_espicada) * 100
        else:
            recuperacion = 0
        factor_conc = V_muestra / V_final

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
        C_agua = st.number_input("Concentración de Benzoilecgonina en agua (ng/L):", 0.0, value=500.0, step=50.0)
        Q = st.number_input("Caudal diario de la PTAR (L/día):", 1000.0, value=1000000.0, step=100000.0, format="%.0f")
        P = st.number_input("Población servida (habitantes):", 100.0, value=100000.0, step=10000.0, format="%.0f")
        f_excrecion = st.number_input("Fracción de excreción (BE = 0.45):", 0.01, 1.0, 0.45, 0.01, format="%.2f")
        st.selectbox("Comparar con estudio en:", ["Medellín (PTAR San Fernando)", "Bogotá (PTAR Salitre)", "Pereira", "Personalizado"])

    with col2:
        st.subheader("📈 Resultados")
        consumo = (C_agua * Q * 1000) / (P * f_excrecion * 1e6)
        carga_diaria = (C_agua * Q) / 1e6

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

        if consumo < 500:
            nivel, color = "Bajo", "#28a745"
        elif consumo < 2000:
            nivel, color = "Moderado", "#ffc107"
        else:
            nivel, color = "Alto", "#dc3545"

        st.markdown(f"""
        <div style="background-color: {color}; padding: 1rem; border-radius: 10px; color: white;">
        <h4>📊 Nivel de Consumo Estimado</h4>
        <p style="font-size: 24px; font-weight: bold;">{nivel}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🇨🇴 Comparación con Estudios en Colombia")
    datos_colombia = {
        "Ciudad": ["Medellín", "Bogotá", "Pereira", "Armenia", "Manizales", "Tu muestra"],
        "Carga (mg/día/1000 hab)": [4000, 900, 4857, 2988, 645, consumo]
    }
    df_comparacion = pd.DataFrame(datos_colombia)
    fig_comparacion = px.bar(
        df_comparacion, x="Ciudad", y="Carga (mg/día/1000 hab)", color="Ciudad",
        color_discrete_map={
            "Medellín": "#667eea", "Bogotá": "#764ba2", "Pereira": "#f093fb",
            "Armenia": "#4facfe", "Manizales": "#43e97b", "Tu muestra": "#ff6b6b"
        },
        title="Comparación de Consumo de Cocaína (Benzoilecgonina) en Ciudades Colombianas"
    )
    fig_comparacion.update_layout(
        xaxis_title="Ciudad", yaxis_title="Carga Másica Normalizada (mg/día/1000 hab)",
        height=500, showlegend=False
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

    st.markdown("### 📐 Fórmula de Retrocálculo")
    st.latex(r"""
    \text{Consumo} = \frac{C_{\text{agua}} \times Q \times 1000}{P \times f_{\text{excreción}}}
    """)
    st.markdown("""
    Donde:
    - $C_{\\text{agua}}$ = Concentración del biomarcador en el afluente (ng/L)
    - $Q$ = Caudal diario de la PTAR (L/día)
    - $P$ = Población servida por la PTAR (habitantes)
    - $f_{\\text{excreción}}$ = Fracción del compuesto original excretado como metabolito (para BE ≈ 0.45)
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
