#!/usr/bin/env python3
"""
Scraper de medicamentos México — PHASE 0.1.

Alcance:
  - fuentes comerciales mexicanas con marca comercial
  - manifest de fuentes permitidas / restringidas
  - subida de texto crudo a Google Drive
  - sin app, sin UI, sin integración clínica

Fuentes activas por defecto:
  - Farmacias Benavides
  - Farmacias del Ahorro
  - Prixz
  - Farmacias Guadalajara (reactivada 2026-07-25: el bloqueo original era un
    timeout técnico en preflight, no una restricción de licencia/WAF/login)
  - Levic (metadata only)

Fuentes registradas pero no scrapeables (bloqueo real, no solo cautela):
  - PLM México — licencia/términos: contenido editorial con derechos reservados
  - Vidal Vademécum México — licencia pendiente: compilación editorial con derechos reservados
  - Mi Vademécum México — licencia/procedencia del catálogo sin validar
  - Farmacia San Pablo — WAF 403 confirmado en preflight (regla del proyecto:
    un 403 persistente deshabilita la fuente, no se evade)
  - Walmart Farmacia México — términos del sitio restringen robots/automatización
  - Amazon México OTC — WAF + términos restrictivos
  - Nadro — portal B2B con login obligatorio
  - Marzam — portal B2B con login obligatorio

Uso:
    .venv/bin/python scraper_medications.py
"""

import hashlib
import json
import os
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

PROGRESS_FILE = "progress_medications.json"
FOLDER_MAP_FILE = Path("medications_drive_folders.json")
MAX_ITEMS_ENV = "MEDICATIONS_MAX_ITEMS"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; MedicationsCorpusBot/1.0; research use, no checkout)",
    "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
}

SOURCE_POLICIES = [
    {
        "slug": "cofepris_reference",
        "name": "COFEPRIS reference",
        "status": "METADATA_ONLY",
        "url": "https://registros.cofepris.gob.mx/BRSDM/default.aspx",
        "reason": "Referencia regulatoria para cruce posterior; este scraper fase 0.1 está centrado en fuentes comerciales.",
        "delay": 5.0,
    },
    {
        "slug": "plm_mexico",
        "name": "PLM México",
        "status": "NO_SCRAPEAR",
        "url": "https://www.medicamentosplm.com/",
        "reason": "Términos del sitio prohíben acceso automatizado mediante scripts o crawlers sin licencia.",
        "delay": 10.0,
    },
    {
        "slug": "vademecum_vidal_mexico",
        "name": "Vademécum México (Vidal)",
        "status": "NO_SCRAPEAR",
        "url": "https://www.vademecum.es/mexico/MX/alfa",
        "reason": "Compilación editorial con derechos reservados; usar solo mediante permiso o licencia.",
        "delay": 10.0,
    },
    {
        "slug": "mi_vademecum_mexico",
        "name": "Mi Vademécum México",
        "status": "NO_SCRAPEAR",
        "url": "https://mx.mivademecum.com/",
        "reason": "Licencia y procedencia del catálogo pendientes de validación formal.",
        "delay": 10.0,
    },
    {
        "slug": "farmacias_guadalajara",
        "name": "Farmacias Guadalajara",
        "status": "SCRAPE_OK",
        "url": "https://www.farmaciasguadalajara.com/",
        "reason": "Reactivada: el bloqueo original era timeout técnico en preflight, no licencia/WAF/login. Se reintenta con sitemap y, si no responde, con crawl de un nivel; sin cuenta, sin checkout.",
        "delay": 10.0,
    },
    {
        "slug": "farmacias_del_ahorro",
        "name": "Farmacias del Ahorro",
        "status": "SCRAPE_OK",
        "url": "https://www.fahorro.com/",
        "reason": "Catálogo comercial público. Se usa endpoint público del front solo para lectura, sin cuenta, sin checkout.",
        "delay": 1.5,
    },
    {
        "slug": "farmacia_san_pablo",
        "name": "Farmacia San Pablo",
        "status": "NO_SCRAPEAR",
        "url": "https://www.farmaciasanpablo.com.mx/",
        "reason": "Preflight devuelve 403 Access Denied por WAF en robots y páginas de producto desde este entorno.",
        "delay": 10.0,
    },
    {
        "slug": "farmacias_benavides",
        "name": "Farmacias Benavides",
        "status": "SCRAPE_OK",
        "url": "https://www.benavides.com.mx/",
        "reason": "Categorías y páginas públicas accesibles. Se evitarán rutas bloqueadas por robots y cualquier cuenta o checkout.",
        "delay": 3.0,
    },
    {
        "slug": "prixz",
        "name": "Prixz",
        "status": "SCRAPE_OK",
        "url": "https://prixz.com/",
        "reason": "Robots y product sitemaps públicos accesibles; páginas de producto con JSON-LD útil.",
        "delay": 2.0,
    },
    {
        "slug": "walmart_farmacia_mexico",
        "name": "Walmart Farmacia México",
        "status": "NO_SCRAPEAR",
        "url": "https://www.walmart.com.mx/content/farmacia/120016",
        "reason": "Términos del sitio restringen el uso de robots o mecanismos automatizados no proporcionados por Walmart.",
        "delay": 10.0,
    },
    {
        "slug": "amazon_mexico_otc",
        "name": "Amazon México OTC",
        "status": "NO_SCRAPEAR",
        "url": "https://www.amazon.com.mx/",
        "reason": "Robots y términos restrictivos; WAF y contenido de terceros.",
        "delay": 10.0,
    },
    {
        "slug": "nadro",
        "name": "Nadro",
        "status": "NO_SCRAPEAR",
        "url": "https://i22-qa.nadro.mx/login",
        "reason": "Portal B2B con login obligatorio.",
        "delay": 10.0,
    },
    {
        "slug": "marzam",
        "name": "Marzam",
        "status": "NO_SCRAPEAR",
        "url": "https://www.marzamenlinea.com.mx/Login/Login.aspx",
        "reason": "Portal B2B con login obligatorio.",
        "delay": 10.0,
    },
    {
        "slug": "levic",
        "name": "Levic",
        "status": "METADATA_ONLY",
        "url": "https://levic.mx/productosfarmaceuticos/",
        "reason": "El catálogo público es parcial; la compra y detalle completo viven en un portal autenticado.",
        "delay": 5.0,
    },
]

BENAVIDES_CATEGORY_URLS = [
    "https://www.benavides.com.mx/medicamentos/antibioticos",
    "https://www.benavides.com.mx/medicamentos/dolor",
    "https://www.benavides.com.mx/medicamentos/respiratorios",
    "https://www.benavides.com.mx/medicamentos/estomacales",
    "https://www.benavides.com.mx/medicamentos/infecciones",
    "https://www.benavides.com.mx/medicamentos/insomnio",
    "https://www.benavides.com.mx/medicamentos/pediatrico",
    "https://www.benavides.com.mx/medicamentos/otico",
    "https://www.benavides.com.mx/medicamentos/especialidades",
]

FAHORRO_QUERY_TERMS = [
    "amoxicilina", "azitromicina", "ibuprofeno", "paracetamol", "ketorolaco",
    "diclofenaco", "omeprazol", "pantoprazol", "losartan", "metformina",
    "insulina", "atorvastatina", "clonazepam", "sertralina", "cetirizina",
    "loratadina", "salbutamol", "amlodipino", "valsartan", "ceftriaxona",
    "ciprofloxacino", "fluconazol", "clindamicina", "metronidazol",
    "prednisona", "dexametasona", "ketamina", "tramadol", "gabapentina",
]

LEVIC_PUBLIC_URLS = [
    "https://levic.mx/productosfarmaceuticos/",
    "https://levic.mx/wp-content/uploads/2021/01/catalogo34-LEVIC.pdf",
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
            "No existe medications_drive_folders.json. Ejecuta primero "
            "`.venv/bin/python create_medications_folders.py`."
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


def fetch_urls_from_sitemap(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code == 429 or not resp.ok:
            return []
        root = ET.fromstring(resp.text)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        return [node.text for node in root.findall(".//sm:loc", ns) if node.text]
    except ET.ParseError:
        return re.findall(r"<loc>\s*(https?://[^<\s]+)\s*</loc>", resp.text)
    except Exception:
        return []


def fetch_sitemap_index_urls(index_url, url_filter=None, delay=0.5):
    urls = []
    for submap in fetch_urls_from_sitemap(index_url):
        found = fetch_urls_from_sitemap(submap)
        if url_filter:
            found = [url for url in found if url_filter(url)]
        urls.extend(found)
        time.sleep(delay)
    return urls


def crawl_one_level(seed, domain, delay=2.0):
    try:
        resp = requests.get(seed, headers=HEADERS, timeout=30)
        if not resp.ok:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        urls = []
        seen = set()
        for anchor in soup.find_all("a", href=True):
            href = urljoin(seed, anchor["href"])
            if domain in href and href.startswith("http") and href not in seen:
                urls.append(href)
                seen.add(href)
        time.sleep(delay)
        return urls
    except Exception:
        return []


def make_inline_record(source_slug, record):
    payload = {"source_slug": source_slug, **record}
    return f"|INLINE_MED_RECORD|{json.dumps(payload, ensure_ascii=False)}"


def parse_benavides_category_items(html, category_url):
    pattern = re.compile(r"var dl4Objects = (\[.*?\]);", re.S)
    match = pattern.search(html)
    records = []
    if not match:
        return records

    try:
        blobs = json.loads(match.group(1))
    except json.JSONDecodeError:
        return records

    for blob in blobs:
        ecommerce = (blob or {}).get("ecommerce", {})
        for item in ecommerce.get("items", []):
            name = item.get("item_name", "").strip()
            if not name:
                continue
            records.append(
                make_inline_record(
                    "farmacias_benavides",
                    {
                        "record_type": "category_item",
                        "category_url": category_url,
                        "commercial_name": item.get("item_brand") or name,
                        "raw_name": name,
                        "price_mxn": item.get("price"),
                        "sku": item.get("item_id"),
                        "category": item.get("item_category"),
                        "subcategory": item.get("item_category2"),
                        "source_url": category_url,
                    },
                )
            )
    return records


def fetch_benavides_urls():
    urls = []
    seen = set()
    for category_url in BENAVIDES_CATEGORY_URLS:
        try:
            resp = requests.get(category_url, headers=HEADERS, timeout=30)
            if not resp.ok:
                continue
            urls.extend(parse_benavides_category_items(resp.text, category_url))
            soup = BeautifulSoup(resp.text, "html.parser")
            for anchor in soup.find_all("a", href=True):
                href = urljoin(category_url, anchor["href"])
                if not href.startswith("https://www.benavides.com.mx/"):
                    continue
                if href.endswith(".html"):
                    continue
                if any(block in href for block in [
                    "/checkout/", "/customer/", "/catalog/", "/review/", "/sendfriend/",
                    "/productos/", "/servicioalcliente/",
                ]):
                    continue
                if "/medicamentos/" in href:
                    continue
                if href not in seen and href.count("/") >= 3:
                    seen.add(href)
                    urls.append(href)
            time.sleep(3.0)
        except Exception:
            continue
    return urls


def fetch_fahorro_urls():
    urls = []
    seen = set()
    endpoint = "https://api.empathy.co/search/v1/query/fda/search"
    for query in FAHORRO_QUERY_TERMS:
        start = 0
        rows = 40
        while True:
            try:
                resp = requests.get(
                    endpoint,
                    params={"query": query, "rows": rows, "lang": "es", "start": start},
                    headers={"User-Agent": HEADERS["User-Agent"], "Accept": "application/json"},
                    timeout=30,
                )
                if not resp.ok:
                    break
                content = resp.json().get("catalog", {}).get("content", [])
                if not content:
                    break
                for item in content:
                    sku = item.get("sku") or item.get("ecommId") or ""
                    record = {
                        "record_type": "search_item",
                        "query": query,
                        "commercial_name": item.get("ecommBrand") or item.get("ecommTitle") or "",
                        "raw_name": item.get("ecommTitle") or "",
                        "sku": sku,
                        "ean_gtin_candidate": sku if sku.isdigit() and len(sku) in (12, 13, 14) else "",
                        "brand": item.get("ecommBrand") or "",
                        "short_description": item.get("ecommShortDescription") or "",
                        "price_mxn": item.get("price") or item.get("currentPrice"),
                        "prescription_required": item.get("prescriptionRequired"),
                        "stock": item.get("stock"),
                        "category": " > ".join(item.get("categories", [])[:5]),
                        "source_url": (
                            f"https://www.fahorro.com/{item.get('ecommUrlKey')}.html"
                            if item.get("ecommUrlKey") else "https://www.fahorro.com/"
                        ),
                    }
                    inline = make_inline_record("farmacias_del_ahorro", record)
                    if inline not in seen:
                        seen.add(inline)
                        urls.append(inline)
                if len(content) < rows:
                    break
                start += rows
                time.sleep(1.5)
            except Exception:
                break
    return urls


def fetch_prixz_urls():
    return fetch_sitemap_index_urls(
        "https://prixz.com/sitemap_index.xml",
        url_filter=lambda url: "/c/" in url and url.startswith("https://prixz.com/"),
        delay=0.5,
    )


def fetch_farmacias_guadalajara_urls():
    urls = fetch_sitemap_index_urls(
        "https://www.farmaciasguadalajara.com/sitemap.xml",
        url_filter=lambda url: any(
            token in url for token in ("/medicamentos", "/producto", "/salud", "/farmacia")
        ),
        delay=1.0,
    )
    if not urls:
        urls = crawl_one_level(
            "https://www.farmaciasguadalajara.com/",
            "farmaciasguadalajara.com",
            delay=3.0,
        )
    return urls


def fetch_levic_urls():
    urls = []
    for url in LEVIC_PUBLIC_URLS:
        if url.endswith(".pdf"):
            urls.append(
                make_inline_record(
                    "levic",
                    {
                        "record_type": "metadata_pdf",
                        "commercial_name": "",
                        "raw_name": "Catálogo Levic PDF",
                        "source_url": url,
                        "notes": "Catálogo público parcial; no se descarga el PDF en esta fase.",
                    },
                )
            )
        else:
            urls.append(url)
    return urls


def load_source(name, status, fetch_fn=None):
    print(f"Cargando {name} [{status}]...", flush=True)
    if status != "SCRAPE_OK" and status != "METADATA_ONLY":
        print("  -> deshabilitada por política", flush=True)
        return []
    if not fetch_fn:
        return []
    try:
        urls = fetch_fn()
        print(f"  -> {len(urls)} registros/URLs", flush=True)
        return urls
    except Exception as exc:
        print(f"  ERROR: {exc}", flush=True)
        return []


def get_all_urls():
    all_urls = []
    policy = source_policy_map()
    all_urls += load_source(
        "Farmacias Benavides",
        policy["farmacias_benavides"]["status"],
        fetch_benavides_urls,
    )
    all_urls += load_source(
        "Farmacias del Ahorro",
        policy["farmacias_del_ahorro"]["status"],
        fetch_fahorro_urls,
    )
    all_urls += load_source(
        "Prixz",
        policy["prixz"]["status"],
        fetch_prixz_urls,
    )
    all_urls += load_source(
        "Farmacias Guadalajara",
        policy["farmacias_guadalajara"]["status"],
        fetch_farmacias_guadalajara_urls,
    )
    all_urls += load_source(
        "Levic",
        policy["levic"]["status"],
        fetch_levic_urls,
    )
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
        if isinstance(data, dict) and "@graph" in data:
            for item in data["@graph"]:
                if item.get("@type") == "Product":
                    return item
        if isinstance(data, dict) and data.get("@type") == "Product":
            return data
    return {}


def compact_text(text):
    return re.sub(r"\s+", " ", text or "").strip()


def scrape_html_page(url):
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "iframe"]):
        tag.decompose()

    title_node = soup.find("h1") or soup.find("title")
    title = compact_text(title_node.get_text(" ", strip=True)) if title_node else url

    meta_description = ""
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        meta_description = compact_text(meta["content"])

    jsonld = parse_jsonld_product(BeautifulSoup(resp.text, "html.parser"))
    jsonld_text = json.dumps(jsonld, ensure_ascii=False, indent=2) if jsonld else "{}"

    text_blocks = []
    for node in soup.find_all(["p", "li", "td", "dd", "h2", "h3", "span"]):
        txt = compact_text(node.get_text(" ", strip=True))
        if len(txt) >= 40:
            text_blocks.append(txt)
    body = "\n".join(dict.fromkeys(text_blocks))

    return {
        "title": title,
        "full_text": (
            f"{title}\n"
            f"{'=' * len(title)}\n\n"
            f"URL: {url}\n\n"
            f"Descripción: {meta_description}\n\n"
            f"JSON-LD Product:\n{jsonld_text}\n\n"
            f"Texto extraído:\n{body}"
        ).strip(),
    }


def scrape_inline_record(inline_str):
    payload = json.loads(inline_str.split("|INLINE_MED_RECORD|", 1)[1])
    title = payload.get("raw_name") or payload.get("commercial_name") or payload.get("source_slug")
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
    if "|INLINE_MED_RECORD|" in url:
        return scrape_inline_record(url)
    return scrape_html_page(url)


def source_slug_for_url(url):
    if "|INLINE_MED_RECORD|" in url:
        payload = json.loads(url.split("|INLINE_MED_RECORD|", 1)[1])
        return payload["source_slug"]
    if "benavides.com.mx" in url:
        return "farmacias_benavides"
    if "farmaciasguadalajara.com" in url:
        return "farmacias_guadalajara"
    if "prixz.com" in url:
        return "prixz"
    if "levic.mx" in url:
        return "levic"
    if "fahorro.com" in url or "api.empathy.co" in url:
        return "farmacias_del_ahorro"
    return "manifests"


def filename_for_url(url):
    if "|INLINE_MED_RECORD|" in url:
        payload = json.loads(url.split("|INLINE_MED_RECORD|", 1)[1])
        base = payload.get("commercial_name") or payload.get("raw_name") or payload["source_slug"]
    else:
        base = url.split("//", 1)[-1].replace("/", "__")
    clean = re.sub(r"[^A-Za-z0-9._-]+", "_", base).strip("_")
    digest = hashlib.md5(url.encode("utf-8")).hexdigest()[:10]
    return f"{clean[:140]}__{digest}.txt"


def delay_for_url(url):
    slug = source_slug_for_url(url)
    policy = source_policy_map().get(slug, {})
    return policy.get("delay", 2.0)


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
    name = f"source_policies__{time.strftime('%Y%m%d_%H%M%S')}.json"
    upload_text(service, folder_id, name, build_policy_manifest())


def main():
    print("Conectando a Google Drive...", flush=True)
    service = get_drive_service()
    folder_map = load_folder_map()
    print("Conexión exitosa.", flush=True)
    print(f"Carpeta raíz Drive: {folder_map['root_name']} ({folder_map['root_id']})", flush=True)

    print("Subiendo manifest de políticas de fuente...", flush=True)
    upload_policy_manifest(service, folder_map)

    all_urls = get_all_urls()
    max_items_raw = os.getenv(MAX_ITEMS_ENV, "").strip()
    if max_items_raw:
        try:
            max_items = max(0, int(max_items_raw))
            all_urls = all_urls[:max_items]
            print(f"Límite activo por entorno: {MAX_ITEMS_ENV}={max_items}", flush=True)
        except ValueError:
            print(f"Ignorando {MAX_ITEMS_ENV} inválido: {max_items_raw}", flush=True)
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
            folder_id = folder_map["folders"][slug]
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
