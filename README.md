# ✦ 3D Particle System — Hand Gesture Control

Sistema de partículas 3D interactivo controlado por **gestos de la mano** en tiempo real. Construido con Three.js y MediaPipe Hands.

![Three.js](https://img.shields.io/badge/Three.js-r128-black?logo=three.js)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hands-4285F4?logo=google)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 Descripción

Una experiencia visual interactiva donde **15,000 partículas** se organizan en formas 3D y responden a los movimientos de tu mano capturados por la webcam. Ideal para demostraciones, festivales y eventos de tecnología.

---

## 🧰 Tecnologías

| Tecnología | Versión | Uso |
|---|---|---|
| [Three.js](https://threejs.org/) | r128 | Motor de renderizado 3D |
| [MediaPipe Hands](https://google.github.io/mediapipe/solutions/hands) | 0.4 | Detección de manos en tiempo real |
| HTML/CSS/JS | — | Todo en un solo archivo autocontenido |

---

## 🖐️ Controles por Gestos

| Gesto | Efecto |
|---|---|
| ✌️ **Peace** (índice + medio arriba) | Muestra el mensaje de bienvenida como texto de partículas |
| **Mover la mano** (izq/der, arriba/abajo) | La figura se mueve siguiendo la posición |
| **Rotar/inclinar la mano** | La figura rota en el eje Z |
| **Abrir la mano** | Las partículas se expanden hacia afuera |
| **Cerrar el puño** | Las partículas se contraen a su forma original |
| **Quitar la mano** | Las partículas vuelven a una **nube dispersa** |
| **Arrastrar con el mouse** | Orbitar manualmente la cámara |

---

## 💬 Frases

| Gesto | Frase |
|---|---|
| ✌️ Peace | `BIENVENIDOS A LA DEMOSTRACION Y PRESENTACION DE CIENCIA DE DATOS` |

El texto se renderiza convirtiendo los caracteres a posiciones de partículas mediante un canvas oculto.

---

## 🔷 Formas Disponibles

| Forma | Descripción |
|---|---|
| ☁️ Cloud | Nube dispersa (estado por defecto sin mano) |
| ❤️ Heart | Corazón paramétrico |
| 🌌 Galaxy | Galaxia espiral con 3 brazos |
| 🪐 Saturn | Esfera + anillo orbital |
| 🌸 Flower | Rosa polar de 6 pétalos |
| 🧬 DNA | Doble hélice |
| 🔮 Sphere | Esfera uniforme |
| 🧠 Brain | Cerebro con hemisferios y surcos |
| ✌️ Welcome | Texto de bienvenida |

---

## 🚀 Cómo Ejecutar

1. Abre `particle_system.html` en **Google Chrome** (recomendado)
2. Permite el acceso a la **cámara web** cuando el navegador lo solicite
3. Las partículas empiezan como una nube dispersa
4. Muestra tu mano frente a la cámara:
    - ✌️ **Peace**: Mensaje de bienvenida
    - 👌 **OK**: Logo oficial "Ciencia de Datos"
5. Usa el botón **"Apagar Cámara"** en el preview si necesitas pausar el tracking sin cerrar la aplicación
6. Usa los botones del panel para cambiar entre formas manualmente

> **Nota:** Requiere conexión a internet para cargar las librerías (Three.js y MediaPipe) desde CDN.

---

## ⚙️ Detalles Técnicos

### Detección de Gestos

- **Peace (✌️)**: Se detecta cuando solo el índice y medio están extendidos (comparando distancia punta-muñeca vs articulación PIP-muñeca)
- **Posición**: landmark 9 (centro de la palma) para tracking X/Y
- **Rotación**: `Math.atan2()` entre landmarks 0 (muñeca) y 9 (palma)
- **Apertura**: ratio de distancia punta-muñeca vs base-muñeca para cada dedo

### Text-to-Particles Engine

- Renderiza texto en un **canvas oculto** (1024×320 px)
- Escanea los píxeles y muestrea 5,000 posiciones donde hay texto visible
- Mapea las coordenadas 2D del canvas a posiciones 3D
- Auto-rotación deshabilitada para mantener el texto legible

### Suavizado

Todos los valores usan **lerp** para evitar movimientos bruscos:

```
smoothValue += (rawValue - smoothValue) * SMOOTH_FACTOR
```

- `HAND_TRACK_SMOOTH = 0.07` para posición y rotación
- `GESTURE_SMOOTH = 0.08` para apertura de la mano
- Sin mano: valores regresan a 0 con suavizado más lento (`× 0.5`)

### Renderizado

- **15,000 partículas** con `THREE.Points`
- **Colores por Partícula**: Cada punto puede tener su propio color (Soporte RGB individual).
- `AdditiveBlending` para efecto de brillo acumulativo
- Las partículas se mueven un **4% por frame** hacia su objetivo (`LERP_SPEED = 0.04`)
- Centrado dinámico: El texto se centra calculando el centroide de los píxeles muestreados.
- Logo Reconstruido: 2.5D con cerebro bicolor, nodos brillantes y **auto-rotación**.
- Rotación automática lenta en Y + control por mouse + control por mano (con inercia para el logo)

---

## 📁 Estructura

```
EXTERNADO FEST/
├── particle_system.html   # Aplicación completa (single-file)
└── README.md              # Este archivo
```

---

## 📝 Changelog

- **v4.1** — Gesto 👌 OK para el Logo, auto-rotación y suavizado de movimiento profesional.
- **v4.0** — Reconstrucción de Logo "CIENCIA DE DATOS", colores dinámicos por partícula y nodos brillantes.
- **v3.1** — Aumento a 15,000 partículas, centrado perfecto de texto y botón de ON/OFF para cámara
- **v3.0** — Detección de gesto ✌️ Peace, texto de bienvenida como partículas, nube por defecto sin mano
- **v2.0** — Tracking de posición y rotación de la mano para mover/rotar la figura 3D
- **v1.0** — Sistema de partículas con 7 formas y control de expansión/contracción por apertura de mano
