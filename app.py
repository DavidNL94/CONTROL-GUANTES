import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ================= CONFIG =================

ARCHIVO_REGISTROS = "registros_guantes.csv"
ARCHIVO_EMPLEADOS = "empleados.csv"

# 🔐 TU CODIGO MAESTRO (CAMBIALO)
CODIGO_MAESTRO = "ADMIN123"

st.set_page_config(
    page_title="Control de Guantes - PROCONGELADOS",
    layout="wide"
)

st.title("🧤 Sistema Control de Guantes - PROCONGELADOS")

# ================= FUNCIONES =================

def cargar_registros():
    if os.path.exists(ARCHIVO_REGISTROS):
        return pd.read_csv(ARCHIVO_REGISTROS)
    return pd.DataFrame(columns=[
        "Empleado","Cargo","Fecha","Hora",
        "Observación","Entregó","Motivo","Entregado Por"
    ])

def cargar_empleados():
    if os.path.exists(ARCHIVO_EMPLEADOS):
        return pd.read_csv(ARCHIVO_EMPLEADOS)
    return pd.DataFrame(columns=[
        "Nombre","Cargo","Codigo","PuedeEntregar"
    ])

def guardar_empleados(df):
    df.to_csv(ARCHIVO_EMPLEADOS, index=False)

def guardar_registros(df):
    df.to_csv(ARCHIVO_REGISTROS, index=False)

df_registros = cargar_registros()
df_empleados = cargar_empleados()

if "admin" not in st.session_state:
    st.session_state.admin = False

# ================= ACCESO MAESTRO =================

with st.sidebar:
    st.markdown("### 🔐 Acceso Maestro")
    codigo = st.text_input("Código Maestro", type="password")

    if codigo == CODIGO_MAESTRO:
        st.session_state.admin = True
        st.success("Modo administrador activado")

# ================= PESTAÑAS =================

tabs = ["Nueva Solicitud","Reportes","Historial"]

if st.session_state.admin:
    tabs.append("Administración")

tab_objects = st.tabs(tabs)

# =========================================================
# ================= NUEVA SOLICITUD =======================
# =========================================================

with tab_objects[0]:

    if len(df_empleados) == 0:
        st.warning("No hay empleados cargados")
    else:

        empleado = st.selectbox("Empleado que solicita", df_empleados["Nombre"])

        cargo = df_empleados[df_empleados["Nombre"]==empleado]["Cargo"].values[0]

        fecha = st.date_input("Fecha", datetime.now())
        observacion = st.text_input("Observación")

        entrego = st.selectbox("¿Entregó guantes anteriores?",["Sí","No"])

        motivo=""
        if entrego=="No":
            motivo=st.text_input("Motivo obligatorio")

        # SOLO LOS AUTORIZADOS
        entregadores = df_empleados[df_empleados["PuedeEntregar"]==True]["Nombre"]

        entregado_por = st.selectbox("Entrega", entregadores)

        codigo_operador = st.text_input("Código del operador", type="password")

        if st.button("Registrar"):

            codigo_real = df_empleados[
                df_empleados["Nombre"]==entregado_por
            ]["Codigo"].values[0]

            if codigo_operador != str(codigo_real):
                st.error("Código incorrecto")
            else:
                nueva = {
                    "Empleado":empleado,
                    "Cargo":cargo,
                    "Fecha":fecha.strftime("%d/%m/%Y"),
                    "Hora":datetime.now().strftime("%H:%M:%S"),
                    "Observación":observacion,
                    "Entregó":entrego,
                    "Motivo":motivo,
                    "Entregado Por":entregado_por
                }

                df_registros = pd.concat([df_registros,pd.DataFrame([nueva])])
                guardar_registros(df_registros)

                st.success("Solicitud registrada correctamente")
                st.rerun()

# =========================================================
# ================= REPORTES ==============================
# =========================================================

with tab_objects[1]:

    st.dataframe(df_registros)

# =========================================================
# ================= HISTORIAL =============================
# =========================================================

with tab_objects[2]:

    st.dataframe(df_registros)

# =========================================================
# ================= ADMINISTRACIÓN ========================
# =========================================================

if st.session_state.admin:

    with tab_objects[3]:

        st.subheader("Panel de Administración")

        st.dataframe(df_empleados)

        st.markdown("### Modificar empleado")

        empleado_sel = st.selectbox("Empleado", df_empleados["Nombre"])

        nuevo_codigo = st.text_input("Nuevo Código")
        puede_entregar = st.checkbox("Puede Entregar Guantes")

        if st.button("Guardar Cambios"):

            df_empleados.loc[
                df_empleados["Nombre"]==empleado_sel,"Codigo"
            ] = nuevo_codigo

            df_empleados.loc[
                df_empleados["Nombre"]==empleado_sel,"PuedeEntregar"
            ] = puede_entregar

            guardar_empleados(df_empleados)

            st.success("Empleado actualizado")
            st.rerun()
