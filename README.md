# 🪐 Data Mastery Externado | Actividad Externado Fest v15.2

![Data Mastery Dashboard](https://supabase.com/dashboard/project/ddoiufkgisillaovdmty/overview) *Nota: Link representativo al backend*

Bienvenido a **Data Mastery Externado**, una experiencia inmersiva de rastreo manual diseñada como herramienta de reclutamiento aspiracional para la carrera de **Ciencia de Datos** de la **Universidad Externado de Colombia**.

## 🚀 Misión del Proyecto
Transformar un juego de habilidad técnica en una vitrina tecnológica que demuestre el poder de la **Ciencia de Datos, la Inteligencia Artificial y la Sincronización en Tiempo Real**.

---

## 🛠️ Stack Tecnológico (v15.2)

### 🎨 Frontend & UX
*   **Vanilla JavaScript (ES6+)**: Lógica pura de alto rendimiento sin frameworks pesados.
*   **Canvas API**: Renderizado de 60 FPS para efectos visuales complejos.
*   **Estética Cyber-Glass**: Interfaz basada en *Glassmorphism* con gradientes animados y desenfoques gaussianos.

### 🦾 Motor de Rastreo (Ultra-Smooth Engine)
*   **MediaPipe Hands**: Engine de visión artificial para la detección de landmarks de la mano.
*   **1 Euro Filter**: Implementación de un filtro adaptativo de baja latencia que elimina el ruido (jitter) en el tracking, proporcionando una suavidad de nivel profesional.
*   **IA de Predicción de Trayectoria**: Visualización proyectada basada en vectores de velocidad para asistir al jugador.

### ☁️ Infraestructura de Datos (Cloud Sync)
*   **Supabase (PostgreSQL)**: Servidor en la nube para persistencia de datos distribuida.
*   **Real-time Subscriptions**: Sincronización instantánea mediante WebSockets para actualizar el tablero de líderes global sin refrescar la página.

### 🔊 Audio Producido por Software (Native SFX)
*   **Web Audio API**: Sintetizador nativo que genera sonidos reactivos (colisiones, grab, victoria) sin necesidad de cargar archivos de audio externos.

---

## 📂 Estructura de Archivos
*   `neon_maze.html`: El núcleo del juego. Contiene el motor de física, tracking y sincronización de nube.
*   `leaderboard.html`: Dashboard central diseñado para proyectarse en pantallas grandes. Muestra el Top 10 de tiempos en tiempo real.
*   `.gitignore`: Exclusión de archivos innecesarios.

---

## 🏆 Hall of Fame & Admin Tools
El sistema incluye un tablero de líderes sincronizado. Los administradores pueden limpiar la base de datos directamente desde el dashboard (`leaderboard.html`) usando el botón **"Borrar Todo (Admin)"** situado en la esquina inferior derecha.

---

## ⚡ Instalación y Despliegue
1.  **Clonar el repositorio**: `git clone [url-repo]`
2.  **Configurar Supabase**: Crear una tabla `leaderboard` con los campos `name` (text) y `time_seconds` (float).
3.  **Despliegue**: Compatible con cualquier servidor estático (Netlify recomendado). Simplemente arrastra la carpeta del proyecto.

---

**Desarrollado para el Externado Fest por Nicolás y Antigravity (IA).** 
*CIENCIA DE DATOS | EXTERNADO DE COLOMBIA* 🪐💎🚀🥈✨
