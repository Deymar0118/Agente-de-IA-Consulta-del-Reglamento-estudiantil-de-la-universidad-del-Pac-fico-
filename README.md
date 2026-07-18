# Agente de IA - Consulta del Reglamento Estudiantil de la Universidad del Pacífico

Este proyecto es un Agente de Inteligencia Artificial desarrollado para facilitar la consulta del Reglamento Estudiantil de la Universidad del Pacífico. Permite a estudiantes, docentes y personal administrativo hacer preguntas en lenguaje natural y obtener respuestas precisas basadas estrictamente en el documento oficial.

---

## Arquitectura del Proyecto

El proyecto está diseñado bajo el patrón RAG (Retrieval-Augmented Generation) y una arquitectura de capas separadas.

1. **Capa de Lógica (Backend):** Utiliza LangChain y Google Gemini (gemini-flash-latest).
   - **Recuperación (Retrieval):** Se extrae la base de conocimiento local (el PDF del reglamento) mediante PyPDFLoader.
   - **Aumento (Augmentation):** El texto del reglamento y el historial de la conversación se inyectan en el prompt del modelo para darle contexto y memoria a corto plazo.
   - **Generación (Generation):** Gemini procesa la información y genera una respuesta limpia usando StrOutputParser.
2. **Capa de Presentación (Frontend):** Construida con Streamlit, ofrece una interfaz web minimalista e interactiva (tipo chat) separada de la lógica de negocio, adaptada a la identidad visual de la universidad.

---

## Pasos de Instalación y Ejecución Local

### 1. Clonar el repositorio y preparar el entorno
Abre tu terminal y ejecuta:
```bash
git clone https://github.com/Deymar0118/Agente-de-IA-Consulta-del-Reglamento-estudiantil-de-la-universidad-del-Pac-fico-.git
cd Agente-de-IA-Consulta-del-Reglamento-estudiantil-de-la-universidad-del-Pac-fico-
```

### 2. Instalar dependencias
Asegúrate de tener Python instalado y ejecuta:
```bash
pip install -r requirements.txt
```

### 3. Configurar la API Key
Crea un archivo llamado .env en la raíz del proyecto y añade tu clave de acceso de Google Gemini:
```env
GEMINI_API_KEY=tu_api_key_aqui
```
### 4. Iniciar la aplicación
Ejecuta el servidor web local con Streamlit:
```bash
streamlit run src/app.py
```
El navegador se abrirá automáticamente en http://localhost:8501.

---

## Despliegue en la Nube

Como alternativa a Oracle Cloud Infrastructure (OCI) sugerido inicialmente, este proyecto ha sido desplegado exitosamente utilizando Streamlit Community Cloud. Esta decisión arquitectónica se tomó porque:
1. Ofrece una integración nativa y optimizada para aplicaciones basadas en Streamlit.
2. Permite despliegue continuo y automático (CI/CD) directamente desde el repositorio de GitHub.
3. No requiere administración de servidores ni apertura manual de puertos de red, lo que resulta en una infraestructura mucho más eficiente para este caso de uso.

*(Para configurar el despliegue en Streamlit Cloud, basta con conectar el repositorio y añadir la variable GEMINI_API_KEY en la sección "Advanced settings -> Secrets").*
