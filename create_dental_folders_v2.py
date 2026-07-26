#!/usr/bin/env python3
"""Crea carpetas NUEVAS en Drive para el inventario dental v2 (2026-07-25).
Ejecutar UNA vez; las carpetas ya existentes se crean dentro de DENTAL_ROOT.
"""
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

DRIVE_DENTAL_ROOT_ID = "1Q2inxTG9_s0Uiq_WOlogYKh_zscFzJa_"

NEW_SUBFOLDERS = [
    # Sec 1 — nuevas
    "iso_dental_metadata",
    "unep_dental",
    # Sec 2 — nuevas
    "consejo_dentistas_spain",
    "adm_mexico",
    "cora_argentina",
    "colegio_dentistas_chile",
    # Sec 3 — nuevas
    "ada_evidence_guidelines",
    "cgdent_uk",
    "rcs_england_dental",
    # Sec 4 — nuevas
    "j_clinical_exp_dentistry",
    "j_oral_maxillofac_research",
    "j_dental_sciences",
    "j_oral_bio_craniofacial",
    "saudi_dental_journal",
    "wiley_dental_oa",
    # Sec 5 — nuevas
    "unpaywall_dental",
    "core_dental",
    "openaire_dental",
    # Sec 6 — nuevas
    "univ_iowa_oral",
    "oral_cancer_foundation",
    "ada_radiation_guidance",
    # Sec 7 — nuevas
    "openfda_drug_dental",
    "openfda_510k_dental",
    "openfda_maude_dental",
    "openfda_recall_dental",
    "rxnorm_dental",
    "pubchem_dental",
    "nist_dental_materials",
    # Sec 8 — nuevas
    "wfo_orthodontics",
    "eacmfs_surgery",
    "aaed_esthetic_dental",
    # Sec 9 — nuevas
    "ecfr_bloodborne",
    "nhs_htm0105_decontam",
    "paho_ipc_dental",
    "ada_infection_control",
    # Sec 10 — nuevas
    "cms_hcpcs_dental",
    "nlm_hcpcs_api",
    "hipaa_security_dental",
    "hipaa_privacy_dental",
    "hl7_fhir_dental",
    "consejo_dentistas_docs",
    "imss_procedimiento_dental",
    "ada_cdt_metadata",
    # Sec 11 — nuevas
    "oral_health_foundation",
    "healthdirect_australia",
    "better_health_vic",
    "colgate_metadata",
    "nidcr_health_info",
    # Sec 12 — nuevas
    "dicom_standard",
    "3shape_dental",
    "itero_dental",
    "exocad_dental",
    "open_ortho",
    "slicer_docs",
    "monai_docs",
    "itksnap_docs",
    "opendental_software",
    # Sec 13 — nuevas
    "nidcr_dds_hub",
    "karolinska_dental",
    "karolinska_open",
    "unam_repositorio",
    "ufes_repositorio",
    "uam_biblos",
    "usp_teses",
    "umich_deep_blue",
    # Sec 14 — nuevas
    "biorxiv_dental",
    "datacite_dental",
    "arxiv_dental",
    "mendeley_dental",
    "researchgate_metadata",
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
              "parents": [DRIVE_DENTAL_ROOT_ID]},
        fields="id,name",
    ).execute()
    print(f'DRIVE_{name.upper()}_ID = "{r["id"]}"  # {name}')
