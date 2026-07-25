#!/usr/bin/env python3
"""Crea subcarpetas para el corpus de medicina humana en Google Drive."""
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

DRIVE_VET_ROOT_ID = "1sypIsu5f1rtKyuLYKgIN9yuSxYIONi7p"

# Crear carpeta raíz de medicina humana dentro del mismo root
NEW_FOLDERS_ROOT = [
    "MEDICINA_HUMANA",
]

SUBFOLDERS = [
    "medlineplus",
    "cdc_content",
    "cdc_mmwr",
    "who_publications",
    "paho",
    "ecdc",
    "nci_pdq",
    "nih_hiv_guidelines",
    "uspstf",
    "ahrq",
    "va_dod_guidelines",
    "atsdr_toxicology",
    "epa_iris",
    "dailymed",
    "openfda",
    "rxnorm_info",
    "clinicaltrials",
    "europe_pmc",
    "plos_medicine",
    "frontiers_medicine",
    "bmc_medicine",
    "nhs_conditions",
    "nhs_medicines",
    "ncbi_bookshelf",
    "orphanet",
]

with open("token.json") as f:
    d = json.load(f)
creds = Credentials(
    token=d["token"], refresh_token=d["refresh_token"],
    token_uri=d["token_uri"], client_id=d["client_id"],
    client_secret=d["client_secret"], scopes=d["scopes"],
)
service = build("drive", "v3", credentials=creds)

# Crear carpeta raíz de medicina humana
root_r = service.files().create(
    body={"name": "MEDICINA_HUMANA", "mimeType": "application/vnd.google-apps.folder", "parents": [DRIVE_VET_ROOT_ID]},
    fields="id,name",
).execute()
MEDICINA_ROOT_ID = root_r["id"]
print(f'DRIVE_MEDICINA_ROOT_ID = "{MEDICINA_ROOT_ID}"  # MEDICINA_HUMANA')

for name in SUBFOLDERS:
    r = service.files().create(
        body={"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": [MEDICINA_ROOT_ID]},
        fields="id,name",
    ).execute()
    print(f'DRIVE_{name.upper()}_ID = "{r["id"]}"  # {name}')
