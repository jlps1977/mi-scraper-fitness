#!/usr/bin/env python3
"""
Scraper de Odontología — corpus para IA de Dental OS (dentistas y consultorios).
14 secciones, 100+ fuentes:
  A) Organismos internacionales (FDI, WHO, PAHO, IAPD)
  B) Asociaciones nacionales (ADA USA, BDA UK, CDA, ADC Australia, SEOC, COEM, CFO, CMD)
  C) Guías clínicas (SDCEP, NICE, AAPD, AAE, AAP, AAOMS, IADT, EFP, EAPD, AAO, AAOMR)
  D) Revistas OA (BMC Oral Health, MDPI Dentistry, Open Dentistry, Frontiers Dental, BDJ Open)
  E) Bases de datos API (PubMed MeSH dental, OpenAlex, Crossref, DOAJ, Zenodo, Semantic Scholar)
  F) Diagnóstico y radiología oral (Radiopaedia dental, CDC oral DX, atlas patología oral)
  G) Farmacología y materiales (DailyMed dental, FDA dental devices, COFEPRIS, INVIMA)
  H) Especialidades (AAE endo, AAP perio, AAO ortho, ITI implantes, EAO, ACP, AAOMFS)
  I) Control de infecciones (CDC infection control dental, OSHA, OSAP)
  J) Codificación y gestión (ADA practice, Dental Economics, NHS BSA, NOM-013)
  K) Educación al paciente (MouthHealthy ADA, CDC oral public, WHO, PAHO, NHS patient)
  L) Tecnología dental (AI in dentistry papers, CBCT, CAD/CAM, flujo digital)
  M) Institutos de investigación (NIDCR NIH, Forsyth, KCL, UCL Eastman, UNAM Estoma)
  N) Repositorios OA y preprints (medRxiv dental, OSF, Figshare, Europe PMC)

Uso: .venv/bin/python scraper_dental.py
Reanuda desde progress_dental.json (crea si no existe).
"""

import os, re, json, time
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from google.oauth2.credentials import Credentials

# ── Drive — IDs de carpetas ────────────────────────────────────────────────────
DRIVE_DENTAL_ROOT_ID              = "1Q2inxTG9_s0Uiq_WOlogYKh_zscFzJa_"

# A. Organismos internacionales
DRIVE_FDI_WORLD_DENTAL_ID         = "1y2BH5RUCFbYVDVMS8KZJUECqkNQ_sxwO"
DRIVE_WHO_ORAL_HEALTH_ID          = "1j7zBEpN3Jr98QM6De7fFUqh_-q6iZOJe"
DRIVE_PAHO_ORAL_HEALTH_ID         = "1-eMqi45LR1zx9fDboEwXQxY58lmZI6xs"
DRIVE_IAPD_INTERNATIONAL_ID       = "14rb1evrg-ZNnaR4TMBUlLvXALNJ917Do"

# B. Asociaciones nacionales
DRIVE_ADA_USA_ID                  = "1ymy9UtU-z_gIaCuejDWdpOMYfP5RIi0C"
DRIVE_BDA_UK_ID                   = "1UXlnb01_bDAiUgHGtdqSKEx07AWW0dO9"
DRIVE_CDA_CANADA_ID               = "19MijoDcY8VSIV9bPTdxL8qyRBon_Rqgb"
DRIVE_ADC_AUSTRALIA_ID            = "1lLGLp56wEjay6Yrxr21ciw6vUGrFfID0"
DRIVE_SEOC_SPAIN_ID               = "1b_vnugH3P2JVk-8-7MmqjAC7e94jzbRt"
DRIVE_COEM_SPAIN_ID               = "1LvRFIHX1XaNDi-8QYbXgKD9aGprbKAPf"
DRIVE_CAO_COLOMBIA_ID             = "1EDcyIlAjJGRoKZaq-juiPlHkTDtgA8k_"
DRIVE_CFO_BRASIL_ID               = "1K101nLG_ULkpx81-eIYaBM-ehZny-4TT"
DRIVE_CMD_MEXICO_ID               = "1BpquqCd-87yJWr_5a8SMfuvq770bwl4K"
DRIVE_NZDA_NEWZEALAND_ID          = "137MYSex9dyGCdjAS693xE191oF6vWFM2"
DRIVE_JDA_JAPAN_ID                = "15EKeduGxGamfvkmO2qw-keEEHHe9HD5q"

# C. Guías clínicas y protocolos
DRIVE_SDCEP_SCOTLAND_ID           = "1-bulw1XqQZZix7b7ncjdxJzeQLm-vWPD"
DRIVE_NICE_ORAL_HEALTH_ID         = "1RPBWTMBGhKC1V-Nuc8GXPDfIX0k2lVl9"
DRIVE_AAPD_GUIDELINES_ID          = "175AmIQxwucBg84g_RxgLruocQ7aNYvfU"
DRIVE_AAE_ENDODONTICS_ID          = "1TkV5VixH_bJ24CvgZV8AWoNSV0nCH8kU"
DRIVE_AAP_PERIODONTICS_ID         = "1CbgUnQL60abtqU0RlwHI4vw5-VwNiW3K"
DRIVE_AAOMS_GUIDELINES_ID         = "1W4x13cykdSOGEaQofPio8Kr737VyBmJ-"
DRIVE_IADT_TRAUMA_ID              = "1ViFvNs3Les578UYmT0nD0leS5eOyv6Et"
DRIVE_EFP_EUROPE_ID               = "1iWUDadqf7VZpbgNKKcv4uxSLXSmh1O6B"
DRIVE_EAPD_EUROPE_ID              = "1XMmblCeedPd2CqEtZWs9a2fDSrTDQdfl"
DRIVE_AAO_ORTHODONTICS_ID         = "1jmKPs82RWmSKhT1ypbTN4yZ_5N7i6gJh"
DRIVE_AAOMR_RADIOLOGY_ID          = "1vqxpUOpnet1NaVRYWCThRLf9y_ncY17t"
DRIVE_AAOM_ORAL_MEDICINE_ID       = "1U_sUCNghin8Uo9BC4EeGRjfW1omTEqLT"

# D. Revistas OA
DRIVE_BMC_ORAL_HEALTH_ID          = "18Hc62UGHIzOegFamBLwiQGGWTKpcljtV"
DRIVE_MDPI_DENTISTRY_ID           = "18vbABGJlixjkTNTuOoRAD-U25w4K93vU"
DRIVE_OPEN_DENTISTRY_JOURNAL_ID   = "17mLylojrSlm-w7pBm-vFhGVsCzhoIX4b"
DRIVE_INTL_J_DENTISTRY_ID         = "1SgDNPtbT46ei8Ulrjojhtu7qqxRM9J5y"
DRIVE_FRONTIERS_DENTAL_ID         = "1JpNmj7pcjBZ9hJkLmTFVUQO0NEYcEInX"
DRIVE_BDJ_OPEN_ID                 = "1aQbpCctsrf_UiEYKXAnJuBLX6UiVrCT2"
DRIVE_EUROPEAN_J_DENTISTRY_ID     = "10BQRRqSltH-wkjC3IeiBT7KJmUWMlJU-"
DRIVE_J_DENTAL_RESEARCH_OA_ID     = "1GXR7iRBj-aVhUNOwvghT7f6x9EzKvaGD"
DRIVE_CLINICAL_ORAL_INVEST_OA_ID  = "1OROYODHnyTlFvnzD7oudAAs6QznWe6Ak"

# E. Bases de datos API
DRIVE_PUBMED_DENTAL_ID            = "1Cxdwxpq_m8q0mdCiKnoDEZvRR24WhQBe"
DRIVE_OPENALEX_DENTAL_ID          = "104dNS_yd1RrbV-GSVv83uNTNZjPvJctu"
DRIVE_CROSSREF_DENTAL_ID          = "1i8SLgP19rZCbWiI_siAJA2FWzwxGVka7"
DRIVE_DOAJ_DENTAL_ID              = "1ttjvwro4HxDUc7d54bPCSO-yENB5x2o2"
DRIVE_ZENODO_DENTAL_ID            = "1CDF1MxSoLdGcejx7kyCCAiCYI6qbOCP5"
DRIVE_SEMANTIC_SCHOLAR_DENTAL_ID  = "13SioxaI8TgC2tWNaARTlNALJtUmuup_w"
DRIVE_EUROPE_PMC_DENTAL_ID        = "16sIFuPfD9MquS3fbvouuzY6lFbJ9G-Yp"

# F. Diagnóstico y radiología oral
DRIVE_RADIOPAEDIA_DENTAL_ID       = "1W-rq38NnOGRv7sou3xVuokYw_fClYMgL"
DRIVE_CDC_ORAL_DX_ID              = "1XhEVbDgvCLbv-RKFtnkEJbUkJGV9BYXF"
DRIVE_ORAL_PATHOLOGY_ATLAS_ID     = "1G4hvz6Y079B-lXDsLzR43Q5d51yolG06"

# G. Farmacología y materiales dentales
DRIVE_DAILYMED_DENTAL_ID          = "18MUio1vDUa6_Acz8yAs-TDPkzdNh8mAY"
DRIVE_FDA_DENTAL_DEVICES_ID       = "1xEggoEZAmD65Jp_NA0_6k5OI3Oo4UWPo"
DRIVE_EUDAMED_IVD_DENTAL_ID       = "1jhGvAJmB2OUOnIK7IV77NqOdulnPcRg5"
DRIVE_INVIMA_DENTAL_COL_ID        = "10_j5Z8GzTMCYpUaHed3G3qFUzyOBgG6d"
DRIVE_COFEPRIS_DENTAL_MEX_ID      = "1ZpELkAudgllQ2hD-0YZo4Icc-1z3WGLO"

# H. Especialidades odontológicas
DRIVE_AAE_ENDO_RESOURCES_ID       = "1thFYHmkCruK1BV4QyXYNSYu07n0vvS85"
DRIVE_AAP_PERIO_RESOURCES_ID      = "1KzZASTFFR220ReNdKv8Mo2kCTeQHyejf"
DRIVE_AAO_ORTHO_RESOURCES_ID      = "18ETfLxyRvr8OWuU7OyhBCHiVsnWDcIGU"
DRIVE_ITI_IMPLANTOLOGY_ID         = "1yS6Z7D-3raPIjcFclZ21cC1shjbUf6qI"
DRIVE_EAO_IMPLANTOLOGY_ID         = "1wRhJcuzz-CvTl5arbshOlft3dUc1mSWk"
DRIVE_ACP_PROSTHODONTICS_ID       = "1H5r6nh_cMZE4ywjisjqqCt7Qq4XgbW9d"
DRIVE_AAOMFS_SURGERY_ID           = "1ooaMTyzruk2IE27hABbg8N1bU-AgJciX"
DRIVE_ESCD_COSMETIC_DENTAL_ID     = "1pWtJaUHHFHxiLvFtRp0n1gNJLNsvguel"

# I. Control de infecciones y bioseguridad
DRIVE_CDC_INFECTION_DENTAL_ID     = "16LXAM5yeR3smpT2CYuOlMXOsA4W-DUK7"
DRIVE_OSHA_DENTAL_ID              = "1kLp7kB6FM2L6ZqS6xuaewe12QuKFCBgt"
DRIVE_OSAP_DENTAL_ID              = "1VvWtTP8ooTDn35Rp6OKw-L-Nn0i-WsFf"
DRIVE_ECDC_ORAL_BIOSAFETY_ID      = "1KFxwxBD0y3osENl54atDLqbKEZNHoF_B"

# J. Codificación, facturación y gestión
DRIVE_ADA_PRACTICE_MGMT_ID        = "1xM5tTfsYE2vzElkrSrvY2HiAQGxddXNi"
DRIVE_DENTAL_ECONOMICS_ID         = "1fG-qaXw8Sj4HtW1npKgcLH0tsraSqpYe"
DRIVE_NHS_BSA_DENTAL_ID           = "1_mJRsicKRANrxSO-JaDBYE5xQap_NC8C"
DRIVE_NOM013_MEXICO_ID            = "1hlooDdPKOYvRDGk25CPXEYDw5jmsDtta"
DRIVE_RESO3100_COLOMBIA_ID        = "1hRYgJJJevI1FvQB6tHYKuQfgAIQqKauX"

# K. Educación al paciente y salud pública oral
DRIVE_MOUTHHEALTHY_ADA_ID         = "15UGMimyMKzT0GxPg7q_9NhuFCFYXKckB"
DRIVE_CDC_ORAL_PUBLIC_ID          = "1455QVQAz5zfqabhEb2Knl2OlPk2uSaAg"
DRIVE_WHO_ORAL_PUBLIC_ID          = "1Z4DR2oUrhtMUr2J7q_tfSwOLMYh4ikTi"
DRIVE_PAHO_ORAL_PUBLIC_ID         = "1g0IvtIdYN7jJhcoUy21OQdsYAYlPAFyK"
DRIVE_NHS_DENTAL_PATIENT_ID       = "15r_OzhsSW0cGUJw0FCe2zwWUQDN3q0YK"

# L. Tecnología dental y odontología digital
DRIVE_AI_DENTISTRY_PAPERS_ID      = "1gNCRxQYtUWBPK4l2AmnNc6x0csJfvmBs"
DRIVE_CBCT_RESOURCES_ID           = "1SvA1Rqo2I12Quc7vDqCY9LPgXccNp708"
DRIVE_CAD_CAM_DENTAL_ID           = "1RjipvTGtDoTfeQfr7FxiLGw__I26Z0Yp"
DRIVE_DIGITAL_WORKFLOW_DENTAL_ID  = "1tM6m97e8vvviaLjBdIXzgl3PNPVDletZ"

# M. Institutos de investigación
DRIVE_NIDCR_NIH_ID                = "1RhD5TjnVcD2sDHMI5LtWIpRVO_8PI_B2"
DRIVE_FORSYTH_INSTITUTE_ID        = "1uu3HjB_ZtOm9pn4rNXXjz4lcafr8eqgv"
DRIVE_KCL_DENTAL_ID               = "16kKW2gP3anBWaDBxgFIZGYxhvZvAqImK"
DRIVE_UCL_EASTMAN_ID              = "13y4uBpK5ulbZ7H6Pf_Nx7WxMBYsWBagj"
DRIVE_UNAM_ESTOMATOLOGIA_ID       = "1dfITW6ya0_XC-XW9gno_RN8zqRnPwFAI"
DRIVE_UAB_DENTAL_SPAIN_ID         = "1MUejON55rSC6qxV8dCXPUUKAHo75LBMs"

# N. Repositorios abiertos y preprints
DRIVE_MEDRXIV_DENTAL_ID           = "1ybtqvq9bXFdIoXmfmOd5viVtynU5CsV-"
DRIVE_OSF_DENTAL_ID               = "1iC_BemYoew7-y1EHH0kuGWJmc68qeYr3"
DRIVE_FIGSHARE_DENTAL_ID          = "1Xrr0nvigLEfMnBbLEPe4YplOZj4Lwjxi"
DRIVE_EUROPE_PMC_DENTAL_REPO_ID   = "1P_LjucevQpb4YVtZmw3ErctntO8vpmEd"

PROGRESS_FILE = "progress_dental.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; DentalOSBot/1.0; research use)",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
}

# ── Autenticación Google Drive ─────────────────────────────────────────────────

def get_drive_service():
    with open("token.json") as f:
        d = json.load(f)
    creds = Credentials(
        token=d["token"], refresh_token=d["refresh_token"],
        token_uri=d["token_uri"], client_id=d["client_id"],
        client_secret=d["client_secret"], scopes=d["scopes"],
    )
    return build("drive", "v3", credentials=creds)


def folder_for_url(url):
    # A. Organismos internacionales
    if "fdiworlddental.org"        in url: return DRIVE_FDI_WORLD_DENTAL_ID
    if "who.int" in url and "oral" in url: return DRIVE_WHO_ORAL_HEALTH_ID
    if "paho.org" in url and "oral" in url: return DRIVE_PAHO_ORAL_HEALTH_ID
    if "iapd.org"                  in url: return DRIVE_IAPD_INTERNATIONAL_ID
    # B. Asociaciones nacionales
    if "ada.org"                   in url: return DRIVE_ADA_USA_ID
    if "bda.org"                   in url: return DRIVE_BDA_UK_ID
    if "cda-adc.ca"                in url: return DRIVE_CDA_CANADA_ID
    if "ada.org.au"                in url: return DRIVE_ADC_AUSTRALIA_ID
    if "seoc.es"                   in url: return DRIVE_SEOC_SPAIN_ID
    if "coem.org.es"               in url: return DRIVE_COEM_SPAIN_ID
    if "cao.org.co"                in url: return DRIVE_CAO_COLOMBIA_ID
    if "cfo.org.br"                in url: return DRIVE_CFO_BRASIL_ID
    if "cmd.org.mx"                in url: return DRIVE_CMD_MEXICO_ID
    if "nzda.org.nz"               in url: return DRIVE_NZDA_NEWZEALAND_ID
    if "jda.or.jp"                 in url: return DRIVE_JDA_JAPAN_ID
    # C. Guías clínicas
    if "sdcep.org.uk"              in url: return DRIVE_SDCEP_SCOTLAND_ID
    if "nice.org.uk" in url and "oral" in url: return DRIVE_NICE_ORAL_HEALTH_ID
    if "aapd.org"                  in url: return DRIVE_AAPD_GUIDELINES_ID
    if "aae.org"                   in url: return DRIVE_AAE_ENDODONTICS_ID
    if "perio.org"                 in url: return DRIVE_AAP_PERIODONTICS_ID
    if "aaoms.org"                 in url: return DRIVE_AAOMS_GUIDELINES_ID
    if "iadt-dentaltrauma.org"     in url: return DRIVE_IADT_TRAUMA_ID
    if "efp.org"                   in url: return DRIVE_EFP_EUROPE_ID
    if "eapd.gr"                   in url: return DRIVE_EAPD_EUROPE_ID
    if "aaoinfo.org"               in url: return DRIVE_AAO_ORTHODONTICS_ID
    if "aaomr.org"                 in url: return DRIVE_AAOMR_RADIOLOGY_ID
    if "aaom.com"                  in url: return DRIVE_AAOM_ORAL_MEDICINE_ID
    # D. Revistas OA
    if "bmcoralhealth"             in url: return DRIVE_BMC_ORAL_HEALTH_ID
    if "mdpi.com" in url and "dentistry" in url: return DRIVE_MDPI_DENTISTRY_ID
    if "benthamopen.com" in url and "dental" in url: return DRIVE_OPEN_DENTISTRY_JOURNAL_ID
    if "hindawi.com/journals/ijd"  in url: return DRIVE_INTL_J_DENTISTRY_ID
    if "frontiersin.org" in url and ("dental" in url or "dentistry" in url): return DRIVE_FRONTIERS_DENTAL_ID
    if "nature.com/bdjo"           in url: return DRIVE_BDJ_OPEN_ID
    if "thieme-connect.com" in url and "dental" in url: return DRIVE_EUROPEAN_J_DENTISTRY_ID
    if "journals.sagepub.com" in url and "jdr" in url: return DRIVE_J_DENTAL_RESEARCH_OA_ID
    if "link.springer.com/journal/784" in url: return DRIVE_CLINICAL_ORAL_INVEST_OA_ID
    # E. Bases de datos API (inline)
    if "|PUBMED_DENTAL|"           in url: return DRIVE_PUBMED_DENTAL_ID
    if "|OPENALEX_DENTAL|"         in url: return DRIVE_OPENALEX_DENTAL_ID
    if "|CROSSREF_DENTAL|"         in url: return DRIVE_CROSSREF_DENTAL_ID
    if "|DOAJ_DENTAL|"             in url: return DRIVE_DOAJ_DENTAL_ID
    if "|ZENODO_DENTAL|"           in url: return DRIVE_ZENODO_DENTAL_ID
    if "|S2_DENTAL|"               in url: return DRIVE_SEMANTIC_SCHOLAR_DENTAL_ID
    if "|EUROPEPMC_DENTAL|"        in url: return DRIVE_EUROPE_PMC_DENTAL_ID
    if "pubmed.ncbi.nlm.nih.gov"   in url: return DRIVE_PUBMED_DENTAL_ID
    if "europepmc.org"             in url: return DRIVE_EUROPE_PMC_DENTAL_ID
    # F. Diagnóstico y radiología
    if "radiopaedia.org" in url and ("dental" in url or "tooth" in url or "oral" in url or "jaw" in url): return DRIVE_RADIOPAEDIA_DENTAL_ID
    if "cdc.gov" in url and "oralhealth" in url: return DRIVE_CDC_ORAL_DX_ID
    if "atlasofpathology" in url or "pathologyoutlines.com" in url: return DRIVE_ORAL_PATHOLOGY_ATLAS_ID
    # G. Farmacología y materiales
    if "dailymed.nlm.nih.gov"      in url: return DRIVE_DAILYMED_DENTAL_ID
    if "fda.gov" in url and "dental" in url: return DRIVE_FDA_DENTAL_DEVICES_ID
    if "eudamed.ec.europa.eu"      in url: return DRIVE_EUDAMED_IVD_DENTAL_ID
    if "invima.gov.co"             in url: return DRIVE_INVIMA_DENTAL_COL_ID
    if "cofepris.gob.mx"           in url: return DRIVE_COFEPRIS_DENTAL_MEX_ID
    # H. Especialidades
    if "aae.org/dental-professionals" in url: return DRIVE_AAE_ENDO_RESOURCES_ID
    if "perio.org/clinical"        in url: return DRIVE_AAP_PERIO_RESOURCES_ID
    if "aaoinfo.org/research"      in url: return DRIVE_AAO_ORTHO_RESOURCES_ID
    if "iti.org"                   in url: return DRIVE_ITI_IMPLANTOLOGY_ID
    if "eao.org"                   in url: return DRIVE_EAO_IMPLANTOLOGY_ID
    if "prosthodontics.org"        in url: return DRIVE_ACP_PROSTHODONTICS_ID
    if "aaoms.org/education"       in url: return DRIVE_AAOMFS_SURGERY_ID
    if "escd.org"                  in url: return DRIVE_ESCD_COSMETIC_DENTAL_ID
    # I. Control de infecciones
    if "cdc.gov" in url and "infectioncontrol" in url: return DRIVE_CDC_INFECTION_DENTAL_ID
    if "osha.gov" in url and "dental" in url: return DRIVE_OSHA_DENTAL_ID
    if "osap.org"                  in url: return DRIVE_OSAP_DENTAL_ID
    if "ecdc.europa.eu"            in url: return DRIVE_ECDC_ORAL_BIOSAFETY_ID
    # J. Gestión y codificación
    if "ada.org/resources/practice" in url: return DRIVE_ADA_PRACTICE_MGMT_ID
    if "dentaleconomics.com"       in url: return DRIVE_DENTAL_ECONOMICS_ID
    if "nhsbsa.nhs.uk/dental"      in url: return DRIVE_NHS_BSA_DENTAL_ID
    if "dof.gob.mx" in url and "NOM-013" in url: return DRIVE_NOM013_MEXICO_ID
    if "minsalud.gov.co" in url and "3100" in url: return DRIVE_RESO3100_COLOMBIA_ID
    # K. Educación al paciente
    if "mouthhealthy.org"          in url: return DRIVE_MOUTHHEALTHY_ADA_ID
    if "cdc.gov/oralhealth"        in url: return DRIVE_CDC_ORAL_PUBLIC_ID
    if "who.int" in url and ("oral" in url or "dental" in url): return DRIVE_WHO_ORAL_PUBLIC_ID
    if "paho.org"                  in url: return DRIVE_PAHO_ORAL_PUBLIC_ID
    if "nhs.uk" in url and "dental" in url: return DRIVE_NHS_DENTAL_PATIENT_ID
    # L. Tecnología dental
    if "frontiersin.org" in url and "ai" in url and "dent" in url: return DRIVE_AI_DENTISTRY_PAPERS_ID
    if "aaomr.org/cbct"            in url: return DRIVE_CBCT_RESOURCES_ID
    if "exocad.com" in url or "3shape.com" in url or "cadcam" in url: return DRIVE_CAD_CAM_DENTAL_ID
    # M. Institutos
    if "nidcr.nih.gov"             in url: return DRIVE_NIDCR_NIH_ID
    if "forsyth.org"               in url: return DRIVE_FORSYTH_INSTITUTE_ID
    if "kcl.ac.uk" in url and "dental" in url: return DRIVE_KCL_DENTAL_ID
    if "ucl.ac.uk" in url and "eastman" in url: return DRIVE_UCL_EASTMAN_ID
    if "unam.mx" in url and ("estomato" in url or "dental" in url): return DRIVE_UNAM_ESTOMATOLOGIA_ID
    if "uab.cat" in url and "dental" in url: return DRIVE_UAB_DENTAL_SPAIN_ID
    # N. Repositorios
    if "medrxiv.org"               in url: return DRIVE_MEDRXIV_DENTAL_ID
    if "osf.io"                    in url: return DRIVE_OSF_DENTAL_ID
    if "figshare.com"              in url: return DRIVE_FIGSHARE_DENTAL_ID
    return DRIVE_BMC_ORAL_HEALTH_ID  # fallback


def upload_file(service, url, name, content):
    folder_id = folder_for_url(url)
    media = MediaInMemoryUpload(content.encode("utf-8"), mimetype="text/plain")
    service.files().create(
        body={"name": name, "parents": [folder_id]},
        media_body=media, fields="id"
    ).execute()


# ── Helpers ────────────────────────────────────────────────────────────────────

def fetch_urls_from_sitemap(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code == 429 or not r.ok:
            return []
        root = ET.fromstring(r.text)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        return [el.text for el in root.findall(".//sm:loc", ns) if el.text]
    except ET.ParseError:
        return re.findall(r"<loc>\s*(https?://[^<\s]+)\s*</loc>", r.text)
    except Exception:
        return []


def _fetch_sitemap_index_urls(index_url, url_filter=None, delay=0.5):
    sub_sitemaps = fetch_urls_from_sitemap(index_url)
    all_urls = []
    for sm in sub_sitemaps:
        urls = fetch_urls_from_sitemap(sm)
        if url_filter:
            urls = [u for u in urls if url_filter(u)]
        all_urls.extend(urls)
        time.sleep(delay)
    return all_urls


def _crawl_one_level(seed, domain_prefix, delay=2.0):
    try:
        r = requests.get(seed, headers=HEADERS, timeout=30)
        if not r.ok:
            return []
        soup = BeautifulSoup(r.text, "html.parser")
        urls = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("/"):
                from urllib.parse import urljoin
                href = urljoin(seed, href)
            if domain_prefix in href and href.startswith("http"):
                urls.add(href)
        time.sleep(delay)
        return list(urls)
    except Exception:
        return []


def extract_inline_content(inline_str):
    try:
        url_part, rtype, json_str = inline_str.split("|", 2)
        data = json.loads(json_str)
        title = data.get("title", "Untitled")
        doi = data.get("doi", "")
        abstract = data.get("abstract", "")
        return (f"{title}\n{'='*len(title)}\n\n"
                f"URL: {url_part}\nDOI: {doi}\nType: {rtype}\n\n{abstract}").strip()
    except Exception:
        return inline_str


# ── Fetchers ───────────────────────────────────────────────────────────────────

# A. Organismos internacionales
def fetch_fdi_urls():
    return _crawl_one_level("https://www.fdiworlddental.org/oral-health", "fdiworlddental.org", delay=3.0)

def fetch_who_oral_urls():
    return _crawl_one_level("https://www.who.int/health-topics/oral-health", "who.int", delay=3.0)

def fetch_paho_oral_urls():
    return _crawl_one_level("https://www.paho.org/en/topics/oral-health", "paho.org", delay=3.0)

def fetch_iapd_urls():
    return _crawl_one_level("https://www.iapd.org/resources", "iapd.org", delay=3.0)

# B. Asociaciones nacionales
def fetch_ada_usa_urls():
    return _fetch_sitemap_index_urls(
        "https://www.ada.org/sitemap.xml",
        url_filter=lambda u: any(k in u for k in ["oral-health-topics", "resources", "news", "publications", "education"]),
        delay=2.0)

def fetch_bda_uk_urls():
    return _crawl_one_level("https://www.bda.org/advice", "bda.org", delay=3.0)

def fetch_cda_canada_urls():
    return _crawl_one_level("https://www.cda-adc.ca/en/oral_health/", "cda-adc.ca", delay=3.0)

def fetch_adc_australia_urls():
    return _crawl_one_level("https://www.ada.org.au/Dental-Professionals/Clinical-Resources", "ada.org.au", delay=3.0)

def fetch_seoc_spain_urls():
    return _crawl_one_level("https://www.seoc.es/publicaciones/", "seoc.es", delay=3.0)

def fetch_coem_spain_urls():
    return _crawl_one_level("https://www.coem.org.es/pacientes/", "coem.org.es", delay=3.0)

def fetch_cfo_brasil_urls():
    return _crawl_one_level("https://cfo.org.br/resolucoes/", "cfo.org.br", delay=3.0)

def fetch_cmd_mexico_urls():
    return _crawl_one_level("https://www.cmd.org.mx/publicaciones/", "cmd.org.mx", delay=3.0)

def fetch_nzda_urls():
    return _crawl_one_level("https://www.nzda.org.nz/dentists/clinical-resources/", "nzda.org.nz", delay=3.0)

# C. Guías clínicas
def fetch_sdcep_urls():
    return _crawl_one_level("https://www.sdcep.org.uk/published-guidance/", "sdcep.org.uk", delay=2.0)

def fetch_nice_oral_urls():
    return _fetch_sitemap_index_urls(
        "https://www.nice.org.uk/sitemap.xml",
        url_filter=lambda u: "oral" in u or "dental" in u,
        delay=1.5)

def fetch_aapd_guidelines_urls():
    return _crawl_one_level(
        "https://www.aapd.org/research/oral-health-policies--recommendations/",
        "aapd.org", delay=3.0)

def fetch_aae_urls():
    return _crawl_one_level("https://www.aae.org/dental-professionals/treatment-guidelines/", "aae.org", delay=3.0)

def fetch_aap_perio_urls():
    return _crawl_one_level("https://www.perio.org/clinical-guidance/", "perio.org", delay=3.0)

def fetch_aaoms_urls():
    return _crawl_one_level("https://www.aaoms.org/dental-professionals/clinical-resources/", "aaoms.org", delay=3.0)

def fetch_iadt_urls():
    return _crawl_one_level("https://www.iadt-dentaltrauma.org/professional-resources/", "iadt-dentaltrauma.org", delay=3.0)

def fetch_efp_urls():
    return _crawl_one_level("https://www.efp.org/publications/", "efp.org", delay=3.0)

def fetch_eapd_urls():
    return _crawl_one_level("https://www.eapd.gr/publications/", "eapd.gr", delay=3.0)

def fetch_aao_ortho_urls():
    return _crawl_one_level("https://www.aaoinfo.org/research/", "aaoinfo.org", delay=3.0)

def fetch_aaomr_urls():
    return _crawl_one_level("https://www.aaomr.org/resources", "aaomr.org", delay=3.0)

def fetch_aaom_urls():
    return _crawl_one_level("https://www.aaom.com/resources", "aaom.com", delay=3.0)

# D. Revistas OA
def fetch_bmc_oral_health_urls():
    return _fetch_sitemap_index_urls(
        "https://bmcoralhealth.biomedcentral.com/sitemap.xml",
        url_filter=lambda u: "article" in u, delay=1.0)

def fetch_mdpi_dentistry_urls():
    return _fetch_sitemap_index_urls(
        "https://www.mdpi.com/sitemap/sitemap-dentistry.xml",
        url_filter=lambda u: "/dentistry/" in u and "/article" in u,
        delay=1.0)

def fetch_open_dentistry_journal_urls():
    return _crawl_one_level(
        "https://www.benthamopen.com/TODENTJ/home/",
        "benthamopen.com", delay=2.0)

def fetch_intl_j_dentistry_urls():
    return _fetch_sitemap_index_urls(
        "https://www.hindawi.com/sitemap.xml",
        url_filter=lambda u: "ijd" in u and "article" in u,
        delay=1.0)

def fetch_frontiers_dental_urls():
    return _fetch_sitemap_index_urls(
        "https://www.frontiersin.org/sitemap.xml",
        url_filter=lambda u: ("dental" in u or "dentistry" in u) and "article" in u,
        delay=1.0)

def fetch_bdj_open_urls():
    return _fetch_sitemap_index_urls(
        "https://www.nature.com/sitemap.xml",
        url_filter=lambda u: "bdjo" in u and "article" in u,
        delay=1.5)

# E. Bases de datos API (inline records)
def fetch_pubmed_dental_urls():
    """PubMed E-utilities — artículos de odontología por MeSH."""
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    dental_queries = [
        '"dentistry"[MeSH] OR "oral health"[MeSH]',
        '"endodontics"[MeSH] OR "root canal therapy"[MeSH]',
        '"periodontal diseases"[MeSH] OR "periodontics"[MeSH]',
        '"orthodontics"[MeSH] OR "malocclusion"[MeSH]',
        '"dental implants"[MeSH] OR "dental prosthesis"[MeSH]',
        '"tooth diseases"[MeSH] OR "dental caries"[MeSH]',
        '"oral surgery"[MeSH] OR "tooth extraction"[MeSH]',
        '"pediatric dentistry"[MeSH] OR "child dental health"[MeSH]',
    ]
    all_urls = []
    for query in dental_queries:
        try:
            r = requests.get(base, params={
                "db": "pubmed", "term": query,
                "retmax": 500, "retmode": "json", "usehistory": "y",
            }, headers=HEADERS, timeout=30)
            ids = r.json()["esearchresult"]["idlist"]
            all_urls += [f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" for pmid in ids]
            time.sleep(1.0)
        except Exception:
            pass
    return all_urls

def fetch_openalex_dental_urls():
    try:
        r = requests.get(
            "https://api.openalex.org/works",
            params={"filter": "concepts.display_name.search:dentistry",
                    "per-page": 200, "select": "id,doi,title,abstract_inverted_index"},
            headers=HEADERS, timeout=30)
        works = r.json().get("results", [])
        urls = []
        for w in works:
            doi = w.get("doi", "")
            title = w.get("title", "")
            wid = w.get("id", "").split("/")[-1]
            urls.append(f"https://openalex.org/works/{wid}|OPENALEX_DENTAL|{json.dumps({'title': title, 'doi': doi})}")
        return urls
    except Exception:
        return []

def fetch_crossref_dental_urls():
    try:
        r = requests.get(
            "https://api.crossref.org/works",
            params={"query": "dental oral health dentistry treatment", "rows": 150},
            headers=HEADERS, timeout=30)
        items = r.json().get("message", {}).get("items", [])
        urls = []
        for it in items:
            doi = it.get("DOI", "")
            title = (it.get("title") or [""])[0]
            urls.append(f"https://doi.org/{doi}|CROSSREF_DENTAL|{json.dumps({'title': title, 'doi': doi})}")
        return urls
    except Exception:
        return []

def fetch_doaj_dental_urls():
    try:
        r = requests.get(
            "https://doaj.org/api/search/articles/dental+oral+health",
            params={"pageSize": 100},
            headers=HEADERS, timeout=30)
        results = r.json().get("results", [])
        urls = []
        for it in results:
            bib = it.get("bibjson", {})
            title = bib.get("title", "")
            doi = (bib.get("identifier") or [{}])[0].get("id", "")
            aid = it.get("id", "")
            urls.append(f"https://doaj.org/article/{aid}|DOAJ_DENTAL|{json.dumps({'title': title, 'doi': doi})}")
        return urls
    except Exception:
        return []

def fetch_zenodo_dental_urls():
    try:
        r = requests.get(
            "https://zenodo.org/api/records/",
            params={"q": "dentistry oral health dental", "size": 100},
            headers=HEADERS, timeout=30)
        hits = r.json().get("hits", {}).get("hits", [])
        urls = []
        for h in hits:
            doi = h.get("doi", "")
            title = h.get("metadata", {}).get("title", "")
            rid = h.get("id", "")
            urls.append(f"https://zenodo.org/record/{rid}|ZENODO_DENTAL|{json.dumps({'title': title, 'doi': doi})}")
        return urls
    except Exception:
        return []

def fetch_semantic_scholar_dental_urls():
    try:
        r = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params={"query": "dental oral health dentistry treatment",
                    "limit": 100, "fields": "title,externalIds,year,abstract"},
            headers=HEADERS, timeout=30)
        papers = r.json().get("data", [])
        urls = []
        for p in papers:
            title = p.get("title", "")
            doi = p.get("externalIds", {}).get("DOI", "")
            abstract = p.get("abstract", "")
            pid = p.get("paperId", "")
            urls.append(f"https://www.semanticscholar.org/paper/{pid}|S2_DENTAL|{json.dumps({'title': title, 'doi': doi, 'abstract': abstract[:500]})}")
        return urls
    except Exception:
        return []

def fetch_europe_pmc_dental_urls():
    try:
        r = requests.get(
            "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
            params={"query": "dentistry oral health MeSH:D003786", "format": "json",
                    "pageSize": 200, "resultType": "lite"},
            headers=HEADERS, timeout=30)
        results = r.json().get("resultList", {}).get("result", [])
        urls = []
        for it in results:
            pmid = it.get("pmid", "")
            title = it.get("title", "")
            doi = it.get("doi", "")
            urls.append(f"https://europepmc.org/article/MED/{pmid}|EUROPEPMC_DENTAL|{json.dumps({'title': title, 'doi': doi})}")
        return urls
    except Exception:
        return []

# F. Diagnóstico y radiología oral
def fetch_radiopaedia_dental_urls():
    seeds = [
        "https://radiopaedia.org/articles/dental-caries",
        "https://radiopaedia.org/articles/periapical-abscess",
        "https://radiopaedia.org/articles/oral-cavity",
        "https://radiopaedia.org/articles/mandible-anatomy",
    ]
    urls = []
    for seed in seeds:
        urls += _crawl_one_level(seed, "radiopaedia.org", delay=2.0)
    return urls

def fetch_cdc_oral_dx_urls():
    return _crawl_one_level("https://www.cdc.gov/oralhealth/", "cdc.gov/oralhealth", delay=2.0)

def fetch_oral_pathology_atlas_urls():
    urls = _crawl_one_level("https://www.pathologyoutlines.com/oralcavity.html", "pathologyoutlines.com", delay=2.0)
    return urls

# G. Farmacología y materiales dentales
def fetch_dailymed_dental_urls():
    try:
        r = requests.get(
            "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json",
            params={"drug_name": "lidocaine dental", "pagesize": 100},
            headers=HEADERS, timeout=30)
        items = r.json().get("data", [])
        urls = []
        for it in items:
            setid = it.get("setid", "")
            title = it.get("title", "")
            urls.append(f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={setid}|DAILYMED_DENTAL|{json.dumps({'title': title})}")
        return urls
    except Exception:
        return _crawl_one_level("https://dailymed.nlm.nih.gov/dailymed/search.cfm?query=dental", "dailymed.nlm.nih.gov", delay=2.0)

def fetch_fda_dental_devices_urls():
    return _crawl_one_level("https://www.fda.gov/medical-devices/dental-devices", "fda.gov/medical-devices/dental", delay=2.0)

def fetch_cofepris_dental_urls():
    return _crawl_one_level("https://www.gob.mx/cofepris/acciones-y-programas/dispositivos-medicos", "cofepris.gob.mx", delay=3.0)

def fetch_invima_dental_urls():
    return _crawl_one_level("https://www.invima.gov.co/dispositivos-medicos/", "invima.gov.co", delay=3.0)

# H. Especialidades
def fetch_iti_implantology_urls():
    return _crawl_one_level("https://www.iti.org/academy/online-education/", "iti.org", delay=3.0)

def fetch_eao_implantology_urls():
    return _crawl_one_level("https://www.eao.org/publications/", "eao.org", delay=3.0)

def fetch_acp_prosthodontics_urls():
    return _crawl_one_level("https://www.prosthodontics.org/resources/", "prosthodontics.org", delay=3.0)

def fetch_escd_urls():
    return _crawl_one_level("https://www.escd.org/education/", "escd.org", delay=3.0)

# I. Control de infecciones
def fetch_cdc_infection_dental_urls():
    return _crawl_one_level(
        "https://www.cdc.gov/oralhealth/infectioncontrol/",
        "cdc.gov/oralhealth/infectioncontrol", delay=2.0)

def fetch_osha_dental_urls():
    return _crawl_one_level("https://www.osha.gov/dental/", "osha.gov/dental", delay=2.0)

def fetch_osap_dental_urls():
    return _crawl_one_level("https://www.osap.org/resources/", "osap.org", delay=3.0)

# J. Gestión y codificación
def fetch_ada_practice_mgmt_urls():
    return _crawl_one_level("https://www.ada.org/resources/practice/practice-management", "ada.org/resources/practice", delay=2.0)

def fetch_dental_economics_urls():
    return _fetch_sitemap_index_urls(
        "https://www.dentaleconomics.com/sitemap.xml",
        url_filter=lambda u: any(k in u for k in ["/practice-management/", "/clinical/", "/products/"]),
        delay=1.5)

def fetch_nhs_bsa_dental_urls():
    return _crawl_one_level("https://www.nhsbsa.nhs.uk/dental-services", "nhsbsa.nhs.uk/dental", delay=2.0)

def fetch_nom013_mexico_urls():
    urls = _crawl_one_level("https://www.dof.gob.mx/busqueda_detalle.php?codigo=NOM-013", "dof.gob.mx", delay=3.0)
    urls += _crawl_one_level("https://www.gob.mx/salud/articulos/normas-oficiales-mexicanas-de-salud-bucal", "gob.mx/salud", delay=3.0)
    return urls

# K. Educación al paciente y salud pública
def fetch_mouthhealthy_urls():
    return _fetch_sitemap_index_urls(
        "https://www.mouthhealthy.org/sitemap.xml",
        url_filter=lambda u: any(k in u for k in ["all-topics", "az-topics", "adults", "teens", "babies"]),
        delay=1.5)

def fetch_cdc_oral_public_urls():
    return _crawl_one_level("https://www.cdc.gov/oralhealth/basics/", "cdc.gov/oralhealth", delay=2.0)

def fetch_who_oral_public_urls():
    return _crawl_one_level("https://www.who.int/news-room/fact-sheets/detail/oral-health", "who.int", delay=3.0)

def fetch_paho_oral_public_urls():
    return _crawl_one_level("https://www.paho.org/en/topics/oral-health", "paho.org", delay=3.0)

def fetch_nhs_dental_patient_urls():
    return _fetch_sitemap_index_urls(
        "https://www.nhs.uk/sitemap.xml",
        url_filter=lambda u: "dental" in u or "teeth" in u or "oral" in u,
        delay=1.5)

# L. Tecnología dental
def fetch_ai_dentistry_urls():
    try:
        r = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params={"query": "artificial intelligence deep learning dental diagnosis",
                    "limit": 100, "fields": "title,externalIds,abstract"},
            headers=HEADERS, timeout=30)
        papers = r.json().get("data", [])
        urls = []
        for p in papers:
            title = p.get("title", "")
            doi = p.get("externalIds", {}).get("DOI", "")
            abstract = p.get("abstract", "")
            pid = p.get("paperId", "")
            urls.append(f"https://www.semanticscholar.org/paper/{pid}|S2_DENTAL|{json.dumps({'title': title, 'doi': doi, 'abstract': abstract[:500]})}")
        return urls
    except Exception:
        return []

def fetch_cbct_resources_urls():
    urls = _crawl_one_level("https://www.aaomr.org/resources/cbct", "aaomr.org", delay=2.0)
    urls += _crawl_one_level("https://www.efp.org/publications/position-papers/", "efp.org", delay=3.0)
    return urls

def fetch_cad_cam_dental_urls():
    return _crawl_one_level("https://www.jdentaled.org/topic/cad-cam", "jdentaled.org", delay=2.0)

def fetch_digital_workflow_dental_urls():
    try:
        r = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params={"query": "digital workflow dentistry CAD CAM intraoral scanner",
                    "limit": 80, "fields": "title,externalIds,abstract"},
            headers=HEADERS, timeout=30)
        papers = r.json().get("data", [])
        urls = []
        for p in papers:
            title = p.get("title", "")
            doi = p.get("externalIds", {}).get("DOI", "")
            abstract = p.get("abstract", "")
            pid = p.get("paperId", "")
            urls.append(f"https://www.semanticscholar.org/paper/{pid}|S2_DENTAL|{json.dumps({'title': title, 'doi': doi, 'abstract': abstract[:500]})}")
        return urls
    except Exception:
        return []

# M. Institutos de investigación
def fetch_nidcr_urls():
    return _fetch_sitemap_index_urls(
        "https://www.nidcr.nih.gov/sitemap.xml",
        url_filter=lambda u: any(k in u for k in ["research", "health-info", "grants", "news"]),
        delay=1.5)

def fetch_forsyth_urls():
    return _crawl_one_level("https://www.forsyth.org/research/", "forsyth.org", delay=3.0)

def fetch_kcl_dental_urls():
    return _crawl_one_level("https://www.kcl.ac.uk/dentistry/research", "kcl.ac.uk/dentistry", delay=2.0)

def fetch_ucl_eastman_urls():
    return _crawl_one_level("https://www.ucl.ac.uk/eastman/research/", "ucl.ac.uk/eastman", delay=2.0)

def fetch_unam_estomatologia_urls():
    return _crawl_one_level("https://www.feo.unam.mx/investigacion/", "unam.mx", delay=3.0)

# N. Repositorios OA y preprints
def fetch_medrxiv_dental_urls():
    try:
        r = requests.get(
            "https://api.biorxiv.org/details/medrxiv/dentistry/0/100",
            headers=HEADERS, timeout=30)
        data = r.json().get("collection", [])
        urls = []
        for it in data:
            doi = it.get("doi", "")
            title = it.get("title", "")
            abstract = it.get("abstract", "")
            urls.append(f"https://www.medrxiv.org/content/{doi}v1|MEDRXIV_DENTAL|{json.dumps({'title': title, 'doi': doi, 'abstract': abstract[:500]})}")
        return urls
    except Exception:
        return _crawl_one_level("https://www.medrxiv.org/collection/dentistry", "medrxiv.org", delay=2.0)

def fetch_osf_dental_urls():
    try:
        r = requests.get("https://osf.io/api/v2/nodes/",
            params={"filter[tags]": "dentistry", "page[size]": 100},
            headers=HEADERS, timeout=30)
        data = r.json().get("data", [])
        urls = []
        for item in data:
            attrs = item.get("attributes", {})
            title = attrs.get("title", "")
            nid = item.get("id", "")
            urls.append(f"https://osf.io/{nid}/|OSF_DENTAL|{json.dumps({'title': title})}")
        return urls
    except Exception:
        return []

def fetch_figshare_dental_urls():
    try:
        r = requests.get(
            "https://api.figshare.com/v2/articles/search",
            json={"search_for": "dental oral health dentistry", "page_size": 100},
            headers=HEADERS, timeout=30)
        items = r.json()
        urls = []
        for it in items:
            title = it.get("title", "")
            doi = it.get("doi", "")
            aid = it.get("id", "")
            urls.append(f"https://figshare.com/articles/{aid}|FIGSHARE_DENTAL|{json.dumps({'title': title, 'doi': doi})}")
        return urls
    except Exception:
        return []


# ── Carga uniforme ─────────────────────────────────────────────────────────────

def _load_source(name, sitemaps=None, fn=None):
    print(f"Cargando {name}...", flush=True)
    urls = []
    if sitemaps:
        for sm in sitemaps:
            try:
                found = fetch_urls_from_sitemap(sm)
                print(f"  {sm.split('/')[-1]}: {len(found)} URLs", flush=True)
                urls.extend(found)
            except Exception as e:
                print(f"  ERROR {sm}: {e}", flush=True)
    if fn:
        try:
            found = fn()
            print(f"  → {len(found)} URLs", flush=True)
            urls.extend(found)
        except Exception as e:
            print(f"  ERROR: {e}", flush=True)
    return urls


def get_all_urls():
    all_urls = []

    # A. Organismos internacionales
    all_urls += _load_source("FDI World Dental",          fn=fetch_fdi_urls)
    all_urls += _load_source("WHO Oral Health",           fn=fetch_who_oral_urls)
    all_urls += _load_source("PAHO Oral Health",          fn=fetch_paho_oral_urls)
    all_urls += _load_source("IAPD International",        fn=fetch_iapd_urls)

    # B. Asociaciones nacionales
    all_urls += _load_source("ADA USA",                   fn=fetch_ada_usa_urls)
    all_urls += _load_source("BDA UK",                    fn=fetch_bda_uk_urls)
    all_urls += _load_source("CDA Canada",                fn=fetch_cda_canada_urls)
    all_urls += _load_source("ADC Australia",             fn=fetch_adc_australia_urls)
    all_urls += _load_source("SEOC Spain",                fn=fetch_seoc_spain_urls)
    all_urls += _load_source("COEM Spain",                fn=fetch_coem_spain_urls)
    all_urls += _load_source("CFO Brasil",                fn=fetch_cfo_brasil_urls)
    all_urls += _load_source("CMD Mexico",                fn=fetch_cmd_mexico_urls)
    all_urls += _load_source("NZDA New Zealand",          fn=fetch_nzda_urls)

    # C. Guías clínicas y protocolos
    all_urls += _load_source("SDCEP Scotland",            fn=fetch_sdcep_urls)
    all_urls += _load_source("NICE Oral Health",          fn=fetch_nice_oral_urls)
    all_urls += _load_source("AAPD Guidelines",           fn=fetch_aapd_guidelines_urls)
    all_urls += _load_source("AAE Endodontics",           fn=fetch_aae_urls)
    all_urls += _load_source("AAP Periodontics",          fn=fetch_aap_perio_urls)
    all_urls += _load_source("AAOMS Guidelines",          fn=fetch_aaoms_urls)
    all_urls += _load_source("IADT Trauma",               fn=fetch_iadt_urls)
    all_urls += _load_source("EFP Europe Perio",          fn=fetch_efp_urls)
    all_urls += _load_source("EAPD Europe Pedo",          fn=fetch_eapd_urls)
    all_urls += _load_source("AAO Orthodontics",          fn=fetch_aao_ortho_urls)
    all_urls += _load_source("AAOMR Radiology",           fn=fetch_aaomr_urls)
    all_urls += _load_source("AAOM Oral Medicine",        fn=fetch_aaom_urls)

    # D. Revistas OA
    all_urls += _load_source("BMC Oral Health",           fn=fetch_bmc_oral_health_urls)
    all_urls += _load_source("MDPI Dentistry",            fn=fetch_mdpi_dentistry_urls)
    all_urls += _load_source("Open Dentistry Journal",    fn=fetch_open_dentistry_journal_urls)
    all_urls += _load_source("Intl J Dentistry (Hindawi)",fn=fetch_intl_j_dentistry_urls)
    all_urls += _load_source("Frontiers Dental Medicine", fn=fetch_frontiers_dental_urls)
    all_urls += _load_source("BDJ Open",                  fn=fetch_bdj_open_urls)

    # E. Bases de datos API
    all_urls += _load_source("PubMed Dental (MeSH)",      fn=fetch_pubmed_dental_urls)
    all_urls += _load_source("OpenAlex Dental",           fn=fetch_openalex_dental_urls)
    all_urls += _load_source("Crossref Dental",           fn=fetch_crossref_dental_urls)
    all_urls += _load_source("DOAJ Dental",               fn=fetch_doaj_dental_urls)
    all_urls += _load_source("Zenodo Dental",             fn=fetch_zenodo_dental_urls)
    all_urls += _load_source("Semantic Scholar Dental",   fn=fetch_semantic_scholar_dental_urls)
    all_urls += _load_source("Europe PMC Dental",         fn=fetch_europe_pmc_dental_urls)

    # F. Diagnóstico y radiología oral
    all_urls += _load_source("Radiopaedia Dental",        fn=fetch_radiopaedia_dental_urls)
    all_urls += _load_source("CDC Oral DX",               fn=fetch_cdc_oral_dx_urls)
    all_urls += _load_source("Oral Pathology Atlas",      fn=fetch_oral_pathology_atlas_urls)

    # G. Farmacología y materiales dentales
    all_urls += _load_source("DailyMed Dental",           fn=fetch_dailymed_dental_urls)
    all_urls += _load_source("FDA Dental Devices",        fn=fetch_fda_dental_devices_urls)
    all_urls += _load_source("COFEPRIS Dental",           fn=fetch_cofepris_dental_urls)
    all_urls += _load_source("INVIMA Dental",             fn=fetch_invima_dental_urls)

    # H. Especialidades
    all_urls += _load_source("ITI Implantology",          fn=fetch_iti_implantology_urls)
    all_urls += _load_source("EAO Implantology",          fn=fetch_eao_implantology_urls)
    all_urls += _load_source("ACP Prosthodontics",        fn=fetch_acp_prosthodontics_urls)
    all_urls += _load_source("ESCD Cosmetic Dental",      fn=fetch_escd_urls)

    # I. Control de infecciones
    all_urls += _load_source("CDC Infection Control Dental", fn=fetch_cdc_infection_dental_urls)
    all_urls += _load_source("OSHA Dental",               fn=fetch_osha_dental_urls)
    all_urls += _load_source("OSAP Dental",               fn=fetch_osap_dental_urls)

    # J. Gestión y codificación
    all_urls += _load_source("ADA Practice Management",   fn=fetch_ada_practice_mgmt_urls)
    all_urls += _load_source("Dental Economics",          fn=fetch_dental_economics_urls)
    all_urls += _load_source("NHS BSA Dental",            fn=fetch_nhs_bsa_dental_urls)
    all_urls += _load_source("NOM-013 Mexico",            fn=fetch_nom013_mexico_urls)

    # K. Educación al paciente
    all_urls += _load_source("MouthHealthy ADA",          fn=fetch_mouthhealthy_urls)
    all_urls += _load_source("CDC Oral Public",           fn=fetch_cdc_oral_public_urls)
    all_urls += _load_source("WHO Oral Public",           fn=fetch_who_oral_public_urls)
    all_urls += _load_source("PAHO Oral Public",          fn=fetch_paho_oral_public_urls)
    all_urls += _load_source("NHS Dental Patient Info",   fn=fetch_nhs_dental_patient_urls)

    # L. Tecnología dental
    all_urls += _load_source("AI in Dentistry (S2)",      fn=fetch_ai_dentistry_urls)
    all_urls += _load_source("CBCT Resources",            fn=fetch_cbct_resources_urls)
    all_urls += _load_source("CAD/CAM Dental",            fn=fetch_cad_cam_dental_urls)
    all_urls += _load_source("Digital Workflow Dental",   fn=fetch_digital_workflow_dental_urls)

    # M. Institutos de investigación
    all_urls += _load_source("NIDCR NIH",                 fn=fetch_nidcr_urls)
    all_urls += _load_source("Forsyth Institute",         fn=fetch_forsyth_urls)
    all_urls += _load_source("KCL Dental",                fn=fetch_kcl_dental_urls)
    all_urls += _load_source("UCL Eastman",               fn=fetch_ucl_eastman_urls)
    all_urls += _load_source("UNAM Estomatología",        fn=fetch_unam_estomatologia_urls)

    # N. Repositorios OA y preprints
    all_urls += _load_source("medRxiv Dental",            fn=fetch_medrxiv_dental_urls)
    all_urls += _load_source("OSF Dental",                fn=fetch_osf_dental_urls)
    all_urls += _load_source("Figshare Dental",           fn=fetch_figshare_dental_urls)

    print(f"\nTotal URLs objetivo: {len(all_urls)}", flush=True)
    return all_urls


# ── Scraping ───────────────────────────────────────────────────────────────────

def delay_for_url(url):
    # Inline API records — no HTTP
    if any(m in url for m in ["|PUBMED_DENTAL|", "|OPENALEX_DENTAL|", "|CROSSREF_DENTAL|",
                               "|DOAJ_DENTAL|", "|ZENODO_DENTAL|", "|S2_DENTAL|",
                               "|EUROPEPMC_DENTAL|", "|MEDRXIV_DENTAL|", "|OSF_DENTAL|",
                               "|FIGSHARE_DENTAL|", "|DAILYMED_DENTAL|"]):
        return 0.1
    if any(d in url for d in ["ada.org", "aae.org", "perio.org", "aaoms.org",
                               "fda.gov", "cdc.gov", "osha.gov", "who.int"]):
        return 3.0
    if any(d in url for d in ["bmcoralhealth", "mdpi.com", "hindawi.com",
                               "frontiersin.org", "nidcr.nih.gov"]):
        return 1.5
    return 2.0


def scrape_page(url):
    # Inline records — no HTTP
    inline_markers = ["|PUBMED_DENTAL|", "|OPENALEX_DENTAL|", "|CROSSREF_DENTAL|",
                      "|DOAJ_DENTAL|", "|ZENODO_DENTAL|", "|S2_DENTAL|",
                      "|EUROPEPMC_DENTAL|", "|MEDRXIV_DENTAL|", "|OSF_DENTAL|",
                      "|FIGSHARE_DENTAL|", "|DAILYMED_DENTAL|"]
    if any(m in url for m in inline_markers):
        text = extract_inline_content(url)
        title = text.split("\n")[0] or "record"
        return {"title": title, "full_text": text}

    resp = requests.get(url, headers=HEADERS, timeout=25)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    h1 = soup.find("h1") or soup.find("h2")
    title = h1.get_text(strip=True) if h1 else url.split("/")[-1].replace("-", " ").title()

    meta = soup.find("meta", {"name": "description"})
    summary = meta["content"] if meta else ""

    for tag in soup(["script", "style", "nav", "footer", "header", "aside",
                     "form", "button", "iframe"]):
        tag.decompose()

    paragraphs = [
        p.get_text(separator=" ", strip=True)
        for p in soup.find_all(["p", "li", "td", "dd"])
        if len(p.get_text(strip=True)) > 50
    ]
    body = "\n\n".join(paragraphs)

    if len(body) < 300:
        for div in soup.find_all("div", class_=re.compile(r"content|article|body|main", re.I)):
            div_text = div.get_text(separator="\n", strip=True)
            if len(div_text) > 300:
                body = div_text
                break

    return {"title": title,
            "full_text": f"{title}\n{'='*len(title)}\n\nURL: {url}\n\n{summary}\n\n{body}".strip()}


def url_to_filename(url):
    if "fdiworlddental.org"        in url: prefix = "fdi"
    elif "who.int"                 in url: prefix = "who_oral"
    elif "paho.org"                in url: prefix = "paho_oral"
    elif "iapd.org"                in url: prefix = "iapd"
    elif "ada.org.au"              in url: prefix = "adc_au"
    elif "ada.org"                 in url: prefix = "ada"
    elif "bda.org"                 in url: prefix = "bda"
    elif "cda-adc.ca"              in url: prefix = "cda"
    elif "seoc.es"                 in url: prefix = "seoc"
    elif "coem.org.es"             in url: prefix = "coem"
    elif "cfo.org.br"              in url: prefix = "cfo"
    elif "cmd.org.mx"              in url: prefix = "cmd"
    elif "nzda.org.nz"             in url: prefix = "nzda"
    elif "sdcep.org.uk"            in url: prefix = "sdcep"
    elif "nice.org.uk"             in url: prefix = "nice_oral"
    elif "aapd.org"                in url: prefix = "aapd"
    elif "aae.org"                 in url: prefix = "aae"
    elif "perio.org"               in url: prefix = "aap"
    elif "aaoms.org"               in url: prefix = "aaoms"
    elif "iadt-dentaltrauma.org"   in url: prefix = "iadt"
    elif "efp.org"                 in url: prefix = "efp"
    elif "eapd.gr"                 in url: prefix = "eapd"
    elif "aaoinfo.org"             in url: prefix = "aao"
    elif "aaomr.org"               in url: prefix = "aaomr"
    elif "aaom.com"                in url: prefix = "aaom"
    elif "bmcoralhealth"           in url: prefix = "bmc_oral"
    elif "mdpi.com"                in url: prefix = "mdpi_dent"
    elif "benthamopen.com"         in url: prefix = "open_dent"
    elif "hindawi.com"             in url: prefix = "hindawi_dent"
    elif "frontiersin.org"         in url: prefix = "frontiers_dent"
    elif "nature.com/bdjo"         in url: prefix = "bdj_open"
    elif "pubmed.ncbi"             in url: prefix = "pubmed_dent"
    elif "europepmc.org"           in url: prefix = "europepmc_dent"
    elif "|PUBMED_DENTAL|"         in url: prefix = "pubmed_dent"
    elif "|OPENALEX_DENTAL|"       in url: prefix = "openalex_dent"
    elif "|CROSSREF_DENTAL|"       in url: prefix = "crossref_dent"
    elif "|DOAJ_DENTAL|"           in url: prefix = "doaj_dent"
    elif "|ZENODO_DENTAL|"         in url: prefix = "zenodo_dent"
    elif "|S2_DENTAL|"             in url: prefix = "s2_dent"
    elif "|EUROPEPMC_DENTAL|"      in url: prefix = "europepmc_dent"
    elif "|MEDRXIV_DENTAL|"        in url: prefix = "medrxiv_dent"
    elif "|OSF_DENTAL|"            in url: prefix = "osf_dent"
    elif "|FIGSHARE_DENTAL|"       in url: prefix = "figshare_dent"
    elif "|DAILYMED_DENTAL|"       in url: prefix = "dailymed_dent"
    elif "radiopaedia.org"         in url: prefix = "radiopaedia_dent"
    elif "pathologyoutlines.com"   in url: prefix = "pathology_oral"
    elif "dailymed.nlm.nih.gov"    in url: prefix = "dailymed_dent"
    elif "fda.gov"                 in url: prefix = "fda_dental"
    elif "cofepris.gob.mx"         in url: prefix = "cofepris_dent"
    elif "invima.gov.co"           in url: prefix = "invima_dent"
    elif "iti.org"                 in url: prefix = "iti"
    elif "eao.org"                 in url: prefix = "eao"
    elif "prosthodontics.org"      in url: prefix = "acp"
    elif "escd.org"                in url: prefix = "escd"
    elif "cdc.gov/oralhealth/infectioncontrol" in url: prefix = "cdc_infection_dent"
    elif "osha.gov"                in url: prefix = "osha_dent"
    elif "osap.org"                in url: prefix = "osap"
    elif "cdc.gov/oralhealth"      in url: prefix = "cdc_oral"
    elif "mouthhealthy.org"        in url: prefix = "mouthhealthy"
    elif "nhs.uk"                  in url: prefix = "nhs_dent"
    elif "nhsbsa.nhs.uk"           in url: prefix = "nhsbsa_dent"
    elif "dentaleconomics.com"     in url: prefix = "dental_econ"
    elif "dof.gob.mx"              in url: prefix = "nom013"
    elif "nidcr.nih.gov"           in url: prefix = "nidcr"
    elif "forsyth.org"             in url: prefix = "forsyth"
    elif "kcl.ac.uk"               in url: prefix = "kcl_dent"
    elif "ucl.ac.uk"               in url: prefix = "ucl_eastman"
    elif "unam.mx"                 in url: prefix = "unam_estomato"
    elif "medrxiv.org"             in url: prefix = "medrxiv_dent"
    elif "osf.io"                  in url: prefix = "osf_dent"
    elif "figshare.com"            in url: prefix = "figshare_dent"
    elif "jdentaled.org"           in url: prefix = "jdentaled"
    else:                                  prefix = "dental"
    path = re.sub(r"[?=&|]", "_", url.split("//", 1)[-1]).replace("/", "__").strip("__")
    return f"{prefix}__{path[:180]}.txt"


# ── Progreso ───────────────────────────────────────────────────────────────────

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"done": [], "failed": []}


def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Conectando a Google Drive...", flush=True)
    service = get_drive_service()
    print("Conexión exitosa.\n", flush=True)

    all_urls = get_all_urls()
    progress = load_progress()
    done_set = set(progress["done"])
    remaining = [u for u in all_urls if u not in done_set]

    total = len(all_urls)
    print(f"\nTotal: {total} | Ya hechos: {len(done_set)} | Pendientes: {len(remaining)}\n", flush=True)

    start_time = time.time()
    batch_errors = 0

    for i, url in enumerate(remaining, 1):
        try:
            data = scrape_page(url)
            filename = url_to_filename(url)
            upload_file(service, url, filename, data["full_text"])
            progress["done"].append(url)
            batch_errors = 0
        except Exception as e:
            err = str(e)
            progress["failed"].append({"url": url, "error": err})
            batch_errors += 1
            slug = url.rstrip("/").split("/")[-1][:60]
            print(f"  ERROR ({batch_errors}): {slug} — {err[:80]}", flush=True)
            if batch_errors >= 10:
                print("  10 errores seguidos, esperando 60s...", flush=True)
                time.sleep(60)
                batch_errors = 0

        if i % 50 == 0:
            save_progress(progress)
            elapsed = time.time() - start_time
            rate = i / elapsed if elapsed > 0 else 0
            eta = (len(remaining) - i) / rate / 60 if rate > 0 else 0
            print(f"[{i}/{len(remaining)}] {rate:.1f} pág/s — ETA {eta:.0f} min", flush=True)

        time.sleep(delay_for_url(url))

    save_progress(progress)
    print(f"\nFinalizado. {len(progress['done'])} páginas subidas.", flush=True)
