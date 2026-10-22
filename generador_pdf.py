"""Fichas horizontales ATIKA: originales exactos para referencias; plantilla para resto."""
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape
import re
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from PIL import Image

BASE=Path(__file__).resolve().parent
REFERENCIAS={
 '30294DC0':'30294DC0-FT.pdf',
 '39467000':'39467000-FT.pdf',
 'P3CR572AT':'P3CR572AT-FT.pdf',
 'DOLOMITE WT 60X120/L':'DOLOMITE-WHITE-60X120-FT.pdf',
 'MUZZANO CINZA 60X120':'MUZZANO-CINZA-60X120-FT.pdf',
}
W,H=780,540
ROJO=HexColor('#D71920'); GRIS=HexColor('#777777')
CAMPOS=[('CÓDIGO','Número de artículo'),('SERIE','SERIE MKT'),('MARCA','Des MARCA'),('ORIGEN DE LA MARCA','Des ORIGEN_MARCA'),('MEDIDA','Des FORMATO_COMERCIAL'),('COLOR','Des COLOR'),('TERMINACIÓN','Des TERMINACION'),('ESPESOR','ESPESOR'),('USO','Des USO'),('ZONA DE APLICACIÓN','Des ZONA_APLICACION'),('VARIACIÓN TONAL','Des VARIACION_TONAL'),('RECTIFICADO','Des RECTIFI'),('MATERIAL','MATERIAL'),('ASIENTO','ASIENTO'),('DESCARGA','DESCARGA'),('CONSUMO DE AGUA','CONSUMO DE AGUA'),('INCLUYE','INCLUYE'),('ABSORCIÓN DE AGUA','Porcentaje de Absorción')]

def limpio(x):
 s=str(x).strip() if x is not None else ''
 return '' if s.lower() in ('nan','none','null','-','y','no','si','0','0.0') else s

def titulo_producto(p):
 a=limpio(p.get('NOMBRE ECOMMERCE'))
 return a if len(a)>5 else limpio(p.get('Descripción del artículo')) or str(p.get('Número de artículo',''))

def texto(c,s,x,y,maxw,size=11,bold=False,color=HexColor('#202020')):
 s=limpio(s); font='Helvetica-Bold' if bold else 'Helvetica'; c.setFont(font,size);c.setFillColor(color)
 while s and stringWidth(s,font,size)>maxw: s=s[:-2].rstrip()+'…'
 c.drawString(x,y,s)

def logo(c):
 p=BASE/'assets'/'logo_atika.png'
 if p.exists():
  try:
   im=Image.open(p);c.drawImage(ImageReader(im),645,477,width=110,height=40,preserveAspectRatio=True,anchor='c',mask='auto');return
  except Exception: pass
 texto(c,'ATIKA',652,488,105,25,True)
 c.setStrokeColor(ROJO);c.setLineWidth(3);c.line(645,482,755,482)

def imagen(c,sku):
 # Fotos provistas por la empresa: assets/productos/SKU.png|jpg|jpeg.
 for ext in ('.png','.jpg','.jpeg','.webp'):
  p=BASE/'assets'/'productos'/f'{sku}{ext}'
  if p.exists():
   try:
    im=Image.open(p).convert('RGB'); iw,ih=im.size; scale=min(330/iw,265/ih)
    c.drawImage(ImageReader(im),435+(330-iw*scale)/2,142+(265-ih*scale)/2,iw*scale,ih*scale);return True
   except Exception: pass
 return False

def crear_pdf(p):
 sku=str(p.get('Número de artículo','')).strip()
 ref=BASE/'referencias'/REFERENCIAS.get(sku,'')
 if sku in REFERENCIAS and ref.is_file(): return ref.read_bytes(),True
 out=BytesIO();c=canvas.Canvas(out,pagesize=(W,H),pageCompression=1)
 c.setFillColor(HexColor('#FFFFFF'));c.rect(0,0,W,H,fill=1,stroke=0)
 texto(c,limpio(p.get('Familia Item')) or limpio(p.get('Rubro')) or 'FICHA TÉCNICA',32,496,500,9,True,GRIS)
 logo(c)
 titulo=titulo_producto(p)
 texto(c,titulo,32,457,715,23,False)
 c.setStrokeColor(ROJO);c.setLineWidth(4);c.line(32,440,82,440)
 desc=limpio(p.get('DESCRIPCIÓN ECOMMERCE'))
 if len(desc)<6:desc=limpio(p.get('Descripción del artículo'))
 texto(c,desc,32,409,390,10,False,GRIS)
 filas=[(etiqueta,limpio(p.get(col))) for etiqueta,col in CAMPOS]
 filas=[(k,v) for k,v in filas if v]
 y=376
 for k,v in filas[:14]:
  c.setStrokeColor(HexColor('#BBBBBB'));c.setLineWidth(.45);c.line(32,y-6,411,y-6)
  texto(c,k,36,y,145,8,True)
  texto(c,v,185,y,222,8)
  y-=23
 if not imagen(c,sku):
  c.setFillColor(HexColor('#F6F6F6'));c.roundRect(449,170,287,210,4,stroke=0,fill=1)
  texto(c,'Fotografía pendiente de asociar al SKU',471,268,250,10,False,GRIS)
  texto(c,sku,471,248,250,10,True,GRIS)
 c.setStrokeColor(HexColor('#EEEEEE'));c.line(32,38,747,38)
 texto(c,'ATIKA.CL',620,18,120,12,True,GRIS)
 texto(c,'Ficha generada desde base de especificaciones',32,20,410,8,False,GRIS)
 c.save();return out.getvalue(),False
