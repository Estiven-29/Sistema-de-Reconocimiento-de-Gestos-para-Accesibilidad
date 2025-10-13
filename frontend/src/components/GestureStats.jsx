import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { BarChart3, Clock } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const GestureStats = ({ recentGestures, profileId }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadStats();
    const interval = setInterval(loadStats, 10000); // Actualizar cada 10 segundos
    return () => clearInterval(interval);
  }, [profileId]);

  const loadStats = async () => {
    try {
      setLoading(true);
      const url = profileId 
        ? `${API}/gestures/stats?profile_id=${profileId}`
        : `${API}/gestures/stats`;
      
      const response = await axios.get(url);
      setStats(response.data);
    } catch (error) {
      console.error('Error al cargar estadísticas:', error);
    } finally {
      setLoading(false);
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

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  return (
    <div className="space-y-6">
      {/* Estadísticas Globales */}
      <Card className="gesture-card border-0 shadow-lg">
        <CardHeader className="bg-gradient-to-r from-blue-50 to-cyan-50">
          <CardTitle className="flex items-center gap-2 text-blue-700">
            <BarChart3 className="h-5 w-5 text-blue-600" />
            Estadísticas de Gestos
          </CardTitle>
          <CardDescription className="text-blue-600/80">
            Análisis de los gestos detectados recientemente
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-4 text-gray-500 text-sm">
              Cargando estadísticas...
            </div>
          ) : stats ? (
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Total de gestos</span>
                <Badge variant="secondary">{stats.total_gestures}</Badge>
              </div>
              
              {stats.gesture_counts && Object.keys(stats.gesture_counts).length > 0 && (
                <div className="space-y-2 pt-3 border-t">
                  <h4 className="text-sm font-medium text-gray-700">Por tipo de gesto:</h4>
                  {Object.entries(stats.gesture_counts)
                    .sort((a, b) => b[1] - a[1])
                    .map(([gesture, count]) => (
                      <div key={gesture} className="flex justify-between items-center">
                        <span className="text-sm flex items-center gap-2">
                          <span>{getGestureEmoji(gesture)}</span>
                          <span className="text-gray-600 capitalize">
                            {gesture.replace('_', ' ')}
                          </span>
                        </span>
                        <Badge variant="outline">{count}</Badge>
                      </div>
                    ))}
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-4 text-gray-500 text-sm">
              No hay estadísticas disponibles
            </div>
          )}
        </CardContent>
      </Card>

      {/* Gestos Recientes */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Gestos Recientes
          </CardTitle>
          <CardDescription>
            Historial de esta sesión
          </CardDescription>
        </CardHeader>
        <CardContent>
          {recentGestures.length === 0 ? (
            <div className="text-center py-8 text-gray-500 text-sm">
              No hay gestos detectados aún
            </div>
          ) : (
            <div className="space-y-2">
              {recentGestures.map((gesture, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{getGestureEmoji(gesture.gesture)}</span>
                    <div>
                      <p className="text-sm font-medium capitalize">
                        {gesture.gesture.replace('_', ' ')}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatTimestamp(gesture.timestamp)}
                      </p>
                    </div>
                  </div>
                  <Badge 
                    variant={gesture.confidence > 0.8 ? "success" : "warning"}
                    className="text-xs"
                  >
                    {(gesture.confidence * 100).toFixed(0)}%
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default GestureStats;
