#!/usr/bin/env python3
"""
Scraper de Nutriología Humana — corpus para IA de nutriólogos.
Cubre 100+ fuentes en 10 fases (INVENTARIO MAESTRO 2026-07-25):

  A) Organizaciones oficiales (FAO, EFSA, USDA, PAHO, UNICEF, WFP, Codex)
  B) Revistas científicas OA (Nutrients, BMC Nutrition, JISSN, 12+ más)
  C) Bases de composición de alimentos (FoodData Central API, Open Food Facts,
     Ciqual, Fineli, Frida, CoFID, AFCD, FOODfiles NZ, Norway API, Sweden API,
     BEDCA, TBCA, Phenol-Explorer, FoodOn)
  D) Guías dietéticas nacionales (DGA 2025, México 2023, España, UK SACN,
     Canadá, Australia, Nordic NNR 2023, Brasil, NZ, EFSA DRV, Japón, India)
  E) Sociedades profesionales (AND, ASN, SENC, FESNAD, SENPE, ESPEN, ASPEN,
     BAPEN, BDA, Nutrition Society, FELANPE, IUNS, FENS, Obesity Canada)
  F) Nutrición clínica y terapéutica (ESPEN guidelines, ASPEN, BAPEN/MUST,
     Critical Care Nutrition, Diabetes UK/CA, IDDSI, ESPGHAN, oncología)
  G) Nutrición deportiva (ISSN Position Stands, AIS Supplement Framework,
     OPSS/DoD, USADA, NCAA, Sport Integrity Australia)
  H) Universidades y hospitales (Harvard Nutrition Source, Tufts, Mayo Clinic,
     Cleveland Clinic, Johns Hopkins)
  I) Microbioma y nutrición (GMrepo, gutMDisorder, MGnify, Gut Microbiota for Health)
  J) Suplementos y micronutrientes (Linus Pauling MIC, Health Canada LNHPD API,
     OPSS Ingredients, EU Health Claims Register, EFSA Botanicals, MSK Herbs)

Uso: .venv/bin/python scraper_nutricion.py
Reanuda desde progress_nutricion.json.
"""

import os, re, json, time
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from google.oauth2.credentials import Credentials

# ── Drive IDs ─────────────────────────────────────────────────────────────────
DRIVE_NUTRICION_ROOT_ID             = "1Bfp5mlxLi9th6SZFwJCQyJY58K_1wu5f"
# A. Organizaciones oficiales
DRIVE_FAO_NUTRITION_ID              = "1VexKVgJ41Y4xCYfH-TqTr_Fma-K49b0h"
DRIVE_FAO_INFOODS_ID                = "1k2lzSKDEt7K0DhpNLoYoxPpBn8euk2DO"
DRIVE_FAO_DIETARY_GUIDELINES_ID     = "1zunVQJFBiBV9EV8K6EBJt9Fku8tUZjYz"
DRIVE_CODEX_ALIMENTARIUS_ID         = "1m0hXxqFSpK8SkYYrN1vifZO0gQceQTAd"
DRIVE_EFSA_NUTRITION_DRV_ID         = "1X0SvUlEkSOqXkjrfdJvQhr_WWJptADRy"
DRIVE_EFSA_FOOD_COMPOSITION_ID      = "1PYnhVdOS6ETAoiBEntbjXoQe21J0PtGG"
DRIVE_EFSA_GUIDANCE_CATALOGUE_ID    = "1H-nchSwcHseNbvRKYHhQLEu4uzZuIi0K"
DRIVE_USDA_NUTRITIONGOV_ID          = "1CBvCaobJR1gcjrDNVEkFYQkWf9CdtFBw"
DRIVE_DGA_USA_2025_ID               = "1YGWrWNw5UyuhUoBO0nBetouNXOyvOGUp"
DRIVE_PAHO_NUTRITION_ID             = "12VV9Z3Ih-lGNRgVmsYcZ5rbXu-Ufv_HP"
DRIVE_UNICEF_NUTRITION_ID           = "1ofEdQqucMDhkawqs9hYJih74G8vzbWD5"
DRIVE_WFP_NUTRITION_ID              = "12vquN3QC7zOO2pZ3ZMK_5lGM3zlovqFN"
DRIVE_GLOBAL_NUTRITION_REPORT_ID    = "1mrlg-1Z1w0C4tka3iGhnw2fAKghuewOC"
DRIVE_EC_KNOWLEDGE4POLICY_ID        = "1ZgjaAy_gORDxfV81_hkKFHDID65ThkOM"
# B. Revistas OA
DRIVE_NUTRIENTS_MDPI_ID             = "1dpZqKFj_Fy2fW99MbBkyUsUwe9zVT-Hq"
DRIVE_CURRENT_DEV_NUTRITION_ID      = "1MaLCbKiJ54myXzvXuTe_g3bUbtTLD7IV"
DRIVE_JOURNAL_NUTRITIONAL_SCIENCE_ID = "1QK7IGyVGA2Zkq4rIH0RhgQ8raBothH7w"
DRIVE_NUTRITION_JOURNAL_BMC_ID      = "1TdJ9RjeWnFiFpGfs2_Hfs8IbC5pCxhqP"
DRIVE_BMC_NUTRITION_ID              = "11Li4seskr1hgU-U-JnsQwYUdnh9iVWTI"
DRIVE_NUTRITION_METABOLISM_ID       = "1QeI_V63U-neFRWlwvTznkNdYQFPQwqNO"
DRIVE_IJBNPA_ID                     = "1i9LVL5AZeLb1mop-OG-v0geAvJQPy5cK"
DRIVE_FOOD_NUTRITION_RESEARCH_ID    = "1JZ-n65ErmkogAYkx74RxflwbdYFIsYzC"
DRIVE_JHPN_ID                       = "1t7GFjmRMl69NqPlImO65YM03UxMlRRNy"
DRIVE_JISSN_SPORTS_NUTR_ID          = "1sf_gJRaVF0z5sQvcYQbDqdqDuz5unl99"
DRIVE_SPORTS_MEDICINE_OPEN_ID       = "1a5XdZiRWkbuMnPwQEjJQDSEamHwdsJ88"
DRIVE_CLINICAL_NUTRITION_OPEN_ID    = "1PIYSgbUXuXggWvQeUawHhJCQ96wTqhdH"
DRIVE_NUTRIRE_JOURNAL_ID            = "1S5ono-_rpFEIKi3Kkoo9vO7pYYFV9yp2"
DRIVE_GENES_NUTRITION_ID            = "1yR2qQTywyuTVqJVfckH3-JK245XcXwA-"
DRIVE_JOURNAL_EATING_DISORDERS_ID   = "1v4uXaOZ2npD-76VXlYssh29IzEcn5kyq"
# C. Bases de composición
DRIVE_USDA_FOODDATA_CENTRAL_ID      = "1toLdVixwpXMM9SxysjNAZzJdozjy5-OJ"
DRIVE_OPEN_FOOD_FACTS_ID            = "1A2cfkcsNcOk0Ze15eHSLE7T4ux3KrfBH"
DRIVE_CANADIAN_NUTRIENT_FILE_ID     = "18OSQ0TJQr-aaofNlFcpQ-tLWs8hRekL4"
DRIVE_CIQUAL_FRANCE_ID              = "1Vt31vV04x4PAGwtq38uPIgfBEv52Rir_"
DRIVE_FINELI_FINLAND_ID             = "18Ya8USER-qUB5LPHAcBWc6KapWgngrEc"
DRIVE_FRIDA_DENMARK_ID              = "1Im3bp1HPRmSxVrrPZVbMgiM08HfWyusz"
DRIVE_COFID_UK_ID                   = "1DYpi6e4UbkR098wEmXH6s-Dyy2jIVllN"
DRIVE_AFCD_AUSTRALIA_ID             = "1e9OVYlNmwCMLWbhzFnnoDz8Tu9zkWe_V"
DRIVE_FOODFILES_NEWZEALAND_ID       = "1wL8hsw6ZiDCJUz2D-y-HZdgjmwNX7RlC"
DRIVE_MATVARETABELLEN_NORWAY_ID     = "156ait0r3l0GQ15tAvk00eUPXugwrpprv"
DRIVE_LIVSMEDELSVERKET_SWEDEN_ID    = "1XJXX6My-5-xSb1sqwEnDBMa5vd8MoYRC"
DRIVE_BEDCA_SPAIN_ID                = "1q_LW1pl_1ptiPusfuL64flgrgQ36kuOf"
DRIVE_TBCA_BRAZIL_ID                = "1twhzWdAfkYeNey2NiYMWldFEp4V1cPNC"
DRIVE_PHENOL_EXPLORER_ID            = "1c3kwhMAWfIEvYBsBlMFCD38LYcpPXFc8"
DRIVE_FOODON_ONTOLOGY_ID            = "1e66tYsMXBNsmWg41mjN4ScbmT7oNQxxv"
# D. Guías dietéticas
DRIVE_FAO_COUNTRY_GUIDELINES_ID     = "1Gfd1rgB1uCIqO0qVEjmKW2YkMFPDh-nD"
DRIVE_DGA_2025_REALFOOD_ID          = "1Yv0stpfRNSPw9DE8NdjOY-WFQaVziYzY"
DRIVE_GUIAS_MEXICO_2023_ID          = "1nYH2lfczVOULlxEnpIFUUMsmJis47XJn"
DRIVE_AESAN_SPAIN_ID                = "1ggcgI9yw0Wu99mdfJZzcJj7LLo4eFFsX"
DRIVE_SACN_UK_ID                    = "14A6XZhHpGfGTxzFugl8RPBNJVDOGvB6-"
DRIVE_CANADA_FOOD_GUIDE_ID          = "1TX8VW04MlOgPedUSwFjoMxzFcbkiezCI"
DRIVE_AUSTRALIA_DIETARY_GUIDELINES_ID = "1-2VQNB6RQRXMKa7zNWJtyRiuCQ39iVqY"
DRIVE_NORDIC_NUTRITION_REC_2023_ID  = "1jkV06sBOLBuPpl501hcL2GVtRG-9lloH"
DRIVE_BRAZIL_DIETARY_GUIDELINES_ID  = "1fJe82hyqm6A7nh--nr9RZaACnvRsMBD0"
DRIVE_NZ_EATING_GUIDELINES_ID       = "1goVw7nF3B2ydDgoAwcvsHiB7YZSKHEJI"
DRIVE_EFSA_DRV_ID                   = "1fdCJ_h-RObv1zxZxDs2a7eTKf9ITdf-X"
DRIVE_JAPAN_DRI_ID                  = "1WhHGrND5OwZ7sO0HGrOMSR8ZjvRO6QOs"
DRIVE_INDIA_DIETARY_GUIDELINES_ID   = "1J2haYTwLbln1MkepYbPg39R1tq_iF-Xo"
# E. Sociedades
DRIVE_AND_EATRIGHT_ID               = "1FP4mPcDp-mvrt1hjniWSxSHHX4ZCQP3A"
DRIVE_ASN_NUTRITION_ID              = "1KkGCcZMZpVNvrNJh01dkQUxOGiFnYegW"
DRIVE_SENC_SPAIN_ID                 = "1T2cjFZySu3Cu0v8juUmE1_19BV1SzRm2"
DRIVE_FESNAD_SPAIN_ID               = "1-H0qvxeIL-bXRw8sJFXqZ8n4wzh5iFDB"
DRIVE_SENPE_SPAIN_ID                = "1P4bUYYQsGUQ95TWUiC-xcELdAqKyODLv"
DRIVE_ESPEN_ID                      = "1o83z48e9hv3vkAzUvZJ8ONjMeD4gcfwo"
DRIVE_ASPEN_CLINICAL_ID             = "1ZqotRGPIOwVkQ6olct7FXCNy5tfH9ysW"
DRIVE_BAPEN_ID                      = "10wTc25CqLXZTUnf6VDaJwZ69KJcKii_i"
DRIVE_BDA_UK_ID                     = "1ZHm38DkhNwgZgKDjfFSKJ-pna_fJWjuW"
DRIVE_NUTRITION_SOCIETY_UK_ID       = "1RJymXXJdT7QE5YUzHrUJMhYX9RqKkylQ"
DRIVE_FELANPE_ID                    = "18ashZFRN8U9FL5gaYo6Eu8N2cseZn8PW"
DRIVE_IUNS_ID                       = "1Tq0fZB1XCeDBkkV-OpY6KOHZH9PylGU-"
DRIVE_FENS_EUROPE_ID                = "1Vmm2NOeGQQi6bJ8sMv_LBxek3TNb6Ebs"
DRIVE_OBESITY_CANADA_ID             = "1I0DywZfAH2W442hHJJ3Ak8E5Lgk8Vz2s"
# F. Nutrición clínica
DRIVE_ESPEN_GUIDELINES_ID           = "1C09QDirRHMfLIy-DVx_AS43BpMespke9"
DRIVE_ASPEN_GUIDELINES_ID           = "1ciocAoyB0FXQKM7AdYRPS0BWADmpaeXx"
DRIVE_BAPEN_MUST_ID                 = "1sYoErmFATgrNd6OjjBtbAX1gp5lXtOhZ"
DRIVE_CRITICAL_CARE_NUTRITION_ID    = "1RhKWzseb9sqq7JXAcG1MoMMvMF_YoV18"
DRIVE_SENPE_GUIAS_ID                = "1xZ6d5ENBhKYzZEkMdl6VcUAFWpBLvMG7"
DRIVE_OBESITY_CANADA_CPG_ID         = "11hNkayitLcIE_3JdhnjuTrSreZnZhpky"
DRIVE_DIABETES_CANADA_NUTR_ID       = "14-c7Gejp72o_6O0MqeJso5-SzzN8LiTR"
DRIVE_DIABETES_UK_NUTR_ID           = "1OLDEeJ2ELWeaX9gq6vGnpewRgIVzgKhq"
DRIVE_IDDSI_DYSPHAGIA_ID            = "1X--tjflRnz2DOy2qva4s1Q7CWTqSZr2a"
DRIVE_ESPGHAN_NUTRITION_ID          = "15S9sHVq-8KngdLGrJKrDsqwoH059i-ei"
DRIVE_CANCER_NUTRITION_ID           = "1IeWHzpNaz98gyM4bULXrYIyVMwJwh8-x"
# G. Nutrición deportiva
DRIVE_ISSN_POSITION_STANDS_ID       = "1qihJK3aSTc7_OJPM8tLyDmVmQTkUcqX7"
DRIVE_AIS_SUPPLEMENT_FRAMEWORK_ID   = "1blIOE3tF_sncEG3JidJrDHZzZUQWS3mH"
DRIVE_OPSS_DOD_ID                   = "1LHCG2UO80w5flwzgEKWKHhEJxCI03Msj"
DRIVE_USADA_SUPPLEMENTS_ID          = "1vo1XXK21IJH7AZvTbCskYJURKS_6RWcr"
DRIVE_NCAA_NUTRITION_ID             = "1KmLgz_06Pe-YpOUEXCSJ-w92L-zEuzWE"
DRIVE_SPORT_INTEGRITY_AU_ID         = "1kSYjZL_KOggeQOG138Z15ofXkGvFbV8V"
# H. Universidades y hospitales
DRIVE_HARVARD_NUTRITION_SOURCE_ID   = "1qP7T7YtwXpaizgtz89jkiD8y-eYTU1ym"
DRIVE_TUFTS_FRIEDMAN_ID             = "1Fpi38mZ6gW2_P9FOoHL2RXTtemBGypXt"
DRIVE_TUFTS_HNRCA_ID                = "1-MeU8po7gEtbZiJLvZtxIxlHRuKBJSpG"
DRIVE_MAYO_CLINIC_NUTRITION_ID      = "10FA8k0gWnRRkpLZfA3REorXYWI0E68Uv"
DRIVE_CLEVELAND_CLINIC_NUTRITION_ID = "1-sqqzdP3p0RK_Kvs-e19Zrx1lepV_9Pn"
DRIVE_JOHNS_HOPKINS_NUTRITION_ID    = "1K3qu0gpSAzkcXCSMGtgzqGiit9FwiCEt"
# I. Microbioma
DRIVE_GMREPO_MICROBIOME_ID          = "12jQLe0VYySsOxqejwuPjnJXFNEKKDYYS"
DRIVE_GUTMDISORDER_ID               = "16g_Z1G1-nQn3iCkABsD24ABZXdIVS-E8"
DRIVE_MGNIFY_NUTRITION_ID           = "1a6FXeic_loxIj4nCa7I0Pv_xN_B2vQ6h"
DRIVE_GUT_MICROBIOTA_HEALTH_ID      = "1ae820tw8HXV6km9A2cKvnc7fvb5NVMV6"
# J. Suplementos y micronutrientes
DRIVE_LINUS_PAULING_MIC_ID          = "1iqx0JwDxU5IQPTteuXCJNHT8ze3N7yr7"
DRIVE_HEALTH_CANADA_LNHPD_ID        = "1HcXQuezxLFFtuNDkYRZX5k7Y59w5VCj5"
DRIVE_OPSS_INGREDIENTS_ID           = "1g65DOeQ25Jqj28-5R9Pst7z0qsCqiVWU"
DRIVE_DOD_PROHIBITED_INGREDIENTS_ID = "1BVKcX-7LwRfx38Ckx_no9RKeAdRW2ASa"
DRIVE_EU_HEALTH_CLAIMS_REGISTER_ID  = "1deSmSfZlebqH28k23uxYds_Gk-l5W30t"
DRIVE_EFSA_HEALTH_CLAIMS_ID         = "14V0NxfMeIWhnKnP1aQrXSc5VZu6Lf6e6"
DRIVE_EFSA_COMPENDIUM_BOTANICALS_ID = "1x6Jun0q6vY447F_nfCaOsosBNQvmPuOY"
DRIVE_ARTG_AUSTRALIA_ID             = "16g4e7d5K2t7YMZi5kmzXwiaT6Epc_wNs"
DRIVE_MSK_ABOUT_HERBS_ID            = "1KtHEr0B_4VVoDZm_MPE11IXwtZck-U9O"

# ── Nuevas (Inventario Complementario 2026-07-26) ──────────────────────────────
DRIVE_NEVO_NETHERLANDS_ID           = "1Nhn7K5HqBKs_2aUWVc-kEIoVz-Gvzzse"
DRIVE_SWISS_FOOD_COMPOSITION_ID     = "1XHFiIjKefM0XYrr0wIpKs1dA60Ui5Ck_"
DRIVE_ASEAN_FOOD_COMPOSITION_ID     = "1uYw-Q6Lp_fq72eMVvF22HS1aU8qqhcSZ"
DRIVE_LANGUAL_TAXONOMY_ID           = "11McpywRRcD9yJmVUsITBeFmBabG07s7D"
DRIVE_FOODB_COMPOUNDS_ID            = "170B0JWvrRi_Ti5m97UDtijbGdF0UiUhP"
DRIVE_FOODREPO_ID                   = "1aM3flpF29fzj-pJBMQPqa0wzdqjrpowo"
DRIVE_GLOBAL_DIETARY_DATABASE_ID    = "1zbMvl8dIo2jNnCjjPQ_smNPHday4Wak5"
DRIVE_GLOBAL_PERSPECTIVES_NUTRITION_ID = "1Kn5yyDnmh45EflrQwfh9l--KwB0mKsoB"
DRIVE_MATERNAL_HEALTH_NEONATOLOGY_NUTR_ID = "1AZUFl_i7RVyNP3eI0lUdnr35F8LN1suv"
DRIVE_HYBRID_NUTRITION_JOURNALS_OA_ID = "1Lv45jSCyCU8DMnfw_lC7FRIqdKhXD8Gk"
DRIVE_KDOQI_KIDNEY_NUTRITION_ID     = "16-KMUA351Hr037ps9mSNa8VhiTuP3UAx"
DRIVE_EASL_LIVER_NUTRITION_ID       = "1nc7yH6ufq2zNk4agPut20Ahe9Xu0DI6S"
DRIVE_CYSTIC_FIBROSIS_NUTRITION_ID  = "1KXzFe21xf0PjRNFTvHNO5CCtg5c4v3z6"
DRIVE_CROHNS_COLITIS_NUTRITION_ID   = "1yNRJ87FamZFc_MprIKFENh1fa0azxDPh"
DRIVE_NATIONAL_LIPID_ASSOC_ID       = "1wtpolVBTxXjZcys2XxUs8Y8ewrPz8K4Y"
DRIVE_CURATED_METAGENOMIC_DATA_ID   = "1JobDCK7x3vRuu01luNQrJL_8t-FF429O"
DRIVE_MICROBIOMEDB_ID               = "1p7tubZ4EQPsvQ70Shy8fNFoY5kQrosst"
DRIVE_DISBIOME_MICROBIOME_ID        = "19VNKRDNOQPLuvQZoRFIqznmoox6JVgBn"
DRIVE_CAM_CANCER_SUMMARIES_ID       = "1DafF-OhX7pi_zFOovUAjhqlX3g-LE6-9"

PROGRESS_FILE = "progress_nutricion.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; HumanNutritionCorpusBot/1.0; research)",
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
    "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# ── Autenticación ──────────────────────────────────────────────────────────────

def get_drive_service():
    with open("token.json") as f:
        d = json.load(f)
    creds = Credentials(
        token=d["token"], refresh_token=d["refresh_token"],
        token_uri=d["token_uri"], client_id=d["client_id"],
        client_secret=d["client_secret"], scopes=d["scopes"],
    )
    return build("drive", "v3", credentials=creds)


# ── Ruteo a carpeta Drive ──────────────────────────────────────────────────────

def folder_for_url(url):
    # A. Organizaciones oficiales
    if "fao.org/infoods"           in url:  return DRIVE_FAO_INFOODS_ID
    if "fao.org/nutrition/education/food-dietary" in url: return DRIVE_FAO_DIETARY_GUIDELINES_ID
    if "codexalimentarius"         in url:  return DRIVE_CODEX_ALIMENTARIUS_ID
    if "fao.org"                   in url:  return DRIVE_FAO_NUTRITION_ID
    if "efsa.europa.eu/en/topics/topic/dietary-reference" in url: return DRIVE_EFSA_NUTRITION_DRV_ID
    if "efsa.europa.eu/en/data-report/food-composition" in url: return DRIVE_EFSA_FOOD_COMPOSITION_ID
    if "efsa.europa.eu/en/applications/guidance" in url: return DRIVE_EFSA_GUIDANCE_CATALOGUE_ID
    if "efsa.europa.eu/en/methodology/guidance" in url: return DRIVE_EFSA_GUIDANCE_CATALOGUE_ID
    if "efsa.europa.eu"            in url:  return DRIVE_EFSA_NUTRITION_DRV_ID
    if "nutrition.gov"             in url:  return DRIVE_USDA_NUTRITIONGOV_ID
    if "dietaryguidelines.gov"     in url or "realfood.gov" in url: return DRIVE_DGA_USA_2025_ID
    if "paho.org"                  in url:  return DRIVE_PAHO_NUTRITION_ID
    if "unicef.org/nutrition"      in url:  return DRIVE_UNICEF_NUTRITION_ID
    if "wfp.org/nutrition"         in url:  return DRIVE_WFP_NUTRITION_ID
    if "globalnutritionreport.org" in url:  return DRIVE_GLOBAL_NUTRITION_REPORT_ID
    if "knowledge4policy.ec.europa.eu" in url: return DRIVE_EC_KNOWLEDGE4POLICY_ID
    # B. Revistas OA
    if "mdpi.com/journal/nutrients" in url or "mdpi.com" in url and "/nutrients/" in url: return DRIVE_NUTRIENTS_MDPI_ID
    if "sciencedirect.com/journal/current-developments-in-nutrition" in url: return DRIVE_CURRENT_DEV_NUTRITION_ID
    if "cambridge.org/core/journals/journal-of-nutritional-science" in url: return DRIVE_JOURNAL_NUTRITIONAL_SCIENCE_ID
    if "nutritionj.biomedcentral.com" in url: return DRIVE_NUTRITION_JOURNAL_BMC_ID
    if "bmcnutr.biomedcentral.com" in url:  return DRIVE_BMC_NUTRITION_ID
    if "nutritionandmetabolism.biomedcentral.com" in url: return DRIVE_NUTRITION_METABOLISM_ID
    if "ijbnpa.biomedcentral.com"  in url:  return DRIVE_IJBNPA_ID
    if "foodandnutritionresearch.net" in url: return DRIVE_FOOD_NUTRITION_RESEARCH_ID
    if "jhpn.biomedcentral.com"    in url:  return DRIVE_JHPN_ID
    # BUGFIX 2026-07-29: excluye la colección "issn-position-stands" (más
    # específica, ver Fase G) para no volverla inalcanzable por shadowing.
    if ("tandfonline.com/journals/rssn" in url and "collections/issn-position-stands" not in url) \
            or "jissn.biomedcentral.com" in url: return DRIVE_JISSN_SPORTS_NUTR_ID
    if "sportsmedicine-open.springeropen.com" in url or "link.springer.com/article/10.1186/s40798" in url: return DRIVE_SPORTS_MEDICINE_OPEN_ID
    if "sciencedirect.com/journal/clinical-nutrition-open-science" in url: return DRIVE_CLINICAL_NUTRITION_OPEN_ID
    if "nutrirejournal.biomedcentral.com" in url: return DRIVE_NUTRIRE_JOURNAL_ID
    if "genesandnutrition.biomedcentral.com" in url: return DRIVE_GENES_NUTRITION_ID
    if "jeatdisord.biomedcentral.com" in url: return DRIVE_JOURNAL_EATING_DISORDERS_ID
    # C. Bases de composición
    if "api.nal.usda.gov/fdc"      in url or "fdc.nal.usda.gov" in url: return DRIVE_USDA_FOODDATA_CENTRAL_ID
    if "openfoodfacts.org"         in url:  return DRIVE_OPEN_FOOD_FACTS_ID
    if "canada.ca" in url and "nutrient" in url: return DRIVE_CANADIAN_NUTRIENT_FILE_ID
    if "ciqual.anses.fr"           in url:  return DRIVE_CIQUAL_FRANCE_ID
    if "fineli.fi"                 in url:  return DRIVE_FINELI_FINLAND_ID
    if "frida.fooddata.dk"         in url:  return DRIVE_FRIDA_DENMARK_ID
    if "gov.uk/government/publications/composition-of-foods" in url: return DRIVE_COFID_UK_ID
    if "foodstandards.gov.au"      in url:  return DRIVE_AFCD_AUSTRALIA_ID
    if "foodcomposition.co.nz"     in url:  return DRIVE_FOODFILES_NEWZEALAND_ID
    if "matvaretabellen.no"        in url:  return DRIVE_MATVARETABELLEN_NORWAY_ID
    if "livsmedelsverket.se"       in url or "dataportal.livsmedelsverket" in url: return DRIVE_LIVSMEDELSVERKET_SWEDEN_ID
    if "bedca.net"                 in url:  return DRIVE_BEDCA_SPAIN_ID
    if "tbca.net.br"               in url:  return DRIVE_TBCA_BRAZIL_ID
    if "phenol-explorer.eu"        in url:  return DRIVE_PHENOL_EXPLORER_ID
    if "foodon.org"                in url:  return DRIVE_FOODON_ONTOLOGY_ID
    # D. Guías dietéticas
    # ORPHANED/INALCANZABLE (flag 2026-07-29, no corregido — requiere
    # decisión de negocio, no de código): "fao.org" ya hace match en la
    # regla general de Fase A (línea ~206, DRIVE_FAO_NUTRITION_ID) ANTES de
    # llegar aquí, y no hay ningún fetcher dedicado exclusivamente a esta
    # sub-ruta — todo el contenido de fetch_fao_nutrition_urls (Fase A) cae
    # en DRIVE_FAO_NUTRITION_ID. DRIVE_FAO_COUNTRY_GUIDELINES_ID nunca se
    # alcanza. No se reordena porque no está claro si es la intención
    # correcta (podría duplicar/fragmentar el contenido de FAO Nutrition).
    if "fao.org/nutrition/education" in url: return DRIVE_FAO_COUNTRY_GUIDELINES_ID
    # ORPHANED/INALCANZABLE (flag 2026-07-29, no corregido): "realfood.gov"
    # ya hace match en la regla general de Fase A (línea ~212,
    # DRIVE_DGA_USA_2025_ID) ANTES de llegar aquí. No hay fetcher dedicado
    # solo a realfood.gov — fetch_dga_usa_urls (Fase A) ya crawlea
    # dietaryguidelines.gov Y realfood.gov juntos hacia esa misma carpeta.
    # DRIVE_DGA_2025_REALFOOD_ID nunca se alcanza.
    if "realfood.gov"              in url:  return DRIVE_DGA_2025_REALFOOD_ID
    if "gob.mx/salud" in url and "guia" in url: return DRIVE_GUIAS_MEXICO_2023_ID
    if "aesan.gob.es"              in url:  return DRIVE_AESAN_SPAIN_ID
    if "sacn" in url or ("gov.uk" in url and "sacn" in url): return DRIVE_SACN_UK_ID
    if "canada.ca/en/health-canada/services/food-guide" in url: return DRIVE_CANADA_FOOD_GUIDE_ID
    if "eatforhealth.gov.au"       in url:  return DRIVE_AUSTRALIA_DIETARY_GUIDELINES_ID
    if "pub.norden.org"            in url or "nordic" in url and "nutrition" in url: return DRIVE_NORDIC_NUTRITION_REC_2023_ID
    if "saude.gov.br"              in url and "nutricao" in url: return DRIVE_BRAZIL_DIETARY_GUIDELINES_ID
    if "health.govt.nz"            in url and ("eat" in url or "nutrition" in url): return DRIVE_NZ_EATING_GUIDELINES_ID
    # ORPHANED/DUPLICADO (flag 2026-07-29, no corregido — requiere decisión
    # de negocio): condición IDÉNTICA a la de Fase A línea ~207
    # ("efsa.europa.eu/en/topics/topic/dietary-reference"), que se evalúa
    # ANTES y devuelve DRIVE_EFSA_NUTRITION_DRV_ID (carpeta DISTINTA). Este
    # DRIVE_EFSA_DRV_ID nunca se alcanza aunque sí existe un fetcher
    # dedicado (fetch_efsa_drv_urls). No se reordena porque no está claro
    # cuál de las dos carpetas de Drive es la correcta/vigente — decidir
    # manualmente si deben fusionarse o si esta debe pasar a ser la
    # ganadora.
    if "efsa.europa.eu/en/topics/topic/dietary-reference" in url: return DRIVE_EFSA_DRV_ID
    if "mhlw.go.jp"                in url:  return DRIVE_JAPAN_DRI_ID
    if "icmr.gov.in"               in url or "nin.res.in" in url: return DRIVE_INDIA_DIETARY_GUIDELINES_ID
    # E. Sociedades
    if "eatrightpro.org"           in url:  return DRIVE_AND_EATRIGHT_ID
    if "nutrition.org"             in url:  return DRIVE_ASN_NUTRITION_ID
    if "nutricioncomunitaria.org"  in url:  return DRIVE_SENC_SPAIN_ID
    if "fesnad.org"                in url:  return DRIVE_FESNAD_SPAIN_ID
    # BUGFIX 2026-07-29: los 5 checks siguientes excluyen su propia sub-ruta
    # F ("/guias", "/guidelines", "/clinical", "/screening") porque antes esta
    # regla general (Sociedades) se evaluaba ANTES que la regla específica de
    # Fase F para el mismo dominio, dejándola inalcanzable (shadowing) pese a
    # existir un fetcher dedicado para esa sub-ruta.
    if "senpe.com" in url and "senpe.com/guias" not in url: return DRIVE_SENPE_SPAIN_ID
    if "espen.org" in url and "espen.org/guidelines" not in url: return DRIVE_ESPEN_ID
    if "nutritioncare.org" in url and "nutritioncare.org/clinical" not in url: return DRIVE_ASPEN_CLINICAL_ID
    if "bapen.org.uk" in url and "bapen.org.uk/screening" not in url: return DRIVE_BAPEN_ID
    if "bda.uk.com"                in url:  return DRIVE_BDA_UK_ID
    if "nutritionsociety.org"      in url:  return DRIVE_NUTRITION_SOCIETY_UK_ID
    if "felanpeweb.org" in url or "felanpe.org" in url: return DRIVE_FELANPE_ID
    if "iuns.org"                  in url:  return DRIVE_IUNS_ID
    if "fensnutrition.org"         in url:  return DRIVE_FENS_EUROPE_ID
    if "obesitycanada.ca" in url and "obesitycanada.ca/guidelines" not in url: return DRIVE_OBESITY_CANADA_ID
    # F. Nutrición clínica
    if "espen.org/guidelines"      in url:  return DRIVE_ESPEN_GUIDELINES_ID
    if "nutritioncare.org/clinical" in url: return DRIVE_ASPEN_GUIDELINES_ID
    if "bapen.org.uk/screening"    in url:  return DRIVE_BAPEN_MUST_ID
    if "criticalcarenutrition.com" in url:  return DRIVE_CRITICAL_CARE_NUTRITION_ID
    if "senpe.com/guias"           in url:  return DRIVE_SENPE_GUIAS_ID
    if "obesitycanada.ca/guidelines" in url: return DRIVE_OBESITY_CANADA_CPG_ID
    if "guidelines.diabetes.ca"    in url:  return DRIVE_DIABETES_CANADA_NUTR_ID
    if "diabetes.org.uk"           in url:  return DRIVE_DIABETES_UK_NUTR_ID
    if "iddsi.org"                 in url:  return DRIVE_IDDSI_DYSPHAGIA_ID
    if "espghan.org"               in url:  return DRIVE_ESPGHAN_NUTRITION_ID
    if "cancer.org.au/health-professionals" in url or "macmillan.org.uk" in url: return DRIVE_CANCER_NUTRITION_ID
    # G. Nutrición deportiva
    if "tandfonline.com/journals/rssn20/collections" in url: return DRIVE_ISSN_POSITION_STANDS_ID
    if "ausport.gov.au/ais/nutrition/supplements" in url or "ais.gov.au/nutrition/supplements" in url: return DRIVE_AIS_SUPPLEMENT_FRAMEWORK_ID
    # BUGFIX 2026-07-29: excluye las dos sub-rutas específicas de Fase J
    # (antes inalcanzables por shadowing pese a tener fetchers dedicados).
    if "opss.org" in url and "opss.org/ingredient" not in url and "opss.org/dod-prohibited" not in url:
        return DRIVE_OPSS_DOD_ID
    if "usada.org/substances/supplement" in url: return DRIVE_USADA_SUPPLEMENTS_ID
    if "ncaa.org" in url and "nutrition" in url: return DRIVE_NCAA_NUTRITION_ID
    if "sportintegrity.gov.au"     in url:  return DRIVE_SPORT_INTEGRITY_AU_ID
    # H. Universidades
    if "nutritionsource.hsph.harvard.edu" in url: return DRIVE_HARVARD_NUTRITION_SOURCE_ID
    if "nutrition.tufts.edu"       in url:  return DRIVE_TUFTS_FRIEDMAN_ID
    if "hnrca.tufts.edu"           in url:  return DRIVE_TUFTS_HNRCA_ID
    if "mayoclinic.org" in url and "nutrition" in url: return DRIVE_MAYO_CLINIC_NUTRITION_ID
    if "health.clevelandclinic.org" in url and "nutrition" in url: return DRIVE_CLEVELAND_CLINIC_NUTRITION_ID
    if "hopkinsmedicine.org" in url and "nutrition" in url: return DRIVE_JOHNS_HOPKINS_NUTRITION_ID
    # I. Microbioma
    if "gmrepo.humangut.info"      in url:  return DRIVE_GMREPO_MICROBIOME_ID
    if "gutmdisorder" in url or "bio-annotation.cn/gutMDisorder" in url: return DRIVE_GUTMDISORDER_ID
    if "ebi.ac.uk/metagenomics"    in url:  return DRIVE_MGNIFY_NUTRITION_ID
    if "gutmicrobiotaforhealth.com" in url: return DRIVE_GUT_MICROBIOTA_HEALTH_ID
    # J. Suplementos
    if "lpi.oregonstate.edu/mic"   in url:  return DRIVE_LINUS_PAULING_MIC_ID
    if "health-products.canada.ca" in url:  return DRIVE_HEALTH_CANADA_LNHPD_ID
    if "opss.org/ingredient"       in url:  return DRIVE_OPSS_INGREDIENTS_ID
    if "opss.org/dod-prohibited"   in url:  return DRIVE_DOD_PROHIBITED_INGREDIENTS_ID
    if "ec.europa.eu/food/food-feed-portal/screen/health-claims" in url: return DRIVE_EU_HEALTH_CLAIMS_REGISTER_ID
    if "efsa.europa.eu" in url and "health-claim" in url: return DRIVE_EFSA_HEALTH_CLAIMS_ID
    if "efsa.europa.eu" in url and "botanical" in url: return DRIVE_EFSA_COMPENDIUM_BOTANICALS_ID
    if "tga.gov.au/resources/artg" in url:  return DRIVE_ARTG_AUSTRALIA_ID
    if "mskcc.org" in url and "herb" in url: return DRIVE_MSK_ABOUT_HERBS_ID

    # ── Nuevas (Inventario Complementario 2026-07-26) ───────────────────────────
    if "|CDN_OA|"                  in url:  return DRIVE_CURRENT_DEV_NUTRITION_ID
    if "|CNOS_OA|"                 in url:  return DRIVE_CLINICAL_NUTRITION_OPEN_ID
    if "|HYBRID_NUTR_OA|"          in url:  return DRIVE_HYBRID_NUTRITION_JOURNALS_OA_ID
    if "|NUTR_METADATA|"           in url:  return DRIVE_NUTRICION_ROOT_ID  # sobreescrito por caller si aplica
    if "rivm.nl"                   in url:  return DRIVE_NEVO_NETHERLANDS_ID
    if "naehrwertdaten.ch"         in url:  return DRIVE_SWISS_FOOD_COMPOSITION_ID
    if "aseanfoods" in url or "inmu.mahidol" in url: return DRIVE_ASEAN_FOOD_COMPOSITION_ID
    if "langual.org"               in url:  return DRIVE_LANGUAL_TAXONOMY_ID
    if "foodb.ca"                  in url:  return DRIVE_FOODB_COMPOUNDS_ID
    if "foodrepo.org"              in url:  return DRIVE_FOODREPO_ID
    if "globaldietarydatabase.org" in url:  return DRIVE_GLOBAL_DIETARY_DATABASE_ID
    if "academic.oup.com/gpn"      in url:  return DRIVE_GLOBAL_PERSPECTIVES_NUTRITION_ID
    if "mhnpjournal.biomedcentral.com" in url: return DRIVE_MATERNAL_HEALTH_NEONATOLOGY_NUTR_ID
    if "kidney.org"                in url:  return DRIVE_KDOQI_KIDNEY_NUTRITION_ID
    if "easl.eu"                   in url:  return DRIVE_EASL_LIVER_NUTRITION_ID
    if "cff.org"                   in url:  return DRIVE_CYSTIC_FIBROSIS_NUTRITION_ID
    if "crohnscolitisfoundation.org" in url: return DRIVE_CROHNS_COLITIS_NUTRITION_ID
    if "lipid.org"                 in url:  return DRIVE_NATIONAL_LIPID_ASSOC_ID
    if "waldronlab.io"             in url:  return DRIVE_CURATED_METAGENOMIC_DATA_ID
    if "microbiomedb.org"          in url:  return DRIVE_MICROBIOMEDB_ID
    if "disbiome.ugent.be"         in url:  return DRIVE_DISBIOME_MICROBIOME_ID
    if "cam-cancer.org"            in url:  return DRIVE_CAM_CANCER_SUMMARIES_ID

    return DRIVE_NUTRICION_ROOT_ID  # fallback


def upload_file(service, url, name, content):
    folder_id = folder_for_url(url)
    media = MediaInMemoryUpload(content.encode("utf-8"), mimetype="text/plain")
    service.files().create(
        body={"name": name, "parents": [folder_id]},
        media_body=media, fields="id"
    ).execute()


# ── Helpers de descubrimiento ──────────────────────────────────────────────────

def fetch_urls_from_sitemap(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code == 429 or not r.ok:
            return []
        root = ET.fromstring(r.text)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        return [el.text for el in root.findall(".//sm:loc", ns) if el.text]
    except ET.ParseError:
        return re.findall(r"<loc>\s*(https?://[^<\s]+)\s*</loc>", r.text if "r" in dir() else "")
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


def _crawl_one_level(seed, domain_prefix, delay=3.0):
    try:
        r = requests.get(seed, headers=HEADERS, timeout=30)
        if not r.ok:
            return []
        soup = BeautifulSoup(r.text, "html.parser")
        urls = set()
        from urllib.parse import urljoin
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith(("javascript:", "mailto:", "tel:", "#")):
                continue
            # BUGFIX 2026-07-29: antes solo se resolvían con urljoin los
            # hrefs que empezaban con "/" (root-relative); los relativos
            # "planos" (p.ej. "articles/foo.html", típicos de sitios
            # generados con pkgdown/Sphinx, como waldronlab.io) se
            # descartaban en silencio porque no empezaban con "http".
            if not href.startswith("http"):
                href = urljoin(seed, href)
            href = href.split("#")[0]  # descarta fragmento (evita duplicados triviales)
            if domain_prefix in href and href.startswith("http"):
                urls.add(href)
        time.sleep(delay)
        return list(urls)
    except Exception:
        return []


def extract_inline_content(inline_str):
    """Convierte 'url|TYPE|json' en texto plano para subir a Drive."""
    parts = inline_str.split("|", 2)
    if len(parts) < 3:
        return inline_str
    url, dtype, payload = parts
    try:
        data = json.loads(payload)
    except Exception:
        return payload
    if dtype == "FDC_FOOD":
        name = data.get("description", "")
        nutrients = data.get("foodNutrients", [])
        lines = [f"FOOD: {name}", f"FDC ID: {data.get('fdcId','')}", f"Category: {data.get('foodCategory','')}",
                 f"Brand: {data.get('brandOwner','')} {data.get('brandName','')}".strip(), ""]
        for n in nutrients[:60]:
            nm = n.get("nutrient", {})
            lines.append(f"  {nm.get('name','')}: {n.get('amount','')} {nm.get('unitName','')}")
        return "\n".join(lines)
    if dtype == "OFF_PRODUCT":
        p = data.get("product", data)
        name = p.get("product_name", p.get("product_name_en", ""))
        lines = [f"PRODUCT: {name}", f"Barcode: {p.get('code','')}",
                 f"Brand: {p.get('brands','')}", f"Country: {p.get('countries','')}", ""]
        nf = p.get("nutriments", {})
        for k, v in list(nf.items())[:30]:
            lines.append(f"  {k}: {v}")
        return "\n".join(lines)
    if dtype == "NORWAY_FOOD":
        lines = [f"MAT: {data.get('foodName','')}",
                 f"ID: {data.get('foodId','')}", f"Group: {data.get('foodGroupName','')}"]
        for comp in data.get("constituents", []):
            lines.append(f"  {comp.get('nutrientName','')}: {comp.get('quantity','')} {comp.get('unit','')}")
        return "\n".join(lines)
    if dtype == "LNHPD_PRODUCT":
        lines = [f"PRODUCT: {data.get('product_name_en','')}",
                 f"NPN: {data.get('npn','')}", f"Company: {data.get('company_name','')}",
                 f"Dosage: {data.get('recommended_dosage_en','')}",
                 f"Purpose: {data.get('recommended_use_en','')}"]
        return "\n".join(lines)
    if dtype == "MGNIFY_STUDY":
        lines = [f"STUDY: {data.get('study_id','')}",
                 f"Title: {data.get('title','')}",
                 f"Biome: {data.get('biome_name','')}",
                 f"Samples: {data.get('samples_count','')}"]
        return "\n".join(lines)
    return json.dumps(data, ensure_ascii=False, indent=2)[:3000]


# ── FASE A: Organizaciones oficiales ──────────────────────────────────────────

def fetch_fao_nutrition_urls():
    # BUGFIX 2026-07-29: ambos seeds anteriores están muertos (404 y 504 —
    # FAO reorganizó /nutrition/*). El hub general "/nutrition" sigue activo
    # (200) y enlaza a todas las sub-secciones (assessment, food-composition,
    # education, policies-programmes, requirements, etc.), así que basta un
    # solo crawl desde ahí.
    return _crawl_one_level("https://www.fao.org/nutrition", "fao.org", delay=4.0)

def fetch_fao_infoods_urls():
    return _crawl_one_level("https://www.fao.org/infoods/infoods/tables-and-databases/en/", "fao.org", delay=4.0)

def fetch_codex_urls():
    return _crawl_one_level("https://www.fao.org/fao-who-codexalimentarius/codex-texts/list-standards/en/", "fao.org", delay=4.0)

def fetch_efsa_nutrition_urls():
    return _fetch_sitemap_index_urls(
        "https://www.efsa.europa.eu/sitemap.xml",
        url_filter=lambda u: any(k in u for k in ["nutrition", "dietary-reference", "diet", "nutrient", "food-composition"]),
        delay=2.0,
    )

def fetch_efsa_guidance_urls():
    # BUGFIX 2026-07-29: /en/applications/guidance devuelve 404 (EFSA
    # reorganizó su sitio); la sección ahora vive bajo /en/methodology/guidance.
    return _crawl_one_level("https://www.efsa.europa.eu/en/methodology/guidance", "efsa.europa.eu", delay=2.0)

def fetch_usda_nutritiongov_urls():
    # BUGFIX 2026-07-29: nutrition.gov/sitemap.xml es un <urlset> PLANO (246
    # páginas reales), no un <sitemapindex>. _fetch_sitemap_index_urls trataba
    # cada página como si fuera, a su vez, otro sitemap XML a re-fetchear —
    # cada intento fallaba (ET.ParseError sobre HTML) y devolvía 0, además de
    # tardar ~15 min recorriendo las 246 "sub-URLs" con delay=2.0 cada una.
    # fetch_urls_from_sitemap() de un solo nivel basta aquí.
    return fetch_urls_from_sitemap("https://www.nutrition.gov/sitemap.xml")

def fetch_dga_usa_urls():
    urls = _crawl_one_level("https://www.dietaryguidelines.gov/resources/", "dietaryguidelines.gov", delay=2.0)
    urls += _crawl_one_level("https://www.realfood.gov/", "realfood.gov", delay=2.0)
    return urls

def fetch_paho_nutrition_urls():
    return _crawl_one_level("https://www.paho.org/en/topics/healthy-diet", "paho.org", delay=3.0)

# Confirmado bloqueado por WAF a nivel de dominio (2026-07-29) — devuelve 403
# incluso para la portada con User-Agent de navegador normal; no evadir.
def fetch_unicef_nutrition_urls():
    return _crawl_one_level("https://www.unicef.org/nutrition", "unicef.org", delay=4.0)

def fetch_wfp_nutrition_urls():
    return _crawl_one_level("https://www.wfp.org/nutrition", "wfp.org", delay=4.0)

def fetch_global_nutrition_report_urls():
    return _crawl_one_level("https://globalnutritionreport.org/", "globalnutritionreport.org", delay=3.0)

# Confirmado bloqueado por WAF a nivel de dominio (2026-07-29) — 403 incluso
# para la portada con User-Agent de navegador normal; no evadir.
def fetch_ec_knowledge4policy_urls():
    return _crawl_one_level(
        "https://knowledge4policy.ec.europa.eu/health-promotion-knowledge-gateway/nutrition_en",
        "knowledge4policy.ec.europa.eu", delay=3.0,
    )


# ── FASE B: Revistas OA ───────────────────────────────────────────────────────

# Confirmado bloqueado por WAF a nivel de dominio (2026-07-29) — 403 incluso
# para la portada con User-Agent de navegador normal; no evadir.
def fetch_nutrients_mdpi_urls():
    return _fetch_sitemap_index_urls(
        "https://www.mdpi.com/sitemap/sitemap-nutrients.xml",
        url_filter=lambda u: "/nutrients/" in u and "/article" in u,
        delay=8.0,
    )

def _fetch_springer_journal_articles(journal_slug, max_pages=20, delay=2.0):
    """BUGFIX 2026-07-29: *.biomedcentral.com/*.springeropen.com/sitemap.xml
    redirige al sitemap GLOBAL de Springer (todas sus revistas, millones de
    URLs) — no sirve para acotar a una sola revista (se detectó con ISSN
    Nutrition en scraper_deporte.py devolviendo 9,968,660 URLs). El
    subdominio dedicado de cada revista sí está bien acotado; se recorre su
    listado paginado de artículos en su lugar."""
    base = f"https://{journal_slug}.biomedcentral.com"
    urls = set()
    for page in range(1, max_pages + 1):
        try:
            seed = f"{base}/articles" if page == 1 else f"{base}/articles?page={page}"
            r = requests.get(seed, headers=HEADERS, timeout=30)
            if not r.ok:
                break
            soup = BeautifulSoup(r.text, "html.parser")
            page_urls = {base + a["href"] for a in soup.find_all("a", href=True)
                         if a["href"].startswith("/article/10.")}
            if not page_urls or not (page_urls - urls):
                urls |= page_urls
                break
            urls |= page_urls
            time.sleep(delay)
        except Exception:
            break
    return list(urls)


def fetch_nutrition_journal_bmc_urls():
    return _fetch_springer_journal_articles("nutritionj")

def fetch_bmc_nutrition_urls():
    return _fetch_springer_journal_articles("bmcnutr")

def fetch_nutrition_metabolism_urls():
    return _fetch_springer_journal_articles("nutritionandmetabolism")

def fetch_ijbnpa_urls():
    return _fetch_springer_journal_articles("ijbnpa")

def fetch_food_nutrition_research_urls():
    return _crawl_one_level(
        "https://foodandnutritionresearch.net/index.php/fnr/issue/archive",
        "foodandnutritionresearch.net", delay=2.0,
    )

def fetch_jhpn_urls():
    return _fetch_springer_journal_articles("jhpn")

def fetch_jissn_urls():
    return _fetch_springer_journal_articles("jissn")

def fetch_sports_medicine_open_urls(max_pages=20, delay=2.0):
    """BUGFIX 2026-07-29: sportsmedicine-open.springeropen.com migró por
    completo a la plataforma link.springer.com — incluso los artículos
    individuales redirigen ahí — así que devolvía 404/0 con el patrón
    compartido de _fetch_springer_journal_articles (que asume subdominio
    *.biomedcentral.com). El ID de revista de Springer para "Sports
    Medicine - Open" es 40798 (prefijo DOI 10.1186/s40798-...)."""
    listing_base = "https://link.springer.com/journal/40798"
    link_domain = "https://link.springer.com"
    urls = set()
    for page in range(1, max_pages + 1):
        try:
            seed = f"{listing_base}/articles" if page == 1 else f"{listing_base}/articles?page={page}"
            r = requests.get(seed, headers=HEADERS, timeout=30)
            if not r.ok:
                break
            soup = BeautifulSoup(r.text, "html.parser")
            page_urls = {link_domain + a["href"] for a in soup.find_all("a", href=True)
                         if a["href"].startswith("/article/10.1186/s40798-")}
            if not page_urls or not (page_urls - urls):
                urls |= page_urls
                break
            urls |= page_urls
            time.sleep(delay)
        except Exception:
            break
    return list(urls)

def fetch_nutrire_urls():
    return _fetch_springer_journal_articles("nutrirejournal")

def fetch_genes_nutrition_urls():
    return _fetch_springer_journal_articles("genesandnutrition")

def fetch_journal_nutritional_science_urls():
    return _crawl_one_level(
        "https://www.cambridge.org/core/journals/journal-of-nutritional-science/listing?",
        "cambridge.org/core/journals/journal-of-nutritional-science", delay=5.0,
    )


# ── FASE C: Bases de composición de alimentos (API inline) ───────────────────

FDC_API_KEY = "DEMO_KEY"  # reemplazar con tu API key propia para producción
# CONFIRMADO (2026-07-29): DEMO_KEY está actualmente rate-limited por USDA —
# la PRIMERA request en una prueba aislada ya devolvió 429 OVER_RATE_LIMIT
# ("You have exceeded your rate limit"). El código ya maneja el 429 con un
# backoff de 60s y reintenta, pero con 3 dataTypes × 25 páginas eso puede
# significar hasta 75 esperas de 60s (~75 min) en el peor caso — se observó
# en vivo que esta fuente no terminó dentro de un budget de 25 min. No es un
# bug de código: requiere una API key real de
# https://fdc.nal.usda.gov/api-key-signup (no se genera aquí — crear cuentas
# está fuera de alcance de esta auditoría). Dejar como TODO para el usuario.
def fetch_fdc_urls():
    """USDA FoodData Central API — primeros 5,000 alimentos de Foundation y SR."""
    base = "https://api.nal.usda.gov/fdc/v1/foods/list"
    urls = []
    for dtype in ["Foundation", "SR Legacy", "Survey (FNDDS)"]:
        params = {"dataType": dtype, "pageSize": 200, "pageNumber": 1, "api_key": FDC_API_KEY}
        for page in range(1, 26):  # máx 25 páginas × 200 = 5,000 por tipo
            params["pageNumber"] = page
            try:
                r = requests.get(base, params=params, headers=HEADERS, timeout=30)
                if r.status_code == 429:
                    time.sleep(60)
                    continue
                items = r.json()
                if not items:
                    break
                for item in items:
                    fdc_id = item.get("fdcId")
                    if fdc_id:
                        urls.append(f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}|FDC_FOOD|{{\"fdcId\":{fdc_id}}}")
                time.sleep(1.0)
            except Exception:
                break
    return urls

def fetch_open_food_facts_urls():
    """Open Food Facts API — sample de 1,000 productos bien documentados."""
    base = "https://world.openfoodfacts.org/cgi/search.pl"
    urls = []
    for page in range(1, 11):  # 10 páginas × 100 = 1,000
        params = {
            "action": "process", "json": 1, "page_size": 100,
            "page": page, "sort_by": "unique_scans_n",
            "fields": "code,product_name,product_name_en,brands,countries,nutriments,categories",
        }
        try:
            r = requests.get(base, params=params, headers=HEADERS, timeout=30)
            data = r.json()
            for p in data.get("products", []):
                code = p.get("code")
                if code:
                    urls.append(f"https://world.openfoodfacts.org/product/{code}|OFF_PRODUCT|{json.dumps({'product':p})}")
            time.sleep(1.5)
        except Exception:
            break
    return urls

def fetch_norway_food_urls():
    """Matvaretabellen Norway REST API — todos los alimentos.
    BUGFIX 2026-07-29: "/api/foods?language=en" devuelve 404 (endpoint
    muerto). El endpoint vigente es "/api/nb/foods.json" y responde un
    objeto {"foods": [...], "locale": ...} en vez de una lista directa."""
    base = "https://www.matvaretabellen.no/api/nb/foods.json"
    try:
        r = requests.get(base, headers=HEADERS, timeout=30)
        data = r.json()
        foods = data.get("foods", []) if isinstance(data, dict) else data
        urls = []
        for food in foods[:2000]:
            fid = food.get("foodId")
            fname = food.get("foodName", "")
            if fid:
                urls.append(f"https://www.matvaretabellen.no/api/food/{fid}/en|NORWAY_FOOD|{json.dumps({'foodId':fid,'foodName':fname})}")
        return urls
    except Exception:
        return []

# Confirmado (2026-07-29): la portada responde 200 pero es un shell casi
# vacío (1145 bytes, 0 <a>) — SPA renderizada por JS del lado del cliente, no
# crawleable con requests+BeautifulSoup. No es un bug de URL ni WAF.
def fetch_ciqual_urls():
    return _crawl_one_level("https://ciqual.anses.fr/", "ciqual.anses.fr", delay=2.0)

def fetch_fineli_urls():
    return _crawl_one_level("https://fineli.fi/fineli/en/foods?", "fineli.fi", delay=2.0)

# Confirmado bloqueado a nivel de dominio (2026-07-29) — la portada tampoco
# conecta (connection refused/timeout) ni siquiera con User-Agent de
# navegador normal; no evadir.
def fetch_phenol_explorer_urls():
    return _crawl_one_level("https://phenol-explorer.eu/compounds", "phenol-explorer.eu", delay=2.0)

# Confirmado (2026-07-29): status 200 pero navegación 100% vía
# "javascript:void(0)" (onclick), sin <a href> reales — no crawleable con
# requests+BeautifulSoup. No es un bug de URL ni WAF.
def fetch_bedca_urls():
    return _crawl_one_level("https://www.bedca.net/bdpub/index_en.php", "bedca.net", delay=4.0)

# Confirmado (2026-07-29): el servidor de TBCA responde 302 con cabecera
# "Location" VACÍA (bug del lado de TBCA, verificado con curl -v) — no hay
# adónde redirigir, así que requests no puede seguir el enlace. No es
# corregible desde el cliente.
def fetch_tbca_urls():
    return _crawl_one_level("https://www.tbca.net.br/base-dados/int_composicao_alimentos.php", "tbca.net.br", delay=4.0)


# ── FASE D: Guías dietéticas ──────────────────────────────────────────────────

# AMBIGUO (2026-07-29): el seed específico ni siquiera conecta (000/timeout),
# aunque el dominio dietaryguidelines.gov sí responde para otras rutas (ver
# fetch_dga_usa_urls en Fase A, que ya crawlea "/resources/" general y
# probablemente cubre este mismo contenido). No se encontró con confianza
# una URL de reemplazo — dejar así en vez de adivinar; posible duplicado.
def fetch_dga_2025_urls():
    return _crawl_one_level("https://www.dietaryguidelines.gov/resources/2025-2030-dietary-guidelines-americans", "dietaryguidelines.gov", delay=2.0)

def fetch_sacn_uk_urls():
    return _crawl_one_level(
        "https://www.gov.uk/government/collections/sacn-reports-and-position-statements",
        "gov.uk", delay=2.0,
    )

def fetch_canada_food_guide_urls():
    return _crawl_one_level("https://www.canada.ca/en/health-canada/services/food-guide.html", "canada.ca", delay=2.0)

def fetch_canada_dri_urls():
    return _crawl_one_level(
        "https://www.canada.ca/en/health-canada/services/food-nutrition/healthy-eating/dietary-reference-intakes/tables.html",
        "canada.ca", delay=2.0,
    )

# Confirmado bloqueado a nivel de dominio (2026-07-29) — eatforhealth.gov.au
# no conecta (connection refused/timeout) ni siquiera en la portada con
# User-Agent de navegador normal; no evadir. Afecta a las 2 fuentes de este
# dominio (guidelines y NRV).
def fetch_australia_guidelines_urls():
    return _crawl_one_level("https://www.eatforhealth.gov.au/guidelines", "eatforhealth.gov.au", delay=2.0)

def fetch_australia_nrv_urls():
    return _crawl_one_level("https://www.eatforhealth.gov.au/nutrient-reference-values", "eatforhealth.gov.au", delay=2.0)

# Confirmado bloqueado por WAF a nivel de dominio (2026-07-29) — 403 incluso
# para la portada con User-Agent de navegador normal; no evadir.
def fetch_nordic_nutrition_urls():
    return _crawl_one_level("https://pub.norden.org/nord2023-003/", "pub.norden.org", delay=2.0)

def fetch_efsa_drv_urls():
    return _crawl_one_level(
        "https://www.efsa.europa.eu/en/topics/topic/dietary-reference-values",
        "efsa.europa.eu", delay=2.0,
    )

def fetch_aesan_spain_urls():
    # AMBIGUO (2026-07-29): esta ruta específica (legado "AECOSAN") devuelve
    # 403 "Forbidden" incluso con User-Agent de navegador normal, aunque la
    # portada de aesan.gob.es sí responde 200 — parece una ruta antigua
    # bloqueada/retirada tras la fusión AECOSAN→AESAN. No se encontró en la
    # portada un enlace de reemplazo claro (navegación probablemente vía JS);
    # se deja así en vez de adivinar.
    return _crawl_one_level("https://www.aesan.gob.es/AECOSAN/web/nutricion/", "aesan.gob.es", delay=3.0)

# AMBIGUO (2026-07-29): este seed devuelve 404; el subsitio gob.mx/salud está
# activo (200 en varias rutas probadas: /salud, /salud/es/,
# /salud/archivo/documentos) pero no se localizó con confianza la página
# vigente de "guías alimentarias" (sin resultados de "guia" en el listado de
# documentos revisado, y varias rutas candidatas dieron excepción de
# conexión). Se deja así en vez de adivinar.
def fetch_mexico_guias_urls():
    return _crawl_one_level(
        "https://www.gob.mx/salud/documentos/guias-alimentarias-saludables-y-sostenibles-para-la-poblacion-mexicana-2023",
        "gob.mx", delay=3.0,
    )


# ── FASE E: Sociedades profesionales ──────────────────────────────────────────

# Confirmado bloqueado (2026-07-29) — tanto el seed como la portada de
# eatrightpro.org redirigen a un bucle de SSO/PassiveAuthentication (login
# wall) en vez de servir la página pública; no evadir/loguear.
def fetch_and_eatright_urls():
    return _crawl_one_level("https://www.eatrightpro.org/practice/position-and-practice-papers", "eatrightpro.org", delay=5.0)

def fetch_asn_nutrition_urls():
    # BUGFIX 2026-07-29: /policy-and-advocacy/ devuelve 404; ASN reorganizó su
    # sitio, la sección ahora vive bajo /public-affairs/asn-advocacy/.
    return _crawl_one_level("https://nutrition.org/public-affairs/asn-advocacy/", "nutrition.org", delay=5.0)

def fetch_senc_spain_urls():
    urls = fetch_urls_from_sitemap("https://www.nutricioncomunitaria.org/wp-sitemap.xml")
    if not urls:
        urls = _crawl_one_level("https://www.nutricioncomunitaria.org/", "nutricioncomunitaria.org", delay=4.0)
    return urls

def fetch_fesnad_urls():
    return _crawl_one_level("https://www.fesnad.org/", "fesnad.org", delay=5.0)

def fetch_senpe_urls():
    urls = fetch_urls_from_sitemap("https://senpe.com/wp-sitemap.xml")
    if not urls:
        urls = _crawl_one_level("https://senpe.com/guias/", "senpe.com", delay=4.0)
    return urls

# Confirmado bloqueado (2026-07-29) — verificado con curl: un User-Agent de
# navegador normal recibe 200, pero el User-Agent propio del scraper
# ("...HumanNutritionCorpusBot...") recibe 403 (WAF/Cloudflare filtrando por
# UA). Por regla de auditoría no se cambia el User-Agent para evadirlo
# (afectaría a los ~70 fetchers que comparten HEADERS); no evadir.
def fetch_espen_urls():
    return _crawl_one_level("https://www.espen.org/guidelines-home/espen-guidelines", "espen.org", delay=5.0)

def fetch_aspen_urls():
    return _crawl_one_level("https://nutritioncare.org/clinical-resources/guidelines-standards/", "nutritioncare.org", delay=5.0)

def fetch_bapen_urls():
    urls = fetch_urls_from_sitemap("https://www.bapen.org.uk/wp-sitemap.xml")
    if not urls:
        urls = _crawl_one_level("https://www.bapen.org.uk/", "bapen.org.uk", delay=4.0)
    return urls

def fetch_bda_uk_urls():
    # BUGFIX 2026-07-29: /resource/food-facts.html devuelve 404; la sección
    # de food facts se movió a /food-health/food-facts.html.
    return _crawl_one_level("https://www.bda.uk.com/food-health/food-facts.html", "bda.uk.com", delay=5.0)

def fetch_nutrition_society_uk_urls():
    return _crawl_one_level("https://www.nutritionsociety.org/", "nutritionsociety.org", delay=5.0)

def fetch_felanpe_urls():
    # BUGFIX 2026-07-29: felanpeweb.org devuelve 200 pero su HTML ya no tiene
    # navegación propia — todos los enlaces internos apuntan a felanpe.org
    # (el sitio real se consolidó ahí). Se crawlea felanpe.org directamente.
    return _crawl_one_level("https://felanpe.org/", "felanpe.org", delay=5.0)

# Confirmado bloqueado (2026-07-29) — igual que espen.org: 200 con
# User-Agent de navegador, 403 con el User-Agent propio del scraper (WAF por
# UA, probablemente el mismo plugin de seguridad WordPress/Cloudflare). No
# evadir cambiando el User-Agent compartido.
def fetch_iuns_urls():
    urls = fetch_urls_from_sitemap("https://iuns.org/wp-sitemap.xml")
    if not urls:
        urls = _crawl_one_level("https://iuns.org/", "iuns.org", delay=5.0)
    return urls

# Confirmado bloqueado (2026-07-29) — mismo patrón: 200 con User-Agent de
# navegador, 403 con el User-Agent propio del scraper. No evadir.
def fetch_fens_urls():
    return _crawl_one_level("https://fensnutrition.org/", "fensnutrition.org", delay=5.0)

def fetch_obesity_canada_urls():
    return _crawl_one_level("https://obesitycanada.ca/resources/", "obesitycanada.ca", delay=4.0)


# ── FASE F: Nutrición clínica ─────────────────────────────────────────────────

# NOTA (2026-07-29): mismo bloqueo por User-Agent que fetch_espen_urls (ver
# comentario ahí) — además esta función es literalmente duplicada de
# fetch_espen_urls (mismo seed exacto). No se elimina la duplicación por
# quedar fuera de alcance de esta auditoría; ambas quedan afectadas por el
# mismo bloqueo WAF.
def fetch_espen_guidelines_urls():
    return _crawl_one_level("https://www.espen.org/guidelines-home/espen-guidelines", "espen.org", delay=5.0)

def fetch_aspen_guidelines_urls():
    return _crawl_one_level("https://nutritioncare.org/clinical-resources/guidelines-standards/", "nutritioncare.org", delay=5.0)

def fetch_bapen_must_urls():
    return _crawl_one_level("https://www.bapen.org.uk/screening-and-must/must/", "bapen.org.uk", delay=4.0)

def fetch_critical_care_nutrition_urls():
    return _crawl_one_level("https://www.criticalcarenutrition.com/", "criticalcarenutrition.com", delay=3.0)

def fetch_obesity_canada_cpg_urls():
    return _crawl_one_level("https://obesitycanada.ca/guidelines/", "obesitycanada.ca", delay=4.0)

def fetch_diabetes_canada_urls():
    return _crawl_one_level("https://guidelines.diabetes.ca/", "guidelines.diabetes.ca", delay=3.0)

# AMBIGUO (2026-07-29): este seed devuelve 404; la portada de diabetes.org.uk
# responde 200 pero no se localizaron enlaces de nutrición/dieta en un
# escaneo simple de la portada (navegación probablemente vía JS/mega-menú).
# No se encontró con confianza una URL de reemplazo — se deja así.
def fetch_diabetes_uk_urls():
    return _crawl_one_level(
        "https://www.diabetes.org.uk/for-professionals/supporting-your-patients/clinical-recommendations-for-professionals/evidence-based-nutrition-guidelines",
        "diabetes.org.uk", delay=4.0,
    )

def fetch_iddsi_urls():
    return _crawl_one_level("https://iddsi.org/", "iddsi.org", delay=3.0)

def fetch_espghan_urls():
    return _crawl_one_level("https://www.espghan.org/knowledge-center/publications/", "espghan.org", delay=5.0)

def fetch_cancer_nutrition_urls():
    urls = _crawl_one_level("https://www.cancer.org.au/health-professionals/clinical-practice-guidelines", "cancer.org.au", delay=4.0)
    urls += _crawl_one_level(
        "https://www.macmillan.org.uk/cancer-information-and-support/treatment/coping-with-treatment/eating-problems",
        "macmillan.org.uk", delay=4.0,
    )
    return urls


# ── FASE G: Nutrición deportiva ───────────────────────────────────────────────

def fetch_issn_position_stands_urls():
    return _crawl_one_level(
        "https://www.tandfonline.com/journals/rssn20/collections/issn-position-stands",
        "tandfonline.com", delay=5.0,
    )

def fetch_ais_supplement_urls():
    return _crawl_one_level("https://www.ais.gov.au/nutrition/supplements", "ais.gov.au", delay=3.0)

def fetch_opss_dod_urls():
    urls = _crawl_one_level("https://www.opss.org/ingredient-and-substance-index", "opss.org", delay=2.0)
    urls += _crawl_one_level("https://www.opss.org/dod-prohibited-dietary-supplement-ingredients", "opss.org", delay=2.0)
    return urls

def fetch_usada_supplements_urls():
    return _crawl_one_level("https://www.usada.org/substances/supplement-connect/", "usada.org", delay=3.0)

def fetch_ncaa_nutrition_urls():
    return _crawl_one_level("https://www.ncaa.org/sports/2016/7/20/nutrition-sleep-and-performance.aspx", "ncaa.org", delay=4.0)

# Confirmado bloqueado a nivel de dominio (2026-07-29) — sportintegrity.gov.au
# no conecta (connection refused/timeout) ni siquiera en la portada con
# User-Agent de navegador normal; no evadir.
def fetch_sport_integrity_au_urls():
    return _crawl_one_level(
        "https://www.sportintegrity.gov.au/what-we-do/anti-doping/supplements-sport",
        "sportintegrity.gov.au", delay=3.0,
    )


# ── FASE H: Universidades y hospitales ───────────────────────────────────────

def fetch_harvard_nutrition_source_urls():
    urls = fetch_urls_from_sitemap("https://nutritionsource.hsph.harvard.edu/wp-sitemap.xml")
    if not urls:
        urls = _crawl_one_level("https://nutritionsource.hsph.harvard.edu/", "nutritionsource.hsph.harvard.edu", delay=5.0)
    return urls

def fetch_tufts_friedman_urls():
    return _crawl_one_level("https://nutrition.tufts.edu/", "nutrition.tufts.edu", delay=5.0)

def fetch_tufts_hnrca_urls():
    return _crawl_one_level("https://hnrca.tufts.edu/", "hnrca.tufts.edu", delay=5.0)

# Confirmado bloqueado por WAF a nivel de dominio (2026-07-29) — 403 incluso
# para la portada con User-Agent de navegador normal; no evadir.
def fetch_mayo_clinic_nutrition_urls():
    return _fetch_sitemap_index_urls(
        "https://www.mayoclinic.org/sitemap.xml",
        url_filter=lambda u: "nutrition" in u or "healthy-eating" in u or "diet" in u,
        delay=5.0,
    )

def fetch_cleveland_clinic_nutrition_urls():
    return _fetch_sitemap_index_urls(
        "https://health.clevelandclinic.org/sitemap.xml",
        url_filter=lambda u: "nutrition" in u or "diet" in u or "food" in u,
        delay=10.0,
    )

def fetch_johns_hopkins_nutrition_urls():
    return _crawl_one_level(
        "https://www.hopkinsmedicine.org/health/wellness-and-prevention/food-and-nutrition",
        "hopkinsmedicine.org", delay=5.0,
    )


# ── FASE I: Microbioma ────────────────────────────────────────────────────────

# Confirmado (2026-07-29): la portada responde 200 pero es un shell Vue.js
# vacío (id="app", 687 bytes) — SPA renderizada por JS del lado del cliente,
# no crawleable con requests+BeautifulSoup. No es un bug de URL ni WAF.
def fetch_gmrepo_urls():
    return _crawl_one_level("https://gmrepo.humangut.info/", "gmrepo.humangut.info", delay=3.0)

# Confirmado bloqueado/inalcanzable (2026-07-29) — bio-annotation.cn no
# conecta (connection refused/timeout) ni siquiera en la portada; posible
# sitio académico descontinuado. No evadir.
def fetch_gutmdisorder_urls():
    return _crawl_one_level("http://bio-annotation.cn/gutMDisorder/", "bio-annotation.cn", delay=3.0)

def fetch_mgnify_nutrition_urls():
    """MGnify API — estudios con términos de dieta en biome intestinal.
    BUGFIX 2026-07-29: el parámetro "biome_name=Human:Gut" no coincide con
    ningún biome real de la API (devolvía count=0) — la API espera el
    lineage completo vía el parámetro "lineage", p.ej.
    "root:Host-associated:Human:Digestive system" (verificado: 586 estudios)."""
    base = "https://www.ebi.ac.uk/metagenomics/api/v1/studies"
    urls = []
    params = {"lineage": "root:Host-associated:Human:Digestive system", "page_size": 50, "page": 1}
    for _ in range(10):
        try:
            r = requests.get(base, params=params, headers=HEADERS, timeout=30)
            data = r.json()
            for study in data.get("data", []):
                sid = study.get("id", "")
                title = study.get("attributes", {}).get("study-name", "")
                payload = json.dumps({"study_id": sid, "title": title})
                urls.append(f"https://www.ebi.ac.uk/metagenomics/studies/{sid}|MGNIFY_STUDY|{payload}")
            next_url = data.get("links", {}).get("next")
            if not next_url:
                break
            params["page"] += 1
            time.sleep(1.0)
        except Exception:
            break
    return urls

def fetch_gut_microbiota_health_urls():
    urls = fetch_urls_from_sitemap("https://www.gutmicrobiotaforhealth.com/wp-sitemap.xml")
    if not urls:
        urls = _crawl_one_level("https://www.gutmicrobiotaforhealth.com/", "gutmicrobiotaforhealth.com", delay=4.0)
    return urls


# ── FASE J: Suplementos y micronutrientes ─────────────────────────────────────

def fetch_linus_pauling_mic_urls():
    return _crawl_one_level("https://lpi.oregonstate.edu/mic", "lpi.oregonstate.edu", delay=5.0)

# AMBIGUO (2026-07-29): el endpoint devuelve 404 y health-products.canada.ca
# responde de forma inconsistente según la ruta (403 en la raíz, 200 en
# /lnhpd-bdpsnh/ que es la UI HTML de búsqueda, no la API JSON; varias rutas
# de API alternativas probadas dieron excepción de conexión). No se encontró
# con confianza el endpoint JSON vigente — se deja así en vez de adivinar.
def fetch_health_canada_lnhpd_urls():
    """Health Canada LNHPD API — primeros 1,000 productos naturales licenciados."""
    base = "https://health-products.canada.ca/api/natural-licenced-natural-health-products/"
    urls = []
    for page in range(0, 10):
        try:
            r = requests.get(f"{base}?lang=en&type=json&start={page*100}&length=100",
                             headers=HEADERS, timeout=30)
            items = r.json()
            if not items:
                break
            for item in items:
                npn = item.get("npn", "")
                name = item.get("product_name_en", "")
                payload = json.dumps({"npn": npn, "product_name_en": name,
                                      "company_name": item.get("company_name", ""),
                                      "recommended_use_en": item.get("recommended_use_en", "")})
                urls.append(f"https://health-products.canada.ca/lnhpd-bdpsnh/info.do?licence={npn}|LNHPD_PRODUCT|{payload}")
            time.sleep(1.0)
        except Exception:
            break
    return urls

def fetch_opss_ingredients_urls():
    return _crawl_one_level("https://www.opss.org/ingredient-and-substance-index", "opss.org", delay=2.0)

# Confirmado (2026-07-29): status 200, página de 94KB pero con 0 etiquetas
# <a> — es una SPA Angular (EU Register on nutrition and health claims), no
# crawleable con requests+BeautifulSoup. No es un bug de URL ni WAF.
def fetch_eu_health_claims_urls():
    return _crawl_one_level(
        "https://ec.europa.eu/food/food-feed-portal/screen/health-claims/eu-register",
        "ec.europa.eu", delay=3.0,
    )

def fetch_efsa_health_claims_urls():
    return _crawl_one_level(
        "https://www.efsa.europa.eu/en/topics/topic/health-claims",
        "efsa.europa.eu", delay=2.0,
    )

def fetch_efsa_botanicals_urls():
    # BUGFIX 2026-07-29: /en/topics/topic/compendium-botanicals devuelve 404;
    # el compendio vive ahora bajo /en/data-report/compendium-botanicals.
    return _crawl_one_level(
        "https://www.efsa.europa.eu/en/data-report/compendium-botanicals",
        "efsa.europa.eu", delay=2.0,
    )

# Confirmado bloqueado a nivel de dominio (2026-07-29) — tga.gov.au no
# conecta (connection refused/timeout) ni siquiera en la portada con
# User-Agent de navegador normal; no evadir.
def fetch_artg_australia_urls():
    return _crawl_one_level("https://www.tga.gov.au/resources/artg", "tga.gov.au", delay=3.0)

def fetch_msk_herbs_urls():
    return _crawl_one_level(
        "https://www.mskcc.org/cancer-care/diagnosis-treatment/symptom-management/integrative-medicine/herbs/search",
        "mskcc.org", delay=5.0,
    )


# ── Fetchers nuevos (Inventario Complementario, 2026-07-26) ────────────────────

def _make_nutr_metadata_record(source_url, title, notes):
    payload = {"title": title, "source_url": source_url, "notes": notes}
    return f"{source_url}|NUTR_METADATA|{json.dumps(payload, ensure_ascii=False)}"


def _fetch_crossref_unpaywall_oa(journal_name, marker, rows=40):
    """Resuelve DOI/PMID vía Crossref y localiza copia OA vía Unpaywall — evita
    crawling directo de publishers híbridos (ScienceDirect, Wiley, OUP, etc.)."""
    urls = []
    try:
        r = requests.get("https://api.crossref.org/works",
                          params={"query.container-title": journal_name, "rows": rows,
                                   "filter": "has-full-text:true"},
                          headers=HEADERS, timeout=30)
        items = r.json().get("message", {}).get("items", [])
        for it in items:
            doi = it.get("DOI", "")
            if not doi:
                continue
            try:
                ur = requests.get(f"https://api.unpaywall.org/v2/{doi}",
                                   params={"email": "jlps1977@gmail.com"}, headers=HEADERS, timeout=15)
                data = ur.json()
                if data.get("is_oa"):
                    best = data.get("best_oa_location") or {}
                    oa_url = best.get("url_for_pdf") or best.get("url") or ""
                    if oa_url:
                        urls.append(f"{oa_url}|{marker}|"
                                    f"{json.dumps({'title': data.get('title', ''), 'doi': doi, 'journal': journal_name})}")
                time.sleep(1.0)
            except Exception:
                continue
    except Exception:
        pass
    return urls

def fetch_current_dev_nutrition_oa_urls():
    return _fetch_crossref_unpaywall_oa("Current Developments in Nutrition", "CDN_OA")

def fetch_clinical_nutrition_open_oa_urls():
    return _fetch_crossref_unpaywall_oa("Clinical Nutrition Open Science", "CNOS_OA")

HYBRID_NUTRITION_JOURNALS_B2 = [
    "American Journal of Clinical Nutrition", "The Journal of Nutrition",
    "Advances in Nutrition", "British Journal of Nutrition",
    "Public Health Nutrition", "Nutrition Reviews",
    "European Journal of Clinical Nutrition", "Maternal & Child Nutrition",
    "Clinical Nutrition", "Journal of Parenteral and Enteral Nutrition",
    "Food & Function", "Nutrition, Metabolism and Cardiovascular Diseases",
]

def fetch_hybrid_nutrition_journals_urls():
    urls = []
    for journal in HYBRID_NUTRITION_JOURNALS_B2:
        urls += _fetch_crossref_unpaywall_oa(journal, "HYBRID_NUTR_OA")
    return urls

# C. Bases de composición — folders ya reservados, sin fetcher hasta ahora
def fetch_afcd_australia_urls():
    return _crawl_one_level(
        "https://www.foodstandards.gov.au/science-data/monitoringnutrients/afcd",
        "foodstandards.gov.au", delay=3.0)

# Confirmado (2026-07-29): el servidor de foodcomposition.co.nz presenta un
# certificado TLS autofirmado/cadena incompleta (SSLCertVerificationError
# bajo el trust store por defecto de Python/certifi; curl con su propio
# trust store del sistema no se queja). No se desactiva la verificación TLS
# (degradación de seguridad fuera de alcance de esta auditoría).
def fetch_foodfiles_nz_urls():
    return _crawl_one_level(
        "https://www.foodcomposition.co.nz/foodfiles", "foodcomposition.co.nz", delay=3.0)

def fetch_cofid_uk_urls():
    return _crawl_one_level(
        "https://www.gov.uk/government/publications/composition-of-foods-integrated-dataset-cofid",
        "gov.uk", delay=3.0)

# AMBIGUO (2026-07-29): dataportal.livsmedelsverket.se da excepción de
# conexión incluso en la raíz del dominio (probado varias rutas), y aparte
# el seed original es una página Swagger UI (JS) que tampoco tendría enlaces
# crawleables aunque cargara. Habría que usar el endpoint REST real de la
# API (no localizado con confianza) en vez de la UI de documentación — se
# deja así en vez de adivinar.
def fetch_livsmedelsverket_sweden_urls():
    return _crawl_one_level(
        "https://dataportal.livsmedelsverket.se/livsmedel/swagger/index.html",
        "livsmedelsverket.se", delay=2.0)

def fetch_foodon_urls():
    return _crawl_one_level("https://foodon.org/", "foodon.org", delay=2.0)

def fetch_journal_eating_disorders_urls():
    return _crawl_one_level(
        "https://jeatdisord.biomedcentral.com/articles", "jeatdisord.biomedcentral.com", delay=2.0)

# C.2 Bases de composición — genuinamente nuevas
def fetch_nevo_netherlands_urls():
    return _crawl_one_level("https://www.rivm.nl/en/dutch-food-composition-database", "rivm.nl", delay=3.0)

def fetch_swiss_food_composition_urls():
    return _crawl_one_level("https://naehrwertdaten.ch/", "naehrwertdaten.ch", delay=3.0)

# AMBIGUO (2026-07-29): este seed específico da excepción de conexión, pese
# a que otras rutas de canada.ca funcionan bien para otros fetchers de este
# archivo (fetch_canada_food_guide_urls, fetch_canada_dri_urls). Podría ser
# una ruta muerta o un fallo intermitente puntual de esta página concreta;
# no se encontró con confianza una URL de reemplazo — se deja así.
def fetch_canadian_nutrient_file_urls():
    return _crawl_one_level(
        "https://www.canada.ca/en/health-canada/services/food-nutrition/healthy-eating/nutrient-data/canadian-nutrient-file-about-us/download-files.html",
        "canada.ca", delay=3.0)

# Confirmado (2026-07-29): foodrepo.org quedó descontinuado — la portada solo
# tiene un <meta http-equiv="refresh"> que redirige a openfoodfacts.org
# ("This site has moved to openfoodfacts.org"). No es un bug ni un bloqueo:
# la fuente se fusionó con Open Food Facts, que este archivo YA cubre por
# separado vía fetch_open_food_facts_urls. No se apunta este fetcher a OFF
# para evitar scraping duplicado del mismo contenido.
def fetch_foodrepo_urls():
    return _crawl_one_level("https://www.foodrepo.org/", "foodrepo.org", delay=3.0)

# Confirmado bloqueado a nivel de dominio (2026-07-29) — globaldietarydatabase.org
# no conecta (connection refused/timeout) ni siquiera en la portada con
# User-Agent de navegador normal; no evadir.
def fetch_global_dietary_database_urls():
    return _crawl_one_level("https://www.globaldietarydatabase.org/", "globaldietarydatabase.org", delay=3.0)

# B. Revistas — genuinamente nuevas
# Confirmado bloqueado por WAF a nivel de dominio (2026-07-29) — 403 incluso
# para la portada de academic.oup.com con User-Agent de navegador normal;
# no evadir.
def fetch_global_perspectives_nutrition_urls():
    return _crawl_one_level("https://academic.oup.com/gpn", "academic.oup.com/gpn", delay=5.0)

def fetch_maternal_health_neonatology_nutr_urls():
    return _crawl_one_level(
        "https://mhnpjournal.biomedcentral.com/articles", "mhnpjournal.biomedcentral.com", delay=2.0)

# F. Nutrición clínica — genuinamente nuevas
def fetch_kdoqi_kidney_nutrition_urls():
    return _crawl_one_level("https://www.kidney.org/professionals/guidelines", "kidney.org", delay=3.0)

def fetch_easl_liver_nutrition_urls():
    # BUGFIX 2026-07-29: /publication/ devuelve 404; la sección correcta es
    # /publications/clinical-practice-guidelines/ (plural + sub-sección).
    return _crawl_one_level("https://easl.eu/publications/clinical-practice-guidelines/", "easl.eu", delay=3.0)

# Confirmado bloqueado por WAF a nivel de dominio (2026-07-29) — 403 incluso
# para la portada de cff.org con User-Agent de navegador normal; no evadir.
def fetch_cystic_fibrosis_nutrition_urls():
    return _crawl_one_level(
        "https://www.cff.org/medical-professionals/clinical-care-guidelines", "cff.org", delay=3.0)

def fetch_crohns_colitis_nutrition_urls():
    return _crawl_one_level(
        "https://www.crohnscolitisfoundation.org/patientsandcaregivers/diet-and-nutrition",
        "crohnscolitisfoundation.org", delay=3.0)

def fetch_national_lipid_assoc_urls():
    return _crawl_one_level("https://www.lipid.org/recommendations", "lipid.org", delay=3.0)

# I. Microbioma — genuinamente nuevas
def fetch_curated_metagenomic_data_urls():
    return _crawl_one_level("https://waldronlab.io/curatedMetagenomicData/", "waldronlab.io", delay=2.0)

# Confirmado (2026-07-29): la portada responde 200 pero el <body> es solo un
# <meta http-equiv="refresh" content="0; ./app"> hacia una SPA (React/Ember,
# familia EuPathDB) — no crawleable con requests+BeautifulSoup. No es un bug
# de URL ni WAF.
def fetch_microbiomedb_urls():
    return _crawl_one_level("https://microbiomedb.org/", "microbiomedb.org", delay=2.0)

# J. Suplementos — genuinamente nuevas
def fetch_cam_cancer_summaries_urls():
    # BUGFIX 2026-07-29: /en/summaries devuelve 404; el sitio se reorganizó,
    # los resúmenes ahora viven en /methodology/evidence-based-summaries.
    return _crawl_one_level("https://cam-cancer.org/methodology/evidence-based-summaries", "cam-cancer.org", delay=5.0)

# Fuentes con licencia/uso restringido — solo metadata, sin crawl masivo
def fetch_langual_metadata_urls():
    return [_make_nutr_metadata_record(
        "https://www.langual.org/", "LanguaL Thesaurus",
        "Descargas gratuitas pero material protegido por copyright; solo referencia, no bulk download.")]

def fetch_foodb_metadata_urls():
    return [_make_nutr_metadata_record(
        "https://foodb.ca/", "FooDB Compounds Database",
        "Consulta pública permitida; explotación comercial requiere licencia separada. No scraping masivo.")]

def fetch_disbiome_metadata_urls():
    return [_make_nutr_metadata_record(
        "https://disbiome.ugent.be/", "Disbiome Microbiome-Disease Database",
        "Uso personal/no comercial; uso comercial de este corpus requiere aprobación expresa de Disbiome/UGent.")]


# ── Delay por fuente ──────────────────────────────────────────────────────────

def delay_for_url(url):
    if "clevelandclinic.org" in url:                 return 10.0
    if any(d in url for d in ["mayoclinic.org", "hopkinsmedicine.org", "tufts.edu",
                               "harvard.edu", "mskcc.org", "mdpi.com"]):  return 5.0
    if any(d in url for d in ["fao.org", "wfp.org", "unicef.org", "paho.org",
                               "espen.org", "nutritioncare.org", "bda.uk.com",
                               "kidney.org", "easl.eu", "cff.org",
                               "crohnscolitisfoundation.org", "lipid.org",
                               "cam-cancer.org", "academic.oup.com"]): return 4.0
    if any(d in url for d in ["efsa.europa.eu", "nutrition.gov", "gov.uk",
                               "bapen.org.uk", "canada.ca", "eatforhealth.gov.au"]): return 3.0
    if "biomedcentral.com" in url or "springeropen.com" in url:           return 2.0
    return 1.5


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
                print(f"  ERROR {sm.split('/')[-1]}: {e}", flush=True)
    if fn:
        try:
            found = fn()
            print(f"  → {len(found)} URLs/registros", flush=True)
            urls.extend(found)
        except Exception as e:
            print(f"  ERROR: {e}", flush=True)
    return urls


def get_all_urls():
    all_urls = []

    # A. Organizaciones oficiales
    all_urls += _load_source("FAO Nutrition",               fn=fetch_fao_nutrition_urls)
    all_urls += _load_source("FAO INFOODS",                 fn=fetch_fao_infoods_urls)
    all_urls += _load_source("Codex Alimentarius",          fn=fetch_codex_urls)
    all_urls += _load_source("EFSA Nutrition/DRV",          fn=fetch_efsa_nutrition_urls)
    all_urls += _load_source("EFSA Guidance Catalogue",     fn=fetch_efsa_guidance_urls)
    all_urls += _load_source("USDA Nutrition.gov",          fn=fetch_usda_nutritiongov_urls)
    all_urls += _load_source("DGA USA 2025-2030",           fn=fetch_dga_usa_urls)
    all_urls += _load_source("PAHO Nutrition",              fn=fetch_paho_nutrition_urls)
    all_urls += _load_source("UNICEF Nutrition",            fn=fetch_unicef_nutrition_urls)
    all_urls += _load_source("WFP Nutrition",               fn=fetch_wfp_nutrition_urls)
    all_urls += _load_source("Global Nutrition Report",     fn=fetch_global_nutrition_report_urls)
    all_urls += _load_source("EC Knowledge4Policy",         fn=fetch_ec_knowledge4policy_urls)

    # B. Revistas OA
    all_urls += _load_source("Nutrients (MDPI)",            fn=fetch_nutrients_mdpi_urls)
    all_urls += _load_source("Nutrition Journal (BMC)",     fn=fetch_nutrition_journal_bmc_urls)
    all_urls += _load_source("BMC Nutrition",               fn=fetch_bmc_nutrition_urls)
    all_urls += _load_source("Nutrition & Metabolism",      fn=fetch_nutrition_metabolism_urls)
    all_urls += _load_source("IJBNPA",                      fn=fetch_ijbnpa_urls)
    all_urls += _load_source("Food & Nutrition Research",   fn=fetch_food_nutrition_research_urls)
    all_urls += _load_source("JHPN",                        fn=fetch_jhpn_urls)
    all_urls += _load_source("JISSN Sports Nutrition",      fn=fetch_jissn_urls)
    all_urls += _load_source("Sports Medicine Open",        fn=fetch_sports_medicine_open_urls)
    all_urls += _load_source("Nutrire Journal",             fn=fetch_nutrire_urls)
    all_urls += _load_source("Genes & Nutrition",           fn=fetch_genes_nutrition_urls)
    all_urls += _load_source("J Nutritional Science",       fn=fetch_journal_nutritional_science_urls)

    # C. Bases de composición
    all_urls += _load_source("USDA FoodData Central API",   fn=fetch_fdc_urls)
    all_urls += _load_source("Open Food Facts API",         fn=fetch_open_food_facts_urls)
    all_urls += _load_source("Matvaretabellen Norway API",  fn=fetch_norway_food_urls)
    all_urls += _load_source("Ciqual France",               fn=fetch_ciqual_urls)
    all_urls += _load_source("Fineli Finland",              fn=fetch_fineli_urls)
    all_urls += _load_source("Phenol-Explorer",             fn=fetch_phenol_explorer_urls)
    all_urls += _load_source("BEDCA Spain",                 fn=fetch_bedca_urls)
    all_urls += _load_source("TBCA Brazil",                 fn=fetch_tbca_urls)

    # D. Guías dietéticas
    all_urls += _load_source("DGA 2025-2030 realfood.gov",  fn=fetch_dga_2025_urls)
    all_urls += _load_source("SACN UK",                     fn=fetch_sacn_uk_urls)
    all_urls += _load_source("Canada Food Guide + DRI",     fn=fetch_canada_food_guide_urls)
    all_urls += _load_source("Canada DRI Tables",           fn=fetch_canada_dri_urls)
    all_urls += _load_source("Australia Dietary Guidelines",fn=fetch_australia_guidelines_urls)
    all_urls += _load_source("Australia NRV",               fn=fetch_australia_nrv_urls)
    all_urls += _load_source("Nordic Nutrition Rec 2023",   fn=fetch_nordic_nutrition_urls)
    all_urls += _load_source("EFSA DRV Portal",             fn=fetch_efsa_drv_urls)
    all_urls += _load_source("AESAN Spain",                 fn=fetch_aesan_spain_urls)
    all_urls += _load_source("México Guías 2023",           fn=fetch_mexico_guias_urls)

    # E. Sociedades profesionales
    all_urls += _load_source("AND/EatRight",                fn=fetch_and_eatright_urls)
    all_urls += _load_source("ASN Nutrition",               fn=fetch_asn_nutrition_urls)
    all_urls += _load_source("SENC Spain",                  fn=fetch_senc_spain_urls)
    all_urls += _load_source("FESNAD Spain",                fn=fetch_fesnad_urls)
    all_urls += _load_source("SENPE Spain",                 fn=fetch_senpe_urls)
    all_urls += _load_source("ESPEN",                       fn=fetch_espen_urls)
    all_urls += _load_source("ASPEN Clinical",              fn=fetch_aspen_urls)
    all_urls += _load_source("BAPEN",                       fn=fetch_bapen_urls)
    all_urls += _load_source("BDA UK",                      fn=fetch_bda_uk_urls)
    all_urls += _load_source("Nutrition Society UK",        fn=fetch_nutrition_society_uk_urls)
    all_urls += _load_source("FELANPE",                     fn=fetch_felanpe_urls)
    all_urls += _load_source("IUNS",                        fn=fetch_iuns_urls)
    all_urls += _load_source("FENS Europe",                 fn=fetch_fens_urls)
    all_urls += _load_source("Obesity Canada",              fn=fetch_obesity_canada_urls)

    # F. Nutrición clínica
    all_urls += _load_source("ESPEN Guidelines",            fn=fetch_espen_guidelines_urls)
    all_urls += _load_source("ASPEN Guidelines",            fn=fetch_aspen_guidelines_urls)
    all_urls += _load_source("BAPEN/MUST",                  fn=fetch_bapen_must_urls)
    all_urls += _load_source("Critical Care Nutrition",     fn=fetch_critical_care_nutrition_urls)
    all_urls += _load_source("Obesity Canada CPG",          fn=fetch_obesity_canada_cpg_urls)
    all_urls += _load_source("Diabetes Canada Nutrition",   fn=fetch_diabetes_canada_urls)
    all_urls += _load_source("Diabetes UK Nutrition",       fn=fetch_diabetes_uk_urls)
    all_urls += _load_source("IDDSI Dysphagia",             fn=fetch_iddsi_urls)
    all_urls += _load_source("ESPGHAN Nutrition",           fn=fetch_espghan_urls)
    all_urls += _load_source("Oncología Nutrición",         fn=fetch_cancer_nutrition_urls)

    # G. Nutrición deportiva
    all_urls += _load_source("ISSN Position Stands",        fn=fetch_issn_position_stands_urls)
    all_urls += _load_source("AIS Supplement Framework",    fn=fetch_ais_supplement_urls)
    all_urls += _load_source("OPSS/DoD",                    fn=fetch_opss_dod_urls)
    all_urls += _load_source("USADA Supplements",           fn=fetch_usada_supplements_urls)
    all_urls += _load_source("NCAA Nutrition",              fn=fetch_ncaa_nutrition_urls)
    all_urls += _load_source("Sport Integrity Australia",   fn=fetch_sport_integrity_au_urls)

    # H. Universidades y hospitales
    all_urls += _load_source("Harvard Nutrition Source",    fn=fetch_harvard_nutrition_source_urls)
    all_urls += _load_source("Tufts Friedman",              fn=fetch_tufts_friedman_urls)
    all_urls += _load_source("Tufts HNRCA",                 fn=fetch_tufts_hnrca_urls)
    all_urls += _load_source("Mayo Clinic Nutrition",       fn=fetch_mayo_clinic_nutrition_urls)
    all_urls += _load_source("Cleveland Clinic Nutrition",  fn=fetch_cleveland_clinic_nutrition_urls)
    all_urls += _load_source("Johns Hopkins Nutrition",     fn=fetch_johns_hopkins_nutrition_urls)

    # I. Microbioma
    all_urls += _load_source("GMrepo Microbiome",           fn=fetch_gmrepo_urls)
    all_urls += _load_source("gutMDisorder",                fn=fetch_gutmdisorder_urls)
    all_urls += _load_source("MGnify Gut/Nutrition",        fn=fetch_mgnify_nutrition_urls)
    all_urls += _load_source("Gut Microbiota for Health",   fn=fetch_gut_microbiota_health_urls)

    # J. Suplementos y micronutrientes
    all_urls += _load_source("Linus Pauling MIC",           fn=fetch_linus_pauling_mic_urls)
    all_urls += _load_source("Health Canada LNHPD API",     fn=fetch_health_canada_lnhpd_urls)
    all_urls += _load_source("OPSS Ingredient Index",       fn=fetch_opss_ingredients_urls)
    all_urls += _load_source("EU Health Claims Register",   fn=fetch_eu_health_claims_urls)
    all_urls += _load_source("EFSA Health Claims",          fn=fetch_efsa_health_claims_urls)
    all_urls += _load_source("EFSA Compendium Botanicals",  fn=fetch_efsa_botanicals_urls)
    all_urls += _load_source("ARTG Australia",              fn=fetch_artg_australia_urls)
    all_urls += _load_source("MSK About Herbs",             fn=fetch_msk_herbs_urls)

    # ── Nuevas (Inventario Complementario 2026-07-26) ───────────────────────────
    # C. Bases de composición — folders ya reservados, activando fetcher
    all_urls += _load_source("AFCD Australia",              fn=fetch_afcd_australia_urls)
    all_urls += _load_source("FOODfiles Nueva Zelanda",     fn=fetch_foodfiles_nz_urls)
    all_urls += _load_source("CoFID UK",                    fn=fetch_cofid_uk_urls)
    all_urls += _load_source("Livsmedelsverket Suecia",     fn=fetch_livsmedelsverket_sweden_urls)
    all_urls += _load_source("FoodOn Ontología",            fn=fetch_foodon_urls)
    all_urls += _load_source("Journal of Eating Disorders", fn=fetch_journal_eating_disorders_urls)
    # C.2 — genuinamente nuevas
    all_urls += _load_source("NEVO Países Bajos",           fn=fetch_nevo_netherlands_urls)
    all_urls += _load_source("Base Suiza de Composición",   fn=fetch_swiss_food_composition_urls)
    all_urls += _load_source("Canadian Nutrient File",      fn=fetch_canadian_nutrient_file_urls)
    all_urls += _load_source("FoodRepo",                    fn=fetch_foodrepo_urls)
    all_urls += _load_source("Global Dietary Database",     fn=fetch_global_dietary_database_urls)
    # B. Revistas — genuinamente nuevas + híbridas vía Crossref/Unpaywall
    all_urls += _load_source("Global Perspectives on Nutrition", fn=fetch_global_perspectives_nutrition_urls)
    all_urls += _load_source("Maternal Health Neonatology Perinatology", fn=fetch_maternal_health_neonatology_nutr_urls)
    all_urls += _load_source("Current Developments in Nutrition (OA)", fn=fetch_current_dev_nutrition_oa_urls)
    all_urls += _load_source("Clinical Nutrition Open Science (OA)", fn=fetch_clinical_nutrition_open_oa_urls)
    all_urls += _load_source("Revistas híbridas nutrición (Crossref/Unpaywall)", fn=fetch_hybrid_nutrition_journals_urls)
    # F. Nutrición clínica — genuinamente nuevas
    all_urls += _load_source("KDOQI Kidney Nutrition",      fn=fetch_kdoqi_kidney_nutrition_urls)
    all_urls += _load_source("EASL Liver Nutrition",        fn=fetch_easl_liver_nutrition_urls)
    all_urls += _load_source("Cystic Fibrosis Foundation Nutrition", fn=fetch_cystic_fibrosis_nutrition_urls)
    all_urls += _load_source("Crohn's & Colitis Foundation Nutrition", fn=fetch_crohns_colitis_nutrition_urls)
    all_urls += _load_source("National Lipid Association",  fn=fetch_national_lipid_assoc_urls)
    # I. Microbioma — genuinamente nuevas
    all_urls += _load_source("curatedMetagenomicData",      fn=fetch_curated_metagenomic_data_urls)
    all_urls += _load_source("MicrobiomeDB",                fn=fetch_microbiomedb_urls)
    all_urls += _load_source("Disbiome (metadata, no comercial)", fn=fetch_disbiome_metadata_urls)
    # J. Suplementos — genuinamente nuevas
    all_urls += _load_source("CAM-Cancer Summaries",        fn=fetch_cam_cancer_summaries_urls)
    all_urls += _load_source("LanguaL (metadata)",          fn=fetch_langual_metadata_urls)
    all_urls += _load_source("FooDB (metadata)",            fn=fetch_foodb_metadata_urls)

    print(f"\nTotal URLs/registros objetivo: {len(all_urls)}", flush=True)
    return all_urls


# ── Scraping de páginas HTML ───────────────────────────────────────────────────

def scrape_page(url):
    # Registros inline de APIs (contienen "|TYPE|")
    if "|FDC_FOOD|" in url or "|OFF_PRODUCT|" in url or "|NORWAY_FOOD|" in url \
            or "|LNHPD_PRODUCT|" in url or "|MGNIFY_STUDY|" in url \
            or "|CDN_OA|" in url or "|CNOS_OA|" in url or "|HYBRID_NUTR_OA|" in url \
            or "|NUTR_METADATA|" in url:
        text = extract_inline_content(url)
        real_url = url.split("|")[0]
        return {"title": real_url.split("/")[-1][:80], "full_text": text}

    # Registros de Norway API que sí tienen ID real — fetchear detalles
    if "matvaretabellen.no/api/food/" in url:
        try:
            r = requests.get(url.replace("|NORWAY_FOOD|", "").split("|")[0],
                             headers=HEADERS, timeout=20)
            data = r.json()
            return {"title": data.get("foodName", url), "full_text": extract_inline_content(url)}
        except Exception:
            return {"title": url, "full_text": extract_inline_content(url)}

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
    base_url = url.split("|")[0]
    if "fao.org/infoods"          in base_url:  prefix = "fao_infoods"
    elif "fao.org"                in base_url:  prefix = "fao"
    elif "codexalimentarius"      in base_url:  prefix = "codex"
    elif "efsa.europa.eu"         in base_url:  prefix = "efsa"
    elif "nutrition.gov"          in base_url:  prefix = "nutritiongov"
    elif "dietaryguidelines.gov"  in base_url or "realfood.gov" in base_url: prefix = "dga_usa"
    elif "paho.org"               in base_url:  prefix = "paho"
    elif "unicef.org"             in base_url:  prefix = "unicef"
    elif "wfp.org"                in base_url:  prefix = "wfp"
    elif "globalnutritionreport"  in base_url:  prefix = "gnr"
    elif "knowledge4policy"       in base_url:  prefix = "ec_k4p"
    elif "mdpi.com"               in base_url:  prefix = "nutrients"
    elif "nutritionj.biomedcentral" in base_url: prefix = "nutritionj"
    elif "bmcnutr.biomedcentral"  in base_url:  prefix = "bmc_nutr"
    elif "nutritionandmetabolism" in base_url:  prefix = "nutr_metab"
    elif "ijbnpa.biomedcentral"   in base_url:  prefix = "ijbnpa"
    elif "foodandnutritionresearch" in base_url: prefix = "fnr"
    elif "jhpn.biomedcentral"     in base_url:  prefix = "jhpn"
    elif "jissn.biomedcentral"    in base_url or "rssn20" in base_url: prefix = "jissn"
    elif "sportsmedicine-open" in base_url or "link.springer.com/article/10.1186/s40798" in base_url: prefix = "sportsmed_open"
    elif "nutrirejournal"         in base_url:  prefix = "nutrire"
    elif "genesandnutrition"      in base_url:  prefix = "genes_nutr"
    elif "cambridge.org/core/journals/journal-of-nutritional" in base_url: prefix = "jns"
    elif "api.nal.usda.gov/fdc"   in base_url or "|FDC_FOOD|" in url: prefix = "fdc"
    elif "openfoodfacts.org"      in base_url or "|OFF_PRODUCT|" in url: prefix = "off"
    elif "matvaretabellen.no"     in base_url or "|NORWAY_FOOD|" in url: prefix = "norway_food"
    elif "ciqual.anses.fr"        in base_url:  prefix = "ciqual"
    elif "fineli.fi"              in base_url:  prefix = "fineli"
    elif "phenol-explorer.eu"     in base_url:  prefix = "phenol"
    elif "bedca.net"              in base_url:  prefix = "bedca"
    elif "tbca.net.br"            in base_url:  prefix = "tbca"
    elif "gov.uk" in base_url and "sacn" in base_url.lower(): prefix = "sacn"
    elif "canada.ca/en/health-canada/services/food-guide" in base_url: prefix = "canada_food_guide"
    elif "canada.ca" in base_url and "dri" in base_url.lower(): prefix = "canada_dri"
    elif "eatforhealth.gov.au"    in base_url:  prefix = "australia_nutr"
    elif "pub.norden.org"         in base_url:  prefix = "nordic_nnr"
    elif "aesan.gob.es"           in base_url:  prefix = "aesan"
    elif "gob.mx/salud"           in base_url:  prefix = "mexico_guias"
    elif "eatrightpro.org"        in base_url:  prefix = "and"
    elif "nutrition.org"          in base_url:  prefix = "asn"
    elif "nutricioncomunitaria.org" in base_url: prefix = "senc"
    elif "fesnad.org"             in base_url:  prefix = "fesnad"
    elif "senpe.com"              in base_url:  prefix = "senpe"
    elif "espen.org"              in base_url:  prefix = "espen"
    elif "nutritioncare.org"      in base_url:  prefix = "aspen"
    elif "bapen.org.uk"           in base_url:  prefix = "bapen"
    elif "bda.uk.com"             in base_url:  prefix = "bda"
    elif "nutritionsociety.org"   in base_url:  prefix = "nutr_soc"
    elif "felanpeweb.org" in base_url or "felanpe.org" in base_url: prefix = "felanpe"
    elif "iuns.org"               in base_url:  prefix = "iuns"
    elif "fensnutrition.org"      in base_url:  prefix = "fens"
    elif "obesitycanada.ca"       in base_url:  prefix = "obesity_ca"
    elif "criticalcarenutrition"  in base_url:  prefix = "ccn"
    elif "guidelines.diabetes.ca" in base_url:  prefix = "diabetes_ca"
    elif "diabetes.org.uk"        in base_url:  prefix = "diabetes_uk"
    elif "iddsi.org"              in base_url:  prefix = "iddsi"
    elif "espghan.org"            in base_url:  prefix = "espghan"
    elif "cancer.org.au"          in base_url or "macmillan.org.uk" in base_url: prefix = "cancer_nutr"
    elif "opss.org"               in base_url:  prefix = "opss"
    elif "ais.gov.au/nutrition/supplements" in base_url: prefix = "ais_supp"
    elif "usada.org"              in base_url:  prefix = "usada"
    elif "ncaa.org"               in base_url:  prefix = "ncaa"
    elif "sportintegrity.gov.au"  in base_url:  prefix = "sia_au"
    elif "nutritionsource.hsph.harvard.edu" in base_url: prefix = "harvard_nutr"
    elif "nutrition.tufts.edu"    in base_url:  prefix = "tufts_nutr"
    elif "hnrca.tufts.edu"        in base_url:  prefix = "hnrca"
    elif "mayoclinic.org"         in base_url:  prefix = "mayo_nutr"
    elif "clevelandclinic.org"    in base_url:  prefix = "cleveland_nutr"
    elif "hopkinsmedicine.org"    in base_url:  prefix = "hopkins_nutr"
    elif "gmrepo.humangut.info"   in base_url:  prefix = "gmrepo"
    elif "gutmdisorder"           in base_url:  prefix = "gutmdisorder"
    elif "ebi.ac.uk/metagenomics" in base_url or "|MGNIFY_STUDY|" in url: prefix = "mgnify"
    elif "gutmicrobiotaforhealth" in base_url:  prefix = "gut_micro_health"
    elif "lpi.oregonstate.edu"    in base_url:  prefix = "lpi_mic"
    elif "health-products.canada.ca" in base_url or "|LNHPD_PRODUCT|" in url: prefix = "lnhpd"
    elif "ec.europa.eu/food/food-feed-portal" in base_url: prefix = "eu_claims"
    elif "efsa.europa.eu" in base_url and "botanical" in base_url: prefix = "efsa_botanicals"
    elif "tga.gov.au"             in base_url:  prefix = "artg_au"
    elif "mskcc.org"              in base_url:  prefix = "msk_herbs"
    elif "|CDN_OA|"                in url:      prefix = "current_dev_nutr_oa"
    elif "|CNOS_OA|"               in url:      prefix = "clin_nutr_open_oa"
    elif "|HYBRID_NUTR_OA|"        in url:      prefix = "hybrid_nutr_oa"
    elif "|NUTR_METADATA|"         in url:      prefix = "nutr_metadata"
    elif "rivm.nl"                 in base_url: prefix = "nevo_nl"
    elif "naehrwertdaten.ch"       in base_url: prefix = "swiss_food_comp"
    elif "foodb.ca"                in base_url: prefix = "foodb"
    elif "foodrepo.org"            in base_url: prefix = "foodrepo"
    elif "globaldietarydatabase.org" in base_url: prefix = "global_dietary_db"
    elif "academic.oup.com/gpn"    in base_url: prefix = "gpn_journal"
    elif "mhnpjournal.biomedcentral.com" in base_url: prefix = "mhnp_journal"
    elif "kidney.org"              in base_url: prefix = "kdoqi"
    elif "easl.eu"                 in base_url: prefix = "easl"
    elif "cff.org"                 in base_url: prefix = "cff_nutr"
    elif "crohnscolitisfoundation.org" in base_url: prefix = "crohns_colitis"
    elif "lipid.org"               in base_url: prefix = "lipid_assoc"
    elif "waldronlab.io"           in base_url: prefix = "curated_metagenomic"
    elif "microbiomedb.org"        in base_url: prefix = "microbiomedb"
    elif "cam-cancer.org"          in base_url: prefix = "cam_cancer"
    elif "foodstandards.gov.au"    in base_url: prefix = "afcd_au"
    elif "foodcomposition.co.nz"   in base_url: prefix = "foodfiles_nz"
    elif "gov.uk" in base_url and "composition-of-foods" in base_url: prefix = "cofid_uk"
    elif "livsmedelsverket.se"     in base_url: prefix = "sweden_food"
    elif "foodon.org"              in base_url: prefix = "foodon"
    elif "jeatdisord.biomedcentral.com" in base_url: prefix = "eating_disorders"
    elif "canada.ca" in base_url and "nutrient" in base_url: prefix = "canadian_nutrient_file"
    else:                                        prefix = "nutricion"
    path = re.sub(r"[?=&]", "_", base_url.split("//", 1)[-1]).replace("/", "__").strip("__")
    return f"{prefix}__{path[:160]}.txt"


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
            print(f"[{i}/{len(remaining)}] {rate:.1f}/s — ETA {eta:.0f} min", flush=True)

        time.sleep(delay_for_url(url))

    save_progress(progress)
    print(f"\nFinalizado. {len(progress['done'])} registros subidos.", flush=True)
