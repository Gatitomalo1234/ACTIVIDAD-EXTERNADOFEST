# CHASQUIDO ✦ — `photo_particles.html`

Experiencia interactiva 2026-2 para el Externado Fest, basada en el motor de
partículas del `particle_system.html` original. Nombre e identidad: **CHASQUIDO**
("Conviértete en 40.000 partículas de datos") — referencia directa al chasquido de
Thanos, que es el nombre de la actividad.

**El flujo del evento:** la persona se ve en un espejo gigante (cámara fullscreen) →
toca el obturador → cuenta regresiva 3-2-1 en partículas sobre su reflejo → flash →
su reflejo congelado se desintegra mientras el polvo se condensa formando su foto en
partículas (chasquido inverso) → la contempla / la fotografían para WhatsApp →
botón "💥 Chasquido" (o auto a los 60s) → la foto se deshace en ceniza llevada por
el viento → vuelve el espejo para la siguiente persona. Ciclo completo sin
intervención del staff; si nadie interactúa, el modo vitrina promociona solo.

## Stack
Three.js r128 + UnrealBloomPass por CDN, Web Audio para sonido sintetizado (sin
archivos), `getUserMedia` 1920×1080 16:9 para la cámara. Archivo único, sin build.

## Calidad del espejo (v9) — la cámara y la pantalla al máximo
Tres problemas encontrados al preparar la operación del día del evento:

1. **La cámara pedía 640×480.** Servía cuando el video era una miniatura, pero
   hoy se muestra a pantalla completa: en un monitor grande se veía suave.
   Ahora pide `1920×1080` con `aspectRatio 16/9`. Medido en una M4: sin costo
   de rendimiento (p95 17.2 ms, cero frames lentos).
2. **Lo que se veía NO era lo que salía en la foto.** El espejo usa
   `object-fit: cover` (recorta), pero `capturePhoto()` guardaba el frame
   completo: la foto traía ~33% más de contenido vertical del que la persona
   vio, y quedaba 4:3 con franjas negras en una pantalla 16:9. Ahora
   `getCoverCrop()` calcula el mismo recorte que muestra el espejo y lo
   comparten la captura y el freeze-frame — WYSIWYG en cualquier pantalla.
3. **El "filtro negro con partículas".** La causa real no era el grain: las
   partículas apagadas son negras y, con `AdditiveBlending`, no suman color
   **pero sí suman alpha al canvas**; al componerse sobre el video lo oscurecían
   punto por punto (durante el countdown son ~48k partículas negras encima del
   reflejo). Se corrigió con `CustomBlending`: aditivo en RGB pero
   `blendSrcAlpha = Zero` / `blendDstAlpha = One`, así el canvas nunca acumula
   opacidad y lo apagado es realmente invisible.

Además, el espejo quedó **limpio y brillante** y el grade cinematográfico se
reservó para el countdown: sin grain, viñeta al 25%, tinte al 30% y
`brightness(1.04)` en vez de `0.96`. El polvo ambiente ahora **enmarca**: se
enciende hacia los bordes (`edge²`) y deja el centro libre, donde la persona se
mira la cara.

**Densidad:** con el 16:9 la foto se muestra más grande, así que la trama se
notaba más gruesa. `PARTICLE_COUNT` subió de 40.000 → **60.000** (rejilla
~310×174) tras verificar que el rendimiento no se movía. `CAPTION_COUNT` pasó a
ser proporcional (`PARTICLE_COUNT * 0.15`): al subir la densidad las celdas —y
los puntos— se achican, y con 6.000 fijas el caption se veía ralo. El tagline
del título se genera desde `PARTICLE_COUNT` para que nunca quede desactualizado.

## Máquina de estados

```
mirror ──(obturador)──▶ countdown 3-2-1 ──(auto)──▶ assembling ──(auto)──▶ photo ──(💥 snap / auto 60s)──▶ dissolving ──(auto)──▶ mirror
```

| Estado | Qué se ve | Partículas |
|---|---|---|
| `mirror` | Video en vivo fullscreen espejado + marca + obturador pulsante | Polvo ambiente tenue flotando sobre el video (aditivo; ~22% visibles, resto en negro = invisible). **Vitrina**: tras 45s sin interacción, el polvo escribe "CHASQUIDO" / "TOCA EL BOTON" alternando con dispersión cada 5s; cualquier movimiento del mouse lo dispersa |
| `countdown` | Video en vivo + número gigante en partículas | 12k partículas forman **3 → 2 → 1** (0.9s por dígito, morph rápido lerp 0.09, tick que sube de tono); al terminar → flash + captura |
| `assembling` | **El reflejo congelado del espejo desintegrándose** mientras nace la foto | Al capturar se congela el último frame en un canvas 2D fullscreen (`#freeze-canvas`, cover-fit espejado); una onda de borrado (`destination-out` con borde en gradiente + 60 motas irregulares por frame) lo come de izq→der sincronizada con la onda de armado de las partículas — el reflejo real se convierte en datos sin corte |
| `photo` | Foto en partículas + caption "EXTERNADO FEST / CIENCIA DE DATOS 2026" debajo; el título DOM se oculta; acciones discretas abajo-izquierda (📱 Descargar / ⬇ Guardar / 💥 Chasquido). La subida a Supabase arranca sola en segundo plano | Respiración sutil + shimmer + repulsión 2D del mouse (foto y caption por igual) |
| `dissolving` | La foto se deshace | Cada partícula espera su turno (onda izq→der irregular), deriva con brisa diagonal + turbulencia y se desvanece a negro (~3s) |

La UI se muestra/oculta por estado vía `body[data-state="..."]` en CSS puro.
**Auto-snap**: si nadie pulsa el botón, la foto se chasquea sola a los 60s
(`AUTO_SNAP_AFTER`) — la instalación nunca se queda atascada.

## Grade cinematográfico (estados mirror/countdown)
- `filter: saturate(1.15) contrast(1.07) brightness(0.96)` en el video (y en el
  freeze-canvas, para que el frame congelado coincida).
- **Grain de película**: overlay con ruido SVG (`feTurbulence` en data-URI) al
  5.5% de opacidad, con jitter en `steps(4)` — se apaga fuera del espejo.
- **Tinte morado frío** en los bordes (radial-gradient) + la viñeta existente.

## Texto→partículas (motor unificado)
`rasterizeToPoints(W, H, drawFn)` rasteriza cualquier cosa a puntos con bbox.
Sobre él: `getDigitPoints` (3/2/1, cache), `getAttractPoints` (palabras de la
vitrina, cache) y el caption. `setOverlayTextTargets(pts, useCount, worldW)`
asigna N partículas al texto (gradiente de marca morado→cian) y deja el resto
donde está apagándose (negro = invisible en aditivo).

## Identidad visual
- **Intro cinematográfica** al cargar: pantalla negra → las 9 letras de "CHASQUIDO"
  caen una a una con blur y rebote (stagger `--i` por letra) → tagline → las 6
  gemas → el video del espejo se revela en fade (clase `.ready` al evento
  `playing`, con delay CSS de 1.1s) → esquinas de visor y obturador suben.
  Secuencia total ~2.5s, todo en CSS con `animation-delay`.
- **Tipografía de marca: Unbounded 900** (display expandida futurista, Google
  Fonts) — reemplazó a Inter en el título, los dígitos del countdown y la
  vitrina (se precarga con `document.fonts.load` para que el rasterizador canvas
  la tenga lista). Inter queda para UI/tagline.
- **Paleta del título: oro Thanos** — gradiente metálico vertical
  (#fdf0b0→#f6d36c→#cf9b22→#94660f, el guantelete) con **glow púrpura** detrás
  (drop-shadow rgba(168,85,247,0.5)) y un **destello especular** que barre las
  letras cada 5.5s (capa de gradiente animada con `background-position`,
  escalonada por letra). Los dígitos del countdown y los textos de la vitrina
  usan el mismo oro en partículas (luz→oro profundo de izq→der); el caption bajo
  la foto conserva el morado→cian del fest. Tras la intro las letras ondulan
  suavemente en loop (letterWave escalonada).
- **Las 6 gemas del infinito** bajo el tagline (morado, azul, rojo, naranja,
  verde, amarillo — guiño al guantelete): pulsan desfasadas en loop.
- **Encuadre de visor**: 4 esquinas estilo cámara enmarcan el espejo (solo estado
  mirror, con "respiración") + chip "● EN VIVO" en la esquina superior.
- **Obturador**: botón circular con el emoji 🫰, dos anillos orbitales punteados
  girando en sentidos opuestos, pulso de glow, hover con rotación.
- En el estado foto **el título desaparece** (fade hacia arriba): protagonismo
  total a la obra. Las acciones son dos mini-pills discretas en la esquina
  inferior izquierda: "⬇ Guardar" y "💥 Chasquido" (tiembla al hover).
- **Caption en partículas** (reemplaza el sello DOM plano): 6.000 de las 40.000
  partículas escriben "EXTERNADO FEST / CIENCIA DE DATOS 2026" debajo de la foto,
  con gradiente morado→cian de izquierda a derecha y 6% de destellos blancos.
  Al ser partículas de la escena: se arma en la misma oleada, se desintegra con
  el chasquido, reacciona al mouse, **y sale automáticamente en el PNG guardado
  y en las fotos que la gente tome con el celular**. El texto se rasteriza una
  vez en un canvas offscreen (1200×300, dos líneas) y se cachea
  (`getCaptionPoints`).
- Layout vertical auto-centrado: `PHOTO_WIDTH` bajó a 7.6 y la rejilla usa
  `PARTICLE_COUNT - CAPTION_COUNT` celdas; foto + `CAPTION_GAP` + caption se
  centran como bloque en el viewport (~7.3 de ~7.7 unidades visibles de alto).
- Viñeta sutil sobre el video; fullscreen y FPS discretos.

## Descarga por QR (v10)

Al armarse la foto, la obra se sube sola a Supabase Storage en segundo plano
(con `SHARE_DELAY = 1.2s` para que los colores terminen de asentarse). El botón
"📱 Descargar" queda habilitado cuando la subida termina y abre un **QR grande**
que el invitado escanea con su celular.

**Qué se sube:** un solo archivo, `<uuid>.jpg` (JPEG calidad 0.92, ~1.4 MB a
2940×1846). El branding ya viene dentro de la imagen: el caption de partículas
es parte de la escena.

### ⚠️ Supabase Storage NO puede servir HTML
La primera versión subía también una `<uuid>.html` con la página de descarga.
**No funciona:** Supabase fuerza `content-type: text/plain` + `nosniff` en todo
HTML (protección suya para que nadie hostee páginas en su dominio), así que el
celular mostraría el código fuente en vez de la página. Verificado subiendo con
`text/html`, `application/xhtml+xml` y con extensión `.txt`: los tres vuelven
como `text/plain`. Las imágenes sí se sirven con su tipo correcto.

**Solución:** la página vive en [`foto.html`](foto.html), un archivo aparte para
desplegar en un hosting estático (Netlify, Vercel, GitHub Pages). Se abre con
`?i=<uuid>` y arma la URL pública de la imagen.
- Si `SHARE_LANDING` está configurado → el QR apunta a esa página.
- Si está vacío (por defecto) → el QR apunta **directo a la imagen** y todo
  funciona igual; solo se pierde la página con marca.

`foto.html` valida el parámetro `?i=` contra `/^[a-zA-Z0-9-]{8,64}$/` para que
nadie pueda apuntar la página a otro sitio, y descarga la foto vía `fetch` +
blob (el atributo `download` se ignora entre dominios; el bucket responde con
`access-control-allow-origin: *`, así que la descarga real sí funciona).

**Detalles de implementación:**
- `grabArtwork()` centraliza la copia del canvas WebGL a un canvas 2D (el buffer
  no se conserva entre frames: hay que renderizar y copiar en el mismo tick).
  Lo usan tanto "⬇ Guardar" como la subida.
- Nombres con `crypto.randomUUID()`: la URL no se puede adivinar (son caras).
- Estados del botón: `idle → uploading ("⏳ Preparando…") → ready | error
  ("⚠️ Sin conexión")`. Si no hay internet o falta el bucket, **el resto de la
  experiencia sigue funcionando** y "⬇ Guardar" continúa disponible.
- El auto-snap de 60s **no dispara mientras el QR está abierto**, para no
  interrumpir a alguien escaneando.
- Al volver al espejo se limpia todo (`resetShare()`): sin URLs de la persona
  anterior.

### Proyecto Supabase — verificado funcionando
Proyecto actual: `aohpheppigbqmbfpzpbg` (los tres HTML apuntan ahí). Todo el
setup está en [`../supabase-setup.sql`](../supabase-setup.sql), que es repetible y
crea el bucket por SQL — no hace falta el dashboard.

Verificado end-to-end contra el proyecto real:
- Tabla `leaderboard`: select / insert / update / delete como `anon` ✓
- Bucket `chasquido`: subida como `anon` ✓, lectura pública sin credenciales ✓
- Ciclo completo de CHASQUIDO: foto subida (2940×1846, 1.4 MB) y QR generado ✓
- [`foto.html`](foto.html) con un id real: imagen cargada y descarga vía blob ✓

`anon` tiene solo `insert` en el bucket: no puede listar ni borrar. Por eso el
listado desde el cliente devuelve vacío — es lo esperado, no un error.

### Privacidad (importante)
Son fotos de las caras de los invitados en un bucket público. Los nombres son
UUID aleatorios (no adivinables), pero **conviene vaciar el bucket al terminar
el evento**. Vale la pena avisar en el stand que la foto se sube para poder
descargarla.

**Ojo:** las fotos **no se pueden borrar con SQL**. Supabase lo bloquea con el
trigger `storage.protect_delete` («Direct deletion from storage tables is not
allowed. Use the Storage API instead»), para no dejar archivos huérfanos. Hay
que borrarlas desde el dashboard (Storage → `chasquido` → seleccionar → Delete)
o con la Storage API usando la clave `service_role`. En
[`../supabase-setup.sql`](../supabase-setup.sql) está el comando de borrado en bloque.

### Riesgo operativo: dependencia de internet
La página carga Three.js, las fuentes, supabase-js y el generador de QR desde
CDN, así que **hoy necesita internet para arrancar**, no solo para el QR. Antes
del fest conviene descargar esas librerías junto al HTML y apuntar los `<script>`
a archivos locales: así, si la wifi falla, la experiencia funciona igual y solo
se pierde el QR.

## Envío por WhatsApp a los invitados

**Implementado — botón "⬇ Guardar"** (`savePhotoCard()`): renderiza un frame del
canvas WebGL en el momento (el buffer no se conserva entre frames, por eso se
fuerza el render antes de leerlo), lo compone sobre fondo negro y descarga
`chasquido-YYYY-MM-DD-HH-MM-SS.png` (timestamp = identificar a cada invitado por
hora de paso). El branding va dentro del render: el caption de partículas
"EXTERNADO FEST / CIENCIA DE DATOS 2026" es parte de la escena.

**Flujo operativo del evento (sin backend):**
1. El invitado pasa, se toma la foto, la contempla.
2. El staff pulsa "⬇ Guardar" → PNG con sello queda en la carpeta de descargas.
3. Con **WhatsApp Web abierto en el mismo equipo**, arrastrar el PNG al chat del
   invitado (o a un grupo del evento). El nombre con timestamp permite mapear
   foto↔persona si se anota la hora al pedir el número.

**Alternativa de siguiente nivel (idea para v6):** subir el PNG a **Supabase
Storage** (el fest ya usa Supabase para el leaderboard) y mostrar un **código QR
en pantalla** junto a la foto — el invitado lo escanea y descarga su foto al
instante en su propio celular, sin pedir números ni enviar nada manualmente.
Es la mejor UX para filas grandes: cero fricción y cero datos personales.

## Sonido (Web Audio sintetizado)
- `playSnapSound()`: chasquido — ráfaga de ruido highpass (0.1s) + cuerpo grave
  descendente 320→70Hz. Suena al capturar y al disolver.
- `playWhoosh(dur)`: ruido bandpass con barrido de frecuencia y envolvente — el
  viento del polvo. Acompaña armado y disolución con su duración.
- `playChime()`: dos senos (Do–Sol) suaves al completarse la foto.
- `playTick(pitch)`: blip de triángulo para la cuenta regresiva — sube de tono
  en cada número (600 → 760 → 920 Hz).
- El `AudioContext` se crea en el primer clic (política de autoplay de los browsers).

## Coreografías (todas sobre buffers por partícula)

**Armado (chasquido inverso)** — al capturar:
- `startPositions` = posición actual + offset en la dirección de la brisa
  (arriba-derecha, magnitud 2.5–6) + jitter → el polvo "viene de donde se iría".
- `delays[i]` = posición X normalizada × `ASSEMBLE_SWEEP` + random ×
  `ASSEMBLE_JITTER` → frente de onda irregular estilo película.
- Viaje con easing smoothstep + turbulencia sinusoidal que se apaga al llegar
  (`wob = (1-e) * 0.3`). El color se enciende con la llegada (`cLerp = e * 0.25`).

**Disolución (el chasquido)** — al pulsar Snap:
- `delays[i]` = onda izq→der + jitter; `drift[i]` = brisa (X: 0.9–1.8, Y: 0.5–1.5,
  Z leve) por partícula.
- Cuando le llega el turno: deriva acelerando (`speed = min(age*1.6, 2.8)`) +
  turbulencia, y el color decae a negro en `DISSOLVE_FADE = 1.4s` (negro sobre
  fondo negro = invisible).

## Pipeline de captura (heredado de v3, intacto)
Rejilla uniforme de una celda por partícula → color promedio por celda →
contraste suavizado (percentiles 2–98, `PHOTO_STRETCH = 0.5`) → saturación 1.25 →
sprite cuadrado redondeado, `NormalBlending`, `toneMapped = false`, solape 1.35,
bloom 0.15/0.8. Foto plana (`PHOTO_DEPTH = 0`) porque el objetivo es fotografiarla
y compartirla por WhatsApp; subir a ~0.9 activa el relieve holograma.

## Rendimiento y limpieza (auditoría v8)
- **Generadores sin basura**: `fillDustTargets()` / `fillPhotoTargets()` escriben
  directo en `targets`/`targetColors`. Antes construían un array de 40.000
  objetos con dos arrays anidados cada uno (~120k allocations por llamada) que
  luego se copiaba; la vitrina los llama cada pocos segundos, así que provocaba
  picos de GC. Se eliminó el envoltorio `setTargets(generator)`.
- **Estado fuera del loop**: `appState === '...'` se resolvía hasta 5 veces por
  partícula (200.000 comparaciones de string por frame). Ahora se resuelve una
  vez por frame en booleanos (`stMirror`, `stPhoto`, …), igual que el vaivén
  `swayA` que se recalculaba por partícula.
- **Rasterizado unificado**: `getCaptionPoints()` duplicaba el loop
  pixel-por-pixel; ahora usa `rasterizeToPoints()` como los dígitos y la vitrina.
- **Muerto eliminado**: `@keyframes gradientShift` (huérfano desde el rediseño
  del título a oro). Verificado: cero identificadores JS sin uso, cero selectores
  CSS sin elemento, cero referencias obsoletas.
- **Favicon inline** (data-URI 🫰): elimina el único 404 que quedaba en consola.

### Bug corregido: caption cortado
El bloque foto+caption medía ~7.35 unidades de alto contra ~7.34 visibles, así
que "CIENCIA DE DATOS 2026" se cortaba contra el borde inferior (detectado al
verificar en navegador, nunca se había visto en las pruebas). `fillPhotoTargets`
ahora calcula el área visible desde el FOV y la distancia de cámara y aplica un
`photoFitScale` (con 8% de margen) a todo el bloque; `applyModeVisuals` usa la
celda ya escalada para el tamaño de partícula, y `resize` reencuadra la foto
(importante al entrar/salir de fullscreen en el evento).

### Verificación en navegador
Ciclo completo ejercitado con Chrome DevTools sobre servidor local:
`mirror → countdown (2.7s) → assembling (3.2s) → photo → dissolving → mirror`,
**60–61 FPS estables** con 40.000 partículas y consola sin errores.

## Detalle técnico de render
El `EffectComposer` pinta fondo opaco, así que **solo se usa cuando el video está
oculto** (assembling/photo/dissolving). En los estados `mirror` y `countdown` se
renderiza directo con `renderer.render()` y clear color transparente para que el
video de la cámara se vea detrás de las partículas.

## Constantes ajustables

| Constante | Valor | Efecto |
|---|---|---|
| `PARTICLE_COUNT` | 60000 | Total (51k foto + 9k caption). Verificado a 60 FPS en M4 |
| `PHOTO_WIDTH` | 7.6 | Tamaño base de la foto; el fit-scale lo ajusta a la pantalla |
| `CAPTION_COUNT` / `CAPTION_WIDTH` / `CAPTION_GAP` | 15% del total / 6.0 / 0.35 | Partículas, ancho y separación del caption |
| `PHOTO_STRETCH` / `PHOTO_SATURATION` | 0.5 / 1.25 | Contraste y color |
| `PHOTO_DEPTH` | 0 | 0 = plana (WhatsApp); ~0.9 = holograma |
| `COUNTDOWN_STEP` / `DIGIT_PARTICLES` / `COUNTDOWN_LERP` | 0.9 / 12000 / 0.09 | Ritmo, densidad y morph del 3-2-1 |
| `ATTRACT_IDLE` / `ATTRACT_PHASE` / `ATTRACT_PARTICLES` | 45 / 5 / 14000 | Espera, ciclo y densidad de la vitrina (`ATTRACT_TEXTS` = palabras) |
| `AUTO_SNAP_AFTER` | 60 | s en foto antes del chasquido automático |
| `ASSEMBLE_SWEEP` / `_DURATION` / `_JITTER` | 1.8 / 1.1 / 0.35 | Ritmo del armado |
| `DISSOLVE_SWEEP` / `_FADE` / `_JITTER` | 1.5 / 1.4 / 0.4 | Ritmo del chasquido |
| `BREATH_AMP` | 0.015 | Respiración (bajado de 0.05: causaba trama zigzag en fondos claros) |
| `REPEL_RADIUS` / `_STRENGTH` | 1.1 / 0.6 | Repulsión 2D del mouse |
| `cellSize * 1.35` | (applyModeVisuals) | Solape de los píxeles |

## Historial de versiones
- **v1**: muestreo aleatorio de píxeles + glow aditivo — foto irreconocible.
- **v2**: rejilla uniforme, blending normal, disco sólido, contraste — reconocible
  pero lavada y con trama.
- **v3**: `toneMapped=false`, contraste suavizado, sprite cuadrado, bloom bajo,
  40k partículas — fiel, pero plana y estática como experiencia.
- **v4**: solape 1.35, enderezado al capturar, armado en oleada, respiración,
  shimmer, repulsión (2D), relieve 3D implementado pero apagado.
- **v5**: experiencia CHASQUIDO completa — espejo fullscreen, máquina de
  estados, coreografías de condensación/desintegración estilo Thanos, sonido
  sintetizado, identidad visual inicial.
- **v6**: intro cinematográfica (letras, gemas, revelado del espejo), obturador
  con anillos orbitales, título oculto en estado foto, acciones mini-pill,
  caption en partículas "EXTERNADO FEST / CIENCIA DE DATOS 2026" (reemplaza el
  sello DOM) y botón "⬇ Guardar" con PNG timestampeado.
- **v7**: cuenta regresiva 3-2-1 en partículas, modo vitrina + auto-snap,
  transición continua (freeze-frame que se desintegra con la onda de armado) y
  grade cinematográfico (filtros + grain + tinte).
- **v8**: título en Unbounded 900 con oro Thanos y destello especular;
  auditoría de código — generadores sin allocations, estado hoisted fuera del
  loop, rasterizado unificado, código muerto eliminado, fix del caption cortado
  y verificación end-to-end en navegador.
- **v9**: calidad del espejo para el día del evento — cámara 1080p 16:9,
  captura WYSIWYG con el mismo recorte que se ve, fix del blending que oscurecía
  el video con partículas negras, espejo limpio (grade reservado al countdown),
  polvo que enmarca sin tapar la cara, y densidad a 60k con caption proporcional.
- **v10 (actual)**: descarga por QR — subida automática a Supabase Storage y
  overlay de QR grande con el botón "📱 Descargar". Migración al proyecto
  `aohpheppigbqmbfpzpbg` (los tres HTML del repo) y `foto.html` como página de
  descarga desplegable, porque Supabase no puede servir HTML.

## Pendiente / ideas
- **Escanear el QR con un celular real** — falta la última milla: verificado que
  la URL es pública y descargable, pero no probado desde un teléfono.
- **Desplegar `foto.html`** (Netlify) y poner su URL en `SHARE_LANDING` si se
  quiere la página con marca en vez del enlace directo a la imagen.
- **Borrar las fotos de prueba** del bucket (sección de mantenimiento del SQL).
- **Vendorizar las librerías CDN** antes del evento (Three.js, fuentes,
  supabase-js, qrcode) para no depender de la wifi del venue.
- Galería/descarga de las fotos originales.
- Tecla `H` para ocultar toda la UI (captura de pantalla 100% limpia).

## Cómo probar
```bash
cd "2026-2" && python3 -m http.server 8000
# abrir http://localhost:8000/photo_particles.html
```
Permitir la cámara. Verificación de sintaxis: extraer el script inline y
`node --check`.
