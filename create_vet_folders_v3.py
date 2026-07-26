#!/usr/bin/env python3
"""Crea carpetas NUEVAS en Drive para el inventario complementario veterinario (2026-07-26).
Ejecutar UNA vez; las carpetas se crean dentro de DRIVE_VET_ROOT_ID.
"""
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

DRIVE_VET_ROOT_ID = "1sypIsu5f1rtKyuLYKgIN9yuSxYIONi7p"

NEW_SUBFOLDERS = [
    # A.2 — condicionales
    "beva_equine",
    "aaep_equine",
    "bsava_metadata",
    "ivis_metadata",
    # B.2 — revistas OA nuevas
    "veterinary_research_springer",
    "acta_vet_scandinavica",
    "animals_mdpi",
    "vetsci_mdpi",
    "irish_vet_journal",
    "canine_medicine_genetics",
    "jvetres_poland",
    "bjvras_brazil",
    "jvs_korea",
    "hybrid_vet_journals_oa",
    # C — farmacología adicional
    "farad",
    "nval_japan",
    # NOTA: "vmd_pharmacovigilance" se creó y se trashed — ya existía un folder
    # huérfano (DRIVE_UK_VET_PHARMACOVIGILANCE_ID) con regla de enrutamiento
    # pero sin fetcher; se reutilizó ese en vez de duplicar.
    # F — genómica/clínica adicional
    # NOTA: "vet_breed_ontology" se creó y se trashed — el fetcher existente
    # (fetch_vbo_breeds_urls, DRIVE_VBO_BREEDS_ID) tenía una URL rota
    # ("vbo.com"); se corrigió para apuntar al GitHub real en vez de duplicar.
    "faang_data_portal",
    # NOTA: "uk_vida_surveillance" se creó y se trashed — ya existía un folder
    # huérfano (DRIVE_UK_VIDA_ID) con regla de enrutamiento inalcanzable
    # (shadowed); se reutilizó ese en vez de duplicar.
    # G — bienestar/refugios adicional
    "assoc_shelter_vets_guidelines",
    "rspca_science_reports",
    # NOTA: "animal_welfare_institute" se creó y se trashed — ya estaba
    # cubierto por el fetcher existente de "AWIN Welfare" (awionline.org).
    "shelter_animals_count",
]

with open("token.json") as f:
    d = json.load(f)
creds = Credentials(
    token=d["token"], refresh_token=d["refresh_token"],
    token_uri=d["token_uri"], client_id=d["client_id"],
    client_secret=d["client_secret"], scopes=d["scopes"],
)
service = build("drive", "v3", credentials=creds)

for name in NEW_SUBFOLDERS:
    r = service.files().create(
        body={"name": name, "mimeType": "application/vnd.google-apps.folder",
              "parents": [DRIVE_VET_ROOT_ID]},
        fields="id,name",
    ).execute()
    print(f'DRIVE_{name.upper()}_ID = "{r["id"]}"  # {name}')
