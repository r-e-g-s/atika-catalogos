
"""Generador dinámico de fichas técnicas ATIKA."""

from io import BytesIO
from pathlib import Path
import re

from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import unicodedata


# ==================================================
# CONFIGURACIÓN
# ==================================================

BASE = Path(__file__).resolve().parent

W, H = 960, 675

RED = HexColor("#D71920")
DARK = HexColor("#202020")
GREY = HexColor("#777777")
LINE = HexColor("#AFAFAF")


# ==================================================
# FUENTES CON SOPORTE PARA Ñ, TILDES Y SÍMBOLOS
# ==================================================

FONT = "Helvetica"
BOLD = "Helvetica-Bold"

fuentes = [
    (
        "DejaVuSans",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    ),
    (
        "LiberationSans",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
    )
]

for nombre, regular, negrita in fuentes:
    if Path(regular).exists() and Path(negrita).exists():

        pdfmetrics.registerFont(
            TTFont(nombre, regular)
        )

        pdfmetrics.registerFont(
            TTFont(nombre + "Bold", negrita)
        )

        FONT = nombre
        BOLD = nombre + "Bold"

        break



# ==================================================
# CAMPOS DEL EXCEL SEGÚN CATEGORÍA
# ==================================================

CAMPOS = {
    "general": [
        ("CÓDIGO", "Número de artículo"),
        ("SERIE", "SERIE MKT"),
        ("MARCA", "Des MARCA"),
        ("ORIGEN DE LA MARCA", "Des ORIGEN_MARCA"),
        ("MEDIDA", "Des FORMATO_COMERCIAL"),
        ("COLOR", "Des COLOR"),
        ("TERMINACIÓN", "Des TERMINACION"),
        ("MATERIAL", "MATERIAL"),
        ("USO", "Des USO"),
        ("ZONA DE APLICACIÓN", "Des ZONA_APLICACION"),
    ],
    "porcelanatos": [
    ("CÓDIGO", "Número de artículo"),
    ("SERIE", "SERIE MKT"),
    ("MARCA", "Des MARCA"),
    ("ORIGEN DE LA MARCA", "Des ORIGEN_MARCA"),
    ("MEDIDA", "Des FORMATO_COMERCIAL"),
    ("ESPESOR", "ESPESOR"),
    ("TERMINACIÓN", "Des TERMINACION"),
    ("USO", "Des USO"),
    ("ZONA DE APLICACIÓN", "Des ZONA_APLICACION"),
    ("GRÁFICAS DISTINTAS", "NÚMERO DE GRÁFICAS POR CAJA"),
    ("ABSORCIÓN DE AGUA", "Porcentaje de Absorción"),
    ],
    "griferia": [
        ("CÓDIGO", "Número de artículo"),
        ("SERIE", "SERIE MKT"),
        ("MARCA", "Des MARCA"),
        ("ORIGEN DE LA MARCA", "Des ORIGEN_MARCA"),
        ("TERMINACIÓN", "Des TERMINACION"),
        ("ZONA DE APLICACIÓN", "Des ZONA_APLICACION"),
        ("MATERIAL", "MATERIAL"),
        ("TIPO", "Des TIPO"),
        ("INCLUYE", "INCLUYE"),
        ("INSTALACIÓN", "INSTALACIÓN"),
    ],
    "sanitarios": [
        ("CÓDIGO", "Número de artículo"),
        ("MARCA", "Des MARCA"),
        ("ORIGEN DE LA MARCA", "Des ORIGEN_MARCA"),
        ("SERIE", "SERIE MKT"),
        ("TERMINACIÓN", "Des TERMINACION"),
        ("DESCARGA", "DESCARGA"),
        ("CONSUMO", "CONSUMO DE AGUA"),
        ("ASIENTO", "ASIENTO"),
        ("INCLUYE", "INCLUYE"),
        ("MATERIAL", "MATERIAL"),
        ("INSTALACIÓN", "Des INSTALACION_SANIT"),
    ],
}


# ==================================================
# FUNCIONES DE PRODUCTOS
# ==================================================


def clean(v):
    if v is None:
        return ""

    s = str(v).strip()

    if s.lower() in (
        "nan", "none", "null", "<na>", "nat", ""
    ):
        return ""

    # Normalizar caracteres Unicode
    # Convierte n + tilde combinada en ñ
    # También normaliza á, é, í, ó, ú
    s = unicodedata.normalize("NFC", s)

    # Eliminar caracteres de control invisibles
    s = "".join(
        caracter
        for caracter in s
        if unicodedata.category(caracter) not in (
            "Cc", "Cf"
        )
    )

    return s



def categoria(p):
    txt = " ".join(
        clean(p.get(k))
        for k in (
            "Rubro",
            "Familia Item",
            "Descripción del artículo",
        )
    ).casefold()

    if any(w in txt for w in (
        "porcelanato", "cerámic", "ceramic", "revestimiento"
    )):
        return "porcelanatos"

    if any(w in txt for w in (
        "grifer", "grifo", "monomando", "mezcladora"
    )):
        return "griferia"

    if any(w in txt for w in (
        "sanitario", "inodoro", "wc ", "wc-", "lavamanos"
    )):
        return "sanitarios"

    return "general"


def nombre(p):
    return (
        clean(p.get("NOMBRE ECOMMERCE"))
        or clean(p.get("Descripción del artículo"))
        or clean(p.get("Número de artículo"))
    )


def safe_sku(s):
    return (
        re.sub(r"[^a-zA-Z0-9._-]+", "_", str(s))
        .strip("._")
        or "SIN_SKU"
    )


# ==================================================
# FUNCIONES GRÁFICAS
# ==================================================

def draw_text(
    c, s, x, y, width,
    size=11, bold=False,
    color=DARK, max_lines=1
):
    s = clean(s)
    if not s:
        return y

    font = BOLD if bold else FONT
    c.setFont(font, size)
    c.setFillColor(color)

    words = s.split()
    lines = []
    line = ""

    for word in words:
        candidate = (line + " " + word).strip()
        if stringWidth(candidate, font, size) <= width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word

    if line:
        lines.append(line)

    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while (
            lines[-1]
            and stringWidth(
                lines[-1] + "…", font, size
            ) > width
        ):
            lines[-1] = lines[-1][:-1]
        lines[-1] += "…"

    for j, t in enumerate(lines):
        c.drawString(
            x,
            y - j * (size + 5),
            t
        )

    return y - len(lines) * (size + 5)


def draw_logo(c):
    path = BASE / "assets" / "logo_atika.png"

    if path.exists():
        try:
            im = Image.open(path).convert("RGBA")
            iw, ih = im.size
            sc = min(160 / iw, 64 / ih)

            c.drawImage(
                ImageReader(im),
                W - 45 - iw * sc,
                H - 86,
                iw * sc,
                ih * sc,
                mask="auto",
            )
            return
        except Exception:
            pass

    draw_text(
        c, "ATIKA",
        W - 183, H - 65,
        140, 29
    )

    c.setStrokeColor(RED)
    c.setLineWidth(3)
    c.line(W - 185, H - 76, W - 45, H - 76)


def asset_path(sku, subdir):
    root = BASE / "assets" / subdir

    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        f = root / (safe_sku(sku) + ext)
        if f.exists():
            return f

    return None


def fit_image(c, path, x, y, w, h):
    im = Image.open(path).convert("RGB")
    iw, ih = im.size

    scale = min(w / iw, h / ih)
    a = iw * scale
    b = ih * scale

    c.drawImage(
        ImageReader(im),
        x + (w - a) / 2,
        y + (h - b) / 2,
        a, b
    )


def placeholder(c, sku, x, y, w, h, category):
    c.setFillColor(HexColor("#F1F1F1"))
    c.roundRect(
        x, y, w, h, 6,
        fill=1, stroke=0
    )

    c.setStrokeColor(HexColor("#D3D3D3"))
    c.setLineWidth(1)

    c.line(x+24, y+24, x+w-24, y+h-24)
    c.line(x+24, y+h-24, x+w-24, y+24)

    draw_text(
        c, "IMAGEN DEMOSTRATIVA",
        x+26, y+h/2+20,
        w-52, 14, True, GREY
    )

    draw_text(
        c, "Sin fotografía validada para este SKU",
        x+26, y+h/2-5,
        w-52, 10, False, GREY, 2
    )

    draw_text(
        c, sku,
        x+26, y+26,
        w-52, 10, True, GREY
    )



def draw_table(c, fields, x, top, w, bottom=94):
    yy = top
    c.setStrokeColor(LINE)
    c.setLineWidth(0.45)
    c.line(x, yy, x + w, yy)

    # Columna izquierda más ancha
    left = min(285, w * 0.46)

    for label, value in fields:
        if not value:
            continue

        label_width = left - 16
        value_width = w - left - 16

        label_size = 8.5
        value_size = 9.1

        # Calcular cuántas líneas necesita cada texto
        def contar_lineas(texto, font, size, width):
            palabras = str(texto).split()
            lineas = 1
            actual = ""

            for palabra in palabras:
                prueba = (actual + " " + palabra).strip()

                if stringWidth(prueba, font, size) <= width:
                    actual = prueba
                else:
                    lineas += 1
                    actual = palabra

            return lineas

        lineas_label = contar_lineas(
            label, BOLD, label_size, label_width
        )

        lineas_valor = contar_lineas(
            value, FONT, value_size, value_width
        )

        # Altura dinámica según contenido
        rowh = max(
            27,
            max(
                lineas_label * (label_size + 5),
                lineas_valor * (value_size + 5)
            ) + 12
        )

        if yy - rowh < bottom:
            return False

        draw_text(
            c, label,
            x + 7, yy - 15,
            label_width,
            label_size,
            True,
            max_lines=lineas_label
        )

        draw_text(
            c, value,
            x + left, yy - 15,
            value_width,
            value_size,
            max_lines=lineas_valor
        )

        c.setStrokeColor(LINE)
        c.setLineWidth(0.45)

        c.line(
            x,
            yy - rowh,
            x + w,
            yy - rowh
        )

        yy -= rowh

    return True



def draw_header(c, p, kind, title=""):
    labels = {
        "porcelanatos": "PORCELANATOS & CERÁMICOS",
        "griferia": "GRIFERÍA DE COCINA Y BAÑO",
        "sanitarios": "SANITARIOS",
        "general": clean(
            p.get("Familia Item")
        ) or "FICHA TÉCNICA",
    }

    draw_text(
        c, labels[kind],
        38, H-52,
        590, 9, False, GREY
    )

    draw_logo(c)

    draw_text(
        c, title or nombre(p),
        38, H-105,
        W-280, 23,
        False, DARK, 2
    )

    c.setStrokeColor(RED)
    c.setLineWidth(4)
    c.line(38, H-151, 106, H-151)



def footer(c, sku, page=1):

    # Pie de página corporativo ATIKA
    footer_path = BASE / "assets" / "footer_atika.png"

    if footer_path.exists():
        img = Image.open(footer_path).convert("RGBA")

        iw, ih = img.size

        # Tamaño proporcional
        ancho_footer = 245
        alto_footer = ancho_footer * ih / iw

        c.drawImage(
            ImageReader(img),
            W - ancho_footer - 28,
            16,
            width=ancho_footer,
            height=alto_footer,
            preserveAspectRatio=True,
            mask="auto"
        )

    else:
        # Respaldo si no existe la imagen
        draw_text(
            c,
            "ATIKA.CL",
            W - 185,
            28,
            140,
            13,
            True,
            GREY
        )

    # Identificador del producto
    draw_text(
        c,
        f"SKU: {sku} | Página {page}",
        38,
        29,
        W - 320,
        8,
        False,
        GREY
    )

def draw_porcelanato_icons(c, p):

    variacion = clean(
        p.get("Des VARIACION_TONAL")
    )

    rectificado = clean(
        p.get("Des RECTIFI")
    )

    antideslizante = clean(
        p.get("Des ANTIDESLIZANTE")
    )

    pei = clean(
        p.get("PEI")
    )

    draw_text(
        c,
        f"Variación tonal: {variacion}",
        40,
        95,
        180,
        9
    )

    draw_text(
        c,
        f"Terminación: {antideslizante}",
        220,
        95,
        180,
        9
    )

    draw_text(
        c,
        f"Rectificado: {rectificado}",
        430,
        95,
        180,
        9
    )

    draw_text(
        c,
        f"PEI: {pei}",
        650,
        95,
        180,
        9
    )


# ==================================================
# PDF GENERAL (COMPORTAMIENTO ACTUAL)
# ==================================================

def crear_pdf_general(p):

    sku = clean(p.get("Número de artículo"))
    kind = categoria(p)

    out = BytesIO()

    c = canvas.Canvas(
        out,
        pagesize=(W, H),
        pageCompression=1
    )

    draw_header(c, p, kind)

    desc = (
        clean(p.get("DESCRIPCIÓN ECOMMERCE"))
        or clean(p.get("DESCRIPCION LARGA ECOMMERCE"))
        or clean(p.get("Descripción del artículo"))
    )

    draw_text(
        c, desc,
        38, H - 193,
        440, 10.5,
        False, GREY, 3
    )

    fields = [
        (lab, clean(p.get(col)))
        for lab, col in CAMPOS[kind]
    ]

    fields = [
        (lab, val)
        for lab, val in fields
        if val
    ]

    draw_table(
        c,
        fields,
        38,
        H - 255,
        440
    )

    img = asset_path(sku, "productos")

    if img:
        try:
            fit_image(
                c,
                img,
                515,
                185,
                405,
                355
            )
        except Exception:
            placeholder(
                c,
                sku,
                515,
                185,
                405,
                355,
                kind
            )
    else:
        placeholder(
            c,
            sku,
            515,
            185,
            405,
            355,
            kind
        )

    plano = asset_path(sku, "planos")

    if plano:
        try:
            fit_image(
                c,
                plano,
                705,
                87,
                190,
                135
            )
        except Exception:
            pass
    if kind == "porcelanatos":
        draw_porcelanato_icons(c, p)
    footer(c, sku)

    c.showPage()

    used = {
        col for _, col in CAMPOS[kind]
    }

    excluded = {
        "#",
        "Inactivo",
        "CDP",
        "ECOMMERCE",
        "BIM",
        "MANTENCIÓN",
        "MANUAL INSTALACIÓN",
        "GARANTÍA",
        "GARANTÍA TEXTO",
        "FICHA TECNICA",
        "Des FICHA TECNICA",
        "Des BIM",
        "Des MANTENCION",
        "Des MANUAL_INSTALACION",
        "Des GARANTIA",
        "Link Instalación",
        "Link Mantención",
        "Link Garantía",
        "Link FichaTecnica",
        "Link Cátalogo",
        "Productos Complementarios",
        "Unnamed: 93",
    }

    extras = []

    for key, val in p.items():

        if (
            key in used
            or key in excluded
            or key.startswith("Link ")
            or key.startswith("Des ")
            or key in (
                "Número de artículo",
                "Descripción del artículo",
                "NOMBRE ECOMMERCE",
                "DESCRIPCIÓN ECOMMERCE",
                "DESCRIPCION LARGA ECOMMERCE",
                "Marca",
                "Rubro",
                "Familia Item",
            )
        ):
            continue

        v = clean(val)

        if v and len(v) < 180:
            extras.append((key.upper(), v))

    if extras:

        draw_header(
            c,
            p,
            kind,
            "Información técnica complementaria"
        )

        draw_table(
            c,
            extras,
            38,
            H - 195,
            W - 76,
            bottom=80
        )

        footer(c, sku, 2)

        c.showPage()

    c.save()

    return out.getvalue()


# ==================================================
# PDF PORCELANATOS
# ==================================================

def crear_pdf_porcelanato(p):

    # Temporalmente reutiliza la lógica actual
    # hasta construir la plantilla oficial.

    return crear_pdf_general(p)


# ==================================================
# PDF GRIFERÍA
# ==================================================

def crear_pdf_griferia(p):

    # Por ahora usa el comportamiento existente.
    # Después se hará la plantilla Grohe/FV/etc.

    return crear_pdf_general(p)


# ==================================================
# PDF SANITARIOS
# ==================================================

def crear_pdf_sanitario(p):

    # Por ahora usa el comportamiento existente.

    return crear_pdf_general(p)


# ==================================================
# ENTRADA PRINCIPAL
# ==================================================

def crear_pdf(p):

    kind = categoria(p)

    if kind == "porcelanatos":
        return crear_pdf_porcelanato(p)

    if kind == "griferia":
        return crear_pdf_griferia(p)

    if kind == "sanitarios":
        return crear_pdf_sanitario(p)

    return crear_pdf_general(p)


