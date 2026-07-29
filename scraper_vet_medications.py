#!/usr/bin/env python3
"""
Scraper de medicamentos veterinarios Mexico - PHASE 0.1.

Alcance:
  - fuentes regulatorias y fabricantes veterinarios con datos publicos
  - manifest de fuentes permitidas / restringidas
  - subida de texto crudo a Google Drive
  - sin app, sin UI, sin integracion clinica

Uso:
    .venv/bin/python create_vet_medications_folders.py
    .venv/bin/python scraper_vet_medications.py

Prueba corta:
    VET_MEDICATIONS_MAX_ITEMS=20 .venv/bin/python scraper_vet_medications.py
"""

import hashlib
import json
import os
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

PROGRESS_FILE = "progress_vet_medications.json"
FOLDER_MAP_FILE = Path("vet_medications_drive_folders.json")
MAX_ITEMS_ENV = "VET_MEDICATIONS_MAX_ITEMS"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; VetMedicationCorpusBot/1.0; research use, no checkout)",
    "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
}

PRODUCT_KEYWORDS = [
    "producto", "productos", "medicamento", "medicamentos", "farmaceutico",
    "farmaceuticos", "veterinario", "veterinaria", "salud-animal",
    "animal-health", "vacuna", "vacunas", "antibiotico", "antiparasitario",
    "perro", "perros", "gato", "gatos", "bovino", "bovinos", "porcino",
    "porcinos", "ave", "aves", "equino", "equinos", "ganado", "mascotas",
]

SOURCE_POLICIES = [
    {
        "slug": "senasica_regulatory",
        "name": "SENASICA registros zoosanitarios",
        "status": "SCRAPE_OK",
        "url": "https://www.gob.mx/senasica",
        "reason": "Fuente regulatoria prioritaria. Se leen paginas publicas del sitio; no se automatizan tramites ni areas privadas.",
        "delay": 5.0,
    },
    {
        "slug": "sader_reference",
        "name": "SADER referencia regulatoria",
        "status": "SCRAPE_OK",
        "url": "https://www.gob.mx/agricultura",
        "reason": "Referencia institucional; se leen paginas publicas del sitio.",
        "delay": 5.0,
    },
    {
        "slug": "zoetis_mexico",
        "name": "Zoetis Mexico",
        "status": "SCRAPE_OK",
        "url": "https://www.zoetis.mx/",
        "reason": "Catalogo publico de fabricante; solo lectura de paginas publicas.",
        "delay": 5.0,
    },
    {
        "slug": "msd_animal_health_mexico",
        "name": "MSD Animal Health Mexico",
        "status": "SCRAPE_OK",
        "url": "https://www.msd-salud-animal.mx/",
        "reason": "Catalogo publico de fabricante; solo lectura de paginas publicas.",
        "delay": 5.0,
    },
    {
        "slug": "boehringer_animal_health_mexico",
        "name": "Boehringer Ingelheim Animal Health Mexico",
        "status": "SCRAPE_OK",
        "url": "https://www.boehringer-ingelheim.com/mx/salud-animal",
        "reason": "Paginas publicas de fabricante; se evita cualquier portal privado.",
        "delay": 5.0,
    },
    {
        "slug": "elanco_mexico",
        "name": "Elanco Mexico",
        "status": "SCRAPE_OK",
        "url": "https://www.elanco.com/es-mx",
        "reason": "Paginas publicas de fabricante; solo contenido indexable.",
        "delay": 5.0,
    },
    {
        "slug": "virbac_mexico",
        "name": "Virbac Mexico",
        "status": "SCRAPE_OK",
        "url": "https://mx.virbac.com/",
        "reason": "Catalogo publico de fabricante; solo lectura de paginas publicas.",
        "delay": 5.0,
    },
    {
        "slug": "ceva_mexico",
        "name": "Ceva Mexico",
        "status": "SCRAPE_OK",
        "url": "https://www.ceva.mx/",
        "reason": "Catalogo publico de fabricante; solo lectura de paginas publicas.",
        "delay": 5.0,
    },
    {
        "slug": "vetoquinol_mexico",
        "name": "Vetoquinol Mexico",
        "status": "SCRAPE_OK",
        "url": "https://www.vetoquinol.mx/",
        "reason": "Catalogo publico de fabricante; solo lectura de paginas publicas.",
        "delay": 5.0,
    },
    {
        "slug": "chinoin_veterinaria",
        "name": "Chinoin Veterinaria",
        "status": "SCRAPE_OK",
        "url": "https://www.chinoin.com/",
        "reason": "Fuente de fabricante; se filtran solamente rutas veterinarias publicas si existen.",
        "delay": 5.0,
    },
    {
        "slug": "pisa_agropecuaria",
        "name": "PiSA Agropecuaria",
        "status": "SCRAPE_OK",
        # BUGFIX 2026-07-29: pisaagropecuaria.com.mx redirige (301) a un
        # dominio distinto (pisasaludanimal.com.mx); same_domain() rechazaba
        # todo el contenido real del sitemap por no coincidir. Se usa
        # directamente el dominio final.
        "url": "https://pisasaludanimal.com.mx/",
        "reason": "Catalogo publico de fabricante; solo lectura de paginas publicas.",
        "delay": 5.0,
    },
]


def get_drive_service():
    with open("token.json") as f:
        d = json.load(f)
    creds = Credentials(
        token=d["token"],
        refresh_token=d["refresh_token"],
        token_uri=d["token_uri"],
        client_id=d["client_id"],
        client_secret=d["client_secret"],
        scopes=d["scopes"],
    )
    return build("drive", "v3", credentials=creds)


def load_folder_map():
    if not FOLDER_MAP_FILE.exists():
        raise FileNotFoundError(
            "No existe vet_medications_drive_folders.json. Ejecuta primero "
            "`.venv/bin/python create_vet_medications_folders.py`."
        )
    return json.loads(FOLDER_MAP_FILE.read_text(encoding="utf-8"))


def upload_text(service, folder_id, name, content):
    media = MediaInMemoryUpload(content.encode("utf-8"), mimetype="text/plain")
    service.files().create(
        body={"name": name, "parents": [folder_id]},
        media_body=media,
        fields="id",
    ).execute()


def source_policy_map():
    return {item["slug"]: item for item in SOURCE_POLICIES}


def compact_text(text):
    return re.sub(r"\s+", " ", text or "").strip()


def same_domain(url, base_url):
    return urlparse(url).netloc.lower().replace("www.", "") == urlparse(base_url).netloc.lower().replace("www.", "")


def likely_product_url(url):
    lower = url.lower()
    return any(keyword in lower for keyword in PRODUCT_KEYWORDS)


def fetch_url(url):
    return requests.get(url, headers=HEADERS, timeout=30)


def fetch_urls_from_sitemap(url):
    try:
        resp = fetch_url(url)
        if resp.status_code == 429 or not resp.ok:
            return []
        root = ET.fromstring(resp.text)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        return [node.text for node in root.findall(".//sm:loc", ns) if node.text]
    except ET.ParseError:
        return re.findall(r"<loc>\s*(https?://[^<\s]+)\s*</loc>", resp.text)
    except Exception:
        return []


def _same_scope(url, base_url):
    """same_domain() más un chequeo de ruta: en portales compartidos (ej.
    gob.mx, donde TODAS las dependencias federales viven bajo un solo
    dominio con un sitemap general) el sitemap "/sitemap.xml" resuelto con
    urljoin ignora la ruta de base_url y devuelve contenido de cualquier
    dependencia, no de la fuente real. BUGFIX 2026-07-29: detectado con
    SENASICA y SADER (ambos en gob.mx) devolviendo exactamente las mismas
    347 URLs de trámites de aviación/banca, ninguna relacionada con
    veterinaria. Si base_url tiene una ruta propia (no es solo la raíz del
    dominio), se exige que esa ruta también aparezca en la URL candidata.
    """
    if not same_domain(url, base_url):
        return False
    base_path = urlparse(base_url).path.strip("/")
    if not base_path:
        return True
    first_segment = base_path.split("/")[0]
    return f"/{first_segment}" in urlparse(url).path


def discover_sitemap_urls(base_url):
    candidates = [
        urljoin(base_url, "/sitemap.xml"),
        urljoin(base_url, "/sitemap_index.xml"),
        urljoin(base_url, "/wp-sitemap.xml"),
    ]
    discovered = []
    seen = set()
    for sitemap_url in candidates:
        locs = fetch_urls_from_sitemap(sitemap_url)
        nested = [loc for loc in locs if loc.endswith(".xml")]
        page_locs = [loc for loc in locs if not loc.endswith(".xml")]
        for nested_url in nested[:20]:
            page_locs.extend(fetch_urls_from_sitemap(nested_url))
            time.sleep(0.5)
        for loc in page_locs:
            if loc not in seen and _same_scope(loc, base_url) and likely_product_url(loc):
                seen.add(loc)
                discovered.append(loc)
        if discovered:
            return discovered
    return discovered


def crawl_one_level(base_url):
    try:
        resp = fetch_url(base_url)
        if not resp.ok:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        urls = []
        seen = set()
        for anchor in soup.find_all("a", href=True):
            href = urljoin(base_url, anchor["href"])
            if href in seen:
                continue
            if same_domain(href, base_url) and likely_product_url(href):
                seen.add(href)
                urls.append(href)
        return urls
    except Exception:
        return []


def make_inline_record(source_slug, record):
    payload = {"source_slug": source_slug, **record}
    return f"|INLINE_VET_MED_RECORD|{json.dumps(payload, ensure_ascii=False)}"


def discover_source_urls(policy):
    slug = policy["slug"]
    status = policy["status"]
    base_url = policy["url"]
    if status == "NO_SCRAPEAR":
        return []
    if status == "METADATA_ONLY":
        return [
            make_inline_record(
                slug,
                {
                    "record_type": "source_metadata",
                    "source_url": base_url,
                    "raw_name": policy["name"],
                    "notes": policy["reason"],
                },
            )
        ]

    urls = discover_sitemap_urls(base_url)
    if not urls:
        urls = crawl_one_level(base_url)
    if not urls:
        urls = [base_url]
    return urls


def get_all_urls():
    all_urls = []
    for policy in SOURCE_POLICIES:
        print(f"Cargando {policy['name']} [{policy['status']}]...", flush=True)
        try:
            urls = discover_source_urls(policy)
            print(f"  -> {len(urls)} registros/URLs", flush=True)
            all_urls.extend(urls)
        except Exception as exc:
            print(f"  ERROR: {exc}", flush=True)
        time.sleep(policy.get("delay", 5.0))
    print(f"\nTotal URLs/registros objetivo: {len(all_urls)}", flush=True)
    return all_urls


def parse_jsonld_product(soup):
    for node in soup.find_all("script", attrs={"type": "application/ld+json"}):
        text = node.get_text(strip=True)
        if not text:
            continue
        try:
            data = json.loads(text)
        except Exception:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if isinstance(item, dict) and "@graph" in item:
                items.extend(item["@graph"])
            if isinstance(item, dict) and item.get("@type") == "Product":
                return item
    return {}


def scrape_html_page(url):
    resp = fetch_url(url)
    resp.raise_for_status()
    soup_raw = BeautifulSoup(resp.text, "html.parser")
    jsonld = parse_jsonld_product(soup_raw)

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "iframe"]):
        tag.decompose()

    title_node = soup.find("h1") or soup.find("title")
    title = compact_text(title_node.get_text(" ", strip=True)) if title_node else url

    meta_description = ""
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        meta_description = compact_text(meta["content"])

    text_blocks = []
    for node in soup.find_all(["p", "li", "td", "dd", "h2", "h3", "span"]):
        txt = compact_text(node.get_text(" ", strip=True))
        if len(txt) >= 35:
            text_blocks.append(txt)
    body = "\n".join(dict.fromkeys(text_blocks))

    return {
        "title": title,
        "full_text": (
            f"{title}\n"
            f"{'=' * len(title)}\n\n"
            f"URL: {url}\n\n"
            f"Descripcion: {meta_description}\n\n"
            f"JSON-LD Product:\n{json.dumps(jsonld, ensure_ascii=False, indent=2) if jsonld else '{}'}\n\n"
            f"Texto extraido:\n{body}"
        ).strip(),
    }


def scrape_inline_record(inline_str):
    payload = json.loads(inline_str.split("|INLINE_VET_MED_RECORD|", 1)[1])
    title = payload.get("raw_name") or payload.get("source_slug")
    return {
        "title": title,
        "full_text": (
            f"{title}\n"
            f"{'=' * len(title)}\n\n"
            f"Source slug: {payload.get('source_slug')}\n"
            f"Source URL: {payload.get('source_url', '')}\n"
            f"Record type: {payload.get('record_type', '')}\n\n"
            f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
        ).strip(),
    }


def scrape_page(url):
    if "|INLINE_VET_MED_RECORD|" in url:
        return scrape_inline_record(url)
    return scrape_html_page(url)


def source_slug_for_url(url):
    if "|INLINE_VET_MED_RECORD|" in url:
        payload = json.loads(url.split("|INLINE_VET_MED_RECORD|", 1)[1])
        return payload["source_slug"]
    for policy in SOURCE_POLICIES:
        if same_domain(url, policy["url"]):
            return policy["slug"]
    return "manifests"


def filename_for_url(url):
    if "|INLINE_VET_MED_RECORD|" in url:
        payload = json.loads(url.split("|INLINE_VET_MED_RECORD|", 1)[1])
        base = payload.get("raw_name") or payload.get("source_slug")
    else:
        base = url.split("//", 1)[-1].replace("/", "__")
    clean = re.sub(r"[^A-Za-z0-9._-]+", "_", base).strip("_")
    digest = hashlib.md5(url.encode("utf-8")).hexdigest()[:10]
    return f"{clean[:140]}__{digest}.txt"


def delay_for_url(url):
    slug = source_slug_for_url(url)
    policy = source_policy_map().get(slug, {})
    return policy.get("delay", 5.0)


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"done": [], "failed": []}


def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)


def build_policy_manifest():
    return json.dumps(
        {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "phase": "0.1",
            "scope": "mexico_veterinary_medications",
            "storage": {
                "target": "google_drive",
                "folder_map_file": str(FOLDER_MAP_FILE),
                "raw_record_format": "txt",
                "progress_file": PROGRESS_FILE,
            },
            "sources": SOURCE_POLICIES,
        },
        indent=2,
        ensure_ascii=False,
    )


def upload_policy_manifest(service, folder_map):
    folder_id = folder_map["folders"]["source_policies"]
    name = f"vet_source_policies__{time.strftime('%Y%m%d_%H%M%S')}.json"
    upload_text(service, folder_id, name, build_policy_manifest())


def main():
    print("Conectando a Google Drive...", flush=True)
    service = get_drive_service()
    folder_map = load_folder_map()
    print("Conexion exitosa.", flush=True)
    print(f"Carpeta raiz Drive: {folder_map['root_name']} ({folder_map['root_id']})", flush=True)

    print("Subiendo manifest de politicas de fuente...", flush=True)
    upload_policy_manifest(service, folder_map)

    all_urls = get_all_urls()
    max_items_raw = os.getenv(MAX_ITEMS_ENV, "").strip()
    if max_items_raw:
        try:
            max_items = max(0, int(max_items_raw))
            all_urls = all_urls[:max_items]
            print(f"Limite activo por entorno: {MAX_ITEMS_ENV}={max_items}", flush=True)
        except ValueError:
            print(f"Ignorando {MAX_ITEMS_ENV} invalido: {max_items_raw}", flush=True)

    progress = load_progress()
    done_set = set(progress["done"])
    remaining = [url for url in all_urls if url not in done_set]

    print(
        f"\nTotal: {len(all_urls)} | Ya hechos: {len(done_set)} | "
        f"Pendientes: {len(remaining)}\n",
        flush=True,
    )

    start = time.time()
    streak_errors = 0

    for idx, url in enumerate(remaining, 1):
        try:
            data = scrape_page(url)
            slug = source_slug_for_url(url)
            folder_id = folder_map["folders"].get(slug, folder_map["folders"]["manifests"])
            upload_text(service, folder_id, filename_for_url(url), data["full_text"])
            progress["done"].append(url)
            streak_errors = 0
        except Exception as exc:
            progress["failed"].append({"url": url, "error": str(exc)})
            streak_errors += 1
            print(f"  ERROR ({streak_errors}) {source_slug_for_url(url)}: {str(exc)[:120]}", flush=True)
            if streak_errors >= 10:
                print("  10 errores seguidos, esperando 60s...", flush=True)
                time.sleep(60)
                streak_errors = 0

        if idx % 50 == 0:
            save_progress(progress)
            elapsed = max(time.time() - start, 1)
            rate = idx / elapsed
            eta = ((len(remaining) - idx) / rate) / 60 if rate > 0 else 0
            print(f"[{idx}/{len(remaining)}] {rate:.2f} rec/s - ETA {eta:.0f} min", flush=True)

        time.sleep(delay_for_url(url))

    save_progress(progress)
    print(f"\nFinalizado. {len(progress['done'])} registros subidos.", flush=True)


if __name__ == "__main__":
    main()
