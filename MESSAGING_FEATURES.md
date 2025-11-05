# Sistema de Mensajería y Chat - GYM v3.0

## Resumen de Nuevas Funcionalidades

Este documento describe las nuevas funcionalidades de mensajería y chat implementadas en el sistema GYM v3.0.

---

## 📱 Aplicación Hija - GUI Mejorada

### Interfaz Profesional con Sidebar

La aplicación hija ahora cuenta con una interfaz moderna y profesional:

#### **Barra Superior (Header)**
- 👤 Información personal del usuario:
  - Nombre completo
  - Equipo asignado
  - Email de contacto
- 🔄 Botón de sincronización rápida

#### **Sidebar de Navegación (Izquierda)**
Menú principal con las siguientes secciones:
- 🏠 **Perfil**: Información personal detallada
- 📅 **Cronograma**: Rutina de entrenamiento
- 🖼️ **Galería**: Fotos personales
- ✉️ **Mensajes**: Sistema de mensajería
- 💬 **Chat en Vivo**: Comunicación en tiempo real

#### **Área de Contenido Principal**
- Diseño limpio y moderno
- Transiciones suaves entre secciones
- Contenido adaptativo según la sección activa

#### **Barra de Estado (Footer)**
- Estado de conexión en tiempo real
- Última sincronización
- Mensajes de estado del sistema

---

## ✉️ Sistema de Mensajería

### Características en la Aplicación Hija

#### Enviar Mensajes
1. Navegar a la sección **Mensajes** (✉️)
2. Click en "✏️ Nuevo Mensaje"
3. Ingresar destinatario (normalmente "admin")
4. Escribir asunto y contenido
5. Enviar

#### Ver Mensajes Recibidos
- Los mensajes se muestran en orden cronológico
- Indicador visual de mensajes no leídos (●)
- Click en "Ver Mensaje" para abrir detalles completos
- Información incluida:
  - Remitente
  - Fecha y hora
  - Asunto
  - Contenido completo
  - Adjuntos (si los hay)

### Características en la Aplicación Madre

#### Buzón de Mensajes (Admin)
La pestaña **"Buzón de Mensajes"** incluye:

1. **Contador de No Leídos**
   - 📬 Muestra cantidad de mensajes sin leer
   - Se actualiza en tiempo real

2. **Lista de Mensajes**
   - Vista completa de todos los mensajes
   - Indicador visual de leído/no leído
   - Información de remitente y fecha

3. **Acciones Disponibles**
   - **Ver**: Abre el mensaje en ventana emergente
   - **Responder**: Crea respuesta con contexto
   - **Exportar**: Guarda mensaje como archivo .txt
   - **Eliminar**: Borra el mensaje permanentemente

4. **Exportar Mensajes a TXT**
   - Formato estructurado con:
     - Cabeceras (De, Para, Asunto, Fecha)
     - Contenido completo del mensaje
     - Lista de adjuntos (si los hay)
   - Archivo legible en cualquier editor de texto

---

## 💬 Chat en Vivo

### En la Aplicación Hija

#### Iniciar Chat
1. Navegar a **Chat en Vivo** (💬)
2. Ver historial de conversaciones anteriores
3. Escribir mensaje en el campo de texto
4. Presionar Enter o click en "Enviar"

#### Características del Chat
- Mensajes en tiempo real con el administrador
- Historial completo de conversaciones
- Indicadores visuales de quién envió cada mensaje
- Marca de tiempo en cada mensaje
- Interfaz estilo mensajería moderna:
  - Mensajes propios alineados a la derecha
  - Mensajes recibidos alineados a la izquierda
  - Colores distintivos para diferenciar

### En la Aplicación Madre

El administrador puede ver y responder chats desde:
- La interfaz web del servidor
- Endpoints de API para integración con otras herramientas

---

## 📎 Adjuntos en Mensajes

### Capacidades
- **Tamaño máximo por archivo**: 50 MB
- **Archivos por mensaje**: Máximo 3
- **Tipos de archivo**: Cualquier extensión soportada

### Estructura en Base de Datos
Los adjuntos se almacenan en la tabla `message_attachments`:
- ID del mensaje padre
- Nombre del archivo
- Ruta de almacenamiento
- Tamaño en bytes
- Fecha de carga

### Uso (Backend Listo)
El backend está completamente preparado para manejar adjuntos. La integración con la UI se puede completar agregando:
1. Selector de archivos en el formulario de mensaje
2. Validación de tamaño y cantidad
3. Upload al servidor
4. Descarga desde el buzón

---

## 🔄 Soporte Multi-Madre

### Concepto
El sistema ahora soporta múltiples servidores Madre sincronizándose entre sí.

### Características

#### Registro de Servidores
- Cada servidor Madre puede registrar otros servidores
- Información almacenada:
  - Nombre del servidor
  - URL de acceso
  - Token de sincronización
  - Estado activo/inactivo
  - Última sincronización

#### Sincronización en Tiempo Real
- Cuando múltiples servidores están activos
- Los mensajes y chats se sincronizan automáticamente
- Permite gestión distribuida:
  - Varios administradores en diferentes ubicaciones
  - Backup y redundancia automática
  - Balanceo de carga entre servidores

#### Endpoints de API
- `POST /registrar_servidor_madre`: Registrar nuevo servidor
- `GET /obtener_servidores_madre`: Listar servidores registrados

---

## 🔧 API REST - Endpoints de Mensajería

### Mensajes

#### Enviar Mensaje
```http
POST /enviar_mensaje
Content-Type: application/json

{
  "from_user": "juan_perez",
  "to_user": "admin",
  "subject": "Consulta",
  "body": "Contenido del mensaje",
  "parent_message_id": null  // Opcional, para respuestas
}
```

#### Obtener Mensajes
```http
GET /obtener_mensajes?usuario=admin&solo_no_leidos=false
```

#### Obtener Mensaje Específico
```http
GET /obtener_mensaje/1
```

#### Marcar como Leído
```http
POST /marcar_leido/1
```

#### Eliminar Mensaje
```http
DELETE /eliminar_mensaje/1
```

#### Contar No Leídos
```http
GET /contar_no_leidos?usuario=admin
```

### Chat en Vivo

#### Enviar Mensaje de Chat
```http
POST /enviar_chat
Content-Type: application/json

{
  "from_user": "juan_perez",
  "to_user": "admin",
  "message": "Hola!"
}
```

#### Obtener Historial de Chat
```http
GET /obtener_chat?user1=juan_perez&user2=admin&limit=50
```

#### Marcar Chat como Leído
```http
POST /marcar_chat_leido?from_user=juan_perez&to_user=admin
```

#### Contar Chat No Leídos
```http
GET /contar_chat_no_leidos?usuario=admin
```

---

## 🗄️ Base de Datos

### Nuevas Tablas

#### `messages` - Mensajes
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_user TEXT NOT NULL,
    to_user TEXT NOT NULL,
    subject TEXT,
    body TEXT NOT NULL,
    sent_date TEXT NOT NULL,
    read_date TEXT,
    is_read INTEGER DEFAULT 0,
    parent_message_id INTEGER
);
```

#### `message_attachments` - Adjuntos
```sql
CREATE TABLE message_attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    upload_date TEXT NOT NULL,
    FOREIGN KEY (message_id) REFERENCES messages(id)
);
```

#### `chat_messages` - Chat
```sql
CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_user TEXT NOT NULL,
    to_user TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    is_read INTEGER DEFAULT 0
);
```

#### `madre_servers` - Multi-Madre
```sql
CREATE TABLE madre_servers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_name TEXT UNIQUE NOT NULL,
    server_url TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    last_sync TEXT,
    sync_token TEXT
);
```

---

## 🚀 Cómo Usar

### Iniciar Sistema Completo

#### 1. Iniciar Aplicación Madre
```bash
python madre_main.py
```
- Se inicia el servidor API en el puerto 8000
- Se abre la interfaz gráfica de gestión

#### 2. Iniciar Aplicación Hija
```bash
python hija_main.py
```
- Ingresar credenciales (ej: juan_perez / gym2024)
- La aplicación se conecta automáticamente

### Flujo de Trabajo Típico

#### En la Hija (Usuario)
1. Login con usuario y contraseña
2. Explorar secciones del sidebar:
   - Ver perfil y datos personales
   - Revisar cronograma del día
   - Ver galería de progreso
   - **Enviar mensaje al admin**
   - **Chatear en vivo con el admin**

#### En la Madre (Administrador)
1. Gestionar usuarios desde la pestaña correspondiente
2. Publicar contenido de sincronización global
3. **Revisar buzón de mensajes**:
   - Ver contador de no leídos
   - Leer mensajes
   - Responder mensajes
   - Exportar mensajes importantes
   - Eliminar mensajes obsoletos

---

## 🔐 Seguridad y Compatibilidad

### Características de Seguridad
- ✅ Contraseñas hasheadas (SHA256)
- ✅ Thread-safety en operaciones de BD
- ✅ Validación de permisos en servidor
- ✅ Tokens para sincronización multi-madre

### Compatibilidad Windows
El sistema está diseñado para ser compatible con:
- ✅ Todas las versiones de Windows (7, 8, 10, 11)
- ✅ Diferentes configuraciones de red
- ✅ Variedad de hardware
- ✅ Sin dependencias complejas

### Protocolo de Comunicación
- Simple y robusto
- Basado en HTTP/REST
- JSON para intercambio de datos
- Sin encriptación compleja (configurable para producción)
- Fácil debug y troubleshooting

---

## 📊 Pruebas

### Ejecutar Tests

#### Suite Completa
```bash
python test_system.py
```

#### Tests de Mensajería
```bash
python test_messaging.py
```

### Resultados Esperados
Todos los tests deben pasar:
- ✓ Database Operations: PASSED
- ✓ API Server: PASSED
- ✓ Credential Management: PASSED
- ✓ Messaging System: PASSED
- ✓ Live Chat System: PASSED
- ✓ Multi-Madre Support: PASSED

---

## 🎯 Próximos Pasos Recomendados

### Funcionalidad
- [ ] Implementar UI para adjuntos de archivos
- [ ] Agregar notificaciones push para nuevos mensajes
- [ ] Implementar búsqueda de mensajes
- [ ] Agregar emojis y formato en chat
- [ ] Sistema de "escribiendo..." en chat

### Seguridad (Producción)
- [ ] Migrar a bcrypt para contraseñas
- [ ] Implementar JWT para sesiones
- [ ] Añadir HTTPS/SSL
- [ ] Implementar rate limiting
- [ ] Añadir logging de auditoría

### Performance
- [ ] Caché de mensajes
- [ ] Paginación optimizada
- [ ] Compresión de adjuntos
- [ ] WebSockets para chat en tiempo real
- [ ] CDN para archivos grandes

---

## 📝 Notas Técnicas

### Estructura de Código
- **madre_db.py**: Todas las operaciones de base de datos
- **madre_server.py**: Endpoints de API REST
- **madre_gui.py**: Interfaz gráfica del administrador
- **hija_comms.py**: Cliente HTTP para la aplicación hija
- **hija_views.py**: Componentes de UI de la aplicación hija
- **hija_main.py**: Controlador principal de la aplicación hija

### Patrones de Diseño
- **MVC**: Separación de vista, controlador y modelo
- **Repository**: Capa de acceso a datos
- **Singleton**: Lock para thread-safety
- **Callback**: Comunicación entre componentes

### Thread-Safety
Todas las operaciones de base de datos están protegidas con `threading.Lock` para garantizar:
- Consistencia de datos
- Prevención de race conditions
- Seguridad en entornos multi-hilo (GUI + API Server)

---

## 🆘 Soporte

### Problemas Comunes

#### Error de Conexión
- Verificar que el servidor Madre esté ejecutándose
- Verificar la URL configurada en `hija_comms.py`
- Revisar firewall y permisos de red

#### Mensajes No Aparecen
- Verificar permisos de usuario
- Ejecutar sincronización manual
- Revisar logs del servidor

#### Base de Datos Corrupta
```bash
# Backup y recrear
cp data/gym_database.db data/gym_database.db.backup
rm data/gym_database.db
python populate_db.py
```

---

**Sistema GYM v3.0** - Sistema completo de gestión con mensajería, chat en vivo y soporte multi-servidor.
