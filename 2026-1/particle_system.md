# Resumen detallado — `particle_system.html`

> **Documento de referencia histórica.** Analiza
> [`particle_system.html`](particle_system.html), la demo original del fest
> 2026-1 y **punto de partida de CHASQUIDO**. Ese archivo se conserva sin
> modificar; la experiencia actual vive en
> [`../2026-2/photo_particles.html`](../2026-2/photo_particles.html) y se
> documenta en [`../2026-2/photo_particles.md`](../2026-2/photo_particles.md).
> Se conserva este análisis porque el motor de partículas (buffers, lerp a
> targets, bloom, texturas) es el mismo, y explica de dónde vienen las
> decisiones de diseño.

Archivo único (HTML + CSS + JS inline), ~1695 líneas. Demo 3D de partículas interactiva
("Particle System Ultra") controlada por gestos de mano, audio del micrófono y mouse.
No depende de build tools: todo se carga vía CDN (`<script src="https://cdn.jsdelivr.net/...">`).

## Librerías externas (CDN, todas en el `<head>`)
- **Three.js r128** — motor 3D (WebGL).
- **Post-processing de Three.js**: `CopyShader`, `LuminosityHighPassShader`, `EffectComposer`,
  `RenderPass`, `ShaderPass`, `UnrealBloomPass` → efecto de *bloom* (glow).
- **MediaPipe Hands** (`@mediapipe/hands`) + **camera_utils** — tracking de manos vía webcam.
- Fuente **Inter** de Google Fonts.

## Estructura visual (HTML/CSS)
- `#canvas-container` → `<canvas id="three-canvas">`: lienzo WebGL a pantalla completa.
- `#fps-badge`: contador de FPS (esquina inferior derecha).
- `#ui-panel`: panel flotante "glassmorphism" (blur, esquina superior izquierda) con:
  - **Shape** (`.shapes-grid`): 4 botones para elegir forma — Logo 🧠, Cloud ☁️ (activo por defecto), Galaxy 🌀, Welcome ✌️.
  - **Color**: `<input type="color">` para tintar las partículas (solo aplica a la forma "cloud").
  - **Audio Reactive**: botón para activar el micrófono + `#audio-bars` (16 barras, visualizador de espectro).
  - **Camera**: preview de la webcam (`#cam-video` + `#cam-overlay` con los landmarks dibujados), badge "LIVE", botón apagar/encender cámara.
  - **Gesture**: indicador de estado (`#gesture-dot` + texto) de qué gesto se detecta.
  - Botones de acción: pausar rotación automática, fullscreen.
- `#toggle-panel`: botón hamburguesa que solo aparece en móvil (`max-width: 600px`) para mostrar/ocultar el panel.

## Configuración global (JS)
```js
const PARTICLE_COUNT = 18000;   // número de partículas
const LERP_SPEED = 0.04;        // velocidad de interpolación posición/color hacia el target
let autoRotate = true;
```

## Setup de Three.js
- `WebGLRenderer` con `antialias`, `alpha`, tone mapping ACES Filmic, `toneMappingExposure = 1.2`.
- `PerspectiveCamera` FOV 75, posicionada en `z = 5`.
- **Bloom** (`setupBloom()`): crea `EffectComposer` con `RenderPass` + `UnrealBloomPass`
  (strength 1.6, radius 0.7, threshold 0.05 → casi todo brilla). Con fallback si Three no expone `EffectComposer`.

## Sistema de partículas (geometría/material)
- Textura circular con glow generada en un `<canvas>` 2D (`createCircleTexture`, gradiente radial) → usada como `map` del `PointsMaterial`.
- `THREE.PointsMaterial`: `size 0.065`, `vertexColors: true`, `AdditiveBlending`, `depthWrite: false`, `sizeAttenuation: true`.
- Buffers `Float32Array` de tamaño `PARTICLE_COUNT * 3`:
  - `positions` / `colors` — estado actual (lo que se renderiza).
  - `velocities` — velocidades físicas (para el efecto vórtice).
  - `targets` / `targetColors` — posición/color objetivo hacia el que se interpola cada frame.
- Inicializado con posiciones aleatorias en un cubo de lado 5 y color morado por defecto (`#c084fc`).

## Generadores de formas (`shapeGenerators`)
Cada uno devuelve un array de `{pos: [x,y,z], col: [r,g,b]}` de tamaño `PARTICLE_COUNT`:

1. **`cloud`** (default): esfera de densidad no uniforme (`r = random^0.7 * 4`), gradiente de color morado (centro) → azul (borde).
2. **`logo`** (`generateLogoPositions`): dibuja en un canvas 2D oculto (1024×1024) un logo compuesto por:
   - Mitad izquierda: un "cerebro" rojo (`#E91E63`) hecho con curvas Bézier + "pliegues" (creases).
   - Mitad derecha: un "circuito" azul (`#00B0FF`) con líneas escalonadas y nodos de colores.
   - Texto "CIENCIA DE DATOS" debajo.
   - Luego samplea los píxeles no transparentes del canvas y asigna partículas aleatoriamente a esos puntos (con su color de origen).
3. **`galaxy`** (`generateGalaxyPositions`): combina un **núcleo** denso (35% de partículas, distribución de potencia, colores blanco/dorado→naranja) y **brazos espirales** (5 brazos, ángulo = `armAngle + r*1.8`, con dispersión creciente según el radio; color pasa de dorado→rosado→púrpura→cian según distancia; 3% de partículas blancas brillantes = "estrellas").
4. **`welcome`** (`generateTextPositions`): renderiza el texto (multilínea) "BIENVENIDOS A LA DEMOSTRACION / Y PRESENTACION DE / CIENCIA DE DATOS" en un canvas, samplea píxeles del texto.
   - 75% de las partículas son el **texto** (con gradiente de color vertical + 12% de "sparkles" dorados), guardadas en `window.particleMetadata` con `type=0`.
   - 25% restante son **6 explosiones tipo fuegos artificiales** alrededor del texto (`type=1`), cada una con velocidad inicial esférica aleatoria, usada luego en el loop de animación para simular gravedad/trayectoria/fade en bucle.

`setTargets(shapeName)` recalcula `targets`/`targetColors` llamando al generador correspondiente.

## Detección de manos y gestos (MediaPipe Hands)
- `calcOpenness(landmarks)`: mide qué tan abierta está la mano comparando distancia punta-muñeca vs. distancia nudillo-muñeca para 5 dedos, normalizado a `[0,1]`.
- `isFingerExtended(landmarks, tip, pip, mcp)`: determina si un dedo está extendido comparando distancias a la muñeca.
- `detectGesture(landmarks)`: clasifica gestos según qué dedos están extendidos:
  - Índice + medio + anular (no meñique) → `three_up` → forma **Galaxy**.
  - Índice + medio (peace ✌️) → `peace` → forma **Welcome**.
  - Solo índice (☝️) → `point` → forma **Logo**.
  - Ninguno de los anteriores → `null`.
- `hands.onResults(...)`: callback principal por frame de cámara.
  - Si hay manos detectadas: dibuja los landmarks (puntos con glow) en `#cam-overlay`.
  - Mano **izquierda** (o única mano): mano de "navegación" — controla `handX/handY` (posición de la palma, landmark 9) y `handRotZ` (rotación Z estimada muñeca→base del dedo medio) y `gestureFactor` (apertura de la mano, usada para el efecto vórtice).
  - Mano **derecha** (o única mano): mano de "comando" — pasa por `detectGesture` para cambiar de forma.
  - Si openness > 0.5 sin gesto especial → `cloud` (vórtice activo); si mano cerrada → `cloud` (sin vórtice).
  - Sin mano detectada → vuelve a `cloud`.
- Cámara gestionada con `Camera` de `camera_utils` (320×240), con botón para pausar/reanudar (`cam-toggle-btn`).

## Audio reactivo (`AudioReactor` class)
- Usa `AudioContext` + `getUserMedia({audio:true})` + `AnalyserNode` (`fftSize=256`, smoothing 0.8).
- Cada frame (`update()`) calcula energía en 3 bandas (`bass`, `mid`, `treble`) a partir de `getByteFrequencyData`, más `energy` combinada y versiones suavizadas (`smoothBass`, `smoothEnergy`).
- También calcula 16 "bins" de frecuencia para el visualizador de barras (`#audio-bars`).
- Afecta: expansión de la nube de partículas, boost de rotación, fuerza del bloom, tamaño de partícula, vibración de posición, y ligero shift de color (excepto en modo "welcome").
- `stop()` cierra el `AudioContext` y resetea valores.

## Loop de animación (`animate()`, corre con `requestAnimationFrame`)
Por cada frame:
1. Actualiza contador de FPS.
2. `audioReactor.update()` y refresca las barras de audio en el DOM.
3. Determina `activeShape` = gesto actual o `'cloud'`; si cambió respecto al frame anterior, llama `setTargets()` y actualiza el botón activo en la UI.
4. Suaviza `gestureFactor` → `smoothGesture` (para apertura de mano) y la posición/rotación de la mano (`smoothHandX/Y`, `smoothHandRotZ`) con interpolación exponencial (inertia distinta si la forma es "logo").
5. Calcula `expansionScale` (cuánto se expande la figura) en función de `smoothGesture` y bajos de audio.
6. Auto-rotación: velocidad distinta según la forma (logo gira más rápido, galaxy más lento), más un pequeño boost por audio.
7. Parámetros de **vórtice** (activo cuando hay mano detectada y `smoothGesture > 0.3`): fuerza tangencial alrededor del eje Y, atracción radial leve, fricción `0.92`.
8. Ajusta `bloomPass.strength` según los graves de audio.
9. **Loop principal por partícula** (`for i < PARTICLE_COUNT`):
   - Calcula target de posición/color con `expansionScale`.
   - Si es forma "welcome": aplica lógica especial por `particleMetadata` — partículas de texto (`type 0`) reciben shift de color tipo onda; partículas de fuegos artificiales (`type 1`) siguen una trayectoria parabólica con gravedad, drag, y fade cíclico (loop de 3.5s).
   - Si es "galaxy": aplica rotación orbital por partícula (más rápida cerca del centro).
   - Modulación de color por audio (excepto en welcome).
   - Física de vórtice: fuerza tangencial + radial aplicada a `velocities`, con fricción.
   - Vibración de posición si audio activo.
   - Actualiza `pos[]` con lerp hacia target + velocidad, y `col[]` con lerp de color (usando `LERP_SPEED = 0.04`).
10. Marca `needsUpdate` en los atributos de geometría.
11. Actualiza rotación de la escena según la forma activa (welcome/galaxy/otras tienen lógica distinta) y aplica `smoothHandX/Y` como traslación.
12. Ajusta `material.size` según gesto + audio.
13. Renderiza con `composer.render()` (bloom) o `renderer.render()` como fallback.

## Interacciones UI adicionales
- Botones de forma: click manual también cambia `currentShape`/`lastGestureShape` y llama `setTargets`.
- Color picker: solo re-tiñe si la forma actual es `cloud` (no afecta logo/welcome/galaxy, que tienen colores propios).
- Botón de audio: activa/desactiva `AudioReactor`.
- Botón de pausa: alterna `autoRotate`.
- Botón fullscreen: `requestFullscreen()` / `exitFullscreen()`.
- Orbit con mouse: arrastrar (`pointerdown/move/up`) acumula `mouseX/mouseY` que se suaviza hacia `rotX/rotY`.
- Resize: reajusta cámara, renderer y composer.

## Puntos relevantes para modificar
- **Rendimiento**: `PARTICLE_COUNT = 18000` es el principal cuello de botella (loop por partícula en CPU cada frame, sin GPU shaders para la física). Bajar este número o mover la física a un `ShaderMaterial`/`GPGPU` sería la vía más directa para optimizar.
- **Agregar una forma nueva**: crear una función `generateXPositions(count)` que devuelva `{pos, col}[]`, registrarla en `shapeGenerators`, y añadir un botón `.shape-btn[data-shape="x"]` en el HTML (opcionalmente un gesto en `detectGesture`).
- **Gestos**: la lógica vive en `detectGesture` + el bloque `hands.onResults`; añadir gestos nuevos implica extender `isFingerExtended` combos y el `if/else` de asignación de `gestureShape`.
- **Todo el estado de "welcome"/fireworks** depende de `window.particleMetadata` (variable global fuera del scope normal) — cualquier cambio en `PARTICLE_COUNT` o en `generateTextPositions` debe mantener la sincronía de tamaño (`count * 5` floats).
- No hay conexión a Supabase ni backend en este archivo — es 100% standalone/frontend, a diferencia de `../2026-1/neon_maze.html` y `../2026-1/leaderboard.html`.
