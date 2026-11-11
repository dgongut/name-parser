"""La detección de la carpeta de una serie.

Un episodio nuevo se ofrece (o va directo) a la carpeta donde ya está el resto
de su serie. Equivocarse es peor que no ofrecer nada: un episodio movido a la
serie que no es son datos en el sitio equivocado. Por eso casi todo esto va de
lo que NO debe coincidir: series que comparten palabras, una película con el
nombre de una serie, el mismo título de otro año, la carpeta de descargas
donde cae todo antes de ordenarlo.

Son comprobaciones sueltas que se hacen al importar y se apuntan en FAILED;
un único test al final las recoge para pytest."""

from name_parser import series_auto_dir, series_dir_candidates, series_identity

FAILED = []
CHECKS = [0]


def check(description, actual, expected):
	CHECKS[0] += 1
	if actual != expected:
		FAILED.append(f"{description}\n  expected: {expected!r}\n  actual:   {actual!r}")


def key(name):
	identity = series_identity(name)
	return identity and (identity["key"], identity["year"], identity["season"])


def dirs(name, torrents, **kwargs):
	return [d for d, _named in series_dir_candidates(name, torrents, **kwargs)]


# ---------------------------------------------------------------------------
# 1. WHAT A SERIES IS
# ---------------------------------------------------------------------------

check("a release name", key("Chicago.Fire.S14E04.1080p.WEB.h264-ETHEL"), ("chicago fire", "", 14))
check("a name the bot renamed with the default template", key("14x04 - Chicago Fire.mkv"), ("chicago fire", "", 14))
check("renamed, with the resolution", key("14x04 - Chicago Fire - 1080p HDR.mkv"), ("chicago fire", "", 14))
check("renamed season pack", key("T14 - Chicago Fire - 1080p"), ("chicago fire", "", 14))
check("renamed season pack in English", key("S14 - Chicago Fire"), ("chicago fire", "", 14))
check("a season pack in Spanish", key("Chicago Fire - Temporada 14 [HDTV 720p]"), ("chicago fire", "", 14))
check("a name that starts with 'Temporada'", key("Temporada 14 - Chicago Fire"), ("chicago fire", "", 14))
check("a name that starts with S01E01", key("S14E04 - Chicago Fire - 1080p.mkv"), ("chicago fire", "", 14))
check("a pack of several seasons has no single season", key("Chicago.Fire.S01-S03.1080p"), ("chicago fire", "", None))
check("an episode range", key("Chicago.Fire.S14E01-E08.1080p"), ("chicago fire", "", 14))
check("the year is kept apart from the title", key("Doctor.Who.2005.S01E01.720p"), ("doctor who", "2005", 1))
check("a year in parentheses", key("Chicago Fire (2012) S14E05"), ("chicago fire", "2012", 14))
check("lowercase and dots", key("chicago.fire.s14e04"), ("chicago fire", "", 14))
check("accents do not count", key("Pokémon S01E01"), ("pokemon", "", 1))
check("underscores", key("chicago_fire_S14E04"), ("chicago fire", "", 14))
check("a .torrent file name", key("Chicago.Fire.S14E04.1080p.torrent"), ("chicago fire", "", 14))
check("the 'Capitulo' convention", key("La.Que.Se.Avecina.Capitulo.1301.1080p.mkv"), ("la que se avecina", "", 13))
check("a movie is not a series", series_identity("El Camino Una pelicula de Breaking Bad (2019) 1080p"), None)
check("a movie with a series name in it", series_identity("El.Camino.A.Breaking.Bad.Movie.2019.1080p.NF.WEB-DL"), None)
check("a plain movie", series_identity("The.Matrix.1999.1080p.BluRay.x264-GROUP.mkv"), None)
check("an episode with no title at all", series_identity("1x01.mkv"), None)
check("an episode marker and nothing else", series_identity("S01E01"), None)
check("nothing", series_identity(""), None)
check("None", series_identity(None), None)
check("a magnet with no name", series_identity("magnet"), None)
check("a number as .torrent name", series_identity("123456"), None)
check("the title keeps how it was written, for the messages",
	series_identity("Chicago.Fire.S14E04.1080p")["title"], "Chicago Fire")

# ---------------------------------------------------------------------------
# 2. WHERE THE SERIES IS
# ---------------------------------------------------------------------------

CHICAGO = [
	("Chicago.Fire.S14E01.1080p.WEB.h264-ETHEL", "/media/SERIES/Chicago Fire", 100),
	("14x02 - Chicago Fire.mkv", "/media/SERIES/Chicago Fire/", 200),
	("chicago fire s14e03 720p", "/media/SERIES/Chicago Fire", 300),
	("Chicago.Med.S10E01.1080p", "/media/SERIES/Chicago Med", 400),
	("Chicago.PD.S12E01.1080p", "/media/SERIES/Chicago PD", 500),
]
NEW = "Chicago.Fire.S14E04.1080p.WEB.h264-ETHEL"

check("the episodes of the series point at their folder",
	series_dir_candidates(NEW, CHICAGO, current_dir="/downloads", generic_dirs=["/downloads"]),
	[("/media/SERIES/Chicago Fire", True)])
check("a trailing slash is the same folder", dirs(NEW, CHICAGO), ["/media/SERIES/Chicago Fire"])
check("a show that shares a word is another show", dirs("Chicago.Med.S10E02", CHICAGO), ["/media/SERIES/Chicago Med"])
check("the user's example, renamed", dirs("14x04 - Chicago Fire.mkv", CHICAGO), ["/media/SERIES/Chicago Fire"])
check("a word of the title is not the title", dirs("Fire.S01E01", CHICAGO), [])
check("a longer title is not the title", dirs("Chicago.Fire.Rescue.S01E01", CHICAGO), [])
check("a movie never gets a series folder", dirs("Chicago.Fire.2019.1080p", CHICAGO), [])
check("nothing of the series", dirs("Severance.S02E01", CHICAGO), [])
check("no torrents at all", dirs(NEW, []), [])

BREAKING = [("Breaking.Bad.S05E16.1080p", "/tv/Breaking Bad", 1)]
check("El Camino is a movie: no Breaking Bad folder for it",
	dirs("El.Camino.A.Breaking.Bad.Movie.2019.1080p", BREAKING), [])
check("and a Breaking Bad episode never goes where El Camino is",
	dirs("Breaking.Bad.S01E01", [("El.Camino.A.Breaking.Bad.Movie.2019.1080p", "/movies", 1)]), [])

# Years
WHO = [("Doctor.Who.1963.S01E01", "/tv/Doctor Who (1963)", 1), ("Doctor.Who.2005.S01E01", "/tv/Doctor Who (2005)", 2)]
check("a year picks its own series", dirs("Doctor.Who.2005.S02E01", WHO), ["/tv/Doctor Who (2005)"])
check("the other year too", dirs("Doctor Who (1963) S02E01", WHO), ["/tv/Doctor Who (1963)"])
check("without a year both are possible, and both are offered",
	sorted(dirs("Doctor.Who.S02E01", WHO)), ["/tv/Doctor Who (1963)", "/tv/Doctor Who (2005)"])
check("so nothing is moved without asking", series_auto_dir(series_dir_candidates("Doctor.Who.S02E01", WHO)), None)
check("a reference without a year matches a name with one",
	dirs("Chicago Fire (2012) S14E05", CHICAGO), ["/media/SERIES/Chicago Fire"])
check("a folder named with another year is not the series",
	dirs("Chicago Fire (2012) S14E05", [], known_dirs=["/tv/Chicago Fire (1999)"]), [])

# The default download folder
STRAY = [("Chicago.Fire.S14E01", "/media/SERIES/Chicago Fire", 1),
		("Chicago.Fire.S14E02", "/downloads", 2), ("Chicago.Fire.S14E03", "/downloads", 3)]
check("the folder where everything lands is never the series folder",
	dirs(NEW, STRAY, generic_dirs=["/downloads"]), ["/media/SERIES/Chicago Fire"])
check("even when more episodes are still there",
	series_auto_dir(series_dir_candidates(NEW, STRAY, generic_dirs=["/downloads/"])), "/media/SERIES/Chicago Fire")
check("a generic folder named after the series does count",
	dirs(NEW, [("Chicago.Fire.S14E01", "/media/Chicago Fire", 1)], generic_dirs=["/media/Chicago Fire"]),
	["/media/Chicago Fire"])
check("an empty generic dir changes nothing", dirs(NEW, STRAY, generic_dirs=["", None]),
	["/media/SERIES/Chicago Fire", "/downloads"])

# Where the torrent already is
check("already in the series folder: nothing to suggest",
	dirs(NEW, CHICAGO, current_dir="/media/SERIES/Chicago Fire"), [])
check("already there, written with a trailing slash",
	dirs(NEW, CHICAGO, current_dir="/media/SERIES/Chicago Fire/"), [])
check("a stray episode elsewhere is no reason to move it",
	dirs(NEW, CHICAGO + [("Chicago.Fire.S14E09", "/old/stuff", 1)], current_dir="/media/SERIES/Chicago Fire"), [])
check("but from somewhere else the series folder is offered",
	dirs(NEW, CHICAGO, current_dir="/media/peliculas"), ["/media/SERIES/Chicago Fire"])

# Ranking
FLAT = [("Chicago.Fire.S13E01", "/data/series", 50), ("Chicago.Fire.S13E02", "/data/series", 60),
		("Chicago.Fire.S14E01", "/media/SERIES/Chicago Fire", 10)]
check("a folder named after the series goes before a shared one",
	dirs(NEW, FLAT), ["/media/SERIES/Chicago Fire", "/data/series"])
check("a shared folder alone is still offered",
	series_dir_candidates(NEW, FLAT[:2]), [("/data/series", False)])
check("but never moved to without asking", series_auto_dir(series_dir_candidates(NEW, FLAT[:2])), None)
TWO = [("Chicago.Fire.S14E01", "/a/Chicago Fire", 10), ("Chicago.Fire.S14E02", "/b/Chicago Fire", 20),
		("Chicago.Fire.S14E03", "/b/Chicago Fire", 30)]
check("more episodes first", dirs(NEW, TWO), ["/b/Chicago Fire", "/a/Chicago Fire"])
check("two named folders are a doubt", series_auto_dir(series_dir_candidates(NEW, TWO)), None)
TIE = [("Chicago.Fire.S14E01", "/a/Chicago Fire", 10), ("Chicago.Fire.S14E02", "/b/Chicago Fire", 20)]
check("a tie goes to the most recent", dirs(NEW, TIE), ["/b/Chicago Fire", "/a/Chicago Fire"])
check("a missing date is the oldest", dirs(NEW, [TIE[0], ("Chicago.Fire.S14E02", "/b/Chicago Fire", None)]),
	["/a/Chicago Fire", "/b/Chicago Fire"])
check("a torrent without folder is ignored", dirs(NEW, [("Chicago.Fire.S14E01", "", 1)]), [])
check("a torrent without name is ignored", dirs(NEW, [("", "/x/Chicago Fire", 1)]), [])
check("no candidates, nothing automatic", series_auto_dir([]), None)

# Favorites
check("a favorite named after the series counts with no torrent at all",
	series_dir_candidates(NEW, [], known_dirs=["/media/SERIES/Chicago Fire", "/media/SERIES"]),
	[("/media/SERIES/Chicago Fire", True)])
check("which is enough to move it", series_auto_dir(series_dir_candidates(NEW, [], known_dirs=["/tv/Chicago Fire/"])),
	"/tv/Chicago Fire")
check("a favorite that is not named after it does not", dirs(NEW, [], known_dirs=["/media/SERIES", "/downloads"]), [])
check("a favorite for another show does not", dirs(NEW, [], known_dirs=["/media/SERIES/Chicago Med"]), [])
check("a favorite with the series deeper in the path does not",
	dirs(NEW, [], known_dirs=["/media/Chicago Fire/extras"]), [])
check("a favorite with the year in parentheses", dirs(NEW, [], known_dirs=["/tv/Chicago Fire (2012)"]),
	["/tv/Chicago Fire (2012)"])
check("a favorite with dots", dirs(NEW, [], known_dirs=["/tv/chicago.fire"]), ["/tv/chicago.fire"])
check("the root is nobody's folder", dirs(NEW, [], known_dirs=["/", ""]), [])
check("a favorite and the torrents agree on one folder",
	series_dir_candidates(NEW, CHICAGO, known_dirs=["/media/SERIES/Chicago Fire"]), [("/media/SERIES/Chicago Fire", True)])

# Season folders
MAD = [("Mad.Men.S01E01", "/tv/Mad Men/Season 01", 1), ("Mad.Men.S01E02", "/tv/Mad Men/Season 01", 2)]
check("the same season, the same folder", dirs("Mad.Men.S01E03", MAD), ["/tv/Mad Men/Season 01"])
check("the next season, the next folder, padding kept", dirs("Mad.Men.S02E01", MAD), ["/tv/Mad Men/Season 02"])
check("a season folder inside the series folder counts as named",
	series_auto_dir(series_dir_candidates("Mad.Men.S02E01", MAD)), "/tv/Mad Men/Season 02")
check("a season over 9 with padding", dirs("Mad.Men.S10E01", MAD), ["/tv/Mad Men/Season 10"])
check("a pack of several seasons goes to the series folder", dirs("Mad.Men.S01-S03.1080p", MAD), ["/tv/Mad Men"])
check("Temporada without padding", dirs("Mad.Men.S12E01", [("Mad.Men.S11E01", "/tv/Mad Men/Temporada 11", 1)]),
	["/tv/Mad Men/Temporada 12"])
check("Temporada from 9 to 10", dirs("Mad.Men.S10E01", [("Mad.Men.S09E01", "/tv/Mad Men/Temporada 9", 1)]),
	["/tv/Mad Men/Temporada 10"])
check("a bare S01 folder", dirs("Mad.Men.S02E01", [("Mad.Men.S01E01", "/tv/Mad Men/S01", 1)]), ["/tv/Mad Men/S02"])
check("a season pack follows the season folders", dirs("Mad.Men.S03.1080p", MAD), ["/tv/Mad Men/Season 03"])
check("two seasons of folders become one for the next season",
	series_dir_candidates("Mad.Men.S03E01", MAD + [("Mad.Men.S02E01", "/tv/Mad Men/Season 02", 9)]),
	[("/tv/Mad Men/Season 03", True)])
check("a favorite season folder is followed too", dirs("Mad.Men.S02E01", [], known_dirs=["/tv/Mad Men/Season 01"]),
	["/tv/Mad Men/Season 02"])
check("a season folder of another show is not followed",
	dirs("Mad.Men.S02E01", [], known_dirs=["/tv/Lost/Season 01"]), [])
check("already in the next season folder", dirs("Mad.Men.S02E01", MAD, current_dir="/tv/Mad Men/Season 02"), [])
check("in last season's folder, the next one is offered",
	dirs("Mad.Men.S02E05", MAD, current_dir="/tv/Mad Men/Season 01"), ["/tv/Mad Men/Season 02"])
check("a season folder at the root is left as it is", dirs("Mad.Men.S02E01", [("Mad.Men.S01E01", "Season 01", 1)]),
	["Season 01"])
check("a folder with a number that is not a season is left as it is",
	dirs("Mad.Men.S02E01", [("Mad.Men.S01E01", "/tv/Mad Men 2007", 1)]), ["/tv/Mad Men 2007"])

# Windows paths (Deluge on Windows)
check("backslashes are kept", dirs("Mad.Men.S02E01", [("Mad.Men.S01E01", "D:\\TV\\Mad Men\\Temporada 1", 1)]),
	["D:\\TV\\Mad Men\\Temporada 2"])
check("a Windows series folder is named", series_auto_dir(series_dir_candidates("Mad.Men.S02E01",
	[("Mad.Men.S01E01", "D:\\TV\\Mad Men", 1)])), "D:\\TV\\Mad Men")

# Numbers that are no season: a year, or more digits than a season ever has.
# The folder is left as it is, and nothing breaks on the way
MYTH = [("MythBusters.S10E01.1080p", "/tv/MythBusters/Season 2010", 1)]
check("a season named after its year is no season 20",
	series_dir_candidates("MythBusters.S11E01.1080p", MYTH), [("/tv/MythBusters/Season 2010", False)])
check("so it is only offered", series_auto_dir(series_dir_candidates("MythBusters.S11E01.1080p", MYTH)), None)
check("the same goes for a favorite", dirs("MythBusters.S11E01.1080p", [], known_dirs=["/tv/MythBusters/Season 2010"]), [])
for folder in ("Season 2010", "Season 001", "Season 100", "Temporada 2010"):
	check(f"'{folder}' is left as it is", dirs("Mad.Men.S02E01", [("Mad.Men.S01E01", f"/tv/Mad Men/{folder}", 1)]),
		[f"/tv/Mad Men/{folder}"])
	check(f"'{folder}' is no season", key(folder), None)
check("Open Season is a movie, not season 20", series_identity("Open.Season.2006.1080p.BluRay.x264-GRP"), None)
check("nor is Killing Season", series_identity("Killing.Season.2013.1080p.BluRay"), None)
check("Season 2 still is one", key("Mad.Men.Season.2.1080p"), ("mad men", "", 2))

# A folder named after the series and its season: the season is swapped as
# well, never sending a new season into last season's folder
FIRE13 = [("Chicago Fire - Temporada 13 [HDTV][Cap.1310]", "/media/series/Chicago Fire - Temporada 13", 1)]
FIRE14 = "Chicago Fire - Temporada 14 [HDTV][Cap.1404]"
check("the next season of a 'Show - Temporada N' folder",
	series_dir_candidates(FIRE14, FIRE13), [("/media/series/Chicago Fire - Temporada 14", True)])
check("which is where it goes without asking", series_auto_dir(series_dir_candidates(FIRE14, FIRE13)),
	"/media/series/Chicago Fire - Temporada 14")
check("never into last season's", "/media/series/Chicago Fire - Temporada 13" in dirs("Chicago.Fire.S14E04", FIRE13), False)
check("the same season stays in it", dirs("Chicago Fire - Temporada 13 [HDTV][Cap.1311]", FIRE13),
	["/media/series/Chicago Fire - Temporada 13"])
check("a release name as the folder", series_dir_candidates("Show.Name.S02E01", [("Show.Name.S01E01", "/tv/Show.Name.S01", 1)]),
	[("/tv/Show.Name.S02", True)])
check("keeping its padding", dirs("Show.Name.S10E01", [("Show.Name.S09E01", "/tv/Show.Name.S09", 1)]), ["/tv/Show.Name.S10"])
check("from 9 to 10", dirs("Chicago.Fire.S10E01", [("Chicago.Fire.S09E01", "/media/Chicago Fire - Temporada 9", 1)]),
	["/media/Chicago Fire - Temporada 10"])
check("with the year of the show", dirs("Doctor.Who.2005.S02E01", [("Doctor.Who.2005.S01E01", "/tv/Doctor Who (2005) - Season 1", 1)]),
	["/tv/Doctor Who (2005) - Season 2"])
check("digits in the title are not the season", dirs("9-1-1.S02E01", [("9-1-1.S01E01", "/tv/9-1-1 - Temporada 1", 1)]),
	["/tv/9-1-1 - Temporada 2"])
check("with backslashes", dirs("Chicago.Fire.S14E01", [("Chicago.Fire.S13E01", "D:\\TV\\Chicago Fire - Temporada 13", 1)]),
	["D:\\TV\\Chicago Fire - Temporada 14"])
check("a favorite named that way is followed too",
	dirs("Chicago.Fire.S14E01", [], known_dirs=["/media/series/Chicago Fire - Temporada 13"]), ["/media/series/Chicago Fire - Temporada 14"])
check("a pack of several seasons goes next to the season folders, asking first",
	series_dir_candidates("Chicago.Fire.S01-S03.1080p", FIRE13), [("/media/series", False)])
check("the season folder of another show is left as it is, and only offered",
	series_dir_candidates("Chicago.Fire.S14E01", [("Chicago.Fire.S13E01", "/media/series/Chicago Med - Temporada 9", 1)]),
	[("/media/series/Chicago Med - Temporada 9", False)])
check("a folder for part of another season is no place for it",
	dirs("Stranger.Things.S05E01", [("Stranger.Things.S04E01", "/tv/Stranger Things S04 Vol 1", 1)]), [])
check("but it is for that season",
	dirs("Stranger.Things.S04E08", [("Stranger.Things.S04E01", "/tv/Stranger Things S04 Vol 1", 1)]), ["/tv/Stranger Things S04 Vol 1"])

# An older season: the number is written the way the folders write it, which
# a number with no leading zero cannot tell. 'Temporada 2' is what sits next
# to 'Temporada 13', never 'Temporada 02'
check("an older season of a 'Temporada 13' folder",
	dirs("Chicago.Fire.S02E01", [("Chicago.Fire.S13E01", "/tv/Chicago Fire/Temporada 13", 1)]), ["/tv/Chicago Fire/Temporada 2"])
check("named after the show too", dirs("Chicago.Fire.S02E01", FIRE13), ["/media/series/Chicago Fire - Temporada 2"])
check("a padded folder stays padded", dirs("Mad.Men.S02E01", [("Mad.Men.S09E01", "/tv/Mad Men/Season 09", 1)]),
	["/tv/Mad Men/Season 02"])
check("and so does a compact marker", dirs("Show.Name.S02E01", [("Show.Name.S13E01", "/tv/Show.Name.S13", 1)]), ["/tv/Show.Name.S02"])
check("a compact one with a single digit", dirs("Show.Name.S10E01", [("Show.Name.S9E01", "/tv/Show.Name.S9", 1)]), ["/tv/Show.Name.S10"])
# An English ordinal goes with its number
for season, folder in [(2, "2nd Season"), (3, "3rd Season"), (4, "4th Season"), (11, "11th Season"), (12, "12th Season"),
						(21, "21st Season"), (22, "22nd Season")]:
	check(f"'1st Season' for season {season}",
		dirs(f"Show.Name.S{season:02d}E01", [("Show.Name.S01E01", "/tv/Show Name/1st Season", 1)]), [f"/tv/Show Name/{folder}"])
check("an ordinal folder named after the show", series_dir_candidates("Show.Name.S02E01",
	[("Show.Name.S01E01", "/tv/Show Name 1st Season", 1)]), [("/tv/Show Name 2nd Season", True)])
# A spaced dash between 'Season' and its number
check("a 'Season - 13' folder", dirs("Show.Name.S14E01", [("Show.Name.S13E01", "/tv/Show Name/Season - 13", 1)]),
	["/tv/Show Name/Season - 14"])
check("is named", series_auto_dir(series_dir_candidates("Show.Name.S14E01", [("Show.Name.S13E01", "/tv/Show Name/Season - 13", 1)])),
	"/tv/Show Name/Season - 14")
check("a 'Show - Season - 1' name", key("Show - Season - 1 - 1080p"), ("show", "", 1))
# A pack whose dash number may be ten seasons is still that show's
check("a 'Season 1 - 10' pack", (key("Friends Season 1 - 10 [1080p BluRay x265]") or ("",))[0], "friends")

# The same series written differently
VARIANTS = ["Chicago.Fire.S14E01", "chicago fire 14x02", "CHICAGO_FIRE_S14E03", "Chicago Fire - 14x05 - Título",
			"[Grupo] Chicago Fire S14E06 [1080p]", "14x07 - Chicago Fire - 1080p.mkv"]
for variant in VARIANTS:
	check(f"'{variant}' is Chicago Fire", key(variant)[0], "chicago fire")


def test_series_folders():
	assert CHECKS[0] > 50
	assert not FAILED, f"{len(FAILED)} comprobaciones fallan:\n\n" + "\n\n".join(FAILED)
