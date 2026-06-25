# scrapers/__init__.py
from .remoteok       import scrape as scrape_remoteok
from .weworkremotely import scrape as scrape_wwr
from .remotive       import scrape as scrape_remotive
from .himalayas      import scrape as scrape_himalayas
from .wellfound      import scrape as scrape_wellfound

ALL_SCRAPERS = [
    ("RemoteOK",        scrape_remoteok),
    ("WeWorkRemotely",  scrape_wwr),
    ("Remotive",        scrape_remotive),
    ("Himalayas",       scrape_himalayas),
    ("Arbeitnow",       scrape_wellfound),
]
