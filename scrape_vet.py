"""
Scraper veterinario — Merck Veterinary Manual + AAHA
VIN excluido: requiere suscripción de pago.
Resumible: guarda progreso en progress_vet.json
Uso: python3 scrape_vet.py
"""
import os, json, time, random, re, requests
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from google.oauth2.credentials import Credentials

DRIVE_VET_ROOT_ID   = "1sypIsu5f1rtKyuLYKgIN9yuSxYIONi7p"   # Proyecto_IA_Veterinaria
DRIVE_MERCK_ID      = "107q-Vp6aWHR7bUYi7FxEedz1ywULSzNV"   # merck_manual
DRIVE_AAHA_ID       = "1N0_pVjDE67q3Gcc743aMb1PBQbrs523f"    # aaha
DRIVE_ACVS_ID       = "1SjE0iSJJBrbFbdmZsFdRMqh27pL7BZO9"    # acvs
PROGRESS_FILE = "progress_vet.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

# ── Sitemaps por fuente ────────────────────────────────────────────────────────

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
    if "merckvetmanual.com" in url:
        return DRIVE_MERCK_ID
    if "acvs.org" in url:
        return DRIVE_ACVS_ID
    return DRIVE_AAHA_ID


def upload_file(service, url, name, content):
    folder_id = folder_for_url(url)
    media = MediaInMemoryUpload(content.encode("utf-8"), mimetype="text/plain")
    service.files().create(
        body={"name": name, "parents": [folder_id]},
        media_body=media, fields="id"
    ).execute()


# ── Sitemap ────────────────────────────────────────────────────────────────────

def fetch_urls_from_sitemap(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    content = r.text
    root = ET.fromstring(content)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [el.text for el in root.findall(".//sm:loc", ns)]


def get_all_urls():
    all_urls = []

    print("Cargando sitemaps de Merck Veterinary Manual...", flush=True)
    for sm in MERCK_SITEMAPS:
        try:
            urls = fetch_urls_from_sitemap(sm)
            print(f"  {sm.split('/')[-1]}: {len(urls)} URLs", flush=True)
            all_urls.extend(urls)
        except Exception as e:
            print(f"  ERROR {sm}: {e}", flush=True)

    print("Cargando sitemaps de AAHA...", flush=True)
    for sm in AAHA_SITEMAPS:
        try:
            urls = fetch_urls_from_sitemap(sm)
            print(f"  {sm.split('/')[-1]}: {len(urls)} URLs", flush=True)
            all_urls.extend(urls)
        except Exception as e:
            print(f"  ERROR {sm}: {e}", flush=True)

    print("Cargando sitemaps de ACVS...", flush=True)
    for sm in ACVS_SITEMAPS:
        try:
            urls = fetch_urls_from_sitemap(sm)
            print(f"  {sm.split('/')[-1]}: {len(urls)} URLs", flush=True)
            all_urls.extend(urls)
        except Exception as e:
            print(f"  ERROR {sm}: {e}", flush=True)

    print(f"\nTotal URLs objetivo: {len(all_urls)}", flush=True)
    return all_urls


# ── Scraping ───────────────────────────────────────────────────────────────────

def scrape_page(url):
    resp = requests.get(url, headers=HEADERS, timeout=25)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Título
    h1 = soup.find("h1") or soup.find("h2")
    title = h1.get_text(strip=True) if h1 else url.split("/")[-2].replace("-", " ").title()

    # Descripción meta
    meta = soup.find("meta", {"name": "description"})
    summary = meta["content"] if meta else ""

    # Limpiar navegación y elementos no-contenido
    for tag in soup(["script", "style", "nav", "footer", "header",
                     "aside", "form", "button", "iframe"]):
        tag.decompose()

    # Extraer párrafos con contenido real
    paragraphs = [
        p.get_text(separator=" ", strip=True)
        for p in soup.find_all(["p", "li", "td", "dd"])
        if len(p.get_text(strip=True)) > 50
    ]
    body = "\n\n".join(paragraphs)

    # Si hay poco texto, buscar en divs de contenido
    if len(body) < 300:
        for div in soup.find_all("div", class_=re.compile(r"content|article|body|main", re.I)):
            div_text = div.get_text(separator="\n", strip=True)
            if len(div_text) > 300:
                body = div_text
                break

    full_text = f"{title}\n{'=' * len(title)}\n\nURL: {url}\n\n{summary}\n\n{body}".strip()
    return {"title": title, "full_text": full_text}


def url_to_filename(url):
    """Convierte URL a nombre de archivo con prefijo de fuente."""
    if "merckvetmanual.com" in url:
        prefix = "merck"
    elif "aaha.org" in url:
        prefix = "aaha"
    elif "acvs.org" in url:
        prefix = "acvs"
    else:
        prefix = "vet"
    path = url.split("//", 1)[-1].replace("/", "__").strip("__")
    # Truncar si es muy largo
    if len(path) > 180:
        path = path[:180]
    return f"{prefix}__{path}.txt"


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
            slug = url.rstrip("/").split("/")[-1]
            print(f"  ERROR ({batch_errors}): {slug} — {err[:80]}", flush=True)
            if batch_errors >= 10:
                print("  10 errores seguidos, esperando 60s...", flush=True)
                time.sleep(60)
                batch_errors = 0

        # Guardar y reportar cada 50 páginas
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

        time.sleep(random.uniform(2.0, 4.0))

    save_progress(progress)
    print(f"\n✓ Terminado.")
    print(f"  Exitosos : {len(progress['done'])}")
    print(f"  Fallidos : {len(progress['failed'])}")
    print(f"  Carpeta  : Google Drive → Proyecto_IA_Veterinaria/")
