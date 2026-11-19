"""Prácticas 13 y 14 · Capturas de las páginas públicas de GitHub Actions con Chrome headless.

Uso:  python tool/p13/capturas.py
"""
import json
import subprocess
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parents[2]
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
CAP = Path(r'D:\Flutter\PRACTICA 13 y 14 - DMI\capturas')
REPO = 'https://github.com/rubiocabrera/skonditbeats-mobile'
CORRIDAS = {c['numero']: c for c in json.loads((RAIZ / 'docs/practica13/evidencias/ci_corridas.json').read_text(encoding='utf-8'))}

PAGINAS = [
    ('01_lista_corridas', f'{REPO}/actions', 1350),
    ('02_corrida1_verde_falso', CORRIDAS[1]['url'], 1000),
    ('03_corrida2_rojo', CORRIDAS[2]['url'], 1000),
    ('04_corrida3_rojo_anotaciones', CORRIDAS[3]['url'], 1500),
    ('05_corrida4_verde', CORRIDAS[4]['url'], 1000),
    ('06_corrida5_verde', CORRIDAS[5]['url'], 1000),
    ('07_workflow', f'{REPO}/blob/master/.github/workflows/pruebas.yml', 2400),
    ('08_pruebas_en_repo', f'{REPO}/tree/master/test/automatizacion', 900),
]

CAP.mkdir(parents=True, exist_ok=True)
for nombre, url, alto in PAGINAS:
    png = CAP / f'{nombre}.png'
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1.5',
                    f'--window-size=1280,{alto}', '--virtual-time-budget=10000', f'--screenshot={png}', url],
                   check=True, capture_output=True, timeout=120)
    # Recorta la barra de navegación de GitHub (68 px a escala 1.5 ≈ 100 px).
    img = Image.open(png)
    img.crop((0, 100, img.width, img.height)).save(png)
    print(nombre, img.size)
