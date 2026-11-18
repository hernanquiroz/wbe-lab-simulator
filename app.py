# ============================================================================
# SIMULADOR INTERACTIVO: DETECCIÓN DE PSICOACTIVOS EN AGUAS RESIDUALES (WBE)
# Versión Streamlit - Universidad de Antioquia
# ============================================================================

import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import io
from scipy import stats

# Alias compatible con NumPy 1.x y 2.x (Evita el error de trapz)
trapz = getattr(np, 'trapezoid', None) or np.trapz

# Configuración de la página
st.set_page_config(
    page_title="Simulador WBE - UdeA",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar estado de sesión para archivos CSV
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {}

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
    .info-box { background-color: #f0f2f6; padding: 1rem; border-radius: 10px; border-left: 5px solid #667eea; margin: 1rem 0; }
    .success-box { background-color: #d4edda; padding: 1rem; border-radius: 10px; border-left: 5px solid #28a745; }
    .warning-box { background-color: #fff3cd; padding: 1rem; border-radius: 10px; border-left: 5px solid #ffc107; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🧪 Simulador de Laboratorio WBE: Detección de Psicoactivos</h1>
    <h3>Epidemiología Basada en Aguas Residuales</h3>
    <p>Universidad de Antioquia - Práctica de Laboratorio Interactiva</p>
</div>
""", unsafe_allow_html=True)

# Sidebar: Configuración Global de Equipos
st.sidebar.title("⚙️ Configuración de Laboratorio")
st.sidebar.markdown("**Equipo Cromatográfico:**")
hplc_brand = st.sidebar.selectbox(
    "Marca/Modelo HPLC/LC-MS",
    ["Agilent 1260 Infinity II (HPLC-UV)", "Waters Acquity UPLC (LC-MS/MS)", "Shimadzu Nexera (LC-MS/MS)"]
)
st.sidebar.markdown("**Extracción en Fase Sólida:**")
spe_cartridge = st.sidebar.selectbox(
    "Tipo de Cartucho SPE",
    ["Oasis HLB (Waters) - Estándar", "Strata-X (Phenomenex)", "Bond Elut Plexa (Agilent)"]
)

st.sidebar.markdown("---")
seccion = st.sidebar.radio(
    "Navegación:",
    ["🏠 Inicio", "🎬 Animación SPE", "📊 Cromatograma", "📈 Calibración e Incertidumbre", "📂 Gestión de Datos CSV", "🌍 Epidemiología"]
)

# ============================================================================
# SECCIÓN 1: INICIO
# ============================================================================
if seccion == "🏠 Inicio":
    st.header("Bienvenido al Simulador de Laboratorio WBE")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Analito Modelo", "Benzoilecgonina", "Metabolito de cocaína")
    with col2: st.metric("Cartucho Seleccionado", spe_cartridge.split('(')[0])
    with col3: st.metric("Equipo Seleccionado", hplc_brand.split('(')[0])

    st.markdown("""
    ### 📋 Objetivo de la Práctica
    Esta herramienta integral permite a estudiantes de pregrado y posgrado:
    1. **Configurar** el método según el equipo disponible en el laboratorio.
    2. **Visualizar** el proceso de Extracción en Fase Sólida (SPE) con animación real.
    3. **Simular** cromatogramas y evaluar el efecto del ruido y la resolución.
    4. **Construir** curvas de calibración y estimar la incertidumbre de la medición.
    5. **Gestionar** datos experimentales reales mediante carga de archivos CSV.
    6. **Calcular** el retrocálculo epidemiológico y compararlo con datos de Colombia.
    """)

# ============================================================================
# SECCIÓN 2: ANIMACIÓN SPE
# ============================================================================
elif seccion == "🎬 Animación SPE":
    st.header("🎬 Proceso de Extracción en Fase Sólida (SPE)")
    st.info(f"Simulación adaptada para cartuchos de tipo: **{spe_cartridge}**")

    PASOS = ["1. Acondicionamiento", "2. Carga de Muestra", "3. Lavado", "4. Secado", "5. Elución", "6. Concentración"]
    INFO = {
        "1. Acondicionamiento": {"color": "#8e44ad", "vol": 5, "solv": "Metanol + Agua (pH 3)", "tiempo": 3, "particulas": False, "flujo": True, "nivel": [0.78, 0.30], "desc": "Activar sitios hidrofóbicos. ⚠️ No dejar secar."},
        "2. Carga de Muestra": {"color": "#7f5539", "vol": 50, "solv": "Agua residual filtrada (pH 3)", "tiempo": 8, "particulas": True, "flujo": True, "nivel": [0.78, 0.45], "desc": "Los analitos se adsorben en la fase estacionaria. Flujo: 1–2 gotas/seg."},
        "3. Lavado": {"color": "#74b9ff", "vol": 5, "solv": "Agua ultrapura (pH 3)", "tiempo": 3, "particulas": True, "flujo": True, "nivel": [0.70, 0.45], "desc": "Eliminar sales e interferencias. Los analitos (●) permanecen retenidos."},
        "4. Secado": {"color": "#ecf0f1", "vol": 0, "solv": "Vacío (aire)", "tiempo": 12, "particulas": True, "flujo": True, "nivel": [0.0, 0.0], "desc": "Eliminar toda el agua (10–15 min). Crítico para una elución eficiente."},
        "5. Elución": {"color": "#00b894", "vol": 6, "solv": "Metanol + 2% NH₄OH", "tiempo": 4, "particulas": True, "flujo": True, "nivel": [0.65, 0.45], "desc": "Desorber los analitos. El medio básico rompe las interacciones hidrofóbicas."},
        "6. Concentración": {"color": "#e17055", "vol": 1, "solv": "Evaporación N₂ → reconstitución", "tiempo": 10, "particulas": False, "flujo": False, "nivel": [0.15, 0.10], "desc": "Concentrar 50–100x. Evaporar ≤ 30°C y reconstituir en 1 mL."},
    }

    def _fig_paso(paso, f, total_frames):
        d = INFO[paso]
        prog = f / max(total_frames - 1, 1)
        fig = go.Figure()
        fig.add_shape(type="rect", x0=0.30, y0=0.18, x1=0.70, y1=0.82, fillcolor="#dfe6e9", opacity=0.5, line=dict(color="#2d3436", width=2))
        fig.add_shape(type="rect", x0=0.35, y0=0.30, x1=0.65, y1=0.70, fillcolor="#f5e6c8", opacity=0.85, line=dict(color="#b2bec3", width=1))
        fig.add_shape(type="rect", x0=0.27, y0=0.82, x1=0.73, y1=0.88, fillcolor="#b2bec3", opacity=0.6, line=dict(color="#2d3436", width=1))
        fig.add_shape(type="rect", x0=0.47, y0=0.10, x1=0.53, y1=0.18, fillcolor="#b2bec3", opacity=0.6)
        fig.add_shape(type="rect", x0=0.42, y0=0.02, x1=0.58, y1=0.10, fillcolor="#ffffff", opacity=0.9, line=dict(color="#2d3436", width=1.5))

        top, bot = d["nivel"][0], d["nivel"][1]
        y_liq = top - (top - bot) * prog
        if y_liq > bot + 0.01:
            fig.add_shape(type="rect", x0=0.35, y0=bot, x1=0.65, y1=y_liq, fillcolor=d["color"], opacity=0.75, line=dict(width=0))

        if d["flujo"]:
            for i in range(6):
                fase = (prog * 3 + i / 6) % 1.0
                yg = 0.82 - fase * 0.74
                if 0.05 < yg < 0.82:
                    fig.add_trace(go.Scatter(x=[0.5], y=[yg], mode="markers", marker=dict(size=7, color=d["color"]), showlegend=False))

        if d["particulas"]:
            rng = np.random.default_rng(7)
            xs, ys = rng.uniform(0.38, 0.62, 22), rng.uniform(0.32, 0.68, 22)
            if paso == "2. Carga de Muestra": ys = np.maximum(0.32, ys + (1 - prog) * 0.5)
            elif paso == "3. Lavado": 
                fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers", marker=dict(size=6, color="#d63031"), showlegend=False))
                xg = rng.uniform(0.38, 0.62, 15)
                fig.add_trace(go.Scatter(x=xg, y=[0.32 + (1 - prog) * 0.4]*15, mode="markers", marker=dict(size=4, color="#636e72", symbol="x"), showlegend=False, opacity=0.6))
                return fig # Early return for lavado to avoid double plotting
            elif paso == "5. Elución": ys = ys - prog * 0.55
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers", marker=dict(size=6, color="#d63031"), showlegend=False))

        if paso in ("2. Carga de Muestra", "3. Lavado", "5. Elución"):
            fig.add_shape(type="rect", x0=0.42, y0=0.02, x1=0.58, y1=0.02 + prog * 0.07, fillcolor=d["color"], opacity=0.8, line=dict(width=0))

        fig.add_annotation(x=0.10, y=0.50, text="Fase<br>HLB", showarrow=False, font=dict(size=10))
        fig.add_annotation(x=0.90, y=0.50, text="Analitos ●", showarrow=False, font=dict(size=10, color="#d63031"))
        fig.add_annotation(x=0.5, y=0.95, text=f"<b>{paso}</b> | {d['solv']} | Vol: {d['vol']*(1-prog):.1f} mL", showarrow=False, font=dict(size=11), bgcolor="#fff3cd", borderwidth=1)
        fig.update_layout(xaxis=dict(visible=False, range=[0, 1]), yaxis=dict(visible=False, range=[0, 1.02]), height=450, margin=dict(l=20, r=20, t=40, b=20))
        return fig

    st.subheader("🎞️ Modo Automático")
    paso_auto = st.selectbox("Paso a animar:", PASOS, key="paso_auto")
    fps = st.slider("Velocidad (frames/seg)", 5, 30, 15, key="fps_auto")
    
    total = 60
    frames = [go.Frame(data=_fig_paso(paso_auto, f, total).data, layout=_fig_paso(paso_auto, f, total).layout, name=str(f)) for f in range(total)]
    fig_anim = _fig_paso(paso_auto, 0, total)
    fig_anim.frames = frames
    fig_anim.update(layout=dict(updatemenus=[dict(type="buttons", x=0.02, y=1.12, buttons=[
        dict(label="▶️ Reproducir", method="animate", args=[None, dict(frame=dict(duration=1000//fps), fromcurrent=True)]),
        dict(label="⏸️ Pausar", method="animate", args=[[None], dict(mode="immediate")])
    ])]))
    st.plotly_chart(fig_anim, width="stretch")
    st.markdown(INFO[paso_auto]["desc"])

# ============================================================================
# SECCIÓN 3: CROMATOGRAMA
# ============================================================================
elif seccion == "📊 Cromatograma":
    st.header("📊 Simulador de Cromatografía")
    st.info(f"Configuración simulada para: **{hplc_brand}**")
    
    col1, col2, col3 = st.columns(3)
    with col1: concentracion = st.slider("Concentración (ng/mL):", 10, 500, 100, 10)
    with col2: ruido = st.slider("Ruido de fondo:", 0.0, 10.0, 2.0, 0.5)
    with col3: resolucion = st.slider("Resolución cromatográfica:", 0.5, 2.0, 1.0, 0.1)

    t_r = 7.0
    sigma = 0.3 / resolucion
    tiempo = np.linspace(0, 15, 1000)
    pico = concentracion * np.exp(-((tiempo - t_r) ** 2) / (2 * sigma ** 2))
    senal = pico + np.random.normal(0, ruido, len(tiempo)) + 5

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tiempo, y=senal, mode='lines', name='Señal', line=dict(color='blue', width=2)))
    fig.add_shape(type='rect', x0=t_r - 3*sigma, y0=5, x1=t_r + 3*sigma, y1=pico.max() + 5, fillcolor='lightblue', opacity=0.3)
    
    area = trapz(pico, tiempo)
    fig.add_annotation(text=f"Área: {area:.2f}<br>Altura: {pico.max():.2f}", x=12, y=senal.max() * 0.8, showarrow=True, bgcolor='lightyellow')
    fig.update_layout(title='Cromatograma Simulado - Benzoilecgonina', xaxis_title='Tiempo (min)', yaxis_title='Intensidad', template='plotly_white', height=500)
    st.plotly_chart(fig, width="stretch")

# ============================================================================
# SECCIÓN 4: CALIBRACIÓN E INCERTIDUMBRE (NUEVO)
# ============================================================================
elif seccion == "📈 Calibración e Incertidumbre":
    st.header("📈 Curva de Calibración y Análisis de Incertidumbre")
    st.markdown("Ingresa los pares de datos (Concentración, Área) separados por coma. Ejemplo: `10, 1500`")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📥 Datos de Calibración")
        datos_texto = st.text_area(
            "Concentración (ng/mL), Área del pico",
            "10, 1500\n50, 7200\n100, 14500\n250, 36000\n500, 71000",
            height=200
        )
    
    with col2:
        st.subheader("📊 Parámetros de Incertidumbre")
        u_rep = st.number_input("Incertidumbre por repetibilidad (%)", 0.0, 20.0, 5.0, 0.1)
        u_vol = st.number_input("Incertidumbre volumétrica (pipetas/matraz) (%)", 0.0, 10.0, 2.0, 0.1)
        k = st.number_input("Factor de cobertura (k)", 1.0, 3.0, 2.0, 0.1, help="k=2 para ~95% de confianza")

    if st.button("Calcular Regresión e Incertidumbre", type="primary"):
        try:
            lineas = [linea.strip() for linea in datos_texto.split('\n') if linea.strip()]
            conc = []
            areas = []
            for linea in lineas:
                c, a = map(float, linea.split(','))
                conc.append(c)
                areas.append(a)
            
            conc = np.array(conc)
            areas = np.array(areas)
            
            # Regresión lineal
            slope, intercept, r_value, p_value, std_err = stats.linregress(conc, areas)
            r_squared = r_value**2
            
            # Incertidumbre combinada (simplificada para fines educativos)
            u_cal = (std_err / np.mean(areas)) * 100 # Incertidumbre de la calibración en %
            u_comb = np.sqrt(u_cal**2 + u_rep**2 + u_vol**2)
            u_expandida = k * u_comb

            st.success(f"✅ Regresión exitosa. Ecuación: $y = {slope:.2f}x + {intercept:.2f}$ | $R^2 = {r_squared:.4f}$")
            
            # Gráfico de calibración
            fig_cal = go.Figure()
            fig_cal.add_trace(go.Scatter(x=conc, y=areas, mode='markers', name='Puntos experimentales', marker=dict(size=8, color='red')))
            x_fit = np.linspace(0, max(conc)*1.1, 100)
            y_fit = slope * x_fit + intercept
            fig_cal.add_trace(go.Scatter(x=x_fit, y=y_fit, mode='lines', name=f'Línea de ajuste (R²={r_squared:.4f})', line=dict(color='blue')))
            fig_cal.update_layout(title='Curva de Calibración', xaxis_title='Concentración (ng/mL)', yaxis_title='Área del pico', template='plotly_white')
            st.plotly_chart(fig_cal, width="stretch")

            st.markdown(f"""
            <div class="info-box">
            <h4>📐 Resumen de Incertidumbre</h4>
            <ul>
                <li><strong>Incertidumbre de calibración (u_cal):</strong> {u_cal:.2f} %</li>
                <li><strong>Incertidumbre por repetibilidad (u_rep):</strong> {u_rep:.2f} %</li>
                <li><strong>Incertidumbre volumétrica (u_vol):</strong> {u_vol:.2f} %</li>
                <li><strong>Incertidumbre combinada (uc):</strong> {u_comb:.2f} %</li>
                <li><strong>Incertidumbre expandida (U, k={k}):</strong> <b>{u_expandida:.2f} %</b></li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error al procesar los datos. Asegúrate de usar el formato 'concentracion, area' por línea. Detalle: {e}")

# ============================================================================
# SECCIÓN 5: GESTIÓN DE DATOS CSV (NUEVO)
# ============================================================================
elif seccion == "📂 Gestión de Datos CSV":
    st.header("📂 Gestión y Análisis de Datos Experimentales (CSV)")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("⬆️ Cargar Archivo")
        uploaded_file = st.file_uploader("Selecciona un archivo CSV", type=['csv'])
        
        if uploaded_file is not None:
            if uploaded_file.name not in st.session_state.uploaded_files:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.session_state.uploaded_files[uploaded_file.name] = df
                    st.success(f"✅ '{uploaded_file.name}' cargado exitosamente.")
                except Exception as e:
                    st.error(f"Error al leer el CSV: {e}")
            else:
                st.warning("Este archivo ya está cargado.")

        st.markdown("### 📥 Formato Esperado del CSV")
        st.code("Muestra,Concentracion_ng_L,Area_Pico\nM1,450.5,12500\nM2,460.2,12800", language="csv")
        btn_template = st.download_button(
            label="Descargar Plantilla CSV",
            data="Muestra,Concentracion_ng_L,Area_Pico\nM1,450.5,12500\nM2,460.2,12800\nM3,445.0,12300",
            file_name="plantilla_datos_wbe.csv",
            mime="text/csv"
        )

    with col2:
        st.subheader("📁 Archivos Cargados")
        if not st.session_state.uploaded_files:
            st.info("No hay archivos cargados en la sesión actual.")
        else:
            for filename, df in st.session_state.uploaded_files.items():
                col_a, col_b, col_c = st.columns([3, 1, 1])
                with col_a: st.write(f"📄 **{filename}** ({df.shape[0]} filas, {df.shape[1]} columnas)")
                with col_b: 
                    if st.button("👁️ Ver", key=f"view_{filename}"):
                        st.session_state[f"show_{filename}"] = not st.session_state.get(f"show_{filename}", False)
                with col_c:
                    if st.button("🗑️ Borrar", key=f"del_{filename}", type="secondary"):
                        del st.session_state.uploaded_files[filename]
                        if f"show_{filename}" in st.session_state:
                            del st.session_state[f"show_{filename}"]
                        st.rerun()
                
                # Mostrar tabla si se solicitó
                if st.session_state.get(f"show_{filename}", False):
                    st.dataframe(df, use_container_width=True)
                    
                    # Análisis automático si existe la columna de concentración
                    if 'Concentracion_ng_L' in df.columns or 'concentracion_ng_l' in df.columns:
                        col_name = 'Concentracion_ng_L' if 'Concentracion_ng_L' in df.columns else 'concentracion_ng_l'
                        st.markdown(f"**📊 Estadística Descriptiva de `{col_name}`:**")
                        st.write(df[col_name].describe())
                        
                        fig_hist = px.histogram(df, x=col_name, nbins=10, title=f"Distribución de Concentraciones en {filename}")
                        st.plotly_chart(fig_hist, width="stretch")

# ============================================================================
# SECCIÓN 6: EPIDEMIOLOGÍA
# ============================================================================
elif seccion == "🌍 Epidemiología":
    st.header("🌍 Retrocálculo Epidemiológico y Comparación")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📥 Parámetros de Entrada")
        C_agua = st.number_input("Concentración de Benzoilecgonina (ng/L):", 0.0, value=500.0, step=50.0)
        Q = st.number_input("Caudal diario PTAR (L/día):", 1000.0, value=1000000.0, step=100000.0, format="%.0f")
        P = st.number_input("Población servida (habitantes):", 100.0, value=100000.0, step=10000.0, format="%.0f")
        f_excrecion = st.number_input("Fracción de excreción (BE = 0.45):", 0.01, 1.0, 0.45, 0.01, format="%.2f")

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

        if consumo < 500: nivel, color = "Bajo", "#28a745"
        elif consumo < 2000: nivel, color = "Moderado", "#ffc107"
        else: nivel, color = "Alto", "#dc3545"

        st.markdown(f"""
        <div style="background-color: {color}; padding: 1rem; border-radius: 10px; color: white;">
        <h4>📊 Nivel de Consumo Estimado</h4>
        <p style="font-size: 24px; font-weight: bold;">{nivel}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🇨🇴 Comparación con Estudios Reales en Colombia")
    datos_colombia = {
        "Ciudad": ["Medellín (San Fernando)", "Bogotá (Salitre)", "Pereira", "Armenia", "Manizales", "👉 Tu Muestra"],
        "Carga (mg/día/1000 hab)": [4000, 900, 4857, 2988, 645, consumo]
    }
    df_comp = pd.DataFrame(datos_colombia)
    fig_comp = px.bar(df_comp, x="Ciudad", y="Carga (mg/día/1000 hab)", color="Ciudad",
        color_discrete_map={"Medellín (San Fernando)": "#667eea", "Bogotá (Salitre)": "#764ba2", "Pereira": "#f093fb",
                            "Armenia": "#4facfe", "Manizales": "#43e97b", "👉 Tu Muestra": "#ff6b6b"},
        title="Comparación de Consumo de Cocaína (Benzoilecgonina)")
    fig_comp.update_layout(xaxis_title="Ciudad / PTAR", yaxis_title="Carga Másica Normalizada", height=500, showlegend=False)
    st.plotly_chart(fig_comp, width="stretch")

    st.markdown("""
    <div class="info-box">
    <h4>📚 Referencias</h4>
    <ul>
    <li><strong>Medellín (2022):</strong> PTAR San Fernando - Carga promedio ~3000-5000 mg/día/1000 hab (Ruiz Montilla et al., 2022).</li>
    <li><strong>Bogotá (2021):</strong> PTAR Salitre - Carga promedio ~800-1000 mg/día/1000 hab.</li>
    <li><strong>Eje Cafetero (2020):</strong> Pereira mostró el mayor consumo (4857 mg/día/1000 hab).</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

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
