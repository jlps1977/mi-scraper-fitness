#!/usr/bin/env python3
"""Crea subcarpetas adicionales para medicina humana en Google Drive."""
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

MEDICINA_ROOT_ID = "1pf4QWGSh4UiqKgFyWmABpGFPanHfgvCl"

NEW_FOLDERS = [
    # Manuales
    "merck_manual_pro",
    "merck_manual_consumer",
    "msd_manual_pro",
    "msd_manual_consumer",
    "wikem",
    "msf_guidelines",
    # Orgs internacionales
    "health_canada",
    "australia_health",
    "samhsa",
    "unicef_health",
    "nhds_conditions",
    # Guías clínicas
    "nice_guidelines",
    "sign_guidelines",
    "ema_human",
    "fda_guidance",
    "cadth",
    "nhmrc_australia",
    "acp_guidelines",
    "aafp_guidelines",
    # Especialidades
    "aha_guidelines",
    "acc_guidelines",
    "esc_guidelines",
    "asco_guidelines",
    "esmo_guidelines",
    "aan_guidelines",
    "idsa_guidelines",
    "kdigo_guidelines",
    "ada_diabetes",
    "endocrine_society",
    "gina_asthma",
    "gold_copd",
    "ats_guidelines",
    "ash_guidelines",
    "acg_guidelines",
    "aga_guidelines",
    "acog_guidelines",
    "rcog_guidelines",
    "aap_guidelines",
    "sccm_guidelines",
    "eau_guidelines",
    "aad_guidelines",
    "apa_guidelines",
    "aaaai_guidelines",
    "wses_guidelines",
    "eras_guidelines",
    # Hospitales / universidades
    "mayo_clinic",
    "cleveland_clinic",
    "johns_hopkins",
    "mount_sinai",
    "stanford_health",
    "ucsf_health",
    "nyu_langone",
    "penn_medicine",
    "yale_medicine",
    # Farmacología extra
    "inchem_toxicology",
    "niosh_pocket",
    "cameo_chemicals",
    "iarc_monographs",
    "cdc_chemical",
    "who_chemical",
    # Literatura científica extra
    "bmc_series",
    "elife_journal",
    "jama_open",
    "cureus",
    "jmir",
    "peerj",
    "eurosurveillance",
    "cdc_eid",
    "annals_family",
    "medrxiv",
    # Bases de datos clínicas extra
    "gard_rare_diseases",
    "hpo_ontology",
    "mondo_ontology",
    "clinvar",
    "open_targets",
    "gwas_catalog",
    "medgen",
    "ncbi_gene",
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
    r = service.files().create(
        body={"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": [MEDICINA_ROOT_ID]},
        fields="id,name",
    ).execute()
    print(f'DRIVE_{name.upper()}_ID = "{r["id"]}"  # {name}')
