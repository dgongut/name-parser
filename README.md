# name-parser

El parser de nombres de *release* y el motor de plantillas de renombrado que comparten [DropBot](https://github.com/dgongut/dropbot) y [Torrent-Controller-Bot](https://github.com/dgongut/torrent-controller-bot).

Antes cada bot llevaba su copia de `name_parser.py`, y un fallo había que arreglarlo dos veces. Ahora los dos dependen de este paquete: se arregla aquí, con sus tests, y cada bot solo sube la versión que tiene fijada.

Un único módulo, sin dependencias fuera de la librería estándar de Python.

## Qué hace

- **Entiende un nombre**: título, año, temporada y episodio, resolución, HDR, idioma, códecs, fuente y grupo (`parse_metadata`).
- **Sugiere un nombre limpio** con una plantilla (`suggest_name`), también para un fichero o una subcarpeta que toma de su carpeta lo que le falta (`suggest_file_name`, `suggest_folder_name`):
  - `The.Matrix.1999.1080p.BluRay.x264.mkv` → `The Matrix (1999) - 1080p.mkv`
  - `Chicago.Fire.S14E04.1080p.WEB.h264-ETHEL.mkv` → `14x04 - Chicago Fire - 1080p.mkv`
- **Valida y aplica plantillas** del usuario (`validate_template`, `render_template`): `{campo}` obligatorio, `{campo.N}` con ceros, `[ ... ]` bloque opcional. Los campos se aceptan en español y en inglés.
- **Empareja subtítulos** con su vídeo para renombrarlos juntos (`companion_subtitle_name`) y reconoce las muestras (`is_sample_file`).
- **Encuentra la carpeta de una serie** entre lo que ya hay descargado (`series_identity`, `series_dir_candidates`, `series_auto_dir`).

Lo que depende de dónde viven los ficheros (el disco, un gestor de torrents) no está aquí: lo pone cada bot.

## Instalarlo

Sin PyPI: del propio repositorio, fijado al commit de un tag.

```
dgongut-name-parser @ https://github.com/dgongut/name-parser/archive/<commit>.zip
```

```python
import name_parser

name_parser.suggest_name("The.Matrix.1999.1080p.BluRay.x264.mkv")
# 'The Matrix (1999) - 1080p.mkv'
```

## Publicar una versión

1. Cambia el código y añade su comprobación en `tests/`.
2. Sube `version` en `pyproject.toml` y `__version__` en `name_parser.py` (un test comprueba que coinciden).
3. Crea el tag `v<versión>`.
4. En cada bot, cambia el commit fijado en `requirements.txt` por el de ese tag.

Lo que usan los bots está listado en `tests/test_package.py`: quitar o renombrar algo de esa lista es un cambio de versión mayor.

## Tests

```bash
pip install pytest
python -m pytest
```
