"""Prácticas 13 y 14 · Arma el .zip de código (mismo formato que las Prácticas 11 y 12).

Uso:  python tool/p13/empaquetar.py
"""
import json
import subprocess
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = Path(r'D:\Flutter\PRACTICA 13 y 14 - DMI (codigo).zip')
EV = RAIZ / 'docs/practica13/evidencias'
REPO = 'https://github.com/rubiocabrera/skonditbeats-mobile'

ARCHIVOS = {
    'pruebas_unitarias': ['test/automatizacion/aut01_registro_login_test.dart',
                          'test/automatizacion/aut02_pago_tarjeta_test.dart',
                          'test/automatizacion/aut03_logica_negocio_test.dart'],
    'pruebas_integracion': ['test/automatizacion/aut04_auth_api_integracion_test.dart',
                            'test/automatizacion/aut05_login_pantalla_red_test.dart',
                            'test/automatizacion/apoyo/servidor_prueba.dart'],
    'pruebas_persistencia': ['test/automatizacion/aut06_persistencia_sqlite_test.dart'],
    'ci': ['.github/workflows/pruebas.yml', 'tool/p13/resumen_pruebas.dart'],
    'evidencias': [str(p.relative_to(RAIZ)).replace('\\', '/') for p in sorted(EV.iterdir())
                   if p.suffix in ('.txt', '.md', '.json') and p.name != 'reporte-final.json'],
    'herramientas': ['tool/p13/corridas_ci.py', 'tool/p13/capturas.py', 'tool/p13/informe.py', 'tool/p13/empaquetar.py'],
}

# Cambios hechos para corregir los errores (diffs de los commits de la práctica).
DIFERENCIAS = {
    'correcciones/ERR-01_03_app_precios_y_login.diff': ('793aa8c', '12586eb', ['lib']),
    'correcciones/ERR-04_ci_pipefail.diff': ('78cc869', '404be08', ['.github']),
    'correcciones/ERR-05_ci_anotaciones_y_node24.diff': ('404be08', '793aa8c', ['.github', 'tool/p13/resumen_pruebas.dart']),
    'correcciones/ERR-05_ci_upload_artifact_v6.diff': ('12586eb', '22d023c', ['.github']),
    'correcciones/app_database_ruta_para_pruebas.diff': ('fa462fc', '78cc869', ['lib/core/database', 'pubspec.yaml']),
}

corridas = json.loads((EV / 'ci_corridas.json').read_text(encoding='utf-8'))
filas = '\n'.join(f"| #{c['numero']} | `{c['commit']}` | {'Éxito' if c['resultado'] == 'success' else 'Falla'} | "
                  f"{c['duracion_job_s']} s | {c['url']} |" for c in corridas)
LEEME = f"""# Prácticas 13 y 14 · Automatización de pruebas y CI — SkonditBeats Mobile

Alumno: Orlando Rubio Cabrera · Grupo IDGS16 · Docente: MANUEL CONTRERAS CASTILLO

Repositorio: {REPO}  (pestaña *Actions* → flujo "Pruebas automatizadas")
Reporte técnico, matriz y conclusiones: `Practicas 13 y 14 - Automatizacion de pruebas y CI - Orlando Rubio Cabrera.pdf`

## Contenido

| Carpeta | Qué hay | Matriz |
|---|---|---|
| `pruebas_unitarias/` | 41 casos: registro/login, pago con tarjeta, lógica de negocio | AUT-01, AUT-02, AUT-03 |
| `pruebas_integracion/` | 14 casos: AuthRepository ↔ servidor HTTP real, LoginScreen ↔ red | AUT-04, AUT-05 |
| `pruebas_persistencia/` | 8 casos: SQLite real (carrito, accesos, migración v1→v3) | AUT-06 |
| `ci/` | `pruebas.yml` (GitHub Actions) y el script de resumen/anotaciones | AUT-07, AUT-08 |
| `correcciones/` | Diffs de los cambios que corrigieron cada error (ERR-01 … ERR-05) | — |
| `evidencias/` | Corrida local antes/después, suite final, datos de las corridas del CI, cobertura | — |
| `herramientas/` | Scripts que generan el informe, las capturas y este paquete | — |

## Corridas del CI

| Corrida | Commit | Resultado | Duración | Enlace |
|---|---|---|---|---|
{filas}

La #1 salió en verde con 5 pruebas fallando (ERR-04: `flutter test | tee` sin pipefail); se corrigió
en la #2 (rojo, como debía). La #4 trae las correcciones de la app (verde) y de la #5 en adelante
son pushes posteriores que el CI volvió a validar automáticamente.

## Reproducir

```
flutter pub get
flutter analyze
flutter test                       # 192 pruebas (63 de esta práctica)
flutter test test/automatizacion   # solo AUT-01 … AUT-06
```
"""


def diff(desde, hasta, rutas):
    r = subprocess.run(['git', 'diff', f'{desde}..{hasta}', '--', *rutas], cwd=RAIZ, capture_output=True)
    return r.stdout


with zipfile.ZipFile(SALIDA, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('LEEME.md', LEEME)
    for carpeta, rutas in ARCHIVOS.items():
        for rel in rutas:
            destino = f'{carpeta}/{Path(rel).name}' if 'apoyo' not in rel else f'{carpeta}/apoyo/{Path(rel).name}'
            z.write(RAIZ / rel, destino)
    for nombre, (desde, hasta, rutas) in DIFERENCIAS.items():
        contenido = diff(desde, hasta, rutas)
        assert contenido, nombre
        z.writestr(nombre, contenido)

with zipfile.ZipFile(SALIDA) as z:
    for i in z.infolist():
        print(f'{i.file_size:>8}  {i.filename}')
print(f'\n{SALIDA}  ({SALIDA.stat().st_size / 1024:.0f} KB)')
