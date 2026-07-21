# Agente de IA - Consulta del Reglamento Estudiantil de la Universidad del Pacífico

Este proyecto es un Agente de Inteligencia Artificial desarrollado para facilitar la consulta del Reglamento Estudiantil de la Universidad del Pacífico. Permite a estudiantes, docentes y personal administrativo hacer preguntas en lenguaje natural y obtener respuestas precisas basadas estrictamente en el documento oficial.

---

## Arquitectura del Proyecto

El proyecto está diseñado bajo el patrón RAG (Retrieval-Augmented Generation) y una arquitectura de capas separadas.

1. **Capa de Lógica (Backend):** Utiliza LangChain y Google Gemini (`gemini-flash-latest`).
   - **Recuperación (Retrieval):** Se extrae la base de conocimiento local (el PDF del reglamento) mediante `PyPDFLoader` e indexación en FAISS.
   - **Aumento (Augmentation):** El texto del reglamento y el historial de la conversación se inyectan en el prompt del modelo para darle contexto y memoria a corto plazo.
   - **Generación (Generation):** Gemini procesa la información y genera una respuesta limpia usando `StrOutputParser`.
2. **Capa de Presentación (Frontend):** Construida con Streamlit, ofrece una interfaz web minimalista e interactiva (tipo chat) separada de la lógica de negocio, adaptada a la identidad visual de la universidad.

---

## Tecnologías y Herramientas Utilizadas

- **Lenguaje:** Python 3.10+
- **Framework RAG:** LangChain
- **Modelo de Lenguaje (LLM):** Google Gemini (`gemini-flash-latest`)
- **Base de Datos Vectorial:** FAISS (Facebook AI Similarity Search)
- **Embeddings:** Google Generative AI Embeddings (`embedding-001`)
- **Procesamiento de Documentos:** PyPDFLoader
- **Interfaz Web:** Streamlit
- **Gestión de Entorno:** `python-dotenv`

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
Crea un archivo llamado `.env` en la raíz del proyecto y añade tu clave de acceso de Google Gemini:
```env
GEMINI_API_KEY=tu_api_key_aqui
```

### 4. Iniciar la aplicación
Ejecuta el servidor web local con Streamlit:
```bash
streamlit run src/app.py
```
El navegador se abrirá automáticamente en `http://localhost:8501`.

---

## Ejemplos de Preguntas y Respuestas del Agente

A continuación se presentan ejemplos reales de consultas que el agente puede responder basándose estrictamente en el Reglamento Estudiantil de la Universidad del Pacífico (Acuerdo No. 029 de 2006):

### Ejemplo 1
- **Pregunta:** ¿Cuáles son los tipos de matrícula que contempla el reglamento de la universidad?
- **Respuesta generada por el agente:** Basado en el reglamento proporcionado, la matrícula se clasifica de las siguientes maneras:

1. Según el plazo en que se realiza (Artículo 15):

Matrícula ordinaria: Es aquella que se realiza dentro de los plazos fijados por la Universidad para tal efecto.
Matrícula extraordinaria: Es la que se realiza de forma extemporánea en el plazo adicional que otorga la Universidad.
2. Según la situación académica del estudiante (Artículo 16):

Inicial: Se otorga a los aspirantes que empiezan un programa académico de pregrado o postgrado.
De renovación: Se otorga a quienes continúan cursando el plan de estudios a partir del segundo semestre sin interrupción.
De reintegro: Se aplica cuando un estudiante vuelve después de haber interrumpido los estudios.
Condicional: Se otorga a un estudiante que ha sido sancionado disciplinariamente luego del respectivo proceso.
📄 Fuentes: Reglamento Estudiantil (Pág. 3, 4, 6, 18)

### Ejemplo 2
- **Pregunta:** ¿Cuál es la nota mínima requerida para aprobar una asignatura en la universidad?
- **Respuesta generada por el agente:** De acuerdo con el Artículo 62 del reglamento proporcionado, la calificación mínima requerida para considerar aprobada una asignatura en los programas académicos de pregrado es de sesenta puntos (60) o superior.

Toda calificación inferior a esta se considera como asignatura reprobada.

📄 Fuentes: Reglamento Estudiantil (Pág. 25, 26, 28)

### Ejemplo 3
- **Pregunta:** ¿Cuáles son los requisitos y el procedimiento para solicitar la cancelación o reserva de matrícula?
- **Respuesta generada por el agente:** 1. Cancelación Total de la Matrícula Académica (Dentro del plazo ordinario)
Plazo máximo: Se puede solicitar hasta la décima (10°) semana del período académico vigente.
Procedimiento y Requisitos:
Debe ser por decisión voluntaria del estudiante y comunicarse por escrito.
Debe contar con el visto bueno (visado) del Director del Programa Académico.
Se debe acompañar de los paz y salvos respectivos y del carné estudiantil.
2. Cancelación Extemporánea de la Matrícula Académica (Fuera del plazo)
Plazo: Después de vencida la décima semana, siempre y cuando no se haya efectuado la evaluación final de las asignaturas.
Requisitos: Solo podrá ser autorizada por el Comité Académico por razones justificadas de:
Calamidad doméstica.
Fuerza mayor o caso fortuito.
Enfermedad comprobada y certificada.
Costo: Esta cancelación extemporánea genera un costo económico equivalente al 10% de un SMMLV (Salario Mínimo Mensual Legal Vigente).
3. Desistimiento de la Matrícula Inicial (Antes de iniciar clases)
Requisitos: Si el estudiante tiene matrícula inicial y desiste de iniciar estudios por calamidad o fuerza mayor, debe informarlo por escrito a la Oficina de Registro y Control Académico con anterioridad al inicio del período académico.
Nota: Con respecto a la reserva de matrícula, el fragmento del reglamento provisto no contiene información específica sobre este trámite.

📄 Fuentes: Reglamento Estudiantil (Pág. 5, 6, 14)

---

## Despliegue en la Nube

Como alternativa a la infraestructura en la nube tradicional, este proyecto ha sido desplegado utilizando Streamlit Community Cloud debido a las siguientes ventajas:
1. Integración nativa y optimizada para aplicaciones Streamlit.
2. Despliegue continuo y automático (CI/CD) directamente conectado con el repositorio de GitHub.
3. Infraestructura gestionada sin necesidad de configuración manual de servidores o puertos.

*(Para configurar el despliegue en Streamlit Cloud, conecta el repositorio y añade la variable `GEMINI_API_KEY` en la sección "Advanced settings -> Secrets").*




## Captura del funcionamiento del agente


