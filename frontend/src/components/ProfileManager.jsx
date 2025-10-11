import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { User, Plus, Edit, Trash2, Check } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ProfileManager = ({ onProfileSelect, selectedProfileId }) => {
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newProfileName, setNewProfileName] = useState('');
  const [newProfileDescription, setNewProfileDescription] = useState('');

  useEffect(() => {
    loadProfiles();
  }, []);

  const loadProfiles = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/profiles`);
      setProfiles(response.data);
    } catch (error) {
      console.error('Error al cargar perfiles:', error);
    } finally {
      setLoading(false);
    }
  };

  const createProfile = async (e) => {
    e.preventDefault();
    
    if (!newProfileName.trim()) {
      alert('Por favor ingresa un nombre para el perfil');
      return;
    }

    try {
      const response = await axios.post(`${API}/profiles`, {
        name: newProfileName,
        description: newProfileDescription
      });
      
      setProfiles([...profiles, response.data]);
      setNewProfileName('');
      setNewProfileDescription('');
      setShowCreateForm(false);
      
      // Seleccionar automáticamente el nuevo perfil
      if (onProfileSelect) {
        onProfileSelect(response.data.id);
      }
    } catch (error) {
      console.error('Error al crear perfil:', error);
      alert('Error al crear el perfil');
    }
  };

  const deleteProfile = async (profileId) => {
    if (!window.confirm('¿Estás seguro de que quieres eliminar este perfil?')) {
      return;
    }

    try {
      await axios.delete(`${API}/profiles/${profileId}`);
      setProfiles(profiles.filter(p => p.id !== profileId));
      
      if (selectedProfileId === profileId && onProfileSelect) {
        onProfileSelect(null);
      }
    } catch (error) {
      console.error('Error al eliminar perfil:', error);
      alert('Error al eliminar el perfil');
    }
  };

  const selectProfile = (profileId) => {
    if (onProfileSelect) {
      onProfileSelect(selectedProfileId === profileId ? null : profileId);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className="flex items-center gap-2">
            <User className="h-6 w-6" />
            Perfiles de Usuario
          </span>
          <Button
            onClick={() => setShowCreateForm(!showCreateForm)}
            size="sm"
            variant={showCreateForm ? "outline" : "default"}
          >
            <Plus className="h-4 w-4 mr-2" />
            Nuevo Perfil
          </Button>
        </CardTitle>
        <CardDescription>
          Gestiona perfiles personalizados con configuraciones de gestos
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Formulario de creación */}
        {showCreateForm && (
          <form onSubmit={createProfile} className="space-y-3 p-4 border rounded-lg bg-gray-50">
            <div>
              <label className="block text-sm font-medium mb-1">Nombre del Perfil</label>
              <input
                type="text"
                value={newProfileName}
                onChange={(e) => setNewProfileName(e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
                placeholder="Ej: Mi Perfil Personal"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Descripción (opcional)</label>
              <textarea
                value={newProfileDescription}
                onChange={(e) => setNewProfileDescription(e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
                placeholder="Describe las configuraciones de este perfil"
                rows={2}
              />
            </div>
            <div className="flex gap-2">
              <Button type="submit" size="sm">
                Crear Perfil
              </Button>
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={() => {
                  setShowCreateForm(false);
                  setNewProfileName('');
                  setNewProfileDescription('');
                }}
              >
                Cancelar
              </Button>
            </div>
          </form>
        )}

        {/* Lista de perfiles */}
        {loading ? (
          <div className="text-center py-8 text-gray-500">
            Cargando perfiles...
          </div>
        ) : profiles.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No hay perfiles creados</p>
            <p className="text-sm mt-2">Crea tu primer perfil para comenzar</p>
          </div>
        ) : (
          <div className="space-y-2">
            {profiles.map((profile) => (
              <div
                key={profile.id}
                className={`p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md ${
                  selectedProfileId === profile.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => selectProfile(profile.id)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-semibold">{profile.name}</h4>
                      {selectedProfileId === profile.id && (
                        <Badge variant="success">
                          <Check className="h-3 w-3 mr-1" />
                          Activo
                        </Badge>
                      )}
                      {profile.is_active && (
                        <Badge variant="secondary">Activo</Badge>
                      )}
                    </div>
                    {profile.description && (
                      <p className="text-sm text-gray-600 mt-1">{profile.description}</p>
                    )}
                    <p className="text-xs text-gray-400 mt-2">
                      Creado: {new Date(profile.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex gap-2 ml-4">
                    <Button
                      size="icon"
                      variant="outline"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteProfile(profile.id);
                      }}
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Opción para usar sin perfil */}
        <div
          className={`p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md ${
            selectedProfileId === null
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-200 hover:border-gray-300'
          }`}
          onClick={() => selectProfile(null)}
        >
          <div className="flex items-center gap-2">
            <h4 className="font-semibold">Sin Perfil (Configuración Predeterminada)</h4>
            {selectedProfileId === null && (
              <Badge variant="success">
                <Check className="h-3 w-3 mr-1" />
                Activo
              </Badge>
            )}
          </div>
          <p className="text-sm text-gray-600 mt-1">
            Usa la configuración predeterminada del sistema
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default ProfileManager;
