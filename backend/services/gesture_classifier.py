import numpy as np
from typing import Dict, List, Optional
import logging
import math

logger = logging.getLogger(__name__)

class GestureClassifier:
    """
    Clasificador de gestos basado en la geometría de los puntos clave de la mano.
    Identifica 5 gestos básicos: índice extendido, puño cerrado, pulgar arriba,
    mano abierta y pinza.
    """
    
    # Índices de landmarks importantes de MediaPipe
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_FINGER_MCP = 5
    INDEX_FINGER_PIP = 6
    INDEX_FINGER_DIP = 7
    INDEX_FINGER_TIP = 8
    MIDDLE_FINGER_MCP = 9
    MIDDLE_FINGER_PIP = 10
    MIDDLE_FINGER_DIP = 11
    MIDDLE_FINGER_TIP = 12
    RING_FINGER_MCP = 13
    RING_FINGER_PIP = 14
    RING_FINGER_DIP = 15
    RING_FINGER_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20
    
    def __init__(self, confidence_thresholds: Optional[Dict[str, float]] = None):
        """
        Inicializa el clasificador con umbrales de confianza personalizados.
        
        Args:
            confidence_thresholds: Diccionario con umbrales mínimos por gesto
        """
        self.thresholds = confidence_thresholds or {
            'index_point': 0.85,  # Índice extendido
            'fist': 0.80,         # Puño cerrado
            'thumbs_up': 0.75,    # Pulgar arriba
            'open_hand': 0.70,    # Mano abierta
            'pinch': 0.65         # Pinza
        }
        
        logger.info(f"GestureClassifier inicializado con umbrales: {self.thresholds}")
    
    def classify(self, landmarks: List[Dict]) -> Dict:
        """
        Clasifica el gesto basándose en los landmarks de la mano.
        
        Args:
            landmarks: Lista de 21 puntos clave de la mano
            
        Returns:
            Diccionario con:
                - gesture: Nombre del gesto detectado
                - confidence: Nivel de confianza (0-1)
                - action: Acción asociada al gesto
                - details: Información adicional del gesto
        """
        if not landmarks or len(landmarks) != 21:
            return {'gesture': 'unknown', 'confidence': 0.0, 'action': 'none'}
        
        # Convertir a array numpy
        lm_array = np.array([[lm['x'], lm['y'], lm['z']] for lm in landmarks])
        
        # Verificar cada gesto en orden de prioridad
        gestures = [
            ('index_point', self._is_index_point, 'move_cursor'),
            ('fist', self._is_fist, 'left_click'),
            ('thumbs_up', self._is_thumbs_up, 'right_click'),
            ('open_hand', self._is_open_hand, 'scroll'),
            ('pinch', self._is_pinch, 'drag_drop')
        ]
        
        for gesture_name, detector_func, action in gestures:
            confidence = detector_func(lm_array)
            if confidence >= self.thresholds[gesture_name]:
                return {
                    'gesture': gesture_name,
                    'confidence': confidence,
                    'action': action,
                    'details': self._get_gesture_details(gesture_name, lm_array)
                }
        
        # No se detectó ningún gesto con suficiente confianza
        return {'gesture': 'unknown', 'confidence': 0.0, 'action': 'none'}
    
    def _is_index_point(self, lm: np.ndarray) -> float:
        """Detecta índice extendido (👆) para mover cursor."""
        # Índice extendido, otros dedos doblados
        index_extended = self._is_finger_extended(lm, self.INDEX_FINGER_TIP, self.INDEX_FINGER_MCP)
        middle_folded = not self._is_finger_extended(lm, self.MIDDLE_FINGER_TIP, self.MIDDLE_FINGER_MCP)
        ring_folded = not self._is_finger_extended(lm, self.RING_FINGER_TIP, self.RING_FINGER_MCP)
        pinky_folded = not self._is_finger_extended(lm, self.PINKY_TIP, self.PINKY_MCP)
        
        # Verificar que el índice esté claramente más extendido que los otros dedos
        index_tip_y = lm[self.INDEX_FINGER_TIP][1]
        middle_tip_y = lm[self.MIDDLE_FINGER_TIP][1]
        ring_tip_y = lm[self.RING_FINGER_TIP][1]
        pinky_tip_y = lm[self.PINKY_TIP][1]
        
        # El índice debe estar más alto (valor Y menor) que los otros dedos
        index_highest = (index_tip_y < middle_tip_y and index_tip_y < ring_tip_y and index_tip_y < pinky_tip_y)
        
        if index_extended and middle_folded and ring_folded and pinky_folded and index_highest:
            return 0.95
        elif index_extended and (middle_folded and ring_folded) and index_highest:
            return 0.85
        elif index_extended and index_highest:
            return 0.75
        return 0.0
    
    def _is_fist(self, lm: np.ndarray) -> float:
        """Detecta puño cerrado (✊) para clic izquierdo."""
        # Todos los dedos doblados
        fingers_folded = [
            not self._is_finger_extended(lm, self.INDEX_FINGER_TIP, self.INDEX_FINGER_MCP),
            not self._is_finger_extended(lm, self.MIDDLE_FINGER_TIP, self.MIDDLE_FINGER_MCP),
            not self._is_finger_extended(lm, self.RING_FINGER_TIP, self.RING_FINGER_MCP),
            not self._is_finger_extended(lm, self.PINKY_TIP, self.PINKY_MCP)
        ]
        
        folded_count = sum(fingers_folded)
        if folded_count == 4:
            return 0.95
        elif folded_count == 3:
            return 0.75
        return 0.0
    
    def _is_thumbs_up(self, lm: np.ndarray) -> float:
        """Detecta pulgar arriba (👍) para clic derecho."""
        # Pulgar extendido hacia arriba, otros dedos doblados
        thumb_extended = lm[self.THUMB_TIP][1] < lm[self.THUMB_MCP][1]  # Y más bajo = arriba
        fingers_folded = [
            not self._is_finger_extended(lm, self.INDEX_FINGER_TIP, self.INDEX_FINGER_MCP),
            not self._is_finger_extended(lm, self.MIDDLE_FINGER_TIP, self.MIDDLE_FINGER_MCP),
            not self._is_finger_extended(lm, self.RING_FINGER_TIP, self.RING_FINGER_MCP),
            not self._is_finger_extended(lm, self.PINKY_TIP, self.PINKY_MCP)
        ]
        
        if thumb_extended and sum(fingers_folded) >= 3:
            return 0.90
        return 0.0
    
    def _is_open_hand(self, lm: np.ndarray) -> float:
        """Detecta mano abierta (🖐️) para scroll."""
        # Todos los dedos extendidos y separados
        fingers_extended = [
            self._is_finger_extended(lm, self.INDEX_FINGER_TIP, self.INDEX_FINGER_MCP),
            self._is_finger_extended(lm, self.MIDDLE_FINGER_TIP, self.MIDDLE_FINGER_MCP),
            self._is_finger_extended(lm, self.RING_FINGER_TIP, self.RING_FINGER_MCP),
            self._is_finger_extended(lm, self.PINKY_TIP, self.PINKY_MCP)
        ]
        
        # Verificar que el pulgar también esté extendido
        thumb_extended = self._is_finger_extended(lm, self.THUMB_TIP, self.THUMB_CMC)
        
        # Verificar que los dedos estén separados (distancia entre puntas)
        index_tip = lm[self.INDEX_FINGER_TIP]
        middle_tip = lm[self.MIDDLE_FINGER_TIP]
        ring_tip = lm[self.RING_FINGER_TIP]
        pinky_tip = lm[self.PINKY_TIP]
        
        # Calcular distancias entre dedos adyacentes
        dist_index_middle = np.linalg.norm(index_tip - middle_tip)
        dist_middle_ring = np.linalg.norm(middle_tip - ring_tip)
        dist_ring_pinky = np.linalg.norm(ring_tip - pinky_tip)
        
        # Los dedos deben estar separados
        fingers_separated = (dist_index_middle > 0.03 and dist_middle_ring > 0.03 and dist_ring_pinky > 0.03)
        
        extended_count = sum(fingers_extended)
        if extended_count >= 4 and thumb_extended and fingers_separated:
            return 0.95
        elif extended_count >= 3 and fingers_separated:
            return 0.80
        return 0.0
    
    def _is_pinch(self, lm: np.ndarray) -> float:
        """Detecta pinza (👌) para drag & drop."""
        # Distancia entre pulgar e índice muy pequeña
        thumb_tip = lm[self.THUMB_TIP]
        index_tip = lm[self.INDEX_FINGER_TIP]
        
        distance = np.linalg.norm(thumb_tip - index_tip)
        
        # Verificar que los otros dedos estén extendidos para diferenciar de puño
        middle_extended = self._is_finger_extended(lm, self.MIDDLE_FINGER_TIP, self.MIDDLE_FINGER_MCP)
        ring_extended = self._is_finger_extended(lm, self.RING_FINGER_TIP, self.RING_FINGER_MCP)
        pinky_extended = self._is_finger_extended(lm, self.PINKY_TIP, self.PINKY_MCP)
        
        other_fingers_extended = middle_extended and ring_extended and pinky_extended
        
        # Otros dedos deben estar extendidos para ser una pinza clara
        if distance < 0.05 and other_fingers_extended:  # Muy cerca y dedos extendidos
            return 0.95
        elif distance < 0.08 and other_fingers_extended:  # Cerca y dedos extendidos
            return 0.85
        elif distance < 0.05:  # Solo muy cerca
            return 0.75
        return 0.0
    
    def _is_finger_extended(self, lm: np.ndarray, tip_idx: int, mcp_idx: int) -> bool:
        """Verifica si un dedo está extendido comparando tip con MCP."""
        tip = lm[tip_idx]
        mcp = lm[mcp_idx]
        
        # Un dedo está extendido si su punta está más lejos de la muñeca que su base
        wrist = lm[self.WRIST]
        
        tip_dist = np.linalg.norm(tip - wrist)
        mcp_dist = np.linalg.norm(mcp - wrist)
        
        return tip_dist > mcp_dist * 1.1  # 10% más lejos
    
    def _get_gesture_details(self, gesture_name: str, lm: np.ndarray) -> Dict:
        """Obtiene detalles adicionales del gesto para control más preciso."""
        if gesture_name == 'index_point' or gesture_name == 'open_hand':
            # Posición del índice para movimiento de cursor
            index_tip = lm[self.INDEX_FINGER_TIP]
            return {
                'cursor_x': float(index_tip[0]),
                'cursor_y': float(index_tip[1])
            }
        elif gesture_name == 'pinch':
            # Posición de la pinza para drag & drop
            thumb_tip = lm[self.THUMB_TIP]
            index_tip = lm[self.INDEX_FINGER_TIP]
            center = (thumb_tip + index_tip) / 2
            return {
                'pinch_x': float(center[0]),
                'pinch_y': float(center[1]),
                'distance': float(np.linalg.norm(thumb_tip - index_tip))
            }
        return {}