import streamlit as st
import os
from langchain_core.messages import HumanMessage, AIMessage
from main import extraer_texto_pdf, consultar_gemini, PDF_PATH

# Rutas de recursos
LOGO_PATH = os.path.join(os.path.dirname(__file__), '..', 'images', 'Escudo.jpg')

st.set_page_config(page_title="Reglamento - U. del Pacífico", page_icon="🎓", layout="centered")

# Estilos minimalistas CSS
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stChatInputContainer {padding-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

# Encabezado con imagen y título
col1, col2 = st.columns([1, 4])
with col1:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
with col2:
    st.title("Asistente IA")
    st.markdown("**Universidad del Pacífico**")

st.markdown("---")

# 1. Cargar y cachear el PDF
@st.cache_data
def cargar_reglamento():
    return extraer_texto_pdf(PDF_PATH)

with st.spinner("Cargando el reglamento oficial..."):
    texto_reglamento = cargar_reglamento()
    
if not texto_reglamento:
    st.error("No se pudo cargar el documento PDF. Verifica la ruta y que el archivo exista.")
    st.stop()

# 2. Inicializar el estado de la sesión para la memoria
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Mostrar el historial de mensajes
for msg in st.session_state.mensajes:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# 3. Interfaz de Chat
pregunta = st.chat_input("Escribe tu pregunta sobre el reglamento aquí...")

if pregunta:
    # Mostrar la pregunta del usuario en la pantalla
    with st.chat_message("user"):
        st.markdown(pregunta)
        
    # Obtener respuesta del modelo
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            # Enviar la pregunta, pasando el historial almacenado
            respuesta = consultar_gemini(texto_reglamento, pregunta, st.session_state.mensajes)
            st.markdown(respuesta)
            
    # Guardar en memoria (estado de la sesión)
    st.session_state.mensajes.append(HumanMessage(content=pregunta))
    st.session_state.mensajes.append(AIMessage(content=respuesta))
