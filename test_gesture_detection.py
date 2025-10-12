#!/usr/bin/env python3
"""
Script de prueba para verificar la detección de gestos.
Crea una imagen de prueba con MediaPipe y la procesa.
"""

import sys
sys.path.insert(0, '/app/backend')

import cv2
import numpy as np
import base64
import json
from services.hand_detector import HandDetector
from services.gesture_classifier import GestureClassifier
from services.gesture_processor import GestureProcessor

def create_test_image():
    """Crea una imagen de prueba simple."""
    # Crear una imagen negra de 640x480
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Agregar algo de contenido para que no sea completamente negra
    cv2.putText(image, 'Test Image', (200, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    
    return image

def test_detection_pipeline():
    """Prueba el pipeline completo de detección."""
    print("🧪 Iniciando pruebas del sistema de detección de gestos...\n")
    
    # 1. Crear instancias de los servicios
    print("1️⃣ Creando instancias de servicios...")
    try:
        detector = HandDetector(max_num_hands=1, min_detection_confidence=0.5)
        print("   ✅ HandDetector inicializado")
        
        classifier = GestureClassifier()
        print("   ✅ GestureClassifier inicializado")
        
        processor = GestureProcessor()
        print("   ✅ GestureProcessor inicializado")
    except Exception as e:
        print(f"   ❌ Error al inicializar servicios: {e}")
        return False
    
    # 2. Crear imagen de prueba
    print("\n2️⃣ Creando imagen de prueba...")
    test_image = create_test_image()
    print(f"   ✅ Imagen creada: {test_image.shape}")
    
    # 3. Probar detección de manos
    print("\n3️⃣ Probando detección de manos...")
    try:
        hands_data, annotated = detector.detect(test_image)
        
        if hands_data is None:
            print("   ⚠️  No se detectaron manos (esperado en imagen de prueba)")
        else:
            print(f"   ✅ Manos detectadas: {len(hands_data)}")
            for i, hand in enumerate(hands_data):
                print(f"      - Mano {i+1}: {hand['handedness']}, confianza: {hand['confidence']:.2f}")
                print(f"      - Landmarks: {len(hand['landmarks'])} puntos")
    except Exception as e:
        print(f"   ❌ Error en detección: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. Probar clasificación (con landmarks simulados)
    print("\n4️⃣ Probando clasificador de gestos...")
    try:
        # Crear landmarks simulados para un puño cerrado
        fake_landmarks = []
        for i in range(21):
            fake_landmarks.append({'x': 0.5, 'y': 0.5, 'z': 0.0})
        
        gesture_result = classifier.classify(fake_landmarks)
        print(f"   ✅ Clasificación exitosa:")
        print(f"      - Gesto: {gesture_result['gesture']}")
        print(f"      - Confianza: {gesture_result['confidence']:.2f}")
        print(f"      - Acción: {gesture_result['action']}")
    except Exception as e:
        print(f"   ❌ Error en clasificación: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. Probar procesador
    print("\n5️⃣ Probando procesador de gestos...")
    try:
        processed = processor.process(gesture_result)
        print(f"   ✅ Procesamiento exitoso:")
        print(f"      - Gesto: {processed['gesture']}")
        print(f"      - Estable: {processed['stable']}")
        print(f"      - Confianza: {processed['confidence']:.2f}")
    except Exception as e:
        print(f"   ❌ Error en procesamiento: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 6. Probar codificación de imagen (como en WebSocket)
    print("\n6️⃣ Probando codificación de imagen...")
    try:
        _, buffer = cv2.imencode('.jpg', test_image)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        data_url = f"data:image/jpeg;base64,{jpg_as_text}"
        print(f"   ✅ Imagen codificada: {len(data_url)} caracteres")
        
        # Probar decodificación
        if ',' in data_url:
            image_data = base64.b64decode(data_url.split(',')[1])
        else:
            image_data = base64.b64decode(data_url)
        
        nparr = np.frombuffer(image_data, np.uint8)
        decoded_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        print(f"   ✅ Imagen decodificada: {decoded_image.shape}")
    except Exception as e:
        print(f"   ❌ Error en codificación/decodificación: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*60)
    print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
    print("="*60)
    print("\n📝 Nota: Para detectar gestos reales, necesitas:")
    print("   1. Una cámara web funcional")
    print("   2. Buena iluminación")
    print("   3. Colocar tu mano visible frente a la cámara")
    print("   4. Hacer los gestos claramente según la guía")
    
    detector.close()
    return True

if __name__ == "__main__":
    success = test_detection_pipeline()
    sys.exit(0 if success else 1)
