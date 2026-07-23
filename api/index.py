import os
import json
import requests
from http.server import BaseHTTPRequestHandler
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/drive"]

SUPPLEMENTS = [
    {"slug": "creatine", "name": "Creatine"},
    {"slug": "protein", "name": "Protein"},
    {"slug": "caffeine", "name": "Caffeine"},
    {"slug": "beta-alanine", "name": "Beta-Alanine"},
    {"slug": "bcaa", "name": "BCAAs"},
]

def get_drive_service():
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if not creds_json:
        raise ValueError("GOOGLE_CREDENTIALS_JSON env var not set")
    creds_info = json.loads(creds_json)
    creds = service_account.Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)

def scrape_examine(slug):
    url = f"https://examine.com/supplements/{slug}/"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; FitnessBot/1.0)"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    title = soup.find("h1")
    title_text = title.get_text(strip=True) if title else slug

    summary_tag = soup.find("meta", {"name": "description"})
    summary = summary_tag["content"] if summary_tag else ""

    paragraphs = soup.find_all("p")
    full_text = "\n\n".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 60)

    return {
        "slug": slug,
        "title": title_text,
        "url": url,
        "summary": summary,
        "full_text": full_text,
    }

def upload_metadata(service, folder_id, data):
    jsonl_line = json.dumps({
        "slug": data["slug"],
        "title": data["title"],
        "url": data["url"],
        "summary": data["summary"],
    }, ensure_ascii=False)
    file_name = f"{data['slug']}_meta.jsonl"
    media = MediaInMemoryUpload(jsonl_line.encode("utf-8"), mimetype="application/json")
    file_meta = {"name": file_name, "parents": [folder_id]}
    service.files().create(body=file_meta, media_body=media, fields="id").execute()
    return file_name

def upload_full_text(service, text_folder_id, data):
    file_name = f"{data['slug']}.txt"
    content = f"{data['title']}\n{'='*len(data['title'])}\n\n{data['full_text']}"
    media = MediaInMemoryUpload(content.encode("utf-8"), mimetype="text/plain")
    file_meta = {"name": file_name, "parents": [text_folder_id]}
    service.files().create(body=file_meta, media_body=media, fields="id").execute()
    return file_name

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        folder_id = os.environ.get("DRIVE_FOLDER_ID")
        text_folder_id = os.environ.get("DRIVE_TEXT_FOLDER_ID")

        if not folder_id or not text_folder_id:
            self._respond(500, {"error": "Missing DRIVE_FOLDER_ID or DRIVE_TEXT_FOLDER_ID"})
            return

        results = []
        errors = []

        try:
            service = get_drive_service()
        except Exception as e:
            self._respond(500, {"error": f"Drive auth failed: {str(e)}"})
            return

        for supp in SUPPLEMENTS:
            try:
                data = scrape_examine(supp["slug"])
                meta_file = upload_metadata(service, folder_id, data)
                text_file = upload_full_text(service, text_folder_id, data)
                results.append({
                    "supplement": supp["name"],
                    "meta_file": meta_file,
                    "text_file": text_file,
                    "status": "ok",
                })
            except Exception as e:
                errors.append({"supplement": supp["name"], "error": str(e)})

        self._respond(200, {
            "message": f"Scraping completado: {len(results)} ok, {len(errors)} errores",
            "results": results,
            "errors": errors,
        })

    def _respond(self, status, body):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False, indent=2).encode("utf-8"))
