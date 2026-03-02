import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import os

# ================= CONFIG =================

ARCHIVO_REGISTROS = "registros_guantes.csv"
ARCHIVO_EMPLEADOS = "empleados.csv"
CODIGO_MAESTRO = "ADMIN123"  # CAMBIA ESTO

ZONA_EC = pytz.timezone("America/Guayaquil")

st.set_page_config(
    page_title="Control de Guantes - PROCONGELADOS",
    layout="wide"
)

st.title("🧤 Sistema Control de Guantes - PROCONGELADOS")

# ================= FUNCIONES =================

def fecha_hora_ecuador():
    ahora = datetime.now(ZONA_EC)
    return ahora.strftime("%d/%m/%Y"), ahora.strftime("%H:%M:%S")


def cargar_empleados():
    if os.path.exists(ARCHIVO_EMPLEADOS):
        df = pd.read_csv(ARCHIVO_EMPLEADOS)

        if "Codigo" not in df.columns:
            df["Codigo"] = ""

        if "PuedeEntregar" not in df.columns:
            df["PuedeEntregar"] = False

        df["PuedeEntregar"] = df["PuedeEntregar"].fillna(False)

        return df

    return pd.DataFrame(columns=["Nombre","Cargo","Codigo","PuedeEntregar"])


def guardar_empleados(df):
    df.to_csv(ARCHIVO_EMPLEADOS, index=False)


def cargar_registros():
    if os.path.exists(ARCHIVO_REGISTROS):
        return pd.read_csv(ARCHIVO_REGISTROS)
    return pd.DataFrame(columns=[
        "Empleado","Cargo","Fecha","Hora",
        "Observación","Entregó","Motivo","Entregado Por"
    ])


def guardar_registros(df):
    df.to_csv(ARCHIVO_REGISTROS, index=False)


df_empleados = cargar_empleados()
df_registros = cargar_registros()

if "admin" not in st.session_state:
    st.session_state.admin = False

# ================= ACCESO MAESTRO =================

with st.sidebar:
    st.markdown("### 🔐 Acceso Maestro")
    codigo_admin = st.text_input("Código Maestro", type="password")

    if codigo_admin == CODIGO_MAESTRO:
        st.session_state.admin = True
        st.success("Modo administrador activado")

# ================= PESTAÑAS =================

tabs = ["Nueva Solicitud","Reportes","Historial"]

if st.session_state.admin:
    tabs.append("Administración")

tab_objs = st.tabs(tabs)

# =========================================================
# ================= NUEVA SOLICITUD =======================
# =========================================================

with tab_objs[0]:

    fecha_ec, hora_ec = fecha_hora_ecuador()

    st.info(f"Fecha Ecuador: {fecha_ec} | Hora Ecuador: {hora_ec}")

    if len(df_empleados) == 0:
        st.warning("Primero cargue empleados")
    else:

        empleado = st.selectbox("Empleado que solicita", df_empleados["Nombre"])

        cargo = df_empleados[
            df_empleados["Nombre"]==empleado
        ]["Cargo"].values[0]

        observacion = st.text_input("Observación")

        entrego = st.selectbox("¿Entregó guantes anteriores?",["Sí","No"])

        motivo=""
        if entrego=="No":
            motivo = st.text_input("Motivo obligatorio")

        autorizados = df_empleados[
            df_empleados["PuedeEntregar"]==True
        ]["Nombre"]

        entregado_por = st.selectbox("Operador que entrega", autorizados)

        codigo_operador = st.text_input("Código del operador", type="password")

        if st.button("Registrar Solicitud"):

            if entrego=="No" and not motivo:
                st.warning("Debe escribir motivo")
            elif not codigo_operador:
                st.warning("Debe ingresar código")
            else:
                codigo_real = df_empleados[
                    df_empleados["Nombre"]==entregado_por
                ]["Codigo"].values[0]

                if str(codigo_operador) != str(codigo_real):
                    st.error("Código incorrecto")
                else:
                    nueva = {
                        "Empleado":empleado,
                        "Cargo":cargo,
                        "Fecha":fecha_ec,
                        "Hora":hora_ec,
                        "Observación":observacion,
                        "Entregó":entrego,
                        "Motivo":motivo,
                        "Entregado Por":entregado_por
                    }

                    df_registros = pd.concat(
                        [df_registros,pd.DataFrame([nueva])],
                        ignore_index=True
                    )

                    guardar_registros(df_registros)

                    st.success("Solicitud registrada correctamente")
                    st.rerun()

# =========================================================
# ================= ADMINISTRACIÓN ========================
# =========================================================

if st.session_state.admin:

    with tab_objs[-1]:

        st.subheader("Panel Administración")

        archivo_excel = st.file_uploader("Cargar Excel Empleados (.xlsx)", type=["xlsx"])

        if archivo_excel is not None:
            df_excel = pd.read_excel(archivo_excel, engine="openpyxl")
            df_excel.columns = df_excel.columns.str.strip()

            if not all(col in df_excel.columns for col in ["Nombre","Cargo"]):
                st.error("El Excel debe tener: Nombre y Cargo")
            else:
                df_excel["Codigo"] = ""
                df_excel["PuedeEntregar"] = False
                guardar_empleados(df_excel)
                st.success("Empleados cargados correctamente")
                st.rerun()

        if len(df_empleados) > 0:

            empleado_sel = st.selectbox("Empleado", df_empleados["Nombre"])

            nuevo_codigo = st.text_input("Asignar Código Único")

            puede = st.checkbox("Puede entregar guantes")

            if st.button("Guardar Cambios"):

                df_empleados.loc[
                    df_empleados["Nombre"]==empleado_sel,"Codigo"
                ] = nuevo_codigo

                df_empleados.loc[
                    df_empleados["Nombre"]==empleado_sel,"PuedeEntregar"
                ] = puede

                guardar_empleados(df_empleados)

                st.success("Empleado actualizado")
                st.rerun()

# =========================================================
# ================= REPORTES ==============================
# =========================================================

with tab_objs[1]:
    st.dataframe(df_registros)

with tab_objs[2]:
    st.dataframe(df_registros)
