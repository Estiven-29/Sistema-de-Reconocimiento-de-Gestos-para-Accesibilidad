# Sistema de Reconocimiento de Gestos para Accesibilidad Creado por System Sven

Este proyecto implementa un sistema de reconocimiento de gestos en tiempo real para mejorar la accesibilidad digital, permitiendo a los usuarios controlar la computadora mediante gestos capturados por la cámara web.

## Características

- Detección de manos y gestos en tiempo real
- Interfaz web intuitiva y accesible
- Panel de control para personalizar gestos
- Soporte para múltiples perfiles de usuario
- Funciona con o sin conexión a base de datos

## Requisitos del sistema

- Python 3.8 o superior
- Node.js 14.0 o superior
- MongoDB (opcional)
- Cámara web
<img width="1144" height="622" alt="image" src="https://github.com/user-attachments/assets/c9ec0cb7-b94c-431f-88dd-7cbc4a6ef458" />


## Instalación

### Backend

1. Navega al directorio del backend:
   ```
   cd backend
   ```

2. Crea un entorno virtual (recomendado):
   ```
   python -m venv venv
   ```

3. Activa el entorno virtual:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```
     source venv/bin/activate
     ```

4. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

### Frontend

1. Navega al directorio del frontend:
   ```
   cd frontend
   ```

2. Instala las dependencias:
   ```
   npm install
   ```

## Ejecución

### Backend

1. Desde el directorio `backend`, inicia el servidor:
   ```
   python -m uvicorn server:app --reload
   ```

   El servidor estará disponible en `http://127.0.0.1:8000`

   Para ejecutar en modo sin base de datos (solo pruebas de gestos):
   ```
   python -m uvicorn simple_test:app --reload
   ```

### Frontend

1. Desde el directorio `frontend`, inicia la aplicación web:
   ```
   npm start
   ```

   La aplicación estará disponible en `http://localhost:3000`

## Uso

1. Abre la aplicación web en tu navegador
2. Permite el acceso a la cámara cuando se solicite
3. Selecciona o crea un perfil de usuario
4. Comienza a utilizar gestos para controlar tu computadora

## Gestos disponibles

- **Puño cerrado**: Clic izquierdo
- **Mano abierta**: Desplazamiento
- **Índice extendido**: Mover cursor
- **Gesto de paz (V)**: Clic derecho
- **Pulgar arriba**: Aceptar/Confirmar

## Solución de problemas

Si encuentras algún problema durante la instalación o ejecución, consulta el archivo `TROUBLESHOOTING.md` para obtener ayuda.

## Estructura del proyecto

```
Sistema-de-Reconocimiento-de-Gestos-para-Accesibilidad/
├── backend/                # Servidor y lógica de procesamiento
│   ├── models/             # Modelos de datos
│   ├── services/           # Servicios de detección y clasificación
│   ├── server.py           # Servidor principal
│   └── simple_test.py      # Servidor simplificado para pruebas
├── frontend/               # Interfaz de usuario web
│   ├── public/             # Archivos estáticos
│   └── src/                # Código fuente React
└── tests/                  # Pruebas automatizadas
```

## Licencia

Este proyecto está licenciado bajo los términos de la licencia MIT.
