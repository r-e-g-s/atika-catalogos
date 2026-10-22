from pathlib import Path
from io import BytesIO
import zipfile
import streamlit as st
import pandas as pd
from generador_pdf import crear_pdf, nombre, categoria, safe_sku

BASE=Path(__file__).resolve().parent
st.set_page_config(page_title='ATIKA | Fichas técnicas automáticas',page_icon='📄',layout='wide')
st.markdown('<style>h1,h2,h3{color:#252525}.stButton>button[kind="primary"]{background:#D71920;border-color:#D71920}</style>',unsafe_allow_html=True)
logo=BASE/'assets'/'logo_atika.png'
if logo.exists(): st.image(str(logo),width=210)
st.title('Fichas técnicas ATIKA')
st.caption('Fichas generadas automáticamente desde las especificaciones actuales del Excel. Ningún PDF original se reutiliza.')

@st.cache_data(show_spinner='Leyendo especificaciones…')
def leer_excel(contenido:bytes):
    df=pd.read_excel(BytesIO(contenido),sheet_name='bbdd',engine='openpyxl',dtype={'Número de artículo':str})
    df.columns=df.columns.astype(str).str.strip()
    if 'Número de artículo' not in df.columns:raise ValueError('Falta la columna Número de artículo en la hoja bbdd')
    df=df.dropna(subset=['Número de artículo']).copy()
    df['Número de artículo']=df['Número de artículo'].astype(str).str.strip()
    df=df[df['Número de artículo']!='']
    df=df.drop_duplicates('Número de artículo',keep='first').fillna('')
    df['Nombre']=df.apply(nombre,axis=1)
    df['Categoría plantilla']=df.apply(categoria,axis=1)
    df['Marca visible']=df.get('Des MARCA',pd.Series('',index=df.index)).astype(str)
    return df

origen=st.radio('Fuente de datos',['Excel del repositorio','Cargar Excel actualizado (prueba)'],horizontal=True)
if origen.startswith('Cargar'):
    archivo=st.file_uploader('Sube un XLSX con hoja bbdd y columna Número de artículo',type=['xlsx'])
    if archivo is None:st.info('Carga el Excel para continuar.');st.stop()
    contenido=archivo.getvalue()
else:
    ruta=BASE/'data'/'productos.xlsx'
    if not ruta.exists():st.error('No existe data/productos.xlsx');st.stop()
    contenido=ruta.read_bytes()
try: df=leer_excel(contenido)
except Exception as exc:st.error(f'No se pudo leer el Excel: {type(exc).__name__}: {exc}');st.stop()

st.caption(f'{len(df):,} SKU únicos disponibles'.replace(',','.'))
q=st.text_input('Buscar por SKU, nombre o marca',placeholder='Ej.: 39467000, Dolomite, Grohe')
c1,c2=st.columns(2)
with c1: cat=st.selectbox('Plantilla',['Todas']+sorted(df['Categoría plantilla'].unique().tolist()))
with c2: marca=st.selectbox('Marca',['Todas']+sorted(df['Marca visible'].unique().tolist()))
vista=df
if cat!='Todas':vista=vista[vista['Categoría plantilla']==cat]
if marca!='Todas':vista=vista[vista['Marca visible']==marca]
if q.strip():
    t=q.strip().casefold()
    mask=vista[['Número de artículo','Nombre','Marca visible']].astype(str).apply(lambda col:col.str.casefold().str.contains(t,regex=False)).any(axis=1)
    vista=vista[mask]
st.caption(f'{len(vista):,} resultados'.replace(',','.'))
if vista.empty:st.info('Sin coincidencias.');st.stop()
max_page=max(1,(len(vista)+49)//50)
pag=st.number_input('Página de resultados',min_value=1,max_value=max_page,value=1)
pagina=vista.iloc[(pag-1)*50:pag*50]
st.dataframe(pagina[['Número de artículo','Nombre','Marca visible','Categoría plantilla']].rename(columns={'Número de artículo':'SKU','Marca visible':'Marca','Categoría plantilla':'Plantilla'}),hide_index=True,use_container_width=True)
options=pagina['Número de artículo'].tolist()
selected=st.multiselect('Selecciona SKU de esta página',options,format_func=lambda sku:f'{sku} — {pagina.loc[pagina["Número de artículo"]==sku,"Nombre"].iloc[0]}')
if selected:
    if len(selected)==1:
        sku=selected[0];prod=pagina[pagina['Número de artículo']==sku].iloc[0].to_dict()
        pdf=crear_pdf(prod)
        st.download_button('📥 Descargar ficha PDF',pdf,file_name=f'{safe_sku(sku)}-FT.pdf',mime='application/pdf',type='primary')
        st.caption('Se generó un PDF nuevo usando los datos del Excel cargado.')
        try:
            import base64
            encoded=base64.b64encode(pdf).decode('ascii')
            st.markdown(f'<iframe src="data:application/pdf;base64,{encoded}" width="100%" height="620" type="application/pdf"></iframe>',unsafe_allow_html=True)
        except Exception:pass
    else:
        buffer=BytesIO()
        with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED) as z:
            for sku in selected:
                prod=pagina[pagina['Número de artículo']==sku].iloc[0].to_dict()
                z.writestr(f'{safe_sku(sku)}-FT.pdf',crear_pdf(prod))
        st.download_button(f'📦 Descargar {len(selected)} fichas en ZIP',buffer.getvalue(),file_name='Fichas_ATIKA.zip',mime='application/zip',type='primary')
else:st.info('Selecciona un producto para generar su ficha, o varios para descargar un ZIP.')
st.divider()
st.caption('Imágenes: assets/productos/SKU.png y planos: assets/planos/SKU.png (también JPG/JPEG/WEBP). Si no existe la imagen, se muestra un marcador demostrativo con el SKU.')

st.caption('Las imágenes y diagramas de productos nuevos deben ser proporcionados o aprobados por ATIKA. No se generan especificaciones no contenidas en la fuente.')
