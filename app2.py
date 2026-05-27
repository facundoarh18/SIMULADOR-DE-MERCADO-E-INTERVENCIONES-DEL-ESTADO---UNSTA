import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Configuración de la página
st.set_page_config(page_title="Simulador de mercado - Economía –", layout="wide")
st.title("📊 Simulador de mercado e intervenciones del estado")
st.caption("Economía – Ingeniería Informática - UNSTA")
st.subheader("""
Integrantes:
ANTÚNEZ RUIZ HUIDOBRO, Facundo
BRAHIN, Federico Tomás
GORDILLO TOLEDO, Rodrigo Gabriel
MATOS VILLALBA, Luis Humberto
""")

# --- FUNCIONES AUXILIARES DE CÁLCULO ---
def resolver_mercado(a, b, c, d, impuesto=0, tipo_impuesto="Ninguno", subsidio=0, cuota=None):
    # Modificaciones por impuestos o subsidios
    # Qd = a - b*P  => P = (a - Qd)/b
    # Qo = c + d*P  => P = (Qs - c)/d
    
    b_ef = b
    d_ef = d
    a_ef = a
    c_ef = c
    
    if tipo_impuesto == "Vendedores" and impuesto > 0:
        # Sube la curva de oferta (grágicamente sube el intercepto, o disminuye c)
        c_ef = c - d * impuesto
    elif tipo_impuesto == "Compradores" and impuesto > 0:
        # Baja la curva de demanda
        a_ef = a - b * impuesto
    elif subsidio > 0:
        # El subsidio actúa de forma inversa a un impuesto (asumimos impacto en oferta para modelar)
        c_ef = c + d * subsidio

    # Calcular equilibrio matemático base (sin restricciones de cuota)
    # a_ef - b_ef*P = c_ef + d_ef*P => P*(d_ef + b_ef) = a_ef - c_ef
    denom = (d_ef + b_ef)
    if denom == 0:
        return None
    
    P_eq = (a_ef - c_ef) / denom
    Q_eq = a_ef - b_ef * P_eq
    
    # Aplicar restricción de cuota si existe
    efecto_cuota = False
    P_consumidor = P_eq
    P_productor = P_eq
    
    if cuota is not None and cuota < Q_eq:
        efecto_cuota = True
        Q_eq = cuota
        # Despejar precios de las funciones originales
        P_consumidor = (a - Q_eq) / b
        P_productor = (Q_eq - c) / d
        P_eq = P_consumidor # El precio de mercado lo determina la demanda
        
    return {
        "P_eq": round(P_eq, 2),
        "Q_eq": round(Q_eq, 2),
        "P_c": round(P_consumidor, 2),
        "P_p": round(P_productor, 2),
        "cuota_activa": efecto_cuota,
        "a_ef": a_ef, "b_ef": b_ef, "c_ef": c_ef, "d_ef": d_ef
    }

# --- BARRA LATERAL: ENTRADA DE DATOS (MÓDULO 4) ---
st.sidebar.header("🛠️ Configuración de funciones")
opcion_entrada = st.sidebar.radio("Método de ingreso de datos:", ["Opción A: Forma algebraica", "Opción B: A partir de 2 puntos"])

a, b, c, d = 0.0, 0.0, 0.0, 0.0
datos_validos = False

if opcion_entrada == "Opción A: Forma algebraica":
    st.sidebar.markdown("**Demand:** $Q_d = a - bP$")
    a = st.sidebar.number_input("Intercepto demanda (a)", value=100.0, step=10.0)
    b = st.sidebar.number_input("Pendiente demanda (b)", value=2.0, step=0.5, min_value=0.01)
    
    st.sidebar.markdown("**Oferta:** $Q_o = c + dP$")
    c = st.sidebar.number_input("Intercepto oferta (c)", value=10.0, step=10.0)
    d = st.sidebar.number_input("Pendiente oferta (d)", value=1.0, step=0.5, min_value=0.01)
    datos_validos = True

else:
    st.sidebar.subheader("Puntos de demanda")
    p1_d = st.sidebar.number_input("P1 (Precio demanda)", value=20.0)
    q1_d = st.sidebar.number_input("Q1 (Cantidad demanda)", value=60.0)
    p2_d = st.sidebar.number_input("P2 (Precio demanda)", value=40.0)
    q2_d = st.sidebar.number_input("Q2 (Cantidad demanda)", value=20.0)
    
    st.sidebar.subheader("Puntos de oferta")
    p1_o = st.sidebar.number_input("P1 (Precio oferta)", value=20.0)
    q1_o = st.sidebar.number_input("Q1 (Cantidad oferta)", value=30.0)
    p2_o = st.sidebar.number_input("P2 (Precio oferta)", value=40.0)
    q2_o = st.sidebar.number_input("Q2 (Cantidad oferta)", value=50.0)
    
    # Calcular coeficientes analíticamente
    if (p2_d - p1_d) != 0 and (p2_o - p1_o) != 0:
        b = - (q2_d - q1_d) / (p2_d - p1_d)
        a = q1_d + b * p1_d
        
        d = (q2_o - q1_o) / (p2_o - p1_o)
        c = q1_o - d * p1_o
        
        if b > 0 and d > 0:
            datos_validos = True
            st.sidebar.success("Ecuaciones deducidas correctamente.")
        else:
            st.sidebar.error("Las pendientes calculadas no reflejan la ley de oferta y demanda.")
    else:
        st.sidebar.error("Los precios P1 y P2 deben ser diferentes.")

# --- TABS PRINCIPALES PARA MÓDULOS ---
if datos_validos:
    # Obtener equilibrio inicial base
    eq_base = resolver_mercado(a, b, c, d)
    
    tab1, tab2 = st.tabs(["📈 – Mercado competitivo y elasticidad", "🏛️ – Intervenciones del estado"])
    
    # ---------------------------------------------------------
    # TAB 1: MERCADO COMPETITIVO Y ELASTICIDAD (Módulo 1 y 2)
    # ---------------------------------------------------------
    with tab1:
        st.header("Módulo 1 y 2: Equilibrio y elasticidad del punto medio")
        
        col_par, col_graf = st.columns([1, 2])
        
        with col_par:
            st.metric("Precio de equilibrio (P*)", f"${eq_base['P_eq']}")
            st.metric("Cantidad de equilibrio (Q*)", f"{eq_base['Q_eq']} u.")
            
            st.markdown("---")
            st.subheader("🧮 Cálculo de elasticidad (Mankiw)")
            st.caption("Seleccionar 2 puntos de precio sobre la curva de demanda para medir su elasticidad:")
            
            p_A = st.slider("Precio punto A", min_value=1.0, max_value=float(a/b), value=float(eq_base['P_eq'] * 0.8))
            p_B = st.slider("Precio punto B", min_value=1.0, max_value=float(a/b), value=float(eq_base['P_eq'] * 1.2))
            
            q_A = a - b * p_A
            q_B = a - b * p_B
            
            if (q_A + q_B) > 0 and (p_A + p_B) > 0 and (p_A != p_B):
                # Fórmula del punto medio de Mankiw
                cambio_Q = (q_B - q_A) / ((q_A + q_B) / 2)
                cambio_P = (p_B - p_A) / ((p_A + p_B) / 2)
                elasticidad = abs(cambio_Q / cambio_P)
                
                st.metric("Elasticidad – Precio", f"{round(elasticidad, 2)}")
                
                # Clasificación
                if elasticidad > 1:
                    tipo_e = "ELÁSTICA 🟢"
                    ingreso_efecto = "Disminuye si sube el precio ('demanda sensible')."
                elif elasticidad < 1:
                    tipo_e = "INELÁSTICA 🔴"
                    ingreso_efecto = "Aumenta si sube el precio ('demanda poco sensible')."
                else:
                    tipo_e = "UNITARIA 🔵"
                    ingreso_efecto = "Se mantiene constante ante variaciones leves."
                    
                st.markdown(f"**Clasificación:** Demanda {tipo_e}")
                st.markdown(f"**Ingreso total:** {ingreso_efecto}")
            else:
                st.warning("Los precios deben ser distintos para computar la elasticidad.")

        with col_graf:
            # Graficar curvas base
            p_max_graf = float(a/b) if b > 0 else 100.0
            p_arr = np.linspace(0, p_max_graf, 100)
            qd_arr = np.clip(a - b * p_arr, 0, None)
            qo_arr = np.clip(c + d * p_arr, 0, None)
            
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(x=qd_arr, y=p_arr, mode='lines', name='Demanda', line=dict(color='blue', width=3)))
            fig1.add_trace(go.Scatter(x=qo_arr, y=p_arr, mode='lines', name='Oferta', line=dict(color='orange', width=3)))
            
            # Punto de equilibrio
            fig1.add_trace(go.Scatter(x=[eq_base['Q_eq']], y=[eq_base['P_eq']], mode='markers+text',
                                      name='Equilibrio', text=["E"], textposition="top right",
                                      marker=dict(color='red', size=12)))
            
            # Puntos A y B de elasticidad
            fig1.add_trace(go.Scatter(x=[q_A, q_B], y=[p_A, p_B], mode='markers', name='Puntos elasticidad',
                                      marker=dict(color='green', size=10, symbol='diamond')))
            
            fig1.update_layout(title="Mercado competitivo simple", xaxis_title="Cantidad (Q)", yaxis_title="Precio (P)",
                              xaxis=dict(range=[0, float(a * 1.1)]), yaxis=dict(range=[0, float(p_max_graf * 1.1)]))
            st.plotly_chart(fig1, use_container_width=True)

    # ---------------------------------------------------------
    # TAB 2: INTERVENCIONES DEL ESTADO (Módulo 3)
    # ---------------------------------------------------------
    with tab2:
        st.header("Módulo 3: Simulador de intervenciones gubernamentales")
        
        tipo_intervencion = st.selectbox("Seleccione el tipo de intervención:", 
                                         ["Ninguna", "Precio máximo", "Precio mínimo", "Impuestos", "Subsidios", "Cuotas de producción"])
        
        # Parámetros dinámicos según el tipo de intervención
        p_max_val = float(eq_base['P_eq'])
        p_min_val = float(eq_base['P_eq'])
        monto_impuesto = 0.0
        tipo_imp = "Ninguno"
        monto_subsidio = 0.0
        valor_cuota = float(eq_base['Q_eq'])
        
        if tipo_intervencion == "Precio máximo":
            p_max_val = st.slider("Establecer precio máximo:", min_value=1.0, max_value=float(eq_base['P_eq'] * 1.5), value=float(eq_base['P_eq'] * 0.75))
        elif tipo_intervencion == "Precio mínimo":
            p_min_val = st.slider("Establecer precio mínimo:", min_value=1.0, max_value=float(eq_base['P_eq'] * 1.5), value=float(eq_base['P_eq'] * 1.25))
        elif tipo_intervencion == "Impuestos":
            monto_impuesto = st.slider("Monto del impuesto por unidad ($):", min_value=0.0, max_value=float(eq_base['P_eq'] * 0.8), value=float(eq_base['P_eq'] * 0.2))
            tipo_imp = st.radio("Incidencia legal inicial sobre:", ["Vendedores", "Compradores"])
        elif tipo_intervencion == "Subsidios":
            monto_subsidio = st.slider("Monto del subsidio por unidad ($):", min_value=0.0, max_value=float(eq_base['P_eq'] * 0.5), value=float(eq_base['P_eq'] * 0.15))
        elif tipo_intervencion == "Cuotas de producción":
            valor_cuota = st.slider("Límite de cantidad máxima (cuota):", min_value=1.0, max_value=float(eq_base['Q_eq'] * 1.2), value=float(eq_base['Q_eq'] * 0.7))

        # Cómputo de la nueva situación económica
        eq_nuevo = resolver_mercado(a, b, c, d, impuesto=monto_impuesto, tipo_impuesto=tipo_imp, subsidio=monto_subsidio, cuota=valor_cuota if tipo_intervencion == "Cuotas de producción" else None)
        
        col_res, col_graf_int = st.columns([1, 2])
        
        with col_res:
            st.subheader("Panel de resultados")
            
            # Tabla interactiva requerida (Requerimiento de Interfaz - Sección 6)
            tabla_datos = [
                {"Variable": "Precio equilibrio inicial", "Valor": f"${eq_base['P_eq']}"},
                {"Variable": "Cantidad equilibrio inicial", "Valor": f"{eq_base['Q_eq']} u."}
            ]
            
            if tipo_intervencion == "Precio máximo":
                qd_int = a - b * p_max_val
                qo_int = c + d * p_max_val
                escasez = qd_int - qo_int
                
                tabla_datos.append({"Variable": "Precio máximo fijado", "Valor": f"${p_max_val}"})
                tabla_datos.append({"Variable": "Cantidad demandada", "Valor": f"{round(qd_int, 2)} u."})
                tabla_datos.append({"Variable": "Cantidad ofrecida", "Valor": f"{round(qo_int, 2)} u."})
                
                if p_max_val < eq_base['P_eq']:
                    tabla_datos.append({"Variable": "Situación de mercado", "Valor": f"🔴 ESCASEZ de {round(escasez, 2)} u."})
                else:
                    tabla_datos.append({"Variable": "Situación de mercado", "Valor": "No vinculante (Precio regulado arriba del equilibrio)"})
                    
            elif tipo_intervencion == "Precio mínimo":
                qd_int = a - b * p_min_val
                qo_int = c + d * p_min_val
                excedente = qo_int - qd_int
                
                tabla_datos.append({"Variable": "Precio mínimo fijado", "Valor": f"${p_min_val}"})
                tabla_datos.append({"Variable": "Cantidad demandada", "Valor": f"{round(qd_int, 2)} u."})
                tabla_datos.append({"Variable": "Cantidad ofrecida", "Valor": f"{round(qo_int, 2)} u."})
                
                if p_min_val > eq_base['P_eq']:
                    tabla_datos.append({"Variable": "Situación de mercado", "Valor": f"🔵 EXCEDENTE de {round(excedente, 2)} u."})
                else:
                    tabla_datos.append({"Variable": "Situación de mercado", "Valor": "No vinculante (Precio regulado abajo del equilibrio)"})
            
            elif tipo_intervencion == "Impuestos":
                recaudacion = monto_impuesto * eq_nuevo['Q_eq']
                inc_comprador = eq_nuevo['P_c'] - eq_base['P_eq']
                inc_vendedor = eq_base['P_eq'] - eq_nuevo['P_p']
                
                tabla_datos.append({"Variable": "Nuevo precio consumidor (Pc)", "Valor": f"${eq_nuevo['P_c']}"})
                tabla_datos.append({"Variable": "Nuevo precio productor (Pp)", "Valor": f"${eq_nuevo['P_p']}"})
                tabla_datos.append({"Variable": "Nueva cantidad mercado", "Valor": f"{eq_nuevo['Q_eq']} u."})
                tabla_datos.append({"Variable": "Recaudación fiscal total", "Valor": f"${round(recaudacion, 2)}"})
                tabla_datos.append({"Variable": "Incidencia al comprador/u.", "Valor": f"${round(inc_comprador, 2)}"})
                tabla_datos.append({"Variable": "Incidencia al vendedor/u.", "Valor": f"${round(inc_vendedor, 2)}"})
                
            elif tipo_intervencion == "Subsidios":
                tabla_datos.append({"Variable": "Nuevo precio de mercado", "Valor": f"${eq_nuevo['P_eq']}"})
                tabla_datos.append({"Variable": "Nueva cantidad de mercado", "Valor": f"{eq_nuevo['Q_eq']} u."})
                tabla_datos.append({"Variable": "Gasto estatal estimado", "Valor": f"${round(monto_subsidio * eq_nuevo['Q_eq'], 2)}"})
                
            elif tipo_intervencion == "Cuotas de Producción":
                tabla_datos.append({"Variable": "Límite establecido", "Valor": f"{valor_cuota} u."})
                tabla_datos.append({"Variable": "Precio que paga el consumidor", "Valor": f"${eq_nuevo['P_c']}"})
                tabla_datos.append({"Variable": "Precio que recibe el productor", "Valor": f"${eq_nuevo['P_p']}"})
                if eq_nuevo['cuota_activa']:
                    tabla_datos.append({"Variable": "Efecto cuota", "Valor": "⚠️ Activa (Contrae el mercado e infla el precio)"})
                else:
                    tabla_datos.append({"Variable": "Efecto cuota", "Valor": "Inactiva (Límite superior al equilibrio)"})
                    
            st.table(tabla_datos)

        with col_graf_int:
            # Gráfico dinámico interactivo de intervenciones
            p_max_g = float(a/b) if b > 0 else 100.0
            p_arr = np.linspace(0, p_max_g, 100)
            
            fig2 = go.Figure()
            # Curvas base invariantes
            fig2.add_trace(go.Scatter(x=np.clip(a - b*p_arr, 0, None), y=p_arr, mode='lines', name='Demanda base', line=dict(color='blue', dash='solid')))
            fig2.add_trace(go.Scatter(x=np.clip(c + d*p_arr, 0, None), y=p_arr, mode='lines', name='Oferta base', line=dict(color='orange', dash='solid')))
            
            if tipo_intervencion == "Precio máximo":
                fig2.add_hline(y=p_max_val, line_dash="dash", line_color="red", annotation_text="Precio máximo")
                if p_max_val < eq_base['P_eq']:
                    qd_pt = a - b * p_max_val
                    qo_pt = c + d * p_max_val
                    fig2.add_trace(go.Scatter(x=[qo_pt, qd_pt], y=[p_max_val, p_max_val], mode='markers+lines', name='Brecha de escasez', line=dict(color='red', width=4)))
                    
            elif tipo_intervencion == "Precio mínimo":
                fig2.add_hline(y=p_min_val, line_dash="dash", line_color="purple", annotation_text="Precio mínimo")
                if p_min_val > eq_base['P_eq']:
                    qd_pt = a - b * p_min_val
                    qo_pt = c + d * p_min_val
                    fig2.add_trace(go.Scatter(x=[qd_pt, qo_pt], y=[p_min_val, p_min_val], mode='markers+lines', name='Brecha de excedente', line=dict(color='purple', width=4)))
            
            elif tipo_intervencion == "Impuestos":
                # Graficar desplazamiento visual según incidencia legal
                if tipo_imp == "Vendedores":
                    qd_new = np.clip(eq_nuevo['a_ef'] - eq_nuevo['b_ef']*p_arr, 0, None)
                    qo_new = np.clip(eq_nuevo['c_ef'] + eq_nuevo['d_ef']*p_arr, 0, None)
                    fig2.add_trace(go.Scatter(x=qo_new, y=p_arr, mode='lines', name='Oferta con impuesto', line=dict(color='darkorange', dash='dot')))
                else:
                    qd_new = np.clip(eq_nuevo['a_ef'] - eq_nuevo['b_ef']*p_arr, 0, None)
                    fig2.add_trace(go.Scatter(x=qd_new, y=p_arr, mode='lines', name='Demanda con impuesto', line=dict(color='darkblue', dash='dot')))
                
                # Sombreado de recaudación impositiva
                fig2.add_trace(go.Scatter(x=[0, eq_nuevo['Q_eq'], eq_nuevo['Q_eq'], 0], y=[eq_nuevo['P_p'], eq_nuevo['P_p'], eq_nuevo['P_c'], eq_nuevo['P_c']],
                                          fill="toself", name="Recaudación fiscal", fillcolor="rgba(0,128,0,0.20)", mode='none'))
                
            elif tipo_intervencion == "Subsidios":
                qo_new = np.clip(eq_nuevo['c_ef'] + eq_nuevo['d_ef']*p_arr, 0, None)
                fig2.add_trace(go.Scatter(x=qo_new, y=p_arr, mode='lines', name='Oferta subsidiada', line=dict(color='green', dash='dot')))
                
            elif tipo_intervencion == "Cuotas de production" and eq_nuevo['cuota_activa']:
                fig2.add_vline(x=valor_cuota, line_dash="dash", line_color="black", annotation_text="Cuota máxima")
                fig2.add_trace(go.Scatter(x=[valor_cuota, valor_cuota], y=[eq_nuevo['P_p'], eq_nuevo['P_c']], mode='markers+lines', name='Renta de la cuota', line=dict(color='black', width=3)))

            fig2.update_layout(title=f"Visualización de efectos: {tipo_intervencion}", xaxis_title="Cantidad", yaxis_title="Precio",
                              xaxis=dict(range=[0, float(a * 1.1)]), yaxis=dict(range=[0, float(p_max_g * 1.1)]))
            st.plotly_chart(fig2, use_container_width=True)

# --- CÓMO EJECUTAR EL SIMULADOR ---
# Guarda este código en un archivo llamado `app.py`
# Ejecuta en tu terminal el comando: `streamlit run app.py`
