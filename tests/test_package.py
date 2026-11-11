"""El paquete: que la versión del módulo y la de pyproject.toml sean la misma,
y que lo que usan los bots siga estando ahí con ese nombre."""

import re
from pathlib import Path

import name_parser

ROOT = Path(__file__).resolve().parent.parent

# Lo que importan DropBot y Torrent-Controller-Bot. Quitar o renombrar algo de
# aquí rompe a los dos: es un cambio de versión mayor
PUBLIC_API = (
	"VALID_EXTENSIONS", "SUBTITLE_EXTENSIONS", "SEASON_ONLY_PATTERNS", "CANONICAL_FIELDS",
	"DEFAULT_MOVIE_TEMPLATE", "DEFAULT_SERIES_TEMPLATE", "DEFAULT_SEASON_PACK_TEMPLATE",
	"TemplateError", "validate_template", "render_template", "parse_metadata",
	"suggest_name", "suggest_file_name", "suggest_folder_name",
	"is_sample_file", "companion_subtitle_name",
	"series_identity", "series_dir_candidates", "series_auto_dir", "comparable_text",
)


def test_la_version_es_la_misma_en_los_dos_sitios():
	declared = re.search(r'^version = "([^"]+)"', (ROOT / "pyproject.toml").read_text(encoding="utf-8"), re.MULTILINE)
	assert declared and declared.group(1) == name_parser.__version__


def test_lo_que_usan_los_bots_sigue_ahi():
	missing = [name for name in PUBLIC_API if not hasattr(name_parser, name)]
	assert not missing, f"falta en name_parser: {missing}"


def test_solo_usa_la_libreria_estandar():
	imports = re.findall(r"^(?:import|from) (\w+)", (ROOT / "name_parser.py").read_text(encoding="utf-8"), re.MULTILINE)
	assert set(imports) <= {"functools", "re", "unicodedata"}
