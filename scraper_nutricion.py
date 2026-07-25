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
    if "tandfonline.com/journals/rssn" in url or "jissn.biomedcentral.com" in url: return DRIVE_JISSN_SPORTS_NUTR_ID
    if "sportsmedicine-open.springeropen.com" in url: return DRIVE_SPORTS_MEDICINE_OPEN_ID
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
    if "fao.org/nutrition/education" in url: return DRIVE_FAO_COUNTRY_GUIDELINES_ID
    if "realfood.gov"              in url:  return DRIVE_DGA_2025_REALFOOD_ID
    if "gob.mx/salud" in url and "guia" in url: return DRIVE_GUIAS_MEXICO_2023_ID
    if "aesan.gob.es"              in url:  return DRIVE_AESAN_SPAIN_ID
    if "sacn" in url or ("gov.uk" in url and "sacn" in url): return DRIVE_SACN_UK_ID
    if "canada.ca/en/health-canada/services/food-guide" in url: return DRIVE_CANADA_FOOD_GUIDE_ID
    if "eatforhealth.gov.au"       in url:  return DRIVE_AUSTRALIA_DIETARY_GUIDELINES_ID
    if "pub.norden.org"            in url or "nordic" in url and "nutrition" in url: return DRIVE_NORDIC_NUTRITION_REC_2023_ID
    if "saude.gov.br"              in url and "nutricao" in url: return DRIVE_BRAZIL_DIETARY_GUIDELINES_ID
    if "health.govt.nz"            in url and ("eat" in url or "nutrition" in url): return DRIVE_NZ_EATING_GUIDELINES_ID
    if "efsa.europa.eu/en/topics/topic/dietary-reference" in url: return DRIVE_EFSA_DRV_ID
    if "mhlw.go.jp"                in url:  return DRIVE_JAPAN_DRI_ID
    if "icmr.gov.in"               in url or "nin.res.in" in url: return DRIVE_INDIA_DIETARY_GUIDELINES_ID
    # E. Sociedades
    if "eatrightpro.org"           in url:  return DRIVE_AND_EATRIGHT_ID
    if "nutrition.org"             in url:  return DRIVE_ASN_NUTRITION_ID
    if "nutricioncomunitaria.org"  in url:  return DRIVE_SENC_SPAIN_ID
    if "fesnad.org"                in url:  return DRIVE_FESNAD_SPAIN_ID
    if "senpe.com"                 in url:  return DRIVE_SENPE_SPAIN_ID
    if "espen.org"                 in url:  return DRIVE_ESPEN_ID
    if "nutritioncare.org"         in url:  return DRIVE_ASPEN_CLINICAL_ID
    if "bapen.org.uk"              in url:  return DRIVE_BAPEN_ID
    if "bda.uk.com"                in url:  return DRIVE_BDA_UK_ID
    if "nutritionsociety.org"      in url:  return DRIVE_NUTRITION_SOCIETY_UK_ID
    if "felanpeweb.org"            in url:  return DRIVE_FELANPE_ID
    if "iuns.org"                  in url:  return DRIVE_IUNS_ID
    if "fensnutrition.org"         in url:  return DRIVE_FENS_EUROPE_ID
    if "obesitycanada.ca"          in url:  return DRIVE_OBESITY_CANADA_ID
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
    if "opss.org"                  in url:  return DRIVE_OPSS_DOD_ID
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
    urls = _crawl_one_level("https://www.fao.org/nutrition/publications/en/", "fao.org", delay=4.0)
    urls += _crawl_one_level("https://www.fao.org/nutrition/education/food-based-dietary-guidelines/en/", "fao.org", delay=4.0)
    return urls

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
    return _crawl_one_level("https://www.efsa.europa.eu/en/applications/guidance", "efsa.europa.eu", delay=2.0)

def fetch_usda_nutritiongov_urls():
    return _fetch_sitemap_index_urls("https://www.nutrition.gov/sitemap.xml", delay=2.0)

def fetch_dga_usa_urls():
    urls = _crawl_one_level("https://www.dietaryguidelines.gov/resources/", "dietaryguidelines.gov", delay=2.0)
    urls += _crawl_one_level("https://www.realfood.gov/", "realfood.gov", delay=2.0)
    return urls

def fetch_paho_nutrition_urls():
    return _crawl_one_level("https://www.paho.org/en/topics/healthy-diet", "paho.org", delay=3.0)

def fetch_unicef_nutrition_urls():
    return _crawl_one_level("https://www.unicef.org/nutrition", "unicef.org", delay=4.0)

def fetch_wfp_nutrition_urls():
    return _crawl_one_level("https://www.wfp.org/nutrition", "wfp.org", delay=4.0)

def fetch_global_nutrition_report_urls():
    return _crawl_one_level("https://globalnutritionreport.org/", "globalnutritionreport.org", delay=3.0)

def fetch_ec_knowledge4policy_urls():
    return _crawl_one_level(
        "https://knowledge4policy.ec.europa.eu/health-promotion-knowledge-gateway/nutrition_en",
        "knowledge4policy.ec.europa.eu", delay=3.0,
    )


# ── FASE B: Revistas OA ───────────────────────────────────────────────────────

def fetch_nutrients_mdpi_urls():
    return _fetch_sitemap_index_urls(
        "https://www.mdpi.com/sitemap/sitemap-nutrients.xml",
        url_filter=lambda u: "/nutrients/" in u and "/article" in u,
        delay=8.0,
    )

def fetch_nutrition_journal_bmc_urls():
    return _fetch_sitemap_index_urls(
        "https://nutritionj.biomedcentral.com/sitemap.xml",
        url_filter=lambda u: "article" in u, delay=2.0,
    )

def fetch_bmc_nutrition_urls():
    return _fetch_sitemap_index_urls(
        "https://bmcnutr.biomedcentral.com/sitemap.xml",
        url_filter=lambda u: "article" in u, delay=2.0,
    )

def fetch_nutrition_metabolism_urls():
    return _fetch_sitemap_index_urls(
        "https://nutritionandmetabolism.biomedcentral.com/sitemap.xml",
        url_filter=lambda u: "article" in u, delay=2.0,
    )

def fetch_ijbnpa_urls():
    return _fetch_sitemap_index_urls(
        "https://ijbnpa.biomedcentral.com/sitemap.xml",
        url_filter=lambda u: "article" in u, delay=2.0,
    )

def fetch_food_nutrition_research_urls():
    return _crawl_one_level(
        "https://foodandnutritionresearch.net/index.php/fnr/issue/archive",
        "foodandnutritionresearch.net", delay=2.0,
    )

def fetch_jhpn_urls():
    return _fetch_sitemap_index_urls(
        "https://jhpn.biomedcentral.com/sitemap.xml",
        url_filter=lambda u: "article" in u, delay=2.0,
    )

def fetch_jissn_urls():
    return _fetch_sitemap_index_urls(
        "https://jissn.biomedcentral.com/sitemap.xml",
        url_filter=lambda u: "article" in u, delay=2.0,
    )

def fetch_sports_medicine_open_urls():
    return _fetch_sitemap_index_urls(
        "https://sportsmedicine-open.springeropen.com/sitemap.xml",
        url_filter=lambda u: "article" in u, delay=2.0,
    )

def fetch_nutrire_urls():
    return _fetch_sitemap_index_urls(
        "https://nutrirejournal.biomedcentral.com/sitemap.xml",
        url_filter=lambda u: "article" in u, delay=2.0,
    )

def fetch_genes_nutrition_urls():
    return _fetch_sitemap_index_urls(
        "https://genesandnutrition.biomedcentral.com/sitemap.xml",
        url_filter=lambda u: "article" in u, delay=2.0,
    )

def fetch_journal_nutritional_science_urls():
    return _crawl_one_level(
        "https://www.cambridge.org/core/journals/journal-of-nutritional-science/listing?",
        "cambridge.org/core/journals/journal-of-nutritional-science", delay=5.0,
    )


# ── FASE C: Bases de composición de alimentos (API inline) ───────────────────

FDC_API_KEY = "DEMO_KEY"  # reemplazar con tu API key propia para producción

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
    """Matvaretabellen Norway REST API — todos los alimentos."""
    base = "https://www.matvaretabellen.no/api/foods"
    try:
        r = requests.get(f"{base}?language=en", headers=HEADERS, timeout=30)
        foods = r.json()
        urls = []
        for food in foods[:2000]:
            fid = food.get("foodId")
            fname = food.get("foodName", "")
            if fid:
                urls.append(f"https://www.matvaretabellen.no/api/food/{fid}/en|NORWAY_FOOD|{json.dumps({'foodId':fid,'foodName':fname})}")
        return urls
    except Exception:
        return []

def fetch_ciqual_urls():
    return _crawl_one_level("https://ciqual.anses.fr/", "ciqual.anses.fr", delay=2.0)

def fetch_fineli_urls():
    return _crawl_one_level("https://fineli.fi/fineli/en/foods?", "fineli.fi", delay=2.0)

def fetch_phenol_explorer_urls():
    return _crawl_one_level("https://phenol-explorer.eu/compounds", "phenol-explorer.eu", delay=2.0)

def fetch_bedca_urls():
    return _crawl_one_level("https://www.bedca.net/bdpub/index_en.php", "bedca.net", delay=4.0)

def fetch_tbca_urls():
    return _crawl_one_level("https://www.tbca.net.br/base-dados/int_composicao_alimentos.php", "tbca.net.br", delay=4.0)


# ── FASE D: Guías dietéticas ──────────────────────────────────────────────────

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

def fetch_australia_guidelines_urls():
    return _crawl_one_level("https://www.eatforhealth.gov.au/guidelines", "eatforhealth.gov.au", delay=2.0)

def fetch_australia_nrv_urls():
    return _crawl_one_level("https://www.eatforhealth.gov.au/nutrient-reference-values", "eatforhealth.gov.au", delay=2.0)

def fetch_nordic_nutrition_urls():
    return _crawl_one_level("https://pub.norden.org/nord2023-003/", "pub.norden.org", delay=2.0)

def fetch_efsa_drv_urls():
    return _crawl_one_level(
        "https://www.efsa.europa.eu/en/topics/topic/dietary-reference-values",
        "efsa.europa.eu", delay=2.0,
    )

def fetch_aesan_spain_urls():
    return _crawl_one_level("https://www.aesan.gob.es/AECOSAN/web/nutricion/", "aesan.gob.es", delay=3.0)

def fetch_mexico_guias_urls():
    return _crawl_one_level(
        "https://www.gob.mx/salud/documentos/guias-alimentarias-saludables-y-sostenibles-para-la-poblacion-mexicana-2023",
        "gob.mx", delay=3.0,
    )


# ── FASE E: Sociedades profesionales ──────────────────────────────────────────

def fetch_and_eatright_urls():
    return _crawl_one_level("https://www.eatrightpro.org/practice/position-and-practice-papers", "eatrightpro.org", delay=5.0)

def fetch_asn_nutrition_urls():
    return _crawl_one_level("https://nutrition.org/policy-and-advocacy/", "nutrition.org", delay=5.0)

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
    return _crawl_one_level("https://www.bda.uk.com/resource/food-facts.html", "bda.uk.com", delay=5.0)

def fetch_nutrition_society_uk_urls():
    return _crawl_one_level("https://www.nutritionsociety.org/", "nutritionsociety.org", delay=5.0)

def fetch_felanpe_urls():
    return _crawl_one_level("https://felanpeweb.org/", "felanpeweb.org", delay=5.0)

def fetch_iuns_urls():
    urls = fetch_urls_from_sitemap("https://iuns.org/wp-sitemap.xml")
    if not urls:
        urls = _crawl_one_level("https://iuns.org/", "iuns.org", delay=5.0)
    return urls

def fetch_fens_urls():
    return _crawl_one_level("https://fensnutrition.org/", "fensnutrition.org", delay=5.0)

def fetch_obesity_canada_urls():
    return _crawl_one_level("https://obesitycanada.ca/resources/", "obesitycanada.ca", delay=4.0)


# ── FASE F: Nutrición clínica ─────────────────────────────────────────────────

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

def fetch_gmrepo_urls():
    return _crawl_one_level("https://gmrepo.humangut.info/", "gmrepo.humangut.info", delay=3.0)

def fetch_gutmdisorder_urls():
    return _crawl_one_level("http://bio-annotation.cn/gutMDisorder/", "bio-annotation.cn", delay=3.0)

def fetch_mgnify_nutrition_urls():
    """MGnify API — estudios con términos de dieta en biome intestinal."""
    base = "https://www.ebi.ac.uk/metagenomics/api/v1/studies"
    urls = []
    params = {"biome_name": "Human:Gut", "page_size": 50, "page": 1}
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
    return _crawl_one_level(
        "https://www.efsa.europa.eu/en/topics/topic/compendium-botanicals",
        "efsa.europa.eu", delay=2.0,
    )

def fetch_artg_australia_urls():
    return _crawl_one_level("https://www.tga.gov.au/resources/artg", "tga.gov.au", delay=3.0)

def fetch_msk_herbs_urls():
    return _crawl_one_level(
        "https://www.mskcc.org/cancer-care/diagnosis-treatment/symptom-management/integrative-medicine/herbs/search",
        "mskcc.org", delay=5.0,
    )


# ── Delay por fuente ──────────────────────────────────────────────────────────

def delay_for_url(url):
    if "clevelandclinic.org" in url:                 return 10.0
    if any(d in url for d in ["mayoclinic.org", "hopkinsmedicine.org", "tufts.edu",
                               "harvard.edu", "mskcc.org", "mdpi.com"]):  return 5.0
    if any(d in url for d in ["fao.org", "wfp.org", "unicef.org", "paho.org",
                               "espen.org", "nutritioncare.org", "bda.uk.com"]): return 4.0
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

    print(f"\nTotal URLs/registros objetivo: {len(all_urls)}", flush=True)
    return all_urls


# ── Scraping de páginas HTML ───────────────────────────────────────────────────

def scrape_page(url):
    # Registros inline de APIs (contienen "|TYPE|")
    if "|FDC_FOOD|" in url or "|OFF_PRODUCT|" in url or "|NORWAY_FOOD|" in url \
            or "|LNHPD_PRODUCT|" in url or "|MGNIFY_STUDY|" in url:
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
    elif "sportsmedicine-open"    in base_url:  prefix = "sportsmed_open"
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
    elif "felanpeweb.org"         in base_url:  prefix = "felanpe"
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
