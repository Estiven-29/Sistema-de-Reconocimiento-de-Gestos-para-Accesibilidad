import numpy as np
from typing import Dict, List, Optional, Deque
from collections import deque
import logging
import time

logger = logging.getLogger(__name__)

class GestureProcessor:
    """
    Procesador de gestos con suavizado temporal y filtrado de falsos positivos.
    Mantiene un buffer de gestos recientes para estabilizar la detección.
    """
    
    def __init__(self, 
                 buffer_size: int = 5,
                 min_consecutive: int = 3,
                 smoothing_factor: float = 0.5):
        """
        Inicializa el procesador.
        
        Args:
            buffer_size: Tamaño del buffer circular para gestos
            min_consecutive: Número mínimo de detecciones consecutivas
            smoothing_factor: Factor de suavizado para posiciones (0-1)
        """
        self.buffer_size = buffer_size
        self.min_consecutive = min_consecutive
        self.smoothing_factor = smoothing_factor
        
        # Buffers para suavizado
        self.gesture_buffer: Deque[Dict] = deque(maxlen=buffer_size)
        self.position_buffer: Deque[tuple] = deque(maxlen=buffer_size)
        
        # Estado actual
        self.current_gesture: Optional[str] = None
        self.current_action: Optional[str] = None
        self.gesture_start_time: float = 0
        self.last_position: Optional[tuple] = None
        
        # Estadísticas
        self.total_gestures_processed: int = 0
        self.gesture_counts: Dict[str, int] = {}
        
        logger.info(f"GestureProcessor inicializado (buffer={buffer_size}, min_consecutive={min_consecutive})")
    
    def process(self, gesture_data: Dict) -> Dict:
        """
        Procesa un gesto detectado y aplica suavizado temporal.
        
        Args:
            gesture_data: Diccionario con gesture, confidence, action, details
            
        Returns:
            Gesto procesado y suavizado con información adicional
        """
        self.total_gestures_processed += 1
        
        # Añadir al buffer
        self.gesture_buffer.append(gesture_data)
        
        # Obtener gesto más frecuente en el buffer
        stable_gesture = self._get_stable_gesture()
        
        if not stable_gesture:
            return {
                'gesture': 'unknown',
                'action': 'none',
                'confidence': 0.0,
                'stable': False
            }
        
        # Detectar cambio de gesto
        gesture_changed = stable_gesture['gesture'] != self.current_gesture
        
        if gesture_changed:
            if self.current_gesture:
                duration = time.time() - self.gesture_start_time
                logger.debug(f"Gesto cambió de {self.current_gesture} a {stable_gesture['gesture']} (duración: {duration:.2f}s)")
            
            self.current_gesture = stable_gesture['gesture']
            self.current_action = stable_gesture['action']
            self.gesture_start_time = time.time()
            
            # Actualizar contadores
            self.gesture_counts[self.current_gesture] = self.gesture_counts.get(self.current_gesture, 0) + 1
        
        # Suavizar posición si el gesto la incluye
        smoothed_details = self._smooth_position(stable_gesture.get('details', {}))
        
        # Construir respuesta
        result = {
            'gesture': stable_gesture['gesture'],
            'action': stable_gesture['action'],
            'confidence': stable_gesture['confidence'],
            'stable': True,
            'gesture_changed': gesture_changed,
            'duration': time.time() - self.gesture_start_time,
            'details': smoothed_details
        }
        
        return result
    
    def _get_stable_gesture(self) -> Optional[Dict]:
        """
        Obtiene el gesto más estable del buffer.
        Requiere un número mínimo de detecciones consecutivas.
        """
        if len(self.gesture_buffer) < self.min_consecutive:
            return None
        
        # Contar frecuencias en el buffer
        gesture_votes: Dict[str, List[Dict]] = {}
        
        for gesture_data in self.gesture_buffer:
            gesture_name = gesture_data['gesture']
            if gesture_name not in gesture_votes:
                gesture_votes[gesture_name] = []
            gesture_votes[gesture_name].append(gesture_data)
        
        # Encontrar el gesto más votado
        if not gesture_votes:
            return None
        
        most_common_gesture = max(gesture_votes.items(), key=lambda x: len(x[1]))
        gesture_name, occurrences = most_common_gesture
        
        # Verificar que tenga suficientes votos
        if len(occurrences) < self.min_consecutive:
            return None
        
        # Calcular confianza promedio
        avg_confidence = np.mean([g['confidence'] for g in occurrences])
        
        # Retornar el gesto más reciente de ese tipo con la confianza promedio
        stable = occurrences[-1].copy()
        stable['confidence'] = float(avg_confidence)
        
        return stable
    
    def _smooth_position(self, details: Dict) -> Dict:
        """
        Suaviza las coordenadas de posición usando un filtro exponencial.
        """
        if not details:
            return details
        
        # Identificar coordenadas a suavizar
        position_keys = []
        if 'cursor_x' in details and 'cursor_y' in details:
            position_keys = ['cursor_x', 'cursor_y']
        elif 'pinch_x' in details and 'pinch_y' in details:
            position_keys = ['pinch_x', 'pinch_y']
        
        if not position_keys:
            return details
        
        current_pos = (details[position_keys[0]], details[position_keys[1]])
        
        # Aplicar suavizado exponencial
        if self.last_position:
            smoothed_x = (self.smoothing_factor * current_pos[0] + 
                         (1 - self.smoothing_factor) * self.last_position[0])
            smoothed_y = (self.smoothing_factor * current_pos[1] + 
                         (1 - self.smoothing_factor) * self.last_position[1])
            
            smoothed_pos = (smoothed_x, smoothed_y)
        else:
            smoothed_pos = current_pos
        
        self.last_position = smoothed_pos
        
        # Actualizar detalles
        smoothed_details = details.copy()
        smoothed_details[position_keys[0]] = float(smoothed_pos[0])
        smoothed_details[position_keys[1]] = float(smoothed_pos[1])
        
        return smoothed_details
    
    def reset(self):
        """Reinicia el estado del procesador."""
        self.gesture_buffer.clear()
        self.position_buffer.clear()
        self.current_gesture = None
        self.current_action = None
        self.last_position = None
        logger.info("GestureProcessor reiniciado")
    
    def get_statistics(self) -> Dict:
        """Obtiene estadísticas del procesamiento."""
        return {
            'total_processed': self.total_gestures_processed,
            'gesture_counts': self.gesture_counts,
            'current_gesture': self.current_gesture,
            'buffer_size': len(self.gesture_buffer)
        }