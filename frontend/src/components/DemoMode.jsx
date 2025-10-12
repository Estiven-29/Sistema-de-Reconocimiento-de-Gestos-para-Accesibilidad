import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { PlayCircle, StopCircle, Sparkles } from 'lucide-react';

const DemoMode = ({ onGestureDetected }) => {
  const [isRunning, setIsRunning] = useState(false);
  const [currentDemo, setCurrentDemo] = useState(0);

  const demoGestures = [
    {
      gesture: 'index_point',
      action: 'move_cursor',
      confidence: 0.92,
      stable: true,
      gesture_changed: true,
      duration: 1.5,
      details: { cursor_x: 0.45, cursor_y: 0.60 },
      hands_detected: 1,
      handedness: 'Right'
    },
    {
      gesture: 'fist',
      action: 'left_click',
      confidence: 0.88,
      stable: true,
      gesture_changed: true,
      duration: 0.8,
      details: {},
      hands_detected: 1,
      handedness: 'Right'
    },
    {
      gesture: 'thumbs_up',
      action: 'right_click',
      confidence: 0.85,
      stable: true,
      gesture_changed: true,
      duration: 1.2,
      details: {},
      hands_detected: 1,
      handedness: 'Right'
    },
    {
      gesture: 'open_hand',
      action: 'scroll',
      confidence: 0.90,
      stable: true,
      gesture_changed: true,
      duration: 2.0,
      details: { cursor_x: 0.50, cursor_y: 0.55 },
      hands_detected: 1,
      handedness: 'Left'
    },
    {
      gesture: 'pinch',
      action: 'drag_drop',
      confidence: 0.78,
      stable: true,
      gesture_changed: true,
      duration: 1.8,
      details: { pinch_x: 0.48, pinch_y: 0.52, distance: 0.03 },
      hands_detected: 1,
      handedness: 'Right'
    }
  ];

  useEffect(() => {
    if (isRunning) {
      const interval = setInterval(() => {
        const gesture = demoGestures[currentDemo];
        if (onGestureDetected) {
          onGestureDetected(gesture);
        }
        setCurrentDemo((prev) => (prev + 1) % demoGestures.length);
      }, 3000); // Cambiar cada 3 segundos

      return () => clearInterval(interval);
    }
  }, [isRunning, currentDemo, onGestureDetected]);

  const toggleDemo = () => {
    setIsRunning(!isRunning);
    if (!isRunning) {
      setCurrentDemo(0);
    }
  };

  const getGestureEmoji = (gesture) => {
    const emojis = {
      'index_point': '☝️',
      'fist': '✊',
      'thumbs_up': '👍',
      'open_hand': '✋',
      'pinch': '👌'
    };
    return emojis[gesture] || '❓';
  };

  return (
    <Card className="border-dashed border-2 border-purple-300 bg-purple-50/50">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-purple-600" />
          Modo Demostración
        </CardTitle>
        <CardDescription>
          Simula gestos automáticamente para ver cómo funciona el sistema
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium">
              {isRunning ? 'Demostración en curso' : 'Demostración pausada'}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Ciclo de 5 gestos cada 3 segundos
            </p>
          </div>
          <Button
            onClick={toggleDemo}
            variant={isRunning ? 'destructive' : 'default'}
            size="sm"
          >
            {isRunning ? (
              <>
                <StopCircle className="h-4 w-4 mr-2" />
                Detener
              </>
            ) : (
              <>
                <PlayCircle className="h-4 w-4 mr-2" />
                Iniciar
              </>
            )}
          </Button>
        </div>

        {isRunning && (
          <div className="bg-white rounded-lg p-4 border border-purple-200">
            <p className="text-sm text-gray-600 mb-2">Gesto actual:</p>
            <div className="flex items-center gap-3">
              <span className="text-4xl">{getGestureEmoji(demoGestures[currentDemo].gesture)}</span>
              <div>
                <p className="font-semibold capitalize">
                  {demoGestures[currentDemo].gesture.replace('_', ' ')}
                </p>
                <Badge variant="secondary" className="mt-1">
                  {demoGestures[currentDemo].action}
                </Badge>
              </div>
            </div>
          </div>
        )}

        <div className="text-xs text-gray-500 bg-white p-3 rounded border">
          💡 <strong>Tip:</strong> Usa este modo para probar la interfaz sin necesidad de una cámara.
          Los gestos se simularán automáticamente y verás cómo aparecen en la sección de estadísticas.
        </div>
      </CardContent>
    </Card>
  );
};

export default DemoMode;
