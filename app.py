
import streamlit as st
from pathlib import Path
import zipfile
import pandas as pd

ruta = Path("data/productos.xlsx")

st.subheader("Diagnóstico Excel")

st.write("Existe:", ruta.exists())

if ruta.exists():
    st.write("Tamaño:", ruta.stat().st_size, "bytes")
    st.write("Es ZIP válido:", zipfile.is_zipfile(ruta))

    try:
        libro = pd.ExcelFile(ruta, engine="openpyxl")
        st.success("Excel leído correctamente")
        st.write("Hojas:", libro.sheet_names)
    except Exception as e:
        st.error(f"Error de lectura: {type(e).__name__}: {e}")
