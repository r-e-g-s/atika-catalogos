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
    page_icon="📄",
    layout="wide"
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

    nombre_pdf = f"{producto['SKU']}.pdf"

    c = canvas.Canvas(
        nombre_pdf,
        pagesize=A4
    )

    ancho, alto = A4

    # titulo

    c.setFont(
        "Helvetica-Bold",
        22
    )

    c.drawString(
        40,
        alto - 50,
        "ATIKA"
    )

    c.setFont(
        "Helvetica-Bold",
        18
    )

    c.drawString(
        40,
        alto - 90,
        producto["Nombre"]
    )

    c.setFont(
        "Helvetica",
        11
    )

    c.drawString(
        40,
        alto - 120,
        f"SKU: {producto['SKU']}"
    )

    c.drawString(
        40,
        alto - 140,
        f"Marca: {producto['Marca']}"
    )

    c.drawString(
        40,
        alto - 160,
        f"Categoria: {producto['Categoria']}"
    )

    try:

        respuesta = requests.get(
            producto["Imagen"],
            timeout=20
        )

        imagen = Image.open(
            BytesIO(
                respuesta.content
            )
        )

        c.drawImage(
            ImageReader(imagen),
            40,
            250,
            width=500,
            height=300
        )

    except:

        c.drawString(
            40,
            500,
            "Error cargando imagen"
        )

    c.setFont(
        "Helvetica-Bold",
        12
    )

    c.drawString(
        40,
        220,
        "DESCRIPCION"
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

    return nombre_pdf

# ==================================================
# CABECERA
# ==================================================

st.title("ATIKA | Generador de Catálogos")

st.write(
    "Seleccione uno o más productos para generar PDFs."
)

# ==================================================
# MULTISELECT
# ==================================================

seleccionados = st.multiselect(
    "Productos disponibles",
    df["Nombre"]
)

# ==================================================
# BOTON
# ==================================================

if st.button("Generar PDFs"):

    if len(seleccionados) == 0:

        st.warning(
            "Seleccione al menos un producto."
        )

    else:

        generados = []

        for producto_nombre in seleccionados:

            producto = df[
                df["Nombre"] == producto_nombre
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
        ) as f:

            st.download_button(
                "📥 Descargar ZIP",
                f,
                file_name=zip_name,
                mime="application/zip"
            )

        st.success(
            f"Se generaron {len(generados)} PDF(s)."
        )

# ==================================================
# GALERIA PRODUCTOS
# ==================================================

st.divider()

st.subheader(
    "Productos disponibles"
)

cols = st.columns(4)

for i, (_, row) in enumerate(df.iterrows()):

    with cols[i % 4\]:

        st.image(
            row["Imagen"],
            use_container_width=True
        )

        st.markdown(
            f"**{row['Nombre']}**"
        )

        st.caption(
            row["Categoria"]
        )

        st.write(
            row["Descripcion"]
        )
