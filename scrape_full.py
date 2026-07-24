"""
Scraper completo de Examine.com
Secciones: supplements, conditions, research-feed
Resumible: guarda progreso en progress.json
Uso: python3 scrape_full.py
"""
import os, json, time, random, re, requests
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from google.oauth2.credentials import Credentials

DRIVE_FOLDER_ID     = "13Y_TDhzJlEVf_3sgwc2ytQuc2C66tehP"
DRIVE_TEXT_FOLDER_ID = "1ZZy7z37s0TUmmKx-qIsiciS9Xvtwd5Cl"
PROGRESS_FILE = "progress.json"
SITEMAP_URL   = "https://examine.com/sitemap.xml"
SECTIONS      = ("supplements/", "conditions/", "research-feed/")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}


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


def upload_file(service, folder_id, name, content, mimetype="text/plain"):
    media = MediaInMemoryUpload(content.encode("utf-8"), mimetype=mimetype)
    service.files().create(
        body={"name": name, "parents": [folder_id]},
        media_body=media, fields="id"
    ).execute()


# ── Sitemap ────────────────────────────────────────────────────────────────────

def get_target_urls():
    print("Descargando sitemap...", flush=True)
    r = requests.get(SITEMAP_URL, headers=HEADERS, timeout=30)
    root = ET.fromstring(r.text)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    all_urls = [el.text for el in root.findall(".//sm:loc", ns)]
    target = [u for u in all_urls
              if any(u.replace("https://examine.com/", "").startswith(s) for s in SECTIONS)]
    print(f"URLs objetivo: {len(target)}", flush=True)
    return target


# ── Scraping ───────────────────────────────────────────────────────────────────

def extract_text_from_nextjs(html):
    """Extrae texto de los scripts next_f (Next.js App Router)."""
    strings = re.findall(r'"([A-Z][^"]{80,600})"', html)
    seen, result = set(), []
    for s in strings:
        clean = s.replace("\\n", "\n").replace("\\\\", "\\").strip()
        if clean not in seen and not clean.startswith("M") and "http" not in clean:
            seen.add(clean)
            result.append(clean)
    return "\n\n".join(result)


def scrape_page(url):
    resp = requests.get(url, headers=HEADERS, timeout=25)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Título
    h1 = soup.find("h1")
    title = h1.get_text(strip=True) if h1 else url.split("/")[-2]

    # Descripción meta
    meta_desc = soup.find("meta", {"name": "description"})
    summary = meta_desc["content"] if meta_desc else ""

    # Párrafos visibles
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")
                  if len(p.get_text(strip=True)) > 50]
    para_text = "\n\n".join(paragraphs)

    # Contenido Next.js si los párrafos son escasos
    if len(para_text) < 200:
        para_text = extract_text_from_nextjs(resp.text)

    full_text = f"{title}\n{'=' * len(title)}\n\nURL: {url}\n\n{summary}\n\n{para_text}".strip()
    return {"url": url, "title": title, "summary": summary, "full_text": full_text}


def url_to_filename(url):
    path = url.replace("https://examine.com/", "").strip("/")
    return path.replace("/", "__") + ".txt"


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

    all_urls = get_target_urls()
    progress = load_progress()
    done_set = set(progress["done"])
    remaining = [u for u in all_urls if u not in done_set]

    total = len(all_urls)
    print(f"Total: {total} | Ya hechos: {len(done_set)} | Pendientes: {len(remaining)}\n", flush=True)

    start_time = time.time()
    batch_errors = 0

    for i, url in enumerate(remaining, 1):
        try:
            data = scrape_page(url)
            filename = url_to_filename(url)
            upload_file(service, DRIVE_TEXT_FOLDER_ID, filename, data["full_text"])
            progress["done"].append(url)
            batch_errors = 0
        except Exception as e:
            err = str(e)
            progress["failed"].append({"url": url, "error": err})
            batch_errors += 1
            print(f"  ERROR ({batch_errors}): {url.split('/')[-2]} — {err[:80]}", flush=True)
            # Si 10 errores seguidos, esperar más
            if batch_errors >= 10:
                print("  10 errores seguidos, esperando 60s...", flush=True)
                time.sleep(60)
                batch_errors = 0

        # Guardar progreso cada 50 páginas
        if i % 50 == 0:
            save_progress(progress)
            elapsed = time.time() - start_time
            rate = i / elapsed if elapsed > 0 else 0
            remaining_count = len(remaining) - i
            eta_min = (remaining_count / rate / 60) if rate > 0 else 0
            done_total = len(done_set) + i
            pct = done_total / total * 100
            print(
                f"[{done_total}/{total} — {pct:.1f}%] "
                f"Velocidad: {rate:.2f} pág/s | "
                f"ETA: {eta_min:.0f} min",
                flush=True,
            )

        # Delay aleatorio
        time.sleep(random.uniform(2.0, 4.5))

    save_progress(progress)
    print(f"\n✓ Terminado. {len(progress['done'])} exitosos, {len(progress['failed'])} fallidos.")
    print("Revisa tu Google Drive: Proyecto_IA_Culturismo/textos_largos/")
