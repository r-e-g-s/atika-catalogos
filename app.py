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
from reportlab.lib.colors import HexColor

# ==================================================
# CONFIG
# ==================================================

st.set_page_config(
    page_title="ATIKA Catálogos",
    page_icon="🏠",
    layout="wide"
)

# ==================================================
# ESTILO
# ==================================================

st.markdown("""
<style>

.stButton > button {
    background-color:#d71920;
    color:white;
    border-radius:8px;
    border:none;
    font-weight:bold;
}

h1 {
    color:#222222;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# LOGO
# ==================================================

if os.path.exists("logo_atika.png"):
    st.image(
        "logo_atika.png",
        width=320
    )

st.title("Catálogos Comerciales")

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
        "Descripcion": "Panel WPC decorativo para muros y cielos con apariencia tipo madera natural.",
        "Material": "WPC",
        "Color": "Walnut",
        "Formato": "2900 x 160 mm",
        "Uso": "Muros y cielos",
        "Imagen": "https://atika.vtexassets.com/arquivos/ids/169616-800-800"
    },

    {
        "SKU": "PORC-001",
        "Nombre": "Porcelanato Eras Ivory Mate",
        "Marca": "ATIKA",
        "Categoria": "Porcelanato",
        "Descripcion": "Porcelanato rectificado acabado mate para uso residencial y comercial.",
        "Material": "Porcelanato",
        "Color": "Ivory",
        "Formato": "60 x 120 cm",
        "Uso": "Piso y muro",
        "Imagen": "https://picsum.photos/900/900?1"
    },

    {
        "SKU": "SPC-001",
        "Nombre": "Piso SPC Aston Oak",
        "Marca": "ATIKA",
        "Categoria": "SPC",
        "Descripcion": "Piso SPC resistente al agua ideal para espacios interiores.",
        "Material": "SPC",
        "Color": "Oak",
        "Formato": "1220 x 180 mm",
        "Uso": "Interior",
        "Imagen": "https://picsum.photos/900/900?2"
    },

    {
        "SKU": "GRIF-001",
        "Nombre": "Grifería Negra Mate",
        "Marca": "ATIKA",
        "Categoria": "Grifería",
        "Descripcion": "Grifería premium con acabado negro mate de diseño contemporáneo.",
        "Material": "Latón",
        "Color": "Negro",
        "Formato": "-",
        "Uso": "Baño",
        "Imagen": "https://picsum.photos/900/900?3"
    }

]

df = pd.DataFrame(productos)

# ==================================================
# PDF PREMIUM
# ==================================================

def crear_pdf(producto):

    archivo_pdf = f"{producto['SKU']}.pdf"

    c = canvas.Canvas(
        archivo_pdf,
        pagesize=A4
    )

    ancho, alto = A4

    ROJO = HexColor("#D71920")
    GRIS = HexColor("#777777")
    FONDO = HexColor("#F4F4F4")

    # -------------------------
    # FONDO
    # -------------------------

    c.setFillColorRGB(1, 1, 1)

    c.rect(
        0,
        0,
        ancho,
        alto,
        fill=1,
        stroke=0
    )

    # -------------------------
    # FRANJA ROJA
    # -------------------------

    c.setFillColor(ROJO)

    c.rect(
        0,
        alto - 10,
        ancho,
        10,
        fill=1,
        stroke=0
    )

    # -------------------------
    # LOGO
    # -------------------------

    if os.path.exists("logo_atika.png"):

        c.drawImage(
            "logo_atika.png",
            40,
            alto - 95,
            width=180,
            height=55,
            preserveAspectRatio=True,
            mask='auto'
        )

    # -------------------------
    # TITULO
    # -------------------------

    c.setFillColor(HexColor("#222222"))

    c.setFont(
        "Helvetica-Bold",
        22
    )

    c.drawString(
        40,
        alto - 130,
        producto["Nombre"]
    )

    c.setFont(
        "Helvetica",
        12
    )

    c.setFillColor(GRIS)

    c.drawString(
        40,
        alto - 150,
        producto["Categoria"]
    )

    # -------------------------
    # FOTO PRINCIPAL
    # -------------------------

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
            300,
            width=520,
            height=300
        )

    except:

        c.drawString(
            40,
            450,
            "Imagen no disponible"
        )

    # -------------------------
    # DESCRIPCION
    # -------------------------

    c.setFillColor(HexColor("#222222"))

    c.setFont(
        "Helvetica-Bold",
        13
    )

    c.drawString(
        40,
        270,
        "DESCRIPCIÓN"
    )

    c.setFont(
        "Helvetica",
        10
    )

    c.drawString(
        40,
        250,
        producto["Descripcion"]
    )

    # -------------------------
    # ESPECIFICACIONES
    # -------------------------

    c.setFillColor(FONDO)

    c.roundRect(
        40,
        70,
        520,
        140,
        8,
        fill=1,
        stroke=0
    )

    c.setFillColor(HexColor("#222222"))

    c.setFont(
        "Helvetica-Bold",
        13
    )

    c.drawString(
        55,
        185,
        "ESPECIFICACIONES"
    )

    datos = [

        ("SKU", producto["SKU"]),
        ("Marca", producto["Marca"]),
        ("Material", producto["Material"]),
        ("Color", producto["Color"]),
        ("Formato", producto["Formato"]),
        ("Uso", producto["Uso"])

    ]

    y = 160

    c.setFont(
        "Helvetica",
        10
    )

    for nombre, valor in datos:

        c.drawString(
            60,
            y,
            f"{nombre}:"
        )

        c.drawString(
            180,
            y,
            str(valor)
        )

        y -= 20

    # -------------------------
    # FOOTER
    # -------------------------

    c.setFillColor(ROJO)

    c.rect(
        0,
        0,
        ancho,
        20,
        fill=1,
        stroke=0
    )

    c.save()

    return archivo_pdf

# ==================================================
# SELECCION
# ==================================================

seleccionados = st.multiselect(
    "Seleccione productos",
    df["Nombre"]
)

if st.button("Generar Catálogos PDF"):

    if len(seleccionados) == 0:

        st.warning(
            "Seleccione al menos un producto."
        )

    else:

        pdfs = []

        for nombre in seleccionados:

            producto = df[
                df["Nombre"] == nombre
            ].iloc[0]

            archivo = crear_pdf(
                producto
            )

            pdfs.append(
                archivo
            )

        zip_name = "Catalogos_ATIKA.zip"

        with zipfile.ZipFile(
            zip_name,
            "w"
        ) as z:

            for pdf in pdfs:

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
                data=f,
                file_name=zip_name,
                mime="application/zip"
            )

# ==================================================
# GALERIA
# ==================================================

st.divider()

st.subheader("Productos Disponibles")

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
