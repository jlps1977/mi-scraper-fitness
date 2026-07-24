#!/usr/bin/env python3
"""Crea subcarpetas adicionales en Proyecto_IA_Veterinaria en Google Drive."""
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

DRIVE_VET_ROOT_ID = "1sypIsu5f1rtKyuLYKgIN9yuSxYIONi7p"

NEW_FOLDERS = [
    "acvim",
    "aavmc",
    "noah_compendium",
    "ema_veterinary",
    "fda_cvm",
    "aspca_toxicology",
    "pet_poison_helpline",
    "frontiers_veterinary",
    "plos_veterinary",
]

with open("token.json") as f:
    d = json.load(f)
creds = Credentials(
    token=d["token"], refresh_token=d["refresh_token"],
    token_uri=d["token_uri"], client_id=d["client_id"],
    client_secret=d["client_secret"], scopes=d["scopes"],
)
service = build("drive", "v3", credentials=creds)

for name in NEW_FOLDERS:
    result = service.files().create(
        body={
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [DRIVE_VET_ROOT_ID],
        },
        fields="id,name",
    ).execute()
    print(f'DRIVE_{name.upper()}_ID  = "{result["id"]}"  # {name}')
