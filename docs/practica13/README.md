# Prácticas 13 y 14 · Automatización de pruebas y CI — SkonditBeats Mobile

| Qué | Dónde |
|---|---|
| Pruebas nuevas (AUT-01 … AUT-06) | `test/automatizacion/` (servidor HTTP de apoyo en `apoyo/servidor_prueba.dart`) |
| Pipeline (AUT-07, AUT-08) | `.github/workflows/pruebas.yml` → pestaña *Actions* de https://github.com/rubiocabrera/skonditbeats-mobile |
| Resumen y anotaciones del CI | `tool/p13/resumen_pruebas.dart` |
| Datos y capturas de las corridas | `tool/p13/corridas_ci.py`, `tool/p13/capturas.py` |
| Informe Word | `tool/p13/informe.py` → `D:\Flutter\PRACTICA 13 y 14 - DMI\` |
| Evidencias | `evidencias/` (corrida local antes/después, reporte JSON final, corridas del CI, cobertura) |

## Matriz

| ID | Tipo | Archivo | Estado |
|---|---|---|---|
| AUT-01 | Unitarias | `aut01_registro_login_test.dart` | Aprobada |
| AUT-02 | Unitarias | `aut02_pago_tarjeta_test.dart` | Aprobada |
| AUT-03 | Unitarias | `aut03_logica_negocio_test.dart` | Aprobada (3 fallaron antes de corregir) |
| AUT-04 | Integración | `aut04_auth_api_integracion_test.dart` | Aprobada (1 falló antes) |
| AUT-05 | Integración | `aut05_login_pantalla_red_test.dart` | Aprobada (1 falló antes) |
| AUT-06 | Persistencia | `aut06_persistencia_sqlite_test.dart` | Aprobada |
| AUT-07 | CI | `pruebas.yml`, corre en push y pull request | Aprobada |
| AUT-08 | CI | corridas #2/#3 rojas → #4/#5 verdes | Aprobada (se corrigió el falso verde de #1) |

## Errores encontrados

| ID | Error | Corrección |
|---|---|---|
| ERR-01 | `formatMoney(-500)` → `$-,500 MXN` | signo antes del símbolo: `-$500 MXN` |
| ERR-02 | `parseNum("NaN")` → NaN y `formatMoney(NaN)` lanzaba `UnsupportedError` | valores no finitos cuentan como 0 |
| ERR-03 | login con 200 sin token → `TypeError` no atrapado, pantalla sin mensaje | `AuthRepository._sesion()` lanza `ApiException` |
| ERR-04 | el CI salía en verde con pruebas fallando (`flutter test \| tee` sin pipefail) | `shell: bash` (`-eo pipefail`) |
| ERR-05 | logs no públicos; aviso de Node.js 20 | anotaciones `::error`/`::notice`; checkout v5 y upload-artifact v6 |

Reproducir: `flutter analyze && flutter test` (192 pruebas, ~30 s, sin red ni Supabase).
