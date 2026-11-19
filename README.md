# SkonditBeats Mobile

Versión móvil (Flutter) de SkonditBeats. Consume la **misma API** que la web
(`erp_beats/api`, Fastify + Supabase).

## Estado actual
- Inicio de sesión con correo/contraseña.
- Verificación en 2 pasos (OTP por correo) para clientes; el admin entra directo.
- Registro con validación de contraseña igual a la del backend y aceptación de términos.
- Términos y condiciones.
- Sesión guardada cifrada (Keystore / Keychain) y redirección por rol.
- Desbloqueo con huella/rostro/PIN al reabrir la app y tras 30 s en segundo plano.
- Perfil: datos del usuario y foto con cámara o galería, subida por URL preasignada
  (`/uploads/presign` → PUT directo a Supabase Storage → `/profile/foto`). Máx. 1 MB, JPG/PNG/WebP.
- Historial de accesos del dispositivo en SQLite (entidad → DAO → base de datos).
- Tienda con scroll infinito (páginas de 20) y carrito en SQLite; pago simulado idempotente.
- Admin: gestor de beats (alta, edición, baja, audio y portada), gestor de usuarios (alta,
  edición, contraseña, roles masivos, activación, ficha con compras), mesa de ayuda por tickets
  (folio, estado, prioridad, asignación), dashboard y auditoría.
- Tickets para el cliente: abrir, seguir, responder, cerrar y reabrir.
- Subidas y descargas reanudables (TUS / HTTP Range): si se corta la red continúan donde se
  quedaron al detectar cualquier conexión. Pantalla "Subidas y descargas".
- Resiliencia de red: reintentos con espera exponencial solo en operaciones seguras,
  `Idempotency-Key` en escrituras, aviso global sin conexión y cierre de sesión ante 401.

## Pruebas y Práctica 12
- `flutter test`: 47 pruebas, sin internet (las de red usan un servidor local dentro de la prueba).
- Entorno local sin Supabase, pruebas de carga, base de datos y profiling:
  ver [docs/practica12/README.md](docs/practica12/README.md).

## Estructura
```
lib/
  core/        config (env), theme, network (dio), storage (secure), router, utils, widgets
  features/
    auth/      data (repositorio), domain (modelo), presentation (controller, pantallas)
    home/      inicio de cliente y admin (placeholder)
    legal/     términos y condiciones
```
Estado con **Riverpod**, rutas con **go_router**, HTTP con **dio**.

## Cómo correrla
1. Levanta la API: en `erp_beats/api` → `npm run dev` (puerto 3000).
2. Corre la app:
   ```bash
   # Emulador Android (10.0.2.2 = tu PC)
   flutter run
   ```
3. **Celular físico por USB** (recomendado, no depende del Wi-Fi ni del firewall):
   ```bash
   # Une el puerto 3000 del celular con el de la PC (repetir si se desconecta el cable)
   D:\AndroidSDK\platform-tools\adb.exe reverse tcp:3000 tcp:3000

   flutter devices   # copia el id de tu celular
   flutter run -d <id-del-celular> --dart-define=API_URL=http://127.0.0.1:3000/api
   ```
   Sin el `--dart-define` la app usa la API de producción
   (`https://skonditbeats-backend.vercel.app/api`). Para instalar la app sin la PC:
   `flutter build apk --release` (o `build_apk.bat`).

## Probar la biometría en el emulador
1. En el emulador: Settings → Security → Screen lock → PIN.
2. Settings → Security → Fingerprint → agregar huella; cuando la pida, en el
   emulador abre `...` (Extended controls) → Fingerprint → **Touch the sensor**.
3. Inicia sesión, cierra la app por completo y ábrela: aparecerá el desbloqueo.

Si el teléfono no tiene bloqueo de pantalla, la app no pide biometría.

## Seguridad aplicada
- Token en `flutter_secure_storage`, nunca en `shared_preferences`.
- HTTP en claro bloqueado excepto hacia la PC local en desarrollo.
- `allowBackup=false` para que la sesión no se copie en respaldos.
- La URL de la API se inyecta con `--dart-define`; no hay secretos en el código.
- El router también valida el rol (un cliente no puede abrir `/admin`).
- Release recomendado: `flutter build appbundle --obfuscate --split-debug-info=build/symbols`.
