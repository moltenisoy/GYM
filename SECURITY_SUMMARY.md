# Security Summary - Sistema GYM v2.0

## Estado Actual de Seguridad

Este documento detalla el estado actual de seguridad del sistema y las recomendaciones para producción.

---

## ✅ Implementaciones de Seguridad Actuales

### 1. Autenticación
- ✅ **Contraseñas hasheadas**: Se usa SHA256 para hash de contraseñas
- ✅ **No hay contraseñas en texto plano**: Ni en BD ni en código
- ✅ **Validación de credenciales**: Verificación en servidor antes de autorizar

### 2. Control de Acceso
- ✅ **Sistema de permisos**: Flag `permiso_acceso` por usuario
- ✅ **Validación en servidor**: Todos los endpoints verifican permisos
- ✅ **Bloqueo de usuarios**: Administrador puede desactivar acceso

### 3. Validación de Sesiones
- ✅ **Validación de 72 horas**: Usuarios deben sincronizar cada 3 días
- ✅ **Bloqueo automático**: Si pasan 72h sin sync, se fuerza re-login
- ✅ **Actualización de timestamps**: Cada sync actualiza `last_sync`

### 4. Persistencia de Datos
- ✅ **Base de datos SQLite**: Datos persisten entre sesiones
- ✅ **Thread-safety**: Lock para operaciones concurrentes
- ✅ **Transacciones**: Operaciones atómicas en BD

### 5. Manejo de Credenciales Locales
- ✅ **Almacenamiento local**: Credenciales guardadas en archivo JSON
- ✅ **Ofuscación básica**: Hash SHA256 almacenado (no contraseña plana)
- ⚠️ **Ubicación**: `data/hija_local/credentials.json`

---

## ⚠️ Vulnerabilidades Conocidas (No Críticas)

### 1. Hashing de Contraseñas - SHA256 (**py/weak-sensitive-data-hashing**)

#### Descripción
El sistema usa SHA256 para hashear contraseñas, que no es óptimo para este propósito ya que:
- Es demasiado rápido (vulnerable a ataques de fuerza bruta)
- No usa salt automáticamente
- No es computacionalmente costoso

#### Ubicaciones
- `madre_db.py:104` - Función `hash_password()`
- `hija_comms.py:37` - Almacenamiento de credenciales
- `hija_comms.py:76` - Verificación de contraseñas

#### Impacto
- **Bajo en entorno de prueba**: 3 usuarios conocidos
- **Medio en producción**: Si la BD se compromete, las contraseñas pueden ser crackeadas

#### Estado
- ✅ **Documentado**: Mencionado en README.md y NUEVAS_FUNCIONALIDADES.md
- ⚠️ **No resuelto**: Se mantiene SHA256 por simplicidad del prototipo
- 📋 **Recomendación**: Migrar a bcrypt/argon2 antes de producción

#### Solución Recomendada
```python
# Instalar bcrypt
# pip install bcrypt

import bcrypt

def hash_password(password: str) -> str:
    """Hash de contraseña usando bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, password_hash: str) -> bool:
    """Verifica una contraseña contra su hash."""
    return bcrypt.checkpw(password.encode(), password_hash.encode())
```

### 2. Almacenamiento de Credenciales Locales

#### Descripción
Las credenciales se guardan en un archivo JSON en el sistema de archivos local:
- `data/hija_local/credentials.json`
- Contiene username y password_hash
- Permisos de archivo estándar

#### Impacto
- **Bajo**: Solo hash almacenado, no contraseña plana
- **Medio**: Si el sistema es comprometido, el hash puede obtenerse

#### Solución Recomendada
Usar el módulo `keyring` de Python:
```python
import keyring

# Guardar
keyring.set_password("GYM_APP", username, password_hash)

# Recuperar
password_hash = keyring.get_password("GYM_APP", username)
```

### 3. Comunicación HTTP No Cifrada

#### Descripción
El sistema usa HTTP sin cifrado (no HTTPS)

#### Impacto
- **Bajo en red local**: Traffic puede ser interceptado en la red
- **Alto en internet**: Contraseñas y datos viajan en claro

#### Solución Recomendada
- Implementar HTTPS/SSL con certificados
- Usar FastAPI con `uvicorn --ssl-keyfile --ssl-certfile`

---

## 🔒 Mejoras Recomendadas para Producción

### Prioridad Alta

1. **Migrar a bcrypt para contraseñas**
   ```bash
   pip install bcrypt
   ```
   - Reemplazar `hash_password()` y `verify_password()` en `madre_db.py`
   - Regenerar hashes de usuarios existentes

2. **Implementar HTTPS/SSL**
   - Obtener certificados SSL (Let's Encrypt para producción)
   - Configurar uvicorn con SSL
   - Actualizar URLs en `hija_comms.py`

3. **Usar keyring para credenciales locales**
   ```bash
   pip install keyring
   ```
   - Reemplazar almacenamiento en JSON
   - Usar sistema de credenciales del OS

### Prioridad Media

4. **Implementar JWT para sesiones**
   ```bash
   pip install pyjwt
   ```
   - Token de sesión con expiración
   - Refresh tokens
   - Invalidación de tokens

5. **Rate Limiting en API**
   ```bash
   pip install slowapi
   ```
   - Limitar intentos de login
   - Prevenir ataques de fuerza bruta

6. **Logging de seguridad**
   - Registrar intentos de login
   - Registrar cambios de permisos
   - Registrar accesos denegados

### Prioridad Baja

7. **Migrar a PostgreSQL**
   - Mayor robustez que SQLite
   - Mejor para múltiples conexiones
   - Soporte para SSL

8. **Auditoría de accesos**
   - Tabla de logs de acceso
   - Historial de cambios
   - Dashboard de actividad

9. **2FA (Two-Factor Authentication)**
   - Autenticación en dos pasos
   - Códigos TOTP
   - Backup codes

---

## 📊 Evaluación de Riesgo

| Vulnerabilidad | Probabilidad | Impacto | Riesgo Global | Estado |
|----------------|--------------|---------|---------------|--------|
| SHA256 para passwords | Media | Medio | **MEDIO** | Documentado |
| Credenciales locales en JSON | Baja | Bajo | **BAJO** | Documentado |
| HTTP sin cifrado | Alta | Alto | **ALTO** | Documentado |
| Sin rate limiting | Media | Medio | **MEDIO** | Documentado |
| Sin JWT/sesiones | Baja | Bajo | **BAJO** | Documentado |

### Leyenda
- **BAJO**: Aceptable para prototipo/pruebas
- **MEDIO**: Resolver antes de despliegue interno
- **ALTO**: Resolver antes de producción

---

## 🎯 Plan de Seguridad Recomendado

### Fase 1: Pre-Producción (Crítico)
- [ ] Migrar a bcrypt para passwords
- [ ] Implementar HTTPS/SSL
- [ ] Usar keyring para credenciales locales

### Fase 2: Producción Inicial
- [ ] Implementar JWT para sesiones
- [ ] Añadir rate limiting
- [ ] Implementar logging de seguridad

### Fase 3: Producción Avanzada
- [ ] Migrar a PostgreSQL con SSL
- [ ] Añadir auditoría completa
- [ ] Implementar 2FA opcional

---

## 📝 Conclusiones

### Estado Actual
El sistema implementa **seguridad básica adecuada para prototipo y pruebas**:
- ✅ Contraseñas hasheadas (aunque con algoritmo subóptimo)
- ✅ Control de permisos funcional
- ✅ Validación de sesiones (72 horas)
- ✅ Base de datos persistente con thread-safety

### Para Producción
Se requiere implementar las mejoras de **Prioridad Alta** como mínimo:
1. bcrypt para passwords
2. HTTPS/SSL
3. keyring para credenciales

### Disclaimer
⚠️ **Este sistema NO debe usarse en producción sin implementar las mejoras de seguridad recomendadas.**

El sistema actual es adecuado para:
- ✅ Desarrollo y pruebas
- ✅ Entornos de demostración
- ✅ Redes privadas cerradas
- ❌ **NO para internet público**
- ❌ **NO para datos sensibles**

---

## 📞 Referencias

- [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [Python bcrypt](https://pypi.org/project/bcrypt/)
- [Python keyring](https://pypi.org/project/keyring/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

---

**Fecha**: 2025-11-05  
**Versión**: 2.0  
**Estado**: Prototipo Funcional con Seguridad Básica
