# ✦ EXTERNADO FEST — Experiencias de Datos Interactivos ✦

Repositorio oficial para las actividades interactivas del **Externado Fest**, enfocado en la interacción humano-computadora (HCI) mediante Inteligencia Artificial y Visión Artificial.

---

## 🕹️ Proyectos Incluidos

### 1. Neon Hand-Maze (Laberinto Neon) — [v10.2 Estable] 🪐🛡️
Un laberinto de precisión controlado totalmente por la punta del dedo índice derecho. Es la actividad principal de rapidez y pulso.

- **Motor de IA**: MediaPipe Legacy Resilience Engine (v10.2).
- **Control**: Seguimiento de la punta del dedo índice con **Adaptive Smoothing** (Cero temblor).
- **Evolución**: 5 niveles de dificultad progresiva con diseño *Neon-Glassmorphism*.
- **Compatibilidad**: 100% compatible con `file://` (doble clic) y `http://localhost`. No requiere configuración previa.

### 2. 3D Particle System (Hand Gesture Control) 🧠✨
Un sistema de 15,000 partículas en 3D que responden a gestos complejos de ambas manos.

- **Tecnología**: Three.js + MediaPipe Hands SDK.
- **Gestos**: ✌️ Peace (Bienvenida), 👌 OK (Logo CD), 🤏 Zoom, 🖐️ Expandir.
- **Formas**: 🧠 Cerebro 2.5D, 🧬 ADN, 🌌 Galaxia, ⚛️ Saturno, ❤️ Corazón y Logos Corporativos de alta fidelidad.

---

## 🚀 Cómo Ejecutar

Para garantizar el mejor rendimiento durante el evento, sigue estos pasos:

1. **Localhost (Recomendado)**:
   - Abre una terminal en la carpeta del proyecto.
   - Ejecuta: `python3 -m http.server`
   - Abre en Google Chrome: `http://localhost:8000/neon_maze.html`
2. **Doble Clic (Protocolo de Archivo)**:
   - Gracias al **Motor de Resiliencia v10.2**, el laberinto ahora funciona perfectamente abriendo el archivo directamente (`neon_maze.html`) en Chrome sin necesidad de servidores.

---

## ⚙️ Innovación Técnica (v10.2)

- **Adaptive Smoothing**: El puntero ignora ruidos de cámara cuando dejas la mano quieta, pero es ultra-reactivo al movimiento rápido mediante una función de interpolación dinámica.
- **Auto-Fallback Engine**: El sistema detecta bloqueos de GPU o restricciones de protocolo y conmuta automáticamente entre modos de renderizado para asegurar que la actividad nunca se detenga.
- **Performance de Baja Latencia**: Optimizado para funcionar en laptops de gama media con alta tasa de refresco en el tracking de manos.

---

## 📝 Changelog Reciente

- **v10.2** — **Estabilidad Final**: Implementación de Adaptive Smoothing y rediseño de niveles para balancear dificultad.
- **v10.0** — **Legacy Resilience Upgrade**: Cambio a arquitectura UMD para 100% de compatibilidad en entornos sin servidor.
- **v8.8** — Globalización de estados y diagnóstico proactivo de errores de seguridad (CORS).
- **v4.6** — Roles Estrictos por Mano en Sistema de Partículas (Izquierda: Zoom, Derecha: Gestos).

---

**EXTERNADO FEST | Ciencia de Datos | 2026**
