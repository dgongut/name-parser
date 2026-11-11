"""Los tests importan el módulo del repositorio, no uno que hubiera instalado."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
