# ============================================================================
# SIMULADOR WBE v3.0 - Universidad de Antioquia
# Simulación realista SPE + Multi-analitos + Reporte PDF
# ============================================================================

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
from fpdf import FPDF, XPos, YPos
from datetime import datetime
import io

# Alias compatible NumPy 1.x / 2.x (evita el error de np.trapz)
trapz = getattr(np, 'trapezoid', None) or np.trapz

# Helper para la API nueva de fpdf2 (elimina DeprecationWarning de "ln")
def _cell(pdf, w, h, txt="", ln=True, border=0, align=''):
    if ln:
        pdf.cell(w, h, txt, border=border, align=align,
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        pdf.cell(w, h, txt, border=border, align=align,
                 new_x=XPos.RIGHT, new_y=YPos.TOP)

# ============================================================================
# BASE DE DATOS DE ANALITOS
# ============================================================================
ANALITOS = {
    "Benzoilecgonina (Cocaína)": {
        "abrev": "BE", "t_r": 7.0, "sigma_base": 0.3,
        "f_excrecion": 0.45, "color": "#e63946", "mw": 289.3,
        "desc": "Metabolito principal de la cocaína. Biomarcador más estudiado en WBE."
    },
    "THC-COOH (Cannabis)": {
        "abrev": "THC-COOH", "t_r": 9.5, "sigma_base": 0.35,
        "f_excrecion": 0.03, "color": "#2a9d8f", "mw": 345.4,
        "desc": "Metabolito del THC. Baja fracción de excreción, requiere SPE eficiente."
    },
    "MDMA (Éxtasis)": {
        "abrev": "MDMA", "t_r": 5.5, "sigma_base": 0.25,
        "f_excrecion": 0.65, "color": "#457b9d", "mw": 193.25,
        "desc": "Droga sintética. Alta fracción de excreción en forma inalterada."
    },
    "Cotinina (Nicotina/Tabaco)": {
        "abrev": "COT", "t_r": 4.0, "sigma_base": 0.28,
        "f_excrecion": 0.15, "color": "#e76f51", "mw": 176.22,
        "desc": "Metabolito de la nicotina. Usado para normalizar cargas por consumo de tabaco."
    },
    "Etanol (Alcohol)": {
        "abrev": "EtOH", "t_r": 2.5, "sigma_base": 0.20,
        "f_excrecion": 0.95, "color": "#9b5de5", "mw": 46.07,
        "desc": "Alcohol etílico. Alta volatilidad, requiere preservación inmediata de muestra."
    }
}

# ============================================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================================
st.set_page_config(
    page_title="Simulador WBE v3.0 - UdeA",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {}
if 'resultados_practica' not in st.session_state:
    st.session_state.resultados_practica = {}

# CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem; border-radius: 15px; color: white;
        text-align: center; margin-bottom: 2rem;
    }
    .info-box { background-color: #f0f2f6; padding: 1rem; border-radius: 10px; border-left: 5px solid #667eea; margin: 1rem 0; }
    .success-box { background-color: #d4edda; padding: 1rem; border-radius: 10px; border-left: 5px solid #28a745; }
    .warning-box { background-color: #fff3cd; padding: 1rem; border-radius: 10px; border-left: 5px solid #ffc107; }
    .analito-card { background: white; padding: 10px; border-radius: 8px; border: 1px solid #ddd; margin: 5px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🧪 Simulador WBE v3.0 - Laboratorio Realista</h1>
    <h3>Epidemiología Basada en Aguas Residuales</h3>
    <p>Universidad de Antioquia | Multi-analitos | Reporte PDF</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚙️ Configuración de Laboratorio")
st.sidebar.markdown("**Equipo Cromatográfico:**")
hplc_brand = st.sidebar.selectbox(
    "Marca/Modelo",
    ["Agilent 1260 Infinity II (HPLC-UV)", "Waters Acquity UPLC (LC-MS/MS)",
     "Shimadzu Nexera (LC-MS/MS)", "Thermo Vanquish (HRMS)"]
)
st.sidebar.markdown("**Cartucho SPE:**")
spe_cartridge = st.sidebar.selectbox(
    "Tipo de cartucho",
    ["Oasis HLB 200mg/6cc (Waters)", "Strata-X 200mg/6cc (Phenomenex)",
     "Bond Elut Plexa 200mg (Agilent)", "Supelclean ENVI-18 (Sigma)"]
)
st.sidebar.markdown("---")
seccion = st.sidebar.radio(
    "Navegación:",
    ["🏠 Inicio", "🎬 SPE Realista", "📊 Cromatograma Multi", "📈 Calibración",
     "📂 Datos CSV", "🌍 Epidemiología", "📄 Reporte PDF"]
)

# ============================================================================
# SECCIÓN 1: INICIO
# ============================================================================
if seccion == "🏠 Inicio":
    st.header("Bienvenido al Simulador WBE v3.0")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Analitos disponibles", len(ANALITOS))
    with col2: st.metric("Cartucho", spe_cartridge.split('(')[0])
    with col3: st.metric("Equipo", hplc_brand.split('(')[0])
    with col4: st.metric("Versión", "3.0")

    st.markdown("""
    ### 🎯 Novedades de la versión 3.0
    - **🎬 Simulación SPE realista**: cartucho cilíndrico, vial, gotas animadas, manifold de vacío
    - **🧪 5 analitos**: Cocaína (BE), Cannabis (THC-COOH), MDMA, Nicotina (Cotinina), Alcohol (Etanol)
    - **📊 Cromatograma multi-analito**: superposición de picos con colores distintivos
    - **📄 Reporte PDF**: descarga automática con todos los resultados de la práctica
    - **📂 Gestión CSV**: subir, visualizar, analizar y eliminar archivos
    """)

    st.markdown("### 🧪 Analitos disponibles")
    for nombre, info in ANALITOS.items():
        st.markdown(f"""
        <div class="analito-card">
            <b style="color:{info['color']}">● {nombre}</b> ({info['abrev']}) — t_R ≈ {info['t_r']} min |
            f_excreción = {info['f_excrecion']} | MW = {info['mw']} g/mol<br>
            <i>{info['desc']}</i>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# SECCIÓN 2: SPE REALISTA
# ============================================================================
elif seccion == "🎬 SPE Realista":
    st.header("🎬 Simulación Realista de Extracción en Fase Sólida")
    st.info(f"Cartucho: **{spe_cartridge}** | Equipo: **{hplc_brand}**")

    analito_spe = st.selectbox("Analito a simular:", list(ANALITOS.keys()), key="analito_spe")
    info_analito = ANALITOS[analito_spe]

    PASOS = ["1. Acondicionamiento", "2. Carga de Muestra", "3. Lavado",
             "4. Secado", "5. Elución", "6. Concentración"]
    INFO = {
        "1. Acondicionamiento": {
            "color": "#8e44ad", "vol": 5, "solv": "Metanol → Agua (pH 3)",
            "tiempo": 3, "particulas": False, "flujo": True,
            "nivel_embudo": 0.85, "nivel_cartucho": 0.30,
            "desc": f"**Objetivo:** Activar sitios hidrofóbicos del cartucho {spe_cartridge.split('(')[0]}.\n\n⚠️ **CRÍTICO:** No dejar secar el cartucho. El analito {info_analito['abrev']} requiere fase estacionaria húmeda para retenerse."
        },
        "2. Carga de Muestra": {
            "color": "#7f5539", "vol": 50, "solv": "Agua residual filtrada (pH 3)",
            "tiempo": 8, "particulas": True, "flujo": True,
            "nivel_embudo": 0.85, "nivel_cartucho": 0.55,
            "desc": f"**Objetivo:** Pasar 50 mL de muestra a 1-2 gotas/seg.\n\nLas moléculas de **{info_analito['abrev']}** (●) se adsorben en la fase HLB por interacciones hidrofóbicas."
        },
        "3. Lavado": {
            "color": "#74b9ff", "vol": 5, "solv": "Agua ultrapura (pH 3)",
            "tiempo": 3, "particulas": True, "flujo": True,
            "nivel_embudo": 0.75, "nivel_cartucho": 0.55,
            "desc": "**Objetivo:** Eliminar sales e interferencias hidrofílicas.\n\nLos analitos (●) permanecen retenidos. Las interferencias (×) salen al vial de desperdicio."
        },
        "4. Secado": {
            "color": "#ecf0f1", "vol": 0, "solv": "Vacío fuerte (aire)",
            "tiempo": 12, "particulas": True, "flujo": False,
            "nivel_embudo": 0.0, "nivel_cartucho": 0.0,
            "desc": "**Objetivo:** Eliminar TODA el agua residual (10-15 min).\n\n⚠️ Paso crítico: el agua diluiría el metanol de elución y reduciría la recuperación."
        },
        "5. Elución": {
            "color": "#00b894", "vol": 6, "solv": "Metanol + 2% NH₄OH",
            "tiempo": 4, "particulas": True, "flujo": True,
            "nivel_embudo": 0.70, "nivel_cartucho": 0.55,
            "desc": f"**Objetivo:** Desorber {info_analito['abrev']} de la fase estacionaria.\n\nEl medio básico (NH₄OH) rompe las interacciones iónicas. Los analitos (●) salen hacia el vial colector."
        },
        "6. Concentración": {
            "color": "#e17055", "vol": 1, "solv": "Evaporación N₂ → 1 mL fase móvil",
            "tiempo": 10, "particulas": False, "flujo": False,
            "nivel_embudo": 0.15, "nivel_cartucho": 0.10,
            "desc": "**Objetivo:** Concentrar 50-100x.\n\nEvaporar bajo N₂ suave a ≤30°C. Reconstituir en 1 mL. Filtrar 0.22 µm antes de inyectar."
        }
    }

    def dibujar_escena_realista(paso, f, total_frames):
        d = INFO[paso]
        prog = f / max(total_frames - 1, 1)
        fig = go.Figure()

        # Mesa de laboratorio
        fig.add_shape(type="rect", x0=0, y0=0, x1=1, y1=0.15,
                      fillcolor="#8b7355", opacity=0.3, line=dict(width=0))
        # Manifold de vacío
        fig.add_shape(type="rect", x0=0.15, y0=0.88, x1=0.85, y1=0.95,
                      fillcolor="#6c757d", opacity=0.8, line=dict(color="#343a40", width=2))
        for x_port in [0.30, 0.50, 0.70]:
            fig.add_shape(type="rect", x0=x_port-0.02, y0=0.85, x1=x_port+0.02, y1=0.88,
                          fillcolor="#495057", opacity=0.9)
        # Tubo de vacío
        fig.add_shape(type="line", x0=0.85, y0=0.92, x1=0.98, y1=0.92,
                      line=dict(color="#343a40", width=3))
        fig.add_annotation(x=0.98, y=0.92, text="🔌 Vacío", showarrow=False, font=dict(size=9))

        # Cartucho SPE (cilindro)
        fig.add_shape(type="rect", x0=0.40, y0=0.30, x1=0.60, y1=0.85,
                      fillcolor="#f8f9fa", opacity=0.95, line=dict(color="#495057", width=2))
        fig.add_shape(type="rect", x0=0.42, y0=0.45, x1=0.58, y1=0.70,
                      fillcolor="#f5e6c8", opacity=0.9, line=dict(color="#b2bec3", width=1))
        fig.add_shape(type="rect", x0=0.42, y0=0.70, x1=0.58, y1=0.72,
                      fillcolor="#adb5bd", opacity=0.7)
        fig.add_shape(type="rect", x0=0.42, y0=0.43, x1=0.58, y1=0.45,
                      fillcolor="#adb5bd", opacity=0.7)
        fig.add_shape(type="path", path="M 0.40 0.43 L 0.60 0.43 L 0.52 0.38 L 0.48 0.38 Z",
                      fillcolor="#f8f9fa", line=dict(color="#495057", width=1.5))
        fig.add_annotation(x=0.50, y=0.58, text="HLB<br>200mg", showarrow=False,
                           font=dict(size=9, color="#6c757d"))

        # Embudo superior
        fig.add_shape(type="path", path="M 0.30 0.85 L 0.70 0.85 L 0.62 0.90 L 0.38 0.90 Z",
                      fillcolor="#dee2e6", opacity=0.9, line=dict(color="#495057", width=1.5))

        # Líquido en embudo
        if d["nivel_embudo"] > 0.05:
            top_emb = d["nivel_embudo"]; bot_emb = 0.85
            y_liq_emb = top_emb - (top_emb - bot_emb) * prog
            if y_liq_emb > bot_emb + 0.01:
                fig.add_shape(type="rect", x0=0.32, y0=bot_emb, x1=0.68, y1=y_liq_emb,
                              fillcolor=d["color"], opacity=0.7, line=dict(width=0))

        # Líquido en cartucho
        if d["nivel_cartucho"] > 0.01:
            top_cart = 0.70; bot_cart = 0.45
            y_liq_cart = top_cart - (top_cart - bot_cart) * prog
            if y_liq_cart > bot_cart + 0.01:
                fig.add_shape(type="rect", x0=0.42, y0=bot_cart, x1=0.58, y1=y_liq_cart,
                              fillcolor=d["color"], opacity=0.75, line=dict(width=0))

        # Gotas cayendo
        if d["flujo"]:
            for i in range(8):
                fase = (prog * 4 + i / 8) % 1.0
                if fase < 0.5:
                    yg = 0.85 - fase * 2 * 0.40; xg = 0.50 + np.sin(fase * 10) * 0.01
                else:
                    fase2 = (fase - 0.5) * 2; yg = 0.45 - fase2 * 0.10; xg = 0.50
                if 0.25 < yg < 0.85:
                    fig.add_trace(go.Scatter(x=[xg], y=[yg], mode="markers",
                        marker=dict(size=8, color=d["color"], symbol="circle",
                                    line=dict(color="white", width=0.5)),
                        showlegend=False, opacity=0.9))

        # Vial colector
        fig.add_shape(type="rect", x0=0.44, y0=0.10, x1=0.56, y1=0.35,
                      fillcolor="#ffffff", opacity=0.85, line=dict(color="#495057", width=1.5))
        fig.add_shape(type="rect", x0=0.45, y0=0.35, x1=0.55, y1=0.37,
                      fillcolor="#2d3436", opacity=0.8)
        if paso in ("2. Carga de Muestra", "3. Lavado", "5. Elución"):
            vial_top = 0.10 + prog * 0.22
            fig.add_shape(type="rect", x0=0.44, y0=0.10, x1=0.56, y1=vial_top,
                          fillcolor=d["color"], opacity=0.8, line=dict(width=0))
            fig.add_shape(type="line", x0=0.44, y0=vial_top, x1=0.56, y1=vial_top,
                          line=dict(color="white", width=1.5))

        # Partículas (analitos)
        if d["particulas"]:
            rng = np.random.default_rng(42)
            xs = rng.uniform(0.43, 0.57, 25); ys = rng.uniform(0.46, 0.69, 25)
            if paso == "2. Carga de Muestra":
                ys_now = np.maximum(0.46, ys + (1 - prog) * 0.40)
                fig.add_trace(go.Scatter(x=xs, y=ys_now, mode="markers",
                    marker=dict(size=7, color=info_analito['color'], symbol="circle",
                                line=dict(color="white", width=0.5)), showlegend=False))
            elif paso == "3. Lavado":
                fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers",
                    marker=dict(size=7, color=info_analito['color'], symbol="circle",
                                line=dict(color="white", width=0.5)), showlegend=False))
                xg = rng.uniform(0.43, 0.57, 12); yg = 0.46 - prog * 0.35
                fig.add_trace(go.Scatter(x=xg, y=[yg]*12, mode="markers",
                    marker=dict(size=5, color="#6c757d", symbol="x"),
                    showlegend=False, opacity=0.7))
            elif paso == "5. Elución":
                ys_now = ys - prog * 0.50
                en_vial = ys_now < 0.35
                fig.add_trace(go.Scatter(x=xs[~en_vial], y=ys_now[~en_vial], mode="markers",
                    marker=dict(size=7, color=info_analito['color'], symbol="circle",
                                line=dict(color="white", width=0.5)), showlegend=False))
                if en_vial.sum() > 0:
                    fig.add_trace(go.Scatter(x=xs[en_vial], y=0.10 + rng.uniform(0.02, 0.20, en_vial.sum()) * prog,
                        mode="markers", marker=dict(size=7, color=info_analito['color'],
                        symbol="circle", line=dict(color="white", width=0.5)),
                        showlegend=False, opacity=0.8))
            else:
                fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers",
                    marker=dict(size=7, color=info_analito['color'], symbol="circle",
                                line=dict(color="white", width=0.5)), showlegend=False))

        # Etiquetas
        fig.add_annotation(x=0.08, y=0.60, text="Manifold<br>de vacío", showarrow=False, font=dict(size=9, color="#495057"))
        fig.add_annotation(x=0.75, y=0.50, text=f"Analito: {info_analito['abrev']}", showarrow=False, font=dict(size=10, color=info_analito['color']))
        fig.add_annotation(x=0.75, y=0.20, text="Vial<br>colector", showarrow=False, font=dict(size=9, color="#495057"))
        fig.add_annotation(x=0.50, y=0.98,
            text=f"<b>{paso}</b>  |  {d['solv']}  |  Vol: {d['vol']*(1-prog):.1f} mL  |  Tiempo: ~{d['tiempo']} min",
            showarrow=False, font=dict(size=11), bgcolor="#fff3cd", bordercolor="#e17055", borderwidth=2)

        fig.update_layout(xaxis=dict(visible=False, range=[0, 1]),
                          yaxis=dict(visible=False, range=[0, 1]),
                          height=550, margin=dict(l=20, r=20, t=40, b=20),
                          plot_bgcolor="#f8f9fa", paper_bgcolor="white")
        return fig

    # MODO AUTOMÁTICO
    st.subheader("🎞️ Modo Automático (animación fluida)")
    paso_auto = st.selectbox("Paso a animar:", PASOS, key="paso_auto")
    fps = st.slider("Velocidad (frames/seg)", 5, 30, 15, key="fps_auto")

    total = 60
    frames = []
    for f in range(total):
        fr = dibujar_escena_realista(paso_auto, f, total)
        frames.append(go.Frame(data=fr.data, layout=fr.layout, name=str(f)))

    fig_anim = dibujar_escena_realista(paso_auto, 0, total)
    fig_anim.frames = frames
    fig_anim.update(layout=dict(
        updatemenus=[dict(type="buttons", x=0.02, y=1.05, buttons=[
            dict(label="▶️ Reproducir", method="animate",
                 args=[None, dict(frame=dict(duration=1000//fps), fromcurrent=True)]),
            dict(label="⏸️ Pausar", method="animate", args=[[None], dict(mode="immediate")])
        ])]
    ))
    st.plotly_chart(fig_anim, width="stretch")
    st.markdown(INFO[paso_auto]["desc"])

    # MODO MANUAL
    st.subheader("🎮 Modo Manual")
    if "frame_manual" not in st.session_state: st.session_state.frame_manual = 0
    if "paso_manual" not in st.session_state: st.session_state.paso_manual = 0
    if "play" not in st.session_state: st.session_state.play = False

    paso_sel = st.select_slider("Paso actual:", options=list(range(6)),
        value=st.session_state.paso_manual, format_func=lambda i: PASOS[i], key="sel_paso_manual")
    st.session_state.paso_manual = paso_sel

    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 3])
    with c1:
        if st.button("⏮️", key="b_prev"): st.session_state.frame_manual = 0
    with c2:
        if st.button("◀️", key="b_back"): st.session_state.frame_manual = max(0, st.session_state.frame_manual - 1)
    with c3:
        if st.button("⏯️ Play/Pausa", key="b_play"): st.session_state.play = not st.session_state.play
    with c4:
        if st.button("▶️", key="b_fwd"): st.session_state.frame_manual = min(59, st.session_state.frame_manual + 1)
    with c5:
        velocidad = st.slider("Velocidad (ms/frame)", 50, 500, 150, key="vel_man")

    st.progress(st.session_state.frame_manual / 59)

    @st.fragment(run_every=velocidad/1000 if st.session_state.play else None)
    def _render_manual():
        if st.session_state.play:
            st.session_state.frame_manual = (st.session_state.frame_manual + 1) % 60
        fig = dibujar_escena_realista(PASOS[st.session_state.paso_manual], st.session_state.frame_manual, 60)
        st.plotly_chart(fig, width="stretch", key=f"man_{st.session_state.frame_manual}")

    _render_manual()
    st.markdown(INFO[PASOS[st.session_state.paso_manual]]["desc"])

# ============================================================================
# SECCIÓN 3: CROMATOGRAMA MULTI-ANALITO
# ============================================================================
elif seccion == "📊 Cromatograma Multi":
    st.header("📊 Cromatograma Multi-Analito")
    st.info(f"Simulación para: **{hplc_brand}** | Cartucho: **{spe_cartridge}**")

    st.markdown("### 🧪 Selecciona los analitos a visualizar")
    cols_analitos = st.columns(len(ANALITOS))
    analitos_seleccionados = []
    for i, (nombre, info) in enumerate(ANALITOS.items()):
        with cols_analitos[i]:
            checked = st.checkbox(f"● {nombre}", value=(i == 0), key=f"chk_{nombre}")
            if checked:
                analitos_seleccionados.append(nombre)

    col1, col2, col3 = st.columns(3)
    with col1: concentracion = st.slider("Concentración base (ng/mL):", 10, 500, 100, 10)
    with col2: ruido = st.slider("Ruido de fondo:", 0.0, 10.0, 2.0, 0.5)
    with col3: resolucion = st.slider("Resolución cromatográfica:", 0.5, 2.0, 1.0, 0.1)

    tiempo = np.linspace(0, 15, 1000)
    senal_total = np.random.normal(0, ruido, len(tiempo)) + 5

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tiempo, y=[5]*len(tiempo), mode='lines',
        name='Línea base', line=dict(color='gray', dash='dot', width=1)))

    areas_resultados = {}
    for nombre in analitos_seleccionados:
        info = ANALITOS[nombre]
        sigma = info['sigma_base'] / resolucion
        factor_conc = concentracion * (0.5 if info['f_excrecion'] < 0.1 else 1.0)
        pico = factor_conc * np.exp(-((tiempo - info['t_r']) ** 2) / (2 * sigma ** 2))
        senal_total += pico
        areas_resultados[nombre] = trapz(pico, tiempo)
        fig.add_trace(go.Scatter(x=tiempo, y=pico + 5, mode='lines',
            name=f"{info['abrev']} (t_R={info['t_r']} min)", line=dict(color=info['color'], width=2)))
        fig.add_trace(go.Scatter(x=[info['t_r']], y=[pico.max() + 5], mode='markers+text',
            marker=dict(size=10, color=info['color']), text=[info['abrev']],
            textposition='top center', showlegend=False))

    fig.add_trace(go.Scatter(x=tiempo, y=senal_total, mode='lines',
        name='Cromatograma total', line=dict(color='black', width=2.5)))
    fig.update_layout(title='Cromatograma Multi-Analito Simulado',
        xaxis_title='Tiempo de Retención (min)', yaxis_title='Intensidad de Señal (u.a.)',
        template='plotly_white', height=500, showlegend=True)
    st.plotly_chart(fig, width="stretch")

    if areas_resultados:
        st.markdown("### 📈 Áreas de Picos Calculadas")
        df_areas = pd.DataFrame([
            {"Analito": n, "Abrev.": ANALITOS[n]['abrev'], "t_R (min)": ANALITOS[n]['t_r'],
             "Área (u.a.·min)": areas_resultados[n]}
            for n in analitos_seleccionados
        ])
        st.dataframe(df_areas, width="stretch")
        st.session_state.resultados_practica['cromatograma'] = {
            'analitos': analitos_seleccionados, 'areas': areas_resultados,
            'concentracion': concentracion, 'ruido': ruido, 'resolucion': resolucion
        }

# ============================================================================
# SECCIÓN 4: CALIBRACIÓN
# ============================================================================
elif seccion == "📈 Calibración":
    st.header("📈 Curva de Calibración e Incertidumbre")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📥 Datos de Calibración")
        datos_texto = st.text_area(
            "Concentración (ng/mL), Área del pico",
            "10, 1500\n50, 7200\n100, 14500\n250, 36000\n500, 71000", height=200)
    with col2:
        st.subheader("📊 Parámetros de Incertidumbre")
        u_rep = st.number_input("Incertidumbre por repetibilidad (%)", 0.0, 20.0, 5.0, 0.1)
        u_vol = st.number_input("Incertidumbre volumétrica (%)", 0.0, 10.0, 2.0, 0.1)
        k = st.number_input("Factor de cobertura (k=2 para 95%)", 1.0, 3.0, 2.0, 0.1)

    if st.button("Calcular Regresión e Incertidumbre", type="primary"):
        try:
            lineas = [l.strip() for l in datos_texto.split('\n') if l.strip()]
            conc, areas = [], []
            for l in lineas:
                c, a = map(float, l.split(','))
                conc.append(c); areas.append(a)
            conc, areas = np.array(conc), np.array(areas)

            slope, intercept, r_value, p_value, std_err = stats.linregress(conc, areas)
            r_squared = r_value ** 2
            u_cal = (std_err / np.mean(areas)) * 100
            u_comb = np.sqrt(u_cal ** 2 + u_rep ** 2 + u_vol ** 2)
            u_expandida = k * u_comb

            st.success(f"✅ Ecuación: $y = {slope:.2f}x + {intercept:.2f}$ | $R^2 = {r_squared:.4f}$")

            fig_cal = go.Figure()
            fig_cal.add_trace(go.Scatter(x=conc, y=areas, mode='markers', name='Experimental',
                marker=dict(size=10, color='red')))
            x_fit = np.linspace(0, max(conc) * 1.1, 100)
            fig_cal.add_trace(go.Scatter(x=x_fit, y=slope * x_fit + intercept, mode='lines',
                name=f'Ajuste (R²={r_squared:.4f})', line=dict(color='blue')))
            fig_cal.update_layout(title='Curva de Calibración', xaxis_title='Concentración (ng/mL)',
                yaxis_title='Área', template='plotly_white')
            st.plotly_chart(fig_cal, width="stretch")

            st.markdown(f"""
            <div class="info-box">
            <h4>📐 Resumen de Incertidumbre</h4>
            <ul>
                <li><strong>Pendiente (m):</strong> {slope:.2f} ± {std_err:.2f}</li>
                <li><strong>Intercepto (b):</strong> {intercept:.2f}</li>
                <li><strong>R²:</strong> {r_squared:.4f}</li>
                <li><strong>u_cal:</strong> {u_cal:.2f}% | <strong>u_rep:</strong> {u_rep:.2f}% | <strong>u_vol:</strong> {u_vol:.2f}%</li>
                <li><strong>Incertidumbre combinada (uc):</strong> {u_comb:.2f}%</li>
                <li><strong>Incertidumbre expandida (U, k={k}):</strong> <b>{u_expandida:.2f}%</b></li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

            st.session_state.resultados_practica['calibracion'] = {
                'pendiente': slope, 'intercepto': intercept, 'r2': r_squared,
                'std_err': std_err, 'u_comb': u_comb, 'u_expandida': u_expandida, 'k': k
            }
        except Exception as e:
            st.error(f"Error: {e}")

# ============================================================================
# SECCIÓN 5: DATOS CSV
# ============================================================================
elif seccion == "📂 Datos CSV":
    st.header("📂 Gestión de Datos Experimentales (CSV)")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("⬆️ Cargar Archivo")
        uploaded_file = st.file_uploader("Selecciona un archivo CSV", type=['csv'])
        if uploaded_file is not None:
            if uploaded_file.name not in st.session_state.uploaded_files:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.session_state.uploaded_files[uploaded_file.name] = df
                    st.success(f"✅ '{uploaded_file.name}' cargado.")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Archivo ya cargado.")

        st.markdown("### 📥 Formato Esperado")
        st.code("Muestra,Concentracion_ng_L,Area_Pico\nM1,450.5,12500\nM2,460.2,12800", language="csv")
        st.download_button("Descargar Plantilla CSV",
            data="Muestra,Concentracion_ng_L,Area_Pico\nM1,450.5,12500\nM2,460.2,12800\nM3,445.0,12300",
            file_name="plantilla_wbe.csv", mime="text/csv")

    with col2:
        st.subheader("📁 Archivos Cargados")
        if not st.session_state.uploaded_files:
            st.info("No hay archivos cargados.")
        else:
            for filename, df in st.session_state.uploaded_files.items():
                col_a, col_b, col_c = st.columns([3, 1, 1])
                with col_a: st.write(f"📄 **{filename}** ({df.shape[0]} filas × {df.shape[1]} cols)")
                with col_b:
                    if st.button("👁️ Ver", key=f"v_{filename}"):
                        st.session_state[f"show_{filename}"] = not st.session_state.get(f"show_{filename}", False)
                with col_c:
                    if st.button("🗑️ Borrar", key=f"d_{filename}", type="secondary"):
                        del st.session_state.uploaded_files[filename]
                        if f"show_{filename}" in st.session_state:
                            del st.session_state[f"show_{filename}"]
                        st.rerun()

                if st.session_state.get(f"show_{filename}", False):
                    st.dataframe(df, width="stretch")
                    col_conc = next((c for c in df.columns if 'concentracion' in c.lower() or 'conc' in c.lower()), None)
                    if col_conc:
                        st.markdown(f"**📊 Estadística de `{col_conc}`:**")
                        st.write(df[col_conc].describe())
                        fig_hist = px.histogram(df, x=col_conc, nbins=10, title=f"Distribución en {filename}")
                        st.plotly_chart(fig_hist, width="stretch")

# ============================================================================
# SECCIÓN 6: EPIDEMIOLOGÍA
# ============================================================================
elif seccion == "🌍 Epidemiología":
    st.header("🌍 Retrocálculo Epidemiológico")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📥 Parámetros")
        analito_epi = st.selectbox("Analito:", list(ANALITOS.keys()), key="analito_epi")
        info_epi = ANALITOS[analito_epi]
        C_agua = st.number_input(f"Concentración de {info_epi['abrev']} (ng/L):", 0.0, value=500.0, step=50.0)
        Q = st.number_input("Caudal diario PTAR (L/día):", 1000.0, value=1000000.0, step=100000.0, format="%.0f")
        P = st.number_input("Población servida (hab):", 100.0, value=100000.0, step=10000.0, format="%.0f")
        f_excrecion = st.number_input(f"Fracción de excreción ({info_epi['abrev']} = {info_epi['f_excrecion']}):",
            0.01, 1.0, info_epi['f_excrecion'], 0.01, format="%.2f")

    with col2:
        st.subheader("📈 Resultados")
        consumo = (C_agua * Q * 1000) / (P * f_excrecion * 1e6)
        carga_diaria = (C_agua * Q) / 1e6

        st.markdown(f"""
        <div class="success-box">
        <h4>🎯 Carga Másica Normalizada ({info_epi['abrev']})</h4>
        <p style="font-size: 28px; font-weight: bold; color: #28a745;">{consumo:.2f} mg/día/1000 hab</p>
        <p>Carga diaria total: {carga_diaria:.2f} mg/día</p>
        </div>
        """, unsafe_allow_html=True)

        if consumo < 500: nivel, color = "Bajo", "#28a745"
        elif consumo < 2000: nivel, color = "Moderado", "#ffc107"
        else: nivel, color = "Alto", "#dc3545"

        st.markdown(f"""
        <div style="background-color: {color}; padding: 1rem; border-radius: 10px; color: white;">
        <h4>📊 Nivel de Consumo</h4><p style="font-size: 24px; font-weight: bold;">{nivel}</p>
        </div>
        """, unsafe_allow_html=True)

        st.session_state.resultados_practica['epidemiologia'] = {
            'analito': analito_epi, 'abrev': info_epi['abrev'],
            'consumo': consumo, 'carga_diaria': carga_diaria, 'nivel': nivel
        }

    st.markdown("### 🇨🇴 Comparación con Estudios en Colombia")
    datos_col = {
        "Ciudad": ["Medellín (San Fernando)", "Bogotá (Salitre)", "Pereira", "Armenia", "Manizales", "👉 Tu Muestra"],
        "Carga BE": [4000, 900, 4857, 2988, 645, consumo if info_epi['abrev'] == 'BE' else consumo * 0.5]
    }
    df_comp = pd.DataFrame(datos_col)
    fig_comp = px.bar(df_comp, x="Ciudad", y="Carga BE", color="Ciudad",
        color_discrete_map={"Medellín (San Fernando)": "#667eea", "Bogotá (Salitre)": "#764ba2",
            "Pereira": "#f093fb", "Armenia": "#4facfe", "Manizales": "#43e97b", "👉 Tu Muestra": "#ff6b6b"},
        title="Comparación de Carga Másica (mg/día/1000 hab)")
    fig_comp.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig_comp, width="stretch")

# ============================================================================
# SECCIÓN 7: REPORTE PDF
# ============================================================================
elif seccion == "📄 Reporte PDF":
    st.header("📄 Generación de Reporte PDF")
    st.info("Genera un reporte completo de la práctica con todos los resultados.")

    col1, col2 = st.columns(2)
    with col1:
        nombre_estudiante = st.text_input("Nombre del estudiante:", "Estudiante UdeA")
        codigo = st.text_input("Código:", "2024XXXXX")
        grupo = st.text_input("Grupo:", "A1")
        fecha_practica = st.date_input("Fecha de práctica:", datetime.now())
    with col2:
        titulo_reporte = st.text_input("Título de la práctica:",
            "Detección de Psicoactivos en Aguas Residuales por WBE")
        observaciones = st.text_area("Observaciones:",
            "Práctica realizada en condiciones de laboratorio simulado.", height=100)

    st.markdown("### 📊 Resultados disponibles para el reporte")
    res = st.session_state.resultados_practica
    cols_res = st.columns(3)
    with cols_res[0]:
        st.markdown(f"**Cromatograma:** {'✅' if 'cromatograma' in res else '⚠️ No realizado'}")
        if 'cromatograma' in res:
            st.write(f"Analitos: {', '.join(res['cromatograma']['analitos'])}")
    with cols_res[1]:
        st.markdown(f"**Calibración:** {'✅' if 'calibracion' in res else '⚠️ No realizada'}")
        if 'calibracion' in res:
            st.write(f"R² = {res['calibracion']['r2']:.4f}")
    with cols_res[2]:
        st.markdown(f"**Epidemiología:** {'✅' if 'epidemiologia' in res else '⚠️ No calculada'}")
        if 'epidemiologia' in res:
            st.write(f"{res['epidemiologia']['abrev']}: {res['epidemiologia']['consumo']:.2f} mg/día/1000 hab")

    if st.button("📄 Generar y Descargar Reporte PDF", type="primary"):
        try:
            # Gráfico de calibración
            fig_cal_img = None
            if 'calibracion' in res:
                fig, ax = plt.subplots(figsize=(8, 5))
                conc_ej = np.array([10, 50, 100, 250, 500])
                areas_ej = res['calibracion']['pendiente'] * conc_ej + res['calibracion']['intercepto']
                ax.scatter(conc_ej, areas_ej, color='red', s=80, zorder=5, label='Puntos experimentales')
                x_fit = np.linspace(0, 550, 100)
                ax.plot(x_fit, res['calibracion']['pendiente'] * x_fit + res['calibracion']['intercepto'],
                        'b-', linewidth=2, label=f"Ajuste lineal (R²={res['calibracion']['r2']:.4f})")
                ax.set_xlabel('Concentración (ng/mL)'); ax.set_ylabel('Área del pico (u.a.)')
                ax.set_title('Curva de Calibración'); ax.legend(); ax.grid(True, alpha=0.3)
                buf = io.BytesIO(); fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                buf.seek(0); fig_cal_img = buf.getvalue(); plt.close(fig)

            # Gráfico de epidemiología
            fig_epi_img = None
            if 'epidemiologia' in res:
                fig, ax = plt.subplots(figsize=(8, 5))
                ciudades = ['Medellín', 'Bogotá', 'Pereira', 'Armenia', 'Manizales', 'Tu muestra']
                cargas = [4000, 900, 4857, 2988, 645, res['epidemiologia']['consumo']]
                colores = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#ff6b6b']
                bars = ax.bar(ciudades, cargas, color=colores)
                ax.set_ylabel('Carga másica (mg/día/1000 hab)')
                ax.set_title(f"Comparación de consumo de {res['epidemiologia']['abrev']}")
                ax.tick_params(axis='x', rotation=45)
                for bar, val in zip(bars, cargas):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                            f'{val:.0f}', ha='center', va='bottom', fontsize=9)
                buf2 = io.BytesIO(); fig.savefig(buf2, format='png', dpi=150, bbox_inches='tight')
                buf2.seek(0); fig_epi_img = buf2.getvalue(); plt.close(fig)

            # PDF
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)

            pdf.add_page()
            pdf.set_font("Helvetica", "B", 22)
            _cell(pdf, 0, 15, "REPORTE DE PRÁCTICA DE LABORATORIO", align='C')
            pdf.ln(5)
            pdf.set_font("Helvetica", "", 14)
            _cell(pdf, 0, 10, titulo_reporte, align='C')
            pdf.ln(10)
            pdf.set_font("Helvetica", "", 12)
            _cell(pdf, 0, 8, "Universidad de Antioquia", align='C')
            _cell(pdf, 0, 8, "Facultad de Ciencias Exactas y Naturales", align='C')
            _cell(pdf, 0, 8, "Programa de Química / Ingeniería Ambiental", align='C')
            pdf.ln(15)

            pdf.set_font("Helvetica", "B", 12)
            _cell(pdf, 0, 8, "INFORMACIÓN DEL ESTUDIANTE")
            pdf.set_font("Helvetica", "", 11)
            _cell(pdf, 95, 7, f"Nombre: {nombre_estudiante}", ln=False)
            _cell(pdf, 95, 7, f"Código: {codigo}")
            _cell(pdf, 95, 7, f"Grupo: {grupo}", ln=False)
            _cell(pdf, 95, 7, f"Fecha: {fecha_practica.strftime('%d/%m/%Y')}")
            pdf.ln(5)

            pdf.set_font("Helvetica", "B", 12)
            _cell(pdf, 0, 8, "CONFIGURACIÓN DE LABORATORIO")
            pdf.set_font("Helvetica", "", 11)
            _cell(pdf, 0, 7, f"Equipo cromatográfico: {hplc_brand}")
            _cell(pdf, 0, 7, f"Cartucho SPE: {spe_cartridge}")
            pdf.ln(5)

            if 'cromatograma' in res:
                pdf.add_page()
                pdf.set_font("Helvetica", "B", 14)
                _cell(pdf, 0, 10, "1. ANÁLISIS CROMATOGRÁFICO")
                pdf.set_font("Helvetica", "", 11)
                _cell(pdf, 0, 7, f"Analitos simulados: {', '.join(res['cromatograma']['analitos'])}")
                _cell(pdf, 0, 7, f"Concentración base: {res['cromatograma']['concentracion']} ng/mL")
                _cell(pdf, 0, 7, f"Resolución: {res['cromatograma']['resolucion']} | Ruido: {res['cromatograma']['ruido']}")
                pdf.ln(5)
                pdf.set_font("Helvetica", "B", 11)
                _cell(pdf, 0, 8, "Áreas de picos calculadas:")
                pdf.set_font("Helvetica", "", 10)
                _cell(pdf, 60, 7, "Analito", border=1, ln=False)
                _cell(pdf, 40, 7, "Abrev.", border=1, ln=False)
                _cell(pdf, 40, 7, "t_R (min)", border=1, ln=False)
                _cell(pdf, 50, 7, "Área (u.a.·min)", border=1)
                for nombre in res['cromatograma']['analitos']:
                    info = ANALITOS[nombre]
                    _cell(pdf, 60, 7, nombre, border=1, ln=False)
                    _cell(pdf, 40, 7, info['abrev'], border=1, ln=False)
                    _cell(pdf, 40, 7, str(info['t_r']), border=1, ln=False)
                    _cell(pdf, 50, 7, f"{res['cromatograma']['areas'][nombre]:.2f}", border=1)

            if 'calibracion' in res:
                pdf.add_page()
                pdf.set_font("Helvetica", "B", 14)
                _cell(pdf, 0, 10, "2. CURVA DE CALIBRACIÓN E INCERTIDUMBRE")
                pdf.set_font("Helvetica", "", 11)
                cal = res['calibracion']
                _cell(pdf, 0, 7, f"Ecuación: y = {cal['pendiente']:.2f}x + {cal['intercepto']:.2f}")
                _cell(pdf, 0, 7, f"Coeficiente de determinación (R²): {cal['r2']:.4f}")
                _cell(pdf, 0, 7, f"Error estándar de la pendiente: {cal['std_err']:.2f}")
                pdf.ln(3)
                pdf.set_font("Helvetica", "B", 11)
                _cell(pdf, 0, 8, "Análisis de Incertidumbre:")
                pdf.set_font("Helvetica", "", 11)
                _cell(pdf, 0, 7, f"Incertidumbre combinada (uc): {cal['u_comb']:.2f}%")
                _cell(pdf, 0, 7, f"Factor de cobertura (k): {cal['k']}")
                _cell(pdf, 0, 7, f"Incertidumbre expandida (U): {cal['u_expandida']:.2f}%")
                if fig_cal_img:
                    pdf.ln(5)
                    pdf.image(io.BytesIO(fig_cal_img), x=10, w=190)

            if 'epidemiologia' in res:
                pdf.add_page()
                pdf.set_font("Helvetica", "B", 14)
                _cell(pdf, 0, 10, "3. RETROCÁLCULO EPIDEMIOLÓGICO")
                pdf.set_font("Helvetica", "", 11)
                epi = res['epidemiologia']
                _cell(pdf, 0, 7, f"Analito: {epi['analito']} ({epi['abrev']})")
                _cell(pdf, 0, 7, f"Carga másica normalizada: {epi['consumo']:.2f} mg/día/1000 hab")
                _cell(pdf, 0, 7, f"Carga diaria total: {epi['carga_diaria']:.2f} mg/día")
                _cell(pdf, 0, 7, f"Nivel de consumo estimado: {epi['nivel']}")
                pdf.ln(5)
                pdf.set_font("Helvetica", "B", 11)
                _cell(pdf, 0, 8, "Fórmula aplicada (EMCDDA):")
                pdf.set_font("Helvetica", "", 10)
                _cell(pdf, 0, 7, "Consumo = (C_agua x Q x 1000) / (P x f_excrecion)")
                pdf.ln(3)
                if fig_epi_img:
                    pdf.image(io.BytesIO(fig_epi_img), x=10, w=190)

            pdf.add_page()
            pdf.set_font("Helvetica", "B", 14)
            _cell(pdf, 0, 10, "4. OBSERVACIONES Y CONCLUSIONES")
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 6, observaciones)
            pdf.ln(10)

            pdf.set_font("Helvetica", "B", 12)
            _cell(pdf, 0, 8, "REFERENCIAS")
            pdf.set_font("Helvetica", "", 10)
            refs = [
                "- EMCDDA. Technical guidelines for wastewater analysis.",
                "- Ruiz Montilla et al. (2022). Estudio WBE Medellin. Universidad de Caldas.",
                "- Bijlsma et al. (2016). Wastewater-based epidemiology in Colombia.",
                "- NTC-ISO 5667-3 (Muestreo de aguas)."
            ]
            for r in refs:
                _cell(pdf, 0, 6, r)

            pdf.ln(10)
            pdf.set_font("Helvetica", "I", 9)
            _cell(pdf, 0, 6,
                  f"Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} | Simulador WBE v3.0 - Universidad de Antioquia",
                  align='C')

            # FIX CRÍTICO: bytearray -> bytes
            pdf_bytes = bytes(pdf.output())

            st.download_button(
                label="⬇️ Descargar Reporte PDF",
                data=pdf_bytes,
                file_name=f"Reporte_WBE_{nombre_estudiante.replace(' ', '_')}_{fecha_practica.strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                type="primary"
            )
            st.success("✅ PDF generado exitosamente. Haz clic en el botón para descargarlo.")

        except Exception as e:
            st.error(f"Error al generar el PDF: {e}")
            st.exception(e)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; padding: 1rem;">
    <p>🧪 Simulador WBE v3.0 - Universidad de Antioquia</p>
    <p>Desarrollado para prácticas de pregrado y posgrado en Química Analítica y Ambiental</p>
    <p>© 2026 - Todos los derechos reservados</p>
</div>
""", unsafe_allow_html=True)
