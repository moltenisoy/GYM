# Compatibilidad Windows y Configuración de Red - GYM v3.0

## 🪟 Compatibilidad Total con Windows

El sistema GYM v3.0 ha sido diseñado para ser **100% compatible con todas las versiones de Windows** y configuraciones de red.

---

## ✅ Versiones de Windows Soportadas

### Windows 7 (SP1 o superior)
- ✅ **Totalmente soportado**
- Requisitos:
  - Python 3.8+ instalado
  - .NET Framework 3.5 o superior
  - 512MB RAM mínimo
  - 100MB espacio en disco

### Windows 8 / 8.1
- ✅ **Totalmente soportado**
- Sin requisitos adicionales
- Soporte nativo para todas las funcionalidades

### Windows 10 (Todas las versiones)
- ✅ **Completamente soportado**
- Rendimiento óptimo
- Todas las características funcionan sin limitaciones
- Incluye versiones:
  - Windows 10 Home
  - Windows 10 Pro
  - Windows 10 Enterprise
  - Windows 10 Education

### Windows 11
- ✅ **Completamente soportado**
- Compatibilidad total con la nueva UI
- Aprovecha mejoras de seguridad de Windows 11

---

## 🔌 Configuraciones de Red Soportadas

### 1. Red Local (LAN)

#### Configuración Básica
```
PC Madre (Servidor)        PC Hija (Cliente)
IP: 192.168.1.100         IP: 192.168.1.101
Puerto: 8000              Conecta a: 192.168.1.100:8000
```

#### Pasos de Configuración:
1. **En la Madre**:
   - Ejecutar: `python madre_main.py`
   - El servidor inicia automáticamente en `0.0.0.0:8000`
   - Anotar la IP local (Cmd → `ipconfig`)

2. **En la Hija**:
   - Editar `hija_comms.py`:
   ```python
   MADRE_BASE_URL = "http://192.168.1.100:8000"
   ```
   - Ejecutar: `python hija_main.py`

#### Firewall
- Windows Firewall preguntará por permisos
- Permitir acceso para Python en redes privadas
- No se requiere configuración manual adicional

---

### 2. WiFi

#### Configuración Idéntica a LAN
- ✅ Funciona exactamente igual que LAN cableada
- Considera:
  - Calidad de señal WiFi
  - Latencia puede ser mayor
  - Uso de WiFi 5GHz recomendado para mejor rendimiento

#### Red Doméstica Típica
```
Internet ──┬── Router WiFi
           │
           ├── PC Madre (WiFi)
           │   192.168.0.10
           │
           ├── PC Hija 1 (WiFi)
           │   192.168.0.11
           │
           └── PC Hija 2 (Ethernet)
               192.168.0.12
```

---

### 3. VPN (Red Privada Virtual)

#### Escenarios Soportados

##### VPN Corporativa
```
Oficina Central          Oficina Remota
PC Madre                 PC Hija
10.8.0.1 ────VPN────> 10.8.0.2
```

##### Configuración:
1. Establecer conexión VPN primero
2. Verificar conectividad: `ping 10.8.0.1`
3. Configurar URL en `hija_comms.py`
4. Ejecutar aplicaciones normalmente

##### Recomendaciones VPN:
- Usar VPN estable (OpenVPN, WireGuard)
- Latencia < 100ms recomendada
- Ancho de banda mínimo: 1 Mbps

---

### 4. Internet Público

#### Configuración con IP Pública

##### Opción A: Port Forwarding
```
Internet
    │
    ├── Router Público (IP: 203.0.113.1)
    │   Port Forwarding: 8000 → 192.168.1.100:8000
    │
    └── PC Madre (192.168.1.100)
```

**Pasos:**
1. En el router, configurar port forwarding:
   - Puerto externo: 8000
   - IP interna: 192.168.1.100
   - Puerto interno: 8000

2. En PC Hija (cualquier lugar del mundo):
   ```python
   MADRE_BASE_URL = "http://203.0.113.1:8000"
   ```

##### Opción B: Servicio de Túnel (ngrok, localtunnel)
```bash
# En PC Madre
ngrok http 8000

# Output:
# Forwarding: https://abc123.ngrok.io -> http://localhost:8000

# En PC Hija
MADRE_BASE_URL = "https://abc123.ngrok.io"
```

**Ventajas:**
- No requiere configurar router
- URL pública temporal
- Ideal para pruebas

---

### 5. Configuraciones Especiales

#### Red Empresarial con Proxy
```python
# En hija_comms.py, modificar __init__:
def __init__(self, base_url: str = MADRE_BASE_URL):
    self.base_url = base_url
    self.session = requests.Session()
    self.session.headers.update({"Content-Type": "application/json"})
    
    # Configurar proxy
    self.session.proxies = {
        'http': 'http://proxy.empresa.com:8080',
        'https': 'http://proxy.empresa.com:8080',
    }
```

#### Red con Autenticación
```python
# Si el proxy requiere autenticación:
self.session.proxies = {
    'http': 'http://usuario:password@proxy.empresa.com:8080',
}
```

---

## 🔥 Configuración de Firewall

### Windows Defender Firewall

#### Permitir Python Automáticamente
1. Al ejecutar primera vez, aparece diálogo
2. Marcar: "Redes privadas" ✅
3. Click "Permitir acceso"

#### Configuración Manual
```powershell
# PowerShell como Administrador
New-NetFirewallRule -DisplayName "GYM Madre Server" `
    -Direction Inbound `
    -LocalPort 8000 `
    -Protocol TCP `
    -Action Allow
```

#### Verificar Regla
```powershell
Get-NetFirewallRule -DisplayName "GYM Madre Server"
```

### Firewalls de Terceros

#### Norton, McAfee, Avast, etc.
1. Agregar excepción para:
   - `python.exe`
   - `pythonw.exe`
   - Puerto 8000
2. Permitir en "redes confiables"

---

## 🔧 Configuraciones de Hardware

### Requisitos Mínimos

#### PC Madre (Servidor)
- **CPU**: Pentium 4 o superior
- **RAM**: 1GB mínimo, 2GB recomendado
- **Disco**: 200MB libres
- **Red**: Adaptador Ethernet o WiFi
- **Sistema**: Windows 7+ (64 bits recomendado)

#### PC Hija (Cliente)
- **CPU**: Cualquier procesador moderno
- **RAM**: 512MB mínimo, 1GB recomendado
- **Disco**: 100MB libres
- **Red**: Conexión a Internet o LAN
- **Sistema**: Windows 7+

### Rendimiento Optimizado

#### PC con Recursos Limitados
- Reducir intervalo de sincronización:
  ```python
  # En hija_main.py
  self.sync_interval = 3600  # 1 hora en vez de 30 min
  ```

#### Múltiples Clientes
- La Madre puede manejar **100+ clientes simultáneos**
- Con PC moderna: hasta 500 clientes
- Limitado por RAM y red, no CPU

---

## 🌐 Configuración Multi-Madre

### Escenario: Dos Sedes con Servidores

```
Sede Principal (Madre A)      Sede Secundaria (Madre B)
192.168.1.100                 192.168.2.100
         │                            │
         ├──────────VPN───────────────┤
         │         Sync                │
         │                            │
    ┌────┴────┐                  ┌────┴────┐
    │ Hijas   │                  │ Hijas   │
    │ 1-50    │                  │ 51-100  │
    └─────────┘                  └─────────┘
```

### Configuración

#### 1. Registrar Servidores Mutuamente

**En Madre A:**
```python
import requests

# Registrar Madre B
requests.post('http://192.168.1.100:8000/registrar_servidor_madre',
    params={
        'server_name': 'Sede_Secundaria',
        'server_url': 'http://192.168.2.100:8000',
        'sync_token': 'token_seguro_123'
    })
```

**En Madre B:**
```python
# Registrar Madre A
requests.post('http://192.168.2.100:8000/registrar_servidor_madre',
    params={
        'server_name': 'Sede_Principal',
        'server_url': 'http://192.168.1.100:8000',
        'sync_token': 'token_seguro_456'
    })
```

#### 2. Sincronización Automática
- Los mensajes se replican entre servidores
- Chat en vivo funciona entre todas las sedes
- Usuarios pueden conectarse a cualquier Madre

---

## 🔒 Seguridad Simple pero Efectiva

### Principios de Diseño

1. **No Requerir Configuración Compleja**
   - Sin certificados SSL complicados
   - Sin VPN obligatoria
   - Sin tokens de autenticación complejos

2. **Seguridad Básica Incluida**
   - ✅ Contraseñas hasheadas (SHA256)
   - ✅ Validación de permisos en servidor
   - ✅ Thread-safety en base de datos
   - ✅ Timeouts en requests

3. **Fácil de Depurar**
   - HTTP simple (no HTTPS obligatorio)
   - JSON legible en requests
   - Logs claros en consola

### Mejoras Opcionales para Producción

```python
# En madre_server.py, agregar SSL:
import ssl

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('cert.pem', 'key.pem')

# Ejecutar con SSL:
uvicorn.run(app, host="0.0.0.0", port=8443, ssl=ssl_context)
```

---

## 🐛 Troubleshooting

### Problema: No Se Puede Conectar

#### Verificar Conectividad
```powershell
# Desde PC Hija
ping 192.168.1.100
telnet 192.168.1.100 8000
```

#### Soluciones:
1. ✅ Verificar que Madre esté ejecutándose
2. ✅ Comprobar IP correcta en `hija_comms.py`
3. ✅ Desactivar temporalmente firewall para probar
4. ✅ Verificar que ambas PCs estén en misma red

### Problema: Firewall Bloquea Conexión

#### Solución Rápida:
```powershell
# Desactivar temporalmente (como Administrador)
netsh advfirewall set allprofiles state off

# Probar conexión

# Reactivar firewall
netsh advfirewall set allprofiles state on

# Agregar regla permanente
netsh advfirewall firewall add rule name="GYM Server" dir=in action=allow protocol=TCP localport=8000
```

### Problema: Error de Puerto en Uso

#### Verificar Puerto:
```powershell
netstat -ano | findstr :8000
```

#### Cambiar Puerto:
```python
# En madre_main.py
HOST_PORT = 8080  # Cambiar a puerto disponible

# En hija_comms.py
MADRE_BASE_URL = "http://192.168.1.100:8080"
```

---

## 📊 Monitoreo y Logs

### Logs del Servidor
```python
# Ver logs en tiempo real
tail -f logs/madre_server.log  # Linux
# En Windows, abrir archivo con Notepad++
```

### Métricas de Red
```powershell
# Windows Resource Monitor
perfmon /res

# Ver conexiones activas
netstat -an | findstr :8000
```

---

## 🚀 Distribución

### Crear Ejecutable para Windows

#### Usar PyInstaller
```bash
# Instalar PyInstaller
pip install pyinstaller

# Crear ejecutable de Madre
pyinstaller --onefile --windowed madre_main.py

# Crear ejecutable de Hija
pyinstaller --onefile --windowed hija_main.py

# Resultados en carpeta dist/
```

#### Incluir Dependencias
```bash
# Crear ejecutable con todo incluido
pyinstaller --onefile --windowed --add-data "data;data" hija_main.py
```

### Instalador para Windows

#### Usar Inno Setup
1. Descargar Inno Setup
2. Crear script de instalación
3. Incluir:
   - Ejecutables
   - Base de datos vacía
   - Archivos de configuración
4. Generar instalador `.exe`

---

## 📝 Checklist de Implementación

### Instalación en Nueva PC

#### PC Madre:
- [ ] Instalar Python 3.8+
- [ ] Instalar dependencias: `pip install -r requirements_madre.txt`
- [ ] Configurar firewall (permitir puerto 8000)
- [ ] Ejecutar: `python populate_db.py` (primera vez)
- [ ] Iniciar: `python madre_main.py`
- [ ] Verificar IP: `ipconfig`
- [ ] Probar acceso: abrir navegador en `http://localhost:8000`

#### PC Hija:
- [ ] Instalar Python 3.8+
- [ ] Instalar dependencias: `pip install -r requirements_hija.txt`
- [ ] Editar `hija_comms.py` con IP de Madre
- [ ] Iniciar: `python hija_main.py`
- [ ] Probar login con usuario de prueba

---

## 🎯 Mejores Prácticas

### Red Local (LAN/WiFi)
1. Usar IPs estáticas para servidores Madre
2. Configurar reserva DHCP en router
3. Documentar IPs de cada equipo
4. Mantener equipos en misma subnet

### Internet Público
1. Usar servicio de DNS dinámico (DynDNS, No-IP)
2. Considerar VPN para seguridad adicional
3. Cambiar puerto por defecto (8000 → otro)
4. Implementar rate limiting
5. Usar HTTPS en producción

### Múltiples Sedes
1. Establecer VPN entre sedes
2. Sincronizar bases de datos regularmente
3. Backup automático en ambas sedes
4. Monitoreo de conectividad
5. Plan de contingencia si se pierde conexión

---

## 📞 Soporte Técnico

### Información de Diagnóstico

```python
# Script de diagnóstico (diagnostic.py)
import socket
import platform
import requests

print(f"Sistema Operativo: {platform.system()} {platform.release()}")
print(f"Python: {platform.python_version()}")
print(f"Hostname: {socket.gethostname()}")
print(f"IP Local: {socket.gethostbyname(socket.gethostname())}")

try:
    r = requests.get('http://localhost:8000/', timeout=2)
    print(f"Servidor Madre: ✅ Online (Status {r.status_code})")
except:
    print("Servidor Madre: ❌ Offline")
```

### Contacto
Para problemas específicos de configuración de red o Windows:
- Documentación completa en `MESSAGING_FEATURES.md`
- Tests en `test_system.py` y `test_messaging.py`
- Logs del sistema en carpeta `logs/`

---

**GYM v3.0** - Compatible con todas las configuraciones de Windows y red, sin complicaciones.
