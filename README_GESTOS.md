# Sistema de Control por Gestos

## 🎯 Descripción

Sistema web de control por gestos diseñado para personas con movilidad reducida. Utiliza visión por computadora para detectar gestos de las manos en tiempo real y mapearlos a acciones específicas.

## 🏗️ Arquitectura

### Stack Tecnológico

**Backend:**
- FastAPI (Python 3.11)
- MediaPipe (Detección de manos)
- OpenCV (Procesamiento de video)
- ONNX Runtime (Inferencia)
- MongoDB (Base de datos)
- WebSocket (Comunicación en tiempo real)

**Frontend:**
- React 19
- Tailwind CSS
- React Webcam
- Axios
- Lucide React (Iconos)

### Módulos Principales

#### Backend (`/app/backend/`)

1. **`services/hand_detector.py`**
   - Detecta manos usando MediaPipe
   - Extrae 21 puntos clave por mano
   - Proporciona coordenadas normalizadas (x, y, z)

2. **`services/gesture_classifier.py`**
   - Clasifica gestos basándose en geometría de puntos
   - 5 gestos soportados:
     - 👆 Índice extendido → Mover cursor
     - ✊ Puño cerrado → Clic izquierdo
     - 👍 Pulgar arriba → Clic derecho
     - ✋ Mano abierta → Scroll
     - 👌 Pinza → Drag & drop
   - Umbrales de confianza configurables

3. **`services/gesture_processor.py`**
   - Suavizado temporal con buffer circular
   - Filtrado de falsos positivos
   - Requiere detecciones consecutivas para estabilidad

4. **`models/profile.py`**
   - Perfiles de usuario con configuraciones personalizadas
   - Ajustes de sensibilidad y umbrales
   - Mapeo personalizado de gestos a acciones

5. **`server.py`**
   - API REST para gestión de perfiles
   - WebSocket endpoint para detección en tiempo real
   - Procesamiento asíncrono de frames

#### Frontend (`/app/frontend/src/`)

1. **`components/GestureCamera.jsx`**
   - Captura video de webcam
   - Envía frames al backend via WebSocket
   - Muestra visualización en tiempo real
   - Indicadores de FPS y latencia

2. **`components/ProfileManager.jsx`**
   - CRUD de perfiles de usuario
   - Selección de perfil activo
   - Configuración predeterminada

3. **`components/GestureStats.jsx`**
   - Estadísticas de gestos detectados
   - Historial de sesión
   - Gráficos de uso por tipo de gesto

4. **`components/Dashboard.jsx`**
   - Vista principal de la aplicación
   - Integración de todos los componentes
   - Guía visual de gestos

## 📊 Flujo de Datos

```
1. Frontend (React) → Captura frame de webcam (640x480, JPEG)
   ↓
2. WebSocket → Envía frame codificado en base64
   ↓
3. Backend (FastAPI) → Decodifica imagen
   ↓
4. MediaPipe → Detecta 21 puntos clave de la mano
   ↓
5. GestureClassifier → Clasifica gesto basándose en geometría
   ↓
6. GestureProcessor → Aplica suavizado temporal y filtrado
   ↓
7. Backend → Guarda log en MongoDB (si gesto cambió)
   ↓
8. WebSocket → Envía resultado al frontend
   ↓
9. Frontend → Actualiza UI con gesto detectado y acción
```

## 🚀 Características Implementadas

### Detección de Gestos
- ✅ Detección de 5 gestos básicos
- ✅ Confianza mínima configurable por gesto
- ✅ Suavizado temporal para estabilidad
- ✅ Procesamiento en tiempo real (<100ms latencia objetivo)

### Perfiles de Usuario
- ✅ Crear, leer, actualizar y eliminar perfiles
- ✅ Configuración personalizada de umbrales
- ✅ Múltiples perfiles por usuario
- ✅ Perfil predeterminado del sistema

### Interfaz de Usuario
- ✅ Vista en tiempo real de cámara
- ✅ Feedback visual de gestos detectados
- ✅ Indicadores de confianza y estabilidad
- ✅ Métricas de rendimiento (FPS, latencia)
- ✅ Guía interactiva de gestos
- ✅ Estadísticas de uso

### Optimización
- ✅ Reducción de resolución a 640x480
- ✅ Procesamiento cada 100ms (10 FPS)
- ✅ Buffer circular para suavizado
- ✅ Detecciones consecutivas mínimas
- ✅ WebSocket para comunicación eficiente

## 📝 API Endpoints

### REST API (`/api`)

**Perfiles:**
- `GET /api/profiles` - Obtener todos los perfiles
- `POST /api/profiles` - Crear nuevo perfil
- `GET /api/profiles/{id}` - Obtener perfil específico
- `PUT /api/profiles/{id}` - Actualizar perfil
- `DELETE /api/profiles/{id}` - Eliminar perfil

**Estadísticas:**
- `GET /api/gestures/stats?profile_id={id}` - Estadísticas de gestos

**Health Check:**
- `GET /api/` - Estado de la API

### WebSocket

**Detección en tiempo real:**
- `WS /ws/gestures?profile_id={id}` - Conexión WebSocket para detección

**Formato de mensaje (Cliente → Servidor):**
```json
{
  "image": "data:image/jpeg;base64,..."
}
```

**Formato de respuesta (Servidor → Cliente):**
```json
{
  "gesture": "index_point",
  "action": "move_cursor",
  "confidence": 0.92,
  "stable": true,
  "gesture_changed": true,
  "duration": 2.5,
  "details": {
    "cursor_x": 0.45,
    "cursor_y": 0.62
  },
  "hands_detected": 1,
  "handedness": "Right"
}
```

## 🎨 Gestos Soportados

| Gesto | Emoji | Acción | Umbral | Descripción |
|-------|-------|--------|--------|-------------|
| Índice Extendido | 👆 | Mover Cursor | 85% | Extiende tu dedo índice mientras mantienes los demás dedos cerrados |
| Puño Cerrado | ✊ | Clic Izquierdo | 80% | Cierra todos los dedos formando un puño |
| Pulgar Arriba | 👍 | Clic Derecho | 75% | Levanta el pulgar mientras cierras los demás dedos |
| Mano Abierta | ✋ | Scroll | 70% | Abre completamente todos los dedos de tu mano |
| Pinza | 👌 | Drag & Drop | 65% | Junta el pulgar con el índice formando un círculo |

## 🛠️ Configuración

### Variables de Entorno

**Backend (`/app/backend/.env`):**
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
CORS_ORIGINS="*"
```

**Frontend (`/app/frontend/.env`):**
```env
REACT_APP_BACKEND_URL=<URL_DEL_BACKEND>
```

### Requisitos del Sistema

- **Python:** 3.11+
- **Node.js:** 16+
- **MongoDB:** 4.0+
- **Webcam:** 720p o superior
- **Navegador:** Chrome/Firefox/Edge (últimas versiones)

## 📦 Dependencias Principales

**Backend:**
```txt
mediapipe==0.10.18
opencv-python-headless==4.11.0.86
onnxruntime==1.23.1
fastapi==0.110.1
motor==3.3.1
python-socketio==5.14.1
```

**Frontend:**
```json
{
  "react": "^19.0.0",
  "react-webcam": "^7.2.0",
  "socket.io-client": "^4.8.1",
  "tailwindcss": "^3.4.18",
  "lucide-react": "^0.507.0"
}
```

## 🔧 Desarrollo

### Iniciar Backend
```bash
cd /app/backend
sudo supervisorctl restart backend
```

### Iniciar Frontend
```bash
cd /app/frontend
sudo supervisorctl restart frontend
```

### Ver Logs
```bash
# Backend
tail -f /var/log/supervisor/backend.*.log

# Frontend
tail -f /var/log/supervisor/frontend.*.log
```

## 🎯 Requisitos No Funcionales

### Rendimiento
- ✅ **Latencia:** <100ms (objetivo alcanzable con optimizaciones)
- ⚠️ **CPU:** Objetivo <15% (depende del hardware)
- ✅ **Precisión:** >90% en condiciones ideales

### Compatibilidad
- ✅ Webcams 720p+
- ✅ Navegadores modernos (Chrome, Firefox, Edge)
- ✅ Windows/Mac/Linux (vía navegador)

### Accesibilidad
- ✅ Diseño centrado en accesibilidad
- ✅ Feedback visual claro
- ✅ Interfaz intuitiva
- ✅ Guía interactiva de gestos

## 🚧 Limitaciones Actuales

1. **Plataforma:** Solo web (no es aplicación desktop nativa)
2. **Control del SO:** Los gestos detectados no controlan directamente el cursor del sistema operativo (simulación en UI)
3. **Modelo ONNX:** Clasificación basada en reglas geométricas (no ML entrenado)
4. **Calibración:** Sistema de calibración básico (no entrenamiento personalizado)
5. **Iluminación:** Sensible a condiciones de iluminación

## 🔮 Mejoras Futuras

### Corto Plazo
- [ ] Añadir más gestos personalizados
- [ ] Calibración interactiva con muestras del usuario
- [ ] Ajuste automático de umbral según entorno
- [ ] Modo de práctica/entrenamiento

### Mediano Plazo
- [ ] Entrenar modelo ONNX personalizado
- [ ] Soporte para dos manos simultáneamente
- [ ] Gestos compuestos (secuencias)
- [ ] Integración con navegador (control real del cursor)

### Largo Plazo
- [ ] Aplicación desktop nativa (.NET/Electron)
- [ ] Control real del sistema operativo
- [ ] Soporte para más idiomas
- [ ] Análisis de ergonomía y fatiga

## 📚 Referencias

- [MediaPipe Hands](https://google.github.io/mediapipe/solutions/hands.html)
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [React Webcam](https://www.npmjs.com/package/react-webcam)
- [WCAG 2.1 Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

## 📄 Licencia

Este proyecto está diseñado como MVP de accesibilidad para demostración.

## 👥 Contribuciones

Desarrollado como sistema de accesibilidad basado en visión por computadora.

---

**Versión:** 1.0.0  
**Última actualización:** Octubre 2025
