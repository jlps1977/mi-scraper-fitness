import os
import json
import time
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

DRIVE_FOLDER_ID = "13Y_TDhzJlEVf_3sgwc2ytQuc2C66tehP"
DRIVE_TEXT_FOLDER_ID = "1ZZy7z37s0TUmmKx-qIsiciS9Xvtwd5Cl"
SCOPES = ["https://www.googleapis.com/auth/drive"]

SUPPLEMENTS = [
    {"slug": "creatine", "name": "Creatine"},
    {"slug": "whey-protein", "name": "Whey Protein"},
    {"slug": "caffeine", "name": "Caffeine"},
    {"slug": "beta-alanine", "name": "Beta-Alanine"},
    {"slug": "bcaa", "name": "BCAAs"},
]

def get_drive_service():
    from google.oauth2.credentials import Credentials
    with open("token.json") as f:
        token_data = json.load(f)
    creds = Credentials(
        token=token_data["token"],
        refresh_token=token_data["refresh_token"],
        token_uri=token_data["token_uri"],
        client_id=token_data["client_id"],
        client_secret=token_data["client_secret"],
        scopes=token_data["scopes"],
    )
    return build("drive", "v3", credentials=creds)

def scrape_examine(slug):
    url = f"https://examine.com/supplements/{slug}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    title = soup.find("h1")
    title_text = title.get_text(strip=True) if title else slug
    summary_tag = soup.find("meta", {"name": "description"})
    summary = summary_tag["content"] if summary_tag else ""
    paragraphs = soup.find_all("p")
    full_text = "\n\n".join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 60)
    return {"slug": slug, "title": title_text, "url": url, "summary": summary, "full_text": full_text}

def upload_metadata(service, data):
    jsonl_line = json.dumps({"slug": data["slug"], "title": data["title"], "url": data["url"], "summary": data["summary"]}, ensure_ascii=False)
    file_name = f"{data['slug']}_meta.jsonl"
    media = MediaInMemoryUpload(jsonl_line.encode("utf-8"), mimetype="application/json")
    service.files().create(body={"name": file_name, "parents": [DRIVE_FOLDER_ID]}, media_body=media, fields="id").execute()
    return file_name

def upload_full_text(service, data):
    file_name = f"{data['slug']}.txt"
    content = f"{data['title']}\n{'='*len(data['title'])}\n\n{data['full_text']}"
    media = MediaInMemoryUpload(content.encode("utf-8"), mimetype="text/plain")
    service.files().create(body={"name": file_name, "parents": [DRIVE_TEXT_FOLDER_ID]}, media_body=media, fields="id").execute()
    return file_name

if __name__ == "__main__":
    print("Conectando a Google Drive...")
    service = get_drive_service()
    print("Conexión exitosa.\n")

    for supp in SUPPLEMENTS:
        print(f"Scrapeando {supp['name']}...", end=" ", flush=True)
        try:
            data = scrape_examine(supp["slug"])
            upload_metadata(service, data)
            upload_full_text(service, data)
            print(f"OK — {len(data['full_text'])} chars")
        except Exception as e:
            print(f"ERROR: {e}")
        time.sleep(2)

    print("\nListo. Revisa tu Google Drive: Proyecto_IA_Culturismo/")
