from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Optional
from datetime import datetime, timezone
import uuid

class GestureSettings(BaseModel):
    """Configuración de sensibilidad y umbrales para cada gesto."""
    index_point_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    fist_threshold: float = Field(default=0.80, ge=0.0, le=1.0)
    thumbs_up_threshold: float = Field(default=0.75, ge=0.0, le=1.0)
    open_hand_threshold: float = Field(default=0.70, ge=0.0, le=1.0)
    pinch_threshold: float = Field(default=0.65, ge=0.0, le=1.0)
    
    # Configuración de sensibilidad
    cursor_sensitivity: float = Field(default=1.0, ge=0.1, le=3.0)
    scroll_sensitivity: float = Field(default=1.0, ge=0.1, le=3.0)
    smoothing_factor: float = Field(default=0.5, ge=0.0, le=1.0)

class ActionMapping(BaseModel):
    """Mapeo personalizado de gestos a acciones."""
    index_point: str = Field(default="move_cursor")
    fist: str = Field(default="left_click")
    thumbs_up: str = Field(default="right_click")
    open_hand: str = Field(default="scroll")
    pinch: str = Field(default="drag_drop")

class UserProfile(BaseModel):
    """Perfil de usuario con configuraciones personalizadas."""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    
    # Configuraciones
    gesture_settings: GestureSettings = Field(default_factory=GestureSettings)
    action_mapping: ActionMapping = Field(default_factory=ActionMapping)
    
    # Metadatos
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True)

class UserProfileCreate(BaseModel):
    """Datos para crear un nuevo perfil."""
    name: str
    description: Optional[str] = None
    gesture_settings: Optional[GestureSettings] = None
    action_mapping: Optional[ActionMapping] = None

class UserProfileUpdate(BaseModel):
    """Datos para actualizar un perfil existente."""
    name: Optional[str] = None
    description: Optional[str] = None
    gesture_settings: Optional[GestureSettings] = None
    action_mapping: Optional[ActionMapping] = None
    is_active: Optional[bool] = None

class CalibrationData(BaseModel):
    """Datos de calibración personalizada."""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    profile_id: str
    gesture_name: str
    
    # Datos de calibración
    sample_count: int = Field(default=0)
    average_confidence: float = Field(default=0.0)
    calibration_data: Dict = Field(default_factory=dict)
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GestureLog(BaseModel):
    """Registro de gestos detectados para análisis."""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    profile_id: Optional[str] = None
    
    gesture: str
    confidence: float
    action: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Metadatos opcionales
    session_id: Optional[str] = None
    duration_ms: Optional[float] = None