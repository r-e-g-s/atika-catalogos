from pathlib import Path
from io import BytesIO
import zipfile
import streamlit as st
import pandas as pd
from generador_pdf import crear_pdf, REFERENCIAS, titulo_producto

BASE=Path(__file__).resolve().parent
st.set_page_config(page_title='ATIKA | Fichas técnicas',layout='wide',page_icon='📄')
st.markdown('''<style>h1,h2,h3{color:#222}.stButton>button[kind="primary"]{background:#D71920;border-color:#D71920}</style>''',unsafe_allow_html=True)
logo=BASE/'assets'/'logo_atika.png'
if logo.exists():st.image(str(logo),width=220)
st.title('Fichas técnicas ATIKA')
st.caption('Selecciona productos por SKU, marca o categoría. Los cinco productos de referencia conservan su PDF original.')

@st.cache_data(show_spinner='Cargando catálogo…')
def cargar_catalogo():
 path=BASE/'data'/'productos.xlsx'
 df=pd.read_excel(path,sheet_name='bbdd',dtype={'Número de artículo':str},engine='openpyxl')
 df.columns=df.columns.astype(str).str.strip()
 df=df.dropna(subset=['Número de artículo']).copy()
 df['Número de artículo']=df['Número de artículo'].astype(str).str.strip()
 df=df.drop_duplicates(subset=['Número de artículo'],keep='first')
 df['Nombre']=df.apply(titulo_producto,axis=1)
 df['Marca visible']=df.get('Des MARCA',pd.Series(index=df.index,dtype='object')).fillna('Sin marca').astype(str)
 df['Categoría visible']=df.get('Familia Item',pd.Series(index=df.index,dtype='object')).fillna('Sin categoría').astype(str)
 df['Referencia']=df['Número de artículo'].isin(REFERENCIAS)
 return df

try: df=cargar_catalogo()
except Exception as e:
 st.error(f'No se pudo leer data/productos.xlsx: {e}');st.stop()

modo=st.radio('Catálogo',['Prototipo · 5 referencias','Catálogo completo'],horizontal=True)
if modo.startswith('Prototipo'): df=df[df['Referencia']].copy()
c1,c2,c3=st.columns([2,1,1])
with c1: busqueda=st.text_input('Buscar SKU o producto',placeholder='Ej.: 39467000, Dolomite, grifo')
with c2:
 marcas=['Todas']+sorted(df['Marca visible'].unique().tolist())
 marca=st.selectbox('Marca',marcas)
with c3:
 categorias=['Todas']+sorted(df['Categoría visible'].unique().tolist())
 categoria=st.selectbox('Categoría',categorias)
if marca!='Todas':df=df[df['Marca visible']==marca]
if categoria!='Todas':df=df[df['Categoría visible']==categoria]
if busqueda:
 q=busqueda.strip().casefold()
 df=df[df[['Número de artículo','Nombre','Marca visible','Categoría visible']].fillna('').astype(str).apply(lambda col:col.str.casefold().str.contains(q,regex=False)).any(axis=1)]
st.caption(f'{len(df):,} productos encontrados'.replace(',','.'))
if df.empty:st.info('No hay resultados para los filtros seleccionados.');st.stop()

# Selector paginado para no saturar la interfaz con 15 mil productos.
if modo.startswith('Prototipo'):
 vista=df
else:
 pagina=st.number_input('Página',min_value=1,max_value=max(1,(len(df)+49)//50),value=1)
 vista=df.iloc[(pagina-1)*50:pagina*50]

st.dataframe(vista[['Número de artículo','Nombre','Marca visible','Categoría visible','Referencia']].rename(columns={'Número de artículo':'SKU','Marca visible':'Marca','Categoría visible':'Categoría','Referencia':'PDF original'}),hide_index=True,use_container_width=True)
opciones=vista['Número de artículo'].tolist()
seleccion=st.multiselect('Selecciona uno o más SKU de los resultados visibles',options=opciones,format_func=lambda s:f'{s} — {vista.loc[vista["Número de artículo"]==s,"Nombre"].iloc[0]}')
if st.button('Seleccionar todos los productos visibles'):
 st.session_state['seleccion_todos']=opciones
if st.session_state.get('seleccion_todos'):
 seleccion=list(dict.fromkeys(seleccion+ [x for x in st.session_state['seleccion_todos'] if x in opciones]))
 st.caption(f'{len(seleccion)} SKU preparados. Puedes cambiar filtros para reiniciar la selección.')

if seleccion:
 if len(seleccion)==1:
  p=df[df['Número de artículo']==seleccion[0]].iloc[0].to_dict()
  contenido,original=crear_pdf(p)
  st.download_button('📥 Descargar PDF',data=contenido,file_name=f'{seleccion[0].replace("/","-")}-FT.pdf',mime='application/pdf',type='primary')
  st.caption('PDF original ATIKA' if original else 'PDF generado a partir de las especificaciones del Excel')
 else:
  memoria=BytesIO()
  with zipfile.ZipFile(memoria,'w',compression=zipfile.ZIP_DEFLATED) as z:
   for sku in seleccion:
    p=df[df['Número de artículo']==sku].iloc[0].to_dict()
    contenido,_=crear_pdf(p)
    z.writestr(f'{sku.replace("/","-")}-FT.pdf',contenido)
  st.download_button(f'📦 Descargar ZIP ({len(seleccion)} PDF)',data=memoria.getvalue(),file_name='Fichas_ATIKA.zip',mime='application/zip',type='primary')
else: st.info('Selecciona un SKU para descargar su ficha o varios para descargar un ZIP.')
st.divider()
st.caption('Las imágenes y diagramas de productos nuevos deben ser proporcionados o aprobados por ATIKA. No se generan especificaciones no contenidas en la fuente.')
