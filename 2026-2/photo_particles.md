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
mirror ──(obturador)──▶ countdown 3-2-1 ──(auto)──▶ assembling ──(auto)──▶ photo ──(💥 chasquido)──▶ dissolving ──(auto)──▶ mirror
```

| Estado | Qué se ve | Partículas |
|---|---|---|
| `mirror` | Video en vivo fullscreen espejado + marca + obturador pulsante | Polvo ambiente tenue flotando sobre el video (aditivo; ~22% visibles, resto en negro = invisible). **Vitrina**: tras 45s sin interacción, el polvo escribe "CHASQUIDO" / "TOCA EL BOTON" alternando con dispersión cada 5s; cualquier movimiento del mouse lo dispersa |
| `countdown` | Video en vivo + número gigante en partículas | 12k partículas forman **3 → 2 → 1** (0.9s por dígito, morph rápido lerp 0.09, tick que sube de tono); al terminar → flash + captura |
| `assembling` | **El reflejo congelado del espejo desintegrándose** mientras nace la foto | Al capturar se congela el último frame en un canvas 2D fullscreen (`#freeze-canvas`, cover-fit espejado); una onda de borrado (`destination-out` con borde en gradiente + 60 motas irregulares por frame) lo come de izq→der sincronizada con la onda de armado de las partículas — el reflejo real se convierte en datos sin corte |
| `photo` | Foto en partículas + logo del departamento a cada lado + caption "EXTERNADO FEST / CIENCIA DE DATOS 2026" debajo; el título DOM se oculta; botón circular abajo-izquierda que despliega 📱 Descargar / ⬇ Guardar / 💥 Chasquido. La subida a Supabase arranca sola en segundo plano | Respiración sutil + shimmer + repulsión 2D del mouse (foto y caption por igual) |
| `dissolving` | La foto se deshace | Cada partícula espera su turno (onda izq→der irregular), deriva con brisa diagonal + turbulencia y se desvanece a negro (~3s) |

La UI se muestra/oculta por estado vía `body[data-state="..."]` en CSS puro.
**Sin auto-disolución** (quitado en v15): la foto se queda en pantalla el
tiempo que haga falta — solo pasa a `dissolving` si alguien toca "💥
Chasquido". Antes se disolvía sola a los 60s (`AUTO_SNAP_AFTER`); se sentía
como que la instalación "volvía a tomar fotos sola" cada cierto tiempo,
quitándole control a quien maneja el stand. El único disparador de
`countdown`/captura sigue siendo, como siempre, tocar el obturador — nunca
automático.

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
  total a la obra. **Botón circular de acciones** (`#actions-toggle`, v15,
  reemplaza las 3 pills sueltas de antes): un toque despliega hacia arriba
  "📱 Descargar" / "⬇ Guardar" / "💥 Chasquido" (`#actions-menu`, animación
  pop); elegir una opción cierra el menú solo, igual que volver al espejo
  (`enterMirror` lo resetea para la siguiente persona). Más discreto que
  tener 3 pills siempre visibles encima de la foto.
- **Caption en partículas** (reemplaza el sello DOM plano): 6.000 de las 40.000
  partículas escriben "EXTERNADO FEST / CIENCIA DE DATOS 2026" debajo de la foto,
  con gradiente morado→cian de izquierda a derecha y 6% de destellos blancos.
  Al ser partículas de la escena: se arma en la misma oleada, se desintegra con
  el chasquido, reacciona al mouse, **y sale automáticamente en el PNG guardado
  y en las fotos que la gente tome con el celular**. El texto se rasteriza una
  vez en un canvas offscreen (1200×300, dos líneas) y se cachea
  (`getCaptionPoints`).
- Layout vertical auto-centrado: `PHOTO_WIDTH` bajó a 7.6 y la rejilla usa
  `PARTICLE_COUNT - CAPTION_COUNT - LOGO_COUNT * 2` celdas; foto +
  `CAPTION_GAP` + caption se centran como bloque en el viewport (~7.3 de
  ~7.7 unidades visibles de alto).
- **Logo del departamento en partículas, a ambos lados de la foto, con fondo
  tipo estampa/sticker**: cerebro rojo + circuito azul, el mismo dibujo
  Bézier de `particle_system.html` (2026-1) — identifica la carrera de
  verdad, a diferencia de una red neuronal genérica que se probó y se
  descartó en la sesión anterior (ver `## Pipeline de captura` para esa
  historia). Detrás del dibujo hay un **rectángulo redondeado blanco cálido**
  (`#f5f2ff`, no blanco puro) con borde sutil morado, dibujado primero y
  tapado por el cerebro+circuito donde van encima — solo asoma en el margen,
  como el respaldo de un sticker real. `getLogoPoints()` dibuja todo (fondo +
  cerebro + circuito) en un único canvas y lo rasteriza una sola vez
  (conservando color), se cachea. `LOGO_COUNT` subió de 8% a 12% del total al
  agregar el fondo — casi duplica el área a cubrir, y con el presupuesto de
  antes se habría visto disperso otra vez (la misma lección de la red
  neuronal: forma sólida grande necesita más partículas absolutas, no solo
  más densidad relativa). Uno a cada lado de la foto, simétrico, mismo
  tamaño: `LOGO_COUNT` es presupuesto **por lado** (el total real restado a
  la foto es el doble). Tamaño adaptativo: limitado por el espacio real
  libre entre la foto y el borde de pantalla y por `LOGO_MAX_HEIGHT_RATIO`
  de la altura de la foto — lo que sea menor, para que nunca desborde el
  monitor. **Inclinación y posición al azar** (`LOGO_TILT_MAX_DEG`,
  `LOGO_Y_JITTER`, `LOGO_X_JITTER`): cada lado, en cada captura, sale con su
  propio ángulo y desplazamiento — se ve pegado a mano, no calcado. El
  cálculo del tamaño máximo cubre el peor caso (inclinación + jitter al
  límite a la vez) con la protrusión real de un rectángulo rotado, no una
  cota genérica — probado en 16:9, 21:9, 4:3, 1:1 y 9:16 con datos
  sintéticos, nunca desborda. Es parte de la escena como el caption: se
  arma en la misma oleada, se desintegra con el chasquido, y sale en el PNG
  guardado. **Pendiente la primera prueba visual real** (no se pudo
  verificar en navegador desde esta sesión — el usuario prueba primero antes
  de que se use el MCP de Chrome).
- **Contador en vivo** (`#visits-chip`, estado espejo): "✦ N CHASQUIDOS
  HOY", sincronización en tiempo real de verdad (canal `postgres_changes` de
  Supabase, mismo patrón que `leaderboard.html`) — no decorativa. Requiere
  la tabla `chasquido_events` (`supabase-setup.sql`, sección 5); si no existe
  o no hay internet, el chip se oculta solo sin afectar el resto.
- **Stickers decorativos** (repertorio de 6: diamante 💎, cohete 🚀,
  planeta 🪐, corazón 💜, rayo ⚡, cámara 📷 — `getDiamondPoints` y
  siguientes): apilados junto al logo, **a los lados de la foto, nunca
  encima**. En cada foto se sortean 4 sin repetir (`pickRandomDistinct`)
  para los 4 huecos disponibles (arriba/abajo de cada logo) — la
  combinación cambia de persona a persona. A diferencia del logo, **sin
  fondo de estampa** (ese respaldo blanco queda solo para el logo del
  departamento; estos son accesorios sueltos, más chicos). Formas sólidas
  simples a propósito — nada de líneas finas, la misma lección de la red
  neuronal descartada. Cada uno con su propia inclinación al azar
  (`STICKER_TILT_MAX_DEG`). Layout en 5 franjas verticales por lado
  (sticker-arriba / hueco / logo / hueco / sticker-abajo), repartidas con
  paso fijo desde el logo hasta el borde real de pantalla — no solo hasta el
  borde de la foto, que dejaba muy poco aire y hacía que todo se
  amontonara. `STICKER_COUNT` es presupuesto **por hueco** (son 4, el total
  real restado a la foto es el cuádruple).
- **Destellos de relleno** (`getSparklePoints`): 12 estrellitas de 4 puntas,
  un solo dibujo blanco cacheado reteñido al azar con los 6 colores de las
  gemas del título — le dan textura al espacio negro entre el logo y los
  stickers sin competir con ellos. Viven **solo en las franjas-hueco** del
  layout (nunca en la del logo ni la de los stickers). Reparto en
  **cuadrícula, no puro azar**: cada zona-hueco se divide en 3 franjas
  iguales (una por destello) con jitter acotado al 35% de su propia
  franja — así ninguno puede invadir el espacio del vecino, ni por mala
  suerte del sorteo (antes sí pasaba: con 14 tirados al azar en poco
  espacio, varios caían pegados entre sí — visto en prueba real).
- **Insignia de la universidad** (`getUniLogoPoints`, código sin usar por
  ahora): se probó el logo real de la Universidad Externado de Colombia
  (vendorizado desde su propio sitio) sobre una insignia oscura — a la
  escala de un sticker casi no se notaba y no convenció, así que se sacó
  del repertorio activo. El código queda intacto por si se retoma con otro
  tratamiento (más grande, otra posición) más adelante.
- **Flor sonriente y moño** (`getFlowerPoints`/`getBowPoints`): lectura
  propia del estilo de ilustración de la campaña Externado Fest Family
  (formas redondeadas, contorno grueso, colores planos) — no una copia
  exacta. Se suman al repertorio de stickers (8 en total).
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

### Experimento descartado: densidad adaptativa (probado y revertido)
Se probó reemplazar la rejilla uniforme por un reparto de partículas por
importancia (más densidad en bordes — ojos, cejas, boca, pelo — menos en
piel/fondo planos), con color leído directo del píxel en vez de promediado
por celda. Dos intentos:
1. Sorteo aleatorio ponderado por celda → varianza de Poisson visible como
   ruido sal-y-pimienta en el fondo (probado en cámara real).
2. Reparto determinista (restos mayores/Hamilton) para eliminar el azar →
   corregía el ruido (validado con datos sintéticos: 0% de celdas de fondo en
   0 partículas), pero probado en cámara real **se veía peor que la rejilla
   original** — la uniforme ya se leía suficientemente clara y nítida, así
   que no valía la pena la complejidad ni el riesgo visual del reparto
   adaptativo. **Revertido** a la rejilla uniforme original; el código de
   ambos intentos no quedó en el archivo (se puede recuperar del historial de
   git si se quiere retomar con otro enfoque — por ejemplo, tamaño de
   partícula variable por vértice vía shader propio, en vez de solo variar la
   posición con un tamaño de sprite fijo global).

Después del muestreo: contraste suavizado (percentiles 2–98,
`PHOTO_STRETCH = 0.5`) → saturación 1.25 → sprite cuadrado redondeado,
`NormalBlending`, `toneMapped = false`, solape 1.35, bloom 0.15/0.8. Foto
plana (`PHOTO_DEPTH = 0`) porque el objetivo es fotografiarla y compartirla
por WhatsApp; subir a ~0.9 activa el relieve holograma.

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
| `LOGO_COUNT` | 12% del total (~7.200), por lado | Partículas del logo (cerebro + circuito + fondo estampa) junto a la foto |
| `LOGO_MAX_HEIGHT_RATIO` / `LOGO_MARGIN` | 0.62 / 0.22 | Tope de tamaño (fracción de la altura de la foto) y separación foto↔logo |
| `LOGO_TILT_MAX_DEG` / `LOGO_Y_JITTER` / `LOGO_X_JITTER` | 14 / 0.16 / 0.12 | Inclinación, desplazamiento vertical y variación del margen — aire para que no se vea rígido |
| `STICKER_COUNT` | 2% del total (~1.200), por sticker | Partículas de cada sticker de esquina (cohete/planeta/diamante) |
| `STICKER_SIZE` / `STICKER_TILT_MAX_DEG` | 0.5 / 20 | Tamaño y inclinación máxima de los stickers decorativos |
| `PHOTO_STRETCH` / `PHOTO_SATURATION` | 0.5 / 1.25 | Contraste y color |
| `PHOTO_DEPTH` | 0 | 0 = plana (WhatsApp); ~0.9 = holograma |
| `COUNTDOWN_STEP` / `DIGIT_PARTICLES` / `COUNTDOWN_LERP` | 0.9 / 12000 / 0.09 | Ritmo, densidad y morph del 3-2-1 |
| `ATTRACT_IDLE` / `ATTRACT_PHASE` / `ATTRACT_PARTICLES` | 45 / 5 / 14000 | Espera, ciclo y densidad de la vitrina (`ATTRACT_TEXTS` = palabras) |
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
- **v10**: descarga por QR — subida automática a Supabase Storage y
  overlay de QR grande con el botón "📱 Descargar". Migración al proyecto
  `aohpheppigbqmbfpzpbg` (los tres HTML del repo) y `foto.html` como página de
  descarga desplegable, porque Supabase no puede servir HTML.
- **v11**: robustez para el día del evento. (1) `animate()` ahora
  corre dentro de un `try/catch`: un frame roto ya no congela la instalación,
  se loguea y se recupera sola al espejo. (2) Todas las dependencias externas
  (Three.js r128 + post-processing, `supabase-js`, `qrcode-generator`, las
  fuentes Inter/Unbounded) se vendorizaron en [`vendor/`](vendor/) — la
  experiencia arranca sin internet; solo la subida a Supabase para el QR
  sigue necesitando conexión real. Detalle de versiones y cómo re-vendorizar
  en [`vendor/README.md`](vendor/README.md). (3) **Ciclo de QR verificado
  con un celular real**: escaneo → `foto.html` → descarga, sin fallos.
- **v12 (probada y revertida)**: se intentó densidad adaptativa (reparto de
  partículas por importancia sobre un mapa de bordes en vez de rejilla
  uniforme) en dos vueltas — sorteo aleatorio (ruido sal-y-pimienta en cámara
  real) y luego reparto determinista para corregirlo. La versión corregida,
  probada en cámara real, **se veía peor que la rejilla original** — no
  aportaba lo suficiente para justificar la complejidad. Revertida a la
  rejilla uniforme (idéntica a v3-v11, ver `## Pipeline de captura`). Detalle
  del experimento y por qué se descartó en la sección de arriba.
- **v13**: logo del departamento (cerebro + circuito, sin texto) en
  partículas junto a la foto, a un solo lado — mismo dibujo Bézier de
  `particle_system.html` (2026-1). Probado en cámara real: quedó bien, pero
  se sintió genérico ("esto lo encuentras en cualquier lado, no tiene nada
  que ver con la carrera más que dos logos y un texto").
- **v14**: más identidad, menos decoración genérica — logo a ambos lados de
  la foto (`LOGO_COUNT` pasó a ser presupuesto *por lado*), cerebro+circuito
  reemplazado por una red neuronal genérica (nodos y conexiones), contador
  en vivo (`#visits-chip`) y chip de datos técnicos (`#stats-chip`).
  Verificado en cámara real con Chrome DevTools: el contador funcionaba bien
  (**de paso se encontró y corrigió un bug real** — mostraba "0" en vez de
  ocultarse cuando la tabla no existe, lo cual habría sido engañoso el día
  del evento), pero la red neuronal se veía **como polvo disperso**, no como
  un diagrama — el presupuesto de partículas (~4.800/lado) alcanza para
  formas sólidas grandes (el cerebro+circuito original) pero no para muchas
  líneas finas y nodos chicos. Se corrigió en la misma sesión con capas más
  simples (3-4-2) y presupuesto de partículas separado entre nodos y líneas
  (62%/38%) — quedó legible, pero en la ronda siguiente igual se decidió
  volver al logo real (ver v15).
- **v15**: dos ajustes después de que probaras v14 en el navegador.
  (1) **Vuelve el logo del departamento** (cerebro+circuito) — la red
  neuronal, aunque ya se veía bien técnicamente, no identificaba a la
  carrera; el logo real "es muy útil" y sí lo hace. (2) **Se quitó el chip
  de datos técnicos** (`#stats-chip`) — no aportaba y generaba ruido visual;
  el contador en vivo (`#visits-chip`) se queda, ese sí es información real
  en tiempo real, no decoración. (3) **Se eliminó `AUTO_SNAP_AFTER`**: la
  foto ya no se disolvía sola a los 60s — se sentía como que la instalación
  "volvía a tomar fotos" por su cuenta. Ahora solo pasa a `dissolving` al
  tocar "💥 Chasquido"; capturar solo pasa al tocar el obturador, como
  siempre. (4) **Botón circular de acciones** (`#actions-toggle`): las 3
  pills sueltas de siempre (Descargar/Guardar/Chasquido) se colapsaron en un
  solo botón que las despliega al tocarlo.
- **v16**: el logo del departamento ahora tiene **fondo tipo
  estampa/sticker** — un rectángulo redondeado blanco cálido con borde
  morado sutil detrás del cerebro+circuito, tapado por el dibujo donde va
  encima, asomando solo en el margen (el respaldo de un sticker real).
  `LOGO_COUNT` subió de 8% a 12% del total para sostener la densidad del
  área nueva.
- **v17**: se probó v16 en cámara real — el sticker en sí se veía
  bien, pero el logo quedaba chico/difícil de distinguir junto a la foto, y
  los dos lados se sentían demasiado idénticos/rígidos (copia espejada
  exacta). Dos ajustes: (1) **Más grande** — `LOGO_MAX_HEIGHT_RATIO` 0.5→0.62
  y `LOGO_MARGIN` 0.3→0.22 (más cerca de la foto, gana espacio). (2) **Menos
  rígido**: cada lado (y cada captura) sale con su propia inclinación
  aleatoria (`LOGO_TILT_MAX_DEG`, ±14°) y un pequeño desplazamiento vertical
  y de margen (`LOGO_Y_JITTER`, `LOGO_X_JITTER`) — como si alguien lo hubiera
  pegado a mano, no perfectamente simétrico. El cálculo de tamaño máximo se
  ajustó para seguir sin desbordar la pantalla incluso en el peor caso
  (inclinación + jitter al máximo a la vez) — verificado matemáticamente en
  5 formatos de pantalla (16:9, 21:9, 4:3, 1:1, 9:16).
- **v18**: tres stickers de esquina nuevos — cohete 🚀 (arriba-der),
  planeta con anillo 🪐 (abajo-der) y diamante 💎 (arriba-izq), pegados sobre
  la foto con el mismo fondo tipo estampa del logo. Se extrajeron
  `rasterizeColorPoints()` y `drawStickerBacking()` como utilidades
  compartidas (antes ese código vivía duplicado dentro de `getLogoPoints`) y
  se refactorizó el logo para usarlas — sin cambiar su geometría (verificado
  igual que en v13: idéntica byte a byte al original de
  `particle_system.html`). `STICKER_COUNT` (2%/sticker, ~1.200 c/u) sale del
  presupuesto de la foto, que baja de 36.600 a 33.000.
- **v19**: se probó v18 en cámara real — pedido de vuelta a
  ajustar: (1) los tres stickers nuevos **ya no llevan fondo de estampa**
  (`drawStickerBacking` se quitó de las tres, se queda solo en el logo del
  departamento). (2) **Ya no van sobre la foto** — se movieron a los lados,
  apilados junto al logo (diamante arriba del izquierdo; cohete arriba y
  planeta abajo del derecho), más chicos que antes (`STICKER_SIZE` 0.85→0.5).
  Sin cambio de presupuesto (sigue en 33.000 para la foto), solo posición y
  tratamiento visual.
- **v20**: "le falta carne" — repertorio ampliado a 6 stickers (+ corazón 💜,
  rayo ⚡, cámara 📷; `getHeartPoints`/`getLightningPoints`/`getCameraPoints`)
  del que se sortean 4 sin repetir por foto (`pickRandomDistinct`), más 14
  **destellos de relleno** (`getSparklePoints`, un solo dibujo blanco
  reteñido al azar con los 6 colores de las gemas). `PARTICLE_COUNT` subió
  de 60k a 90k (el usuario confirmó que su equipo lo aguanta) para no
  seguir recortándole a la foto — queda en 43.920.
- **v21**: se probó v20 en cámara real — los destellos caían en el
  mismo rango vertical que los stickers grandes y se amontonaban unos
  encima de otros junto al logo. Causa real: el layout usaba el alto de la
  **foto** para acotar dónde caben las cosas, cuando el margen lateral en
  realidad corre todo el alto de **pantalla** (`visibleH`) — mucho más
  espacio del que se estaba aprovechando. Rediseñado en 5 franjas por lado
  (sticker-arriba / hueco / logo / hueco / sticker-abajo), repartidas con un
  paso fijo (`rowStep`) desde el logo hasta el borde real de pantalla; los
  destellos ahora solo caen dentro de las franjas-hueco, nunca en la del
  logo ni la de los stickers. Verificado en 16:9/21:9/4:3/1:1/9:16: separación
  positiva entre todas las piezas en los 5 formatos (21:9 es el más
  ajustado, ~0.11 unidades de margen, pero sin superposición).
- **v22**: conexión visible con la universidad. Se investigó la
  landing de Externado Fest Family (marca verde institucional + mascota
  "Lilly") — es otra sub-campaña (día familiar), no encaja con la identidad
  morado/cian ya construida para CHASQUIDO, así que se descartó mezclarla.
  En su lugar: se encontró y vendorizó el **logo oficial real** de la
  universidad (`vendor/uexternado/logo-uec.svg`, bajado directo de
  `uexternado.edu.co` — confirmado por su propio `alt="Universidad
  Externado de Colombia"`, no un redibujo a mano). `getUniLogoPoints()` lo
  carga (precarga asíncrona al inicio, `uexternadoLogoReady`) y lo dibuja
  sobre una insignia oscura con borde en gradiente de marca (el SVG viene en
  blanco, pensado para fondo oscuro) — se distingue del resto de los
  stickers (que llevan respaldo claro) como "la pieza oficial". A diferencia
  del repertorio de 6 (que se sortea), **esta insignia sale siempre** en el
  primer hueco (arriba del logo izquierdo) — con reserva a sortear un cuarto
  sticker normal si por lo que sea la imagen no cargó a tiempo.
- **v23**: el pedido real no era el logo institucional — era
  recrear el *estilo* de ilustración de la campaña Family (flores
  sonrientes, el moño de "Lilly") como stickers. Dos nuevos, agregados al
  repertorio (ya no 6, ahora 8 — `getFlowerPoints`, `getBowPoints`): una
  flor tipo tulipán con cara sonriente (3 pétalos superpuestos, tallo y
  hojas) y un moño rosa con cola dorada — lectura propia del estilo de la
  referencia, no una copia exacta. Se dejó afuera, a propósito, recrear la
  ilustración completa de la chica de la campaña: una figura humana con esa
  cantidad de detalle (pelo, ropa, manos) es mucho más riesgosa de
  simplificar bien al tamaño chico de un sticker de partículas — candidata
  para una ronda futura si estos dos funcionan bien. Sin cambio de
  presupuesto (el repertorio creció, pero se sigue sorteando el mismo total
  de 4 huecos). Verificado en cámara real: se ve bien.
- **v24**: pruebas de rendimiento en cámara real (M4 MacBook Air, 16GB) —
  `PARTICLE_COUNT` subido en escalones 90k → 150k → 200k, sin caída de FPS
  visible en ninguno. Se queda en **200.000** (foto ~98.8k). Pendiente
  encontrar el techo real (no medido con precisión, solo confirmado que
  200k no lo alcanza en este equipo) — ver `## Pendiente / ideas`.
- **v25 (actual)**: dos ajustes después de probar v23-v24 en cámara real.
  (1) **Insignia de la universidad, fuera del repertorio activo**: a la
  escala de un sticker se notaba muy poco y no convenció — se sacó del
  sorteo de huecos (`chosenStickers` volvió a ser 4 simples del repertorio
  de 8, sin slot garantizado). El código (`getUniLogoPoints`, el SVG
  vendorizado, la precarga) se dejó intacto pero sin usar, por si se
  retoma con otro tratamiento más adelante. (2) **Destellos ya no se
  superponen entre sí**: antes cada uno sorteaba su posición de forma
  totalmente independiente dentro de su zona, y con 14 tirados al azar en
  poco espacio, por pura probabilidad varios caían pegados (el problema
  del cumpleaños — se veía en captura real). Ahora cada zona-hueco se
  reparte en una cuadrícula (una franja por destello, con jitter acotado al
  35% de su propia franja) — ningún destello puede invadir el espacio del
  vecino, sin importar el azar. `SPARKLE_TOTAL` bajó de 14 a 12 (múltiplo
  exacto de las 4 zonas — con 14 el redondeo habría colocado 16 y
  descuadrado el presupuesto). Ver `## Identidad visual`. **Pendiente la
  primera prueba visual real** de este ajuste puntual — no se pudo
  verificar en navegador desde esta sesión (el usuario prueba primero antes
  de que se use el MCP de Chrome).
- **v26 (actual)**: limpieza tras revisar en cámara real. (1) **Insignia de
  la universidad, borrada por completo** (no solo desconectada): se quitó
  `getUniLogoPoints()`, la precarga (`uexternadoLogoImg`/
  `uexternadoLogoReady`/`preloadUniLogo()`) y el asset vendorizado
  `vendor/uexternado/logo-uec.svg` (ver `vendor/README.md`, ya sin esa
  fila). Ya no queda código muerto de esa idea. (2) **Modo DEBUG temporal
  "catálogo"**: `DEBUG_SHOW_ALL_STICKERS = true` (junto a `STICKER_SLOTS`
  en `CONFIG`) hace que cada foto muestre **los 8 stickers del repertorio a
  la vez** (en vez del sorteo de 4), en 2 filas de 4 pegadas a los bordes
  superior/inferior de la pantalla — orden fijo, el mismo de `stickerPool`,
  para poder señalar "el tercero de arriba es tal". `STICKER_SLOTS` pasa a
  8 automáticamente con el flag (el presupuesto de partículas se
  reajusta solo, sigue sumando exacto). **Poner `DEBUG_SHOW_ALL_STICKERS`
  en `false` cuando se termine de decidir la limpieza** — no es el modo
  normal del photobooth, solo para esta revisión. (3) **Pendiente,
  reportado por el usuario, aún sin resolver**: los dígitos 3-2-1 de la
  cuenta regresiva no se están viendo. Revisado el código a fondo
  (`getDigitPoints`, `setOverlayTextTargets`, el bloque `stCountdown` del
  loop de animación, blending del material en modo `dust`, z-index de
  capas) sin encontrar ninguna diferencia contra el original — nada de esa
  ruta cambió en todo el diff de la sesión. Falta diagnóstico en vivo
  (consola del navegador durante la cuenta regresiva) para encontrar la
  causa real.
- **v27 (actual)**: revisado el modo catálogo en cámara real — todo bien
  menos flor y moño (los dos "rosas"), que salieron del repertorio por
  completo (`getFlowerPoints`/`getBowPoints` borradas, no solo
  desconectadas). En su lugar entran 3 nuevos, con un ángulo de Ciencia de
  Datos en vez de la ilustración de campaña — mismo criterio de siempre
  (formas sólidas, contorno grueso, sin líneas finas tipo red neuronal):
  **gráfico de barras** (`getBarChartPoints`, 4 barras de colores de gema),
  **base de datos** (`getDatabasePoints`, el cilindro clásico de 3 capas) y
  **lupa con dispersión** (`getMagnifierPoints`, scatter plot de puntos de
  colores dentro del lente). Repertorio activo: 6 → **9** con estos
  cambios. El catálogo de `DEBUG_SHOW_ALL_STICKERS` ahora reparte
  dinámicamente (`Math.ceil(n/2)` arriba, el resto abajo) en vez de una
  cuadrícula fija, así que escala solo si el repertorio vuelve a cambiar.
  `STICKER_SLOTS` en modo DEBUG pasa a 9 (presupuesto reverificado, sigue
  sumando exacto). **Sigue pendiente el bug de los dígitos 3-2-1** (ver
  v26) — no se tocó nada de esa ruta en este cambio.
- **v28 (actual)**: catálogo revisado y aprobado. `DEBUG_SHOW_ALL_STICKERS`
  vuelve a `false` — el photobooth queda otra vez en su modo normal: 4
  huecos a los lados del logo, sorteados sin repetir del repertorio de 9
  (antes 6 + los 3 nuevos de Ciencia de Datos). El bloque DEBUG se deja en
  el código (apagado) por si hace falta revisar el repertorio de nuevo más
  adelante. Presupuesto reverificado con `STICKER_SLOTS=4`: sigue sumando
  exacto (foto ~98.8k, igual que antes de las pruebas del catálogo).

## Pendiente / ideas
- **Correr `supabase-setup.sql` actualizado** en el proyecto real — crea
  `chasquido_events`, sin lo cual el contador en vivo no aparece.
- **Desplegar `foto.html`** (Netlify) y poner su URL en `SHARE_LANDING` si se
  quiere la página con marca en vez del enlace directo a la imagen. Hoy el QR
  sigue apuntando directo a la imagen (`SHARE_LANDING` vacío) — funciona, ya
  verificado, pero sin la página con marca.
- **Borrar las fotos de prueba** del bucket (sección de mantenimiento del SQL).
- Galería/descarga de las fotos originales.
- Tecla `H` para ocultar toda la UI (captura de pantalla 100% limpia).

## Cómo probar
```bash
cd "2026-2" && python3 -m http.server 8000
# abrir http://localhost:8000/photo_particles.html
```
Permitir la cámara. Verificación de sintaxis: extraer el script inline y
`node --check`.
