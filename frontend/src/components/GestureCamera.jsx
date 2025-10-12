import React, { useRef, useEffect, useState, useCallback } from 'react';
import Webcam from 'react-webcam';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Video, VideoOff, Activity } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const GestureCamera = ({ profileId, onGestureDetected }) => {
  const webcamRef = useRef(null);
  const socketRef = useRef(null);
  const [isActive, setIsActive] = useState(false);
  const [currentGesture, setCurrentGesture] = useState(null);
  const [confidence, setConfidence] = useState(0);
  const [fps, setFps] = useState(0);
  const [latency, setLatency] = useState(0);
  const frameCountRef = useRef(0);
  const lastTimeRef = useRef(Date.now());

  // Configuración de webcam
  const videoConstraints = {
    width: 640,
    height: 480,
    facingMode: "user"
  };

  // Conectar WebSocket
  useEffect(() => {
    if (isActive) {
      // Construir la URL del WebSocket correctamente
      const backendUrl = new URL(BACKEND_URL);
      const protocol = backendUrl.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${backendUrl.host}/ws/gestures${profileId ? `?profile_id=${profileId}` : ''}`;
      
      console.log('Conectando a WebSocket:', wsUrl);
      
      // Usar WebSocket nativo para conexión directa
      const ws = new WebSocket(wsUrl);
      socketRef.current = ws;

      ws.onopen = () => {
        console.log('✅ WebSocket conectado exitosamente');
      };

      ws.onmessage = (event) => {
        const result = JSON.parse(event.data);
        handleGestureResult(result);
      };

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('WebSocket desconectado');
      };

      return () => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.close();
        }
      };
    }
  }, [isActive, profileId]);

  // Capturar y enviar frames
  useEffect(() => {
    if (!isActive || !socketRef.current) return;

    const interval = setInterval(() => {
      captureAndSendFrame();
    }, 100); // 10 FPS para reducir carga

    return () => clearInterval(interval);
  }, [isActive]);

  const captureAndSendFrame = useCallback(() => {
    if (webcamRef.current && socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const imageSrc = webcamRef.current.getScreenshot();
      
      if (imageSrc) {
        const startTime = Date.now();
        
        socketRef.current.send(JSON.stringify({
          image: imageSrc
        }));

        // Actualizar FPS
        frameCountRef.current++;
        const now = Date.now();
        if (now - lastTimeRef.current >= 1000) {
          setFps(frameCountRef.current);
          frameCountRef.current = 0;
          lastTimeRef.current = now;
        }
      }
    }
  }, []);

  const handleGestureResult = (result) => {
    if (result.error) {
      console.error('Error en detección:', result.error);
      return;
    }

    setCurrentGesture(result);
    setConfidence(result.confidence || 0);
    setLatency(Date.now() - lastTimeRef.current);

    // Notificar al padre si el gesto cambió
    if (result.gesture_changed && onGestureDetected) {
      onGestureDetected(result);
    }
  };

  const toggleCamera = () => {
    setIsActive(!isActive);
    if (isActive) {
      setCurrentGesture(null);
      setConfidence(0);
    }
  };

  const getGestureEmoji = (gesture) => {
    const emojis = {
      'index_point': '☝️',
      'fist': '✊',
      'thumbs_up': '👍',
      'open_hand': '✋',
      'pinch': '👌',
      'none': '❌',
      'unknown': '❓'
    };
    return emojis[gesture] || '❓';
  };

  const getGestureName = (gesture) => {
    const names = {
      'index_point': 'Índice Extendido',
      'fist': 'Puño Cerrado',
      'thumbs_up': 'Pulgar Arriba',
      'open_hand': 'Mano Abierta',
      'pinch': 'Pinza',
      'none': 'Sin mano detectada',
      'unknown': 'Gesto desconocido'
    };
    return names[gesture] || 'Desconocido';
  };

  const getActionName = (action) => {
    const actions = {
      'move_cursor': 'Mover Cursor',
      'left_click': 'Clic Izquierdo',
      'right_click': 'Clic Derecho',
      'scroll': 'Desplazar',
      'drag_drop': 'Arrastrar y Soltar',
      'none': 'Ninguna'
    };
    return actions[action] || 'Ninguna';
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Activity className="h-6 w-6" />
            Detección de Gestos en Tiempo Real
          </span>
          <Button
            onClick={toggleCamera}
            variant={isActive ? "destructive" : "default"}
            size="sm"
          >
            {isActive ? (
              <>
                <VideoOff className="h-4 w-4 mr-2" />
                Detener
              </>
            ) : (
              <>
                <Video className="h-4 w-4 mr-2" />
                Iniciar
              </>
            )}
          </Button>
        </CardTitle>
        <CardDescription>
          Usa tu cámara para detectar gestos de mano y controlar acciones
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Vista de la cámara */}
        <div className="relative bg-gray-900 rounded-lg overflow-hidden" style={{ aspectRatio: '4/3' }}>
          {isActive ? (
            <Webcam
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              videoConstraints={videoConstraints}
              className="w-full h-full object-cover"
              mirrored
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-400">
              <div className="text-center">
                <VideoOff className="h-16 w-16 mx-auto mb-4" />
                <p>Cámara desactivada</p>
                <p className="text-sm">Haz clic en "Iniciar" para comenzar</p>
              </div>
            </div>
          )}

          {/* Overlay de información */}
          {isActive && (
            <div className="absolute top-4 left-4 right-4 flex justify-between items-start">
              <div className="space-y-2">
                <Badge variant="secondary" className="bg-black/70 text-white border-none">
                  FPS: {fps}
                </Badge>
                <Badge variant="secondary" className="bg-black/70 text-white border-none">
                  Latencia: {latency}ms
                </Badge>
              </div>
            </div>
          )}
        </div>

        {/* Información del gesto detectado */}
        {isActive && currentGesture && (
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-500">Gesto Detectado</h4>
              <div className="flex items-center gap-3">
                <span className="text-4xl">{getGestureEmoji(currentGesture.gesture)}</span>
                <div>
                  <p className="font-semibold">{getGestureName(currentGesture.gesture)}</p>
                  <p className="text-sm text-gray-500">
                    Confianza: {(confidence * 100).toFixed(0)}%
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-500">Acción Asociada</h4>
              <div>
                <p className="font-semibold text-blue-600">{getActionName(currentGesture.action)}</p>
                {currentGesture.stable ? (
                  <Badge variant="success">Estable</Badge>
                ) : (
                  <Badge variant="warning">Detectando...</Badge>
                )}
              </div>
            </div>
          </div>
        )}

        {!isActive && (
          <div className="text-center text-gray-500 py-8">
            <p>Activa la cámara para comenzar a detectar gestos</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default GestureCamera;
