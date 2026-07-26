#!/usr/bin/env python3
"""Crea carpetas NUEVAS en Drive para el inventario complementario de nutrición (2026-07-26).
Ejecutar UNA vez; las carpetas se crean dentro de DRIVE_NUTRICION_ROOT_ID.
"""
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

DRIVE_NUTRICION_ROOT_ID = "1Bfp5mlxLi9th6SZFwJCQyJY58K_1wu5f"

NEW_SUBFOLDERS = [
    # NOTA: "canadian_nutrient_file" NO está aquí — ya existía una carpeta
    # reservada desde la construcción original (DRIVE_CANADIAN_NUTRIENT_FILE_ID).
    # Se creó y luego se envió a la papelera un duplicado; no la vuelvas a crear.
    # C. Bases de composición — faltantes
    "nevo_netherlands",
    "swiss_food_composition",
    "asean_food_composition",
    "langual_taxonomy",
    "foodb_compounds",
    "foodrepo",
    "global_dietary_database",
    # B. Revistas — faltantes
    "global_perspectives_nutrition",
    "maternal_health_neonatology_nutr",
    "hybrid_nutrition_journals_oa",
    # F. Nutrición clínica — faltantes
    "kdoqi_kidney_nutrition",
    "easl_liver_nutrition",
    "cystic_fibrosis_nutrition",
    "crohns_colitis_nutrition",
    "national_lipid_assoc",
    # I. Microbioma — faltantes
    "curated_metagenomic_data",
    "microbiomedb",
    "disbiome_microbiome",
    # J. Suplementos — faltantes
    "cam_cancer_summaries",
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
              "parents": [DRIVE_NUTRICION_ROOT_ID]},
        fields="id,name",
    ).execute()
    print(f'DRIVE_{name.upper()}_ID = "{r["id"]}"  # {name}')
