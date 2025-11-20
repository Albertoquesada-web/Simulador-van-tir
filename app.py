import streamlit as st
import pandas as pd
import numpy_financial as npf
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Simulador Financiero Pro", layout="wide", page_icon="📊")

# Estilos CSS personalizados para un look profesional
st.markdown("""
    <style>
    .big-font { font-size:20px !important; font-weight: bold; color: #2C3E50; }
    .metric-card { background-color: #f0f2f6; border-radius: 10px; padding: 20px; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- TÍTULO E INTRODUCCIÓN ---
st.title("📊 Simulador de Evaluación de Proyectos (VAN y TIR)")
st.markdown("### Herramienta interactiva para el análisis de flujos de caja")
st.markdown("---")

# --- BARRA LATERAL (PARAMETROS GENERALES) ---
with st.sidebar:
    st.header("⚙️ Parámetros del Proyecto")
    
    inversion_inicial = st.number_input(
        "Inversión Inicial ($)", 
        value=10000.0, 
        step=1000.0,
        help="Monto del desembolso inicial (Periodo 0)"
    )
    
    tasa_descuento = st.number_input(
        "Tasa de Descuento / COK (%)", 
        value=12.0, 
        step=0.5,
        help="Costo de Oportunidad del Capital o Tasa de Interés esperada"
    )
    
    num_periodos = st.slider("Duración del Proyecto (Años/Periodos)", min_value=1, max_value=20, value=5)

# --- SECCIÓN PRINCIPAL: EDICIÓN DE FLUJOS ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 Editor de Flujos")
    st.write("Modifique los ingresos y egresos por periodo:")
    
    # Crear DataFrame inicial con ceros
    data = {
        "Periodo": list(range(1, num_periodos + 1)),
        "Ingresos ($)": [0.0] * num_periodos,
        "Egresos ($)": [0.0] * num_periodos
    }
    
    # Pre-llenar con valores ejemplo para que no se vea vacío al inicio
    if num_periodos >= 3:
        data["Ingresos ($)"] = [3000.0, 4000.0, 5000.0] + [5000.0]*(num_periodos-3)
        data["Egresos ($)"] = [1000.0, 1200.0, 1300.0] + [1300.0]*(num_periodos-3)
        
    df_input = pd.DataFrame(data)
    
    # WIDGET EDITABLE (La clave de tu solicitud)
    edited_df = st.data_editor(
        df_input,
        hide_index=True,
        column_config={
            "Periodo": st.column_config.NumberColumn(format="%d"),
            "Ingresos ($)": st.column_config.NumberColumn(format="$ %.2f"),
            "Egresos ($)": st.column_config.NumberColumn(format="$ %.2f"),
        },
        num_rows="fixed"
    )

# --- CÁLCULOS FINANCIEROS ---
# 1. Calcular Flujo Neto por periodo operativo
edited_df["Flujo Neto ($)"] = edited_df["Ingresos ($)"] - edited_df["Egresos ($)"]

# 2. Construir el arreglo completo de flujos (Incluyendo la inversión en t=0 en negativo)
flujos_completo = [-inversion_inicial] + edited_df["Flujo Neto ($)"].tolist()

# 3. Calcular VAN (NPV)
van = npf.net_present_value(tasa_descuento / 100, flujos_completo)

# 4. Calcular TIR (IRR)
# Nota: La TIR puede no tener solución matemática en ciertos flujos atípicos
try:
    tir = npf.irr(flujos_completo) * 100
    tir_display = f"{tir:.2f}%"
except:
    tir = None
    tir_display = "No calc."

# --- VISUALIZACIÓN DE RESULTADOS (KPIs) ---
with col2:
    st.subheader("📈 Resultados de Rentabilidad")
    
    kpi1, kpi2, kpi3 = st.columns(3)
    
    # Colores condicionales para los indicadores
    color_van = "green" if van > 0 else "red"
    color_tir = "green" if (tir is not None and tir > tasa_descuento) else "red"

    kpi1.metric(label="Inversión Inicial", value=f"$ {inversion_inicial:,.2f}")
    kpi2.metric(label="VAN (Valor Actual Neto)", value=f"$ {van:,.2f}", delta_color="normal" if van > 0 else "inverse")
    kpi3.metric(label="TIR (Tasa Interna de Retorno)", value=tir_display)

    st.divider()

    # --- GRÁFICOS PROFESIONALES CON PLOTLY ---
    
    # Gráfico Combinado: Barras (Ingresos/Egresos) y Línea (Flujo Neto)
    fig = go.Figure()

    # Barras de Ingresos
    fig.add_trace(go.Bar(
        x=edited_df["Periodo"],
        y=edited_df["Ingresos ($)"],
        name='Ingresos',
        marker_color='#27AE60'  # Verde profesional
    ))

    # Barras de Egresos
    fig.add_trace(go.Bar(
        x=edited_df["Periodo"],
        y=edited_df["Egresos ($)"],
        name='Egresos',
        marker_color='#C0392B'  # Rojo profesional
    ))

    # Línea de Flujo Neto
    fig.add_trace(go.Scatter(
        x=edited_df["Periodo"],
        y=edited_df["Flujo Neto ($)"],
        name='Flujo Neto',
        line=dict(color='#2C3E50', width=4, dash='dot'), # Azul oscuro
        mode='lines+markers'
    ))

    fig.update_layout(
        title='Análisis de Flujos de Caja por Periodo',
        xaxis_title='Periodo (Tiempo)',
        yaxis_title='Monto ($)',
        barmode='group',
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

# --- TABLA RESUMEN ---
st.divider()
with st.expander("Ver detalle de flujos completos"):
    st.dataframe(edited_df.style.format({
        "Ingresos ($)": "${:,.2f}",
        "Egresos ($)": "${:,.2f}",
        "Flujo Neto ($)": "${:,.2f}"
    }), use_container_width=True)
