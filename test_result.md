#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: |
  Sistema web de control por gestos usando FastAPI + React + MongoDB.
  Objetivo: Permitir que personas con movilidad reducida controlen acciones mediante gestos de manos.
  
  Gestos implementados:
  - Índice extendido (👆) → mover cursor (85% confianza)
  - Puño cerrado (✊) → clic izquierdo (80% confianza)
  - Pulgar arriba (👍) → clic derecho (75% confianza)
  - Mano abierta (🖐️) → scroll (70% confianza)
  - Pinza (👌) → drag & drop (65% confianza)
  
  Stack: FastAPI, React 19, MediaPipe, OpenCV, MongoDB, WebSocket

backend:
  - task: "Servicio de detección de manos con MediaPipe"
    implemented: true
    working: "NA"
    file: "/app/backend/services/hand_detector.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Implementado HandDetector con MediaPipe para detectar 21 puntos clave por mano. Soporta hasta 2 manos simultáneas."

  - task: "Clasificador de gestos"
    implemented: true
    working: "NA"
    file: "/app/backend/services/gesture_classifier.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Implementado GestureClassifier con lógica basada en geometría de puntos. Clasifica 5 gestos básicos con umbrales configurables."

  - task: "Procesador de gestos con suavizado"
    implemented: true
    working: "NA"
    file: "/app/backend/services/gesture_processor.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Implementado GestureProcessor con buffer circular, suavizado temporal y filtrado de falsos positivos."

  - task: "Modelos de datos (Perfiles, Calibración, Logs)"
    implemented: true
    working: "NA"
    file: "/app/backend/models/profile.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Creados modelos Pydantic para UserProfile, GestureSettings, ActionMapping, CalibrationData y GestureLog."

  - task: "API REST para perfiles"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Implementados endpoints CRUD para perfiles: GET, POST, PUT, DELETE /api/profiles"

  - task: "WebSocket para detección en tiempo real"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Implementado WebSocket en /ws/gestures con ConnectionManager. Procesa frames base64 y devuelve gestos detectados."

  - task: "Endpoint de estadísticas"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Implementado GET /api/gestures/stats para obtener estadísticas de gestos por perfil."

frontend:
  - task: "Componente GestureCamera"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/components/GestureCamera.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Implementado componente con react-webcam y WebSocket. Captura frames, envía al backend y muestra gestos detectados con FPS y latencia."

  - task: "Componente ProfileManager"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/components/ProfileManager.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Implementado gestor de perfiles con CRUD completo. Permite crear, seleccionar y eliminar perfiles de usuario."

  - task: "Componente GestureStats"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/components/GestureStats.jsx"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Implementado componente de estadísticas que muestra gestos recientes y contadores por tipo."

  - task: "Dashboard principal"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/components/Dashboard.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Implementado dashboard con integración de todos los componentes, guía de gestos y diseño responsivo."

  - task: "Componentes UI (Button, Card, Badge)"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/components/ui/"
    stuck_count: 0
    priority: "low"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Creados componentes UI base con Tailwind CSS para consistencia visual."

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 0
  run_ui: true

test_plan:
  current_focus:
    - "WebSocket para detección en tiempo real"
    - "Componente GestureCamera"
    - "API REST para perfiles"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: |
      Sistema de control por gestos completamente implementado.
      
      BACKEND:
      - MediaPipe integrado para detección de 21 puntos clave
      - Clasificador de 5 gestos con umbrales configurables
      - Procesador con suavizado temporal y filtrado
      - API REST completa para perfiles
      - WebSocket para comunicación en tiempo real
      - MongoDB para persistencia
      
      FRONTEND:
      - Dashboard completo con React 19
      - Captura de webcam con react-webcam
      - Visualización en tiempo real de gestos
      - Gestión de perfiles de usuario
      - Estadísticas y métricas de rendimiento
      - Guía visual de gestos
      
      PRÓXIMO PASO: Testing del flujo completo
      - Probar WebSocket connection
      - Verificar detección de gestos con cámara real
      - Validar CRUD de perfiles
      - Confirmar estadísticas