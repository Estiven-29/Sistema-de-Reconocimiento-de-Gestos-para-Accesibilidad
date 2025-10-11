import React, { useState } from 'react';
import GestureCamera from './GestureCamera';
import ProfileManager from './ProfileManager';
import GestureStats from './GestureStats';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Hand, Activity, BarChart3, Info } from 'lucide-react';

const Dashboard = () => {
  const [selectedProfile, setSelectedProfile] = useState(null);
  const [recentGestures, setRecentGestures] = useState([]);

  const handleGestureDetected = (gestureData) => {
    // Añadir el gesto a la lista de gestos recientes
    setRecentGestures(prev => [
      {
        ...gestureData,
        timestamp: new Date().toISOString()
      },
      ...prev.slice(0, 9) // Mantener solo los últimos 10
    ]);
  };

  const gestures = [
    {
      emoji: '☝️',
      name: 'Índice Extendido',
      action: 'Mover Cursor',
      threshold: '85%',
      description: 'Extiende tu dedo índice mientras mantienes los demás dedos cerrados'
    },
    {
      emoji: '✊',
      name: 'Puño Cerrado',
      action: 'Clic Izquierdo',
      threshold: '80%',
      description: 'Cierra todos los dedos formando un puño'
    },
    {
      emoji: '👍',
      name: 'Pulgar Arriba',
      action: 'Clic Derecho',
      threshold: '75%',
      description: 'Levanta el pulgar mientras cierras los demás dedos'
    },
    {
      emoji: '✋',
      name: 'Mano Abierta',
      action: 'Desplazar',
      threshold: '70%',
      description: 'Abre completamente todos los dedos de tu mano'
    },
    {
      emoji: '👌',
      name: 'Pinza',
      action: 'Arrastrar y Soltar',
      threshold: '65%',
      description: 'Junta el pulgar con el índice formando un círculo'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-600 rounded-xl">
                <Hand className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Control por Gestos
                </h1>
                <p className="text-sm text-gray-600 mt-1">
                  Sistema de accesibilidad con visión por computadora
                </p>
              </div>
            </div>
            <Badge variant="success" className="text-sm px-4 py-2">
              <Activity className="h-4 w-4 mr-2" />
              Sistema Activo
            </Badge>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Columna Principal - Cámara */}
          <div className="lg:col-span-2 space-y-6">
            <GestureCamera
              profileId={selectedProfile}
              onGestureDetected={handleGestureDetected}
            />

            {/* Guía de Gestos */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Info className="h-6 w-6" />
                  Guía de Gestos
                </CardTitle>
                <CardDescription>
                  Aprende los gestos disponibles y sus acciones asociadas
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {gestures.map((gesture, index) => (
                    <div
                      key={index}
                      className="p-4 border rounded-lg hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-start gap-3">
                        <span className="text-4xl">{gesture.emoji}</span>
                        <div className="flex-1">
                          <h4 className="font-semibold text-gray-900">{gesture.name}</h4>
                          <p className="text-sm text-blue-600 font-medium mt-1">
                            → {gesture.action}
                          </p>
                          <p className="text-xs text-gray-600 mt-2">{gesture.description}</p>
                          <Badge variant="secondary" className="mt-2 text-xs">
                            Confianza mínima: {gesture.threshold}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Columna Lateral - Perfiles y Estadísticas */}
          <div className="space-y-6">
            <ProfileManager
              onProfileSelect={setSelectedProfile}
              selectedProfileId={selectedProfile}
            />

            <GestureStats
              recentGestures={recentGestures}
              profileId={selectedProfile}
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-600">
            <p>
              Sistema de Control por Gestos - Desarrollado con React, FastAPI y MediaPipe
            </p>
            <p className="mt-2 text-xs text-gray-500">
              Diseñado para personas con movilidad reducida • Versión 1.0.0
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Dashboard;
