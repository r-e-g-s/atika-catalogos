import streamlit as st
import pandas as pd
import requests
import zipfile
import os

from io import BytesIO
from PIL import Image

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

# ==================================================
# CONFIG
# ==================================================

st.set_page_config(
    page_title="ATIKA Catálogos",
    page_icon="🏠",
    layout="wide"
)

# ==================================================
# ESTILOS
# ==================================================

st.markdown("""
<style>

.stButton > button {
    background-color: #d71920;
    color: white;
    border-radius: 8px;
    border: none;
    font-weight: bold;
}

.stButton > button:hover {
    background-color: #b31218;
    color: white;
}

.card {
    border-radius: 12px;
    background-color: white;
    padding: 10px;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.15);
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# LOGO
# ==================================================

if os.path.exists("logo_atika.png"):

    st.image(
        "logo_atika.png",
        width=300
    )

st.title("Generador de Catálogos")

st.write(
    "Seleccione uno o más productos para generar fichas PDF."
)

# ==================================================
# PRODUCTOS DEMO
# ==================================================

productos = [

    {
        "SKU": "WPC-16200-WALNUT",
        "Nombre": "Wall Panel 16200 Walnut",
        "Marca": "ATIKA",
        "Categoria": "Revestimiento Decorativo",
        "Descripcion": "Panel WPC decorativo para muros y cielos.",
        "Imagen": "https://atika.vtexassets.com/arquivos/ids/169616-800-800"
    },

    {
        "SKU": "PORC-001",
        "Nombre": "Porcelanato Eras Ivory Mate 60x120",
        "Marca": "ATIKA",
        "Categoria": "Porcelanato",
        "Descripcion": "Porcelanato rectificado acabado mate.",
        "Imagen": "https://picsum.photos/800/800?1"
    },

    {
        "SKU": "SPC-001",
        "Nombre": "Piso SPC Aston Oak",
        "Marca": "ATIKA",
        "Categoria": "SPC",
        "Descripcion": "Piso SPC resistente al agua.",
        "Imagen": "https://picsum.photos/800/800?2"
    },

    {
        "SKU": "GRIF-001",
        "Nombre": "Grifería Negra Mate",
        "Marca": "ATIKA",
        "Categoria": "Grifería",
        "Descripcion": "Grifería premium color negro mate.",
        "Imagen": "https://picsum.photos/800/800?3"
    }

]

df = pd.DataFrame(productos)

# ==================================================
# PDF
# ==================================================

def crear_pdf(producto):

    archivo_pdf = f"{producto['SKU']}.pdf"

    c = canvas.Canvas(
        archivo_pdf,
        pagesize=A4
    )

    ancho, alto = A4

    # Logo

    if os.path.exists("logo_atika.png"):

        c.drawImage(
            "logo_atika.png",
            40,
            alto - 100,
            width=180,
            height=60,
            preserveAspectRatio=True,
            mask='auto'
        )

    # Nombre producto

    c.setFont(
        "Helvetica-Bold",
        18
    )

    c.drawString(
        40,
        alto - 130,
        producto["Nombre"]
    )

    # Datos

    c.setFont(
        "Helvetica",
        11
    )

    c.drawString(
        40,
        alto - 160,
        f"SKU: {producto['SKU']}"
    )

    c.drawString(
        40,
        alto - 180,
        f"Marca: {producto['Marca']}"
    )

    c.drawString(
        40,
        alto - 200,
        f"Categoría: {producto['Categoria']}"
    )

    # Imagen

    try:

        r = requests.get(
            producto["Imagen"],
            timeout=20
        )

        img = Image.open(
            BytesIO(r.content)
        )

        c.drawImage(
            ImageReader(img),
            40,
            250,
            width=500,
            height=300
        )

    except:

        c.drawString(
            40,
            500,
            "No fue posible cargar la imagen"
        )

    # Descripción

    c.setFont(
        "Helvetica-Bold",
        12
    )

    c.drawString(
        40,
        220,
        "DESCRIPCIÓN"
    )

    c.setFont(
        "Helvetica",
        10
    )

    c.drawString(
        40,
        200,
        producto["Descripcion"]
    )

    c.save()

    return archivo_pdf

# ==================================================
# SELECTOR
# ==================================================

seleccionados = st.multiselect(
    "Seleccione productos",
    df["Nombre"]
)

# ==================================================
# BOTON
# ==================================================

if st.button("Generar Catálogos PDF"):

    if len(seleccionados) == 0:

        st.warning(
            "Seleccione al menos un producto."
        )

    else:

        generados = []

        for nombre in seleccionados:

            producto = df[
                df["Nombre"] == nombre
            ].iloc[0]

            pdf = crear_pdf(producto)

            generados.append(pdf)

        zip_name = "Catalogos_ATIKA.zip"

        with zipfile.ZipFile(
            zip_name,
            "w"
        ) as z:

            for pdf in generados:

                z.write(
                    pdf,
                    arcname=os.path.basename(pdf)
                )

        with open(
            zip_name,
            "rb"
        ) as archivo_zip:

            st.download_button(
                label="📥 Descargar ZIP",
                data=archivo_zip,
                file_name=zip_name,
                mime="application/zip"
            )

        st.success(
            f"Se generaron {len(generados)} PDF(s)."
        )

# ==================================================
# GALERIA
# ==================================================

st.divider()

st.subheader("Productos disponibles")

cols = st.columns(4)

for i, (_, row) in enumerate(df.iterrows()):

    with cols[i % 4]:

        st.image(
            row["Imagen"],
            use_container_width=True
        )

        st.markdown(
            f"### {row['Nombre']}"
        )

        st.caption(
            row["Categoria"]
        )

        st.write(
            row["Descripcion"]
        )

        st.markdown(
            f"**SKU:** {row['SKU']}"
        )
