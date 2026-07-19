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
from vectorstore.faiss_store import obtener_o_crear_vectorstore
from llm.gemini_chain import consultar_con_rag

# Configuración de rutas
PDF_PATH = os.path.join(os.path.dirname(__file__), '..', 'documentos', 'Reglamento.pdf')
LOGO_PATH = os.path.join(os.path.dirname(__file__), '..', 'images', 'Escudo.jpg')

# --- Configuración de la página ---
st.set_page_config(
    page_title="Reglamento - U. del Pacífico",
    page_icon="🎓",
    layout="centered"
)

# Estilos minimalistas y barras laterales decorativas
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
            width: 80px;
            height: 100vh;
            background-color: #0F4C81;
            z-index: 99999;
        }
        .side-bar-right {
            position: fixed;
            top: 0;
            right: 0;
            width: 80px;
            height: 100vh;
            background-color: #007A33;
            z-index: 99999;
        }
        
        /* En pantallas más pequeñas (como móviles), las hacemos más delgadas para no tapar el chat */
        @media (max-width: 992px) {
            .side-bar-left, .side-bar-right {
                width: 10px;
            }
        }
    </style>
    <div class="side-bar-left"></div>
    <div class="side-bar-right"></div>
""", unsafe_allow_html=True)

# --- Encabezado con escudo ---
col1, col2 = st.columns([1, 4])
with col1:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
with col2:
    st.title("Asistente IA")
    st.markdown("**Universidad del Pacífico**")

st.markdown("---")

# --- Carga del sistema RAG (una sola vez por sesión del servidor) ---
@st.cache_resource(show_spinner="Indexando el reglamento oficial...")
def inicializar_rag(api_key: str):
    """
    Carga el PDF, crea los chunks y construye/carga el vectorstore FAISS.
    Se ejecuta una sola vez gracias a @st.cache_resource.
    """
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

# Mostrar historial de conversación
for msg in st.session_state.mensajes:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# --- Interfaz de chat ---
pregunta = st.chat_input("Escribe tu pregunta sobre el reglamento aquí...")

if pregunta:
    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):
        with st.spinner("Buscando en el reglamento..."):
            respuesta = consultar_con_rag(
                vectorstore,
                pregunta,
                st.session_state.mensajes
            )
            st.markdown(respuesta)

    # Guardar en memoria de sesión
    st.session_state.mensajes.append(HumanMessage(content=pregunta))
    st.session_state.mensajes.append(AIMessage(content=respuesta))
