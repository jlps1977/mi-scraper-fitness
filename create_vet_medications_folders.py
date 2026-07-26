#!/usr/bin/env python3
"""Crea carpetas en Google Drive para medicamentos veterinarios Mexico.

Uso:
    .venv/bin/python create_vet_medications_folders.py

Salida:
    - crea/recupera la carpeta raiz `vet_medications_mexico_phase0`
    - crea/recupera subcarpetas por fuente
    - escribe `vet_medications_drive_folders.json` con el mapping de IDs
"""

import json
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ROOT_FOLDER_NAME = "vet_medications_mexico_phase0"
FOLDER_MAP_FILE = Path("vet_medications_drive_folders.json")

SOURCE_FOLDERS = {
    "source_policies": "source_policies",
    "senasica_regulatory": "senasica_regulatory",
    "sader_reference": "sader_reference",
    "zoetis_mexico": "zoetis_mexico",
    "msd_animal_health_mexico": "msd_animal_health_mexico",
    "boehringer_animal_health_mexico": "boehringer_animal_health_mexico",
    "elanco_mexico": "elanco_mexico",
    "virbac_mexico": "virbac_mexico",
    "ceva_mexico": "ceva_mexico",
    "vetoquinol_mexico": "vetoquinol_mexico",
    "chinoin_veterinaria": "chinoin_veterinaria",
    "pisa_agropecuaria": "pisa_agropecuaria",
    "restricted_sources": "restricted_sources",
    "manifests": "manifests",
}


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


def find_folder(service, name, parent_id=None):
    parent_filter = f" and '{parent_id}' in parents" if parent_id else ""
    query = (
        "mimeType = 'application/vnd.google-apps.folder' "
        f"and name = '{name}' and trashed = false{parent_filter}"
    )
    resp = service.files().list(q=query, fields="files(id,name)", pageSize=10).execute()
    files = resp.get("files", [])
    return files[0]["id"] if files else None


def ensure_folder(service, name, parent_id=None):
    existing = find_folder(service, name, parent_id=parent_id)
    if existing:
        return existing, False

    body = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        body["parents"] = [parent_id]
    created = service.files().create(body=body, fields="id,name").execute()
    return created["id"], True


def main():
    service = get_drive_service()

    root_id, created = ensure_folder(service, ROOT_FOLDER_NAME)
    print(f'ROOT_ID = "{root_id}"  # {"created" if created else "existing"}')

    folder_map = {
        "root_name": ROOT_FOLDER_NAME,
        "root_id": root_id,
        "folders": {},
    }

    for key, folder_name in SOURCE_FOLDERS.items():
        folder_id, was_created = ensure_folder(service, folder_name, parent_id=root_id)
        folder_map["folders"][key] = folder_id
        print(
            f'DRIVE_{key.upper()}_ID = "{folder_id}"  '
            f'# {folder_name} {"created" if was_created else "existing"}'
        )

    FOLDER_MAP_FILE.write_text(json.dumps(folder_map, indent=2), encoding="utf-8")
    print(f"\nEscrito: {FOLDER_MAP_FILE}")


if __name__ == "__main__":
    main()
