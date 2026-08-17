# Sukuna — Plan de trabajo

> Documento vivo. Se actualiza a medida que avanza cada fase — marcar checkboxes,
> anotar decisiones y resultados de las pruebas aquí mismo, para no perder el hilo
> entre sesiones.
>
> **Regla de organización**: todo el trabajo vive en **un solo `index.html`**, que
> se edita y evoluciona en el lugar. No se crean archivos ni carpetas nuevas por
> cada iteración — eso desorganiza el proyecto. Si algo se reemplaza, se reemplaza
> de verdad (y se documenta aquí qué cambió y por qué), no se deja como código
> muerto al lado.

## Qué es esto

Un experimento de **realidad aumentada anclada a la mano**, inspirado en
[este reel](https://www.instagram.com/p/Db-CWglpfpr/): al mover las manos frente
a la cámara, una figura 3D aparece y **sigue el movimiento en tiempo real**.

Es un proyecto **separado** de `photo_particles.html` (CHASQUIDO). No lo modifica,
no depende de él. Vive en su propia carpeta para poder fallar o iterar sin riesgo.

**Pensado para demostración en persona** (no para producción de video/redes).

## Decisiones ya tomadas (no reabrir sin razón de peso)

- ❌ **Sin HUD de coordenadas/cajas de escaneo** — evaluado y descartado.
- ❌ **Sin marcador físico** — se probó con tarjeta impresa (MindAR) y funcionó,
  pero se reemplazó por tracking de mano directo, que es lo que se necesita.
- ✅ **Un solo HTML autocontenido**, sin backend. Cámara, tracking y render 3D,
  todo en el cliente, todo por CDN.
- ✅ **MediaPipe Hands (Tasks Vision)** — la API moderna de Google — para el
  tracking. `numHands: 2` (antes 1; se subió al necesitar ambas manos para el
  cuadrilátero de 4 puntos, ver abajo).
- ✅ **Three.js reciente sin restricciones de versión** (ya no se depende de
  MindAR, así que no hay que fijar una versión vieja por compatibilidad).
- ✅ **Filtro de suavizado: el *1 Euro Filter*** de `2026-1/neon_maze.html`,
  portado tal cual — probado en producción para este tipo de ruido de tracking.
- ✅ **Construir el mecanismo primero, plano y sin decoración; vestirlo después.**
  Se ha repetido esta fórmula en cada etapa (marcador → mano rígida → cuadrilátero
  deformable) porque funciona: si el mecanismo no convence, se sabe antes de
  invertir tiempo en que se vea bien.

## Estructura de la carpeta

```
2026-2/sukuna/
├── PLAN.md      este archivo
└── index.html   ★ el único entregable — se edita en el lugar en cada iteración
```

Sin `node_modules`, sin carpetas de archivo, sin builds. Todo (Three.js,
MediaPipe, el modelo de IA) se carga por CDN en tiempo real.

---

## Historial del mecanismo (qué se probó y qué quedó)

### 1. Marcador impreso + MindAR — funcionó, descartado por decisión de producto
Una tarjeta impresa con un patrón entrenado, reconocida por MindAR, con un objeto
3D anclado a su pose. **Quedó validado en persona** (reconocimiento + seguimiento
fluido confirmados) antes de decidir que la experiencia final no debía depender de
ninguna tarjeta física — se pivotó a tracking de mano directo.

Aprendizajes que se reutilizaron o vale la pena recordar (por si algún enfoque
similar vuelve a hacer falta):
- El compilador de marcadores de MindAR puede correr en Node con el paquete
  `canvas`, sin depender de su herramienta web — pero cuidado con versiones
  duplicadas de `canvas` en `node_modules` (mind-ar puede traer la suya propia,
  incompatible con la instalada).
- `canvas` necesita dependencias nativas de sistema en macOS (`pkg-config cairo
  pango libpng jpeg giflib librsvg pixman`, vía Homebrew).
- Embeber un asset binario grande en base64 dentro de un HTML autocontenido
  (decodificar a `Blob` → URL `blob:` en runtime) **funciona bien** — verificado
  con una petición de red real.
- Fijar versiones de librerías de terceros cuando una dependencia intermedia usa
  una API que versiones más nuevas remueven (pasó con `sRGBEncoding` de Three.js).

### 2. Mano única, objeto rígido — funcionó, evolucionado a algo más expresivo
Un icosaedro placeholder anclado a la pose de **una mano**: posición (landmark 9,
centro de palma), orientación (base ortonormal calculada desde `worldLandmarks`),
y zoom (tamaño aparente de la mano en imagen). **Quedó validado en persona**:
rotación fluida, sigue bien, zoom calibrado con datos reales de cámara.

Aprendizajes:
- `worldLandmarks` (métricos, sin distorsión de perspectiva) sirven para
  ORIENTACIÓN; `landmarks` (espacio de imagen) sirven para POSICIÓN y para el
  "zoom" — son los que sí reflejan la distancia real a la cámara.
- Medir "tamaño de mano" con un solo vector (ej. índice-a-meñique) es sensible a
  la ROTACIÓN de la mano, no solo a la distancia — promediar varias distancias
  muñeca→nudillo da una señal más limpia.
- Calibrar constantes (como `REFERENCE_HAND_SPAN`) con datos reales de cámara en
  vivo es mucho mejor que adivinar — se hizo instrumentando temporalmente un
  lector de depuración en pantalla, capturando valores reales, y quitándolo antes
  de dejar el archivo final.

### 3. Cuadrilátero deformable, 2 manos — actual, en validación

Reemplazó al objeto rígido de una mano por completo (mismo `index.html`, no hay
versión vieja al lado). Inspirado directamente en las fotos de referencia: una
tarjeta/tira flexible sostenida por los dedos, cuyos lados se doblan según cómo
se mueve cada mano.

**Mecanismo**: 4 puntos de control independientes — pulgar e índice de cada mano
(landmarks 4 y 8) — mapeados a los 4 vértices de un plano de Three.js
(`BufferGeometry` de 1×1 segmentos). Cada vértice se reposiciona cada frame según
su punto de control correspondiente, con su propio par de filtros *1 Euro*. Las
manos se asignan a "izquierda"/"derecha" de la malla comparando su posición X en
pantalla cada frame (no por la etiqueta Left/Right de MediaPipe) — así el lado
izquierdo de la malla siempre sigue a la mano que está visualmente a la
izquierda, sin saltos si las manos se cruzan.

El "zoom" ya no necesita cálculo aparte: al acercar las manos a la cámara, los 4
puntos se separan más entre sí en el espacio de imagen por perspectiva, así que
el cuadrilátero crece solo.

Sigue sin color/textura (`MeshNormalMaterial`) — se ve como un bloque sólido
azul/morado en vez de multicolor como el icosaedro, porque un plano casi no
tiene variación de normales (a diferencia de un icosaedro con caras en muchos
ángulos). Es visualmente correcto para esta etapa, no un error.

**Geometría preparada para la decoración futura**: la malla ya tiene UVs
asignadas (aunque no se usan todavía), para no tener que reconstruir la
geometría cuando llegue la textura a rayas de las fotos de referencia.

## Checklist técnico (cuadrilátero, 2 manos)

- [x] `numHands: 2` en el HandLandmarker.
- [x] Extraer pulgar (landmark 4) e índice (landmark 8) de cada mano.
- [x] Asignar mano izquierda/derecha por posición X en pantalla (estable frame
      a frame, no depende de la etiqueta de MediaPipe).
- [x] `BufferGeometry` de 4 vértices + 2 triángulos, con UVs ya definidas.
- [x] Reposicionar los 4 vértices cada frame según los puntos de control
      (con suavizado *1 Euro* independiente por vértice) + recomputar normales.
- [x] Mostrar la malla solo cuando se detectan **las 2 manos**; estado en
      pantalla distingue 0/1/2 manos detectadas.
- [x] **Verificado en vivo** (cámara real disponible en el entorno de
      desarrollo): ambas manos detectadas, el cuadrilátero se forma entre los 4
      dedos, y **se deforma de verdad** entre dos capturas tomadas en momentos
      distintos (cambió de trapecio a un cuadrilátero asimétrico según el
      movimiento real de las manos). 56-61 FPS. Consola limpia.
- [x] **Prueba dedicada en persona**: "el movimiento con las manos es
      perfecto y se ve muy limpio" — la deformación en sí queda validada.
- [x] **Rango de alcance corregido.** Problema detectado: la figura quedaba
      "muy lejos de los dedos", con poco campo de acción. Causa real: el
      mapeo de landmark → mundo 3D usaba un rango inventado
      (`HAND_MOVE_RANGE = 3.2`) que cubría solo una fracción del ancho
      visible real de la cámara 3D — el objeto nunca llegaba a los bordes
      aunque el dedo sí. Corregido calculando el tamaño visible real a partir
      del FOV de la cámara (`getVisibleFrustum`) y corrigiendo además el
      recorte que hace `object-fit: cover` en el video
      (`getCoverCrop`) — sin esto último el mapeo queda desalineado con lo
      que la persona realmente ve en pantalla si la proporción de la cámara
      no coincide con la de la ventana. Verificado en vivo: el objeto ahora
      ocupa gran parte de la pantalla y las puntas quedan junto a los dedos
      reales, no cerca del centro. 53 FPS, consola limpia.

## Riesgos y notas a mantener presentes

- **Dependencia de CDN/internet**: Three.js + MediaPipe + el modelo de IA (7.8 MB)
  vienen de CDN/Google Cloud Storage. Vendorizar al disco antes de la demo si el
  lugar no tiene wifi confiable — mismo pendiente que CHASQUIDO.
- **Rendimiento con 2 manos**: ligeramente más pesado que con una sola (56 vs.
  60-61 FPS observado) — sigue siendo holgado, pero vale la pena confirmarlo en
  la máquina real de la demo, no solo en la de desarrollo.
- **Robustez cuando una mano se pierde momentáneamente**: hoy la malla
  desaparece por completo si falta cualquiera de las dos manos (aunque sea un
  frame). Vale la pena probar si eso se siente bien en uso real o si conviene
  tolerar una ausencia breve antes de ocultar.
- **No mezclar con decoración antes de tiempo**: color, textura de rayas, marca
  — todo eso espera a que el mecanismo de 4 puntos esté probado y se sienta bien.

## Cómo probar

1. `cd 2026-2/sukuna && python3 -m http.server 8000` (servidor HTTP, no
   `file://`, por los permisos de cámara).
2. Abrir `http://localhost:8000/index.html`, aceptar el permiso de cámara.
3. Mostrar **las dos manos** a la cámara, con pulgar e índice extendidos como
   pellizcando una tarjeta imaginaria (como en las fotos de referencia).
4. Observar:
   - ¿Aparece el cuadrilátero entre los 4 dedos?
   - Al mover una mano sin mover la otra, ¿esa mitad de la figura se mueve
     independiente, o se nota rara/con retraso?
   - ¿Se siente como sostener algo flexible entre los dedos, o más como una
     forma genérica que no conecta bien con el gesto?
   - Probar cruzar las manos, acercarlas/alejarlas entre sí, acercar/alejar
     ambas de la cámara juntas.

## Estado actual

**Mecanismo de cuadrilátero (2 manos, 4 puntos): ✅ validado en persona,
incluido el rango de alcance real.**

### Calidad de cámara subida a 1080p

Se pedía 720p como "ideal" — no era el máximo. Subido a 1920×1080 (mismo
criterio que CHASQUIDO). Un detalle real encontrado: pedir `{ideal: 1920}` /
`{ideal: 1080}` solo **no bastó** — el navegador negoció 1280×720 igual (la
cámara real soporta hasta 1920×1080, confirmado con `getCapabilities()`, así
que no era límite de hardware). Agregar `aspectRatio: {ideal: 16/9}` sí forzó
la resolución completa — mismo hallazgo que ya se había hecho antes en
CHASQUIDO, se repitió aquí.

**Costo de rendimiento medido (no asumido):** en reposo (sin manos) sigue a
60-61 FPS igual que antes. Con las dos manos activas siendo detectadas —el
caso real de uso— bajaba a **~40-53 FPS** (antes con 720p rondaba 56-61 FPS con
manos activas). Ver la sección de optimización de abajo — quedó corregido.

### Optimización: desacoplar detección de render — 40-53 FPS → 52-58 FPS

**Diagnóstico primero, no se optimizó a ciegas.** Se instrumentó el código
temporalmente para medir cada pieza por separado (y se quitó la instrumentación
antes de dejar el archivo final):

- `handLandmarker.detectForVideo()` sola cuesta **~19-23ms** por llamada con
  las 2 manos a 1080p. El presupuesto para 60 FPS es 16.7ms/frame — la
  detección **sola** ya excede ese presupuesto, antes de renderizar nada.
- Sin ninguna detección corriendo, el render solo (video + malla + Three.js)
  sí llega limpio a **60-61 FPS** — confirma que el cuello de botella es
  exclusivamente la detección, no el render ni la decodificación de video.
- Se probó alimentarle a MediaPipe un canvas más chico (640×360, escalado
  desde el video) en vez del `<video>` completo, esperando que menos píxeles
  = menos costo. **Resultado contraintuitivo: fue más lento** (21-31ms según
  la corrida, siempre peor que los ~19-23ms del `<video>` completo) —
  verificado además invirtiendo el orden de las pruebas para descartar que
  fuera solo un efecto de "calentamiento" del detector. MediaPipe tiene un
  camino optimizado para leer directamente de un elemento `<video>` que un
  `<canvas>` no aprovecha (probablemente porque un canvas exige una lectura
  de píxeles por CPU antes de re-subir la textura, mientras que el video se
  puede subir directo a GPU). **Esta vía se descartó.**
- Se confirmó que no existe una variante de modelo más liviana para
  `hand_landmarker` (a diferencia de otros modelos de MediaPipe como
  pose_landmarker, que sí tienen lite/full/heavy) — probado contra el bucket
  público de Google, solo existe la versión que ya se usa.

**La solución real**: desacoplar la detección del render. Antes corrían
pegadas en el mismo tick de `requestAnimationFrame` — si la detección tardaba
20ms, ese frame completo tardaba 20ms, topando todo el loop. Ahora se
renderiza en **cada** tick (barato, ~1ms), pero se llama a
`detectForVideo` solo cada `DETECT_EVERY_N = 2` ticks — así la detección tiene
un presupuesto de ~33ms en vez de 16.7ms, que le sobra cómodo. Entre
detecciones, la malla se queda en la última posición conocida (el *1 Euro
Filter* ya está diseñado para tolerar esto sin saltos bruscos cuando llega el
siguiente dato real).

Se probó también `DETECT_EVERY_N = 3`: la ganancia sobre `2` fue marginal
(52-57 FPS vs. 52-56 FPS) a cambio de actualizar la mano con menos frecuencia
(~20Hz en vez de ~30Hz) — no valió la pena, se quedó en `2`.

**Resultado final, medido con las manos activas**: 52-58 FPS (antes 40-53),
verificado visualmente que la deformación se sigue viendo fluida y sin
retraso perceptible incluso en movimiento rápido. No llega a un 60 perfecto y
constante — el resto de la brecha probablemente es overhead de scheduling del
navegador (una llamada de ~20ms que igual ocurre cada 2 frames puede correr
el *timing* de ese frame específico más allá de un múltiplo exacto de vsync)
más que algo optimizable con más cambios de código. Se considera un resultado
sólido para la demo.

### Segunda figura: triángulo (1 mano) + transición automática

Se agregó una segunda figura, siguiendo la misma lógica que el cuadrilátero
pero leyendo 3 puntos de una sola mano en vez de 4 puntos de dos manos. El
sistema **decide solo** cuál mostrar, sin botón ni temporizador: cuenta
cuántas manos detecta (señal que ya se calculaba, no cuesta nada extra) —
**2 manos → cuadrilátero, 1 mano → triángulo, 0 → ninguna**.

**Refactor**: la creación de malla deformable se generalizó a
`createDeformableShape(vertexCount, indices, uvs)`, reutilizada por ambas
figuras — evita duplicar la lógica de geometría/material entre ellas.

**Transición entre figuras**: no se intentó un morph geométrico entre
cuadrilátero y triángulo — no tiene sentido físico, porque pasar de 1 a 2
manos es un cambio discreto (nadie "interpola" entre mostrar una mano y dos).
En su lugar: la figura que aparece entra con un pop-in corto (~220ms, escala
0.6→1 + opacidad 0→1), la que desaparece se oculta directo. Se ve intencional
sin tener que resolver una correspondencia de vértices entre topologías
distintas (4 vértices vs. 3) que no tendría un significado real.

**Puntos del triángulo — encontrado y corregido un problema en vivo:**
primer intento fue pulgar+índice+medio (extensión directa del patrón
pulgar+índice del cuadrilátero). En la prueba con cámara real se vio como
**una astilla delgada**, no un triángulo — esas tres puntas quedan muy cerca
entre sí en cuanto la mano no está bien abierta. Se cambió a
**muñeca (0) + índice (8) + meñique (20)**: la muñeca es un punto que casi no
se mueve con el gesto de los dedos, e índice/meñique son los dos dedos más
separados de la mano — debería dar una forma más grande y robusta.

**Honestidad sobre lo verificado**: con el segundo intento (muñeca+índice+
meñique) el triángulo *seguía* viéndose como astilla en las capturas — pero
en ambos casos la mano estaba en una pose relajada/cerrada (puño apoyado
cerca de la cara), no en un gesto deliberado de mano abierta como en las
fotos de referencia. No se pudo confirmar con certeza si el problema persiste
con la mano genuinamente abierta, porque el entorno de prueba solo permite
observar gestos que ocurren de forma natural frente a la cámara, no
dirigirlos. **Es físicamente esperable que cualquier elección de 3 puntos
basados en la punta de los dedos se junte cuando la mano se cierra** — no es
necesariamente un defecto de qué landmarks se eligieron.

**Pendiente de tu prueba**: mostrar la mano bien abierta/extendida (como en
las fotos de referencia) y confirmar si el triángulo se ve bien en ese caso.
Si sigue viéndose chico incluso abierta, la alternativa es usar nudillos
(index_mcp=5, pinky_mcp=17) en vez de puntas — más estable ante el cierre de
la mano, a cambio de sentirse menos "atado" al movimiento de los dedos
individuales.

**Mecanismo de auto-cambio: verificado en vivo.** Con la cámara real
disponible en el entorno de desarrollo, se confirmó que el sistema alterna
correctamente entre "triángulo (1 mano)" y "cuadrilátero (2 manos)" en tiempo
real según cuántas manos aparecen — incluida una secuencia de 15 lecturas
consecutivas mostrando cambios de ida y vuelta sin quedarse pegado en un
estado. Consola limpia, sin errores.

### Figuras fijadas en pantalla ("dejar" figuras al estilo del video de referencia)

El usuario aclaró la intención real: no es un video pre-renderado, es una
demostración en vivo que sigue el mismo ORDEN que el video de referencia
(cuadrado → triángulos → más cuadrados...), dejando figuras acumuladas en
pantalla en distintas posiciones mientras la figura activa sigue viva.

**Mecanismo descartado**: fijar al soltar la mano (mi propuesta inicial). El
usuario pidió explícitamente lo contrario — no quiere que quitar las manos
sea el disparador.

**Mecanismo implementado**: fijar por **quietud con tolerancia**. Cada figura
activa monitorea su propio centroide (promedio de sus vértices) cada vez que
se actualiza el tracking. Si el centroide se mantiene dentro de un radio de
tolerancia (`STILL_TOLERANCE = 0.45` unidades de mundo — no un punto exacto,
porque con un punto exacto el temblor natural de la mano nunca cumpliría la
condición) durante `STILL_DURATION_MS = 600ms` ("no tiene que ser mucho"), se
clona la geometría+material actuales (con la forma deformada exacta de ese
instante) en una malla estática independiente, agregada a un array
`stampedShapes` (tope `MAX_STAMPED_SHAPES = 10`, la más vieja se remueve y se
libera con `.dispose()` si se excede). La figura viva sigue funcionando
normal después — puede volver a fijar otra copia si se queda quieta en otro
lugar (el estado de quietud se resetea automáticamente al detectar
movimiento, y también al ocultarse/reaparecer la figura).

**No hay pop-in en el fijado**: la figura ya estaba totalmente visible antes
de quedarse quieta, así que fijar es un "congelamiento" instantáneo (opacidad
1, sin transición), no una aparición nueva — el pop-in sigue siendo solo para
cuando una figura pasa de oculta a visible por primera vez.

**Verificado en vivo, extensamente** (con la cámara real disponible en el
entorno de desarrollo, sin intervención humana dirigida — solo observando
comportamiento natural frente a cámara durante varios minutos):
- Se fijaron figuras automáticamente sin ninguna acción especial — confirmado
  tanto para el cuadrilátero como para el triángulo (el contador subió justo
  en los frames donde el estado decía "cuadrilátero (2 manos)" en un caso).
- Las copias fijadas **persisten** en pantalla incluso cuando no hay ninguna
  mano visible ("buscando…") — no dependen de que la figura viva se muestre.
- El contador llegó exactamente a **10/10 y se quedó ahí** (no lo superó) —
  confirma que el tope + reemplazo de la más vieja funciona.
- **60 FPS con las 10 figuras acumuladas simultáneamente** — el `.dispose()`
  al remover las viejas evita que el costo crezca sin control en una demo
  larga.
- Bonus: una captura con la mano genuinamente abierta mostró el triángulo
  en vivo grande y claro — confirma la sospecha de la sección anterior: el
  problema de "astilla delgada" era por la pose relajada de la mano en las
  pruebas anteriores, no por los landmarks elegidos (muñeca+índice+meñique
  parece una buena elección después de todo).

### Control manual: puño = espacio libre (no trackear)

El usuario pidió una válvula de escape: poder reposicionar la(s) mano(s) sin
que eso trackee ni fije nada — "para tener ese espacio libre cuando no se
quiera poner nada". Se implementó detectando **puño**: si una mano tiene al
menos 3 de sus 4 dedos (índice/medio/anular/meñique; se excluyó el pulgar por
comportarse distinto anatómicamente con este método) doblados — comparando
distancia punta-muñeca contra distancia nudillo medio(PIP)-muñeca, el mismo
criterio que ya usaba `particle_system.html` originalmente — esa mano **no
cuenta** para el tracking.

Esto se integró filtrando `usableHands` (manos detectadas menos las que están
en puño) **antes** de la lógica existente de conteo — no fue necesario tocar
el resto de la máquina de estados. Efecto natural: si de 2 manos una está en
puño, queda 1 mano usable y pasa a modo triángulo con la mano abierta; si las
dos están en puño (o no hay manos), no se trackea nada.

**Verificado en vivo**: se capturó el estado "pausado (puño)" con la mano
sosteniendo un celular en una posición de agarre tipo puño — ninguna figura
nueva trackeaba en vivo mientras tanto, solo las ya fijadas de antes seguían
en pantalla (correcto: el puño pausa el tracking, no borra lo ya fijado). Se
confirmó además la transición fluida entre los 4 estados
(puño → triángulo → cuadrilátero → puño) en una sola sesión de observación,
sin quedarse pegado en ninguno. Consola limpia.

### Gesto de borrado: tres intentos hasta llegar a puño + codo

El video de referencia usa un pase de codo frente a cámara para borrar todo.
**MediaPipe Hands no tiene esa información** — solo rastrea de la muñeca a
los dedos, no el brazo. Se pasó por tres diseños:

**Intento 1 — swipe rápido de mano** (cero costo extra, sin dependencias
nuevas): centro de todas las manos detectadas, distancia recorrida en una
ventana corta de tiempo. Se implementó y se verificó en vivo que sí disparaba
(figuras acumuladas 5/5 → 0/5 con un movimiento natural). **Rechazado por el
usuario tras usarlo**: "no se siente nada bien, es difícil que borre todo y
no se deja claro cuál es el comando" — funcionaba técnicamente pero no se
sentía como un gesto deliberado ni discoverable.

**Intento 2 — codo real por proximidad/movimiento** (`PoseLandmarker`,
landmarks 13/14): se agregó el modelo `pose_landmarker_lite` corriendo a una
frecuencia mucho menor que el de manos (`POSE_DETECT_EVERY_N = 16`, ~3-4
veces/seg contra ~30Hz de manos) para no repetir el problema de rendimiento
ya resuelto — **verificado en vivo que la URL del modelo existe y carga sin
costo perceptible de FPS** (58-60 FPS con ambos modelos corriendo). Pero el
gesto en sí (mover el codo una distancia mínima cerca de cámara) requería
mostrar la mano abierta para que el codo quedara bien visible en cuadro — y
una mano abierta ya dispara el modo triángulo de fondo, compitiendo
visualmente justo en el momento de intentar borrar. **Rechazado antes de
terminar de probarlo en vivo**, por este choque de diseño detectado por el
usuario.

**Intento 3 (actual) — puño + codo visible, sostenidos**: combina dos señales
que ya existen en el proyecto en vez de sumar una tercera detección. El PUÑO
(`isFist`, ya usado para "espacio libre") + el CODO visible en cuadro
(`PoseLandmarker`, mismo modelo del intento 2, misma cadencia reducida). Con
el puño no hay choque visual: una mano en puño ya es filtrada por
`usableHands`, así que ninguna figura aparece mientras se hace el gesto de
borrado. Se exige sostener ambas condiciones **600ms**
(`ELBOW_CLEAR_HOLD_MS`) antes de disparar — evita que un puño casual con el
codo de paso en cuadro (p. ej. reacomodando la postura) borre todo sin
querer — más un `ELBOW_CLEAR_COOLDOWN_MS = 1200ms` para no disparar varias
veces seguidas del mismo gesto sostenido.

**Feedback agregado** (el intento 1 falló en parte por falta de claridad):
línea de estado `Codo: listo / fuera de cuadro` en el panel (así se sabe si
el sistema puede ver el codo *antes* de intentar el gesto), y al borrar, el
contador de figuras muestra `¡BORRADO!` un momento antes de volver a
`Fijadas: 0/5` — confirmación inequívoca del instante exacto del disparo.

**Límite bajado de 10 a 5** copias fijadas simultáneas, a pedido del usuario
(se mantiene con este diseño).

**Verificado en vivo (parcial)**: carga de ambos modelos sin errores, 58-60
FPS sostenidos con manos + pose corriendo juntos, transición correcta entre
"Codo: listo"/"fuera de cuadro" según el codo entra/sale de cuadro, el modo
triángulo/cuadrilátero sigue funcionando sin regresión, el tope de 5 copias
se respeta. **Pendiente**: confirmar en vivo que sostener puño+codo dispara
el borrado — no se pudo dirigir el gesto exacto desde el entorno de
desarrollo (solo se observa comportamiento natural frente a cámara, no se
puede mover el brazo de quien prueba). Pendiente de confirmación del usuario
probándolo él mismo.

**Confirmado por el usuario probándolo en persona**: "si siente perfecto lo
acabe de probar y esta muy bien, todo quedo perfecto" — el gesto de
puño+codo sostenido queda validado como mecanismo final de borrado.

### Limpieza de código (buenas prácticas, no rendimiento)

Pasada de revisión pedida explícitamente para buscar código muerto y mejorar
prácticas de programación — **no** para ganar FPS (ya está en un punto sólido,
ver secciones de arriba). Cuatro hallazgos, los cuatro aplicados y verificados
en vivo sin ningún cambio de comportamiento:

- **`isFist()` se llamaba dos veces por mano** en el mismo tick de detección
  (una vez en `.some()` para el gesto de borrado, otra en `.filter()` para
  separar manos usables). Se unificó en una sola pasada por `allHands` que
  llena `usableHands` y marca `anyHandIsFist` a la vez.
- **`setElbowStatus()` reescribía `innerHTML` en cada frame** (~60/seg, ya que
  `checkElbowClearGesture` corre en cada tick), casi siempre con el mismo
  texto. Se reemplazaron `setHandStatus`/`setElbowStatus` por una fábrica
  `makeStatusSetter(el, label)` que memoriza el último valor y solo toca el
  DOM cuando el texto realmente cambia.
- **Código muerto de verdad**: `mesh.scale.set(1, 1, 1)` en `stampShape()` no
  hacía nada — un `THREE.Mesh` recién creado ya nace con escala `(1,1,1)` por
  defecto. Se quitó la línea, se dejó solo el comentario explicando por qué
  la escala final no depende del pop-in de la malla viva.
- **Número mágico duplicado**: el `"Fijadas: 0/5"` inicial en el HTML no
  tiene ninguna relación formal con `MAX_STAMPED_SHAPES` en el JS (que sí es
  la fuente real del tope) — funciona porque el JS lo sobreescribe al
  cargar, pero quedaba como una duplicación silenciosa. Se agregó un
  comentario HTML aclarando que ese texto es solo el placeholder inicial.

**Verificado en vivo tras el cambio**: recarga limpia, consola sin errores
nuevos, comportamiento idéntico al de antes de la limpieza (confirmado por el
usuario: "todo quedo funcionando exactamente como estaba el anterior, quedo
perfecto").

Próximo paso: la decoración — textura a rayas (o lo que se defina) usando las
UVs ya preparadas, y look de marca si aplica.
