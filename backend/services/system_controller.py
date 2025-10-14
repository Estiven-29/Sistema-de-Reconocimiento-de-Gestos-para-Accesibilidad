import pyautogui
import logging
import time
from typing import Dict, Tuple, Optional

logger = logging.getLogger(__name__)

# Configuración de seguridad para pyautogui
pyautogui.FAILSAFE = True  # Mover el mouse a la esquina superior izquierda detendrá el programa

class SystemController:
    """
    Controla el sistema operativo mediante acciones de mouse y teclado
    basadas en los gestos detectados.
    """
    
    def __init__(self, sensitivity: float = 1.0, scroll_speed: int = 5):
        """
        Inicializa el controlador del sistema.
        
        Args:
            sensitivity: Factor de sensibilidad para el movimiento del cursor (1.0 = normal)
            scroll_speed: Velocidad de desplazamiento al hacer scroll
        """
        self.sensitivity = sensitivity
        self.scroll_speed = scroll_speed
        self.screen_width, self.screen_height = pyautogui.size()
        self.is_dragging = False
        self.last_position = None
        logger.info(f"SystemController inicializado. Resolución de pantalla: {self.screen_width}x{self.screen_height}")
    
    def execute_action(self, action: str, details: Optional[Dict] = None) -> Dict:
        """
        Ejecuta una acción del sistema basada en el gesto detectado.
        
        Args:
            action: Tipo de acción a ejecutar (move_cursor, left_click, etc.)
            details: Detalles adicionales para la acción (posición, etc.)
            
        Returns:
            Diccionario con el resultado de la acción
        """
        details = details or {}
        result = {"success": False, "message": "Acción no implementada"}
        
        try:
            if action == "move_cursor":
                result = self._move_cursor(details)
            elif action == "left_click":
                result = self._left_click()
            elif action == "right_click":
                result = self._right_click()
            elif action == "scroll":
                result = self._scroll(details)
            elif action == "drag_drop":
                result = self._drag_drop(details)
            else:
                logger.warning(f"Acción no reconocida: {action}")
        
        except Exception as e:
            logger.error(f"Error al ejecutar acción {action}: {str(e)}")
            result = {"success": False, "message": f"Error: {str(e)}"}
        
        return result
    
    def _move_cursor(self, details: Dict) -> Dict:
        """Mueve el cursor a la posición indicada."""
        if 'position' not in details:
            return {"success": False, "message": "Posición no especificada"}
        
        # Obtener posición normalizada (0-1) y convertir a coordenadas de pantalla
        norm_x, norm_y = details['position']
        
        # Aplicar sensibilidad y límites de pantalla
        screen_x = max(0, min(self.screen_width, int(norm_x * self.screen_width * self.sensitivity)))
        screen_y = max(0, min(self.screen_height, int(norm_y * self.screen_height * self.sensitivity)))
        
        # Mover el cursor
        pyautogui.moveTo(screen_x, screen_y)
        self.last_position = (screen_x, screen_y)
        
        return {
            "success": True,
            "message": f"Cursor movido a ({screen_x}, {screen_y})"
        }
    
    def _left_click(self) -> Dict:
        """Realiza un clic izquierdo en la posición actual."""
        pyautogui.click()
        return {
            "success": True,
            "message": "Clic izquierdo realizado"
        }
    
    def _right_click(self) -> Dict:
        """Realiza un clic derecho en la posición actual."""
        pyautogui.rightClick()
        return {
            "success": True,
            "message": "Clic derecho realizado"
        }
    
    def _scroll(self, details: Dict) -> Dict:
        """Realiza scroll vertical."""
        direction = details.get('direction', 'down')
        amount = self.scroll_speed * (-1 if direction == 'up' else 1)
        
        pyautogui.scroll(amount)
        return {
            "success": True,
            "message": f"Scroll {direction} realizado"
        }
    
    def _drag_drop(self, details: Dict) -> Dict:
        """Inicia o finaliza una operación de arrastrar y soltar."""
        if not self.is_dragging:
            # Iniciar arrastre
            pyautogui.mouseDown()
            self.is_dragging = True
            return {
                "success": True,
                "message": "Arrastre iniciado"
            }
        else:
            # Finalizar arrastre
            pyautogui.mouseUp()
            self.is_dragging = False
            return {
                "success": True,
                "message": "Arrastre finalizado"
            }