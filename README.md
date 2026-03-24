# TeVi 👀 - Conexiones Universitarias

**TeVi** es una aplicación web social diseñada exclusivamente para estudiantes universitarios. Su objetivo es facilitar la conexión entre personas de la misma comunidad educativa mediante un sistema de perfiles, matches y chat en tiempo real, similar a aplicaciones de citas pero enfocado en el entorno académico.

## 🚀 Características Principales

*   **Autenticación Segura**: Registro y Login exclusivo para correos institucionales (`.edu.co`).
*   **Perfiles Completos**: Carga de fotos, detección de ubicación, carrera, facultad e intereses.
*   **Sistema de Match**: 
    *   Dar "Like" (Me miró) o "Dislike" (No).
    *   Notificaciones visuales (Globos y Toast) al hacer Match.
    *   Los perfiles descartados no vuelven a aparecer.
*   **Chat en Tiempo Real**:
    *   Interfaz moderna estilo WhatsApp/Messenger.
    *   Lista de contactos y sala de chat dedicada.
    *   Soporte para fotos de perfil en los mensajes.
*   **Diseño Moderno**: Interfaz "Dark Mode" con acentos en Rojo Amor, botones estilizados y totalmente responsiva.

## 🛠️ Tecnologías Utilizadas

*   **Python**: Lenguaje principal.
*   **Streamlit**: Framework para la interfaz web interactiva.
*   **SQLite**: Base de datos local para usuarios, likes, matches y mensajes.
*   **Bcrypt**: Encriptación segura de contraseñas.
*   **CSS Personalizado**: Estilos avanzados para tarjetas, chat y botones.

## 📦 Requisitos e Instalación

Para ejecutar este proyecto en tu computadora, necesitas tener instalado **Python** (versión 3.8 o superior).

### 1. Clonar o Descargar el proyecto
Asegúrate de tener todos los archivos (`app.py`, `style.css`) en una carpeta.

### 2. Instalar Dependencias
Abre tu terminal o línea de comandos (CMD/PowerShell) en la carpeta del proyecto y ejecuta el siguiente comando para instalar las librerías necesarias:

```bash
pip install streamlit bcrypt email-validator
```

*   `streamlit`: Ejecuta la aplicación web.
*   `bcrypt`: Protege las contraseñas de los usuarios.
*   `email-validator`: Verifica que los correos sean válidos y existan.

### 3. Ejecutar la Aplicación
Una vez instaladas las dependencias, inicia la aplicación con el siguiente comando:

```bash
streamlit run app.py
```

Automáticamente se abrirá una pestaña en tu navegador (usualmente en `http://localhost:8501`) donde podrás usar la aplicación.

## 📂 Estructura del Proyecto

*   `app.py`: Archivo principal que contiene toda la lógica (Login, Base de Datos, Chat, Match).
*   `style.css`: Hoja de estilos para personalizar la apariencia (colores, bordes, fuentes).
*   `tevi.db`: (Se crea automáticamente) Archivo de base de datos local.
*   `uploads/`: (Se crea automáticamente) Carpeta donde se guardan las fotos de perfil de los usuarios.

---
Desarrollado para conectar la comunidad universitaria. ❤️
```

<!--
[PROMPT_SUGGESTION]¿Cómo puedo desplegar esta aplicación en Streamlit Cloud para que otros la usen desde internet?[/PROMPT_SUGGESTION]
[PROMPT_SUGGESTION]¿Cómo puedo agregar una función para reportar usuarios por comportamiento inadecuado?[/PROMPT_SUGGESTION]

