"""Prácticas 13 y 14 · Descarga de la API pública de GitHub los datos de las corridas del CI
(commit, resultado, duración, tiempo por paso y anotaciones) y los guarda en
docs/practica13/evidencias/ci_corridas.json. No usa token: el repositorio es público.

Uso:  python tool/p13/corridas_ci.py
"""
import json
import urllib.request
from datetime import datetime
from pathlib import Path

REPO = 'rubiocabrera/skonditbeats-mobile'
API = f'https://api.github.com/repos/{REPO}'
SALIDA = Path(__file__).resolve().parents[2] / 'docs/practica13/evidencias/ci_corridas.json'


def get(url):
    req = urllib.request.Request(url, headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'p13-informe'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def seg(a, b):
    f = lambda s: datetime.fromisoformat(s.replace('Z', '+00:00'))
    return round((f(b) - f(a)).total_seconds()) if a and b else None


corridas = []
for run in sorted(get(f'{API}/actions/runs?per_page=50')['workflow_runs'], key=lambda r: r['run_number']):
    job = get(f"{API}/actions/runs/{run['id']}/jobs")['jobs'][0]
    anot = get(f"{API}/check-runs/{job['id']}/annotations")
    corridas.append({
        'numero': run['run_number'],
        'id': run['id'],
        'url': run['html_url'],
        'commit': run['head_sha'][:7],
        'mensaje': run['head_commit']['message'].split('\n')[0],
        'evento': run['event'],
        'resultado': run['conclusion'],
        'inicio': job['started_at'],
        'duracion_job_s': seg(job['started_at'], job['completed_at']),
        'pasos': [{'n': s['number'], 'nombre': s['name'], 'resultado': s['conclusion'],
                   'segundos': seg(s['started_at'], s['completed_at'])} for s in job['steps']],
        'anotaciones': [{'nivel': a['annotation_level'], 'titulo': a['title'], 'mensaje': a['message']} for a in anot],
    })

SALIDA.write_text(json.dumps(corridas, ensure_ascii=False, indent=2), encoding='utf-8')
for c in corridas:
    paso = next((p for p in c['pasos'] if p['nombre'].startswith('Pruebas')), {})
    print(f"#{c['numero']} {c['commit']} {c['resultado']:8} job {c['duracion_job_s']} s · pruebas {paso.get('segundos')} s · {c['mensaje'][:60]}")
