"""Prácticas 13 y 14 · Genera el informe Word (mismo formato que las Prácticas 11 y 12).

Lee los datos medidos:
  - docs/practica13/evidencias/reporte-final.json  (flutter test --file-reporter json)
  - docs/practica13/evidencias/ci_corridas.json    (tool/p13/corridas_ci.py)
  - docs/practica13/evidencias/cobertura.json      (de coverage/lcov.info)
  - capturas de PRACTICA 13 y 14 - DMI/capturas    (tool/p13/capturas.py)

Uso:  python tool/p13/informe.py
"""
import json
import re
from collections import defaultdict
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from PIL import Image

RAIZ = Path(__file__).resolve().parents[2]
EV = RAIZ / 'docs/practica13/evidencias'
PRACTICA = Path(r'D:\Flutter\PRACTICA 13 y 14 - DMI')
CAP = PRACTICA / 'capturas'
EVT = PRACTICA / 'evidencias_texto'
PLANTILLA = Path(r'D:\Flutter\PRACTICA 8 - DMI\Practica 8 - Pruebas de caja negra - Orlando Rubio Cabrera.docx')
SALIDA = PRACTICA / 'Practicas 13 y 14 - Automatizacion de pruebas y CI - Orlando Rubio Cabrera.docx'
REPO = 'https://github.com/rubiocabrera/skonditbeats-mobile'

AZUL = RGBColor(0x1F, 0x3A, 0x5F)
ROJO = RGBColor(0xA6, 0x1B, 0x1B)
VERDE = RGBColor(0x2F, 0x7D, 0x4A)
GRIS = RGBColor(0x59, 0x59, 0x59)
ANCHO = 9360

# Funciones de formato del informe de la Práctica 11 (doc, par, h1, tabla, ficha, imagen, codigo, ...).
_src = (RAIZ / 'tool/p11/informe.py').read_text(encoding='utf-8')
_bloque = _src.split('# ── Documento a partir de la plantilla')[1].split('# Atajos a los datos medidos')[0]
exec(_bloque.split('\n', 1)[1])


def jl(nombre):
    return json.loads((EV / nombre).read_text(encoding='utf-8-sig'))


# ── Datos medidos ──────────────────────────────────────────────────────────────
CI = {c['numero']: c for c in jl('ci_corridas.json')}
COB = jl('cobertura.json')


def leer_reporte(ruta):
    suites, pruebas, res = {}, {}, {}
    total_ms = 0
    for l in Path(ruta).read_text(encoding='utf-8').splitlines():
        if not l.strip():
            continue
        e = json.loads(l)
        t = e['type']
        if t == 'suite':
            suites[e['suite']['id']] = e['suite']['path'].replace('\\', '/').split('/test/')[-1]
        elif t == 'testStart':
            pruebas[e['test']['id']] = (e['test']['name'], e['test']['suiteID'])
        elif t == 'testDone' and not e['hidden']:
            res[e['testID']] = e['result']
        elif t == 'done':
            total_ms = e['time']
    filas = [(pruebas[i][0], suites[pruebas[i][1]], r) for i, r in res.items()]
    return filas, total_ms


FINAL, FINAL_MS = leer_reporte(EV / 'reporte-final.json')
N_TOTAL = len(FINAL)
N_OK = sum(1 for f in FINAL if f[2] == 'success')
AUT = defaultdict(lambda: [0, 0])
for nombre, archivo, r in FINAL:
    m = re.search(r'AUT-0\d', nombre)
    if m:
        AUT[m[0]][0 if r == 'success' else 1] += 1
N_AUT = sum(a + b for a, b in AUT.values())
# Primera corrida local, antes de corregir (texto de flutter test --reporter expanded).
ANTES = (EV / 'corrida1_antes.txt').read_text(encoding='utf-8')
ANTES_RES = re.findall(r'\+(\d+) -(\d+): Some tests failed', ANTES)[-1]


def paso(c, prefijo):
    return next(p for p in CI[c]['pasos'] if p['nombre'].startswith(prefijo))


def notice(c):
    a = next((x for x in CI[c]['anotaciones'] if x['nivel'] == 'notice'), None)
    return a['mensaje'] if a else '— (la anotación se agregó en la corrida 3)'


def cob(archivo):
    h, t = COB[archivo]
    return f'{100 * h / t:.0f} % ({h}/{t})'


RES_CI = {'success': 'Éxito', 'failure': 'Falla'}


def recorte(nombre, alto=None):
    """Panel principal de la corrida, sin la barra lateral de GitHub (texto más legible)."""
    im = Image.open(CAP / f'{nombre}.png')
    destino = CAP / f'{nombre}_panel.png'
    ancho = im.width - 20 - 525
    titulo = im.crop((0, 170, ancho, 300))             # icono de estado, mensaje y número de corrida
    panel = im.crop((525, 300, im.width - 20, min(alto or im.height, im.height)))
    junto = Image.new('RGB', (ancho, titulo.height + panel.height), im.getpixel((5, 5)))
    junto.paste(titulo, (0, 0))
    junto.paste(panel, (0, titulo.height))
    junto.save(destino)
    return destino

# ═════════════════════════════════════════════════════════════════════════════
# Portada
# ═════════════════════════════════════════════════════════════════════════════
for _ in range(4):
    doc.add_paragraph()
par('Desarrollo Móvil Integral', tam=16, color=AZUL, alin=WD_ALIGN_PARAGRAPH.CENTER)
par('Prácticas 13 y 14', tam=26, negrita=True, color=AZUL, alin=WD_ALIGN_PARAGRAPH.CENTER)
par('Automatización de pruebas y validación continua de aplicaciones móviles Flutter', tam=16, color=AZUL,
    alin=WD_ALIGN_PARAGRAPH.CENTER)
par('Aplicación evaluada: SkonditBeats Mobile (Flutter + API Fastify)', tam=12, color=AZUL, alin=WD_ALIGN_PARAGRAPH.CENTER)
doc.add_paragraph()
for linea in ('Alumno: Orlando Rubio Cabrera', 'Docente: MANUEL CONTRERAS CASTILLO', 'Grupo: IDGS16',
              'Fecha: 18 de noviembre de 2026', f'Repositorio: {REPO}'):
    par(linea, tam=12, alin=WD_ALIGN_PARAGRAPH.CENTER)
salto()
par('Índice', tam=16, negrita=True, color=AZUL)
campo_toc()
salto()

# ═════════════════════════════════════════════════════════════════════════════
# 1. Reporte técnico (1–2 cuartillas)
# ═════════════════════════════════════════════════════════════════════════════
h1('1. Reporte técnico')
par('SkonditBeats Mobile es la app Flutter de la tienda de beats SkonditBeats (catálogo, carrito, pago simulado, tickets de '
    'soporte y panel de administración) que consume la API REST Fastify de la web. En las prácticas 11 y 12 las pruebas se '
    f'corrían a mano en la PC. En esta práctica se automatizaron: se agregaron {N_AUT} pruebas nuevas (AUT-01 a AUT-06) a las '
    f'129 que ya existían, y un flujo de GitHub Actions las corre todas ({N_TOTAL}) junto con el análisis estático en cada push y '
    'en cada pull request.')

h2('Fase 1 · Componentes críticos seleccionados')
tabla(['Tipo', 'Componente', 'Por qué es crítico', 'Riesgo previo que se previene'], [
    ['Función crítica', 'Registro e inicio de sesión (`Validators`, `LoginScreen`, `AuthController`) y pago con tarjeta',
     'Es la entrada a la app y al dinero: un error deja fuera al usuario o acepta una tarjeta inválida',
     'DEF-06 (P11): "12/99" pasaba como vigente. DEF-07 (P11): `luhn()` lanzaba FormatException'],
    ['Servicio / endpoint', '`AuthRepository` ↔ `POST /api/auth/login`, `/verify-otp`, `/register` (Dio + `ReintentoInterceptor`)',
     'Toda la comunicación pasa por el mismo cliente HTTP y su política de reintentos',
     'RES-03/04/05 (P12): servidor caído, 500, 401; DEF-01 (P11): mensaje de Fastify en inglés'],
    ['Persistencia', '`AppDatabase` (SQLite, v3) con `CartDao` y `AccesoDao`',
     'El carrito y el historial viven en el teléfono y sobreviven a cerrar la app',
     'Duplicados en el carrito, mezclar carritos de usuarios y migraciones que borren datos'],
], [0.95, 1.75, 1.75, 2.05], tam=8.5)

h2('Fases 2 y 3 · Pruebas automatizadas')
vinetas([
    f'**Unitarias (AUT-01 a AUT-03, {sum(AUT[k][0] + AUT[k][1] for k in ("AUT-01", "AUT-02", "AUT-03"))} casos).** Cubren '
    'los cinco criterios: entrada válida, vacía o nula, fuera de rango (edad 17/121, tarjeta de 15/17 dígitos, mes 00/13, '
    'vigencia > 20 años, montos negativos), resultado esperado exacto (el texto del mensaje) y manejo de excepciones '
    '(`luhn()` con letras, NaN, regreso de Google con error → `ApiException`).',
    f'**Integración (AUT-04 y AUT-05, {sum(AUT[k][0] + AUT[k][1] for k in ("AUT-04", "AUT-05"))} casos).** La app real '
    '(Dio + interceptor de reintentos + repositorio, y la pantalla de login montada) habla con un **servidor HTTP real en '
    '127.0.0.1** que responde como la API: 200, 201, 401, 409, 503, 200 incompleto, HTML, servidor apagado y servidor que no '
    'contesta. Se comprueba el cuerpo JSON enviado, el código HTTP y el mensaje que ve el usuario.',
    f'**Persistencia (AUT-06, {sum(AUT["AUT-06"])} casos).** SQLite real (`sqflite_common_ffi`) con el mismo esquema y DAO '
    'del teléfono: guardar/leer por usuario, llave primaria sin duplicados, borrar, reabrir la base, restricción CHECK, '
    'controlador → DAO → SQLite y migración de la versión 1 a la 3 sin perder datos.',
])
par('**Adaptación justificada:** las pruebas de integración no usan la API de producción (Supabase), porque el resultado '
    'cambiaría con el Wi-Fi y cada corrida ensuciaría la base real. El servidor local de la prueba usa los mismos contratos '
    '(rutas, cuerpos y códigos) que la API Fastify, y así la misma prueba pasa igual en la PC y en GitHub Actions.')

h2('Fase 4 · Pipeline de integración continua')
par('`.github/workflows/pruebas.yml` se dispara con `push`, `pull_request` y a mano. Instala Flutter 3.44.0 (la versión '
    'de la PC) y SQLite, y corre `flutter pub get` → `flutter analyze` → `flutter test --coverage`. Después publica un resumen '
    'con anotaciones por prueba fallida y guarda como artefacto el reporte JSON, la salida, el resumen y `lcov.info` '
    '(30 días). No usa secretos ni internet más allá de pub.dev.')

h2('Fase 5 · Resultados')
c1, c2, c3, c4, c5 = (CI[i] for i in range(1, 6))
tabla(['Ejecución', 'Commit', 'Resultado', 'Pruebas', 'Tiempo'], [
    ['Local, antes de corregir', '—', 'Falla', f'{int(ANTES_RES[0]) + int(ANTES_RES[1])} nuevas: {ANTES_RES[0]} ✓, {ANTES_RES[1]} ✗',
     '51 s'],
    *[[f'CI corrida #{c["numero"]}', f'`{c["commit"]}`', RES_CI[c['resultado']],
       {1: '187 ✓, 5 ✗ (no detectadas)', 2: '187 ✓, 5 ✗', 3: '187 ✓, 5 ✗'}.get(c['numero'], f'{N_TOTAL} ✓, 0 ✗'),
       f'{c["duracion_job_s"]} s (pruebas {paso(c["numero"], "Pruebas")["segundos"]} s)'] for c in (c1, c2, c3, c4, c5)],
    ['Local, final', '`22d023c`', 'Éxito', f'{N_OK} ✓, {N_TOTAL - N_OK} ✗', f'{FINAL_MS / 1000:.1f} s'],
], [1.6, 0.8, 0.8, 2.0, 1.3], tam=8.5)
par(f'Total final: **{N_TOTAL} pruebas ejecutadas, {N_OK} aprobadas, {N_TOTAL - N_OK} fallidas**, '
    f'{FINAL_MS / 1000:.1f} s en la PC y {paso(5, "Pruebas")["segundos"]} s en el paso de pruebas del CI '
    f'({c5["duracion_job_s"]} s el job completo, con la instalación de Flutter en caché). Cobertura de líneas de los componentes '
    f'críticos: `validators.dart` {cob("lib/core/utils/validators.dart")}, `money.dart` {cob("lib/core/utils/money.dart")}, '
    f'`auth_repository.dart` {cob("lib/features/auth/data/auth_repository.dart")}, `cart_dao.dart` '
    f'{cob("lib/features/cart/data/cart_dao.dart")}, `app_database.dart` {cob("lib/core/database/app_database.dart")}.')
par('**Errores encontrados y cambios.** Las pruebas encontraron cuatro defectos en la app (sección 4). Lo más '
    'importante: el login quedaba **en silencio** si la API respondía 200 sin token, porque salía un `TypeError` que la pantalla '
    'no atrapaba. En el CI se encontró un quinto defecto, más peligroso: la **corrida 1 salió en verde con 5 pruebas fallando**, '
    'porque `flutter test | tee` tomaba el código de salida de `tee`. Se corrigió con `bash -eo pipefail` (corrida 2, roja '
    'como debía). Luego se agregaron anotaciones públicas (corrida 3) y se subieron las correcciones de la app (corrida 4, verde). '
    'El último push (corrida 5) actualizó `upload-artifact` a Node 24 y comprobó que el flujo vuelve a correr solo y sin avisos.')

h2('Fase 6 · Conclusión técnica')
par('La automatización convierte cada defecto corregido en una regla que el repositorio vuelve a comprobar sola. DEF-06 y '
    'DEF-07 de la Práctica 11, o el `TypeError` del login de esta práctica, ya no dependen de que alguien se acuerde de probarlos '
    f'a mano: si un cambio futuro los reintroduce, alguna de las {N_TOTAL} pruebas falla y GitHub marca el commit en rojo antes '
    'de que llegue al teléfono. El CI además fija el entorno (Flutter 3.44.0, Ubuntu, sin datos locales), así que '
    '"en mi PC sí pasa" deja de ser un argumento, y el resultado queda registrado por commit.')
par('La lección más valiosa vino del propio pipeline. Un CI en verde no garantiza nada si no se comprueba que también '
    'sabe ponerse en rojo. Por eso la secuencia rojo → verde se forzó a propósito: commit con pruebas que fallan, CI rojo; '
    'commit con la corrección, CI verde. Como las pruebas de integración usan un servidor local en lugar de Supabase, son '
    'rápidas (unos 30 s en total) y deterministas, condición necesaria para que se corran en cada push y nadie tenga motivo '
    'para desactivarlas.')
salto()

# ═════════════════════════════════════════════════════════════════════════════
h1('2. Matriz de automatización')
pasos_ok = lambda c: sum(1 for p in CI[c]['pasos'] if p['resultado'] == 'success')
tabla(['ID', 'Tipo', 'Qué valida', 'Archivo / evidencia', 'Casos', 'Estado'], [
    ['AUT-01', 'Unitarias', 'Registro e inicio de sesión: correo, contraseña (política del backend), edad, teléfono, nombre, OTP y '
     'datos que se envían al registrarse', '`aut01_registro_login_test.dart`', f'{AUT["AUT-01"][0]}', 'Aprobada'],
    ['AUT-02', 'Unitarias', 'Pago con tarjeta: Luhn, vencimiento, CVV, titular, formateador; regresión de DEF-06 y DEF-07',
     '`aut02_pago_tarjeta_test.dart`', f'{AUT["AUT-02"][0]}', 'Aprobada'],
    ['AUT-03', 'Unitarias', 'Precios, números de la API, artículo del carrito, mensajes de error HTTP y regreso de Google',
     '`aut03_logica_negocio_test.dart`', f'{AUT["AUT-03"][0]}', 'Aprobada (3 fallaron antes de corregir)'],
    ['AUT-04', 'Integración', '`AuthRepository` ↔ servidor HTTP: 200/201/401/409/503, OTP, respuesta incompleta y HTML',
     '`aut04_auth_api_integracion_test.dart`', f'{AUT["AUT-04"][0]}', 'Aprobada (1 falló antes)'],
    ['AUT-05', 'Integración', '`LoginScreen` real ↔ red: servidor apagado, sin respuesta, 401, 200 dañado, formulario vacío',
     '`aut05_login_pantalla_red_test.dart`', f'{AUT["AUT-05"][0]}', 'Aprobada (1 falló antes)'],
    ['AUT-06', 'Persistencia', 'SQLite real: carrito por usuario, sin duplicados, borrar, reabrir, CHECK, controlador→DAO, '
     'accesos y migración v1→v3', '`aut06_persistencia_sqlite_test.dart`', f'{AUT["AUT-06"][0]}', 'Aprobada'],
    ['AUT-07', 'CI', 'El flujo corre solo en push y pull request: análisis estático + todas las pruebas + reportes',
     f'`pruebas.yml`; corridas #1–#5', f'{pasos_ok(5)} pasos', 'Aprobada'],
    ['AUT-08', 'CI', 'El CI detecta una regresión (rojo) y se recupera con la corrección (verde) en un nuevo push',
     'Corridas #2/#3 (rojo) → #4/#5 (verde)', '5 corridas', 'Aprobada (corregido el falso verde de #1)'],
], [0.55, 0.75, 2.2, 1.6, 0.55, 0.85], tam=8)
par(f'Las {N_TOTAL - N_AUT} pruebas de las prácticas 11 y 12 (`test/whitebox`, `resiliencia_test.dart`, etc.) también corren en '
    'el pipeline, así que todo cambio vuelve a validar el trabajo anterior.', tam=10, color=GRIS)

# ═════════════════════════════════════════════════════════════════════════════
h1('3. Detalle de las pruebas')
h2('3.1 Unitarias: criterios cubiertos')
tabla(['Criterio', 'AUT-01 (registro/login)', 'AUT-02 (pago)', 'AUT-03 (lógica)'], [
    ['Entrada válida', '`cliente@skondit.com`, `Skondit2026!`, edad 18 y 120', '4242 4242 4242 4242, `11/26` con hoy = nov-2026',
     '`formatMoney(1234567.6)` → `$1,234,568 MXN`'],
    ['Vacía o nula', '`null`, `""`, `"   "` → "El correo es obligatorio"', 'número, vencimiento y CVV `null`/`""`',
     '`parseNum(null)`, `""`, `"abc"` → 0'],
    ['Fuera de rango', 'Edad 17, -5, 121; contraseña de 9; teléfono de 9 y 14', '15 y 17 dígitos; mes 00 y 13; `01/47` (> 20 años)',
     '`formatMoney(-500)`; `NaN`, `Infinity`'],
    ['Resultado esperado', 'Mensaje exacto de la primera regla que falta', '"La tarjeta está vencida", "Fecha no válida"',
     'JSON normalizado del registro; ida y vuelta toMap/fromMap'],
    ['Excepciones', 'Edad `99999999999999999999999` no lanza', '`luhn("4242abcd…")` → false sin lanzar (DEF-07)',
     'Regreso de Google con error → `ApiException`'],
], [1.1, 1.85, 1.75, 1.8], tam=8)
h2('3.2 Integración y persistencia')
tabla(['Caso', 'Escenario', 'Resultado esperado'], [
    ['AUT-04a', 'Login de admin (200)', 'POST `/api/auth/login` con JSON `{email en minúsculas, password}` → token y rol ADMIN'],
    ['AUT-04b/c', 'Cliente con 2FA y verificación OTP', '`LoginNeedsOtp` con `otpDev`; luego sesión con rol CLIENTE'],
    ['AUT-04d', 'Contraseña incorrecta (401)', '`ApiException` 401 con el mensaje de la API; **1 sola petición**'],
    ['AUT-04e/f', 'Registro: correo repetido (409) y correcto (201)', 'Mensaje de la API / usuario creado con datos normalizados'],
    ['AUT-04g/h', '200 sin token / 200 con HTML', '`ApiException` "La respuesta del servidor no es válida" (antes: TypeError)'],
    ['AUT-04i', '503 en un POST sin Idempotency-Key', 'No se reintenta a ciegas (evita duplicar escrituras, P12)'],
    ['AUT-05a/b', 'Servidor apagado / colgado', 'Aviso "Sin conexión…" o "El servidor tardó demasiado…" y botón reactivado'],
    ['AUT-05c/d', '401 / respuesta dañada', 'SnackBar con el mensaje de la API / mensaje de error sin excepción'],
    ['AUT-05e', 'Formulario vacío', 'Mensajes de validación y **0 peticiones** al servidor'],
    ['AUT-06a–f', 'Carrito en SQLite', 'Por usuario y en orden; PK sin duplicados; vaciar solo el propio; sobrevive a reabrir; CHECK'],
    ['AUT-06g/h', 'Accesos y migración', 'Más reciente primero con límite; base v1 → v3 conserva los accesos y crea carrito'],
], [0.85, 2.0, 3.65], tam=8.5)
salto()

# ═════════════════════════════════════════════════════════════════════════════
h1('4. Errores encontrados y correcciones')
for cod, filas in [
    ('ERR-01 · Precio negativo mal formateado', [
        ('Detectado por', 'AUT-03 "fuera de rango: montos negativos"'),
        ('Síntoma', '`formatMoney(-500)` devolvía `$-,500 MXN`: el signo contaba como dígito al poner comas'),
        ('Severidad', 'Media: reembolsos o descuentos mostrados mal'),
        ('Solución aplicada', 'Se formatea el valor absoluto y el signo va antes del símbolo: `-$500 MXN` (`money.dart`, commit `12586eb`)')]),
    ('ERR-02 · NaN/Infinity tumbaban la pantalla', [
        ('Detectado por', 'AUT-03 "un valor no finito no tumba la pantalla" y "parseNum NaN/Infinity"'),
        ('Síntoma', '`parseNum("NaN")` devolvía NaN y `formatMoney(NaN)` lanzaba `UnsupportedError` al hacer `round()`'),
        ('Severidad', 'Alta: un precio raro de la API rompía la construcción de la tarjeta del beat'),
        ('Solución aplicada', '`parseNum` devuelve 0 si el número no es finito y `formatMoney` lo trata como 0')]),
    ('ERR-03 · Login en silencio con respuesta incompleta', [
        ('Detectado por', 'AUT-04g (repositorio) y AUT-05d (pantalla)'),
        ('Síntoma', 'Un 200 sin `token`/`user` (proxy, caché o API vieja) lanzaba `TypeError` en `data["token"] as String`; '
                    '`LoginScreen` solo atrapa `ApiException`, así que el botón volvía a la normalidad sin ningún mensaje'),
        ('Severidad', 'Alta: el usuario no sabe por qué no entra'),
        ('Solución aplicada', '`AuthRepository._sesion()` valida token, id y correo y lanza `ApiException` con mensaje claro; '
                              'lo mismo para el correo de la respuesta 2FA')]),
    ('ERR-04 · El CI daba verde con pruebas fallando', [
        ('Detectado por', 'Corrida #1: éxito en el commit `78cc869`, que tiene 5 pruebas que fallan'),
        ('Síntoma', 'GitHub corre los pasos con `bash -e` **sin pipefail**; en `flutter test | tee salida.txt` el código del paso '
                    'era el de `tee` (0)'),
        ('Severidad', 'Crítica: el pipeline no protegía nada'),
        ('Solución aplicada', '`defaults.run.shell: bash` (→ `bash -eo pipefail`) y `set -o pipefail`; la corrida #2 ya sale en rojo (`404be08`)')]),
    ('ERR-05 · Avisos del pipeline', [
        ('Detectado por', 'Anotaciones de las corridas #1–#4'),
        ('Síntoma', 'Los logs y el resumen de Actions no se ven sin sesión iniciada; aviso "Node.js 20 is deprecated"'),
        ('Severidad', 'Baja'),
        ('Solución aplicada', '`::notice`/`::error` por prueba (públicos); `checkout@v5` y `upload-artifact@v6` (Node 24). Corrida #5 sin avisos')]),
]:
    h3(cod)
    ficha(filas)
par('Además, durante la creación de las pruebas, AUT-05a a AUT-05c fallaron por un problema de la propia prueba, no de la app: '
    '`testWidgets` reemplaza el `HttpClient` por uno simulado que responde 400 a todo. Se corrigió con '
    '`HttpOverrides.global = null` y lanzando la petición en la zona de tiempo real (`tester.runAsync`).', tam=10, color=GRIS)
salto()

# ═════════════════════════════════════════════════════════════════════════════
h1('5. Evidencia de la ejecución automática')
par(f'Repositorio público: `{REPO}` → pestaña Actions. Cada corrida se disparó sola con `git push`.')
tabla(['#', 'Commit', 'Cambio', 'Resultado', 'Anotación de totales'], [
    [str(c['numero']), f'`{c["commit"]}`', c['mensaje'].split(' (Practicas')[0], RES_CI[c['resultado']], notice(c['numero'])]
    for c in (c1, c2, c3, c4, c5)
], [0.3, 0.75, 2.6, 0.7, 2.15], tam=8)
imagen(CAP / '01_lista_corridas.png', ancho_max=6.4, pie='Figura 1. Las cinco corridas del flujo "Pruebas automatizadas", todas disparadas por push.')
imagen(recorte('02_corrida1_verde_falso', 1290), ancho_max=5.2, pie='Figura 2. Corrida #1: verde con 5 pruebas fallando (ERR-04).')
imagen(recorte('04_corrida3_rojo_anotaciones'), ancho_max=6.2, alto_max=8.0,
       pie='Figura 3. Corrida #3: el CI detecta las 5 pruebas fallidas y muestra la causa de cada una.')
imagen(recorte('05_corrida4_verde', 1150), ancho_max=5.2, pie='Figura 4. Corrida #4: con las correcciones de la app, todo en verde.')
imagen(recorte('06_corrida5_verde', 1150), ancho_max=5.2, pie='Figura 5. Corrida #5 (nuevo push): el flujo se ejecuta otra vez, en verde y sin avisos.')
h2('Tiempo por paso (corrida #5)')
tabla(['Paso', 'Resultado', 'Segundos'], [
    [p['nombre'], RES_CI.get(p['resultado'], p['resultado']), str(p['segundos'])] for p in c5['pasos']
    if not p['nombre'].startswith(('Post ', 'Set up', 'Complete'))
], [4.2, 1.0, 1.0], tam=9, centrar=(1, 2))
salto()

# ═════════════════════════════════════════════════════════════════════════════
h1('6. Entregables')
tabla(['#', 'Entregable', 'Dónde'], [
    ['1', 'Repositorio actualizado', f'`{REPO}` (rama `master`)'],
    ['2', 'Código de al menos 5 pruebas unitarias', f'`test/automatizacion/aut01…aut03_*_test.dart` ({sum(AUT[k][0] for k in ("AUT-01", "AUT-02", "AUT-03"))} casos)'],
    ['3', 'Código de al menos 3 pruebas de integración', f'`aut04_*`, `aut05_*` ({AUT["AUT-04"][0] + AUT["AUT-05"][0]} casos) y `aut06_*` (persistencia, {AUT["AUT-06"][0]})'],
    ['4', 'Archivo de configuración del pipeline', '`.github/workflows/pruebas.yml` (Anexo A)'],
    ['5', 'Evidencia de ejecución exitosa', 'Sección 5, corridas #4 y #5; artefacto `reportes-pruebas-N` en cada corrida'],
    ['6', 'Matriz de validación completada', 'Sección 2 (AUT-01 … AUT-08)'],
    ['7', 'Reporte técnico (1–2 cuartillas)', 'Sección 1'],
], [0.3, 2.4, 3.8], tam=9)

h1('Anexo A · Pipeline (.github/workflows/pruebas.yml)')
codigo((RAIZ / '.github/workflows/pruebas.yml').read_text(encoding='utf-8').splitlines())

salto()
h1('Anexo B · Fragmentos de las pruebas')
par('Integración contra el servidor local (AUT-04g, regresión de ERR-03):', negrita=True)
src4 = (RAIZ / 'test/automatizacion/aut04_auth_api_integracion_test.dart').read_text(encoding='utf-8').splitlines()
i = next(n for n, l in enumerate(src4) if 'AUT-04g' in l)
codigo(src4[i:i + 8])
par('Persistencia con SQLite real (AUT-06d):', negrita=True)
src6 = (RAIZ / 'test/automatizacion/aut06_persistencia_sqlite_test.dart').read_text(encoding='utf-8').splitlines()
i = next(n for n, l in enumerate(src6) if "test('d ·" in l)
codigo(src6[i:i + 10])

h1('Anexo C · Cómo reproducir')
codigo([
    r'cd D:\Flutter\skondit_beats_mobile',
    'flutter pub get',
    'flutter analyze',
    'flutter test test/automatizacion            # solo AUT-01 … AUT-06',
    'flutter test --coverage --file-reporter json:reporte.json',
    'dart run tool/p13/resumen_pruebas.dart reporte.json resumen.md',
    'python tool/p13/corridas_ci.py   # datos de las corridas de GitHub Actions',
    'python tool/p13/capturas.py ; python tool/p13/informe.py',
])

SALIDA.parent.mkdir(parents=True, exist_ok=True)
doc.save(str(SALIDA))
print('Informe:', SALIDA)
