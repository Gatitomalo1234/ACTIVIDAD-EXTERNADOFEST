# ✦ 3D Particle System — Hand Gesture Control

Sistema de partículas 3D interactivo controlado por **gestos de la mano** en tiempo real. Construido con Three.js y MediaPipe Hands.

![Three.js](https://img.shields.io/badge/Three.js-r128-black?logo=three.js)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hands-4285F4?logo=google)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 Descripción

Una experiencia visual interactiva donde **5,000 partículas** se organizan en formas 3D y responden a los movimientos de tu mano capturados por la webcam. Ideal para demostraciones, festivales y eventos de tecnología.

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
| **Mover la mano** (izq/der, arriba/abajo) | La figura se mueve siguiendo la posición de la mano |
| **Rotar/inclinar la mano** | La figura rota en el eje Z |
| **Abrir la mano** | Las partículas se expanden hacia afuera |
| **Cerrar el puño** | Las partículas se contraen a su forma original |
| **Quitar la mano** | La figura vuelve suavemente al centro |
| **Arrastrar con el mouse** | Orbitar manualmente la cámara |

---

## 🔷 Formas Disponibles

| Forma | Descripción |
|---|---|
| ❤️ Heart | Corazón paramétrico |
| 🌌 Galaxy | Galaxia espiral con 3 brazos |
| 🪐 Saturn | Esfera + anillo orbital |
| 🌸 Flower | Rosa polar de 6 pétalos |
| 🧬 DNA | Doble hélice |
| 🔮 Sphere | Esfera uniforme |
| 🧠 Brain | Cerebro con hemisferios y surcos |

---

## 🚀 Cómo Ejecutar

1. Abre `particle_system.html` en **Google Chrome** (recomendado)
2. Permite el acceso a la **cámara web** cuando el navegador lo solicite
3. Muestra tu mano frente a la cámara para controlar las partículas

> **Nota:** Requiere conexión a internet para cargar las librerías (Three.js y MediaPipe) desde CDN.

---

## ⚙️ Detalles Técnicos

### Detección de la Mano

- Se usa el **landmark 9** (base del dedo medio / centro de la palma) para rastrear la posición X/Y de la mano.
- La **rotación** se calcula con `Math.atan2()` entre el landmark 0 (muñeca) y el landmark 9 (centro de la palma).
- La **apertura** de la mano se mide comparando la distancia de cada punta de dedo a la muñeca vs. la distancia de la articulación base a la muñeca.

### Suavizado

Todos los valores de tracking usan **interpolación lineal (lerp)** para evitar movimientos bruscos:

```
smoothValue += (rawValue - smoothValue) * SMOOTH_FACTOR
```

- `HAND_TRACK_SMOOTH = 0.07` para posición y rotación
- `GESTURE_SMOOTH = 0.08` para apertura de la mano
- Cuando no se detecta mano, los valores regresan a 0 con suavizado más lento (`× 0.5`)

### Renderizado

- **5,000 partículas** con `THREE.Points`
- `AdditiveBlending` para efecto de brillo acumulativo
- Las partículas se mueven un **4% por frame** hacia su objetivo (`LERP_SPEED = 0.04`)
- Rotación automática lenta en Y + control por mouse + control por mano

---

## 📁 Estructura

```
EXTERNADO FEST/
├── particle_system.html   # Aplicación completa (single-file)
└── README.md              # Este archivo
```

---

## 📝 Changelog

- **v2.0** — Tracking de posición y rotación de la mano para mover/rotar la figura 3D
- **v1.0** — Sistema de partículas con 7 formas y control de expansión/contracción por apertura de mano
