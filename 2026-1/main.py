import cv2
import mediapipe as mp
import time
import numpy as np
import random
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# --- Sistema de Partículas para Animaciones ---
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-15, 15)
        self.vy = random.uniform(-15, 15)
        self.life = 255

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 15

    def draw(self, img):
        if self.life > 0:
            color = (random.randint(50,255), random.randint(150,255), random.randint(200,255))
            cv2.circle(img, (int(self.x), int(self.y)), max(2, int(self.life / 25)), color, -1)

# --- Gestor de Resultados de MediaPipe ---
class HandProcessor:
    def __init__(self):
        self.results = None

    def capture_result(self, result: vision.HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        self.results = result

# --- Colisión Circulo-Rectángulo ---
def rect_circle_collision(cx, cy, r, rx, ry, rw, rh):
    closest_x = max(rx, min(cx, rx + rw))
    closest_y = max(ry, min(cy, ry + rh))
    distance_x = cx - closest_x
    distance_y = cy - closest_y
    return (distance_x ** 2) + (distance_y ** 2) < (r ** 2)

def main():
    processor = HandProcessor()
    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.LIVE_STREAM,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        result_callback=processor.capture_result)

    cap = cv2.VideoCapture(0)
    
    # Variables y configuración del minijuego
    WIDTH, HEIGHT = 640, 480
    start_pos = (50, 50)
    player_x, player_y = start_pos
    player_radius = 20
    is_dragging = False

    # (x, y, w, h)
    obstacles = [
        (160, 0, 40, 320),   
        (330, 160, 40, 320), 
        (500, 0, 40, 320)    
    ]
    goal_rect = (550, 360, 80, 80)
    
    game_won = False
    particles = []

    print("Iniciando Juego Laberinto. Presiona 'ESC' en la ventana para salir.")

    with vision.HandLandmarker.create_from_options(options) as landmarker:
        start_time = time.time()
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                continue

            # 1. Asegurar misma resolucion del laberinto para que nunca falle la logica
            image = cv2.resize(image, (WIDTH, HEIGHT))
            # 2. Voltear como espejo para naturalidad
            image = cv2.flip(image, 1)
            
            # Pasar a MediaPipe
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
            timestamp_ms = int((time.time() - start_time) * 1000)
            landmarker.detect_async(mp_image, timestamp_ms)

            # --- DIBUJADO DEL ESCENARIO ---
            # Interfaz base
            cv2.putText(image, "Arrastra la bola azul con el INDICE DERECHO", (10, HEIGHT - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                        
            # Dibujar Muros (Obstaculos)
            for obs in obstacles:
                ox, oy, ow, oh = obs
                cv2.rectangle(image, (ox, oy), (ox+ow, oy+oh), (0, 0, 200), -1)
                cv2.rectangle(image, (ox, oy), (ox+ow, oy+oh), (0, 0, 100), 3) # borde

            # Dibujar Meta
            gx, gy, gw, gh = goal_rect
            pulse = int(5 * np.sin(time.time() * 8)) # Animacion pulsante
            cv2.rectangle(image, (gx - pulse, gy - pulse), (gx+gw + pulse, gy+gh + pulse), (0, 255, 0), 3)
            cv2.rectangle(image, (gx, gy), (gx+gw, gy+gh), (0, 100, 0), -1)
            cv2.putText(image, "META", (gx + 10, gy + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            finger_x, finger_y = None, None

            # --- LOGICA MEDIA PIPE ---
            if processor.results and processor.results.hand_landmarks:
                for idx, hand_landmarks in enumerate(processor.results.hand_landmarks):
                    handedness = processor.results.handedness[idx][0].category_name
                    
                    # ATENCION: Al estar la imagen volteada horizontalmente (modo espejo),
                    # MediaPipe identifica tu mano DERECHA fisica como 'Left' y tu IZQUIERDA fisica como 'Right'
                    is_physical_right_hand = (handedness == "Left")
                    
                    if is_physical_right_hand:
                        # Landmark 8 es la punta del indice
                        index_tip = hand_landmarks[8]
                        finger_x = int(index_tip.x * WIDTH)
                        finger_y = int(index_tip.y * HEIGHT)
                        
                        # Dibujar cursor en el dedo
                        cv2.circle(image, (finger_x, finger_y), 12, (0, 255, 255), -1) # Amarillo
                        cv2.circle(image, (finger_x, finger_y), 15, (255, 255, 255), 2)
                        
                        # Logica de Arrastre
                        dist = np.sqrt((finger_x - player_x)**2 + (finger_y - player_y)**2)
                        # Si el dedo toca la bola se la "lleva" (is_dragging = True)
                        if dist < player_radius + 40:
                            is_dragging = True
                            player_x = finger_x
                            player_y = finger_y
                        else:
                            is_dragging = False
                        break # Solo procesamos una mano derecha
                        
            if finger_x is None:
                is_dragging = False

            # --- FISICAS Y COLISIONES ---
            if not game_won:
                for obs in obstacles:
                    ox, oy, ow, oh = obs
                    # Si chocamos el muro
                    if rect_circle_collision(player_x, player_y, player_radius, ox, oy, ow, oh):
                        # Animacion de choque texto rojo y regresar al inicio
                        cv2.putText(image, "OUCH!", (int(player_x) + 20, int(player_y) - 20), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                        player_x, player_y = start_pos
                        is_dragging = False
                        break

                # Colision con la Meta
                if rect_circle_collision(player_x, player_y, player_radius, gx, gy, gw, gh):
                    game_won = True
                    for _ in range(80): # Generar particulas explosivas
                        particles.append(Particle(player_x, player_y))

            # --- DIBUJAR AL JUGADOR (EL OBJETO ARRASTRABLE) ---
            color_player = (255, 150, 50) if is_dragging else (255, 0, 0)
            if not game_won:
                cv2.circle(image, (int(player_x), int(player_y)), player_radius, color_player, -1)
                cv2.circle(image, (int(player_x), int(player_y)), player_radius, (255, 255, 255), 2)
                # Aura simple
                radius_anim = player_radius + int(3 * abs(np.sin(time.time() * 5)))
                cv2.circle(image, (int(player_x), int(player_y)), radius_anim, (255, 255, 255), 1)
            else:
                cv2.putText(image, "VICTORIA!", (WIDTH//2 - 150, HEIGHT//2), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 255, 255), 4)

            # --- ANIMACION DE PARTICULAS AL GANAR ---
            if particles:
                for p in particles:
                    p.update()
                    p.draw(image)
                particles = [p for p in particles if p.life > 0]
                
                # Despues de ganar y que termine la purpurina, reiniciar la bola al inicio!
                if len(particles) == 0:
                    game_won = False
                    player_x, player_y = start_pos

            cv2.imshow('Laberinto Hand-Tracking', image)

            if cv2.waitKey(5) & 0xFF == 27:
                break
                
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
