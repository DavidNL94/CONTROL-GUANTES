import streamlit as st
import pandas as pd
from datetime import datetime
import os

ARCHIVO = "registros_guantes.csv"

st.set_page_config(
    page_title="Control de Guantes - PROCONGELADOS",
    layout="wide"
)

st.title("🧤 Sistema Control de Guantes - PROCONGELADOS")

COLUMNAS = [
    "Empleado", "Cargo", "Fecha",
    "Hora", "Observación",
    "Entregó", "Motivo"
]

# ================= CARGAR DATOS =================

def cargar_datos():
    if os.path.exists(ARCHIVO):
        try:
            df = pd.read_csv(ARCHIVO, engine="python")
            for col in COLUMNAS:
                if col not in df.columns:
                    df[col] = ""
            return df[COLUMNAS]
        except:
            return pd.DataFrame(columns=COLUMNAS)
    else:
        return pd.DataFrame(columns=COLUMNAS)

df = cargar_datos()

# ================= SESSION EMPLEADOS =================

if "empleados" not in st.session_state:
    st.session_state.empleados = pd.DataFrame(columns=["Nombre", "Cargo"])

if "mensaje_exito" not in st.session_state:
    st.session_state.mensaje_exito = False

# ================= CREAR PESTAÑAS FIJAS =================

tab1, tab2, tab3, tab4 = st.tabs(
    ["Nueva Solicitud", "Cargar Empleados", "Reportes", "Historial"]
)

# =====================================================
# ================= NUEVA SOLICITUD ===================
# =====================================================

with tab1:

    st.subheader("Registrar Nueva Solicitud")

    if st.session_state.mensaje_exito:
        st.success("✅ Nueva solicitud registrada con éxito")
        st.session_state.mensaje_exito = False

    if len(st.session_state.empleados) == 0:
        st.warning("Primero debe cargar empleados desde Excel")
    else:

        lista_empleados = st.session_state.empleados["Nombre"].tolist()

        empleado = st.selectbox("Empleado", lista_empleados)

        cargo = st.session_state.empleados[
            st.session_state.empleados["Nombre"] == empleado
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

                df_nuevo = pd.concat(
                    [df, pd.DataFrame([nueva_fila])],
                    ignore_index=True
                )

                df_nuevo.to_csv(ARCHIVO, index=False)

                st.session_state.mensaje_exito = True
                st.rerun()

# =====================================================
# ================= CARGAR EMPLEADOS ==================
# =====================================================

with tab2:

    st.subheader("📂 Cargar Empleados desde Excel")

    archivo_excel = st.file_uploader(
        "Seleccione archivo Excel (.xlsx)",
        type=["xlsx"]
    )

    if archivo_excel is not None:
        try:
            df_empleados = pd.read_excel(archivo_excel)

            if "Nombre" not in df_empleados.columns or "Cargo" not in df_empleados.columns:
                st.error("El archivo debe tener columnas: Nombre y Cargo")
            else:
                st.session_state.empleados = df_empleados[["Nombre", "Cargo"]]
                st.success("Empleados cargados correctamente")
                st.dataframe(st.session_state.empleados)

        except:
            st.error("Error al leer el archivo Excel")

# =====================================================
# ================= REPORTES ==========================
# =====================================================

with tab3:

    st.subheader("📊 Reportes por Rango de Fecha")

    if len(df) == 0:
        st.warning("No hay registros")
    else:
        col1, col2 = st.columns(2)

        with col1:
            desde = st.date_input("Desde", datetime.now())

        with col2:
            hasta = st.date_input("Hasta", datetime.now())

        if st.button("Generar Reporte"):

            df["Fecha_dt"] = pd.to_datetime(
                df["Fecha"],
                format="%d/%m/%Y",
                errors="coerce"
            )

            filtro = df[
                (df["Fecha_dt"] >= pd.to_datetime(desde)) &
                (df["Fecha_dt"] <= pd.to_datetime(hasta))
            ]

            resumen = (
                filtro
                .groupby("Empleado")
                .size()
                .reset_index(name="Cantidad Cambios")
            )

            st.write("### Total cambios en rango:", len(filtro))
            st.dataframe(resumen, use_container_width=True)

# =====================================================
# ================= HISTORIAL =========================
# =====================================================

with tab4:

    st.subheader("📋 Historial Completo")

    if len(df) == 0:
        st.info("No hay registros aún")
    else:
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Descargar Historial CSV",
            data=csv,
            file_name="historial_guantes.csv",
            mime="text/csv"
        )