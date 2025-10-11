import cv2
import mediapipe as mp
import numpy as np
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class HandDetector:
    """
    Servicio para detectar manos y extraer puntos clave usando MediaPipe.
    Detecta hasta 21 puntos por mano en tiempo real.
    """
    
    def __init__(self, 
                 static_image_mode: bool = False,
                 max_num_hands: int = 2,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):
        """
        Inicializa el detector de manos.
        
        Args:
            static_image_mode: Si es True, trata cada imagen como independiente
            max_num_hands: Número máximo de manos a detectar
            min_detection_confidence: Confianza mínima para detección
            min_tracking_confidence: Confianza mínima para seguimiento
        """
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        logger.info(f"HandDetector inicializado con max_hands={max_num_hands}")
    
    def detect(self, image: np.ndarray) -> Tuple[Optional[List[Dict]], np.ndarray]:
        """
        Detecta manos en una imagen y extrae puntos clave.
        
        Args:
            image: Imagen BGR (formato OpenCV)
            
        Returns:
            Tupla de (lista de manos detectadas, imagen anotada)
            Cada mano es un diccionario con:
                - landmarks: Lista de 21 puntos (x, y, z) normalizados
                - handedness: 'Left' o 'Right'
                - confidence: Nivel de confianza de la detección
        """
        # Convertir BGR a RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Procesar imagen
        results = self.hands.process(image_rgb)
        
        # Crear imagen anotada
        annotated_image = image.copy()
        
        hands_data = []
        
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                # Dibujar landmarks en la imagen
                self.mp_drawing.draw_landmarks(
                    annotated_image,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
                
                # Extraer información de la mano
                landmarks = []
                for landmark in hand_landmarks.landmark:
                    landmarks.append({
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z
                    })
                
                hand_info = {
                    'landmarks': landmarks,
                    'handedness': handedness.classification[0].label,
                    'confidence': handedness.classification[0].score
                }
                
                hands_data.append(hand_info)
        
        return hands_data if hands_data else None, annotated_image
    
    def get_landmark_array(self, landmarks: List[Dict]) -> np.ndarray:
        """
        Convierte landmarks a un array numpy para procesamiento.
        
        Args:
            landmarks: Lista de puntos clave
            
        Returns:
            Array numpy de forma (21, 3) con coordenadas x, y, z
        """
        return np.array([[lm['x'], lm['y'], lm['z']] for lm in landmarks])
    
    def close(self):
        """Libera recursos."""
        self.hands.close()
        logger.info("HandDetector cerrado")