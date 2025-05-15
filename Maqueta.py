import streamlit as st
import pandas as pd
import os
import datetime
from io import StringIO, BytesIO

st.set_page_config(page_title="Generador de Reportes de Sustentabilidad", layout="wide")

# --- DIRECTORIOS ---
input_dir = os.path.join(os.getcwd(), "input")
out_dir = "/mnt/data/simulated_reports"

# Crear carpeta de datos de entrada simulados
if not os.path.exists(input_dir):
    os.makedirs(input_dir)
    # Datos simulados de entrada
    df_raw_ambiental = pd.DataFrame({
        "fecha_reporte": ["2025-03-01", "2025-03-15"],
        "consumo_hidrico_m3": [12345, 11320],
        "emisiones_co2_ton": [350, 340],
        "area": ["Ambiental", "Ambiental"]
    })
    df_raw_social = pd.DataFrame({
        "fecha": ["2025-03-10", "2025-04-01"],
        "actividad": ["Reunión con junta de vecinos", "Entrega de informe de avance"],
        "participantes": [20, 35],
        "area": ["Comunicaciones", "Comunicaciones"]
    })
    df_raw_ambiental.to_csv(os.path.join(input_dir, "ambiental_q1.csv"), index=False)
    df_raw_social.to_csv(os.path.join(input_dir, "social_abril.csv"), index=False)

# --- DIRECTORIOS ---
sim_in_dir = input_dir  # Datos simulados en carpeta del proyecto
# out_dir remains unchanged
if 'uploads' not in st.session_state:
    st.session_state.uploads = []  # list of dicts: {nombre, df, variables, category}

# --- MENÚ ---
st.sidebar.image("https://chile.angloamerican.com/~/media/Images/A/Anglo-American-Group-v9/Universal/logo/anglo-american-footer-logo.svg", width=900)
with st.sidebar:
    st.markdown("### Menú Principal")
    menu = st.selectbox("Selecciona una página:", ["Inicio", "Carga y Normalización de Datos", "Generador de Reportes", "Preguntas Frecuentes (FAQ)"])

if menu == "Inicio":
    st.image("https://urbanismo.malaga.eu/export/sites/urbanismo/.galleries/IMAGENES-Imagenes-de-estructura/banner-equipo-redactor.jpg", width=200)
    st.title("🧠 Plataforma de Reportes de Sustentabilidad Asistida por IA")
    st.markdown("""
    Hola!, esta herramienta inteligente te ayudará transformar documentos no estructurados en reportes claros, trazables y adaptados a distintas audiencias estratégicas.

    A través de esta plataforma podrás:
    - Subir informes y documentos internos.
    - Normalizar datos automáticamente mediante procesamiento semántico.
    - Generar reportes personalizables adaptados a públicos específicos (comunidad, reguladores, inversionistas).

    Usa el menú lateral para comenzar.
    """)
    st.markdown("---")
    st.subheader("📈 Últimos reportes generados")
    data_dummy = pd.DataFrame([
        {"Título": "Informe Ambiental Abril 2025", "Responsable": "María Torres", "Fecha": "2025-05-16", "Temas": "Indicadores Ambientales, Impacto Social"},
        {"Título": "Reporte Participación Ciudadana", "Responsable": "Luis Soto", "Fecha": "2025-05-15", "Temas": "Relaciones Comunitarias"},
        {"Título": "Resumen Ejecutivo Q1", "Responsable": "Ana Rivas", "Fecha": "2025-05-14", "Temas": "Ambiental, Social"}
    ])
    st.dataframe(data_dummy, use_container_width=True)

elif menu == "Carga y Normalización de Datos":
    st.header("📥 Carga y Normalización de Datos")
    st.markdown(
        "Sube archivos de cualquier naturaleza y deja que la IA detecte variables y los clasifique en datasets.")

    # Carga de archivos de cualquier tipo
    st.markdown("### Formulario de carga manual")
    with st.form("form_carga_manual"):
        autor = st.text_input("Nombre del responsable del archivo")
        unidad = st.text_input("Unidad o área de la empresa")
        uploaded = st.file_uploader("Subir archivos", accept_multiple_files=True)
        submit_carga = st.form_submit_button("Cargar")

    if submit_carga and uploaded:
        for file in uploaded:
            filename = file.name
            ext = filename.split('.')[-1].lower()
            try:
                if ext == 'csv':
                    df = pd.read_csv(file)
                elif ext in ['xls', 'xlsx']:
                    df = pd.read_excel(file)
                elif ext == 'json':
                    df = pd.read_json(file)
                elif ext in ['txt', 'log', 'md']:
                    text = file.read().decode('utf-8', errors='ignore')
                    df = pd.DataFrame({'Contenido': text.splitlines()})
                elif ext in ['html', 'htm']:
                    text = file.read().decode('utf-8', errors='ignore')
                    df = pd.DataFrame({'HTML': [text]})
                else:
                    content = file.read()
                    df = pd.DataFrame({'Bytes': [content]})
                variables = df.columns.tolist()
                if 'impacto' in filename.lower():
                    category = 'Impacto Social'
                elif 'ambiental' in filename.lower():
                    category = 'Indicadores Ambientales'
                else:
                    category = 'Otros Datos'
                st.session_state.uploads.append({
                    'autor': autor,
                    'unidad': unidad,
                    'nombre': filename,
                    'df': df,
                    'variables': variables,
                    'category': category
                })
                st.toast(f"Archivo '{filename}' procesado como {category}", icon="📄")
            except Exception as e:
                st.warning(f"No se pudo procesar el archivo '{filename}': {e}")

    # Procesar automáticamente archivos en la carpeta input
    for filename in os.listdir(input_dir):
        full_path = os.path.join(input_dir, filename)
        if filename in [u['nombre'] for u in st.session_state.uploads]:
            continue  # ya cargado
        try:
            ext = filename.split('.')[-1].lower()
            if ext == 'csv':
                df = pd.read_csv(full_path)
            elif ext in ['xls', 'xlsx']:
                df = pd.read_excel(full_path)
            elif ext == 'json':
                df = pd.read_json(full_path)
            elif ext in ['txt', 'log', 'md']:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                df = pd.DataFrame({'Contenido': text.splitlines()})
            elif ext in ['html', 'htm']:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                df = pd.DataFrame({'HTML': [text]})
            else:
                with open(full_path, 'rb') as f:
                    content = f.read()
                df = pd.DataFrame({'Bytes': [content]})
            variables = df.columns.tolist()
            if 'impacto' in filename.lower():
                category = 'Impacto Social'
            elif 'ambiental' in filename.lower():
                category = 'Indicadores Ambientales'
            else:
                category = 'Otros Datos'
            st.session_state.uploads.append({
                'nombre': filename,
                'df': df,
                'variables': variables,
                'category': category
            })
            st.toast(f"Archivo '{filename}' clasificado como {category}", icon="📄")
        except Exception as e:
            st.warning(f"No se pudo procesar automáticamente '{filename}': {e}")

    # Mostrar datasets disponibles
    import random
    from datetime import date

    st.subheader("🧪 Datasets y variables disponibles")
    with st.popover("¿Qué estoy viendo aquí?"):
        st.markdown("""
        **📘 Diccionario de campos:**
        - **Variable**: nombre de la métrica o campo extraído desde los archivos.
        - **Definición**: explicación breve del significado de la variable.
        - **Última actualización**: fecha del último archivo que aportó datos a esta variable.
        - **Calidad**: porcentaje estimado de completitud y consistencia interna de los datos.
        - **Presencia**: número estimado de documentos en los que esta variable fue detectada.
        - **Variabilidad**: indicador numérico (entre 0 y 1) que refleja la dispersión o cambio de los valores reportados en distintos archivos.
        """)
    datasets_catalogo = {
        "Indicadores Ambientales": {
            "descripcion": "Contiene métricas clave sobre consumo hídrico, emisiones de gases y residuos generados en las operaciones.",
            "fecha_actualizacion": "2025-05-15",
            "calidad": f"{random.randint(85, 98)}%",
            "variables": {
                "consumo_hidrico_m3": "Volumen total de agua utilizada en m³",
                "emisiones_co2_ton": "Toneladas de CO2 emitidas en el periodo",
                "residuos_generados": "Total de residuos sólidos registrados"
            }
        },
        "Relaciones Comunitarias": {
            "descripcion": "Registra eventos de vinculación comunitaria, talleres, reuniones y acciones de participación ciudadana.",
            "fecha_actualizacion": "2025-05-14",
            "calidad": f"{random.randint(80, 96)}%",
            "variables": {
                "actividad": "Nombre de la actividad ejecutada",
                "participantes": "Cantidad de personas participantes",
                "comunidad": "Nombre o sector de la comunidad involucrada"
            }
        },
        "Impacto Social": {
            "descripcion": "Resume los impactos positivos o negativos de los proyectos sobre el bienestar de las comunidades.",
            "fecha_actualizacion": "2025-05-13",
            "calidad": f"{random.randint(78, 95)}%",
            "variables": {
                "categoria_impacto": "Área temática del impacto (salud, educación, etc.)",
                "nivel_impacto": "Magnitud del impacto percibido",
                "beneficiarios_directos": "Número estimado de personas afectadas positivamente"
            }
        }
    }

    ds_tabs = st.tabs(list(datasets_catalogo.keys()))
    for tab, ds_name in zip(ds_tabs, datasets_catalogo.keys()):
        with tab:
            data = datasets_catalogo[ds_name]
            st.markdown(f"**Descripción:** {data['descripcion']}")
            st.markdown(f"**Fecha de última actualización:** {data['fecha_actualizacion']}")
            st.markdown(f"**Índice global de calidad:** {data['calidad']}")
            with st.expander("🔍 Ver variables disponibles"):
                rows = []
                for var, definicion in data['variables'].items():
                    calidad = f"{random.randint(80, 100)}%"
                    fecha = date.today().strftime("%Y-%m-%d")
                    rows.append({
                        "Variable": var,
                        "Definición": definicion,
                        "Última actualización": fecha,
                        "Calidad": calidad,
                        "Presencia": f"{random.randint(2, 12)} documentos",
                        "Variabilidad": f"{random.uniform(0.1, 1.0):.2f}"
                    })
                st.table(pd.DataFrame(rows))

    # Historial de cargas abajo
    st.subheader("📜 Historial de Archivos Subidos")
    if st.session_state.uploads:
        df_hist = pd.DataFrame([
            {
                'Archivo': u['nombre'],
                'Categoría': u['category'],
                'Formato': u['nombre'].split('.')[-1].upper(),
                'Fecha de carga': date.today().strftime("%Y-%m-%d"),
                'Variables detectadas': len(u['variables']),
                'Autor': u.get('autor', 'Desconocido'),
                'Unidad': u.get('unidad', 'No especificada'),
                '⚠️': '🟠 Posible inconsistencia' if len(u['variables']) < 2 or (len(u['df']) < 2) else ''
            } for u in st.session_state.uploads
        ])
        st.table(df_hist)
    else:
        st.info("No se ha subido ningún archivo aún.")

elif menu == "Generador de Reportes":
    st.header("🧾 Generador de Reportes")
    st.markdown("""
    Esta sección permite generar reportes automáticos adaptados al tipo de audiencia a partir de los datasets ya organizados.
    """)

    st.markdown("### 🔄 Copiar estructura de otro informe")
    plantilla = st.file_uploader("Sube un informe anterior para reutilizar su estructura:", type=["docx", "txt", "pdf"])
    if plantilla:
        st.success(
            "Estructura del informe cargada correctamente. Se utilizarán las secciones detectadas como base del nuevo reporte.")
        # Simulación de secciones detectadas
        secciones_simuladas = ["Introducción", "Metodología", "Indicadores Clave", "Conclusiones"]
        st.markdown("#### 🧩 Secciones detectadas:")
        for sec in secciones_simuladas:
            st.markdown(f"- {sec}")
        st.info("Puedes modificar el contenido dentro de cada sección más adelante en el proceso de generación.")

    with st.popover("¿Cómo funciona este generador?"):
        st.markdown("""
        - **Audiencia**: define el enfoque del lenguaje, profundidad y énfasis temático del informe.
        - **Componentes**: selecciona qué áreas temáticas (datasets) se incluirán en el informe generado.
        - **Resumen automático**: se genera un texto inicial que puedes editar según tus necesidades.
        - **Formato de salida**: define si deseas descargar el informe como PDF, Word o HTML.
        - **Título y Objetivo**: te permiten establecer el enfoque general y el propósito específico del informe.
        - **Longitud estimada**: puedes establecer un límite manual en páginas o permitir que la IA determine la extensión óptima según los contenidos disponibles.
        - **Estilo narrativo**: orienta el tipo de redacción esperada: ejecutiva, técnica o con énfasis visual.
        - **Estructura preexistente**: si cargas un informe anterior, el sistema detectará sus secciones para reutilizarlas como plantilla.
        - **Visualizaciones sugeridas**: la IA puede recomendar imágenes y gráficos simulados en base a los componentes seleccionados.
        """)

    # Selección del tipo de audiencia
    audiencia = st.selectbox("Selecciona el tipo de audiencia:", [
        "Público general", "Comunidad local", "Medio de comunicación", "Autoridad reguladora", "Inversionistas"])

    # Selección de componentes
    componentes = st.multiselect(
        "Componentes del reporte:", [
            "Indicadores Ambientales", "Relaciones Comunitarias", "Impacto Social"
        ], default=["Indicadores Ambientales"])

    # Selección de formato
    formato = st.radio("Formato de salida:", ["PDF", "HTML", "Word"], horizontal=True)

    # Parámetros del informe
    usar_ia_longitud = st.checkbox("Permitir que la IA determine la longitud automáticamente", value=True)
    if usar_ia_longitud:
        longitud = "Sin límite"
    else:
        longitud = st.slider("Selecciona la longitud máxima del informe (en páginas):", 1, 10, 5)
    titulo = st.text_input("Título sugerido del informe:",
                           value=f"Informe de {audiencia} - {datetime.date.today().strftime('%B %Y')}")
    objetivo = st.text_area("Objetivo principal del informe:", "Este informe tiene como propósito...")

    # Estilo narrativo sugerido
    estilo = st.selectbox("Estilo del informe:",
                          ["Resumen ejecutivo", "Informe técnico", "Informe con visualizaciones"], index=0)

    # Recomendación automática de la IA (simulada)
    st.info(
        f"🤖 Recomendación de IA: Para la audiencia '{audiencia}', se recomienda un estilo '{estilo}' con énfasis en '{componentes[0] if componentes else 'contenido general'}'.")

    # Generación simulada de imágenes para diagramación
    with st.expander("🖼️ Imágenes sugeridas para la diagramación"):
        for comp in componentes:
            st.image("https://via.placeholder.com/500x300.png?text=Gráfico+de+" + comp.replace(" ", "+"),
                     caption=f"Visualización sugerida: {comp}", use_container_width=True)

    # Campo de resumen editable
    st.markdown("#### 📝 Resumen automático generado")
    resumen = st.text_area("Puedes editar este resumen si lo deseas:",
                           f"Este reporte presenta un resumen ejecutivo adaptado a la audiencia '{audiencia}', basado en {', '.join(componentes)}.")

    # Vista previa estructurada del informe
    with st.expander("🔍 Vista previa del esquema del informe"):
        st.markdown(f"**Título:** {titulo}")
        st.markdown(f"**Audiencia objetivo:** {audiencia}")
        st.markdown(f"**Componentes seleccionados:** {', '.join(componentes)}")
        st.markdown(f"**Formato de salida:** {formato}")
        st.markdown(f"**Longitud estimada:** {longitud} páginas" if isinstance(longitud,
                                                                               int) else "**Longitud estimada:** Sin límite (determinado por IA)")
        st.markdown(f"**Objetivo:** {objetivo}")
        st.markdown(f"**Resumen:** {resumen}")

    # Botón para generar el reporte
    if st.button("Generar Reporte"):
        st.success(f"Reporte generado exitosamente para: {audiencia} en formato {formato}.")
        st.download_button("📥 Descargar reporte simulado", data="Contenido simulado del reporte.",
                           file_name=f"reporte_{audiencia.lower().replace(' ', '_')}.{formato.lower()}")
    st.write("Seleccione una opción del menú.")
    
elif menu == "Preguntas Frecuentes (FAQ)":
    st.header("❓ Preguntas Frecuentes (FAQ)")
    with st.expander("¿Qué tipo de archivos puedo subir a la plataforma?"):
        st.markdown("Puedes subir archivos en formato .csv, .xlsx, .json, .docx, .txt, .pdf, entre otros. La IA intentará extraer automáticamente información útil desde cualquier tipo de documento.")

    with st.expander("¿Cómo clasifica la IA los archivos subidos?"):
        st.markdown("El sistema analiza el contenido del archivo (nombres de columnas, texto, patrones) y lo asigna automáticamente a categorías temáticas como 'Indicadores Ambientales', 'Impacto Social' o 'Relaciones Comunitarias'.")

    with st.expander("¿Puedo subir un informe anterior como base para uno nuevo?"):
        st.markdown("Sí. Puedes cargar un informe en formato .pdf, .docx o .txt y el sistema extraerá su estructura (secciones) para reutilizarla con datos actualizados.")

    with st.expander("¿Qué significa la calidad o consistencia de los datos?"):
        st.markdown("Es un indicador generado por la IA basado en la completitud, coherencia y frecuencia de aparición de cada variable. Se muestra como semáforo o porcentaje.")

    with st.expander("¿Qué hace el sistema cuando marco 'longitud determinada por la IA'?"):
        st.markdown("Cuando habilitas esta opción, el sistema estimará automáticamente la extensión más adecuada del informe según la cantidad y calidad de los datos disponibles.")

    with st.expander("¿Qué tan personalizable es el informe final?"):
        st.markdown("Puedes editar el título, el objetivo, el resumen, la estructura (si cargas una plantilla) y también el estilo narrativo. Además, puedes elegir el formato de salida.")
