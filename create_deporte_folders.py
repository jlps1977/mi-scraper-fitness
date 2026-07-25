#!/usr/bin/env python3
"""Crea carpetas en Google Drive para el corpus de entrenamiento deportivo."""
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Root donde viven vet y medicina — se crea una nueva carpeta hermana
DRIVE_MASTER_ROOT_ID = "1sypIsu5f1rtKyuLYKgIN9yuSxYIONi7p"

SUBFOLDERS = [
    # A. Organismos internacionales y antidopaje
    "ioc_olympics",
    "wada_antidoping",
    "usada",
    "ukad",
    "global_dro",
    # B. Federaciones internacionales por deporte
    "world_athletics",
    "fifa_football",
    "fiba_basketball",
    "fivb_volleyball",
    "world_aquatics",
    "uci_cycling",
    "itf_tennis",
    "world_rugby",
    "ihf_handball",
    "bwf_badminton",
    "world_taekwondo",
    "ijf_judo",
    "isu_skating",
    "fis_skiing",
    "world_rowing",
    "world_gymnastics",
    "world_boxing",
    "ufc_mma_resources",
    # C. Ciencias del deporte
    "acsm",
    "nsca",
    "ecss",
    "bases_uk",
    "asca_au",
    "uksca",
    "conade_mexico",
    "sport_australia_clearinghouse",
    "uk_sport",
    "usopc_resources",
    # D. Medicina deportiva
    "fims",
    "amssm",
    "aossm",
    "esska",
    "bjsm",
    "sports_health_journal",
    "nata_athletic_training",
    # E. Nutrición deportiva
    "issn_nutrition",
    "ais_nutrition",
    "gssi_gatorade",
    "scan_dietitians",
    "ioc_nutrition",
    # F. Psicología del deporte
    "aasp_psychology",
    "issp_psychology",
    "fepsac_europe",
    # G. Fuerza, acondicionamiento y biomecánica
    "isbs_biomechanics",
    "nsca_strength",
    "velocity_based_training",
    "catapult_resources",
    # H. Revistas OA
    "jssm_journal",
    "sports_mdpi",
    "frontiers_sports",
    "bmc_sports_sci",
    "peerj_sports",
    "translational_sports_med",
    "intl_j_sports_physiol",
    "journal_sport_science",
    # I. Institutos de élite y recursos nacionales
    "ais_australia",
    "inef_spain",
    "aspire_qatar",
    "canadian_sport_institute",
    "sport_new_zealand",
    # J. Bases de datos y recursos educativos
    "sirc_canada",
    "pubmed_sports",
    "coach_education_resources",
    "strength_power_research",
]

with open("token.json") as f:
    d = json.load(f)
creds = Credentials(
    token=d["token"], refresh_token=d["refresh_token"],
    token_uri=d["token_uri"], client_id=d["client_id"],
    client_secret=d["client_secret"], scopes=d["scopes"],
)
service = build("drive", "v3", credentials=creds)

# Crear carpeta raíz de deporte
root_r = service.files().create(
    body={"name": "DEPORTE_ENTRENADORES", "mimeType": "application/vnd.google-apps.folder",
          "parents": [DRIVE_MASTER_ROOT_ID]},
    fields="id,name",
).execute()
DEPORTE_ROOT_ID = root_r["id"]
print(f'DRIVE_DEPORTE_ROOT_ID = "{DEPORTE_ROOT_ID}"  # DEPORTE_ENTRENADORES')

for name in SUBFOLDERS:
    r = service.files().create(
        body={"name": name, "mimeType": "application/vnd.google-apps.folder",
              "parents": [DEPORTE_ROOT_ID]},
        fields="id,name",
    ).execute()
    print(f'DRIVE_{name.upper()}_ID = "{r["id"]}"  # {name}')
