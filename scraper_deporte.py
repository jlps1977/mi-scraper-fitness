#!/usr/bin/env python3
"""
Scraper de Ciencias del Deporte — corpus para IA de entrenadores deportivos.
Cubre 70+ fuentes en 10 categorías:
  A) Organismos internacionales y antidopaje (IOC, WADA, USADA, UKAD, Global DRO)
  B) Federaciones internacionales por deporte (World Athletics, FIFA, FIBA, FIVB,
     World Aquatics, UCI, ITF, World Rugby, IHF, BWF, Taekwondo, IJF, ISU, FIS,
     World Rowing, World Gymnastics, World Boxing)
  C) Ciencias del deporte (ACSM, NSCA, ECSS, BASES UK, ASCA AU, UKSCA,
     CONADE, Sport Australia Clearinghouse, UK Sport, USOPC)
  D) Medicina deportiva (FIMS, AMSSM, AOSSM, ESSKA, BJSM, Sports Health, NATA)
  E) Nutrición deportiva (ISSN, AIS, GSSI, SCAN, IOC Nutrition)
  F) Psicología del deporte (AASP, ISSP, FEPSAC)
  G) Fuerza, acondicionamiento y biomecánica (ISBS, NSCA Strength, VBT,
     Catapult)
  H) Revistas científicas OA (JSSM, Sports MDPI, Frontiers Sports, BMC Sports,
     PeerJ Sports, Translational Sports Med, IJSPP, JSS)
  I) Institutos de élite (AIS Australia, INEF Spain, Aspire Qatar, CSI Canada,
     Sport New Zealand)
  J) Bases de datos y recursos educativos (SIRC, PubMed sports, coach resources)

Uso: .venv/bin/python scraper_deporte.py
Reanuda desde progress_deporte.json (crea si no existe).
"""

import os, re, json, time
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from google.oauth2.credentials import Credentials

# ── Drive — IDs de carpetas ────────────────────────────────────────────────────
DRIVE_DEPORTE_ROOT_ID             = "1nInRjNCwMhbwTa39QYSfxJvu7Q-SIAZv"

# A. Organismos internacionales y antidopaje
DRIVE_IOC_OLYMPICS_ID             = "1999K4g1QfgLhYkudkrMp-kDx_E8cm1n6"
DRIVE_WADA_ANTIDOPING_ID          = "19q2P1KHuaxTHEccc74aqtt3Gr6ptKYw4"
DRIVE_USADA_ID                    = "15wBmpFPnjsHtwzWYGhXPXAm98LJJDc-G"
DRIVE_UKAD_ID                     = "1guV_mxYV03ia1ybi4Nq19xFNkK-c5jmb"
DRIVE_GLOBAL_DRO_ID               = "1GVZ4QbqVD4odbrp60ptUPWXZ5Faon2Cb"

# B. Federaciones internacionales
DRIVE_WORLD_ATHLETICS_ID          = "1yRDskY5BwOZ9lbMXmqoWzkSqpOfMEDD1"
DRIVE_FIFA_FOOTBALL_ID            = "1AAPQX-MlzN6T_cOsICe1k2thskWmJMj4"
DRIVE_FIBA_BASKETBALL_ID          = "1bshu6FxnDowt586aJxssB8S4vwFEBVA7"
DRIVE_FIVB_VOLLEYBALL_ID          = "1ipjEZNrIMWqZUL5KiE1iPjhAt8e3cm6A"
DRIVE_WORLD_AQUATICS_ID           = "19TxwjvK3oo5EmlfBKEZeigRWx1GuLtWI"
DRIVE_UCI_CYCLING_ID              = "1erjwHyJN-kXAI7ivuh1hTYdihPeyBOEg"
DRIVE_ITF_TENNIS_ID               = "1UDTWISFrOO6pdgRX_cIkieX5jmzfYQxp"
DRIVE_WORLD_RUGBY_ID              = "137jlVDXwg9jsI2V8XlYeOeraF32eCYdV"
DRIVE_IHF_HANDBALL_ID             = "1QvflIx1Le3uDaN4y4qiJlcLPligm1qh-"
DRIVE_BWF_BADMINTON_ID            = "1eNP0nux3y6CxhYceSJhsQiYsdyiGPdQr"
DRIVE_WORLD_TAEKWONDO_ID          = "1p0dIICMdrK6fzbaj0zT8sNuk_mlqs-1Y"
DRIVE_IJF_JUDO_ID                 = "1hWEt6MMFS_XwB-xEYH8qOTgMk2njIh17"
DRIVE_ISU_SKATING_ID              = "15S_DNOf__0E5LySE2QeKg5vAhV3PxLd9"
DRIVE_FIS_SKIING_ID               = "10btfXeX-p7dcKX-1zMkRFDrAWYPeJVI9"
DRIVE_WORLD_ROWING_ID             = "1sI8uhfbYDgPWrPXrUsrQ6uIgtzKeQmLW"
DRIVE_WORLD_GYMNASTICS_ID         = "1iY4kq9z66ukgqIBgBjsR1lSJi8jyys0q"
DRIVE_WORLD_BOXING_ID             = "1EGQzGnUxnVbu2tmBDykHFgmBsrVLqyrC"
DRIVE_UFC_MMA_RESOURCES_ID        = "1Bd-ysMvjktvrV17JqfN45dUSeGssnygx"

# C. Ciencias del deporte
DRIVE_ACSM_ID                     = "18F7TpsMfUY2D6YZwac-LPrOAMDsh5-y1"
DRIVE_NSCA_ID                     = "1FFeBRLWP1FD_jJZnLirkkVAUuxmi8TYF"
DRIVE_ECSS_ID                     = "1atUEtwV3liyw7-oTS-19g1YDO0Qj0jHw"
DRIVE_BASES_UK_ID                 = "1dkqPav--YidkE6SMhqv7coGhQVoDRDsN"
DRIVE_ASCA_AU_ID                  = "1-GiP_0Aht9uCQnxvY2YB-JLGLzBQEnnD"
DRIVE_UKSCA_ID                    = "1_kv5SiiUPIJfE-24QLAlebV-l3l9rLRo"
DRIVE_CONADE_MEXICO_ID            = "14g8Zkxtluy-gucmJpQagfoRxMCZ4JKUf"
DRIVE_SPORT_AUSTRALIA_CLEARINGHOUSE_ID = "1RRT_Ohw86HzbfHkyAewE66Lxfl13Bt_6"
DRIVE_UK_SPORT_ID                 = "1hxqgADr6l0-zigDLRX8k2J1Go482W64j"
DRIVE_USOPC_RESOURCES_ID          = "1WgW1ac4QCLl0iUM6xU4iqsPee9sDvMzm"

# D. Medicina deportiva
DRIVE_FIMS_ID                     = "1pUHcsOfeYy4RsGeDwcSzEopYL2FzoK25"
DRIVE_AMSSM_ID                    = "1MNQVel3D9TMfjOnLYPkaAhfZGYBTcWV6"
DRIVE_AOSSM_ID                    = "1jRcMw1HSq3fUoQ5nYYnMjbBEaUTmDte_"
DRIVE_ESSKA_ID                    = "1hmNNcCD-DaQv2I88p5yHKrLsqoTirziu"
DRIVE_BJSM_ID                     = "1X8db7M6uKQLfyER8c_TWrfLU_R_OlJXd"
DRIVE_SPORTS_HEALTH_JOURNAL_ID    = "1snvwxRluGjAnefcRM1KlV2bp25DA8MtA"
DRIVE_NATA_ATHLETIC_TRAINING_ID   = "15ekn6DwhXkPxGhfr8IC4biXmi5r7Tk8P"

# E. Nutrición deportiva
DRIVE_ISSN_NUTRITION_ID           = "1qRv3pDW6-a6DJkSVIpreiRhNIGyknsWR"
DRIVE_AIS_NUTRITION_ID            = "1EKsw69L6ZTEQ5QAFtQ0YGijCuW67GJ0S"
DRIVE_GSSI_GATORADE_ID            = "1mP4YtXIAdnut4weyP-duqmtocGdc8A_D"
DRIVE_SCAN_DIETITIANS_ID          = "1yJT2pP5B6BnTshUKB8tZDNF3UOwFUl9s"
DRIVE_IOC_NUTRITION_ID            = "1_bj4TJ-ubWxgLnjk6e50ak5PVpgvrwWT"

# F. Psicología del deporte
DRIVE_AASP_PSYCHOLOGY_ID          = "1EA-kWJEMxJYaVMc74PNshYK58TNB16G4"
DRIVE_ISSP_PSYCHOLOGY_ID          = "1ZzWGWputPfG4bO-JCmnOJA9ir8-29c7t"
DRIVE_FEPSAC_EUROPE_ID            = "1o9bM-2RLQCFKmxL5cPEGvqFhd1kZarhS"

# G. Fuerza, acondicionamiento y biomecánica
DRIVE_ISBS_BIOMECHANICS_ID        = "1tQ7d8nTJ6dzTup6lTuq7lxSlm5sX9u7g"
DRIVE_NSCA_STRENGTH_ID            = "1wOxG-JW_nZfETKrMFFTW2kvhFwE5gJJU"
DRIVE_VELOCITY_BASED_TRAINING_ID  = "1ls-foMxmMn0_5NursmVqc_ezJoyhP5mp"
DRIVE_CATAPULT_RESOURCES_ID       = "1DtdnqJN1Mbp5xBu6k4L-zyFv4Hvmp0O5"

# H. Revistas OA
DRIVE_JSSM_JOURNAL_ID             = "1ojhSAjU9jHvwMSdSqIBTahUUm2WC5Y3O"
DRIVE_SPORTS_MDPI_ID              = "15J2FpvGSIqVQO1hwnEjwdq5axmQ38N66"
DRIVE_FRONTIERS_SPORTS_ID         = "1LwY7FTPell4JQ7w8GXqjJbhe7dAuoHm9"
DRIVE_BMC_SPORTS_SCI_ID           = "1E3oI87qImzuX5T2DUNenNrY7oEIF2_29"
DRIVE_PEERJ_SPORTS_ID             = "1hmZb9OkH0V_Ymrbtf2wHggaDeGCtdLYY"
DRIVE_TRANSLATIONAL_SPORTS_MED_ID = "1p5XWyksDVV50CkEO3Cl-dNvMInWkWS2h"
DRIVE_INTL_J_SPORTS_PHYSIOL_ID    = "17YR0ywTDEzcux-8irSAhVciBXXPqoNwp"
DRIVE_JOURNAL_SPORT_SCIENCE_ID    = "1bJVVBpRDU2K5If3J19S9FO__YmU9Jb88"

# I. Institutos de élite
DRIVE_AIS_AUSTRALIA_ID            = "1QI6wpBlSH7XtVC-moYDOdJV_Bm_v3p6u"
DRIVE_INEF_SPAIN_ID               = "17sXNCD7mGAXpQjRCTq_sj0mw_8EeStMK"
DRIVE_ASPIRE_QATAR_ID             = "1w2H2wYysyEScVLtCGB-0dXiufUVxaEPi"
DRIVE_CANADIAN_SPORT_INSTITUTE_ID = "1Kc7W3EfgCyXWgAPoF0Gc0rRM3oRYcWs-"
DRIVE_SPORT_NEW_ZEALAND_ID        = "1QpNLkoMRDHrTL_ZPCeVnM5vJw5LphtbY"

# J. Bases de datos y recursos educativos
DRIVE_SIRC_CANADA_ID              = "1WRXUMyQyUDAtUeqijd4DY_QlVmKtDGju"
DRIVE_PUBMED_SPORTS_ID            = "1NOmRA3YFVAePvXFA120ZD6kedGYsKKj3"
DRIVE_COACH_EDUCATION_RESOURCES_ID = "1AMA3NQ1Wa9T8wrPLksByRe-LNQehE9QB"
DRIVE_STRENGTH_POWER_RESEARCH_ID  = "1OyDt367XpAvkq8lFJdCM_shinCnqTneZ"

PROGRESS_FILE = "progress_deporte.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SportsScienceBot/1.0; research use)",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
}

# ── Autenticación Google Drive ─────────────────────────────────────────────────

def get_drive_service():
    with open("token.json") as f:
        d = json.load(f)
    creds = Credentials(
        token=d["token"], refresh_token=d["refresh_token"],
        token_uri=d["token_uri"], client_id=d["client_id"],
        client_secret=d["client_secret"], scopes=d["scopes"],
    )
    return build("drive", "v3", credentials=creds)


def folder_for_url(url):
    # A. Antidopaje e IOC
    if "olympics.com"           in url or "olympic.org" in url: return DRIVE_IOC_OLYMPICS_ID
    if "wada-ama.org"           in url:  return DRIVE_WADA_ANTIDOPING_ID
    if "usada.org"              in url:  return DRIVE_USADA_ID
    if "ukad.org.uk"            in url:  return DRIVE_UKAD_ID
    if "globaldro.com"          in url:  return DRIVE_GLOBAL_DRO_ID
    # B. Federaciones
    if "worldathletics.org"     in url:  return DRIVE_WORLD_ATHLETICS_ID
    if "fifa.com"               in url:  return DRIVE_FIFA_FOOTBALL_ID
    if "fiba.basketball"        in url:  return DRIVE_FIBA_BASKETBALL_ID
    if "fivb.com"               in url:  return DRIVE_FIVB_VOLLEYBALL_ID
    if "worldaquatics.com"      in url:  return DRIVE_WORLD_AQUATICS_ID
    if "uci.org"                in url:  return DRIVE_UCI_CYCLING_ID
    if "itftennis.com"          in url:  return DRIVE_ITF_TENNIS_ID
    if "world.rugby"            in url:  return DRIVE_WORLD_RUGBY_ID
    if "ihf.info"               in url:  return DRIVE_IHF_HANDBALL_ID
    if "bwfbadminton.com"       in url:  return DRIVE_BWF_BADMINTON_ID
    if "worldtaekwondo.org"     in url:  return DRIVE_WORLD_TAEKWONDO_ID
    if "ijf.org"                in url:  return DRIVE_IJF_JUDO_ID
    if "isu.org"                in url:  return DRIVE_ISU_SKATING_ID
    if "fis-ski.com"            in url:  return DRIVE_FIS_SKIING_ID
    if "worldrowing.com"        in url:  return DRIVE_WORLD_ROWING_ID
    if "gymnastics.sport"       in url:  return DRIVE_WORLD_GYMNASTICS_ID
    if "iba-boxing.com"         in url or "worldboxing.sport" in url: return DRIVE_WORLD_BOXING_ID
    if "ufc.com"                in url or "mma"     in url:  return DRIVE_UFC_MMA_RESOURCES_ID
    # C. Ciencias del deporte
    if "acsm.org"               in url:  return DRIVE_ACSM_ID
    if "nsca.com"               in url:  return DRIVE_NSCA_ID
    if "ecss.de"                in url:  return DRIVE_ECSS_ID
    if "bases.org.uk"           in url:  return DRIVE_BASES_UK_ID
    if "strengthandconditioning.org" in url: return DRIVE_ASCA_AU_ID
    if "uksca.org.uk"           in url:  return DRIVE_UKSCA_ID
    if "conade.gob.mx"          in url:  return DRIVE_CONADE_MEXICO_ID
    if "clearinghouseforsport"  in url:  return DRIVE_SPORT_AUSTRALIA_CLEARINGHOUSE_ID
    if "uksport.gov.uk"         in url:  return DRIVE_UK_SPORT_ID
    if "usopc.org"              in url or "teamusa.org" in url: return DRIVE_USOPC_RESOURCES_ID
    # D. Medicina deportiva
    if "fims.org"               in url:  return DRIVE_FIMS_ID
    if "amssm.org"              in url:  return DRIVE_AMSSM_ID
    if "aossm.org"              in url:  return DRIVE_AOSSM_ID
    if "esska.org"              in url:  return DRIVE_ESSKA_ID
    if "bjsm.bmj.com"           in url:  return DRIVE_BJSM_ID
    if "sportshealth.org"       in url or "journals.sagepub.com/home/sph" in url: return DRIVE_SPORTS_HEALTH_JOURNAL_ID
    if "nata.org"               in url:  return DRIVE_NATA_ATHLETIC_TRAINING_ID
    # E. Nutrición deportiva
    if "jissn.biomedcentral.com" in url or "issn.org" in url: return DRIVE_ISSN_NUTRITION_ID
    if "ais.gov.au"             in url:  return DRIVE_AIS_NUTRITION_ID
    if "gssiweb.org"            in url:  return DRIVE_GSSI_GATORADE_ID
    if "scandpg.org"            in url:  return DRIVE_SCAN_DIETITIANS_ID
    if "ioc.nutrition"          in url or ("olympics.com" in url and "nutrition" in url): return DRIVE_IOC_NUTRITION_ID
    # F. Psicología
    if "appliedsportpsych.org"  in url:  return DRIVE_AASP_PSYCHOLOGY_ID
    if "issponline.org"         in url:  return DRIVE_ISSP_PSYCHOLOGY_ID
    if "fepsac.eu"              in url:  return DRIVE_FEPSAC_EUROPE_ID
    # G. Fuerza / biomecánica
    if "isbs.org"               in url:  return DRIVE_ISBS_BIOMECHANICS_ID
    if "vbt"                    in url or "velocity-based" in url: return DRIVE_VELOCITY_BASED_TRAINING_ID
    if "catapultsports.com"     in url:  return DRIVE_CATAPULT_RESOURCES_ID
    # H. Revistas OA
    if "jssm.org"               in url:  return DRIVE_JSSM_JOURNAL_ID
    if "mdpi.com/journal/sports" in url: return DRIVE_SPORTS_MDPI_ID
    if "frontiersin.org"        in url and "sports" in url: return DRIVE_FRONTIERS_SPORTS_ID
    if "bmcsportsscimedrehabil"  in url: return DRIVE_BMC_SPORTS_SCI_ID
    if "peerj.com"              in url and "sport" in url: return DRIVE_PEERJ_SPORTS_ID
    if "translational-sports-medicine" in url: return DRIVE_TRANSLATIONAL_SPORTS_MED_ID
    if "ijspp.humankinetics.com" in url: return DRIVE_INTL_J_SPORTS_PHYSIOL_ID
    if "tandfonline.com/journals/rjsp" in url: return DRIVE_JOURNAL_SPORT_SCIENCE_ID
    # I. Institutos de élite
    if "clearinghouseforsport.gov.au" in url or ("ais.gov.au" in url and "nutrition" not in url): return DRIVE_AIS_AUSTRALIA_ID
    if "inef.upm.es"            in url:  return DRIVE_INEF_SPAIN_ID
    if "aspire.qa"              in url:  return DRIVE_ASPIRE_QATAR_ID
    if "canadiansportinstitute" in url or "csiontario.ca" in url: return DRIVE_CANADIAN_SPORT_INSTITUTE_ID
    if "sportnz.org.nz"         in url:  return DRIVE_SPORT_NEW_ZEALAND_ID
    # J. Bases de datos
    if "sirc.ca"                in url:  return DRIVE_SIRC_CANADA_ID
    if "pubmed.ncbi.nlm.nih.gov" in url: return DRIVE_PUBMED_SPORTS_ID
    if "icce-office.org"        in url or "coachingassociation.ca" in url: return DRIVE_COACH_EDUCATION_RESOURCES_ID
    return DRIVE_STRENGTH_POWER_RESEARCH_ID  # fallback


def upload_file(service, url, name, content):
    folder_id = folder_for_url(url)
    media = MediaInMemoryUpload(content.encode("utf-8"), mimetype="text/plain")
    service.files().create(
        body={"name": name, "parents": [folder_id]},
        media_body=media, fields="id"
    ).execute()


# ── Helpers de URL discovery ───────────────────────────────────────────────────

def fetch_urls_from_sitemap(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code == 429 or not r.ok:
            return []
        root = ET.fromstring(r.text)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        return [el.text for el in root.findall(".//sm:loc", ns) if el.text]
    except ET.ParseError:
        return re.findall(r"<loc>\s*(https?://[^<\s]+)\s*</loc>", r.text)
    except Exception:
        return []


def _fetch_sitemap_index_urls(index_url, url_filter=None, delay=0.5):
    sub_sitemaps = fetch_urls_from_sitemap(index_url)
    all_urls = []
    for sm in sub_sitemaps:
        urls = fetch_urls_from_sitemap(sm)
        if url_filter:
            urls = [u for u in urls if url_filter(u)]
        all_urls.extend(urls)
        time.sleep(delay)
    return all_urls


def _crawl_one_level(seed, domain_prefix, delay=2.0):
    try:
        r = requests.get(seed, headers=HEADERS, timeout=30)
        if not r.ok:
            return []
        soup = BeautifulSoup(r.text, "html.parser")
        urls = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("/"):
                from urllib.parse import urljoin
                href = urljoin(seed, href)
            if domain_prefix in href and href.startswith("http"):
                urls.add(href)
        time.sleep(delay)
        return list(urls)
    except Exception:
        return []


# ── Fetchers por fuente ────────────────────────────────────────────────────────

# A. IOC y antidopaje
def fetch_ioc_urls():
    urls = _fetch_sitemap_index_urls("https://www.olympics.com/sitemap.xml",
        url_filter=lambda u: any(k in u for k in ["athlete", "sport", "news", "medical", "education"]),
        delay=1.5)
    return urls

def fetch_wada_urls():
    return _crawl_one_level("https://www.wada-ama.org/en/resources", "wada-ama.org", delay=3.0)

def fetch_usada_urls():
    return _crawl_one_level("https://www.usada.org/resources/", "usada.org", delay=3.0)

def fetch_ukad_urls():
    return _crawl_one_level("https://www.ukad.org.uk/resources", "ukad.org.uk", delay=3.0)

def fetch_global_dro_urls():
    return _crawl_one_level("https://www.globaldro.com/", "globaldro.com", delay=3.0)

# B. Federaciones
def fetch_world_athletics_urls():
    return _fetch_sitemap_index_urls("https://worldathletics.org/sitemap.xml",
        url_filter=lambda u: any(k in u for k in ["news", "athlete", "records", "disciplines", "about"]),
        delay=1.5)

def fetch_fifa_urls():
    return _crawl_one_level("https://www.fifa.com/football-development/", "fifa.com", delay=3.0)

def fetch_fiba_urls():
    return _crawl_one_level("https://www.fiba.basketball/pages/eng/fa/news/p/id/NWSVL.html", "fiba.basketball", delay=3.0)

def fetch_fivb_urls():
    return _crawl_one_level("https://www.fivb.com/en/volleyball/resources", "fivb.com", delay=3.0)

def fetch_world_aquatics_urls():
    return _crawl_one_level("https://www.worldaquatics.com/news", "worldaquatics.com", delay=3.0)

def fetch_uci_urls():
    return _crawl_one_level("https://www.uci.org/regulations", "uci.org", delay=3.0)

def fetch_itf_urls():
    return _crawl_one_level("https://www.itftennis.com/en/about-us/science-and-technical/", "itftennis.com", delay=3.0)

def fetch_world_rugby_urls():
    return _crawl_one_level("https://www.world.rugby/the-game/player-welfare/", "world.rugby", delay=3.0)

def fetch_ihf_urls():
    return _crawl_one_level("https://www.ihf.info/activities/coaches-education", "ihf.info", delay=3.0)

def fetch_bwf_urls():
    return _crawl_one_level("https://www.bwfbadminton.com/technical/", "bwfbadminton.com", delay=3.0)

def fetch_world_taekwondo_urls():
    return _crawl_one_level("https://www.worldtaekwondo.org/education/", "worldtaekwondo.org", delay=3.0)

def fetch_ijf_urls():
    return _crawl_one_level("https://www.ijf.org/education", "ijf.org", delay=3.0)

def fetch_isu_urls():
    return _crawl_one_level("https://www.isu.org/inside-isu/rules-regulations/isu-communications", "isu.org", delay=3.0)

def fetch_fis_urls():
    return _crawl_one_level("https://www.fis-ski.com/en/inside-fis/document-library/", "fis-ski.com", delay=3.0)

def fetch_world_rowing_urls():
    return _crawl_one_level("https://worldrowing.com/technical/", "worldrowing.com", delay=3.0)

def fetch_world_gymnastics_urls():
    return _crawl_one_level("https://www.gymnastics.sport/site/rules.php", "gymnastics.sport", delay=3.0)

def fetch_world_boxing_urls():
    return _crawl_one_level("https://www.iba-boxing.com/technical/", "iba-boxing.com", delay=3.0)

# C. Ciencias del deporte
def fetch_acsm_urls():
    return _fetch_sitemap_index_urls("https://www.acsm.org/sitemap.xml",
        url_filter=lambda u: any(k in u for k in ["articles", "news", "education", "research", "resource"]),
        delay=1.5)

def fetch_nsca_urls():
    return _crawl_one_level("https://www.nsca.com/education/resources/", "nsca.com", delay=3.0)

def fetch_ecss_urls():
    return _crawl_one_level("https://www.ecss.de/publications/", "ecss.de", delay=3.0)

def fetch_bases_uk_urls():
    return _crawl_one_level("https://www.bases.org.uk/page-sport-and-exercise-science-resources.html", "bases.org.uk", delay=3.0)

def fetch_asca_au_urls():
    return _crawl_one_level("https://www.strengthandconditioning.org/resources/", "strengthandconditioning.org", delay=3.0)

def fetch_uksca_urls():
    return _crawl_one_level("https://www.uksca.org.uk/resources", "uksca.org.uk", delay=3.0)

def fetch_conade_urls():
    return _crawl_one_level("https://www.gob.mx/conade/articulos", "conade.gob.mx", delay=3.0)

def fetch_sport_australia_clearinghouse_urls():
    return _fetch_sitemap_index_urls("https://www.clearinghouseforsport.gov.au/sitemap.xml", delay=1.5)

def fetch_uk_sport_urls():
    return _crawl_one_level("https://www.uksport.gov.uk/resources", "uksport.gov.uk", delay=2.0)

def fetch_usopc_urls():
    return _crawl_one_level("https://www.usopc.org/resources", "usopc.org", delay=3.0)

# D. Medicina deportiva
def fetch_fims_urls():
    return _crawl_one_level("https://www.fims.org/resources/", "fims.org", delay=3.0)

def fetch_amssm_urls():
    return _crawl_one_level("https://www.amssm.org/Content.aspx?ID=197", "amssm.org", delay=3.0)

def fetch_aossm_urls():
    return _crawl_one_level("https://www.aossm.org/education/", "aossm.org", delay=3.0)

def fetch_esska_urls():
    return _crawl_one_level("https://www.esska.org/library/", "esska.org", delay=3.0)

def fetch_bjsm_urls():
    return _fetch_sitemap_index_urls("https://bjsm.bmj.com/sitemap.xml",
        url_filter=lambda u: "content" in u,
        delay=1.0)

def fetch_sports_health_urls():
    return _crawl_one_level("https://journals.sagepub.com/toc/spha/current", "sagepub.com", delay=2.0)

def fetch_nata_urls():
    return _crawl_one_level("https://www.nata.org/practice-patient-care/health-information/", "nata.org", delay=3.0)

# E. Nutrición deportiva
def fetch_issn_nutrition_urls():
    return _fetch_sitemap_index_urls("https://jissn.biomedcentral.com/sitemap.xml",
        url_filter=lambda u: "article" in u,
        delay=1.0)

def fetch_ais_nutrition_urls():
    return _crawl_one_level("https://www.ais.gov.au/nutrition/", "ais.gov.au", delay=2.0)

def fetch_gssi_urls():
    return _crawl_one_level("https://www.gssiweb.org/sports-science-institute/topics", "gssiweb.org", delay=2.0)

def fetch_scan_urls():
    return _crawl_one_level("https://www.scandpg.org/sports-nutrition/", "scandpg.org", delay=3.0)

def fetch_ioc_nutrition_urls():
    return _crawl_one_level("https://www.olympics.com/ioc/nutrition", "olympics.com", delay=3.0)

# F. Psicología del deporte
def fetch_aasp_urls():
    return _crawl_one_level("https://www.appliedsportpsych.org/resources/", "appliedsportpsych.org", delay=3.0)

def fetch_issp_urls():
    return _crawl_one_level("https://issponline.org/resources/", "issponline.org", delay=3.0)

def fetch_fepsac_urls():
    return _crawl_one_level("https://www.fepsac.eu/resources/", "fepsac.eu", delay=3.0)

# G. Fuerza, acondicionamiento y biomecánica
def fetch_isbs_urls():
    return _crawl_one_level("https://ojs.ub.uni-konstanz.de/cpa/issue/archive", "isbs.org", delay=2.0)

def fetch_catapult_urls():
    return _crawl_one_level("https://www.catapultsports.com/resources", "catapultsports.com", delay=3.0)

# H. Revistas OA
def fetch_jssm_urls():
    return _fetch_sitemap_index_urls("https://www.jssm.org/sitemap.xml", delay=1.0)

def fetch_sports_mdpi_urls():
    return _fetch_sitemap_index_urls("https://www.mdpi.com/sitemap/sitemap-sports.xml",
        url_filter=lambda u: "/sports/" in u and "/article" in u,
        delay=1.0)

def fetch_frontiers_sports_urls():
    return _fetch_sitemap_index_urls(
        "https://www.frontiersin.org/sitemap.xml",
        url_filter=lambda u: "sports" in u and "article" in u,
        delay=1.0,
    )

def fetch_bmc_sports_sci_urls():
    return _fetch_sitemap_index_urls(
        "https://bmcsportsscimedrehabil.biomedcentral.com/sitemap.xml",
        url_filter=lambda u: "article" in u,
        delay=1.0,
    )

def fetch_peerj_sports_urls():
    return _fetch_sitemap_index_urls(
        "https://peerj.com/sitemap.xml",
        url_filter=lambda u: "sport" in u.lower() and "article" in u,
        delay=1.0,
    )

def fetch_translational_sports_med_urls():
    return _crawl_one_level("https://onlinelibrary.wiley.com/journal/25738488", "translational-sports", delay=2.0)

# I. Institutos de élite
def fetch_ais_australia_urls():
    return _crawl_one_level("https://www.ais.gov.au/resources/", "ais.gov.au", delay=2.0)

def fetch_inef_spain_urls():
    return _crawl_one_level("https://www.inef.upm.es/publicaciones/", "inef.upm.es", delay=3.0)

def fetch_aspire_qatar_urls():
    return _crawl_one_level("https://www.aspire.qa/research/", "aspire.qa", delay=3.0)

def fetch_canadian_sport_institute_urls():
    return _crawl_one_level("https://www.canadiansportinstitute.ca/resources/", "canadiansportinstitute", delay=3.0)

def fetch_sport_nz_urls():
    return _crawl_one_level("https://www.sportnz.org.nz/resources/", "sportnz.org.nz", delay=2.0)

# J. Bases de datos y recursos educativos
def fetch_sirc_urls():
    return _crawl_one_level("https://sirc.ca/resources/", "sirc.ca", delay=3.0)

def fetch_pubmed_sports_urls():
    """PubMed E-utilities — artículos de sports medicine (MeSH)."""
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "term": '"sports medicine"[MeSH] OR "athletic performance"[MeSH] OR "exercise"[MeSH Major Topic] OR "strength training"[MeSH]',
        "retmax": 2000,
        "retmode": "json",
        "usehistory": "y",
    }
    try:
        r = requests.get(base, params=params, headers=HEADERS, timeout=30)
        data = r.json()
        webenv = data["esearchresult"]["webenv"]
        ids = data["esearchresult"]["idlist"]
        return [f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" for pmid in ids]
    except Exception:
        return []

def fetch_coach_education_urls():
    urls = _crawl_one_level("https://www.icce-office.org/resources/", "icce-office.org", delay=3.0)
    urls += _crawl_one_level("https://www.coachingassociation.ca/", "coachingassociation.ca", delay=3.0)
    return urls


# ── Carga de todas las URLs ────────────────────────────────────────────────────

def _load_source(name, sitemaps=None, fn=None):
    print(f"Cargando {name}...", flush=True)
    urls = []
    if sitemaps:
        for sm in sitemaps:
            try:
                found = fetch_urls_from_sitemap(sm)
                print(f"  {sm.split('/')[-1]}: {len(found)} URLs", flush=True)
                urls.extend(found)
            except Exception as e:
                print(f"  ERROR {sm.split('/')[-1]}: {e}", flush=True)
    if fn:
        try:
            found = fn()
            print(f"  → {len(found)} URLs", flush=True)
            urls.extend(found)
        except Exception as e:
            print(f"  ERROR: {e}", flush=True)
    return urls


def get_all_urls():
    all_urls = []

    # A. Antidopaje e IOC
    all_urls += _load_source("IOC Olympics",            fn=fetch_ioc_urls)
    all_urls += _load_source("WADA Antidoping",         fn=fetch_wada_urls)
    all_urls += _load_source("USADA",                   fn=fetch_usada_urls)
    all_urls += _load_source("UKAD",                    fn=fetch_ukad_urls)
    all_urls += _load_source("Global DRO",              fn=fetch_global_dro_urls)

    # B. Federaciones internacionales
    all_urls += _load_source("World Athletics",         fn=fetch_world_athletics_urls)
    all_urls += _load_source("FIFA Football",           fn=fetch_fifa_urls)
    all_urls += _load_source("FIBA Basketball",         fn=fetch_fiba_urls)
    all_urls += _load_source("FIVB Volleyball",         fn=fetch_fivb_urls)
    all_urls += _load_source("World Aquatics",          fn=fetch_world_aquatics_urls)
    all_urls += _load_source("UCI Cycling",             fn=fetch_uci_urls)
    all_urls += _load_source("ITF Tennis",              fn=fetch_itf_urls)
    all_urls += _load_source("World Rugby",             fn=fetch_world_rugby_urls)
    all_urls += _load_source("IHF Handball",            fn=fetch_ihf_urls)
    all_urls += _load_source("BWF Badminton",           fn=fetch_bwf_urls)
    all_urls += _load_source("World Taekwondo",         fn=fetch_world_taekwondo_urls)
    all_urls += _load_source("IJF Judo",                fn=fetch_ijf_urls)
    all_urls += _load_source("ISU Skating",             fn=fetch_isu_urls)
    all_urls += _load_source("FIS Skiing",              fn=fetch_fis_urls)
    all_urls += _load_source("World Rowing",            fn=fetch_world_rowing_urls)
    all_urls += _load_source("World Gymnastics",        fn=fetch_world_gymnastics_urls)
    all_urls += _load_source("World Boxing",            fn=fetch_world_boxing_urls)

    # C. Ciencias del deporte
    all_urls += _load_source("ACSM",                    fn=fetch_acsm_urls)
    all_urls += _load_source("NSCA",                    fn=fetch_nsca_urls)
    all_urls += _load_source("ECSS",                    fn=fetch_ecss_urls)
    all_urls += _load_source("BASES UK",                fn=fetch_bases_uk_urls)
    all_urls += _load_source("ASCA Australia",          fn=fetch_asca_au_urls)
    all_urls += _load_source("UKSCA",                   fn=fetch_uksca_urls)
    all_urls += _load_source("CONADE Mexico",           fn=fetch_conade_urls)
    all_urls += _load_source("Sport Australia Clearinghouse", fn=fetch_sport_australia_clearinghouse_urls)
    all_urls += _load_source("UK Sport",                fn=fetch_uk_sport_urls)
    all_urls += _load_source("USOPC Resources",         fn=fetch_usopc_urls)

    # D. Medicina deportiva
    all_urls += _load_source("FIMS",                    fn=fetch_fims_urls)
    all_urls += _load_source("AMSSM",                   fn=fetch_amssm_urls)
    all_urls += _load_source("AOSSM",                   fn=fetch_aossm_urls)
    all_urls += _load_source("ESSKA",                   fn=fetch_esska_urls)
    all_urls += _load_source("BJSM",                    fn=fetch_bjsm_urls)
    all_urls += _load_source("Sports Health Journal",   fn=fetch_sports_health_urls)
    all_urls += _load_source("NATA Athletic Training",  fn=fetch_nata_urls)

    # E. Nutrición deportiva
    all_urls += _load_source("ISSN Nutrition",          fn=fetch_issn_nutrition_urls)
    all_urls += _load_source("AIS Nutrition",           fn=fetch_ais_nutrition_urls)
    all_urls += _load_source("GSSI / Gatorade",         fn=fetch_gssi_urls)
    all_urls += _load_source("SCAN Dietitians",         fn=fetch_scan_urls)
    all_urls += _load_source("IOC Nutrition",           fn=fetch_ioc_nutrition_urls)

    # F. Psicología del deporte
    all_urls += _load_source("AASP Psychology",         fn=fetch_aasp_urls)
    all_urls += _load_source("ISSP Psychology",         fn=fetch_issp_urls)
    all_urls += _load_source("FEPSAC Europe",           fn=fetch_fepsac_urls)

    # G. Fuerza y biomecánica
    all_urls += _load_source("ISBS Biomechanics",       fn=fetch_isbs_urls)
    all_urls += _load_source("Catapult Resources",      fn=fetch_catapult_urls)

    # H. Revistas OA
    all_urls += _load_source("JSSM",                    fn=fetch_jssm_urls)
    all_urls += _load_source("Sports MDPI",             fn=fetch_sports_mdpi_urls)
    all_urls += _load_source("Frontiers Sports",        fn=fetch_frontiers_sports_urls)
    all_urls += _load_source("BMC Sports Sci",          fn=fetch_bmc_sports_sci_urls)
    all_urls += _load_source("PeerJ Sports",            fn=fetch_peerj_sports_urls)
    all_urls += _load_source("Translational Sports Med",fn=fetch_translational_sports_med_urls)

    # I. Institutos de élite
    all_urls += _load_source("AIS Australia",           fn=fetch_ais_australia_urls)
    all_urls += _load_source("INEF Spain",              fn=fetch_inef_spain_urls)
    all_urls += _load_source("Aspire Qatar",            fn=fetch_aspire_qatar_urls)
    all_urls += _load_source("Canadian Sport Institute",fn=fetch_canadian_sport_institute_urls)
    all_urls += _load_source("Sport New Zealand",       fn=fetch_sport_nz_urls)

    # J. Bases de datos y recursos educativos
    all_urls += _load_source("SIRC Canada",             fn=fetch_sirc_urls)
    all_urls += _load_source("PubMed Sports Medicine",  fn=fetch_pubmed_sports_urls)
    all_urls += _load_source("Coach Education (ICCE)",  fn=fetch_coach_education_urls)

    print(f"\nTotal URLs objetivo: {len(all_urls)}", flush=True)
    return all_urls


# ── Scraping ───────────────────────────────────────────────────────────────────

def delay_for_url(url):
    if any(d in url for d in ["wada-ama.org", "usada.org", "fifa.com", "uci.org",
                               "worldathletics.org", "world.rugby"]):
        return 4.0
    if any(d in url for d in ["bjsm.bmj.com", "acsm.org", "nsca.com"]):
        return 2.0
    return 1.5


def scrape_page(url):
    resp = requests.get(url, headers=HEADERS, timeout=25)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    h1 = soup.find("h1") or soup.find("h2")
    title = h1.get_text(strip=True) if h1 else url.split("/")[-1].replace("-", " ").title()

    meta = soup.find("meta", {"name": "description"})
    summary = meta["content"] if meta else ""

    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "button", "iframe"]):
        tag.decompose()

    paragraphs = [
        p.get_text(separator=" ", strip=True)
        for p in soup.find_all(["p", "li", "td", "dd"])
        if len(p.get_text(strip=True)) > 50
    ]
    body = "\n\n".join(paragraphs)

    if len(body) < 300:
        for div in soup.find_all("div", class_=re.compile(r"content|article|body|main", re.I)):
            div_text = div.get_text(separator="\n", strip=True)
            if len(div_text) > 300:
                body = div_text
                break

    return {"title": title, "full_text": f"{title}\n{'='*len(title)}\n\nURL: {url}\n\n{summary}\n\n{body}".strip()}


def url_to_filename(url):
    if "olympics.com"           in url:  prefix = "ioc"
    elif "wada-ama.org"         in url:  prefix = "wada"
    elif "usada.org"            in url:  prefix = "usada"
    elif "ukad.org.uk"          in url:  prefix = "ukad"
    elif "globaldro.com"        in url:  prefix = "globaldro"
    elif "worldathletics.org"   in url:  prefix = "worldathletics"
    elif "fifa.com"             in url:  prefix = "fifa"
    elif "fiba.basketball"      in url:  prefix = "fiba"
    elif "fivb.com"             in url:  prefix = "fivb"
    elif "worldaquatics.com"    in url:  prefix = "worldaquatics"
    elif "uci.org"              in url:  prefix = "uci"
    elif "itftennis.com"        in url:  prefix = "itf"
    elif "world.rugby"          in url:  prefix = "worldrugby"
    elif "ihf.info"             in url:  prefix = "ihf"
    elif "bwfbadminton.com"     in url:  prefix = "bwf"
    elif "worldtaekwondo.org"   in url:  prefix = "taekwondo"
    elif "ijf.org"              in url:  prefix = "ijf"
    elif "isu.org"              in url:  prefix = "isu"
    elif "fis-ski.com"          in url:  prefix = "fis"
    elif "worldrowing.com"      in url:  prefix = "worldrowing"
    elif "gymnastics.sport"     in url:  prefix = "gymnastics"
    elif "iba-boxing.com"       in url:  prefix = "boxing"
    elif "acsm.org"             in url:  prefix = "acsm"
    elif "nsca.com"             in url:  prefix = "nsca"
    elif "ecss.de"              in url:  prefix = "ecss"
    elif "bases.org.uk"         in url:  prefix = "bases"
    elif "strengthandconditioning.org" in url: prefix = "asca"
    elif "uksca.org.uk"         in url:  prefix = "uksca"
    elif "conade.gob.mx"        in url:  prefix = "conade"
    elif "clearinghouseforsport" in url: prefix = "clearinghouse_sport"
    elif "uksport.gov.uk"       in url:  prefix = "uksport"
    elif "usopc.org"            in url:  prefix = "usopc"
    elif "fims.org"             in url:  prefix = "fims"
    elif "amssm.org"            in url:  prefix = "amssm"
    elif "aossm.org"            in url:  prefix = "aossm"
    elif "esska.org"            in url:  prefix = "esska"
    elif "bjsm.bmj.com"         in url:  prefix = "bjsm"
    elif "sportshealth.org"     in url:  prefix = "sportshealth"
    elif "nata.org"             in url:  prefix = "nata"
    elif "jissn.biomedcentral"  in url:  prefix = "issn"
    elif "ais.gov.au"           in url and "nutrition" in url: prefix = "ais_nutrition"
    elif "gssiweb.org"          in url:  prefix = "gssi"
    elif "scandpg.org"          in url:  prefix = "scan"
    elif "appliedsportpsych.org" in url: prefix = "aasp"
    elif "issponline.org"       in url:  prefix = "issp"
    elif "fepsac.eu"            in url:  prefix = "fepsac"
    elif "isbs.org"             in url:  prefix = "isbs"
    elif "catapultsports.com"   in url:  prefix = "catapult"
    elif "jssm.org"             in url:  prefix = "jssm"
    elif "mdpi.com"             in url:  prefix = "sports_mdpi"
    elif "frontiersin.org"      in url:  prefix = "frontiers_sports"
    elif "bmcsportssci"         in url:  prefix = "bmc_sports"
    elif "peerj.com"            in url:  prefix = "peerj_sports"
    elif "ais.gov.au"           in url:  prefix = "ais_au"
    elif "inef.upm.es"          in url:  prefix = "inef"
    elif "aspire.qa"            in url:  prefix = "aspire"
    elif "canadiansportinstitute" in url: prefix = "csi"
    elif "sportnz.org.nz"       in url:  prefix = "sportnz"
    elif "sirc.ca"              in url:  prefix = "sirc"
    elif "pubmed.ncbi"          in url:  prefix = "pubmed_sport"
    elif "icce-office.org"      in url:  prefix = "icce"
    else:                                prefix = "deporte"
    path = re.sub(r"[?=&]", "_", url.split("//", 1)[-1]).replace("/", "__").strip("__")
    return f"{prefix}__{path[:180]}.txt"


# ── Progreso ───────────────────────────────────────────────────────────────────

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"done": [], "failed": []}


def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Conectando a Google Drive...", flush=True)
    service = get_drive_service()
    print("Conexión exitosa.\n", flush=True)

    all_urls = get_all_urls()
    progress = load_progress()
    done_set = set(progress["done"])
    remaining = [u for u in all_urls if u not in done_set]

    total = len(all_urls)
    print(f"\nTotal: {total} | Ya hechos: {len(done_set)} | Pendientes: {len(remaining)}\n", flush=True)

    start_time = time.time()
    batch_errors = 0

    for i, url in enumerate(remaining, 1):
        try:
            data = scrape_page(url)
            filename = url_to_filename(url)
            upload_file(service, url, filename, data["full_text"])
            progress["done"].append(url)
            batch_errors = 0
        except Exception as e:
            err = str(e)
            progress["failed"].append({"url": url, "error": err})
            batch_errors += 1
            slug = url.rstrip("/").split("/")[-1][:60]
            print(f"  ERROR ({batch_errors}): {slug} — {err[:80]}", flush=True)
            if batch_errors >= 10:
                print("  10 errores seguidos, esperando 60s...", flush=True)
                time.sleep(60)
                batch_errors = 0

        if i % 50 == 0:
            save_progress(progress)
            elapsed = time.time() - start_time
            rate = i / elapsed if elapsed > 0 else 0
            eta = (len(remaining) - i) / rate / 60 if rate > 0 else 0
            print(f"[{i}/{len(remaining)}] {rate:.1f} pág/s — ETA {eta:.0f} min", flush=True)

        time.sleep(delay_for_url(url))

    save_progress(progress)
    print(f"\nFinalizado. {len(progress['done'])} páginas subidas.", flush=True)
