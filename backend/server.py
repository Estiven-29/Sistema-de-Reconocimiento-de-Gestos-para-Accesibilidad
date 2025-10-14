from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from typing import List
import uuid
from datetime import datetime, timezone
import json
import base64
import cv2
import numpy as np
import asyncio
from contextlib import asynccontextmanager

# Importar modelos y servicios
from models import (
    UserProfile,
    UserProfileCreate,
    UserProfileUpdate,
    CalibrationData,
    GestureLog
)
from services.hand_detector import HandDetector
from services.gesture_classifier import GestureClassifier
from services.gesture_processor import GestureProcessor
from services.system_controller import SystemController

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Modo sin MongoDB para pruebas de gestos
print("Iniciando en modo sin base de datos para pruebas de gestos")
MONGODB_AVAILABLE = False
client = None
db = None

@asynccontextmanager
async def lifespan(app):
    # Código que se ejecuta al iniciar
    yield
    # Código que se ejecuta al apagar
    logger.info("Servidor apagado")

# Create the main app without a prefix
app = FastAPI(title="Sistema de Control por Gestos", version="1.0.0", lifespan=lifespan)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# ENDPOINTS DE PERFILES
# ============================================================================

@api_router.get("/profiles", response_model=List[UserProfile])
async def get_profiles():
    """Obtener todos los perfiles de usuario"""
    # Devolver un perfil predeterminado en modo sin base de datos
    return [
        {
            "id": "default",
            "name": "Perfil Predeterminado",
            "settings": {
                "gesture_sensitivity": 0.7,
                "scroll_speed": 10,
                "cursor_sensitivity": 1.5
            },
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]

@api_router.post("/profiles", response_model=UserProfile)
async def create_profile(profile_data: UserProfileCreate):
    """Crea un nuevo perfil de usuario."""
    # En modo de prueba, simplemente devolver el perfil predeterminado
    return {
        "id": "default",
        "name": profile_data.name,
        "settings": profile_data.gesture_settings or {},
        "created_at": datetime.now(timezone.utc).isoformat()
    }

@api_router.get("/profiles/{profile_id}", response_model=UserProfile)
async def get_profile(profile_id: str):
    """Obtiene un perfil específico por ID."""
    profile = await db.profiles.find_one({"id": profile_id}, {"_id": 0})
    
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    
    # Convertir timestamps
    if isinstance(profile.get('created_at'), str):
        profile['created_at'] = datetime.fromisoformat(profile['created_at'])
    if isinstance(profile.get('updated_at'), str):
        profile['updated_at'] = datetime.fromisoformat(profile['updated_at'])
    
    return profile

@api_router.put("/profiles/{profile_id}", response_model=UserProfile)
async def update_profile(profile_id: str, update_data: UserProfileUpdate):
    """Actualiza un perfil existente."""
    existing = await db.profiles.find_one({"id": profile_id}, {"_id": 0})
    
    if not existing:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    
    # Actualizar campos
    update_dict = update_data.model_dump(exclude_unset=True)
    update_dict['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.profiles.update_one(
        {"id": profile_id},
        {"$set": update_dict}
    )
    
    # Obtener perfil actualizado
    updated_profile = await db.profiles.find_one({"id": profile_id}, {"_id": 0})
    
    # Convertir timestamps
    if isinstance(updated_profile.get('created_at'), str):
        updated_profile['created_at'] = datetime.fromisoformat(updated_profile['created_at'])
    if isinstance(updated_profile.get('updated_at'), str):
        updated_profile['updated_at'] = datetime.fromisoformat(updated_profile['updated_at'])
    
    return updated_profile

@api_router.delete("/profiles/{profile_id}")
async def delete_profile(profile_id: str):
    """Elimina un perfil."""
    result = await db.profiles.delete_one({"id": profile_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    
    return {"message": "Perfil eliminado exitosamente"}

# ============================================================================
# ENDPOINTS DE GESTOS Y ESTADÍSTICAS
# ============================================================================

@api_router.get("/gestures/stats")
async def get_gesture_stats(profile_id: str = None):
    """Obtiene estadísticas de gestos detectados."""
    query = {}
    if profile_id:
        query["profile_id"] = profile_id
    
    logs = await db.gesture_logs.find(query, {"_id": 0}).to_list(1000)
    
    # Calcular estadísticas
    gesture_counts = {}
    total_count = len(logs)
    
    for log in logs:
        gesture = log.get('gesture', 'unknown')
        gesture_counts[gesture] = gesture_counts.get(gesture, 0) + 1
    
    return {
        "total_gestures": total_count,
        "gesture_counts": gesture_counts,
        "recent_logs": logs[-20:]  # Últimos 20
    }

@api_router.get("/")
async def root():
    """Endpoint de salud de la API."""
    return {
        "message": "Sistema de Control por Gestos API",
        "version": "1.0.0",
        "status": "online"
    }

# ============================================================================
# WEBSOCKET PARA DETECCIÓN EN TIEMPO REAL
# ============================================================================

class ConnectionManager:
    """Gestiona las conexiones WebSocket activas."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.detectors: dict = {}  # websocket -> (detector, classifier, processor, system_controller)
    
    async def connect(self, websocket: WebSocket, profile_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Cargar configuración del perfil si existe
        thresholds = None
        smoothing = 0.5
        
        if profile_id:
            profile = await db.profiles.find_one({"id": profile_id}, {"_id": 0})
            if profile and 'gesture_settings' in profile:
                settings = profile['gesture_settings']
                thresholds = {
                    'index_point': settings.get('index_point_threshold', 0.85),
                    'fist': settings.get('fist_threshold', 0.80),
                    'thumbs_up': settings.get('thumbs_up_threshold', 0.75),
                    'open_hand': settings.get('open_hand_threshold', 0.70),
                    'pinch': settings.get('pinch_threshold', 0.65)
                }
                smoothing = settings.get('smoothing_factor', 0.5)
        
        # Crear instancias de los servicios
        detector = HandDetector(max_num_hands=1, min_detection_confidence=0.5)
        classifier = GestureClassifier(confidence_thresholds=thresholds)
        processor = GestureProcessor(smoothing_factor=smoothing)
        system_controller = SystemController()
        
        self.detectors[websocket] = (detector, classifier, processor, system_controller, profile_id)
        
        logger.info(f"Cliente conectado. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if websocket in self.detectors:
            detector, _, _, _, _ = self.detectors[websocket]
            detector.close()
            del self.detectors[websocket]
        
        logger.info(f"Cliente desconectado. Total: {len(self.active_connections)}")
    
    async def process_frame(self, websocket: WebSocket, frame_data: dict):
        """Procesa un frame y detecta gestos."""
        if websocket not in self.detectors:
            return {"error": "Detector no inicializado"}
        
        detector, classifier, processor, system_controller, profile_id = self.detectors[websocket]
        
        try:
            # Decodificar imagen base64
            image_data = base64.b64decode(frame_data['image'].split(',')[1] if ',' in frame_data['image'] else frame_data['image'])
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {"error": "No se pudo decodificar la imagen"}
            
            # Detectar manos
            hands_data, annotated_image = detector.detect(image)
            
            if not hands_data:
                return {
                    "gesture": "none",
                    "action": "none",
                    "confidence": 0.0,
                    "hands_detected": 0
                }
            
            # Clasificar gesto de la primera mano
            hand = hands_data[0]
            gesture_result = classifier.classify(hand['landmarks'])
            
            # Procesar con suavizado
            processed = processor.process(gesture_result)
            
            # Ejecutar acción del sistema si el gesto es estable
            if processed['stable'] and processed['action'] != 'none':
                action_details = {}
                
                # Preparar detalles según el tipo de acción
                if processed['action'] == 'move_cursor':
                    # Normalizar la posición del índice para mover el cursor
                    index_tip = hand['landmarks'][8]  # Punta del índice
                    # Convertir coordenadas de la imagen a coordenadas normalizadas (0-1)
                    h, w, _ = image.shape
                    action_details['position'] = (index_tip[0] / w, index_tip[1] / h)
                elif processed['action'] == 'scroll':
                    # Determinar dirección del scroll basado en la posición de la mano
                    palm_y = hand['landmarks'][0][1]  # Centro de la palma
                    prev_y = processor.get_previous_position()[1] if processor.get_previous_position() else palm_y
                    action_details['direction'] = 'up' if palm_y < prev_y else 'down'
                
                # Ejecutar la acción correspondiente
                system_controller.execute_action(processed['action'], action_details)
            
            # Guardar log si es un gesto válido y cambió
            if processed['stable'] and processed['gesture_changed'] and processed['gesture'] != 'unknown':
                log = GestureLog(
                    profile_id=profile_id,
                    gesture=processed['gesture'],
                    confidence=processed['confidence'],
                    action=processed['action']
                )
                
                log_doc = log.model_dump()
                log_doc['timestamp'] = log_doc['timestamp'].isoformat()
                
                # Guardar de forma asíncrona sin bloquear
                asyncio.create_task(db.gesture_logs.insert_one(log_doc))
            
            return {
                "gesture": processed['gesture'],
                "action": processed['action'],
                "confidence": processed['confidence'],
                "stable": processed['stable'],
                "gesture_changed": processed['gesture_changed'],
                "duration": processed['duration'],
                "details": processed.get('details', {}),
                "hands_detected": len(hands_data),
                "handedness": hand['handedness']
            }
            
        except Exception as e:
            logger.error(f"Error procesando frame: {e}")
            return {"error": str(e)}

manager = ConnectionManager()

@app.websocket("/ws/gestures")
async def websocket_gesture_detection(websocket: WebSocket, profile_id: str = None):
    """
    WebSocket para detección de gestos en tiempo real.
    
    El cliente envía frames en base64 y recibe resultados de detección.
    """
    await manager.connect(websocket, profile_id)
    
    try:
        while True:
            # Recibir datos del cliente
            data = await websocket.receive_text()
            frame_data = json.loads(data)
            
            # Procesar frame
            result = await manager.process_frame(websocket, frame_data)
            
            # Enviar resultado
            await websocket.send_json(result)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Error en WebSocket: {e}")
        manager.disconnect(websocket)

@app.websocket("/ws/{profile_id}")
async def websocket_endpoint(websocket: WebSocket, profile_id: str):
    await connection_manager.connect(websocket)
    
    # Usar perfil predeterminado para pruebas de gestos
    profile = {
        "id": profile_id or "default",
        "name": "Perfil Predeterminado",
        "settings": {
            "gesture_sensitivity": 0.7,
            "scroll_speed": 10,
            "cursor_sensitivity": 1.5
        }
    }
    
    if not profile:
        await websocket.close(code=1008, reason="Perfil no encontrado")
        return
        
    # Procesar frames
    try:
        while True:
            data = await websocket.receive_text()
            await connection_manager.process_frame(websocket, data, profile)
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)