import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ================= ARCHIVOS =================

ARCHIVO_REGISTROS = "registros_guantes.csv"
ARCHIVO_EMPLEADOS = "empleados.csv"

# ================= CONFIG =================

st.set_page_config(
    page_title="Control de Guantes - PROCONGELADOS",
    layout="wide"
)

st.title("🧤 Sistema Control de Guantes - PROCONGELADOS")

COLUMNAS_REGISTROS = [
    "Empleado", "Cargo", "Fecha",
    "Hora", "Observación",
    "Entregó", "Motivo"
]

# ================= FUNCIONES =================

def cargar_registros():
    if os.path.exists(ARCHIVO_REGISTROS):
        try:
            df = pd.read_csv(ARCHIVO_REGISTROS, engine="python")
            for col in COLUMNAS_REGISTROS:
                if col not in df.columns:
                    df[col] = ""
            return df[COLUMNAS_REGISTROS]
        except:
            return pd.DataFrame(columns=COLUMNAS_REGISTROS)
    else:
        return pd.DataFrame(columns=COLUMNAS_REGISTROS)


def cargar_empleados():
    if os.path.exists(ARCHIVO_EMPLEADOS):
        return pd.read_csv(ARCHIVO_EMPLEADOS)
    else:
        return pd.DataFrame(columns=["Nombre", "Cargo"])


def guardar_empleados(df_emp):
    df_emp.to_csv(ARCHIVO_EMPLEADOS, index=False)


def guardar_registros(df_reg):
    df_reg.to_csv(ARCHIVO_REGISTROS, index=False)


# ================= CARGA INICIAL =================

df_registros = cargar_registros()
df_empleados = cargar_empleados()

if "mensaje_exito" not in st.session_state:
    st.session_state.mensaje_exito = False

# ================= PESTAÑAS =================

tab1, tab2, tab3, tab4 = st.tabs(
    ["Nueva Solicitud", "Cargar Empleados", "Reportes", "Historial"]
)

# =========================================================
# ================= NUEVA SOLICITUD =======================
# =========================================================

with tab1:

    st.subheader("Registrar Nueva Solicitud")

    if st.session_state.mensaje_exito:
        st.success("✅ Nueva solicitud registrada con éxito")
        st.session_state.mensaje_exito = False

    if len(df_empleados) == 0:
        st.warning("Debe cargar empleados primero")
    else:

        lista_empleados = df_empleados["Nombre"].tolist()

        empleado = st.selectbox("Empleado", lista_empleados)

        cargo = df_empleados[
            df_empleados["Nombre"] == empleado
        ]["Cargo"].values[0]

        fecha = st.date_input("Fecha", datetime.now())
        observacion = st.text_input("Observación")

        entrego = st.selectbox(
            "¿Entregó guantes anteriores?",
            ["Sí", "No"]
        )

        motivo = ""
        if entrego == "No":
            motivo = st.text_input("⚠ Motivo de no entrega (obligatorio)")

        if st.button("Registrar Solicitud"):

            if not observacion:
                st.warning("Debe colocar la observación")

            elif entrego == "No" and not motivo:
                st.warning("Debe escribir el motivo de no entrega")

            else:
                nueva_fila = {
                    "Empleado": empleado,
                    "Cargo": cargo,
                    "Fecha": fecha.strftime("%d/%m/%Y"),
                    "Hora": datetime.now().strftime("%H:%M:%S"),
                    "Observación": observacion,
                    "Entregó": entrego,
                    "Motivo": motivo
                }

                df_registros = pd.concat(
                    [df_registros, pd.DataFrame([nueva_fila])],
                    ignore_index=True
                )

                guardar_registros(df_registros)

                st.session_state.mensaje_exito = True
                st.rerun()

# =========================================================
# ================= CARGAR EMPLEADOS ======================
# =========================================================

with tab2:

    st.subheader("📂 Cargar Empleados desde Excel")

    archivo_excel = st.file_uploader(
        "Seleccione archivo Excel (.xlsx)",
        type=["xlsx"]
    )

    if archivo_excel is not None:
        try:
            df_excel = pd.read_excel(archivo_excel, engine="openpyxl")
            df_excel.columns = df_excel.columns.str.strip()

            if "Nombre" not in df_excel.columns or "Cargo" not in df_excel.columns:
                st.error("El archivo debe tener columnas: Nombre y Cargo")
            else:
                df_empleados = df_excel[["Nombre", "Cargo"]]
                guardar_empleados(df_empleados)
                st.success("Empleados guardados permanentemente")
                st.dataframe(df_empleados)

        except:
            st.error("Error al leer el archivo Excel")

    if len(df_empleados) > 0:
        st.markdown("### Empleados actuales")
        st.dataframe(df_empleados)

# =========================================================
# ================= REPORTES ==============================
# =========================================================

with tab3:

    st.subheader("📊 Reportes por Rango de Fecha")

    if len(df_registros) == 0:
        st.warning("No hay registros")
    else:

        col1, col2 = st.columns(2)

        with col1:
            desde = st.date_input("Desde", datetime.now())

        with col2:
            hasta = st.date_input("Hasta", datetime.now())

        if st.button("Generar Reporte"):

            df_registros["Fecha_dt"] = pd.to_datetime(
                df_registros["Fecha"],
                format="%d/%m/%Y",
                errors="coerce"
            )

            filtro = df_registros[
                (df_registros["Fecha_dt"] >= pd.to_datetime(desde)) &
                (df_registros["Fecha_dt"] <= pd.to_datetime(hasta))
            ]

            resumen = (
                filtro
                .groupby("Empleado")
                .size()
                .reset_index(name="Cantidad Cambios")
            )

            st.write("### Total cambios en rango:", len(filtro))
            st.dataframe(resumen, use_container_width=True)

# =========================================================
# ================= HISTORIAL =============================
# =========================================================

with tab4:

    st.subheader("📋 Historial Completo")

    if len(df_registros) == 0:
        st.info("No hay registros aún")
    else:
        st.dataframe(df_registros, use_container_width=True)

        csv = df_registros.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Descargar Historial CSV",
            data=csv,
            file_name="historial_guantes.csv",
            mime="text/csv"
        )
