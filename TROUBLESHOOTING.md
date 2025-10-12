# 🔧 Guía de Solución de Problemas - Sistema de Control por Gestos

## ❌ Problema: No se detectan gestos cuando los hago para la cámara

### Diagnóstico Paso a Paso

#### 1. ✅ Verificar Permisos de Cámara

**Síntoma:** La cámara no se activa o muestra error de permisos.

**Solución:**
- En Chrome/Edge: Verifica el ícono de cámara en la barra de direcciones
- Permite el acceso a la cámara cuando el navegador lo solicite
- Si ya negaste el permiso, ve a: `chrome://settings/content/camera`
- Busca tu sitio y cambia el permiso a "Permitir"

**En Firefox:**
- Ve a Preferencias → Privacidad y Seguridad → Permisos → Cámara
- Busca tu sitio y permite el acceso

#### 2. 🔌 Verificar Conexión WebSocket

**Síntoma:** Indicador muestra "🔴 Desconectado" en la esquina superior de la cámara.

**Solución:**
```bash
# Verificar que el backend está corriendo
tail -f /var/log/supervisor/backend.*.log

# Reiniciar backend si es necesario
sudo supervisorctl restart backend

# Verificar que el puerto 8001 está escuchando
netstat -tlnp | grep 8001
```

**En el navegador:**
- Abre la consola de desarrollador (F12)
- Busca errores de WebSocket
- Verifica que la URL de conexión sea correcta

#### 3. 💡 Verificar Iluminación y Posición

**Síntoma:** La cámara funciona pero no se detectan gestos.

**Requisitos para detección óptima:**
- ✅ **Iluminación:** Buena iluminación frontal (evitar contraluz)
- ✅ **Distancia:** 30-60 cm de la cámara
- ✅ **Fondo:** Preferible fondo uniforme y contraste con tu mano
- ✅ **Posición:** Mano completamente visible en el frame
- ✅ **Movimiento:** Gestos claros y deliberados (no muy rápidos)

#### 4. 📸 Verificar Calidad de Cámara

**Requisitos mínimos:**
- Resolución: 640x480 (720p recomendado)
- FPS: Mínimo 10 FPS
- Webcam funcional (no virtual)

**Test de cámara:**
```javascript
// Abre la consola del navegador y ejecuta:
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => console.log("✅ Cámara OK:", stream))
  .catch(err => console.error("❌ Error:", err));
```

#### 5. 🎯 Hacer Gestos Correctamente

**Gestos y cómo hacerlos:**

**☝️ Índice Extendido (85% confianza)**
- Extiende SOLO el dedo índice
- Mantén los otros dedos completamente cerrados
- Mantén la posición 1-2 segundos

**✊ Puño Cerrado (80% confianza)**
- Cierra TODOS los dedos firmemente
- Forma un puño compacto
- No escondas el pulgar

**👍 Pulgar Arriba (75% confianza)**
- Levanta el pulgar hacia arriba
- Cierra los otros 4 dedos
- Mantén el pulgar bien extendido

**✋ Mano Abierta (70% confianza)**
- Abre TODOS los dedos
- Extiende la mano completamente
- Separa los dedos ligeramente

**👌 Pinza (65% confianza)**
- Junta pulgar e índice formando un círculo
- Mantén los otros dedos extendidos o semi-cerrados
- El círculo debe ser pequeño y claro

#### 6. 🔍 Verificar Logs del Backend

```bash
# Ver logs en tiempo real
tail -f /var/log/supervisor/backend.*.log

# Buscar errores específicos
tail -n 200 /var/log/supervisor/backend.*.log | grep -i error

# Verificar si MediaPipe está funcionando
cd /app && python test_gesture_detection.py
```

#### 7. 🌐 Verificar Configuración del Navegador

**Restricciones de seguridad:**
- WebSocket solo funciona en contextos seguros (HTTPS o localhost)
- Algunas extensiones pueden bloquear WebSocket
- Modo incógnito puede bloquear cámara

**Probar en otro navegador:**
- Chrome (recomendado)
- Firefox
- Edge

#### 8. 📊 Usar Modo Demostración

**Si todo falla, usa el Modo Demo:**
1. En el Dashboard, busca el card "Modo Demostración"
2. Haz clic en "Iniciar"
3. El sistema simulará gestos automáticamente
4. Esto te permite verificar que el resto del sistema funciona

## 🐛 Errores Comunes y Soluciones

### Error: "NotAllowedError: Permission denied"
**Causa:** Permiso de cámara denegado  
**Solución:** Permitir acceso a cámara en configuración del navegador

### Error: "NotFoundError: No camera found"
**Causa:** No hay cámara disponible  
**Solución:** Conecta una webcam o usa modo demostración

### Error: "WebSocket connection failed"
**Causa:** Backend no está corriendo o URL incorrecta  
**Solución:** Reinicia el backend con `sudo supervisorctl restart backend`

### Error: FPS = 0
**Causa:** Frames no se están capturando  
**Solución:** 
1. Verifica que la cámara esté activa (luz indicadora encendida)
2. Recarga la página
3. Verifica logs del navegador (F12)

### Gesto detectado pero confianza muy baja
**Causa:** Gesto no es lo suficientemente claro  
**Solución:**
1. Mejora la iluminación
2. Acércate más a la cámara
3. Haz el gesto más exagerado
4. Mantén el gesto por 2-3 segundos

### Gestos cambian constantemente (inestables)
**Causa:** Sistema de suavizado no está funcionando  
**Solución:**
1. Mantén la mano más quieta
2. Haz gestos más claros y distintos
3. Aumenta el umbral de confianza en el perfil

## 📱 Checklist Rápido

Antes de reportar un problema, verifica:

- [ ] ✅ Backend está corriendo (`sudo supervisorctl status backend`)
- [ ] ✅ Frontend está corriendo (`sudo supervisorctl status frontend`)
- [ ] ✅ Permisos de cámara otorgados
- [ ] ✅ Cámara funcional (luz encendida)
- [ ] ✅ Buena iluminación
- [ ] ✅ WebSocket conectado (indicador verde)
- [ ] ✅ FPS > 0
- [ ] ✅ Mano visible en el frame
- [ ] ✅ Gestos claros y mantenidos
- [ ] ✅ Sin errores en consola del navegador

## 🧪 Modo de Prueba

### Probar Backend Directamente

```bash
# Test completo del pipeline
cd /app && python test_gesture_detection.py

# Verificar endpoints REST
curl http://localhost:8001/api/
curl http://localhost:8001/api/profiles

# Verificar MongoDB
mongosh --eval "db.adminCommand('ping')"
```

### Probar Frontend

```javascript
// En consola del navegador (F12)

// 1. Verificar que BACKEND_URL está definido
console.log(process.env.REACT_APP_BACKEND_URL);

// 2. Test de conexión a API
fetch(process.env.REACT_APP_BACKEND_URL + '/api/')
  .then(r => r.json())
  .then(d => console.log('✅ API:', d))
  .catch(e => console.error('❌ Error:', e));

// 3. Test de WebSocket
const ws = new WebSocket(
  process.env.REACT_APP_BACKEND_URL.replace('http', 'ws') + '/ws/gestures'
);
ws.onopen = () => console.log('✅ WebSocket OK');
ws.onerror = (e) => console.error('❌ WebSocket Error:', e);
```

## 📞 Soporte

Si después de seguir estos pasos el problema persiste:

1. Captura los logs del backend:
   ```bash
   tail -n 500 /var/log/supervisor/backend.*.log > backend_logs.txt
   ```

2. Captura los logs del navegador (F12 → Console → Copiar todo)

3. Toma un screenshot del error

4. Describe:
   - ¿Qué gesto estás intentando?
   - ¿Qué esperabas que pasara?
   - ¿Qué pasó en realidad?
   - ¿Condiciones de iluminación?
   - ¿Tipo de cámara?

## 💡 Tips para Mejor Detección

1. **Calibración inicial:** Practica cada gesto frente a la cámara
2. **Feedback visual:** Observa la confianza mostrada
3. **Gestos exagerados:** Hazlos más obvios al principio
4. **Consistencia:** Mantén la misma posición de mano
5. **Paciencia:** El sistema requiere 3 detecciones consecutivas para estabilizar
6. **Perfiles:** Crea perfiles con umbrales ajustados a tu entorno

## 🎓 Recursos Adicionales

- **MediaPipe Hands:** https://google.github.io/mediapipe/solutions/hands.html
- **WebRTC troubleshooting:** https://webrtc.github.io/samples/
- **Browser permissions:** chrome://settings/content

---

**Versión:** 1.0.0  
**Última actualización:** Octubre 2025
