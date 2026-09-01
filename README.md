# 🪐 Data Mastery Externado | Externado Fest

Experiencias interactivas diseñadas como herramienta de reclutamiento aspiracional
para la carrera de **Ciencia de Datos** de la **Universidad Externado de Colombia**.

## 🚀 Misión del Proyecto
Transformar la tecnología en una vitrina: demostrar el poder de la **Ciencia de
Datos, la Inteligencia Artificial y la Sincronización en Tiempo Real** con
experiencias que la gente quiera vivir y compartir.

---

## 🎪 Las dos actividades

### 1️⃣ Laberinto — Data Mastery ([`2026-1/`](2026-1/))
Juego de habilidad: arrastra una esfera por un laberinto **con el dedo índice**,
detectado por la cámara. Los tiempos se sincronizan en vivo a un tablero de
líderes proyectado en pantalla grande.

*   [`2026-1/neon_maze.html`](2026-1/neon_maze.html) — el juego. Motor de física,
    tracking de mano y escritura a la nube.
*   [`2026-1/leaderboard.html`](2026-1/leaderboard.html) — tablero para
    proyectar. Top de tiempos actualizado en tiempo real vía WebSockets, con
    herramientas de admin (borrar todo, exportar a Excel).
*   [`2026-1/README.md`](2026-1/README.md) — detalle de la actividad.

### 2️⃣ CHASQUIDO ([`2026-2/`](2026-2/))
Cabina de fotos con partículas: la persona se ve en un **espejo gigante**, toca
el obturador, una cuenta regresiva 3-2-1 se forma en partículas sobre su reflejo,
y su foto se **reconstruye con 60.000 partículas** al estilo del chasquido de
Thanos. Al final puede llevarse su foto escaneando un QR.

*   [`2026-2/photo_particles.html`](2026-2/photo_particles.html) — la experiencia
    completa.
*   [`2026-2/foto.html`](2026-2/foto.html) — página de descarga a la que apunta
    el QR (se despliega aparte; ver su documentación).
*   [`2026-2/photo_particles.md`](2026-2/photo_particles.md) — **documentación
    detallada**: máquina de estados, coreografías, constantes ajustables e
    historial de versiones.

---

## 🛠️ Stack Tecnológico

### 🎨 Frontend & UX
*   **Vanilla JavaScript (ES6+)**: sin frameworks, alto rendimiento.
*   **Canvas API / Three.js**: renderizado a 60 FPS.
*   **Estética Cyber-Glass**: glassmorphism, gradientes animados y desenfoques.

### 🦾 Visión por Computador
*   **MediaPipe Hands**: detección de landmarks de la mano (laberinto).
*   **1 Euro Filter**: filtro adaptativo de baja latencia que elimina el jitter
    del tracking.
*   **Muestreo de imagen a rejilla**: la foto de CHASQUIDO se convierte en una
    celda por partícula con color promediado.

### ☁️ Infraestructura de Datos
*   **Supabase (PostgreSQL)**: persistencia del tablero de líderes.
*   **Real-time Subscriptions**: el tablero se actualiza sin refrescar.
*   **Supabase Storage**: alojamiento de las fotos de CHASQUIDO para el QR.

### 🔊 Audio por Software
*   **Web Audio API**: todos los sonidos se sintetizan en el navegador
    (chasquido, whoosh, ticks, colisiones) — cero archivos de audio.

---

## 📂 Estructura de Archivos

```
├── README.md
├── supabase-setup.sql        Setup de la BD — compartido por ambas actividades
├── 2026-1/                   Primera edición
│   ├── README.md             Detalle de la actividad
│   ├── neon_maze.html        Juego del laberinto
│   ├── leaderboard.html      Tablero de líderes para proyectar
│   ├── particle_system.html  Sistema de partículas original (base de CHASQUIDO)
│   ├── particle_system.md    Análisis técnico del anterior
│   └── main.py               Prototipo del laberinto en Python (ver su README)
└── 2026-2/                   Segunda edición
    ├── photo_particles.html  CHASQUIDO — la experiencia
    ├── foto.html             Página de descarga del QR (desplegar aparte)
    ├── photo_particles.md    Documentación técnica de CHASQUIDO
    └── vendor/               Three.js, supabase-js, qrcode y fuentes
                               vendorizados (arranca sin depender del wifi
                               del venue; ver vendor/README.md)
```

Cada carpeta es autónoma: los HTML no dependen de rutas relativas, así que se
pueden abrir o desplegar por separado. Lo único compartido es la base de datos.

---

## ⚡ Instalación y Despliegue

1.  **Clonar el repositorio**: `git clone [url-repo]`

2.  **Configurar Supabase**: correr
    [`supabase-setup.sql`](supabase-setup.sql) completo en el SQL Editor del
    proyecto. Crea la tabla `leaderboard` con sus permisos, **activa Realtime**
    (sin esto el tablero no se actualiza solo) y crea el bucket de fotos. Es
    repetible: se puede volver a correr sin romper nada.

3.  **Credenciales**: la URL del proyecto y la clave publicable van en los tres
    HTML (`neon_maze`, `leaderboard`, `photo_particles`). Son claves de cliente,
    seguras de exponer; **nunca** poner ahí la `service_role`.

4.  **Servir por HTTP**: las páginas usan la cámara, así que necesitan `https://`
    o `localhost` (abrirlas con doble clic desde `file://` puede fallar):
    ```bash
    python3 -m http.server 8000
    # http://localhost:8000/2026-1/neon_maze.html
    # http://localhost:8000/2026-2/photo_particles.html
    ```

5.  **Despliegue**: compatible con cualquier hosting estático (Netlify
    recomendado).

---

## 🏆 Herramientas de Admin
El tablero (`leaderboard.html`) permite **exportar a Excel** y **borrar todo**
desde los botones de las esquinas inferiores. Ojo: ese borrado no pide
autenticación, cualquiera con la página puede vaciar el tablero — aceptable para
un evento controlado.

## 🔒 Privacidad
CHASQUIDO sube las fotos de los invitados a un bucket público con nombres
aleatorios no adivinables. **Vaciar el bucket al terminar el evento** (ver la
sección de mantenimiento en `supabase-setup.sql`).

---

**Desarrollado para el Externado Fest por Nicolás.**
*CIENCIA DE DATOS | EXTERNADO DE COLOMBIA* 🪐💎🚀🥈✨
