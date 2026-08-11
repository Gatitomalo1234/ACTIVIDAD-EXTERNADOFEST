# 🌀 Externado Fest 2026-1 — Data Mastery

Actividades de la primera edición. Todo son archivos HTML autónomos: se abren
en el navegador sin build ni instalación (las librerías vienen de CDN).

---

## 🎮 El laberinto

La actividad principal: arrastrar una esfera por un laberinto **con el dedo
índice**, detectado por la cámara. Al llegar a la meta el tiempo se registra en
la nube y aparece al instante en el tablero.

### [`neon_maze.html`](neon_maze.html) — el juego
Motor de física y colisiones, tracking de mano con **MediaPipe Hands**, y un
**1 Euro Filter** que elimina el jitter del tracking para que el movimiento se
sienta suave. Al ganar escribe el tiempo en la tabla `leaderboard` de Supabase
(si el jugador ya existe, solo actualiza cuando mejora su récord).

### [`leaderboard.html`](leaderboard.html) — el tablero
Pensado para proyectar en pantalla grande. Muestra podio, estadísticas
(participantes, mejor tiempo, promedio) y la tabla completa. Se actualiza **en
tiempo real** por WebSockets: no hay que refrescar cuando alguien termina una
partida.

Botones de admin en las esquinas inferiores:
- **Borrar Todo** — vacía el tablero.
- **Cerrar Grupo** — exporta a Excel y luego vacía.

> ⚠️ Esos botones no piden autenticación: cualquiera con la página puede vaciar
> el tablero. Aceptable en un evento controlado, pero conviene no dejar la URL
> circulando.

---

## ✨ El sistema de partículas

### [`particle_system.html`](particle_system.html)
Demo 3D de 18.000 partículas que se reorganizan en cuatro formas (nube, logo de
Ciencia de Datos, galaxia y un texto de bienvenida), controlada por **gestos de
mano** y reactiva al **audio del micrófono**.

Es el **punto de partida de CHASQUIDO** (fest 2026-2): su motor de partículas
—buffers, interpolación hacia targets, bloom, texturas— es el mismo que usa la
experiencia nueva. Está documentado en detalle en
[`particle_system.md`](particle_system.md).

---

## 🐍 El prototipo

### [`main.py`](main.py)
Versión de escritorio del laberinto (OpenCV + MediaPipe) que precedió a la web.
Se conserva como referencia histórica.

**No corre tal cual**: necesita el modelo `hand_landmarker.task`, que no está en
el repo. Hay que descargarlo de la documentación de MediaPipe y ponerlo en esta
carpeta. Dependencias: `opencv-python`, `mediapipe`, `numpy`.

---

## ▶️ Cómo ejecutar

Las páginas usan la cámara, así que necesitan `https://` o `localhost` — abrirlas
con doble clic (`file://`) puede fallar:

```bash
# desde la raíz del repo
python3 -m http.server 8000
# luego abrir http://localhost:8000/2026-1/neon_maze.html
```

La base de datos se configura con
[`../supabase-setup.sql`](../supabase-setup.sql) (crea la tabla `leaderboard`,
sus permisos y **activa Realtime**, sin lo cual el tablero no se actualiza solo).
Las credenciales van dentro de cada HTML.
