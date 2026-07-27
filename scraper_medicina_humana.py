#!/usr/bin/env python3
"""
scraper_medicina_humana.py — Corpus completo de medicina humana para IA
Incluye todas las fuentes públicamente accesibles: APTO, FILTRAR, LICENCIA, PREFLIGHT.
Se excluyen únicamente las que tienen paywall/WAF duro o robots.txt restrictivo explícito.
Resumible: guarda progreso en progress_medicina.json
"""

import json, os, re, time, xml.etree.ElementTree as ET
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

# ── Drive folder IDs ───────────────────────────────────────────────────────────
DRIVE_MEDICINA_ROOT_ID      = "1pf4QWGSh4UiqKgFyWmABpGFPanHfgvCl"
DRIVE_MEDLINEPLUS_ID        = "16Mcyb_b4YNsPubFihzqSHVKMv-8DZedp"
DRIVE_CDC_CONTENT_ID        = "1sUb3COk4igElhtcHAELiZEp8Pv0l7CVy"
DRIVE_CDC_MMWR_ID           = "1Xyf6_HhznsCDa4jpn4cNdPov9f_VivGl"
DRIVE_WHO_PUBLICATIONS_ID   = "1lJHVuxl3n4acin_yOZqa_3wiF1LPS6po"
DRIVE_PAHO_ID               = "1QvnE6Fg8EkkCjd53OcjuxQwqe9R_lTDq"
DRIVE_ECDC_ID               = "1dskbWxFbI7auPdIDAg-NxcG8706FOG8j"
DRIVE_NCI_PDQ_ID            = "1SsHwNQ1_D6KWBY_jfyVGqKafLv3aH3ZT"
DRIVE_NIH_HIV_GUIDELINES_ID = "1ldXWDeF98gtXNVoFvJ-doZ3CVJWN7RxX"
DRIVE_USPSTF_ID             = "1ul38g8jXCG96gF3hRtYiLo5s3R2aqrB8"
DRIVE_AHRQ_ID               = "1iGW87AhSi0QYjwirTC0hAhWy8brana3D"
DRIVE_VA_DOD_GUIDELINES_ID  = "1j0_bZ5XTXQTGUO2EQIhEylKMBC4ORtqb"
DRIVE_ATSDR_TOXICOLOGY_ID   = "1glkvSURA6DIRn0oiGvLyuaKastJmgOdK"
DRIVE_EPA_IRIS_ID           = "1aukSOn2BGYDgN9rvCZ1FH3OXq8OL-gsF"
DRIVE_DAILYMED_ID           = "1wqghJqPniSpKINtanAQSDsIzTElt9jc7"
DRIVE_OPENFDA_ID            = "12X2OMNLUW4JFpuqmlPvX7Lrrazk5qfqG"
DRIVE_RXNORM_INFO_ID        = "1e9d2v4BylDCsweMHf62tKl3uvGhNIZAA"
DRIVE_CLINICALTRIALS_ID     = "1HJdNwrFCh6-3EODdoJvx0Zg0w5AiSZ7n"
DRIVE_EUROPE_PMC_ID         = "1MlQnoMVzNjQ22gog_DpIBXo9ayKb2mC-"
DRIVE_PLOS_MEDICINE_ID      = "1vNCbVXzUO0bOxAeOz9u3RXVs-7TC9qSU"
DRIVE_FRONTIERS_MEDICINE_ID = "1Gk2JtzJgZNn6-yJF19BUF0notFZe8lr9"
DRIVE_BMC_MEDICINE_ID       = "1QtKfG4IP4Km6IlEsZ2ZBJWufrI5eNDLq"
DRIVE_NHS_CONDITIONS_ID     = "1RF3R6yuiO3DLVRJHukKgW7mJdC5gvzKg"
DRIVE_NHS_MEDICINES_ID      = "1R0b7K_8zNx_l02jgdUDpmxIOoLXhje89"
DRIVE_NCBI_BOOKSHELF_ID     = "1tXKipC2ATuqyKlAfAAm_sxeaLm4UeIO0"
DRIVE_ORPHANET_ID           = "1wF1NWUH8FQ_XNdWUjknBXxo9ZVc3AQm5"

# Batch 2 — todas las fuentes adicionales
DRIVE_MERCK_MANUAL_PRO_ID      = "1YqtoUmZq5efJ9Piv7oAgiJja-F-FU9hJ"
DRIVE_MERCK_MANUAL_CONSUMER_ID = "1Cs1QAl_5i-M3CDVeVKRMbps01Cr9zGq-"
DRIVE_MSD_MANUAL_PRO_ID        = "1RD-7k7OBN0VbaAGG5uFPr3aibPUmLhvK"
DRIVE_MSD_MANUAL_CONSUMER_ID   = "1axj_bsMi_8BXlBIhYUC6vcrgWjaCrn9t"
DRIVE_WIKEM_ID                 = "17-15-aZN0iGD9RHvUfqWA5jOihfp1cRQ"
DRIVE_MSF_GUIDELINES_ID        = "17eRH-VBU3NeljQLjKzfJRDagH-jkLC8e"
DRIVE_HEALTH_CANADA_ID         = "1PpBGFtdqtIpHzOkIWAjJXmHkm4GNIP3n"
DRIVE_AUSTRALIA_HEALTH_ID      = "13uVQIm_QbtkwjIYQs73p9pwk_-u8Xwe7"
DRIVE_SAMHSA_ID                = "1PNvlEznUHNLM6kdO0I2ALe6544ee7TfV"
DRIVE_UNICEF_HEALTH_ID         = "1GnuBw4tRreOWg_VSEa0YwSIA7B5_FjaA"
DRIVE_NICE_GUIDELINES_ID       = "1GjEZyQgTEJTpthdMLQ-YmXocge7u3L0Q"
DRIVE_SIGN_GUIDELINES_ID       = "1EynMCTNVSvAdHcFmiQ0p3XcJVknmXTkv"
DRIVE_EMA_HUMAN_ID             = "1FIDNDuFChwE89c6uTxbxJDlrQpwHa3vO"
DRIVE_FDA_GUIDANCE_ID          = "1U7iIo1FxZxZkSBEEk3wG2ao8CVBRJ_w4"
DRIVE_CADTH_ID                 = "1S2kcbzJoDk4E2FzOWVI1IhALlzDbbEP0"
DRIVE_NHMRC_AUSTRALIA_ID       = "1ib4eDroDkWB_fD_zRGQJqVNVQFL4AE1z"
DRIVE_ACP_GUIDELINES_ID        = "1A57VLyeDnQBgZjqMQmb8MeaTOPYvyseo"
DRIVE_AAFP_GUIDELINES_ID       = "1DlNdqqaFmagGZDw1v-iqrDQc-mwuvXo8"
DRIVE_AHA_GUIDELINES_ID        = "1wV15N_4mx8wCReWVLHjs0xn1CvzoxCm1"
DRIVE_ACC_GUIDELINES_ID        = "1yR4zyzr2jgoxsWWcvfHMUAyVqyFu-h0V"
DRIVE_ESC_GUIDELINES_ID        = "1hnPbTllcKMPmb8uhXPQDjva9hkdr8_vs"
DRIVE_ASCO_GUIDELINES_ID       = "1tXtuGaZr_nk7OT7xzqWSAVEYdkc0f9cH"
DRIVE_ESMO_GUIDELINES_ID       = "1Yv2JSJ8y2380eAeoo943yAslQMSIhTV8"
DRIVE_AAN_GUIDELINES_ID        = "1gSkpMLU3o6Sc1rn6B9yBwexPFfsCMYW7"
DRIVE_IDSA_GUIDELINES_ID       = "1rTIqpDv6S_B2J7R8hM3OWfNT9D9Z8GsD"
DRIVE_KDIGO_GUIDELINES_ID      = "1osZqFMjiM-ZmnIQAD9DwQ3033ZcVmdUG"
DRIVE_ADA_DIABETES_ID          = "14MtPQc4JIqU3FZgNle4n_mZHcIaWOMaj"
DRIVE_ENDOCRINE_SOCIETY_ID     = "1Yj6s9OBs9XSe69AiTJ3-g2rMua3gMsMc"
DRIVE_GINA_ASTHMA_ID           = "1wywE0fuc-XRBIJ3CoIF92NN3GZiLDrh8"
DRIVE_GOLD_COPD_ID             = "1IEKLbtziNcrXcczerLlSsGNs4vykoPz7"
DRIVE_ATS_GUIDELINES_ID        = "1UVIjpzh5N9JAA8u6DP-5WqtqpjgeuAmU"
DRIVE_ASH_GUIDELINES_ID        = "1ytFjUhJQSUd5EDKNxI-Dv4qHnjU3OGCV"
DRIVE_ACG_GUIDELINES_ID        = "14lwT3EZeH9qTeql5XgfkNG3r0P7EuwM7"
DRIVE_AGA_GUIDELINES_ID        = "1NiYE0GyibAbNnu7X14_a_M9onIBxck7B"
DRIVE_ACOG_GUIDELINES_ID       = "1I_lCf-fRyK99X1XS9UbB2c-kXEM2-Ila"
DRIVE_RCOG_GUIDELINES_ID       = "14qEMLlAMdd_t7U9xQ-TVBkyeY3lGVrSC"
DRIVE_AAP_GUIDELINES_ID        = "1U00IKi2Nzj1U2tkdzt21EtqR2Hd2saKk"
DRIVE_SCCM_GUIDELINES_ID       = "16kt-PlL25YPga4abZ9JCkG7YYvRw-Yf1"
DRIVE_EAU_GUIDELINES_ID        = "1nfU8FOdKaIlOZZx80z7Oy6rATc-s_EqN"
DRIVE_AAD_GUIDELINES_ID        = "1JqhxCPVFmmkrokhiLhx3asEGWryrgyNq"
DRIVE_APA_GUIDELINES_ID        = "1YBdhIdYeKjglKtgrUVO2BRbWAJOrcmFa"
DRIVE_AAAAI_GUIDELINES_ID      = "1Z96ZEwUJ59qSzDxrKEjnM-ZvPRDxiYs2"
DRIVE_WSES_GUIDELINES_ID       = "1SiRCYKEkfH5n6clKAVORaYpBHFz5afD3"
DRIVE_ERAS_GUIDELINES_ID       = "1Rc4rOPHqGJB27N5C4Cn8HLXFe2AlKp_f"
DRIVE_MAYO_CLINIC_ID           = "1dfLvkL5gjUgCdPah7Jh1OvRKDVYA7c7D"
DRIVE_CLEVELAND_CLINIC_ID      = "10c6k-ZyRvmU18HFEaBGyxPJikiAETZzn"
DRIVE_JOHNS_HOPKINS_ID         = "1LJ9nX0pIezA3Gr7ITiDKp1Ec3QdU46Gv"
DRIVE_MOUNT_SINAI_ID           = "1TRklar6uPqe6dDkPxQB6q-FHQMs4dyAC"
DRIVE_STANFORD_HEALTH_ID       = "14siD-mpzU7ni6umbKPdpFODyhqJZCTbE"
DRIVE_UCSF_HEALTH_ID           = "11Qm-NNeJ817w2iuBRr9MRFLw8u_yxy7S"
DRIVE_NYU_LANGONE_ID           = "1AIzbgED35_45C9aHlt14bgODNyo768yO"
DRIVE_PENN_MEDICINE_ID         = "1NljAej3Asg_xIjurlwodi-NLQwna1g_f"
DRIVE_YALE_MEDICINE_ID         = "1WZuBT2OWN1GR18zd0WYRhtDxEdpPDhvK"
DRIVE_INCHEM_TOXICOLOGY_ID     = "1o_LOdCOKOcwugFxzQANRQ7Atxw5hKOhL"
DRIVE_NIOSH_POCKET_ID          = "1MYG2lMuhORD2Mq4fj-ie3j3jOqWfwHev"
DRIVE_CAMEO_CHEMICALS_ID       = "1AOQRepes0FhKwRQi7jYreLK3Hs0jKWxE"
DRIVE_IARC_MONOGRAPHS_ID       = "1VbUXb5uipiFOdf8oJQpde4j1tyrJwVAj"
DRIVE_CDC_CHEMICAL_ID          = "1avkBrTzJDVaAiZMohvl_q_eWYByMINgL"
DRIVE_WHO_CHEMICAL_ID          = "1fZjxZ2CxHPofgnz0FQKHikPi8mTg1TzH"
DRIVE_BMC_SERIES_ID            = "1Fe1XWKbGZtGmKpfb5v9LsQfdpeY6LrF7"
DRIVE_ELIFE_JOURNAL_ID         = "1khG2B2yPikJbswtrRkQ-uCqeLwzj96IZ"
DRIVE_JAMA_OPEN_ID             = "1BklKVB_G147n6xgGTVcHU8YzcvyRIvPS"
DRIVE_CUREUS_ID                = "10v1MbjixvBhBAj3KqWezdz5cusQtcO6B"
DRIVE_JMIR_ID                  = "1DASpvSWQ0qkH587fLXAfud2XyA1CNMXG"
DRIVE_PEERJ_ID                 = "1fE4TKbpP5dXEFINMfPI95-FKMHXC1uRd"
DRIVE_EUROSURVEILLANCE_ID      = "1ufG6CzKPFz3jdlKXrSdra0YFzhkkHqvV"
DRIVE_CDC_EID_ID               = "17CGbQ9_Awc4-nzRrMpw21c_UyznTrWZH"
DRIVE_ANNALS_FAMILY_ID         = "1nDjrLtAWXqyv1QG4lxDm6yNoGp4CyIR1"
DRIVE_MEDRXIV_ID               = "1o4dDY8e9I6AOVgphG884iVGZNMfu4cLc"
DRIVE_GARD_RARE_DISEASES_ID    = "1daXw15HEJROjCRXKSVXemIzWK58fG7-E"
DRIVE_HPO_ONTOLOGY_ID          = "14VL5v6_6iuvAAfdZwJ9bqOua37aUNJWf"
DRIVE_MONDO_ONTOLOGY_ID        = "1XCVYxzxnmbyG194tx_spPooi8ocjPDXm"
DRIVE_CLINVAR_ID               = "1xwJ7RlLP_g27wbGhTvDerJCiELjsf2_v"
DRIVE_OPEN_TARGETS_ID          = "1IywWQxruGJ5WiWMx-3EBLhlQPucKfwGb"
DRIVE_GWAS_CATALOG_ID          = "1uDz1mknjq4nqy8WiE1nXkXj5mZm2vm1X"
DRIVE_MEDGEN_ID                = "14vNMfbI6d9uZ_5juRXfnsEBsmcDK5eXv"
DRIVE_NCBI_GENE_ID             = "1wFX-XPD6hqHSmmOmiv4GMJz3TaG2_aEo"
DRIVE_OPENALEX_MED_ID          = "1BvQtEvVgyBVeMUtYTEWiWaXTUxLEw1Gk"   # openalex_medicina_humana

PROGRESS_FILE = "progress_medicina.json"

HEADERS = {
    "User-Agent": "HumanMedicineCorpusBot/1.0 (educational-AI-project; contact: jlps1977@gmail.com)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
}

# ── URLs / endpoints de fuentes ────────────────────────────────────────────────
# --- Sitemaps HTML ---
NHS_CONDITIONS_SITEMAP      = "https://www.nhs.uk/sitemap.xml"
NHS_MEDICINES_SITEMAP       = "https://www.nhs.uk/sitemap.xml"
USPSTF_SEED                 = "https://www.uspreventiveservicestaskforce.org/uspstf/recommendation-topics"
AHRQ_SITEMAP                = "https://effectivehealthcare.ahrq.gov/sitemap.xml"
VA_DOD_SEED                 = "https://www.healthquality.va.gov/"
ATSDR_PROFILES_SEED         = "https://www.atsdr.cdc.gov/tox-profile/about/index.html"
ATSDR_TOXFAQS_SEED          = "https://www.atsdr.cdc.gov/toxfaqs/"
NCI_PDQ_SEED                = "https://www.cancer.gov/publications/pdq"
NIH_HIV_SEED                = "https://clinicalinfo.hiv.gov/en/guidelines"
ECDC_SITEMAP                = "https://www.ecdc.europa.eu/sitemap.xml"
PAHO_SITEMAP                = "https://www.paho.org/sitemap.xml"
MMWR_SITEMAP                = "https://www.cdc.gov/mmwr/sitemap.xml"
NCBI_BOOKSHELF_SEEDS = [
    "https://www.ncbi.nlm.nih.gov/books/NBK430685/",  # StatPearls
    "https://www.ncbi.nlm.nih.gov/books/NBK547852/",  # LiverTox
    "https://www.ncbi.nlm.nih.gov/books/NBK501922/",  # LactMed
]

# --- APIs ---
CLINICALTRIALS_API  = "https://clinicaltrials.gov/api/v2/studies"
DAILYMED_API        = "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json"
OPENFDA_API         = "https://api.fda.gov/drug/label.json"
EUROPE_PMC_API      = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
PLOS_API            = "https://api.plos.org/search"
WHO_API             = "https://www.who.int/api/hubs/publications"
MEDLINEPLUS_XML     = "https://wsearch.nlm.nih.gov/ws/query?db=healthTopicsEnglish&term=*&retmax=1000"
FRONTIERS_SITEMAP   = "https://www.frontiersin.org/sitemap-articles.xml"

# ── Google Drive ───────────────────────────────────────────────────────────────
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
    # NHS
    if "nhs.uk/conditions"           in url:  return DRIVE_NHS_CONDITIONS_ID
    if "nhs.uk/medicines"            in url:  return DRIVE_NHS_MEDICINES_ID
    if "nhs.uk"                      in url:  return DRIVE_NHS_CONDITIONS_ID
    # Guías / reguladores
    if "uspreventiveservices"        in url:  return DRIVE_USPSTF_ID
    if "effectivehealthcare"         in url:  return DRIVE_AHRQ_ID
    if "ahrq.gov"                    in url:  return DRIVE_AHRQ_ID
    if "healthquality.va.gov"        in url:  return DRIVE_VA_DOD_GUIDELINES_ID
    if "nice.org.uk"                 in url:  return DRIVE_NICE_GUIDELINES_ID
    if "sign.ac.uk"                  in url:  return DRIVE_SIGN_GUIDELINES_ID
    if "ema.europa.eu/en/medicines/human" in url: return DRIVE_EMA_HUMAN_ID
    if "fda.gov/regulatory-information"  in url:  return DRIVE_FDA_GUIDANCE_ID
    if "cda-amc.ca"                  in url:  return DRIVE_CADTH_ID
    if "nhmrc.gov.au"                in url:  return DRIVE_NHMRC_AUSTRALIA_ID
    if "acponline.org"               in url:  return DRIVE_ACP_GUIDELINES_ID
    if "aafp.org"                    in url:  return DRIVE_AAFP_GUIDELINES_ID
    # Especialidades
    if "professional.heart.org"      in url:  return DRIVE_AHA_GUIDELINES_ID
    if "acc.org"                     in url:  return DRIVE_ACC_GUIDELINES_ID
    if "escardio.org"                in url:  return DRIVE_ESC_GUIDELINES_ID
    if "asco.org"                    in url:  return DRIVE_ASCO_GUIDELINES_ID
    if "esmo.org"                    in url:  return DRIVE_ESMO_GUIDELINES_ID
    if "aan.com"                     in url:  return DRIVE_AAN_GUIDELINES_ID
    if "idsociety.org"               in url:  return DRIVE_IDSA_GUIDELINES_ID
    if "kdigo.org"                   in url:  return DRIVE_KDIGO_GUIDELINES_ID
    if "professional.diabetes.org"   in url:  return DRIVE_ADA_DIABETES_ID
    if "endocrine.org"               in url:  return DRIVE_ENDOCRINE_SOCIETY_ID
    if "ginasthma.org"               in url:  return DRIVE_GINA_ASTHMA_ID
    if "goldcopd.org"                in url:  return DRIVE_GOLD_COPD_ID
    if "thoracic.org"                in url:  return DRIVE_ATS_GUIDELINES_ID
    if "ersnet.org"                  in url:  return DRIVE_ATS_GUIDELINES_ID
    if "hematology.org"              in url:  return DRIVE_ASH_GUIDELINES_ID
    if "gi.org"                      in url:  return DRIVE_ACG_GUIDELINES_ID
    if "gastro.org"                  in url:  return DRIVE_AGA_GUIDELINES_ID
    if "acog.org"                    in url:  return DRIVE_ACOG_GUIDELINES_ID
    if "rcog.org.uk"                 in url:  return DRIVE_RCOG_GUIDELINES_ID
    if "aap.org"                     in url:  return DRIVE_AAP_GUIDELINES_ID
    if "sccm.org"                    in url:  return DRIVE_SCCM_GUIDELINES_ID
    if "uroweb.org"                  in url:  return DRIVE_EAU_GUIDELINES_ID
    if "aad.org"                     in url:  return DRIVE_AAD_GUIDELINES_ID
    if "psychiatry.org"              in url:  return DRIVE_APA_GUIDELINES_ID
    if "aaaai.org"                   in url:  return DRIVE_AAAAI_GUIDELINES_ID
    if "wses.org.uk"                 in url:  return DRIVE_WSES_GUIDELINES_ID
    if "erassociety.org"             in url:  return DRIVE_ERAS_GUIDELINES_ID
    # Manuales
    if "merckmanuals.com/professional" in url:  return DRIVE_MERCK_MANUAL_PRO_ID
    if "merckmanuals.com/home"         in url:  return DRIVE_MERCK_MANUAL_CONSUMER_ID
    if "merckmanuals.com"              in url:  return DRIVE_MERCK_MANUAL_PRO_ID
    if "msdmanuals.com/professional"   in url:  return DRIVE_MSD_MANUAL_PRO_ID
    if "msdmanuals.com/home"           in url:  return DRIVE_MSD_MANUAL_CONSUMER_ID
    if "msdmanuals.com"                in url:  return DRIVE_MSD_MANUAL_PRO_ID
    if "wikem.org"                     in url:  return DRIVE_WIKEM_ID
    if "medicalguidelines.msf.org"     in url:  return DRIVE_MSF_GUIDELINES_ID
    # Orgs internacionales
    if "health.canada.ca"            in url:  return DRIVE_HEALTH_CANADA_ID
    if "health.gov.au"               in url:  return DRIVE_AUSTRALIA_HEALTH_ID
    if "samhsa.gov"                  in url:  return DRIVE_SAMHSA_ID
    if "unicef.org/health"           in url:  return DRIVE_UNICEF_HEALTH_ID
    # Toxicología
    if "atsdr.cdc.gov"               in url:  return DRIVE_ATSDR_TOXICOLOGY_ID
    if "inchem.org"                  in url:  return DRIVE_INCHEM_TOXICOLOGY_ID
    if "iris.epa.gov"                in url:  return DRIVE_EPA_IRIS_ID
    if "niosh/npg"                   in url:  return DRIVE_NIOSH_POCKET_ID
    if "cameochemicals"              in url:  return DRIVE_CAMEO_CHEMICALS_ID
    if "iarc.who.int"                in url:  return DRIVE_IARC_MONOGRAPHS_ID
    if "cdc.gov/chemical"            in url:  return DRIVE_CDC_CHEMICAL_ID
    if "who.int/health-topics/chemical" in url: return DRIVE_WHO_CHEMICAL_ID
    # Hospitales
    if "mayoclinic.org"              in url:  return DRIVE_MAYO_CLINIC_ID
    if "clevelandclinic.org"         in url:  return DRIVE_CLEVELAND_CLINIC_ID
    if "hopkinsmedicine.org"         in url:  return DRIVE_JOHNS_HOPKINS_ID
    if "mountsinai.org"              in url:  return DRIVE_MOUNT_SINAI_ID
    if "stanfordhealthcare.org"      in url:  return DRIVE_STANFORD_HEALTH_ID
    if "ucsfhealth.org"              in url:  return DRIVE_UCSF_HEALTH_ID
    if "nyulangone.org"              in url:  return DRIVE_NYU_LANGONE_ID
    if "pennmedicine.org"            in url:  return DRIVE_PENN_MEDICINE_ID
    if "yalemedicine.org"            in url:  return DRIVE_YALE_MEDICINE_ID
    # Fuentes originales Fase 1
    if "cancer.gov"                  in url:  return DRIVE_NCI_PDQ_ID
    if "clinicalinfo.hiv.gov"        in url:  return DRIVE_NIH_HIV_GUIDELINES_ID
    if "ecdc.europa.eu"              in url:  return DRIVE_ECDC_ID
    if "paho.org"                    in url:  return DRIVE_PAHO_ID
    if "cdc.gov/mmwr"                in url:  return DRIVE_CDC_MMWR_ID
    if "cdc.gov"                     in url:  return DRIVE_CDC_CONTENT_ID
    if "who.int"                     in url:  return DRIVE_WHO_PUBLICATIONS_ID
    if "medlineplus.gov"             in url:  return DRIVE_MEDLINEPLUS_ID
    if "ncbi.nlm.nih.gov/books"      in url:  return DRIVE_NCBI_BOOKSHELF_ID
    if "clinicaltrials.gov"          in url:  return DRIVE_CLINICALTRIALS_ID
    if "dailymed.nlm.nih.gov"        in url:  return DRIVE_DAILYMED_ID
    if "api.fda.gov"                 in url:  return DRIVE_OPENFDA_ID
    if "europepmc.org"               in url:  return DRIVE_EUROPE_PMC_ID
    if "journals.plos.org"           in url:  return DRIVE_PLOS_MEDICINE_ID
    if "frontiersin.org"             in url:  return DRIVE_FRONTIERS_MEDICINE_ID
    if "biomedcentral.com"           in url:  return DRIVE_BMC_MEDICINE_ID
    if "orphanet"                    in url:  return DRIVE_ORPHANET_ID
    # Revistas extra
    if "elifesciences.org"           in url:  return DRIVE_ELIFE_JOURNAL_ID
    if "jamanetworkopen.com"         in url:  return DRIVE_JAMA_OPEN_ID
    if "cureus.com"                  in url:  return DRIVE_CUREUS_ID
    if "jmir.org"                    in url:  return DRIVE_JMIR_ID
    if "peerj.com"                   in url:  return DRIVE_PEERJ_ID
    if "eurosurveillance.org"        in url:  return DRIVE_EUROSURVEILLANCE_ID
    if "wwwnc.cdc.gov/eid"           in url:  return DRIVE_CDC_EID_ID
    if "annfammed.org"               in url:  return DRIVE_ANNALS_FAMILY_ID
    if "medrxiv.org"                 in url:  return DRIVE_MEDRXIV_ID
    # Bases de datos clínicas
    if "rarediseases.info.nih.gov"   in url:  return DRIVE_GARD_RARE_DISEASES_ID
    if "hpo.jax.org"                 in url:  return DRIVE_HPO_ONTOLOGY_ID
    if "mondo.monarchinitiative.org" in url:  return DRIVE_MONDO_ONTOLOGY_ID
    if "ncbi.nlm.nih.gov/clinvar"    in url:  return DRIVE_CLINVAR_ID
    if "platform.opentargets.org"    in url:  return DRIVE_OPEN_TARGETS_ID
    if "ebi.ac.uk/gwas"              in url:  return DRIVE_GWAS_CATALOG_ID
    if "ncbi.nlm.nih.gov/medgen"     in url:  return DRIVE_MEDGEN_ID
    if "ncbi.nlm.nih.gov/gene"       in url:  return DRIVE_NCBI_GENE_ID
    if "|OPENALEX_MED|"              in url:  return DRIVE_OPENALEX_MED_ID
    return DRIVE_MEDICINA_ROOT_ID


def upload_file(service, url, name, content):
    folder_id = folder_for_url(url)
    safe_name  = re.sub(r"[^\w\-.]", "_", name)[:180] + ".txt"
    body = {"name": safe_name, "parents": [folder_id], "mimeType": "text/plain"}
    media = MediaInMemoryUpload(content.encode("utf-8", errors="replace"), mimetype="text/plain")
    service.files().create(body=body, media_body=media, fields="id").execute()


# ── Helpers de sitemap ─────────────────────────────────────────────────────────
def fetch_urls_from_sitemap(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code == 429:
            return []
        if not r.ok:
            return []
        try:
            root = ET.fromstring(r.text)
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            return [el.text for el in root.findall(".//sm:loc", ns) if el.text]
        except ET.ParseError:
            return re.findall(r"<loc>\s*(https?://[^<\s]+)\s*</loc>", r.text)
    except Exception as e:
        print(f"  sitemap error {url}: {e}", flush=True)
        return []


def _fetch_sitemap_index_urls(index_url, url_filter=None, delay=1.0):
    sub_sitemaps = fetch_urls_from_sitemap(index_url)
    if not sub_sitemaps:
        return []
    all_urls = []
    for sm in sub_sitemaps:
        urls = fetch_urls_from_sitemap(sm)
        if url_filter:
            urls = [u for u in urls if url_filter(u)]
        all_urls.extend(urls)
        time.sleep(delay)
    return all_urls


def _crawl_one_level(seed, domain_match, delay=3.0):
    visited = set([seed])
    try:
        r = requests.get(seed, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        base = seed.split("/")[0] + "//" + seed.split("/")[2]
        for a in soup.find_all("a", href=True):
            href = a["href"].split("#")[0].split("?")[0]
            if not href:
                continue
            if href.startswith("http"):
                if domain_match in href:
                    visited.add(href)
            elif href.startswith("/"):
                visited.add(base + href)
    except Exception as e:
        print(f"  crawl error {seed}: {e}", flush=True)
    time.sleep(delay)
    return list(visited)


# ── Fetchers por fuente ────────────────────────────────────────────────────────

def fetch_nhs_conditions_urls():
    all_u = _fetch_sitemap_index_urls(
        NHS_CONDITIONS_SITEMAP,
        url_filter=lambda u: "/conditions/" in u or "/medicines/" in u,
        delay=2.0,
    )
    return list(set(all_u))


def fetch_uspstf_urls():
    return _crawl_one_level(USPSTF_SEED, "uspreventiveservicestaskforce.org", delay=3.0)


def fetch_ahrq_urls():
    return _fetch_sitemap_index_urls(AHRQ_SITEMAP, delay=2.0)


def fetch_va_dod_urls():
    return _crawl_one_level(VA_DOD_SEED, "healthquality.va.gov", delay=3.0)


def fetch_atsdr_urls():
    urls = set()
    for seed in [ATSDR_PROFILES_SEED, ATSDR_TOXFAQS_SEED]:
        found = _crawl_one_level(seed, "atsdr.cdc.gov", delay=2.0)
        urls.update(found)
    return list(urls)


def fetch_nci_pdq_urls():
    return _crawl_one_level(NCI_PDQ_SEED, "cancer.gov", delay=2.0)


def fetch_nih_hiv_urls():
    return _crawl_one_level(NIH_HIV_SEED, "clinicalinfo.hiv.gov", delay=2.0)


def fetch_ecdc_urls():
    return _fetch_sitemap_index_urls(
        ECDC_SITEMAP,
        url_filter=lambda u: "/en/" in u,
        delay=2.0,
    )


def fetch_paho_urls():
    return _fetch_sitemap_index_urls(PAHO_SITEMAP, delay=2.0)


def fetch_mmwr_urls():
    urls = fetch_urls_from_sitemap(MMWR_SITEMAP)
    if not urls:
        urls = _crawl_one_level("https://www.cdc.gov/mmwr/", "cdc.gov/mmwr", delay=2.0)
    return urls


def fetch_ncbi_bookshelf_urls():
    urls = set()
    for seed in NCBI_BOOKSHELF_SEEDS:
        found = _crawl_one_level(seed, "ncbi.nlm.nih.gov/books", delay=5.0)
        urls.update(found)
    return list(urls)


def fetch_clinicaltrials_urls():
    """API ClinicalTrials.gov v2 — retorna hasta 10,000 estudios con delay 1s."""
    urls = []
    params = {
        "format": "json",
        "pageSize": 1000,
        "fields": "NCTId,BriefTitle,OfficialTitle,BriefSummary,Condition,InterventionName,Phase,OverallStatus",
    }
    next_token = None
    fetched = 0
    MAX_RECORDS = 10000
    print("  ClinicalTrials API paginando...", flush=True)
    while fetched < MAX_RECORDS:
        if next_token:
            params["pageToken"] = next_token
        try:
            r = requests.get(CLINICALTRIALS_API, params=params, headers=HEADERS, timeout=30)
            if not r.ok:
                print(f"  ClinicalTrials API error {r.status_code}", flush=True)
                break
            data = r.json()
        except Exception as e:
            print(f"  ClinicalTrials API error: {e}", flush=True)
            break
        studies = data.get("studies", [])
        if not studies:
            break
        for s in studies:
            nct_id = s.get("protocolSection", {}).get("identificationModule", {}).get("nctId", "")
            if nct_id:
                urls.append(f"https://clinicaltrials.gov/study/{nct_id}|JSON|{json.dumps(s)}")
        fetched += len(studies)
        next_token = data.get("nextPageToken")
        if not next_token:
            break
        time.sleep(1.0)
        print(f"  ClinicalTrials: {fetched} estudios...", flush=True)
    return urls


def fetch_dailymed_urls():
    """DailyMed API — primera página de etiquetas de medicamentos."""
    urls = []
    params = {"pagesize": 100, "page": 1}
    MAX_PAGES = 50
    print("  DailyMed API paginando...", flush=True)
    for page in range(1, MAX_PAGES + 1):
        params["page"] = page
        try:
            r = requests.get(DAILYMED_API, params=params, headers=HEADERS, timeout=30)
            if not r.ok:
                break
            data = r.json()
        except Exception as e:
            print(f"  DailyMed error: {e}", flush=True)
            break
        spls = data.get("data", [])
        if not spls:
            break
        for spl in spls:
            setid = spl.get("setid", "")
            title = spl.get("title", "")
            if setid:
                urls.append(f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={setid}|SETID|{title}")
        time.sleep(1.0)
        if page % 10 == 0:
            print(f"  DailyMed: {len(urls)} etiquetas...", flush=True)
    return urls


def fetch_openfda_urls():
    """openFDA drug label API — medicamentos con información clínica."""
    urls = []
    params = {"limit": 100, "skip": 0}
    MAX_SKIP = 5000
    print("  openFDA API paginando...", flush=True)
    while params["skip"] < MAX_SKIP:
        try:
            r = requests.get(OPENFDA_API, params=params, headers=HEADERS, timeout=30)
            if not r.ok:
                if r.status_code == 404:
                    break
                print(f"  openFDA error {r.status_code}", flush=True)
                break
            data = r.json()
        except Exception as e:
            print(f"  openFDA error: {e}", flush=True)
            break
        results = data.get("results", [])
        if not results:
            break
        for item in results:
            brand = (item.get("openfda", {}).get("brand_name") or ["unknown"])[0]
            urls.append(f"https://api.fda.gov/drug/label|LABEL|{json.dumps(item)}")
        params["skip"] += 100
        time.sleep(1.0)
        if params["skip"] % 1000 == 0:
            print(f"  openFDA: {len(urls)} etiquetas...", flush=True)
    return urls


def fetch_europe_pmc_urls():
    """Europe PMC — artículos OA de medicina humana, filtro clínico."""
    queries = [
        'OPEN_ACCESS:Y AND HAS_FT:Y AND SRC:MED AND LANG:eng AND (("clinical trial") OR ("systematic review") OR ("randomized controlled trial"))',
        'OPEN_ACCESS:Y AND HAS_FT:Y AND SRC:MED AND LANG:eng AND (("clinical practice") OR ("treatment guidelines") OR ("diagnosis"))',
    ]
    urls = []
    MAX_PER_QUERY = 2000
    for query in queries:
        params = {
            "query": query,
            "format": "json",
            "pageSize": 1000,
            "resultType": "core",
        }
        cursor = "*"
        fetched_q = 0
        print(f"  Europe PMC query: {query[:60]}...", flush=True)
        while fetched_q < MAX_PER_QUERY:
            params["cursorMark"] = cursor
            try:
                r = requests.get(EUROPE_PMC_API, params=params, headers=HEADERS, timeout=30)
                if not r.ok:
                    break
                data = r.json()
            except Exception as e:
                print(f"  Europe PMC error: {e}", flush=True)
                break
            articles = data.get("resultList", {}).get("result", [])
            if not articles:
                break
            for a in articles:
                pmcid = a.get("pmcid", "")
                pmid  = a.get("pmid", "")
                title = a.get("title", "")
                abstract = a.get("abstractText", "")
                if pmcid:
                    url = f"https://europepmc.org/article/pmc/{pmcid.replace('PMC','')}"
                    payload = f"TITLE: {title}\n\nABSTRACT: {abstract}"
                    urls.append(f"{url}|EPMC|{payload}")
                elif pmid:
                    url = f"https://europepmc.org/article/med/{pmid}"
                    payload = f"TITLE: {title}\n\nABSTRACT: {abstract}"
                    urls.append(f"{url}|EPMC|{payload}")
            next_cursor = data.get("nextCursorMark", "")
            fetched_q += len(articles)
            if not next_cursor or next_cursor == cursor:
                break
            cursor = next_cursor
            time.sleep(1.5)
        print(f"  Europe PMC total: {len(urls)} artículos", flush=True)
    return list(set(urls))


def fetch_plos_medicine_urls():
    """PLOS API — artículos de medicina y salud pública."""
    params = {
        "q": 'journal:"PLOS Medicine" OR subject:"Public Health and Epidemiology" OR subject:"Clinical Medicine"',
        "fl": "id,title_display,abstract",
        "rows": 1000,
        "wt": "json",
    }
    urls = []
    start = 0
    while True:
        params["start"] = start
        try:
            r = requests.get(PLOS_API, params=params, headers=HEADERS, timeout=30)
            data = r.json()
        except Exception as e:
            print(f"  PLOS error at start={start}: {e}", flush=True)
            break
        docs = data["response"]["docs"]
        if not docs:
            break
        for doc in docs:
            doi = doc.get("id", "")
            title = (doc.get("title_display") or [""])[0] if isinstance(doc.get("title_display"), list) else doc.get("title_display", "")
            abstract = (doc.get("abstract") or [""])[0] if isinstance(doc.get("abstract"), list) else doc.get("abstract", "")
            if doi:
                urls.append(f"https://journals.plos.org/plosmedicine/article?id={doi}|PLOS|TITLE: {title}\n\nABSTRACT: {abstract}")
        total = data["response"]["numFound"]
        start += 1000
        if start >= min(total, 5000):
            break
        time.sleep(2.0)
    return urls


def fetch_frontiers_medicine_urls():
    return _fetch_sitemap_index_urls(
        FRONTIERS_SITEMAP,
        url_filter=lambda u: "/medicine/" in u or "/public-health/" in u or "/pharmacology/" in u,
        delay=1.5,
    )


def fetch_who_urls():
    """WHO publications API."""
    urls = []
    params = {"sf_culture": "en", "_format": "json", "page": 0, "pageSize": 100}
    MAX_PAGES = 30
    print("  WHO API paginando...", flush=True)
    for page in range(MAX_PAGES):
        params["page"] = page
        try:
            r = requests.get(WHO_API, params=params, headers=HEADERS, timeout=30)
            if not r.ok:
                break
            data = r.json()
        except Exception as e:
            print(f"  WHO API error: {e}", flush=True)
            break
        items = data if isinstance(data, list) else data.get("results", data.get("items", []))
        if not items:
            break
        for item in items:
            url = item.get("url", item.get("Url", ""))
            title = item.get("title", item.get("Title", ""))
            if url and "who.int" in url:
                urls.append(url)
        time.sleep(1.5)
        if len(items) < 100:
            break
    return list(set(urls))


# ── Fetchers adicionales (batch 2) ────────────────────────────────────────────

def fetch_merck_manual_urls():
    urls = _fetch_sitemap_index_urls("https://www.merckmanuals.com/sitemap.xml", delay=5.0)
    pro  = [u for u in urls if "/professional/" in u]
    con  = [u for u in urls if "/home/" in u]
    return pro + con


def fetch_msd_manual_urls():
    return _fetch_sitemap_index_urls("https://www.msdmanuals.com/sitemap.xml", delay=5.0)


def fetch_wikem_urls():
    """WikEM usa MediaWiki — crawl de 1 nivel desde el índice de artículos."""
    return _crawl_one_level("https://wikem.org/wiki/WikEM:Main_Page", "wikem.org/wiki", delay=1.5)


def fetch_msf_guidelines_urls():
    return _crawl_one_level("https://medicalguidelines.msf.org/en", "medicalguidelines.msf.org", delay=3.0)


def fetch_health_canada_urls():
    return _fetch_sitemap_index_urls(
        "https://www.canada.ca/sitemap.xml",
        url_filter=lambda u: "health-canada" in u or "sante-canada" in u,
        delay=3.0,
    )


def fetch_australia_health_urls():
    return _fetch_sitemap_index_urls("https://www.health.gov.au/sitemap.xml", delay=3.0)


def fetch_samhsa_urls():
    return _fetch_sitemap_index_urls("https://www.samhsa.gov/sitemap.xml", delay=3.0)


def fetch_unicef_health_urls():
    return _crawl_one_level("https://www.unicef.org/health", "unicef.org/health", delay=3.0)


def fetch_nice_guidelines_urls():
    return _crawl_one_level("https://www.nice.org.uk/guidance", "nice.org.uk/guidance", delay=5.0)


def fetch_sign_guidelines_urls():
    return _crawl_one_level("https://www.sign.ac.uk/our-guidelines/", "sign.ac.uk", delay=4.0)


def fetch_ema_human_urls():
    return _fetch_sitemap_index_urls(
        "https://www.ema.europa.eu/sitemap.xml",
        url_filter=lambda u: "/en/medicines/human" in u or "/en/documents/product-information" in u,
        delay=2.0,
    )


def fetch_fda_guidance_urls():
    return _crawl_one_level(
        "https://www.fda.gov/regulatory-information/search-fda-guidance-documents",
        "fda.gov/regulatory-information",
        delay=30.0,
    )


def fetch_cadth_urls():
    return _fetch_sitemap_index_urls("https://www.cda-amc.ca/sitemap.xml", delay=5.0)


def fetch_nhmrc_urls():
    return _crawl_one_level("https://www.nhmrc.gov.au/guidelines", "nhmrc.gov.au/guidelines", delay=4.0)


def _fetch_society_guidelines(seed, domain, delay=5.0):
    return _crawl_one_level(seed, domain, delay=delay)


def fetch_inchem_urls():
    return _crawl_one_level("https://inchem.org/", "inchem.org", delay=3.0)


def fetch_niosh_urls():
    return _crawl_one_level("https://www.cdc.gov/niosh/npg/", "cdc.gov/niosh", delay=2.0)


def fetch_cameo_urls():
    return _crawl_one_level("https://cameochemicals.noaa.gov/", "cameochemicals.noaa.gov", delay=2.0)


def fetch_iarc_urls():
    return _crawl_one_level("https://monographs.iarc.who.int/", "monographs.iarc.who.int", delay=3.0)


def fetch_cdc_chemical_urls():
    return _crawl_one_level("https://www.cdc.gov/chemical-emergencies/", "cdc.gov/chemical", delay=2.0)


def fetch_mayo_clinic_urls():
    return _fetch_sitemap_index_urls(
        "https://www.mayoclinic.org/sitemap.xml",
        url_filter=lambda u: "/diseases-conditions/" in u or "/symptoms/" in u or "/drugs-supplements/" in u,
        delay=5.0,
    )


def fetch_cleveland_clinic_urls():
    return _fetch_sitemap_index_urls(
        "https://my.clevelandclinic.org/sitemap.xml",
        url_filter=lambda u: "/health/" in u,
        delay=5.0,
    )


def fetch_johns_hopkins_urls():
    urls = fetch_urls_from_sitemap("https://www.hopkinsmedicine.org/health-sitemap.xml")
    if not urls:
        urls = _crawl_one_level("https://www.hopkinsmedicine.org/health", "hopkinsmedicine.org/health", delay=4.0)
    return urls


def fetch_mount_sinai_urls():
    return _crawl_one_level("https://www.mountsinai.org/health-library", "mountsinai.org/health-library", delay=5.0)


def fetch_stanford_health_urls():
    return _crawl_one_level("https://stanfordhealthcare.org/medical-conditions.html", "stanfordhealthcare.org", delay=5.0)


def fetch_ucsf_urls():
    return _crawl_one_level("https://www.ucsfhealth.org/", "ucsfhealth.org", delay=5.0)


def fetch_nyu_langone_urls():
    return _crawl_one_level("https://nyulangone.org/conditions", "nyulangone.org/conditions", delay=5.0)


def fetch_penn_medicine_urls():
    return _crawl_one_level(
        "https://www.pennmedicine.org/for-patients-and-visitors/patient-information/conditions-treated-a-to-z",
        "pennmedicine.org",
        delay=5.0,
    )


def fetch_yale_medicine_urls():
    return _crawl_one_level("https://www.yalemedicine.org/conditions", "yalemedicine.org/conditions", delay=5.0)


def fetch_elife_urls():
    return _crawl_one_level("https://elifesciences.org/", "elifesciences.org", delay=2.0)


def fetch_jama_open_urls():
    return _crawl_one_level("https://jamanetworkopen.com/", "jamanetworkopen.com", delay=5.0)


def fetch_cureus_urls():
    return _crawl_one_level("https://www.cureus.com/", "cureus.com", delay=3.0)


def fetch_jmir_urls():
    return _fetch_sitemap_index_urls("https://www.jmir.org/sitemap.xml", delay=2.0)


def fetch_peerj_urls():
    return _fetch_sitemap_index_urls("https://peerj.com/sitemap.xml", delay=2.0)


def fetch_eurosurveillance_urls():
    return _fetch_sitemap_index_urls("https://www.eurosurveillance.org/sitemap.xml", delay=2.0)


def fetch_cdc_eid_urls():
    return _crawl_one_level("https://wwwnc.cdc.gov/eid/", "wwwnc.cdc.gov/eid", delay=2.0)


def fetch_annals_family_urls():
    return _crawl_one_level("https://www.annfammed.org/", "annfammed.org", delay=3.0)


def fetch_medrxiv_urls():
    """medRxiv API — preprints de medicina (corpus separado, marcado como preprint)."""
    urls = []
    params = {"server": "medrxiv", "category": "all", "interval": "2024-01-01:2026-07-25", "format": "json"}
    try:
        r = requests.get("https://api.biorxiv.org/details/medrxiv/2024-01-01/2026-07-25/0/json",
                         headers=HEADERS, timeout=30)
        data = r.json()
        total = data["messages"][0]["total"]
        for cursor in range(0, min(total, 5000), 100):
            r2 = requests.get(f"https://api.biorxiv.org/details/medrxiv/2024-01-01/2026-07-25/{cursor}/json",
                              headers=HEADERS, timeout=30)
            d2 = r2.json()
            for paper in d2.get("collection", []):
                doi = paper.get("doi", "")
                title = paper.get("title", "")
                abstract = paper.get("abstract", "")
                if doi:
                    urls.append(f"https://www.medrxiv.org/content/{doi}|PREPRINT|TITLE: {title}\n\nABSTRACT: {abstract}")
            time.sleep(1.0)
    except Exception as e:
        print(f"  medRxiv error: {e}", flush=True)
    return urls


def fetch_gard_urls():
    return _crawl_one_level("https://rarediseases.info.nih.gov/", "rarediseases.info.nih.gov", delay=2.0)


# ── Carga de todas las URLs ────────────────────────────────────────────────────

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


# Segments via OpenAlex's Domain>Field>Subfield>Topic taxonomy: unions the
# three Health Sciences fields other than Dentistry/Veterinary (Medicine,
# Nursing, Health Professions -- same filter key, pipe-OR works in one call)
# per the team's decision to cover the full Health Sciences scope for
# MedicalOS, not just core clinical Medicine. See
# health-platform-knowledge-infrastructure README for the domain-mapping
# rationale. Cursor-paginated so a single run isn't capped.
OPENALEX_API_KEY = os.environ.get("OPENALEX_API_KEY", "")
OPENALEX_MAX_RESULTS = 300  # per run; raise for a one-off catch-up


def _openalex_reconstruct_abstract(inverted_index):
    if not inverted_index:
        return ""
    positions = {}
    for word, idxs in inverted_index.items():
        for i in idxs:
            positions[i] = word
    return " ".join(positions[i] for i in sorted(positions))


def fetch_openalex_med_urls():
    urls = []
    cursor = "*"
    while cursor and len(urls) < OPENALEX_MAX_RESULTS:
        params = {
            "filter": "primary_topic.field.id:27|29|36", "per-page": 100, "cursor": cursor,
            "select": "id,doi,title,abstract_inverted_index",
        }
        if OPENALEX_API_KEY:
            params["api_key"] = OPENALEX_API_KEY
        try:
            r = requests.get("https://api.openalex.org/works", params=params, headers=HEADERS, timeout=30)
            data = r.json()
        except Exception:
            break
        works = data.get("results", [])
        if not works:
            break
        for w in works:
            doi = w.get("doi") or ""
            title = w.get("title") or ""
            wid = w.get("id", "").split("/")[-1]
            abstract = _openalex_reconstruct_abstract(w.get("abstract_inverted_index"))
            urls.append(f"https://openalex.org/works/{wid}|OPENALEX_MED|"
                        f"{json.dumps({'title': title, 'doi': doi, 'abstract': abstract})}")
        cursor = (data.get("meta") or {}).get("next_cursor")
    return urls


def get_all_urls():
    all_urls = []

    # ── FASE 1: fuentes core APTO ─────────────────────────────────────────────
    all_urls += _load_source("NHS Conditions & Medicines",       fn=fetch_nhs_conditions_urls)
    all_urls += _load_source("USPSTF Recommendations",           fn=fetch_uspstf_urls)
    all_urls += _load_source("AHRQ Effective Health Care",       fn=fetch_ahrq_urls)
    all_urls += _load_source("VA/DoD Clinical Guidelines",       fn=fetch_va_dod_urls)
    all_urls += _load_source("ATSDR Toxicology Profiles",        fn=fetch_atsdr_urls)
    all_urls += _load_source("NCI PDQ Oncology",                 fn=fetch_nci_pdq_urls)
    all_urls += _load_source("NIH HIV/AIDS Guidelines",          fn=fetch_nih_hiv_urls)
    all_urls += _load_source("ECDC Publications",                fn=fetch_ecdc_urls)
    all_urls += _load_source("PAHO/OPS",                         fn=fetch_paho_urls)
    all_urls += _load_source("CDC MMWR",                         fn=fetch_mmwr_urls)
    all_urls += _load_source("NCBI Bookshelf (StatPearls etc.)", fn=fetch_ncbi_bookshelf_urls)
    all_urls += _load_source("OpenAlex Medicina Humana (Fields 27|29|36)", fn=fetch_openalex_med_urls)
    all_urls += _load_source("WHO Publications",                 fn=fetch_who_urls)
    all_urls += _load_source("Frontiers Medicine",               fn=fetch_frontiers_medicine_urls)
    # APIs
    all_urls += _load_source("ClinicalTrials.gov API",           fn=fetch_clinicaltrials_urls)
    all_urls += _load_source("DailyMed Drug Labels",             fn=fetch_dailymed_urls)
    all_urls += _load_source("openFDA Drug Labels",              fn=fetch_openfda_urls)
    all_urls += _load_source("Europe PMC OA",                    fn=fetch_europe_pmc_urls)
    all_urls += _load_source("PLOS Medicine",                    fn=fetch_plos_medicine_urls)

    # ── FASE 2: manuales ──────────────────────────────────────────────────────
    all_urls += _load_source("Merck Manual Pro/Consumer",        fn=fetch_merck_manual_urls)
    all_urls += _load_source("MSD Manual Pro/Consumer",          fn=fetch_msd_manual_urls)
    all_urls += _load_source("WikEM (Emergency Medicine)",       fn=fetch_wikem_urls)
    all_urls += _load_source("MSF Medical Guidelines",           fn=fetch_msf_guidelines_urls)

    # ── FASE 3: organizaciones adicionales ────────────────────────────────────
    all_urls += _load_source("Health Canada",                    fn=fetch_health_canada_urls)
    all_urls += _load_source("Australia Dept of Health",         fn=fetch_australia_health_urls)
    all_urls += _load_source("SAMHSA Mental Health",             fn=fetch_samhsa_urls)
    all_urls += _load_source("UNICEF Health",                    fn=fetch_unicef_health_urls)

    # ── FASE 4: guías clínicas ────────────────────────────────────────────────
    all_urls += _load_source("NICE Guidelines (UK)",             fn=fetch_nice_guidelines_urls)
    all_urls += _load_source("SIGN Guidelines (Scotland)",       fn=fetch_sign_guidelines_urls)
    all_urls += _load_source("EMA Human Medicines",              fn=fetch_ema_human_urls)
    all_urls += _load_source("FDA Guidance Documents",           fn=fetch_fda_guidance_urls)
    all_urls += _load_source("CADTH (Canada HTA)",               fn=fetch_cadth_urls)
    all_urls += _load_source("NHMRC Australia",                  fn=fetch_nhmrc_urls)

    # ── FASE 5: especialidades médicas ───────────────────────────────────────
    all_urls += _load_source("AHA Cardiology Guidelines",        fn=lambda: _fetch_society_guidelines("https://professional.heart.org/en/guidelines-and-statements", "professional.heart.org"))
    all_urls += _load_source("ACC Cardiology",                   fn=lambda: _fetch_society_guidelines("https://www.acc.org/guidelines", "acc.org/guidelines"))
    all_urls += _load_source("ESC Cardiology",                   fn=lambda: _fetch_society_guidelines("https://www.escardio.org/Guidelines", "escardio.org/Guidelines"))
    all_urls += _load_source("ASCO Oncology",                    fn=lambda: _fetch_society_guidelines("https://www.asco.org/guidelines", "asco.org/guidelines"))
    all_urls += _load_source("ESMO Oncology",                    fn=lambda: _fetch_society_guidelines("https://www.esmo.org/guidelines", "esmo.org/guidelines"))
    all_urls += _load_source("AAN Neurology",                    fn=lambda: _fetch_society_guidelines("https://www.aan.com/practice/guidelines", "aan.com/practice"))
    all_urls += _load_source("IDSA Infectious Diseases",         fn=lambda: _fetch_society_guidelines("https://www.idsociety.org/practice-guideline/", "idsociety.org"))
    all_urls += _load_source("KDIGO Nephrology",                 fn=lambda: _fetch_society_guidelines("https://kdigo.org/guidelines/", "kdigo.org"))
    all_urls += _load_source("ADA Diabetes Standards",           fn=lambda: _fetch_society_guidelines("https://professional.diabetes.org/standards-of-care", "diabetes.org"))
    all_urls += _load_source("Endocrine Society",                fn=lambda: _fetch_society_guidelines("https://www.endocrine.org/clinical-practice-guidelines", "endocrine.org"))
    all_urls += _load_source("GINA Asthma",                      fn=lambda: _fetch_society_guidelines("https://ginasthma.org/", "ginasthma.org"))
    all_urls += _load_source("GOLD COPD",                        fn=lambda: _fetch_society_guidelines("https://goldcopd.org/", "goldcopd.org"))
    all_urls += _load_source("ATS Pulmonology",                  fn=lambda: _fetch_society_guidelines("https://www.thoracic.org/statements/", "thoracic.org"))
    all_urls += _load_source("ERS Pulmonology",                  fn=lambda: _fetch_society_guidelines("https://www.ersnet.org/guidelines/", "ersnet.org"))
    all_urls += _load_source("ASH Hematology",                   fn=lambda: _fetch_society_guidelines("https://www.hematology.org/education/clinicians/guidelines-and-quality-care", "hematology.org"))
    all_urls += _load_source("ACG Gastroenterology",             fn=lambda: _fetch_society_guidelines("https://gi.org/guidelines/", "gi.org/guidelines"))
    all_urls += _load_source("AGA Gastroenterology",             fn=lambda: _fetch_society_guidelines("https://gastro.org/clinical-guidance/", "gastro.org"))
    all_urls += _load_source("ACOG Obstetrics",                  fn=lambda: _fetch_society_guidelines("https://www.acog.org/clinical", "acog.org/clinical"))
    all_urls += _load_source("RCOG Obstetrics (UK)",             fn=lambda: _fetch_society_guidelines("https://www.rcog.org.uk/guidance/", "rcog.org.uk"))
    all_urls += _load_source("AAP Pediatrics",                   fn=lambda: _fetch_society_guidelines("https://publications.aap.org/pediatrics", "aap.org"))
    all_urls += _load_source("SCCM Critical Care",               fn=lambda: _fetch_society_guidelines("https://www.sccm.org/clinical-resources/guidelines", "sccm.org"))
    all_urls += _load_source("EAU Urology",                      fn=lambda: _fetch_society_guidelines("https://uroweb.org/guidelines", "uroweb.org"))
    all_urls += _load_source("AAD Dermatology",                  fn=lambda: _fetch_society_guidelines("https://www.aad.org/member/clinical-quality/guidelines", "aad.org"))
    all_urls += _load_source("APA Psychiatry",                   fn=lambda: _fetch_society_guidelines("https://www.psychiatry.org/psychiatrists/practice/clinical-practice-guidelines", "psychiatry.org"))
    all_urls += _load_source("AAAAI Allergy/Immunology",         fn=lambda: _fetch_society_guidelines("https://www.aaaai.org/allergist-resources/statements-practice-parameters", "aaaai.org"))
    all_urls += _load_source("WSES Surgery",                     fn=lambda: _fetch_society_guidelines("https://www.wses.org.uk/clinical-guidelines", "wses.org.uk"))
    all_urls += _load_source("ERAS Perioperative",               fn=lambda: _fetch_society_guidelines("https://erassociety.org/guidelines/", "erassociety.org"))

    # ── FASE 6: toxicología extra ─────────────────────────────────────────────
    all_urls += _load_source("INCHEM Chemical Safety",           fn=fetch_inchem_urls)
    all_urls += _load_source("NIOSH Pocket Guide",               fn=fetch_niosh_urls)
    all_urls += _load_source("CAMEO Chemicals",                  fn=fetch_cameo_urls)
    all_urls += _load_source("IARC Monographs",                  fn=fetch_iarc_urls)
    all_urls += _load_source("CDC Chemical Emergencies",         fn=fetch_cdc_chemical_urls)

    # ── FASE 7: hospitales / universidades ───────────────────────────────────
    all_urls += _load_source("Mayo Clinic",                      fn=fetch_mayo_clinic_urls)
    all_urls += _load_source("Cleveland Clinic",                 fn=fetch_cleveland_clinic_urls)
    all_urls += _load_source("Johns Hopkins Medicine",           fn=fetch_johns_hopkins_urls)
    all_urls += _load_source("Mount Sinai Health Library",       fn=fetch_mount_sinai_urls)
    all_urls += _load_source("Stanford Health Care",             fn=fetch_stanford_health_urls)
    all_urls += _load_source("UCSF Health",                      fn=fetch_ucsf_urls)
    all_urls += _load_source("NYU Langone Health",               fn=fetch_nyu_langone_urls)
    all_urls += _load_source("Penn Medicine",                    fn=fetch_penn_medicine_urls)
    all_urls += _load_source("Yale Medicine",                    fn=fetch_yale_medicine_urls)

    # ── FASE 8: revistas científicas extra ───────────────────────────────────
    all_urls += _load_source("eLife Journal",                    fn=fetch_elife_urls)
    all_urls += _load_source("JAMA Network Open",                fn=fetch_jama_open_urls)
    all_urls += _load_source("Cureus (Open Access)",             fn=fetch_cureus_urls)
    all_urls += _load_source("JMIR Publications",                fn=fetch_jmir_urls)
    all_urls += _load_source("PeerJ Medicine",                   fn=fetch_peerj_urls)
    all_urls += _load_source("Eurosurveillance",                 fn=fetch_eurosurveillance_urls)
    all_urls += _load_source("CDC Emerging Infectious Diseases", fn=fetch_cdc_eid_urls)
    all_urls += _load_source("Annals of Family Medicine",        fn=fetch_annals_family_urls)
    all_urls += _load_source("medRxiv Preprints (2024-2026)",    fn=fetch_medrxiv_urls)

    # ── FASE 9: bases de datos clínicas ──────────────────────────────────────
    all_urls += _load_source("GARD Rare Diseases (NIH)",         fn=fetch_gard_urls)

    print(f"\nTotal URLs objetivo: {len(all_urls)}", flush=True)
    return all_urls


# ── Scraping de páginas HTML ───────────────────────────────────────────────────

def scrape_page(url):
    """Devuelve texto limpio de una URL HTML."""
    resp = requests.get(url, headers=HEADERS, timeout=25)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    h1 = soup.find("h1") or soup.find("h2")
    title = h1.get_text(strip=True) if h1 else url.split("/")[-1].replace("-", " ").title()

    meta = soup.find("meta", {"name": "description"})
    summary = meta["content"] if meta else ""

    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "button", "iframe"]):
        tag.decompose()

    paragraphs = [
        p.get_text(separator=" ", strip=True)
        for p in soup.find_all(["p", "li", "h1", "h2", "h3", "h4", "td", "th"])
        if p.get_text(strip=True)
    ]

    body = "\n".join(paragraphs)
    if len(body) < 200:
        main = soup.find("main") or soup.find("article") or soup.find("div", {"id": re.compile("content|main", re.I)})
        if main:
            body = main.get_text(separator="\n", strip=True)

    return f"SOURCE: {url}\nTITLE: {title}\nSUMMARY: {summary}\n\n{body}"


def url_to_filename(url):
    url_clean = url.split("|")[0]
    MAP = [
        ("nhs.uk/conditions",           "nhs_cond"),
        ("nhs.uk/medicines",            "nhs_med"),
        ("nhs.uk",                      "nhs"),
        ("uspreventiveservices",        "uspstf"),
        ("effectivehealthcare",         "ahrq"),
        ("ahrq.gov",                    "ahrq"),
        ("healthquality.va.gov",        "va_dod"),
        ("atsdr.cdc.gov",               "atsdr"),
        ("cancer.gov",                  "nci"),
        ("clinicalinfo.hiv.gov",        "nih_hiv"),
        ("ecdc.europa.eu",              "ecdc"),
        ("paho.org",                    "paho"),
        ("cdc.gov/mmwr",                "mmwr"),
        ("wwwnc.cdc.gov/eid",           "cdc_eid"),
        ("cdc.gov/niosh",               "niosh"),
        ("cdc.gov/chemical",            "cdc_chem"),
        ("cdc.gov",                     "cdc"),
        ("who.int",                     "who"),
        ("ncbi.nlm.nih.gov/books",      "bookshelf"),
        ("clinicaltrials.gov",          "ct"),
        ("dailymed",                    "dailymed"),
        ("api.fda.gov",                 "openfda"),
        ("fda.gov/regulatory",          "fda_guidance"),
        ("europepmc.org",               "epmc"),
        ("openalex.org",                "openalex_med"),
        ("journals.plos.org",           "plos"),
        ("frontiersin.org",             "frontiers"),
        ("biomedcentral.com",           "bmc"),
        ("merckmanuals.com/professional","merck_pro"),
        ("merckmanuals.com/home",       "merck_con"),
        ("merckmanuals.com",            "merck"),
        ("msdmanuals.com/professional", "msd_pro"),
        ("msdmanuals.com/home",         "msd_con"),
        ("msdmanuals.com",              "msd"),
        ("wikem.org",                   "wikem"),
        ("medicalguidelines.msf.org",   "msf"),
        ("health.canada.ca",            "health_canada"),
        ("health.gov.au",               "aus_health"),
        ("samhsa.gov",                  "samhsa"),
        ("unicef.org",                  "unicef"),
        ("nice.org.uk",                 "nice"),
        ("sign.ac.uk",                  "sign"),
        ("ema.europa.eu",               "ema_human"),
        ("cda-amc.ca",                  "cadth"),
        ("nhmrc.gov.au",                "nhmrc"),
        ("professional.heart.org",      "aha"),
        ("acc.org",                     "acc"),
        ("escardio.org",                "esc"),
        ("asco.org",                    "asco"),
        ("esmo.org",                    "esmo"),
        ("aan.com",                     "aan"),
        ("idsociety.org",               "idsa"),
        ("kdigo.org",                   "kdigo"),
        ("diabetes.org",                "ada"),
        ("endocrine.org",               "endocrine"),
        ("ginasthma.org",               "gina"),
        ("goldcopd.org",                "gold"),
        ("thoracic.org",                "ats"),
        ("ersnet.org",                  "ers"),
        ("hematology.org",              "ash"),
        ("gi.org",                      "acg"),
        ("gastro.org",                  "aga"),
        ("acog.org",                    "acog"),
        ("rcog.org.uk",                 "rcog"),
        ("aap.org",                     "aap"),
        ("sccm.org",                    "sccm"),
        ("uroweb.org",                  "eau"),
        ("aad.org",                     "aad"),
        ("psychiatry.org",              "apa"),
        ("aaaai.org",                   "aaaai"),
        ("wses.org.uk",                 "wses"),
        ("erassociety.org",             "eras"),
        ("mayoclinic.org",              "mayo"),
        ("clevelandclinic.org",         "cleveland"),
        ("hopkinsmedicine.org",         "hopkins"),
        ("mountsinai.org",              "mount_sinai"),
        ("stanfordhealthcare.org",      "stanford"),
        ("ucsfhealth.org",              "ucsf"),
        ("nyulangone.org",              "nyu"),
        ("pennmedicine.org",            "penn"),
        ("yalemedicine.org",            "yale"),
        ("inchem.org",                  "inchem"),
        ("iris.epa.gov",                "epa_iris"),
        ("cameochemicals",              "cameo"),
        ("monographs.iarc",             "iarc"),
        ("elifesciences.org",           "elife"),
        ("jamanetworkopen.com",         "jama_open"),
        ("cureus.com",                  "cureus"),
        ("jmir.org",                    "jmir"),
        ("peerj.com",                   "peerj"),
        ("eurosurveillance.org",        "eurosurv"),
        ("annfammed.org",               "ann_fam"),
        ("medrxiv.org",                 "medrxiv"),
        ("rarediseases.info.nih.gov",   "gard"),
        ("orphanet",                    "orphanet"),
    ]
    for pattern, prefix in MAP:
        if pattern in url_clean:
            slug = re.sub(r"[^\w]", "_", url_clean)[-80:]
            return f"{prefix}_{slug}"
    slug = re.sub(r"[^\w]", "_", url_clean)[-80:]
    return f"med_{slug}"


def delay_for_url(url):
    for marker in ("|JSON|", "|SETID|", "|LABEL|", "|EPMC|", "|PLOS|", "|PREPRINT|"):
        if marker in url:
            return 0.0
    if "fda.gov"                in url:  return 30.0
    if "ncbi.nlm.nih.gov"       in url:  return 5.0
    if "merckmanuals.com"       in url:  return 5.0
    if "msdmanuals.com"         in url:  return 5.0
    if "mayoclinic.org"         in url:  return 5.0
    if "clevelandclinic.org"    in url:  return 5.0
    if "hopkinsmedicine.org"    in url:  return 5.0
    if "mountsinai.org"         in url:  return 7.0
    if "stanfordhealthcare.org" in url:  return 5.0
    if "ucsfhealth.org"         in url:  return 5.0
    if "nyulangone.org"         in url:  return 5.0
    if "pennmedicine.org"       in url:  return 5.0
    if "yalemedicine.org"       in url:  return 5.0
    if "ecdc.europa.eu"         in url:  return 3.0
    if "paho.org"               in url:  return 3.0
    if "sign.ac.uk"             in url:  return 4.0
    if "cda-amc.ca"             in url:  return 5.0
    if "nice.org.uk"            in url:  return 5.0
    if "health.canada.ca"       in url:  return 3.0
    if "health.gov.au"          in url:  return 3.0
    if "cdc.gov"                in url:  return 2.0
    if "who.int"                in url:  return 2.0
    if "nhs.uk"                 in url:  return 2.0
    if "cancer.gov"             in url:  return 2.0
    if "frontiersin.org"        in url:  return 1.5
    if "aan.com"                in url:  return 5.0
    if "acog.org"               in url:  return 5.0
    if "psychiatry.org"         in url:  return 5.0
    return 3.0


def extract_inline_content(url_entry):
    """Para URLs con contenido inline (API), extrae directamente sin HTTP."""
    parts = url_entry.split("|", 2)
    url    = parts[0]
    kind   = parts[1] if len(parts) > 1 else ""
    data   = parts[2] if len(parts) > 2 else ""

    if kind == "JSON":
        try:
            s = json.loads(data)
            modules = s.get("protocolSection", {})
            ident   = modules.get("identificationModule", {})
            desc    = modules.get("descriptionModule", {})
            cond    = modules.get("conditionsModule", {})
            interv  = modules.get("armsInterventionsModule", {})
            title   = ident.get("officialTitle") or ident.get("briefTitle", "")
            summary = desc.get("briefSummary", "")
            nct     = ident.get("nctId", "")
            conditions = ", ".join(cond.get("conditions", []))
            text = (
                f"SOURCE: {url}\n"
                f"TYPE: Clinical Trial\nNCT_ID: {nct}\nTITLE: {title}\n"
                f"CONDITIONS: {conditions}\n\n{summary}"
            )
            return text
        except Exception:
            return f"SOURCE: {url}\n{data}"

    if kind == "SETID":
        return f"SOURCE: {url}\nTYPE: Drug Label (DailyMed)\nTITLE: {data}\n\nSee full label at {url}"

    if kind == "LABEL":
        try:
            item = json.loads(data)
            brand    = (item.get("openfda", {}).get("brand_name") or [""])[0]
            generic  = (item.get("openfda", {}).get("generic_name") or [""])[0]
            purpose  = " ".join(item.get("purpose", [""]))
            warnings = " ".join(item.get("warnings", [""]))
            indic    = " ".join(item.get("indications_and_usage", [""]))
            dosage   = " ".join(item.get("dosage_and_administration", [""]))
            text = (
                f"SOURCE: openFDA Drug Label\n"
                f"BRAND: {brand}\nGENERIC: {generic}\n\n"
                f"INDICATIONS: {indic}\n\nWARNINGS: {warnings}\n\n"
                f"DOSAGE: {dosage}\n\nPURPOSE: {purpose}"
            )
            return text
        except Exception:
            return f"SOURCE: openFDA\n{data[:2000]}"

    if kind in ("EPMC", "PLOS"):
        return f"SOURCE: {url}\n{data}"

    if kind == "PREPRINT":
        return f"SOURCE: {url}\nTYPE: Preprint (NOT peer-reviewed)\n\n{data}"

    if kind == "OPENALEX_MED":
        try:
            item = json.loads(data)
            title = item.get("title", "Untitled")
            doi = item.get("doi", "")
            abstract = item.get("abstract", "")
            return (f"{title}\n{'='*len(title)}\n\nURL: {url}\nDOI: {doi}\n\n{abstract}").strip()
        except Exception:
            return f"SOURCE: {url}\n{data}"

    return None


# ── Progreso ───────────────────────────────────────────────────────────────────

def load_progress():
    try:
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {"done": [], "failed": []}


def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)


# ── Main loop ──────────────────────────────────────────────────────────────────

def main():
    print("=== Scraper Medicina Humana ===", flush=True)
    service  = get_drive_service()
    progress = load_progress()
    done_set = set(p.split("|")[0] if "|" in p else p for p in progress["done"])

    print("Descubriendo URLs de todas las fuentes...", flush=True)
    all_urls = get_all_urls()

    remaining = [u for u in all_urls if (u.split("|")[0] if "|" in u else u) not in done_set]
    total = len(all_urls)
    print(f"\nTotal: {total} | Ya hechos: {len(done_set)} | Pendientes: {len(remaining)}\n", flush=True)

    for i, url_entry in enumerate(remaining, 1):
        url = url_entry.split("|")[0] if "|" in url_entry else url_entry
        name = url_to_filename(url_entry)

        try:
            # Fuentes con contenido inline (API)
            inline = extract_inline_content(url_entry) if "|" in url_entry else None

            if inline is not None:
                text = inline
            else:
                text = scrape_page(url)

            if len(text.strip()) < 100:
                raise ValueError("Contenido demasiado corto")

            upload_file(service, url, name, text)
            progress["done"].append(url)

        except Exception as e:
            err = str(e)[:120]
            progress["failed"].append({"url": url, "error": err})
            print(f"  ✗ {url[:70]} — {err}", flush=True)

        d = delay_for_url(url_entry)
        if d > 0:
            time.sleep(d)

        if i % 50 == 0:
            save_progress(progress)
            done_total = len(done_set) + i
            pct = done_total / total * 100
            print(
                f"[{done_total}/{total} — {pct:.1f}%] "
                f"fallidos: {len(progress['failed'])}",
                flush=True,
            )

    save_progress(progress)
    print("\n=== Completado ===", flush=True)
    print(f"  Exitosos : {len(progress['done'])}")
    print(f"  Fallidos : {len(progress['failed'])}")


if __name__ == "__main__":
    main()
