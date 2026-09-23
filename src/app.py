"""
Interfaz gráfica web con Streamlit para el Asistente de IA RAG.
"""
import os
import sys
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

# Añadir src al path para importaciones de módulos locales
sys.path.insert(0, os.path.dirname(__file__))

from loaders.pdf_loader import cargar_y_trocear_pdf
from vectorstore.faiss_store import obtener_o_crear_vectorstore, FAISS_INDEX_PATH
from llm.gemini_chain import consultar_con_rag_stream

# Configuración de rutas
PDF_PATH = os.path.join(os.path.dirname(__file__), '..', 'documentos', 'Reglamento.pdf')
LOGO_PATH = os.path.join(os.path.dirname(__file__), '..', 'images', 'Escudo.jpg')
DOC_PATH = os.path.join(os.path.dirname(__file__), '..', 'DOCUMENTACION_COMPLETA_PROYECTO.md')

# --- Configuración de la página ---
st.set_page_config(
    page_title="Reglamento - U. del Pacífico",
    page_icon="🎓",
    layout="centered"
)

# Estilos minimalistas y acentos institucionales no invasivos
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stChatInputContainer {padding-bottom: 20px;}
        
        .side-bar-left {
            position: fixed;
            top: 0;
            left: 0;
            width: 6px;
            height: 100vh;
            background-color: #0F4C81;
            z-index: 100;
        }
        .side-bar-right {
            position: fixed;
            top: 0;
            right: 0;
            width: 6px;
            height: 100vh;
            background-color: #007A33;
            z-index: 100;
        }
    </style>
    <div class="side-bar-left"></div>
    <div class="side-bar-right"></div>
""", unsafe_allow_html=True)

# --- Encabezado con escudo ---
col1, col2 = st.columns([1, 4])
with col1:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_column_width=True)
with col2:
    st.title("Asistente IA")
    st.markdown("**Universidad del Pacífico**")

# --- Barra lateral con información, reset y descargas ---
with st.sidebar:
    st.header("📄 Documentación y Recursos")
    st.markdown(
        "Este asistente utiliza arquitectura **RAG** (*Retrieval-Augmented Generation*) "
        "para consultar de forma precisa el Reglamento Estudiantil Oficial."
    )
    
    if st.button("🗑️ Nueva Consulta", use_container_width=True, type="secondary"):
        st.session_state.mensajes = []
        st.session_state.pregunta_sugerida = None
        st.rerun()

    st.markdown("---")
    
    if os.path.exists(DOC_PATH):
        with open(DOC_PATH, "r", encoding="utf-8") as f:
            doc_content = f.read()
        st.download_button(
            label="📥 Descargar Documentación Técnica (.md)",
            data=doc_content,
            file_name="DOCUMENTACION_TECNICA_RAG_UNIPACIFICO.md",
            mime="text/markdown",
            use_container_width=True
        )
        
    if os.path.exists(PDF_PATH):
        with open(PDF_PATH, "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            label="📖 Descargar Reglamento Oficial (PDF)",
            data=pdf_bytes,
            file_name="Reglamento_Estudiantil_Unipacifico.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    st.markdown("---")
    st.caption("Arquitectura: LangChain + FAISS + Gemini Flash (Streaming + History-Aware)")

st.markdown("---")

# --- Carga del sistema RAG (una sola vez por sesión del servidor) ---
@st.cache_resource(show_spinner="Cargando el asistente...")
def inicializar_rag(api_key: str):
    """
    Carga el vectorstore FAISS y lo deja listo para consultas.
    Si el índice ya existe en disco, se omite por completo la carga del PDF.
    """
    if os.path.exists(FAISS_INDEX_PATH):
        return obtener_o_crear_vectorstore(chunks=[], api_key=api_key)
    else:
        chunks = cargar_y_trocear_pdf(PDF_PATH)
        return obtener_o_crear_vectorstore(chunks, api_key)

# Leer la API Key: primero desde st.secrets (Streamlit Cloud), luego desde .env (local)
def obtener_api_key() -> str:
    try:
        return st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        return os.getenv("GEMINI_API_KEY", "")

api_key = obtener_api_key()

if not api_key or api_key == "tu_api_key_aqui":
    st.error("⚠️ No se encontró la API Key. Configúrala en Streamlit Secrets o en el archivo .env.")
    st.stop()

vectorstore = inicializar_rag(api_key)

if vectorstore is None:
    st.error("No se pudo inicializar el sistema. Verifica tu GEMINI_API_KEY.")
    st.stop()

# --- Estado de sesión para memoria conversacional ---
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

if "pregunta_sugerida" not in st.session_state:
    st.session_state.pregunta_sugerida = None

# Mostrar sugerencias si aún no hay mensajes
if not st.session_state.mensajes:
    st.markdown("##### 💡 Preguntas frecuentes sugeridas:")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📝 ¿Cuál es la nota mínima para aprobar?", use_container_width=True):
            st.session_state.pregunta_sugerida = "¿Cuál es la nota mínima requerida para aprobar una asignatura en la universidad?"
            st.rerun()
        if st.button("🚫 ¿Con cuántas faltas repruebo?", use_container_width=True):
            st.session_state.pregunta_sugerida = "¿Con qué porcentaje de inasistencias se reprueba una asignatura teórica o práctica?"
            st.rerun()
    with col_b:
        if st.button("📅 ¿Hasta cuándo cancelar matrícula?", use_container_width=True):
            st.session_state.pregunta_sugerida = "¿Hasta qué semana del período académico se puede solicitar la cancelación total de matrícula?"
            st.rerun()
        if st.button("📑 ¿Cómo pedir segundo calificador?", use_container_width=True):
            st.session_state.pregunta_sugerida = "¿Cuál es el plazo y procedimiento para solicitar un segundo calificador si no estoy de acuerdo con mi nota?"
            st.rerun()

# Mostrar historial de conversación
for msg in st.session_state.mensajes:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# --- Entrada de chat o pregunta sugerida activada ---
pregunta_input = st.chat_input("Escribe tu pregunta sobre el reglamento aquí...")
pregunta_activa = pregunta_input or st.session_state.pregunta_sugerida

if pregunta_activa:
    st.session_state.pregunta_sugerida = None

    with st.chat_message("user"):
        st.markdown(pregunta_activa)

    with st.chat_message("assistant"):
        respuesta = st.write_stream(
            consultar_con_rag_stream(
                vectorstore,
                pregunta_activa,
                st.session_state.mensajes
            )
        )

    # Guardar en memoria de sesión
    st.session_state.mensajes.append(HumanMessage(content=pregunta_activa))
    st.session_state.mensajes.append(AIMessage(content=respuesta))
