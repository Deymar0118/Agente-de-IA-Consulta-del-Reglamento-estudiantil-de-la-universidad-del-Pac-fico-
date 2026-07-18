# 🎓 Agente de IA - Consulta del Reglamento Estudiantil

Este proyecto es un Agente de Inteligencia Artificial desarrollado para facilitar la consulta del **Reglamento Estudiantil de la Universidad del Pacífico**. Permite a estudiantes, docentes y personal administrativo hacer preguntas en lenguaje natural y obtener respuestas precisas basadas estrictamente en el documento oficial.

---

## 🏗️ Arquitectura del Proyecto

El proyecto está diseñado bajo el patrón **RAG (Retrieval-Augmented Generation)** y una arquitectura de capas separadas (Cliente-Servidor interno), garantizando modularidad y escalabilidad.

1. **Capa de Lógica (Backend):** Utiliza `LangChain` y `Google Gemini (gemini-flash-latest)`.
   - **Recuperación (Retrieval):** Se extrae la base de conocimiento local (el PDF del reglamento) mediante `PyPDFLoader`.
   - **Aumento (Augmentation):** El texto del reglamento y el historial de la conversación se inyectan en el prompt del modelo para darle contexto y memoria a corto plazo.
   - **Generación (Generation):** Gemini procesa la información y genera una respuesta limpia usando `StrOutputParser`.
2. **Capa de Presentación (Frontend):** Construida con `Streamlit`, ofrece una interfaz web minimalista e interactiva (tipo chat) separada de la lógica de negocio, adaptada a la identidad visual de la universidad.

---

## 💬 Ejemplos de Uso

El agente es capaz de responder preguntas complejas y mantener el contexto de la conversación. Aquí tienes algunos ejemplos de interacciones:

> **👤 Usuario:** ¿Cuáles son los deberes de los estudiantes?
> **🤖 Asistente:** Según el Capítulo IX del reglamento, los deberes incluyen: respetar a la comunidad universitaria, cumplir los estatutos, cuidar los bienes materiales de la institución y mantener un buen rendimiento académico.

> **👤 Usuario:** ¿Y qué pasa si incumplo el tercero? *(Ejemplo de memoria conversacional)*
> **🤖 Asistente:** Si dañas o atentas contra los bienes materiales de la institución (el tercer deber mencionado), se considera una falta grave según el Capítulo XIV. Esto puede acarrear sanciones disciplinarias que van desde una amonestación pública hasta la expulsión, dependiendo de la gravedad del daño.

> **👤 Usuario:** ¿Quién ganó el mundial de 2018?
> **🤖 Asistente:** Lo siento, no encuentro información sobre eso en el reglamento oficial.

---

## 🚀 Instalación y Ejecución Local

Si deseas ejecutar este proyecto en tu propia computadora, sigue estos pasos:

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
Crea un archivo llamado `.env` en la raíz del proyecto y añade tu clave de acceso de Google Gemini:
```env
GEMINI_API_KEY=tu_api_key_aqui
```
*(Nota: Nunca compartas este archivo públicamente).*

### 4. Iniciar la aplicación
Ejecuta el servidor web local con Streamlit:
```bash
streamlit run src/app.py
```
El navegador se abrirá automáticamente en `http://localhost:8501`.

---

## ☁️ Despliegue en la Nube (Oracle Cloud - OCI)

El proyecto se encuentra desplegado y accesible públicamente a través de Oracle Cloud Infrastructure (OCI).

🔗 **Enlace de la aplicación en vivo:** `[ENLACE_PENDIENTE_DE_ORACLE]`
