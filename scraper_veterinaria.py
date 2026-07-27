"""
Scraper veterinario completo — 90+ fuentes
Incluye: manuales, organizaciones, guías, farmacología, toxicología,
revistas OA, universidades, organizaciones regionales, bases de datos
clínicas/genéticas/epidemiológicas, y nutrición/bienestar animal.
Resumible: guarda progreso en progress_vet.json
"""
import os, json, time, random, re, requests
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from google.oauth2.credentials import Credentials

# ── Drive IDs ──────────────────────────────────────────────────────────────────

DRIVE_VET_ROOT_ID   = "1sypIsu5f1rtKyuLYKgIN9yuSxYIONi7p"   # Proyecto_IA_Veterinaria
DRIVE_MERCK_ID      = "107q-Vp6aWHR7bUYi7FxEedz1ywULSzNV"   # merck_manual
DRIVE_AAHA_ID       = "1N0_pVjDE67q3Gcc743aMb1PBQbrs523f"    # aaha
DRIVE_ACVS_ID       = "1SjE0iSJJBrbFbdmZsFdRMqh27pL7BZO9"   # acvs
DRIVE_MSD_ID        = "1p6840PyVvvuSbz05v5V5ZCNhSHpUUy-E"   # msd_manual
DRIVE_WOAH_ID       = "1lehKe-HXiSTn1SaP1f4Iefs656_y70LW"   # woah
DRIVE_WSAVA_ID      = "12KhYXEdNAbej2bErtVIwFx6b7A9IT2en"   # wsava
DRIVE_ACVIM_ID      = "1GCrjYJFJWoLnA_eM1oDiakJMrONuSO6-"   # acvim
DRIVE_AAVMC_ID      = "1urggNC3UPd5mfK4B8pF3LNZbWEyS9q-i"   # aavmc
DRIVE_NOAH_ID       = "1ayGiovBa8v986wcR_z5z2Za0Vv59Nekc"    # noah_compendium
DRIVE_EMA_ID        = "1QF9-QzuHaRScm_pghdCz5rDchr0ASuhj"   # ema_veterinary
DRIVE_FDA_ID        = "1uliwOpKtvjV44iPHd3dsjOvSPXVW_8ys"    # fda_cvm
DRIVE_ASPCA_ID      = "13QEwv1X496Qp73FT6S7IXCYitfiGZDvs"   # aspca_toxicology
DRIVE_PPH_ID        = "1IWMPqwucjt9TCsMCAVXiD1XPTZZh3Hkm"   # pet_poison_helpline
DRIVE_FRONTIERS_ID  = "1BV1jUxsrwETuMZWj1x-UHc-AEKFBrwCy"   # frontiers_veterinary
DRIVE_PLOS_ID       = "14r1wc4gXMOzo7kbtE5cimjEPVFya3Z_R"    # plos_veterinary
DRIVE_CB_ID         = "1IDQuSWGnG2cX0lMGk7BBwi3WeW-uSH7E"   # clinicians_brief
DRIVE_TVP_ID        = "1fNU5Jjaz4d26dsEdQxjJE-OTrE714eVW"   # todays_vet_practice
DRIVE_EFSA_ID2      = "181t6H-_m4Elj9_boIQYHTOS_Eajur1to"   # efsa
DRIVE_FAO_ID        = "1Ls66EIg1rY-0IkLebsXDrjdZRYo1eBp-"   # fao_animal_health
DRIVE_CORNELL_ID    = "10kssTKPoLHItZfK1YXYWStmqlnHWZaSa"   # cornell_vet
DRIVE_UCDAVIS_ID    = "1cHlmGAVCnVxbn2UWZ4Bu1TvximsaaWmR"   # uc_davis_vet
DRIVE_PURDUE_ID     = "1Qq5br-xoR-VVe8KdfLwK23yS8tCyYZQK"   # purdue_vet
DRIVE_TAMU_ID       = "1PZHrQcf8DQGg59pUPWqYJ1bVndg-wgO5"   # texas_am_vet
DRIVE_OSU_ID        = "17T52a-QfK8P-So9UKppeF78hmre6Bc6q"   # ohio_state_vet
DRIVE_SYDNEY_ID     = "1-Rl1UMq8px1u3Jw8FugDrohZnNJDLS3X"   # sydney_vet

# ── OpenAlex (Domain>Field>Subfield>Topic taxonomy segmentation) ─────────────
DRIVE_OPENALEX_VET_ID          = "1ODS5jx8DlV3QVJuVS-Vz02nbzcCB-jxY"   # openalex_veterinaria

# ── Drive IDs — batch 4 (90+ fuentes adicionales) ─────────────────────────────
# A. Sociedades
DRIVE_ECVIM_CONGRESS_ID        = "11GemfGD3L_Z01ifnHYeucGmMbXbQAcEH"
DRIVE_ESCCAP_ID                = "1eVVXILqiX-H4xFLVitLWX8RbbVMbEXAD"
DRIVE_CAPC_ID                  = "1QxLzE5CM3wwqJ18TXRUyTTUJ5dVNywYz"
DRIVE_TROCCAP_ID               = "1-EyBxFvs8LSEeN55SwA3VzXwh6vB4usm"
DRIVE_ABCD_CATS_ID             = "1yTXzrVD4keZN-OJlPCbVKE1xHRDYZmbL"
DRIVE_ISCAID_ID                = "15juVFj1CfNYk7ZViIofOhtbK4EmhYX8L"
DRIVE_VECCS_RECOVER_ID         = "1AsCcJPp_Q9xbxk2brnwQoEFq6NvOpNWb"
DRIVE_FECAVA_ID                = "1HalLMs9upepGHcWI8Cx-hqLZs3vwEu4L"
DRIVE_AAFP_FELINE_ID           = "1BMgATa7fZiQu6QyeWrKoJvKuiXTrwstH"
DRIVE_LAVECCS_ID               = "13ddiK1Q_tOig5Bm-5lh64i154T3PN6Av"
DRIVE_CVMA_ID                  = "1FtP6NIfFkVaIJGn-hA0MVwWWtPdwAO24"
DRIVE_NZVA_ID                  = "1x0OxsHQ1zWpzkuEx-YP0BmtOvlakNvG-"
DRIVE_WAVMA_ID                 = "1ZwbIhtANDbtiLFbkovnT-hNXInlULyUk"
DRIVE_AASV_ID                  = "12pnL4VZSLjvrWyCGA9AgUXy8kHuP2CW7"
DRIVE_AABP_ID                  = "1gwWnzHPSZXiIcxfS28unS0sqptPGoS39"
DRIVE_AAV_AVIAN_ID             = "1mQIJpoV-sK4iTfmAU8c5OV-QEWTmm5lr"
# B. Revistas OA adicionales
DRIVE_EUROPE_PMC_VET_ID        = "110ExE8IdNnmVT3nq0FMvckK4_qB6xjDj"
DRIVE_VETERINARY_WORLD_ID      = "1ekjVJ-11ID29j7Gl2EIl231d5mN4VXY9"
DRIVE_VETERINARY_EVIDENCE_ID   = "153cuSYFezDdSUnN_pmhRErONV_BqIwXt"
DRIVE_OPEN_VET_JOURNAL_ID      = "1oee2JdcGh2l6sjnXeUp2okenWxYUTXgB"
DRIVE_JSTAGE_JVMS_ID           = "1t35vS-ueslyQCh9eAEL3Jkyhx0-ZUuw4"
DRIVE_SCIELO_VET_ID            = "18jy5kOJ5c2oMxb54lmMeZ1-kye6O_1Wj"
DRIVE_JOURNAL_SHELTER_MED_ID   = "1crzQIg0FyFiIKlWsJt_eeZOj1bp0E0BE"
DRIVE_BMC_VET_RESEARCH_ID      = "1ugJ5NysJlTY-clcWng2J7MemsFzmueTh"
DRIVE_PARASITES_VECTORS_VET_ID = "1edcqeGEqtlE1PLI18dyoV0d9SEDaD0Gt"
# C. Farmacología veterinaria
DRIVE_VMD_UK_ID                = "1e4KOTWwveuvIOIVFqPcW_-debBFpki1X"
DRIVE_APVMA_AUSTRALIA_ID       = "1ZKc0Vnxn1514t6_bjDZgGVABXmenWhQQ"
DRIVE_ACVM_NEWZEALAND_ID       = "19qIXNcjM1FZjRzhemXObVrxZ9ZlbabIP"
DRIVE_HEALTH_CANADA_VET_ID     = "1zT524wBumOLBcWjUdF9d3MRcwGABqvnY"
DRIVE_UK_VARSS_ID              = "1pEx0W_x0q5spugy6f3dlPIarzRXDvRVb"
DRIVE_UK_VET_PHARMACOVIGILANCE_ID = "1rM9hfZDLIRWxefkCXNLuiRPQhIQtVlK3"
DRIVE_DRUGCENTRAL_VET_ID       = "1JYtAKpWS36Y9wt3vJxIGog9FmeOcu1uy"
DRIVE_CHEMBL_VET_ID            = "1jEQK51z-RE2f5CMaMGthyT4Y_BKrYtLj"
# D. Universidades adicionales
DRIVE_RVC_LONDON_ID            = "1Iu5ZAIT7swZEeWh7FrE6Mp9JDnAqy6YF"
DRIVE_EDINBURGH_VET_ID         = "1R1UHV-RQOUphFtPuRtxhCf1kv8jJvVp2"
DRIVE_MELBOURNE_VET_ID         = "1ZjOclOWVJ_YkSRyVCfh6CPSRIiXnF4jx"
DRIVE_UTRECHT_VET_ID           = "1h0Tz7Q7iXXGXUnyrEkwGd-rfmiatR2j9"
DRIVE_GUELPH_OVC_ID            = "1Zk1IlkCONU_cS0sHTRvqVpvUlnWQfUyj"
DRIVE_VETMEDUNI_VIENNA_ID      = "1zm5TPWVXqOPGg3n1D7yjylxcdeKstgaj"
DRIVE_LIVERPOOL_SAVSNET_ID     = "1ElZ75jyXFmq_UIDIngdbQmGSF3iTK67F"
DRIVE_NOTTINGHAM_CEVM_ID       = "1-w5hAcpyHOv4z3qKZs997_ExPCo49_mD"
DRIVE_IOWA_CFSPH_ID            = "1NEdxfGRKVF2E3-6i-5CRtE4M5XAnftpW"
DRIVE_MINNESOTA_CAHFS_ID       = "1ip28i7rZykrpdW3xGwFESyXRllppZxAT"
DRIVE_TUFTS_VET_ID             = "1-qnEEMah4U7S7c3W7zEHr1-FkR1deuDa"
DRIVE_GLASGOW_VET_ID           = "18codDRGa1X0kz1uRZJVzQASwiVv2rhiB"
DRIVE_BRISTOL_VET_ID           = "1eS86ZZEWvifvbYKb34OVi5OIoQq99h3I"
# E. Organizaciones regionales
DRIVE_FVE_EUROPE_ID            = "1Qo9k3zhfMK7GU5uoHSkRgTvJNdLxhd1I"
DRIVE_AVA_AUSTRALIA_ID         = "1gbqTPt3La1deb4ODrz-CZJrkSd4POGFm"
DRIVE_CAHSS_CANADA_ID          = "1UXWeyJMic3rA-4XfURQl6QnjxPCfg5yZ"
DRIVE_CFIA_ANIMAL_HEALTH_ID    = "1RBN51bYSYpptk3OOgjjLUnQLjvO1lg87"
DRIVE_UK_APHA_ID               = "1hmKV4Bj7zISC7TU-3mr2dltizK7OhS6D"
DRIVE_USDA_APHIS_VET_ID        = "1MLpDBz08LBV9Wg6hRzTVwtdE5m6uB_AY"
DRIVE_USDA_NAHMS_ID            = "1Nu8KyEJpNcSTa7IFyJIZnfi3EStwb-oq"
DRIVE_EC_ANIMAL_HEALTH_ID      = "10UfbVDmevi3mBlzz4-YFRDU08B9K8cZl"
DRIVE_AHA_AUSTRALIA_ID         = "1HhTsZjSkY1FhmOSG45TfTJb4-g0DX9pI"
DRIVE_AGRICULTURE_VICTORIA_ID  = "1BMdjIn6kczwAwqKKr02KEjF8CDQBKP8_"
DRIVE_ANIMAL_HEALTH_IRELAND_ID = "1eOwh53eOlEs-wsVy1xydWCwJ3IwqXQN-"
# F. Bases de datos clínicas
DRIVE_VETSREV_ID               = "1OpLFrXW2foQirNVKPUMgycMZtlW9GdVu"
DRIVE_OMIA_ID                  = "1qhSrnsoMYQDJNdB_inwEfwGP13Z9fKrB"
DRIVE_VETBACT_ID               = "1k0baC6N-3nzsXeSllEPWhzOFA5WdRkpa"
DRIVE_VETCOMPASS_ID            = "12CP1Jr3AN1439oqobwOCeY3QZzXhCi3P"
DRIVE_VBO_BREEDS_ID            = "1Woa_WC3ab5gtpr3WqbRIfXoZJnttkrWt"
DRIVE_GBADS_ID                 = "1mM2G2rESqnAVRm4W3-tLr3qIdspEE8me"
DRIVE_CIDD_ID                  = "10_ooVGDGAEXygNk1lFe2SnZaKJOQIkGK"
DRIVE_PENNGEN_ID               = "1FPae9Sr4m2aO489ehgMTMiwpBGa3INc0"
DRIVE_ANIMAL_QTLDB_ID          = "1wbmXOuKgNzCcbBUjODlIb-rWnvP5dZSi"
DRIVE_PHI_BASE_ID              = "1PtiS2XSkd8-V__zfqly-l6y1nLzpzDzA"
DRIVE_UK_VIDA_ID               = "1SyRHQkwBqHKrghAHnZAhq1zYZV73y91o"
# G. Nutrición y bienestar
DRIVE_FEDIAF_ID                = "1jjt6go8I71BoNZS6Iz-OBXOeRA1AfQp0"
DRIVE_PET_NUTRITION_ALLIANCE_ID = "1MeyVqtTFt3bPPxCFaOTdXiOd0Ik9Iqkp"
DRIVE_TUFTS_PETFOODOLOGY_ID    = "1UXtBYZd0CNsVYCzfx4jnAp4Nw5kHISIa"
DRIVE_WALTHAM_ID               = "1XsIaLQ-JI1RlFLCsmfxH2TmP_hF_vMRw"
DRIVE_RSPCA_KNOWLEDGEBASE_ID   = "1nkBFQt6E7NcZvPV0CWdpWD4YNepNmeWj"
DRIVE_MADDIES_FUND_ID          = "1TNaUqdi4DDEtvCZgNG3-ygzrBJ-BLDwq"
DRIVE_ASPCAPRO_SHELTER_ID      = "1ydmt6EqepYYVPU3snhJd8s-1ODik59NW"
DRIVE_AWIN_WELFARE_ID          = "1WxXFVSIb1umLlftGD1wskOza3E_f7OtM"
DRIVE_ICAM_COALITION_ID        = "1ZvbAQdj9Gd9UWML9WwK_b30ScmCr2Vhf"
DRIVE_UFAW_ID                  = "1Qv8th7rYSZSQ5z84Yqfh2YIU19XI_0z1"
DRIVE_NAL_ANIMAL_HEALTH_ID     = "1SWz-WJPuiEgqFECciR3TZ4M246hjGYB1"
DRIVE_HUMANE_SLAUGHTER_ID      = "1dH4nTl8bSNtdW92G_ViVqVhtFDUOkqdp"

# ── Nuevas (Inventario Complementario 2026-07-26) ──────────────────────────────
DRIVE_BEVA_EQUINE_ID           = "1PmXfr_bxDXS6q-D4JKZLXVJOZq9Ys21Z"
DRIVE_AAEP_EQUINE_ID           = "15WhG3s9uJ0ZkHVDxJdGHXeqsG0gdCVfE"
DRIVE_BSAVA_METADATA_ID        = "1P1f45o_ScE3Q3osk6bLdrXFhRamm4zAU"
DRIVE_IVIS_METADATA_ID         = "1aDENIEEowH0BXIEtMaqvjPb0QGTWWh4u"
DRIVE_VETERINARY_RESEARCH_SPRINGER_ID = "1GqbbkYaRM5QcIfvWha9lrZd1NNV27Zdw"
DRIVE_ACTA_VET_SCANDINAVICA_ID = "1bouC_Y062AIReq_NJwRN9tW8ZRB018SN"
DRIVE_ANIMALS_MDPI_ID          = "1W_9makR1WmbZU2modWfNvGIJ4eT36LGJ"
DRIVE_VETSCI_MDPI_ID           = "1bwjb-fCVfJGQN-pYZGHLq-EFHiD__Dj3"
DRIVE_IRISH_VET_JOURNAL_ID     = "1HK5nnHF5GzIpotW9waystv5_P1Vu-ZWW"
DRIVE_CANINE_MEDICINE_GENETICS_ID = "1OXPWqaDN5sYhQNUjXd326Ymfz-HaDMjy"
DRIVE_JVETRES_POLAND_ID        = "1TWf6hvJ3LE2avDF7plgD5VO78otO9Dtz"
DRIVE_BJVRAS_BRAZIL_ID         = "1L9tV4bhB5MhAE07WFSspnPtFySXfxXCm"
DRIVE_JVS_KOREA_ID             = "1b-FxfHDl1p4Co1z2rowpEGljksrJetwe"
DRIVE_HYBRID_VET_JOURNALS_OA_ID = "1hCdPRdHPPAovR_Qjkz8xsCUezSz8zvAL"
DRIVE_FARAD_ID                 = "1StwBk-kALjQA3AKA4JucNcge7oQtdCRr"
DRIVE_NVAL_JAPAN_ID            = "1Z06JZBRa8rWaLDNzcoTXSCw-n-5o1WJK"
DRIVE_FAANG_DATA_PORTAL_ID     = "1BCAN_WObajqdYtgs_Sf9d6Eb69SBNlYe"
DRIVE_ASSOC_SHELTER_VETS_GUIDELINES_ID = "1_5LyPNSdvD132yWKWSTVq0pE6zJXTIco"
DRIVE_RSPCA_SCIENCE_REPORTS_ID = "12xzGZuEa_jLvsOJjDG3XRuLat54LuVjk"
DRIVE_SHELTER_ANIMALS_COUNT_ID = "119cPcb5MHpd71n0vSxU3o6Nqf8go2lFA"
# Nota: "Animal Welfare Institute" ya cubierto por DRIVE_AWIN_WELFARE_ID (awionline.org).
# "Veterinary Breed Ontology" y "UK VIDA surveillance" reutilizan folders ya
# existentes (DRIVE_VBO_BREEDS_ID, DRIVE_UK_VIDA_ID) que estaban huérfanos/rotos.

PROGRESS_FILE = "progress_vet.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

# ── Sitemaps y endpoints por fuente ───────────────────────────────────────────

MERCK_SITEMAPS = [
    "https://www.merckvetmanual.com/sitemaps/veterinary-topic.xml.gz",
    "https://www.merckvetmanual.com/sitemaps/veterinary-casestudy.xml",
    "https://www.merckvetmanual.com/sitemaps/veterinary-news.xml",
]
AAHA_SITEMAPS = [
    "https://www.aaha.org/resource-sitemap.xml",
    "https://www.aaha.org/resource-sitemap2.xml",
    "https://www.aaha.org/publication-sitemap.xml",
    "https://www.aaha.org/publication-sitemap2.xml",
]
ACVS_SITEMAPS = [
    "https://www.acvs.org/small-animal-sitemap.xml",
    "https://www.acvs.org/large-animal-sitemap.xml",
    "https://www.acvs.org/resources-sitemap.xml",
    "https://www.acvs.org/post-sitemap.xml",
]
MSD_SITEMAPS = [
    "https://www.msdvetmanual.com/sitemaps/veterinary-topic.xml.gz",
]
ACVIM_SITEMAPS = [
    "https://acvim.org/sitemap.xml",
]
CB_SITEMAP_INDEX  = "https://www.cliniciansbrief.com/sitemap.xml"
TVP_SITEMAP_INDEX = "https://todaysveterinarypractice.com/sitemap.xml"
FAO_SITEMAP_INDEX = "https://www.fao.org/sitemap.xml"
CORNELL_SITEMAP_INDEX  = "https://www.vet.cornell.edu/sitemap.xml"
PURDUE_SITEMAP_INDEX   = "https://vet.purdue.edu/sitemap.xml"
TAMU_SITEMAP_INDEX     = "https://vetmed.tamu.edu/sitemap.xml"
OSU_SITEMAP            = "https://vet.osu.edu/sitemap.xml"
SYDNEY_SITEMAP_INDEX   = "https://www.sydney.edu.au/sitemap.xml"
EFSA_SEED    = "https://www.efsa.europa.eu/en/topics/topic/animal-health"
UCDAVIS_SEED = "https://www.vetmed.ucdavis.edu"

WOAH_SITEMAP_INDEX      = "https://www.woah.org/sitemap_index.xml"
AAVMC_SITEMAP_INDEX     = "https://aavmc.org/sitemap_index.xml"
EMA_SITEMAP_INDEX       = "https://www.ema.europa.eu/sitemap.xml"
PPH_SITEMAP_INDEX       = "https://www.petpoisonhelpline.com/sitemap_index.xml"
FRONTIERS_SITEMAP_INDEX = "https://www.frontiersin.org/articles/sitemap-index.xml"
WSAVA_GUIDELINES_INDEX  = "https://wsava.org/global-guidelines/"
ASPCA_SITEMAP           = "https://www.aspca.org/sitemap.xml"
NOAH_SITEMAP            = "https://www.noahcompendium.co.uk/Sitemaps/1.xml"
FDA_CVM_SEED            = "https://www.fda.gov/animal-veterinary"
PLOS_API_URL            = "https://api.plos.org/search"

# ── Drive ──────────────────────────────────────────────────────────────────────

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
    if "merckvetmanual.com" in url:  return DRIVE_MERCK_ID
    if "msdvetmanual.com"   in url:  return DRIVE_MSD_ID
    if "woah.org"           in url:  return DRIVE_WOAH_ID
    if "wsava.org"          in url:  return DRIVE_WSAVA_ID
    if "acvs.org"           in url:  return DRIVE_ACVS_ID
    if "acvim.org"          in url:  return DRIVE_ACVIM_ID
    if "aavmc.org"          in url:  return DRIVE_AAVMC_ID
    if "noahcompendium"     in url:  return DRIVE_NOAH_ID
    if "ema.europa.eu"      in url:  return DRIVE_EMA_ID
    if "fda.gov"            in url:  return DRIVE_FDA_ID
    if "aspca.org"          in url:  return DRIVE_ASPCA_ID
    if "petpoisonhelpline"  in url:  return DRIVE_PPH_ID
    if "frontiersin.org"    in url:  return DRIVE_FRONTIERS_ID
    if "plos.org"           in url:  return DRIVE_PLOS_ID
    if "cliniciansbrief"    in url:  return DRIVE_CB_ID
    if "todaysveterinary"   in url:  return DRIVE_TVP_ID
    if "efsa.europa.eu"     in url:  return DRIVE_EFSA_ID2
    if "fao.org"            in url:  return DRIVE_FAO_ID
    if "vet.cornell.edu"    in url:  return DRIVE_CORNELL_ID
    if "vetmed.ucdavis"     in url:  return DRIVE_UCDAVIS_ID
    if "vet.purdue.edu"     in url:  return DRIVE_PURDUE_ID
    if "vetmed.tamu.edu"    in url:  return DRIVE_TAMU_ID
    if "vet.osu.edu"        in url:  return DRIVE_OSU_ID
    if "sydney.edu.au"      in url:  return DRIVE_SYDNEY_ID
    if "aaha.org"           in url:  return DRIVE_AAHA_ID
    # ── batch 4 ───────────────────────────────────────────────────────────────
    # A. Sociedades
    if "ecvim.org"          in url:  return DRIVE_ECVIM_CONGRESS_ID
    if "esccap.org"         in url:  return DRIVE_ESCCAP_ID
    if "capcvet.org"        in url:  return DRIVE_CAPC_ID
    if "troccap.com"        in url:  return DRIVE_TROCCAP_ID
    if "abcdcatsvets.org"   in url:  return DRIVE_ABCD_CATS_ID
    if "iscaid.org"         in url:  return DRIVE_ISCAID_ID
    if "veccs.org"          in url or "recover-cpr.org" in url: return DRIVE_VECCS_RECOVER_ID
    if "fecava.org"         in url:  return DRIVE_FECAVA_ID
    if "catvets.com"        in url:  return DRIVE_AAFP_FELINE_ID
    if "laveccs.org"        in url:  return DRIVE_LAVECCS_ID
    if "canadianveterinarians.net" in url: return DRIVE_CVMA_ID
    if "nzva.org.nz"        in url:  return DRIVE_NZVA_ID
    if "wavma.org"          in url:  return DRIVE_WAVMA_ID
    if "aasv.org"           in url:  return DRIVE_AASV_ID
    if "aabp.org"           in url:  return DRIVE_AABP_ID
    if "associationofavianvets.org" in url: return DRIVE_AAV_AVIAN_ID
    # B. Revistas OA adicionales
    if "europepmc.org"      in url:  return DRIVE_EUROPE_PMC_VET_ID
    if "veterinaryworld.org" in url: return DRIVE_VETERINARY_WORLD_ID
    if "veterinaryevidence.org" in url: return DRIVE_VETERINARY_EVIDENCE_ID
    if "benthamopen.com/TOVETJ" in url: return DRIVE_OPEN_VET_JOURNAL_ID
    if "jstage.jst.go.jp"   in url:  return DRIVE_JSTAGE_JVMS_ID
    if "scielo.org"         in url or "scielo.br" in url: return DRIVE_SCIELO_VET_ID
    if "sheltervet.org"     in url or "journalofsheltervet" in url: return DRIVE_JOURNAL_SHELTER_MED_ID
    if "bmcvetres.biomedcentral.com" in url: return DRIVE_BMC_VET_RESEARCH_ID
    if "parasitesandvectors.com" in url: return DRIVE_PARASITES_VECTORS_VET_ID
    # C. Farmacología veterinaria
    if "vmd.defra.gov.uk"   in url:  return DRIVE_VMD_UK_ID
    if "apvma.gov.au"       in url:  return DRIVE_APVMA_AUSTRALIA_ID
    if "epa.govt.nz"        in url or "acvm.govt.nz" in url: return DRIVE_ACVM_NEWZEALAND_ID
    if "canada.ca/en/health-canada" in url and "vet" in url: return DRIVE_HEALTH_CANADA_VET_ID
    if "vmd.defra.gov.uk/varss" in url: return DRIVE_UK_VARSS_ID
    if "pharmacovigilance" in url and "vet" in url: return DRIVE_UK_VET_PHARMACOVIGILANCE_ID
    if "drugcentral.org"    in url:  return DRIVE_DRUGCENTRAL_VET_ID
    if "ebi.ac.uk/chembl"   in url or "chembl.org" in url: return DRIVE_CHEMBL_VET_ID
    # D. Universidades adicionales
    if "rvc.ac.uk"          in url:  return DRIVE_RVC_LONDON_ID
    if "ed.ac.uk"           in url and "vet" in url: return DRIVE_EDINBURGH_VET_ID
    if "unimelb.edu.au"     in url and "vet" in url: return DRIVE_MELBOURNE_VET_ID
    if "uu.nl"              in url and "vet" in url: return DRIVE_UTRECHT_VET_ID
    if "uoguelph.ca"        in url:  return DRIVE_GUELPH_OVC_ID
    if "vetmeduni.ac.at"    in url:  return DRIVE_VETMEDUNI_VIENNA_ID
    if "liverpool.ac.uk"    in url and ("vet" in url or "savsnet" in url): return DRIVE_LIVERPOOL_SAVSNET_ID
    if "nottingham.ac.uk"   in url and "vet" in url: return DRIVE_NOTTINGHAM_CEVM_ID
    if "cfsph.iastate.edu"  in url:  return DRIVE_IOWA_CFSPH_ID
    if "cahfs.umn.edu"      in url:  return DRIVE_MINNESOTA_CAHFS_ID
    if "tufts.edu"          in url and "vet" in url: return DRIVE_TUFTS_VET_ID
    if "gla.ac.uk"          in url and "vet" in url: return DRIVE_GLASGOW_VET_ID
    if "bristol.ac.uk"      in url and "vet" in url: return DRIVE_BRISTOL_VET_ID
    # E. Organizaciones regionales
    if "fve.org"            in url:  return DRIVE_FVE_EUROPE_ID
    if "ava.com.au"         in url:  return DRIVE_AVA_AUSTRALIA_ID
    if "cahss.org"          in url:  return DRIVE_CAHSS_CANADA_ID
    if "inspection.canada.ca" in url or "inspection.gc.ca" in url: return DRIVE_CFIA_ANIMAL_HEALTH_ID
    if "apha.gov.uk"        in url:  return DRIVE_UK_APHA_ID
    if "aphis.usda.gov"     in url:  return DRIVE_USDA_APHIS_VET_ID
    if "nahms.usda.gov"     in url:  return DRIVE_USDA_NAHMS_ID
    if "ec.europa.eu"       in url and "animal" in url: return DRIVE_EC_ANIMAL_HEALTH_ID
    if "animalhealthaustralia.com.au" in url: return DRIVE_AHA_AUSTRALIA_ID
    if "agriculture.vic.gov.au" in url: return DRIVE_AGRICULTURE_VICTORIA_ID
    if "animalhealthireland.ie" in url: return DRIVE_ANIMAL_HEALTH_IRELAND_ID
    # F. Bases de datos
    if "vetsrev.nottingham.ac.uk" in url: return DRIVE_VETSREV_ID
    if "omia.org"           in url:  return DRIVE_OMIA_ID
    if "vetbact.org"        in url:  return DRIVE_VETBACT_ID
    if "vetcompass.org"     in url:  return DRIVE_VETCOMPASS_ID
    if "vbo.org" in url or "breeds.org" in url or "vertebrate-breed-ontology" in url: return DRIVE_VBO_BREEDS_ID
    if "gbads.org"          in url or "animalhealthmetrics.org" in url: return DRIVE_GBADS_ID
    if "cidd.org"           in url:  return DRIVE_CIDD_ID
    if "vet.upenn.edu/penngen" in url: return DRIVE_PENNGEN_ID
    if "animalgenome.org/QTLdb" in url: return DRIVE_ANIMAL_QTLDB_ID
    if "phi-base.org"       in url:  return DRIVE_PHI_BASE_ID
    if "gov.uk" in url and "scanning-surveillance" in url: return DRIVE_UK_VIDA_ID
    # G. Nutrición y bienestar
    if "fediaf.org"         in url:  return DRIVE_FEDIAF_ID
    if "petnutritionalliance.org" in url: return DRIVE_PET_NUTRITION_ALLIANCE_ID
    if "vetnutrition.tufts.edu" in url: return DRIVE_TUFTS_PETFOODOLOGY_ID
    if "waltham.com"        in url:  return DRIVE_WALTHAM_ID
    if "kb.rspca.org.au"    in url:  return DRIVE_RSPCA_KNOWLEDGEBASE_ID
    if "maddiesfund.org"    in url:  return DRIVE_MADDIES_FUND_ID
    if "aspcapro.org"       in url:  return DRIVE_ASPCAPRO_SHELTER_ID
    if "awionline.org"      in url or "awin-site.org" in url: return DRIVE_AWIN_WELFARE_ID
    if "icam-coalition.org" in url:  return DRIVE_ICAM_COALITION_ID
    if "ufaw.org.uk"        in url:  return DRIVE_UFAW_ID
    if "nal.usda.gov"       in url and "animal" in url: return DRIVE_NAL_ANIMAL_HEALTH_ID
    if "hsa.org.uk"         in url or "humane-slaughter.org" in url: return DRIVE_HUMANE_SLAUGHTER_ID

    # ── Nuevas (Inventario Complementario 2026-07-26) ───────────────────────────
    if "beva.org.uk"        in url:  return DRIVE_BEVA_EQUINE_ID
    if "aaep.org"           in url:  return DRIVE_AAEP_EQUINE_ID
    if "bsavalibrary.com"   in url:  return DRIVE_BSAVA_METADATA_ID
    if "ivis.org"           in url:  return DRIVE_IVIS_METADATA_ID
    if "link.springer.com/journal/13567" in url: return DRIVE_VETERINARY_RESEARCH_SPRINGER_ID
    if "actavetscand.biomedcentral.com" in url: return DRIVE_ACTA_VET_SCANDINAVICA_ID
    if "mdpi.com" in url and "/animals/" in url: return DRIVE_ANIMALS_MDPI_ID
    if "mdpi.com" in url and "/vetsci/" in url: return DRIVE_VETSCI_MDPI_ID
    if "irishvetjournal.biomedcentral.com" in url: return DRIVE_IRISH_VET_JOURNAL_ID
    if "cgejournal.biomedcentral.com" in url: return DRIVE_CANINE_MEDICINE_GENETICS_ID
    if "sciendo.com" in url and "jvetres" in url.lower(): return DRIVE_JVETRES_POLAND_ID
    if "revistas.usp.br/bjvras" in url: return DRIVE_BJVRAS_BRAZIL_ID
    if "vetsci.org"         in url:  return DRIVE_JVS_KOREA_ID
    if "|HYBRID_VET_OA|"    in url:  return DRIVE_HYBRID_VET_JOURNALS_OA_ID
    if "|OPENALEX_VET|"     in url:  return DRIVE_OPENALEX_VET_ID
    if "farad.org"          in url:  return DRIVE_FARAD_ID
    if "maff.go.jp/nval"    in url:  return DRIVE_NVAL_JAPAN_ID
    if "faang" in url and "data.faang.org" in url: return DRIVE_FAANG_DATA_PORTAL_ID
    if "shelterstandards" in url or "sheltervetstandards" in url: return DRIVE_ASSOC_SHELTER_VETS_GUIDELINES_ID
    if "rspca.org.uk" in url and ("science" in url or "research" in url): return DRIVE_RSPCA_SCIENCE_REPORTS_ID
    if "shelteranimalscount.org" in url: return DRIVE_SHELTER_ANIMALS_COUNT_ID

    return DRIVE_AAHA_ID  # fallback


def upload_file(service, url, name, content):
    folder_id = folder_for_url(url)
    media = MediaInMemoryUpload(content.encode("utf-8"), mimetype="text/plain")
    service.files().create(
        body={"name": name, "parents": [folder_id]},
        media_body=media, fields="id"
    ).execute()


# ── Helpers de sitemap ─────────────────────────────────────────────────────────

def fetch_urls_from_sitemap(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    if r.status_code == 429:
        # Rate-limited: skip silently (no reintentar, el siguiente delay ayudará)
        return []
    if not r.ok:
        return []
    try:
        root = ET.fromstring(r.text)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        return [el.text for el in root.findall(".//sm:loc", ns)]
    except ET.ParseError:
        # Fallback regex para XML con caracteres especiales no escapados
        return re.findall(r"<loc>\s*(https?://[^<\s]+)\s*</loc>", r.text)


def _fetch_sitemap_index_urls(index_url, url_filter=None, delay=0.5):
    """Descarga un sitemap-index, luego cada sub-sitemap; filtra con url_filter."""
    sub_sitemaps = fetch_urls_from_sitemap(index_url)
    all_urls = []
    for sm in sub_sitemaps:
        urls = fetch_urls_from_sitemap(sm)
        if url_filter:
            urls = [u for u in urls if url_filter(u)]
        all_urls.extend(urls)
        time.sleep(delay)
    return all_urls


# ── Descubridores por fuente ───────────────────────────────────────────────────

def fetch_woah_urls():
    r = requests.get(WOAH_SITEMAP_INDEX, headers=HEADERS, timeout=30)
    root = ET.fromstring(r.text)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sub_sitemaps = [el.text for el in root.findall(".//sm:loc", ns)]
    print(f"  WOAH: {len(sub_sitemaps)} sub-sitemaps", flush=True)
    en_urls = []
    for sm in sub_sitemaps:
        try:
            urls = fetch_urls_from_sitemap(sm)
            en_urls.extend(u for u in urls if "/en/" in u or u.rstrip("/").endswith("/en"))
        except Exception as e:
            print(f"    WOAH error {sm.split('/')[-1]}: {e}", flush=True)
        time.sleep(0.5)
    return en_urls


def fetch_wsava_guideline_urls():
    r = requests.get(WSAVA_GUIDELINES_INDEX, headers=HEADERS, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "wsava.org" in href and href != WSAVA_GUIDELINES_INDEX:
            if not any(s in href for s in ["#", "mailto:", "javascript:"]):
                links.add(href.rstrip("/"))
        elif href.startswith("/") and len(href) > 1:
            links.add("https://wsava.org" + href.rstrip("/"))
    return [
        u for u in links
        if "wsava.org" in u
        and not u.endswith("wsava.org")
        and "/global-guidelines" not in u.rstrip("/")
    ]


def fetch_aavmc_urls():
    return _fetch_sitemap_index_urls(AAVMC_SITEMAP_INDEX)


def fetch_ema_vet_urls():
    """Filtra el enorme sitemap de EMA a solo páginas de medicamentos veterinarios."""
    return _fetch_sitemap_index_urls(
        EMA_SITEMAP_INDEX,
        url_filter=lambda u: "/veterinary-medicines" in u,
        delay=2.0,  # EMA tiene rate-limit agresivo — 2s entre sub-sitemaps
    )


def fetch_fda_cvm_urls():
    """Crawl de 1 nivel desde la página principal de FDA CVM."""
    seed = FDA_CVM_SEED
    prefix_abs = "https://www.fda.gov/animal-veterinary"
    prefix_rel = "/animal-veterinary"
    visited = set()
    try:
        r = requests.get(seed, headers=HEADERS, timeout=20)
        visited.add(seed)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"].split("#")[0].split("?")[0]
            if href.startswith(prefix_rel):
                visited.add("https://www.fda.gov" + href)
            elif href.startswith(prefix_abs):
                visited.add(href)
    except Exception as e:
        print(f"  FDA CVM error: {e}", flush=True)
    return list(visited)


def fetch_aspca_tox_urls():
    """Solo páginas del sitio ASPCA relacionadas con toxicología."""
    try:
        urls = fetch_urls_from_sitemap(ASPCA_SITEMAP)
    except Exception as e:
        print(f"  ASPCA sitemap error: {e}", flush=True)
        return []
    return [
        u for u in urls
        if "poison" in u or "toxic" in u or "animal-poison-control" in u
    ]


def fetch_pph_urls():
    """Pet Poison Helpline — incluye las sub-sitemaps de base de datos de toxinas."""
    return _fetch_sitemap_index_urls(PPH_SITEMAP_INDEX)


def fetch_frontiers_vet_urls():
    """Artículos de Frontiers in Veterinary Science filtrados por URL."""
    return _fetch_sitemap_index_urls(
        FRONTIERS_SITEMAP_INDEX,
        url_filter=lambda u: "veterinary-science" in u or "fvets" in u,
        delay=0.3,
    )


def _crawl_one_level(seed, domain_prefix, delay=2.0):
    """Crawl de 1 nivel: recoge todos los links del seed dentro del mismo dominio."""
    visited = set()
    try:
        r = requests.get(seed, headers=HEADERS, timeout=20)
        visited.add(seed)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"].split("#")[0].split("?")[0]
            if href.startswith(domain_prefix):
                visited.add(href if href.startswith("http") else "https://" + href.lstrip("/"))
            elif href.startswith("/") and domain_prefix in seed:
                base = seed.split("/")[0] + "//" + seed.split("/")[2]
                visited.add(base + href)
    except Exception as e:
        print(f"  crawl error {seed}: {e}", flush=True)
    time.sleep(delay)
    return list(visited)


def fetch_efsa_urls():
    return _crawl_one_level(EFSA_SEED, "efsa.europa.eu", delay=10.0)


def fetch_ucdavis_urls():
    return _crawl_one_level(UCDAVIS_SEED, "vetmed.ucdavis.edu", delay=2.0)


def fetch_sydney_vet_urls():
    """Sydney tiene sitemap universitario grande; filtra a la escuela de veterinaria."""
    return _fetch_sitemap_index_urls(
        SYDNEY_SITEMAP_INDEX,
        url_filter=lambda u: "veterinary-science" in u or "/vet/" in u,
        delay=1.0,
    )


def fetch_clinicians_brief_urls():
    return _fetch_sitemap_index_urls(CB_SITEMAP_INDEX, delay=1.0)


def fetch_tvp_urls():
    return _fetch_sitemap_index_urls(TVP_SITEMAP_INDEX, delay=1.0)


def fetch_fao_animal_health_urls():
    return _fetch_sitemap_index_urls(
        FAO_SITEMAP_INDEX,
        url_filter=lambda u: "animal-health" in u or "animal-disease" in u or "animal-production" in u,
        delay=1.0,
    )


def fetch_cornell_vet_urls():
    return _fetch_sitemap_index_urls(CORNELL_SITEMAP_INDEX, delay=1.0)


def fetch_purdue_vet_urls():
    return _fetch_sitemap_index_urls(PURDUE_SITEMAP_INDEX, delay=1.0)


def fetch_tamu_vet_urls():
    return _fetch_sitemap_index_urls(TAMU_SITEMAP_INDEX, delay=1.0)


def fetch_osu_vet_urls():
    return fetch_urls_from_sitemap(OSU_SITEMAP)


# ── Fetchers batch 4 ──────────────────────────────────────────────────────────

# A. Sociedades
def fetch_ecvim_urls():
    return _crawl_one_level("https://www.ecvim-ca.org/congress/proceedings", "ecvim-ca.org", delay=3.0)

def fetch_esccap_urls():
    return _crawl_one_level("https://www.esccap.org/guidelines/", "esccap.org", delay=3.0)

def fetch_capc_urls():
    return _crawl_one_level("https://capcvet.org/guidelines/", "capcvet.org", delay=3.0)

def fetch_troccap_urls():
    return _crawl_one_level("https://www.troccap.com/recommendations/", "troccap.com", delay=3.0)

def fetch_abcd_cats_urls():
    return _crawl_one_level("https://www.abcdcatsvets.org/guidelines/", "abcdcatsvets.org", delay=3.0)

def fetch_iscaid_urls():
    return _crawl_one_level("https://www.iscaid.org/guidelines/", "iscaid.org", delay=3.0)

def fetch_veccs_recover_urls():
    urls = _crawl_one_level("https://www.veccs.org/education/", "veccs.org", delay=3.0)
    urls += _crawl_one_level("https://www.recover-cpr.org/guidelines/", "recover-cpr.org", delay=3.0)
    return urls

def fetch_fecava_urls():
    return _crawl_one_level("https://www.fecava.org/policies-actions/", "fecava.org", delay=3.0)

def fetch_aafp_feline_urls():
    return _crawl_one_level("https://catvets.com/guidelines/practice-guidelines/", "catvets.com", delay=3.0)

def fetch_laveccs_urls():
    return _crawl_one_level("https://www.laveccs.org/", "laveccs.org", delay=3.0)

def fetch_cvma_urls():
    return _crawl_one_level("https://www.canadianveterinarians.net/policy-and-outreach/", "canadianveterinarians.net", delay=3.0)

def fetch_nzva_urls():
    return _crawl_one_level("https://www.nzva.org.nz/page/resources", "nzva.org.nz", delay=3.0)

def fetch_wavma_urls():
    return _crawl_one_level("https://www.wavma.org/", "wavma.org", delay=3.0)

def fetch_aasv_urls():
    return _crawl_one_level("https://www.aasv.org/pages/aasv_resources.php", "aasv.org", delay=3.0)

def fetch_aabp_urls():
    return _crawl_one_level("https://www.aabp.org/resources/", "aabp.org", delay=3.0)

def fetch_aav_avian_urls():
    return _crawl_one_level("https://www.associationofavianvets.org/resources", "associationofavianvets.org", delay=3.0)

# B. Revistas OA adicionales
def fetch_europe_pmc_vet_urls():
    """Europe PMC API — artículos con MeSH veterinario."""
    base = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {"query": "veterinary[MeSH]", "format": "json", "pageSize": 1000, "resultType": "lite"}
    urls = []
    cursor = "*"
    for _ in range(5):  # max 5 páginas
        params["cursorMark"] = cursor
        try:
            r = requests.get(base, params=params, headers=HEADERS, timeout=30)
            data = r.json()
        except Exception:
            break
        for hit in data.get("resultList", {}).get("result", []):
            pmid = hit.get("pmid")
            if pmid:
                urls.append(f"https://europepmc.org/article/MED/{pmid}")
        cursor = data.get("nextCursorMark", "")
        if not cursor or cursor == params["cursorMark"]:
            break
        time.sleep(1.0)
    return urls

def fetch_veterinary_world_urls():
    return _fetch_sitemap_index_urls("https://www.veterinaryworld.org/sitemap-index.xml", delay=1.0)

def fetch_veterinary_evidence_urls():
    return _crawl_one_level("https://veterinaryevidence.org/index.php/ve", "veterinaryevidence.org", delay=2.0)

def fetch_open_vet_journal_urls():
    return _crawl_one_level("https://benthamopen.com/TOVETJ/", "benthamopen.com", delay=2.0)

def fetch_jstage_jvms_urls():
    return _fetch_sitemap_index_urls(
        "https://www.jstage.jst.go.jp/sitemap/jvms.xml",
        url_filter=lambda u: "/jvms/" in u,
        delay=1.0,
    )

def fetch_scielo_vet_urls():
    return _crawl_one_level("https://www.scielo.org/en/journals/?status=current&subject=veterinary-sciences", "scielo.org", delay=2.0)

def fetch_journal_shelter_med_urls():
    return _crawl_one_level("https://www.sheltervet.org/assets/docs/shelter-medicine-textbook-toc.html", "sheltervet.org", delay=3.0)

def fetch_bmc_vet_research_urls():
    return _fetch_sitemap_index_urls(
        "https://bmcvetres.biomedcentral.com/sitemap.xml",
        delay=1.0,
    )

def fetch_parasites_vectors_vet_urls():
    return _fetch_sitemap_index_urls(
        "https://parasitesandvectors.biomedcentral.com/sitemap.xml",
        url_filter=lambda u: "article" in u,
        delay=1.0,
    )

# C. Farmacología veterinaria
def fetch_vmd_uk_urls():
    return _crawl_one_level("https://www.vmd.defra.gov.uk/ProductInformationDatabase/", "vmd.defra.gov.uk", delay=3.0)

def fetch_apvma_urls():
    return _crawl_one_level("https://apvma.gov.au/node/106", "apvma.gov.au", delay=3.0)

def fetch_acvm_nz_urls():
    return _crawl_one_level("https://www.epa.govt.nz/database-search/acvm-register/", "epa.govt.nz", delay=3.0)

def fetch_health_canada_vet_urls():
    return _crawl_one_level("https://www.canada.ca/en/health-canada/services/drugs-health-products/veterinary-drugs.html", "canada.ca", delay=3.0)

def fetch_uk_varss_urls():
    return _crawl_one_level("https://www.vmd.defra.gov.uk/varss/", "vmd.defra.gov.uk", delay=3.0)

def fetch_drugcentral_vet_urls():
    return _crawl_one_level("https://drugcentral.org/pharmacology", "drugcentral.org", delay=2.0)

def fetch_chembl_vet_urls():
    return _crawl_one_level("https://www.ebi.ac.uk/chembl/g/#browse/compounds", "ebi.ac.uk", delay=2.0)

# D. Universidades adicionales
def fetch_rvc_urls():
    return _fetch_sitemap_index_urls("https://www.rvc.ac.uk/sitemap.xml", delay=1.0)

def fetch_edinburgh_vet_urls():
    return _crawl_one_level("https://www.ed.ac.uk/vet/research", "ed.ac.uk", delay=2.0)

def fetch_melbourne_vet_urls():
    return _crawl_one_level("https://fvas.unimelb.edu.au/research", "unimelb.edu.au", delay=2.0)

def fetch_utrecht_vet_urls():
    return _crawl_one_level("https://www.uu.nl/en/organisation/faculty-of-veterinary-medicine", "uu.nl", delay=2.0)

def fetch_guelph_ovc_urls():
    return _fetch_sitemap_index_urls("https://ovc.uoguelph.ca/sitemap.xml", delay=1.0)

def fetch_vetmeduni_vienna_urls():
    return _crawl_one_level("https://www.vetmeduni.ac.at/en/research/", "vetmeduni.ac.at", delay=2.0)

def fetch_liverpool_savsnet_urls():
    return _crawl_one_level("https://www.liverpool.ac.uk/savsnet/", "liverpool.ac.uk", delay=2.0)

def fetch_nottingham_cevm_urls():
    return _crawl_one_level("https://www.nottingham.ac.uk/vet/", "nottingham.ac.uk", delay=2.0)

def fetch_iowa_cfsph_urls():
    return _crawl_one_level("https://www.cfsph.iastate.edu/Factsheets/", "cfsph.iastate.edu", delay=2.0)

def fetch_minnesota_cahfs_urls():
    return _crawl_one_level("https://cahfs.umn.edu/", "cahfs.umn.edu", delay=2.0)

def fetch_tufts_vet_urls():
    return _crawl_one_level("https://vetnutrition.tufts.edu/", "tufts.edu", delay=2.0)

def fetch_glasgow_vet_urls():
    return _crawl_one_level("https://www.gla.ac.uk/schools/vet/research/", "gla.ac.uk", delay=2.0)

def fetch_bristol_vet_urls():
    return _crawl_one_level("https://www.bristol.ac.uk/vet-school/research/", "bristol.ac.uk", delay=2.0)

# E. Organizaciones regionales
def fetch_fve_urls():
    return _crawl_one_level("https://www.fve.org/publications/", "fve.org", delay=3.0)

def fetch_ava_australia_urls():
    return _crawl_one_level("https://www.ava.com.au/policy-advocacy/policies/", "ava.com.au", delay=3.0)

def fetch_cahss_canada_urls():
    return _crawl_one_level("https://cahss.org/publications/", "cahss.org", delay=3.0)

def fetch_cfia_animal_health_urls():
    return _crawl_one_level("https://inspection.canada.ca/animal-health/eng/1299009566369/1299009642126", "inspection.canada.ca", delay=3.0)

def fetch_uk_apha_urls():
    return _crawl_one_level("https://www.gov.uk/government/organisations/animal-and-plant-health-agency", "apha.gov.uk", delay=3.0)

def fetch_usda_aphis_vet_urls():
    return _crawl_one_level("https://www.aphis.usda.gov/aphis/ourfocus/animalhealth", "aphis.usda.gov", delay=3.0)

def fetch_usda_nahms_urls():
    return _crawl_one_level("https://www.nahms.usda.gov/publications/", "nahms.usda.gov", delay=3.0)

def fetch_ec_animal_health_urls():
    return _crawl_one_level("https://ec.europa.eu/info/departments/health-and-food-safety_en", "ec.europa.eu", delay=3.0)

def fetch_aha_australia_urls():
    return _crawl_one_level("https://www.animalhealthaustralia.com.au/publications/", "animalhealthaustralia.com.au", delay=3.0)

def fetch_agriculture_victoria_urls():
    return _crawl_one_level("https://agriculture.vic.gov.au/livestock-and-animals", "agriculture.vic.gov.au", delay=3.0)

def fetch_animal_health_ireland_urls():
    return _crawl_one_level("https://www.animalhealthireland.ie/programmes/", "animalhealthireland.ie", delay=3.0)

# F. Bases de datos
def fetch_vetsrev_urls():
    return _crawl_one_level("https://vetsrev.nottingham.ac.uk/", "vetsrev.nottingham.ac.uk", delay=3.0)

def fetch_omia_urls():
    return _crawl_one_level("https://omia.org/home/", "omia.org", delay=2.0)

def fetch_vetbact_urls():
    return _crawl_one_level("https://www.vetbact.org/vetbact/", "vetbact.org", delay=2.0)

def fetch_vetcompass_urls():
    return _crawl_one_level("https://www.vetcompass.org/publications/", "vetcompass.org", delay=2.0)

def fetch_vbo_breeds_urls():
    # BUGFIX 2026-07-26: la URL "vbo.com" era incorrecta y no correspondía a la
    # Vertebrate Breed Ontology real (alojada en GitHub, monarch-initiative).
    return _crawl_one_level(
        "https://github.com/monarch-initiative/vertebrate-breed-ontology",
        "github.com/monarch-initiative/vertebrate-breed-ontology", delay=2.0)

def fetch_gbads_urls():
    return _crawl_one_level("https://www.gbads.org/resources/", "gbads.org", delay=3.0)

def fetch_cidd_urls():
    return _crawl_one_level("https://www.cidd.org/", "cidd.org", delay=3.0)

def fetch_penngen_urls():
    return _crawl_one_level("https://www.vet.upenn.edu/research/centers-laboratories/penngen", "vet.upenn.edu", delay=2.0)

def fetch_animal_qtldb_urls():
    return _crawl_one_level("https://www.animalgenome.org/QTLdb/", "animalgenome.org", delay=2.0)

def fetch_phi_base_urls():
    return _crawl_one_level("https://www.phi-base.org/searchFacet.htm", "phi-base.org", delay=2.0)

# G. Nutrición y bienestar
def fetch_fediaf_urls():
    return _crawl_one_level("https://www.fediaf.org/self-regulation/nutrition-guidelines.html", "fediaf.org", delay=3.0)

def fetch_pet_nutrition_alliance_urls():
    return _crawl_one_level("https://petnutritionalliance.org/resources.php", "petnutritionalliance.org", delay=3.0)

def fetch_tufts_petfoodology_urls():
    return _fetch_sitemap_index_urls("https://vetnutrition.tufts.edu/post-sitemap.xml", delay=1.0)

def fetch_waltham_urls():
    return _crawl_one_level("https://www.waltham.com/resources/", "waltham.com", delay=3.0)

def fetch_rspca_knowledgebase_urls():
    return _crawl_one_level("https://kb.rspca.org.au/", "kb.rspca.org.au", delay=2.0)

def fetch_maddies_fund_urls():
    return _crawl_one_level("https://www.maddiesfund.org/resources.htm", "maddiesfund.org", delay=3.0)

def fetch_aspcapro_urls():
    return _crawl_one_level("https://www.aspcapro.org/resources", "aspcapro.org", delay=3.0)

def fetch_awin_welfare_urls():
    return _crawl_one_level("https://awionline.org/content/farm-animals", "awionline.org", delay=3.0)

def fetch_icam_urls():
    return _crawl_one_level("https://www.icam-coalition.org/resources/", "icam-coalition.org", delay=3.0)

def fetch_ufaw_urls():
    return _crawl_one_level("https://www.ufaw.org.uk/the-ufaw-journal/the-ufaw-journal", "ufaw.org.uk", delay=3.0)

def fetch_nal_animal_health_urls():
    return _crawl_one_level("https://www.nal.usda.gov/legacy/awic/animal-health-and-welfare", "nal.usda.gov", delay=3.0)

def fetch_humane_slaughter_urls():
    return _crawl_one_level("https://www.hsa.org.uk/publications/publications", "hsa.org.uk", delay=3.0)


def fetch_plos_vet_urls():
    """PLOS API — retorna URLs de artículos sobre veterinaria."""
    params = {
        "q": 'subject_area:"veterinary science"',
        "fl": "id",
        "rows": 1000,
        "wt": "json",
    }
    article_urls = []
    start = 0
    journal_map = {
        "pone": "plosone", "ppat": "plospathogens", "pbio": "plosbiology",
        "pmed": "plosmedicine", "pgen": "plosgenetics", "pcbi": "ploscompbiol",
        "pntd": "plosntds",
    }
    while True:
        params["start"] = start
        try:
            r = requests.get(PLOS_API_URL, params=params, headers=HEADERS, timeout=30)
            data = r.json()
        except Exception as e:
            print(f"  PLOS API error at start={start}: {e}", flush=True)
            break
        docs = data["response"]["docs"]
        if not docs:
            break
        for doc in docs:
            doi = doc.get("id", "")
            if not doi:
                continue
            parts = doi.split("/")
            journal_key = parts[-1].split(".")[1] if len(parts) > 1 else "pone"
            journal_slug = journal_map.get(journal_key, "plosone")
            article_urls.append(f"https://journals.plos.org/{journal_slug}/article?id={doi}")
        total = data["response"]["numFound"]
        start += 1000
        if start >= total:
            break
        time.sleep(2.0)
    return article_urls


# ── Fetchers nuevos (Inventario Complementario, 2026-07-26) ────────────────────

def fetch_beva_urls():
    return _crawl_one_level("https://www.beva.org.uk/Guidance", "beva.org.uk", delay=5.0)

def fetch_aaep_urls():
    return _crawl_one_level("https://aaep.org/resource-repository", "aaep.org", delay=5.0)

def _make_vet_metadata_record(source_url, title, notes):
    payload = {"title": title, "notes": notes}
    return f"{source_url}|VET_METADATA|{json.dumps(payload, ensure_ascii=False)}"

def fetch_bsava_metadata_urls():
    return [_make_vet_metadata_record(
        "https://www.bsavalibrary.com/", "BSAVA Library",
        "Biblioteca extensa con libros/proceedings mayormente para miembros o compra; "
        "el sitio reserva derechos de text and data mining e IA. Solo metadata/abstracts públicos.")]

def fetch_ivis_metadata_urls():
    return [_make_vet_metadata_record(
        "https://www.ivis.org/", "International Veterinary Information Service",
        "Gran biblioteca veterinaria; parte pública, parte con login y derechos propietarios. "
        "Solo metadata por defecto.")]

def fetch_veterinary_research_springer_urls():
    return _crawl_one_level(
        "https://link.springer.com/journal/13567/articles", "link.springer.com/journal/13567", delay=2.5)

def fetch_acta_vet_scandinavica_urls():
    return _crawl_one_level(
        "https://actavetscand.biomedcentral.com/articles", "actavetscand.biomedcentral.com", delay=2.5)

def fetch_animals_mdpi_urls():
    return _fetch_sitemap_index_urls(
        "https://www.mdpi.com/sitemap/sitemap-animals.xml",
        url_filter=lambda u: "/animals/" in u and "/article" in u, delay=1.0)

def fetch_vetsci_mdpi_urls():
    return _fetch_sitemap_index_urls(
        "https://www.mdpi.com/sitemap/sitemap-vetsci.xml",
        url_filter=lambda u: "/vetsci/" in u and "/article" in u, delay=1.0)

def fetch_irish_vet_journal_urls():
    return _crawl_one_level(
        "https://irishvetjournal.biomedcentral.com/articles", "irishvetjournal.biomedcentral.com", delay=2.5)

def fetch_canine_medicine_genetics_urls():
    return _crawl_one_level(
        "https://cgejournal.biomedcentral.com/articles", "cgejournal.biomedcentral.com", delay=2.5)

def fetch_jvetres_poland_urls():
    return _crawl_one_level("https://sciendo.com/journal/JVETRES", "sciendo.com", delay=3.0)

def fetch_bjvras_brazil_urls():
    return _crawl_one_level("https://www.revistas.usp.br/bjvras", "revistas.usp.br/bjvras", delay=2.5)

def fetch_jvs_korea_urls():
    return _crawl_one_level("https://vetsci.org/", "vetsci.org", delay=2.5)

# ── OpenAlex ────────────────────────────────────────────────────────────────
# Segments the corpus using OpenAlex's own Domain>Field>Subfield>Topic
# taxonomy instead of a hardcoded journal whitelist -- see
# docs/drive-source-map.md / health-platform-knowledge-infrastructure README
# for the full domain-mapping rationale. The Veterinary field (fields/34) is
# narrow (only "Small Animals" + "Equine" subfields) and excludes general/
# livestock/production-animal medicine, which OpenAlex instead classifies
# under Agricultural and Biological Sciences > Animal Science and Zoology
# (subfields/1103) -- both are queried and merged/deduped by work id since
# OpenAlex doesn't support OR across different filter keys in one call.
OPENALEX_API_KEY = os.environ.get("OPENALEX_API_KEY", "")
OPENALEX_MAX_RESULTS = 300  # per filter, per run; raise for a one-off catch-up


def _openalex_reconstruct_abstract(inverted_index):
    if not inverted_index:
        return ""
    positions = {}
    for word, idxs in inverted_index.items():
        for i in idxs:
            positions[i] = word
    return " ".join(positions[i] for i in sorted(positions))


def _openalex_fetch_works(filter_str, max_results=OPENALEX_MAX_RESULTS):
    """Cursor-paginated OpenAlex /works query, filtered by Domain/Field/Subfield/Topic id."""
    results = []
    cursor = "*"
    while cursor and len(results) < max_results:
        params = {
            "filter": filter_str, "per-page": 100, "cursor": cursor,
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
            results.append({
                "id": w.get("id", "").split("/")[-1],
                "doi": w.get("doi") or "",
                "title": w.get("title") or "",
                "abstract": _openalex_reconstruct_abstract(w.get("abstract_inverted_index")),
            })
            if len(results) >= max_results:
                break
        cursor = (data.get("meta") or {}).get("next_cursor")
    return results


def fetch_openalex_vet_urls():
    works = {}
    for filter_str in ("primary_topic.field.id:34", "primary_topic.subfield.id:1103"):
        for w in _openalex_fetch_works(filter_str):
            works.setdefault(w["id"], w)
    return [
        f"https://openalex.org/works/{w['id']}|OPENALEX_VET|"
        f"{json.dumps({'title': w['title'], 'doi': w['doi'], 'abstract': w['abstract']})}"
        for w in works.values()
    ]


HYBRID_VET_JOURNALS = [
    "Journal of Veterinary Internal Medicine", "Veterinary Medicine and Science",
    "Veterinary Record Open", "Journal of Feline Medicine and Surgery Open Reports",
    "Veterinary and Animal Science", "Preventive Veterinary Medicine",
    "Veterinary Parasitology: Regional Studies and Reports",
    "Transboundary and Emerging Diseases",
]

def _fetch_crossref_unpaywall_oa_vet(journal_name, marker, rows=40):
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

def fetch_hybrid_vet_journals_urls():
    urls = []
    for journal in HYBRID_VET_JOURNALS:
        urls += _fetch_crossref_unpaywall_oa_vet(journal, "HYBRID_VET_OA")
    return urls

def fetch_farad_urls():
    return _crawl_one_level("https://www.farad.org/publications/", "farad.org", delay=5.0)

def fetch_nval_japan_urls():
    return _crawl_one_level("https://www.maff.go.jp/nval/english/", "maff.go.jp/nval", delay=5.0)

def fetch_uk_vet_pharmacovigilance_urls():
    return _crawl_one_level(
        "https://www.gov.uk/government/collections/veterinary-pharmacovigilance",
        "gov.uk", delay=3.0)

def fetch_uk_vida_urls():
    return _crawl_one_level(
        "https://www.gov.uk/government/collections/animal-diseases-scanning-surveillance",
        "gov.uk", delay=3.0)

def fetch_faang_data_portal_urls():
    return _crawl_one_level("https://data.faang.org/", "data.faang.org", delay=3.0)

def fetch_assoc_shelter_vets_guidelines_urls():
    return [_make_vet_metadata_record(
        "https://www.sheltervet.org/assets/docs/shelter-standards-oct2011-wforward.pdf",
        "Guidelines for Standards of Care in Animal Shelters (2nd ed.)",
        "Documento único principal + anexos; referencia directa en vez de crawl.")]

def fetch_rspca_science_reports_urls():
    return _crawl_one_level("https://science.rspca.org.uk/", "rspca.org.uk", delay=5.0)

def fetch_shelter_animals_count_urls():
    return _crawl_one_level("https://www.shelteranimalscount.org/data/", "shelteranimalscount.org", delay=3.0)


# ── Carga de todas las URLs ────────────────────────────────────────────────────

def _load_source(name, sitemaps=None, fn=None):
    """Helper: carga URLs desde lista de sitemaps o función, imprime resultado."""
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
            print(f"  → {len(found)} URLs", flush=True)
            urls.extend(found)
        except Exception as e:
            print(f"  ERROR: {e}", flush=True)
    return urls


def get_all_urls():
    all_urls = []
    all_urls += _load_source("Merck Veterinary Manual",  sitemaps=MERCK_SITEMAPS)
    all_urls += _load_source("AAHA",                     sitemaps=AAHA_SITEMAPS)
    all_urls += _load_source("ACVS",                     sitemaps=ACVS_SITEMAPS)
    all_urls += _load_source("MSD Veterinary Manual",    sitemaps=MSD_SITEMAPS)
    all_urls += _load_source("ACVIM",                    sitemaps=ACVIM_SITEMAPS)
    all_urls += _load_source("WOAH (OIE)",               fn=fetch_woah_urls)
    all_urls += _load_source("WSAVA guidelines",         fn=fetch_wsava_guideline_urls)
    all_urls += _load_source("AAVMC",                    fn=fetch_aavmc_urls)
    all_urls += _load_source("NOAH Compendium",          fn=lambda: fetch_urls_from_sitemap(NOAH_SITEMAP))
    all_urls += _load_source("EMA Veterinary Medicines", fn=fetch_ema_vet_urls)  # lento por rate-limit, ~8 min
    all_urls += _load_source("FDA CVM (crawl)",          fn=fetch_fda_cvm_urls)
    all_urls += _load_source("ASPCA Toxicology",         fn=fetch_aspca_tox_urls)
    all_urls += _load_source("Pet Poison Helpline",      fn=fetch_pph_urls)
    all_urls += _load_source("Frontiers Vet Science",    fn=fetch_frontiers_vet_urls)
    all_urls += _load_source("PLOS ONE Veterinary",      fn=fetch_plos_vet_urls)
    all_urls += _load_source("Clinician's Brief",         fn=fetch_clinicians_brief_urls)
    all_urls += _load_source("Today's Vet Practice",      fn=fetch_tvp_urls)
    all_urls += _load_source("EFSA Animal Health",        fn=fetch_efsa_urls)
    all_urls += _load_source("FAO Animal Health",         fn=fetch_fao_animal_health_urls)
    all_urls += _load_source("Cornell Vet",               fn=fetch_cornell_vet_urls)
    all_urls += _load_source("UC Davis Vet",              fn=fetch_ucdavis_urls)
    all_urls += _load_source("Purdue Vet",                fn=fetch_purdue_vet_urls)
    all_urls += _load_source("Texas A&M Vet",             fn=fetch_tamu_vet_urls)
    all_urls += _load_source("Ohio State Vet",            fn=fetch_osu_vet_urls)
    all_urls += _load_source("Univ. of Sydney Vet",       fn=fetch_sydney_vet_urls)

    # ── batch 4: 70+ nuevas fuentes ──────────────────────────────────────────
    # A. Sociedades adicionales
    all_urls += _load_source("ECVIM Congress",             fn=fetch_ecvim_urls)
    all_urls += _load_source("ESCCAP",                     fn=fetch_esccap_urls)
    all_urls += _load_source("CAPC",                       fn=fetch_capc_urls)
    all_urls += _load_source("TroCCAP",                    fn=fetch_troccap_urls)
    all_urls += _load_source("ABCD Cats",                  fn=fetch_abcd_cats_urls)
    all_urls += _load_source("ISCAID",                     fn=fetch_iscaid_urls)
    all_urls += _load_source("VECCS/RECOVER",              fn=fetch_veccs_recover_urls)
    all_urls += _load_source("FECAVA",                     fn=fetch_fecava_urls)
    all_urls += _load_source("AAFP Feline",                fn=fetch_aafp_feline_urls)
    all_urls += _load_source("LAVECCS",                    fn=fetch_laveccs_urls)
    all_urls += _load_source("CVMA Canada",                fn=fetch_cvma_urls)
    all_urls += _load_source("NZVA",                       fn=fetch_nzva_urls)
    all_urls += _load_source("WAVMA",                      fn=fetch_wavma_urls)
    all_urls += _load_source("AASV",                       fn=fetch_aasv_urls)
    all_urls += _load_source("AABP",                       fn=fetch_aabp_urls)
    all_urls += _load_source("AAV Avian",                  fn=fetch_aav_avian_urls)
    # B. Revistas OA adicionales
    all_urls += _load_source("Europe PMC Vet",             fn=fetch_europe_pmc_vet_urls)
    all_urls += _load_source("Veterinary World",           fn=fetch_veterinary_world_urls)
    all_urls += _load_source("Veterinary Evidence",        fn=fetch_veterinary_evidence_urls)
    all_urls += _load_source("Open Vet Journal",           fn=fetch_open_vet_journal_urls)
    all_urls += _load_source("J-STAGE JVMS",               fn=fetch_jstage_jvms_urls)
    all_urls += _load_source("SciELO Vet",                 fn=fetch_scielo_vet_urls)
    all_urls += _load_source("Journal Shelter Medicine",   fn=fetch_journal_shelter_med_urls)
    all_urls += _load_source("BMC Vet Research",           fn=fetch_bmc_vet_research_urls)
    all_urls += _load_source("Parasites & Vectors Vet",    fn=fetch_parasites_vectors_vet_urls)
    # C. Farmacología veterinaria
    all_urls += _load_source("VMD UK",                     fn=fetch_vmd_uk_urls)
    all_urls += _load_source("APVMA Australia",            fn=fetch_apvma_urls)
    all_urls += _load_source("ACVM New Zealand",           fn=fetch_acvm_nz_urls)
    all_urls += _load_source("Health Canada Vet",          fn=fetch_health_canada_vet_urls)
    all_urls += _load_source("UK VARSS",                   fn=fetch_uk_varss_urls)
    all_urls += _load_source("DrugCentral Vet",            fn=fetch_drugcentral_vet_urls)
    all_urls += _load_source("ChEMBL Vet",                 fn=fetch_chembl_vet_urls)
    # D. Universidades adicionales
    all_urls += _load_source("RVC London",                 fn=fetch_rvc_urls)
    all_urls += _load_source("Edinburgh Vet",              fn=fetch_edinburgh_vet_urls)
    all_urls += _load_source("Melbourne Vet",              fn=fetch_melbourne_vet_urls)
    all_urls += _load_source("Utrecht Vet",                fn=fetch_utrecht_vet_urls)
    all_urls += _load_source("Guelph OVC",                 fn=fetch_guelph_ovc_urls)
    all_urls += _load_source("Vetmeduni Vienna",           fn=fetch_vetmeduni_vienna_urls)
    all_urls += _load_source("Liverpool SAVSNET",          fn=fetch_liverpool_savsnet_urls)
    all_urls += _load_source("Nottingham CEVM",            fn=fetch_nottingham_cevm_urls)
    all_urls += _load_source("Iowa CFSPH",                 fn=fetch_iowa_cfsph_urls)
    all_urls += _load_source("Minnesota CAHFS",            fn=fetch_minnesota_cahfs_urls)
    all_urls += _load_source("Tufts Vet",                  fn=fetch_tufts_vet_urls)
    all_urls += _load_source("Glasgow Vet",                fn=fetch_glasgow_vet_urls)
    all_urls += _load_source("Bristol Vet",                fn=fetch_bristol_vet_urls)
    # E. Organizaciones regionales
    all_urls += _load_source("FVE Europe",                 fn=fetch_fve_urls)
    all_urls += _load_source("AVA Australia",              fn=fetch_ava_australia_urls)
    all_urls += _load_source("CAHSS Canada",               fn=fetch_cahss_canada_urls)
    all_urls += _load_source("CFIA Animal Health",         fn=fetch_cfia_animal_health_urls)
    all_urls += _load_source("UK APHA",                    fn=fetch_uk_apha_urls)
    all_urls += _load_source("USDA APHIS Vet",             fn=fetch_usda_aphis_vet_urls)
    all_urls += _load_source("USDA NAHMS",                 fn=fetch_usda_nahms_urls)
    all_urls += _load_source("EC Animal Health",           fn=fetch_ec_animal_health_urls)
    all_urls += _load_source("Animal Health Australia",    fn=fetch_aha_australia_urls)
    all_urls += _load_source("Agriculture Victoria",       fn=fetch_agriculture_victoria_urls)
    all_urls += _load_source("Animal Health Ireland",      fn=fetch_animal_health_ireland_urls)
    # F. Bases de datos
    all_urls += _load_source("VetSRev",                    fn=fetch_vetsrev_urls)
    all_urls += _load_source("OMIA",                       fn=fetch_omia_urls)
    all_urls += _load_source("VetBact",                    fn=fetch_vetbact_urls)
    all_urls += _load_source("VetCompass",                 fn=fetch_vetcompass_urls)
    all_urls += _load_source("GBADs",                      fn=fetch_gbads_urls)
    all_urls += _load_source("CIDD",                       fn=fetch_cidd_urls)
    all_urls += _load_source("PennGen",                    fn=fetch_penngen_urls)
    all_urls += _load_source("Animal QTLdb",               fn=fetch_animal_qtldb_urls)
    all_urls += _load_source("PHI-base",                   fn=fetch_phi_base_urls)
    # G. Nutrición y bienestar
    all_urls += _load_source("FEDIAF",                     fn=fetch_fediaf_urls)
    all_urls += _load_source("Pet Nutrition Alliance",     fn=fetch_pet_nutrition_alliance_urls)
    all_urls += _load_source("Tufts Petfoodology",         fn=fetch_tufts_petfoodology_urls)
    all_urls += _load_source("Waltham",                    fn=fetch_waltham_urls)
    all_urls += _load_source("RSPCA Knowledgebase",        fn=fetch_rspca_knowledgebase_urls)
    all_urls += _load_source("Maddie's Fund",              fn=fetch_maddies_fund_urls)
    all_urls += _load_source("ASPCApro",                   fn=fetch_aspcapro_urls)
    all_urls += _load_source("AWIN Welfare",               fn=fetch_awin_welfare_urls)
    all_urls += _load_source("ICAM Coalition",             fn=fetch_icam_urls)
    all_urls += _load_source("UFAW",                       fn=fetch_ufaw_urls)
    all_urls += _load_source("NAL Animal Health",          fn=fetch_nal_animal_health_urls)
    all_urls += _load_source("Humane Slaughter Assoc.",    fn=fetch_humane_slaughter_urls)

    # ── Nuevas (Inventario Complementario 2026-07-26) ───────────────────────────
    # A.2 — condicionales
    all_urls += _load_source("BEVA",                       fn=fetch_beva_urls)
    all_urls += _load_source("AAEP",                       fn=fetch_aaep_urls)
    all_urls += _load_source("BSAVA (metadata)",           fn=fetch_bsava_metadata_urls)
    all_urls += _load_source("IVIS (metadata)",            fn=fetch_ivis_metadata_urls)
    # B.2 — revistas OA nuevas
    all_urls += _load_source("Veterinary Research (Springer)", fn=fetch_veterinary_research_springer_urls)
    all_urls += _load_source("Acta Veterinaria Scandinavica", fn=fetch_acta_vet_scandinavica_urls)
    all_urls += _load_source("Animals (MDPI)",             fn=fetch_animals_mdpi_urls)
    all_urls += _load_source("Veterinary Sciences (MDPI)", fn=fetch_vetsci_mdpi_urls)
    all_urls += _load_source("Irish Veterinary Journal",   fn=fetch_irish_vet_journal_urls)
    all_urls += _load_source("Canine Medicine and Genetics", fn=fetch_canine_medicine_genetics_urls)
    all_urls += _load_source("J Veterinary Research Poland", fn=fetch_jvetres_poland_urls)
    all_urls += _load_source("Brazilian J Vet Research (USP)", fn=fetch_bjvras_brazil_urls)
    all_urls += _load_source("J Veterinary Science (Korea)", fn=fetch_jvs_korea_urls)
    all_urls += _load_source("Revistas híbridas veterinaria (Crossref/Unpaywall)", fn=fetch_hybrid_vet_journals_urls)
    all_urls += _load_source("OpenAlex Veterinaria (Field 34 + Subfield 1103)", fn=fetch_openalex_vet_urls)
    # C — farmacología adicional
    all_urls += _load_source("FARAD",                      fn=fetch_farad_urls)
    all_urls += _load_source("National Vet Assay Lab Japón", fn=fetch_nval_japan_urls)
    all_urls += _load_source("UK Vet Pharmacovigilance",   fn=fetch_uk_vet_pharmacovigilance_urls)
    all_urls += _load_source("UK VIDA Surveillance",       fn=fetch_uk_vida_urls)
    # F — genómica adicional
    all_urls += _load_source("FAANG Data Portal",          fn=fetch_faang_data_portal_urls)
    # G — bienestar/refugios adicional
    all_urls += _load_source("Assoc. Shelter Vets Guidelines", fn=fetch_assoc_shelter_vets_guidelines_urls)
    all_urls += _load_source("RSPCA Science Reports",      fn=fetch_rspca_science_reports_urls)
    all_urls += _load_source("Shelter Animals Count",      fn=fetch_shelter_animals_count_urls)

    print(f"\nTotal URLs objetivo: {len(all_urls)}", flush=True)
    return all_urls


# ── Scraping de páginas HTML ───────────────────────────────────────────────────

def scrape_page(url):
    if "|HYBRID_VET_OA|" in url or "|VET_METADATA|" in url or "|OPENALEX_VET|" in url:
        real_url, marker, payload_str = url.split("|", 2)
        try:
            payload = json.loads(payload_str)
        except Exception:
            payload = {}
        title = payload.get("title") or real_url.split("/")[-1][:80]
        lines = [title, "=" * len(title), "", f"URL: {real_url}"]
        for k, v in payload.items():
            if k != "title":
                lines.append(f"{k}: {v}")
        return {"title": title, "full_text": "\n".join(lines)}

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

    return {"title": title, "full_text": f"{title}\n{'=' * len(title)}\n\nURL: {url}\n\n{summary}\n\n{body}".strip()}


def url_to_filename(url):
    if "merckvetmanual.com" in url:  prefix = "merck"
    elif "msdvetmanual.com" in url:  prefix = "msd"
    elif "woah.org"          in url:  prefix = "woah"
    elif "wsava.org"         in url:  prefix = "wsava"
    elif "acvs.org"          in url:  prefix = "acvs"
    elif "acvim.org"         in url:  prefix = "acvim"
    elif "aavmc.org"         in url:  prefix = "aavmc"
    elif "noahcompendium"    in url:  prefix = "noah"
    elif "ema.europa.eu"     in url:  prefix = "ema"
    elif "fda.gov"           in url:  prefix = "fda"
    elif "aspca.org"         in url:  prefix = "aspca"
    elif "petpoisonhelpline" in url:  prefix = "pph"
    elif "frontiersin.org"   in url:  prefix = "frontiers"
    elif "plos.org"          in url:  prefix = "plos"
    elif "cliniciansbrief"   in url:  prefix = "cb"
    elif "todaysveterinary"  in url:  prefix = "tvp"
    elif "efsa.europa.eu"    in url:  prefix = "efsa"
    elif "fao.org"           in url:  prefix = "fao"
    elif "vet.cornell.edu"   in url:  prefix = "cornell"
    elif "vetmed.ucdavis"    in url:  prefix = "ucdavis"
    elif "vet.purdue.edu"    in url:  prefix = "purdue"
    elif "vetmed.tamu.edu"   in url:  prefix = "tamu"
    elif "vet.osu.edu"       in url:  prefix = "osu"
    elif "sydney.edu.au"     in url:  prefix = "sydney"
    elif "aaha.org"          in url:  prefix = "aaha"
    # batch 4
    elif "ecvim-ca.org"      in url:  prefix = "ecvim"
    elif "esccap.org"        in url:  prefix = "esccap"
    elif "capcvet.org"       in url:  prefix = "capc"
    elif "troccap.com"       in url:  prefix = "troccap"
    elif "abcdcatsvets.org"  in url:  prefix = "abcd"
    elif "iscaid.org"        in url:  prefix = "iscaid"
    elif "veccs.org"         in url or "recover-cpr.org" in url: prefix = "veccs"
    elif "fecava.org"        in url:  prefix = "fecava"
    elif "catvets.com"       in url:  prefix = "aafp_feline"
    elif "laveccs.org"       in url:  prefix = "laveccs"
    elif "canadianveterinarians.net" in url: prefix = "cvma"
    elif "nzva.org.nz"       in url:  prefix = "nzva"
    elif "wavma.org"         in url:  prefix = "wavma"
    elif "aasv.org"          in url:  prefix = "aasv"
    elif "aabp.org"          in url:  prefix = "aabp"
    elif "associationofavianvets.org" in url: prefix = "aav"
    elif "europepmc.org"     in url:  prefix = "europepmc_vet"
    elif "veterinaryworld.org" in url: prefix = "vetworld"
    elif "veterinaryevidence.org" in url: prefix = "vetevidence"
    elif "benthamopen.com"   in url:  prefix = "openvetj"
    elif "jstage.jst.go.jp"  in url:  prefix = "jvms"
    elif "scielo"            in url:  prefix = "scielo_vet"
    elif "sheltervet.org"    in url:  prefix = "sheltermed"
    elif "bmcvetres"         in url:  prefix = "bmcvet"
    elif "parasitesandvectors" in url: prefix = "parasitesvectors"
    elif "vmd.defra.gov.uk"  in url:  prefix = "vmd_uk"
    elif "apvma.gov.au"      in url:  prefix = "apvma"
    elif "epa.govt.nz"       in url:  prefix = "acvm_nz"
    elif "health-canada"     in url and "vet" in url: prefix = "healthcanada_vet"
    elif "drugcentral.org"   in url:  prefix = "drugcentral"
    elif "ebi.ac.uk/chembl"  in url:  prefix = "chembl"
    elif "rvc.ac.uk"         in url:  prefix = "rvc"
    elif "ed.ac.uk"          in url:  prefix = "edinburgh_vet"
    elif "unimelb.edu.au"    in url:  prefix = "melbourne_vet"
    elif "uu.nl"             in url:  prefix = "utrecht_vet"
    elif "uoguelph.ca"       in url:  prefix = "guelph_ovc"
    elif "vetmeduni.ac.at"   in url:  prefix = "vetmeduni"
    elif "liverpool.ac.uk"   in url:  prefix = "liverpool_vet"
    elif "nottingham.ac.uk"  in url:  prefix = "nottingham_vet"
    elif "cfsph.iastate.edu" in url:  prefix = "iowa_cfsph"
    elif "cahfs.umn.edu"     in url:  prefix = "minnesota_cahfs"
    elif "vetnutrition.tufts.edu" in url: prefix = "tufts_vet"
    elif "gla.ac.uk"         in url:  prefix = "glasgow_vet"
    elif "bristol.ac.uk"     in url:  prefix = "bristol_vet"
    elif "fve.org"           in url:  prefix = "fve"
    elif "ava.com.au"        in url:  prefix = "ava_au"
    elif "cahss.org"         in url:  prefix = "cahss"
    elif "inspection.canada.ca" in url: prefix = "cfia"
    elif "apha.gov.uk"       in url or "gov.uk/government/organisations/animal" in url: prefix = "uk_apha"
    elif "aphis.usda.gov"    in url:  prefix = "usda_aphis"
    elif "nahms.usda.gov"    in url:  prefix = "usda_nahms"
    elif "animalhealthaustralia.com.au" in url: prefix = "aha_au"
    elif "agriculture.vic.gov.au" in url: prefix = "agvic"
    elif "animalhealthireland.ie" in url: prefix = "ahi"
    elif "vetsrev.nottingham.ac.uk" in url: prefix = "vetsrev"
    elif "omia.org"          in url:  prefix = "omia"
    elif "vetbact.org"       in url:  prefix = "vetbact"
    elif "vetcompass.org"    in url:  prefix = "vetcompass"
    elif "animalgenome.org"  in url:  prefix = "animal_qtldb"
    elif "phi-base.org"      in url:  prefix = "phi_base"
    elif "gbads.org"         in url:  prefix = "gbads"
    elif "cidd.org"          in url:  prefix = "cidd"
    elif "vet.upenn.edu"     in url:  prefix = "penngen"
    elif "fediaf.org"        in url:  prefix = "fediaf"
    elif "petnutritionalliance.org" in url: prefix = "pna"
    elif "waltham.com"       in url:  prefix = "waltham"
    elif "kb.rspca.org.au"   in url:  prefix = "rspca"
    elif "maddiesfund.org"   in url:  prefix = "maddies"
    elif "aspcapro.org"      in url:  prefix = "aspcapro"
    elif "awionline.org"     in url:  prefix = "awin"
    elif "icam-coalition.org" in url: prefix = "icam"
    elif "ufaw.org.uk"       in url:  prefix = "ufaw"
    elif "nal.usda.gov"      in url:  prefix = "nal_animal"
    elif "hsa.org.uk"        in url:  prefix = "humane_slaughter"
    elif "|HYBRID_VET_OA|"   in url:  prefix = "hybrid_vet_oa"
    elif "|OPENALEX_VET|"    in url:  prefix = "openalex_vet"
    elif "|VET_METADATA|"    in url:  prefix = "vet_metadata"
    elif "beva.org.uk"       in url:  prefix = "beva"
    elif "aaep.org"          in url:  prefix = "aaep"
    elif "bsavalibrary.com"  in url:  prefix = "bsava"
    elif "ivis.org"          in url:  prefix = "ivis"
    elif "link.springer.com/journal/13567" in url: prefix = "vet_research"
    elif "actavetscand.biomedcentral.com" in url: prefix = "acta_vet_scand"
    elif "mdpi.com" in url and "/animals/" in url: prefix = "animals_mdpi"
    elif "mdpi.com" in url and "/vetsci/" in url: prefix = "vetsci_mdpi"
    elif "irishvetjournal.biomedcentral.com" in url: prefix = "irish_vet_j"
    elif "cgejournal.biomedcentral.com" in url: prefix = "canine_med_genetics"
    elif "sciendo.com"       in url:  prefix = "jvetres_poland"
    elif "revistas.usp.br/bjvras" in url: prefix = "bjvras"
    elif "vetsci.org"        in url:  prefix = "jvs_korea"
    elif "farad.org"         in url:  prefix = "farad"
    elif "maff.go.jp/nval"   in url:  prefix = "nval_japan"
    elif "gov.uk" in url and "pharmacovigilance" in url: prefix = "uk_vet_pharmacovigilance"
    elif "gov.uk" in url and "scanning-surveillance" in url: prefix = "uk_vida"
    elif "data.faang.org"    in url:  prefix = "faang"
    elif "shelteranimalscount.org" in url: prefix = "shelter_animals_count"
    elif "rspca.org.uk"      in url:  prefix = "rspca_science"
    elif "vertebrate-breed-ontology" in url: prefix = "vbo_breeds"
    else:                             prefix = "vet"
    path = re.sub(r"[?=&]", "_", url.split("//", 1)[-1]).replace("/", "__").strip("__")
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
            eta_min = ((len(remaining) - i) / rate / 60) if rate > 0 else 0
            done_total = len(done_set) + i
            pct = done_total / total * 100
            print(
                f"[{done_total}/{total} — {pct:.1f}%] "
                f"{rate:.2f} pág/s | ETA: {eta_min:.0f} min",
                flush=True,
            )

        # Delay mayor para sitios con crawl-delay declarado (ASPCA, PPH, PLOS)
        if any(d in url for d in ("aspca.org", "petpoisonhelpline", "plos.org")):
            time.sleep(random.uniform(10.0, 15.0))
        else:
            time.sleep(random.uniform(2.0, 4.0))

    save_progress(progress)
    print(f"\n✓ Terminado.")
    print(f"  Exitosos : {len(progress['done'])}")
    print(f"  Fallidos : {len(progress['failed'])}")
    print(f"  Carpeta  : Google Drive → Proyecto_IA_Veterinaria/")
