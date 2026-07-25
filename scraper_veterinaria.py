"""
Scraper veterinario completo — 25 fuentes
Excluidos (paywall/WAF): VIN, AVMA, BSAVA, ECVIM, IVIS, Vetlexicon,
  CAB, Wiley, Elsevier, MDPI, BMC/Springer, RVC, Melbourne, Colorado State, USDA, CDC.
Resumible: guarda progreso en progress_vet.json
Uso: python3 scrape_vet.py
"""
import os, json, time, random, re, requests
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from google.oauth2.credentials import Credentials

# ── Drive IDs ──────────────────────────────────────────────────────────────────

DRIVE_VET_ROOT_ID   = "1sypIsu5f1rtKyuLYKgIN9yuSxYIONi7p"   # Proyecto_IA_Veterinaria
DRIVE_MERCK_ID      = "107q-Vp6aWHR7bUYi7FxEedz1ywULSzNV"   # merck_manual
DRIVE_AAHA_ID       = "1N0_pVjDE67q3Gcc743aMb1PBQbrs523f"    # aaha
DRIVE_ACVS_ID       = "1SjE0iSJJBrbFbdmZsFdRMqh27pL7BZO9"   # acvs
DRIVE_MSD_ID        = "1p6840PyVvvuSbz05v5V5ZCNhSHpUUy-E"   # msd_manual
DRIVE_WOAH_ID       = "1lehKe-HXiSTn1SaP1f4Iefs656_y70LW"   # woah
DRIVE_WSAVA_ID      = "12KhYXEdNAbej2bErtVIwFx6b7A9IT2en"   # wsava
DRIVE_ACVIM_ID      = "1GCrjYJFJWoLnA_eM1oDiakJMrONuSO6-"   # acvim
DRIVE_AAVMC_ID      = "1urggNC3UPd5mfK4B8pF3LNZbWEyS9q-i"   # aavmc
DRIVE_NOAH_ID       = "1ayGiovBa8v986wcR_z5z2Za0Vv59Nekc"    # noah_compendium
DRIVE_EMA_ID        = "1QF9-QzuHaRScm_pghdCz5rDchr0ASuhj"   # ema_veterinary
DRIVE_FDA_ID        = "1uliwOpKtvjV44iPHd3dsjOvSPXVW_8ys"    # fda_cvm
DRIVE_ASPCA_ID      = "13QEwv1X496Qp73FT6S7IXCYitfiGZDvs"   # aspca_toxicology
DRIVE_PPH_ID        = "1IWMPqwucjt9TCsMCAVXiD1XPTZZh3Hkm"   # pet_poison_helpline
DRIVE_FRONTIERS_ID  = "1BV1jUxsrwETuMZWj1x-UHc-AEKFBrwCy"   # frontiers_veterinary
DRIVE_PLOS_ID       = "14r1wc4gXMOzo7kbtE5cimjEPVFya3Z_R"    # plos_veterinary
DRIVE_CB_ID         = "1IDQuSWGnG2cX0lMGk7BBwi3WeW-uSH7E"   # clinicians_brief
DRIVE_TVP_ID        = "1fNU5Jjaz4d26dsEdQxjJE-OTrE714eVW"   # todays_vet_practice
DRIVE_EFSA_ID2      = "181t6H-_m4Elj9_boIQYHTOS_Eajur1to"   # efsa
DRIVE_FAO_ID        = "1Ls66EIg1rY-0IkLebsXDrjdZRYo1eBp-"   # fao_animal_health
DRIVE_CORNELL_ID    = "10kssTKPoLHItZfK1YXYWStmqlnHWZaSa"   # cornell_vet
DRIVE_UCDAVIS_ID    = "1cHlmGAVCnVxbn2UWZ4Bu1TvximsaaWmR"   # uc_davis_vet
DRIVE_PURDUE_ID     = "1Qq5br-xoR-VVe8KdfLwK23yS8tCyYZQK"   # purdue_vet
DRIVE_TAMU_ID       = "1PZHrQcf8DQGg59pUPWqYJ1bVndg-wgO5"   # texas_am_vet
DRIVE_OSU_ID        = "17T52a-QfK8P-So9UKppeF78hmre6Bc6q"   # ohio_state_vet
DRIVE_SYDNEY_ID     = "1-Rl1UMq8px1u3Jw8FugDrohZnNJDLS3X"   # sydney_vet

PROGRESS_FILE = "progress_vet.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

# ── Sitemaps y endpoints por fuente ───────────────────────────────────────────

MERCK_SITEMAPS = [
    "https://www.merckvetmanual.com/sitemaps/veterinary-topic.xml.gz",
    "https://www.merckvetmanual.com/sitemaps/veterinary-casestudy.xml",
    "https://www.merckvetmanual.com/sitemaps/veterinary-news.xml",
]
AAHA_SITEMAPS = [
    "https://www.aaha.org/resource-sitemap.xml",
    "https://www.aaha.org/resource-sitemap2.xml",
    "https://www.aaha.org/publication-sitemap.xml",
    "https://www.aaha.org/publication-sitemap2.xml",
]
ACVS_SITEMAPS = [
    "https://www.acvs.org/small-animal-sitemap.xml",
    "https://www.acvs.org/large-animal-sitemap.xml",
    "https://www.acvs.org/resources-sitemap.xml",
    "https://www.acvs.org/post-sitemap.xml",
]
MSD_SITEMAPS = [
    "https://www.msdvetmanual.com/sitemaps/veterinary-topic.xml.gz",
]
ACVIM_SITEMAPS = [
    "https://acvim.org/sitemap.xml",
]
CB_SITEMAP_INDEX  = "https://www.cliniciansbrief.com/sitemap.xml"
TVP_SITEMAP_INDEX = "https://todaysveterinarypractice.com/sitemap.xml"
FAO_SITEMAP_INDEX = "https://www.fao.org/sitemap.xml"
CORNELL_SITEMAP_INDEX  = "https://www.vet.cornell.edu/sitemap.xml"
PURDUE_SITEMAP_INDEX   = "https://vet.purdue.edu/sitemap.xml"
TAMU_SITEMAP_INDEX     = "https://vetmed.tamu.edu/sitemap.xml"
OSU_SITEMAP            = "https://vet.osu.edu/sitemap.xml"
SYDNEY_SITEMAP_INDEX   = "https://www.sydney.edu.au/sitemap.xml"
EFSA_SEED    = "https://www.efsa.europa.eu/en/topics/topic/animal-health"
UCDAVIS_SEED = "https://www.vetmed.ucdavis.edu"

WOAH_SITEMAP_INDEX      = "https://www.woah.org/sitemap_index.xml"
AAVMC_SITEMAP_INDEX     = "https://aavmc.org/sitemap_index.xml"
EMA_SITEMAP_INDEX       = "https://www.ema.europa.eu/sitemap.xml"
PPH_SITEMAP_INDEX       = "https://www.petpoisonhelpline.com/sitemap_index.xml"
FRONTIERS_SITEMAP_INDEX = "https://www.frontiersin.org/articles/sitemap-index.xml"
WSAVA_GUIDELINES_INDEX  = "https://wsava.org/global-guidelines/"
ASPCA_SITEMAP           = "https://www.aspca.org/sitemap.xml"
NOAH_SITEMAP            = "https://www.noahcompendium.co.uk/Sitemaps/1.xml"
FDA_CVM_SEED            = "https://www.fda.gov/animal-veterinary"
PLOS_API_URL            = "https://api.plos.org/search"

# ── Drive ──────────────────────────────────────────────────────────────────────

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
    if "merckvetmanual.com" in url:  return DRIVE_MERCK_ID
    if "msdvetmanual.com"   in url:  return DRIVE_MSD_ID
    if "woah.org"           in url:  return DRIVE_WOAH_ID
    if "wsava.org"          in url:  return DRIVE_WSAVA_ID
    if "acvs.org"           in url:  return DRIVE_ACVS_ID
    if "acvim.org"          in url:  return DRIVE_ACVIM_ID
    if "aavmc.org"          in url:  return DRIVE_AAVMC_ID
    if "noahcompendium"     in url:  return DRIVE_NOAH_ID
    if "ema.europa.eu"      in url:  return DRIVE_EMA_ID
    if "fda.gov"            in url:  return DRIVE_FDA_ID
    if "aspca.org"          in url:  return DRIVE_ASPCA_ID
    if "petpoisonhelpline"  in url:  return DRIVE_PPH_ID
    if "frontiersin.org"    in url:  return DRIVE_FRONTIERS_ID
    if "plos.org"           in url:  return DRIVE_PLOS_ID
    if "cliniciansbrief"    in url:  return DRIVE_CB_ID
    if "todaysveterinary"   in url:  return DRIVE_TVP_ID
    if "efsa.europa.eu"     in url:  return DRIVE_EFSA_ID2
    if "fao.org"            in url:  return DRIVE_FAO_ID
    if "vet.cornell.edu"    in url:  return DRIVE_CORNELL_ID
    if "vetmed.ucdavis"     in url:  return DRIVE_UCDAVIS_ID
    if "vet.purdue.edu"     in url:  return DRIVE_PURDUE_ID
    if "vetmed.tamu.edu"    in url:  return DRIVE_TAMU_ID
    if "vet.osu.edu"        in url:  return DRIVE_OSU_ID
    if "sydney.edu.au"      in url:  return DRIVE_SYDNEY_ID
    if "aaha.org"           in url:  return DRIVE_AAHA_ID
    return DRIVE_AAHA_ID  # fallback


def upload_file(service, url, name, content):
    folder_id = folder_for_url(url)
    media = MediaInMemoryUpload(content.encode("utf-8"), mimetype="text/plain")
    service.files().create(
        body={"name": name, "parents": [folder_id]},
        media_body=media, fields="id"
    ).execute()


# ── Helpers de sitemap ─────────────────────────────────────────────────────────

def fetch_urls_from_sitemap(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    if r.status_code == 429:
        # Rate-limited: skip silently (no reintentar, el siguiente delay ayudará)
        return []
    if not r.ok:
        return []
    try:
        root = ET.fromstring(r.text)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        return [el.text for el in root.findall(".//sm:loc", ns)]
    except ET.ParseError:
        # Fallback regex para XML con caracteres especiales no escapados
        return re.findall(r"<loc>\s*(https?://[^<\s]+)\s*</loc>", r.text)


def _fetch_sitemap_index_urls(index_url, url_filter=None, delay=0.5):
    """Descarga un sitemap-index, luego cada sub-sitemap; filtra con url_filter."""
    sub_sitemaps = fetch_urls_from_sitemap(index_url)
    all_urls = []
    for sm in sub_sitemaps:
        urls = fetch_urls_from_sitemap(sm)
        if url_filter:
            urls = [u for u in urls if url_filter(u)]
        all_urls.extend(urls)
        time.sleep(delay)
    return all_urls


# ── Descubridores por fuente ───────────────────────────────────────────────────

def fetch_woah_urls():
    r = requests.get(WOAH_SITEMAP_INDEX, headers=HEADERS, timeout=30)
    root = ET.fromstring(r.text)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sub_sitemaps = [el.text for el in root.findall(".//sm:loc", ns)]
    print(f"  WOAH: {len(sub_sitemaps)} sub-sitemaps", flush=True)
    en_urls = []
    for sm in sub_sitemaps:
        try:
            urls = fetch_urls_from_sitemap(sm)
            en_urls.extend(u for u in urls if "/en/" in u or u.rstrip("/").endswith("/en"))
        except Exception as e:
            print(f"    WOAH error {sm.split('/')[-1]}: {e}", flush=True)
        time.sleep(0.5)
    return en_urls


def fetch_wsava_guideline_urls():
    r = requests.get(WSAVA_GUIDELINES_INDEX, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "wsava.org" in href and href != WSAVA_GUIDELINES_INDEX:
            if not any(s in href for s in ["#", "mailto:", "javascript:"]):
                links.add(href.rstrip("/"))
        elif href.startswith("/") and len(href) > 1:
            links.add("https://wsava.org" + href.rstrip("/"))
    return [
        u for u in links
        if "wsava.org" in u
        and not u.endswith("wsava.org")
        and "/global-guidelines" not in u.rstrip("/")
    ]


def fetch_aavmc_urls():
    return _fetch_sitemap_index_urls(AAVMC_SITEMAP_INDEX)


def fetch_ema_vet_urls():
    """Filtra el enorme sitemap de EMA a solo páginas de medicamentos veterinarios."""
    return _fetch_sitemap_index_urls(
        EMA_SITEMAP_INDEX,
        url_filter=lambda u: "/veterinary-medicines" in u,
        delay=2.0,  # EMA tiene rate-limit agresivo — 2s entre sub-sitemaps
    )


def fetch_fda_cvm_urls():
    """Crawl de 1 nivel desde la página principal de FDA CVM."""
    seed = FDA_CVM_SEED
    prefix_abs = "https://www.fda.gov/animal-veterinary"
    prefix_rel = "/animal-veterinary"
    visited = set()
    try:
        r = requests.get(seed, headers=HEADERS, timeout=20)
        visited.add(seed)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"].split("#")[0].split("?")[0]
            if href.startswith(prefix_rel):
                visited.add("https://www.fda.gov" + href)
            elif href.startswith(prefix_abs):
                visited.add(href)
    except Exception as e:
        print(f"  FDA CVM error: {e}", flush=True)
    return list(visited)


def fetch_aspca_tox_urls():
    """Solo páginas del sitio ASPCA relacionadas con toxicología."""
    try:
        urls = fetch_urls_from_sitemap(ASPCA_SITEMAP)
    except Exception as e:
        print(f"  ASPCA sitemap error: {e}", flush=True)
        return []
    return [
        u for u in urls
        if "poison" in u or "toxic" in u or "animal-poison-control" in u
    ]


def fetch_pph_urls():
    """Pet Poison Helpline — incluye las sub-sitemaps de base de datos de toxinas."""
    return _fetch_sitemap_index_urls(PPH_SITEMAP_INDEX)


def fetch_frontiers_vet_urls():
    """Artículos de Frontiers in Veterinary Science filtrados por URL."""
    return _fetch_sitemap_index_urls(
        FRONTIERS_SITEMAP_INDEX,
        url_filter=lambda u: "veterinary-science" in u or "fvets" in u,
        delay=0.3,
    )


def _crawl_one_level(seed, domain_prefix, delay=2.0):
    """Crawl de 1 nivel: recoge todos los links del seed dentro del mismo dominio."""
    visited = set()
    try:
        r = requests.get(seed, headers=HEADERS, timeout=20)
        visited.add(seed)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"].split("#")[0].split("?")[0]
            if href.startswith(domain_prefix):
                visited.add(href if href.startswith("http") else "https://" + href.lstrip("/"))
            elif href.startswith("/") and domain_prefix in seed:
                base = seed.split("/")[0] + "//" + seed.split("/")[2]
                visited.add(base + href)
    except Exception as e:
        print(f"  crawl error {seed}: {e}", flush=True)
    time.sleep(delay)
    return list(visited)


def fetch_efsa_urls():
    return _crawl_one_level(EFSA_SEED, "efsa.europa.eu", delay=10.0)


def fetch_ucdavis_urls():
    return _crawl_one_level(UCDAVIS_SEED, "vetmed.ucdavis.edu", delay=2.0)


def fetch_sydney_vet_urls():
    """Sydney tiene sitemap universitario grande; filtra a la escuela de veterinaria."""
    return _fetch_sitemap_index_urls(
        SYDNEY_SITEMAP_INDEX,
        url_filter=lambda u: "veterinary-science" in u or "/vet/" in u,
        delay=1.0,
    )


def fetch_clinicians_brief_urls():
    return _fetch_sitemap_index_urls(CB_SITEMAP_INDEX, delay=1.0)


def fetch_tvp_urls():
    return _fetch_sitemap_index_urls(TVP_SITEMAP_INDEX, delay=1.0)


def fetch_fao_animal_health_urls():
    return _fetch_sitemap_index_urls(
        FAO_SITEMAP_INDEX,
        url_filter=lambda u: "animal-health" in u or "animal-disease" in u or "animal-production" in u,
        delay=1.0,
    )


def fetch_cornell_vet_urls():
    return _fetch_sitemap_index_urls(CORNELL_SITEMAP_INDEX, delay=1.0)


def fetch_purdue_vet_urls():
    return _fetch_sitemap_index_urls(PURDUE_SITEMAP_INDEX, delay=1.0)


def fetch_tamu_vet_urls():
    return _fetch_sitemap_index_urls(TAMU_SITEMAP_INDEX, delay=1.0)


def fetch_osu_vet_urls():
    return fetch_urls_from_sitemap(OSU_SITEMAP)


def fetch_plos_vet_urls():
    """PLOS API — retorna URLs de artículos sobre veterinaria."""
    params = {
        "q": 'subject_area:"veterinary science"',
        "fl": "id",
        "rows": 1000,
        "wt": "json",
    }
    article_urls = []
    start = 0
    journal_map = {
        "pone": "plosone", "ppat": "plospathogens", "pbio": "plosbiology",
        "pmed": "plosmedicine", "pgen": "plosgenetics", "pcbi": "ploscompbiol",
        "pntd": "plosntds",
    }
    while True:
        params["start"] = start
        try:
            r = requests.get(PLOS_API_URL, params=params, headers=HEADERS, timeout=30)
            data = r.json()
        except Exception as e:
            print(f"  PLOS API error at start={start}: {e}", flush=True)
            break
        docs = data["response"]["docs"]
        if not docs:
            break
        for doc in docs:
            doi = doc.get("id", "")
            if not doi:
                continue
            parts = doi.split("/")
            journal_key = parts[-1].split(".")[1] if len(parts) > 1 else "pone"
            journal_slug = journal_map.get(journal_key, "plosone")
            article_urls.append(f"https://journals.plos.org/{journal_slug}/article?id={doi}")
        total = data["response"]["numFound"]
        start += 1000
        if start >= total:
            break
        time.sleep(2.0)
    return article_urls


# ── Carga de todas las URLs ────────────────────────────────────────────────────

def _load_source(name, sitemaps=None, fn=None):
    """Helper: carga URLs desde lista de sitemaps o función, imprime resultado."""
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
    all_urls += _load_source("Merck Veterinary Manual",  sitemaps=MERCK_SITEMAPS)
    all_urls += _load_source("AAHA",                     sitemaps=AAHA_SITEMAPS)
    all_urls += _load_source("ACVS",                     sitemaps=ACVS_SITEMAPS)
    all_urls += _load_source("MSD Veterinary Manual",    sitemaps=MSD_SITEMAPS)
    all_urls += _load_source("ACVIM",                    sitemaps=ACVIM_SITEMAPS)
    all_urls += _load_source("WOAH (OIE)",               fn=fetch_woah_urls)
    all_urls += _load_source("WSAVA guidelines",         fn=fetch_wsava_guideline_urls)
    all_urls += _load_source("AAVMC",                    fn=fetch_aavmc_urls)
    all_urls += _load_source("NOAH Compendium",          fn=lambda: fetch_urls_from_sitemap(NOAH_SITEMAP))
    all_urls += _load_source("EMA Veterinary Medicines", fn=fetch_ema_vet_urls)  # lento por rate-limit, ~8 min
    all_urls += _load_source("FDA CVM (crawl)",          fn=fetch_fda_cvm_urls)
    all_urls += _load_source("ASPCA Toxicology",         fn=fetch_aspca_tox_urls)
    all_urls += _load_source("Pet Poison Helpline",      fn=fetch_pph_urls)
    all_urls += _load_source("Frontiers Vet Science",    fn=fetch_frontiers_vet_urls)
    all_urls += _load_source("PLOS ONE Veterinary",      fn=fetch_plos_vet_urls)
    all_urls += _load_source("Clinician's Brief",         fn=fetch_clinicians_brief_urls)
    all_urls += _load_source("Today's Vet Practice",      fn=fetch_tvp_urls)
    all_urls += _load_source("EFSA Animal Health",        fn=fetch_efsa_urls)
    all_urls += _load_source("FAO Animal Health",         fn=fetch_fao_animal_health_urls)
    all_urls += _load_source("Cornell Vet",               fn=fetch_cornell_vet_urls)
    all_urls += _load_source("UC Davis Vet",              fn=fetch_ucdavis_urls)
    all_urls += _load_source("Purdue Vet",                fn=fetch_purdue_vet_urls)
    all_urls += _load_source("Texas A&M Vet",             fn=fetch_tamu_vet_urls)
    all_urls += _load_source("Ohio State Vet",            fn=fetch_osu_vet_urls)
    all_urls += _load_source("Univ. of Sydney Vet",       fn=fetch_sydney_vet_urls)

    print(f"\nTotal URLs objetivo: {len(all_urls)}", flush=True)
    return all_urls


# ── Scraping de páginas HTML ───────────────────────────────────────────────────

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

    return {"title": title, "full_text": f"{title}\n{'=' * len(title)}\n\nURL: {url}\n\n{summary}\n\n{body}".strip()}


def url_to_filename(url):
    if "merckvetmanual.com" in url:  prefix = "merck"
    elif "msdvetmanual.com" in url:  prefix = "msd"
    elif "woah.org"          in url:  prefix = "woah"
    elif "wsava.org"         in url:  prefix = "wsava"
    elif "acvs.org"          in url:  prefix = "acvs"
    elif "acvim.org"         in url:  prefix = "acvim"
    elif "aavmc.org"         in url:  prefix = "aavmc"
    elif "noahcompendium"    in url:  prefix = "noah"
    elif "ema.europa.eu"     in url:  prefix = "ema"
    elif "fda.gov"           in url:  prefix = "fda"
    elif "aspca.org"         in url:  prefix = "aspca"
    elif "petpoisonhelpline" in url:  prefix = "pph"
    elif "frontiersin.org"   in url:  prefix = "frontiers"
    elif "plos.org"          in url:  prefix = "plos"
    elif "cliniciansbrief"   in url:  prefix = "cb"
    elif "todaysveterinary"  in url:  prefix = "tvp"
    elif "efsa.europa.eu"    in url:  prefix = "efsa"
    elif "fao.org"           in url:  prefix = "fao"
    elif "vet.cornell.edu"   in url:  prefix = "cornell"
    elif "vetmed.ucdavis"    in url:  prefix = "ucdavis"
    elif "vet.purdue.edu"    in url:  prefix = "purdue"
    elif "vetmed.tamu.edu"   in url:  prefix = "tamu"
    elif "vet.osu.edu"       in url:  prefix = "osu"
    elif "sydney.edu.au"     in url:  prefix = "sydney"
    elif "aaha.org"          in url:  prefix = "aaha"
    else:                             prefix = "vet"
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
            eta_min = ((len(remaining) - i) / rate / 60) if rate > 0 else 0
            done_total = len(done_set) + i
            pct = done_total / total * 100
            print(
                f"[{done_total}/{total} — {pct:.1f}%] "
                f"{rate:.2f} pág/s | ETA: {eta_min:.0f} min",
                flush=True,
            )

        # Delay mayor para sitios con crawl-delay declarado (ASPCA, PPH, PLOS)
        if any(d in url for d in ("aspca.org", "petpoisonhelpline", "plos.org")):
            time.sleep(random.uniform(10.0, 15.0))
        else:
            time.sleep(random.uniform(2.0, 4.0))

    save_progress(progress)
    print(f"\n✓ Terminado.")
    print(f"  Exitosos : {len(progress['done'])}")
    print(f"  Fallidos : {len(progress['failed'])}")
    print(f"  Carpeta  : Google Drive → Proyecto_IA_Veterinaria/")
