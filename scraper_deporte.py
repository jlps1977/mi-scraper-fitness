#!/usr/bin/env python3
"""
Scraper de Ciencias del Deporte — corpus para IA de entrenadores deportivos.
Inventario Maestro 2026-07-25. 200+ fuentes en 14 secciones:
  1) Antidopaje y regulación (WADA, USADA, UKAD, ITA, CCES, NADA, AFLD, CELAD, JADA, SAIDS, ABCD)
  2) Fisiología del ejercicio (ACSM, ECSS, CASES, Sports Med Open, JHK, IJES, Biology of Sport, JSSM)
  3) Fuerza y acondicionamiento (NSCA, ALTIS, SimpliFaster, IJSC, Trainology, Stronger By Science, EliteFTS)
  4) Nutrición deportiva (JISSN, ISSN Stands, AIS, GSSI, IOC, Sports Dietitians AU, Athlete Triad)
  5) Psicología del deporte (AASP, ISSP, FEPSAC, Frontiers, NCAA Mental Health, AIS Mental Health)
  6) Biomecánica y análisis del movimiento (ISBS, ISB, OpenSim, OpenCap, SimTK, Kinovea, Vicon, Qualisys)
  7) Medicina deportiva (BJSM, AMSSM, NATA, JAT, Aspetar, OJSM, CDC HEADS UP, IFSPT, Physiopedia)
  8) Entrenamiento táctico y análisis de juego (FIFA TC, UEFA Reports, StatsBomb, Metrica, SkillCorner,
     Friends of Tracking, Kloppy, socceraction, MIT Sloan, FIVB Coaches)
  9) Federaciones internacionales 40+ (FIFA/IFAB, FIBA, FIVB, World Athletics, World Aquatics, UCI,
     ITF, World Rugby, IHF, BWF, Taekwondo, IJF, FIS, World Rowing, FIG, World Boxing, IMMAF,
     WBSC, IGF, R&A, World Triathlon, FIE, ISSF, IWF, UWW, FIH, IIHF, World Lacrosse, ICC,
     World Archery, ITTF, ICF, World Sailing, IFSC, ISA, UIPM, World Skate)
  10) Deportes paralímpicos (IPC, World Para Athletics/Swimming/Powerlifting, Boccia,
      Wheelchair Rugby/Basketball, IBSA, Virtus, WorldAbilitySport, ParaVolley)
  11) Desarrollo de entrenadores (ICCE, UEFA Conv, CONMEBOL, England Football, UK Coaching,
      Coaching CA, Sport NZ, Olympic Solidarity, FIBA WABC, World Athletics Coaching)
  12) Tecnología deportiva (Catapult, Polar, Garmin, Firstbeat, VALD, STATSports, KINEXON,
      Kubios, HRV4Training, Hawkin Dynamics, Delsys, Noraxon, COSMED, NeuroKit2, GoldenCheetah)
  13) Institutos nacionales (AIS, UKSI, UK Sport, INSEP, INEFC, Aspire, Aspetar, COPSIN,
      CSI Pacific, HPSNZ, USOPC, JISS, Singapore, KISS, Sport Ireland, Olympiatoppen, BISp, SFISM)
  14) Bases de datos OA (PubMed, PMC, Europe PMC, OpenAlex, Crossref, Unpaywall, DOAJ, CORE,
      OpenAIRE, Semantic Scholar, DataCite, Zenodo, OSF, SportRxiv, Figshare, Harvard Dataverse,
      arXiv, LA84, Olympic World Library, NCAA Research, SIRC)

Uso: .venv/bin/python scraper_deporte.py
Reanuda desde progress_deporte.json (crea si no existe).
"""

import os, re, json, time
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from google.oauth2.credentials import Credentials

# ── Drive — IDs de carpetas ────────────────────────────────────────────────────
DRIVE_DEPORTE_ROOT_ID             = "1nInRjNCwMhbwTa39QYSfxJvu7Q-SIAZv"

# A. Organismos internacionales y antidopaje
DRIVE_IOC_OLYMPICS_ID             = "1999K4g1QfgLhYkudkrMp-kDx_E8cm1n6"
DRIVE_WADA_ANTIDOPING_ID          = "19q2P1KHuaxTHEccc74aqtt3Gr6ptKYw4"
DRIVE_USADA_ID                    = "15wBmpFPnjsHtwzWYGhXPXAm98LJJDc-G"
DRIVE_UKAD_ID                     = "1guV_mxYV03ia1ybi4Nq19xFNkK-c5jmb"
DRIVE_GLOBAL_DRO_ID               = "1GVZ4QbqVD4odbrp60ptUPWXZ5Faon2Cb"

# B. Federaciones internacionales
DRIVE_WORLD_ATHLETICS_ID          = "1yRDskY5BwOZ9lbMXmqoWzkSqpOfMEDD1"
DRIVE_FIFA_FOOTBALL_ID            = "1AAPQX-MlzN6T_cOsICe1k2thskWmJMj4"
DRIVE_FIBA_BASKETBALL_ID          = "1bshu6FxnDowt586aJxssB8S4vwFEBVA7"
DRIVE_FIVB_VOLLEYBALL_ID          = "1ipjEZNrIMWqZUL5KiE1iPjhAt8e3cm6A"
DRIVE_WORLD_AQUATICS_ID           = "19TxwjvK3oo5EmlfBKEZeigRWx1GuLtWI"
DRIVE_UCI_CYCLING_ID              = "1erjwHyJN-kXAI7ivuh1hTYdihPeyBOEg"
DRIVE_ITF_TENNIS_ID               = "1UDTWISFrOO6pdgRX_cIkieX5jmzfYQxp"
DRIVE_WORLD_RUGBY_ID              = "137jlVDXwg9jsI2V8XlYeOeraF32eCYdV"
DRIVE_IHF_HANDBALL_ID             = "1QvflIx1Le3uDaN4y4qiJlcLPligm1qh-"
DRIVE_BWF_BADMINTON_ID            = "1eNP0nux3y6CxhYceSJhsQiYsdyiGPdQr"
DRIVE_WORLD_TAEKWONDO_ID          = "1p0dIICMdrK6fzbaj0zT8sNuk_mlqs-1Y"
DRIVE_IJF_JUDO_ID                 = "1hWEt6MMFS_XwB-xEYH8qOTgMk2njIh17"
DRIVE_ISU_SKATING_ID              = "15S_DNOf__0E5LySE2QeKg5vAhV3PxLd9"
DRIVE_FIS_SKIING_ID               = "10btfXeX-p7dcKX-1zMkRFDrAWYPeJVI9"
DRIVE_WORLD_ROWING_ID             = "1sI8uhfbYDgPWrPXrUsrQ6uIgtzKeQmLW"
DRIVE_WORLD_GYMNASTICS_ID         = "1iY4kq9z66ukgqIBgBjsR1lSJi8jyys0q"
DRIVE_WORLD_BOXING_ID             = "1EGQzGnUxnVbu2tmBDykHFgmBsrVLqyrC"
DRIVE_UFC_MMA_RESOURCES_ID        = "1Bd-ysMvjktvrV17JqfN45dUSeGssnygx"

# C. Ciencias del deporte
DRIVE_ACSM_ID                     = "18F7TpsMfUY2D6YZwac-LPrOAMDsh5-y1"
DRIVE_NSCA_ID                     = "1FFeBRLWP1FD_jJZnLirkkVAUuxmi8TYF"
DRIVE_ECSS_ID                     = "1atUEtwV3liyw7-oTS-19g1YDO0Qj0jHw"
DRIVE_BASES_UK_ID                 = "1dkqPav--YidkE6SMhqv7coGhQVoDRDsN"
DRIVE_ASCA_AU_ID                  = "1-GiP_0Aht9uCQnxvY2YB-JLGLzBQEnnD"
DRIVE_UKSCA_ID                    = "1_kv5SiiUPIJfE-24QLAlebV-l3l9rLRo"
DRIVE_CONADE_MEXICO_ID            = "14g8Zkxtluy-gucmJpQagfoRxMCZ4JKUf"
DRIVE_SPORT_AUSTRALIA_CLEARINGHOUSE_ID = "1RRT_Ohw86HzbfHkyAewE66Lxfl13Bt_6"
DRIVE_UK_SPORT_ID                 = "1hxqgADr6l0-zigDLRX8k2J1Go482W64j"
DRIVE_USOPC_RESOURCES_ID          = "1WgW1ac4QCLl0iUM6xU4iqsPee9sDvMzm"

# D. Medicina deportiva
DRIVE_FIMS_ID                     = "1pUHcsOfeYy4RsGeDwcSzEopYL2FzoK25"
DRIVE_AMSSM_ID                    = "1MNQVel3D9TMfjOnLYPkaAhfZGYBTcWV6"
DRIVE_AOSSM_ID                    = "1jRcMw1HSq3fUoQ5nYYnMjbBEaUTmDte_"
DRIVE_ESSKA_ID                    = "1hmNNcCD-DaQv2I88p5yHKrLsqoTirziu"
DRIVE_BJSM_ID                     = "1X8db7M6uKQLfyER8c_TWrfLU_R_OlJXd"
DRIVE_SPORTS_HEALTH_JOURNAL_ID    = "1snvwxRluGjAnefcRM1KlV2bp25DA8MtA"
DRIVE_NATA_ATHLETIC_TRAINING_ID   = "15ekn6DwhXkPxGhfr8IC4biXmi5r7Tk8P"

# E. Nutrición deportiva
DRIVE_ISSN_NUTRITION_ID           = "1qRv3pDW6-a6DJkSVIpreiRhNIGyknsWR"
DRIVE_AIS_NUTRITION_ID            = "1EKsw69L6ZTEQ5QAFtQ0YGijCuW67GJ0S"
DRIVE_GSSI_GATORADE_ID            = "1mP4YtXIAdnut4weyP-duqmtocGdc8A_D"
DRIVE_SCAN_DIETITIANS_ID          = "1yJT2pP5B6BnTshUKB8tZDNF3UOwFUl9s"
DRIVE_IOC_NUTRITION_ID            = "1_bj4TJ-ubWxgLnjk6e50ak5PVpgvrwWT"

# F. Psicología del deporte
DRIVE_AASP_PSYCHOLOGY_ID          = "1EA-kWJEMxJYaVMc74PNshYK58TNB16G4"
DRIVE_ISSP_PSYCHOLOGY_ID          = "1ZzWGWputPfG4bO-JCmnOJA9ir8-29c7t"
DRIVE_FEPSAC_EUROPE_ID            = "1o9bM-2RLQCFKmxL5cPEGvqFhd1kZarhS"

# G. Fuerza, acondicionamiento y biomecánica
DRIVE_ISBS_BIOMECHANICS_ID        = "1tQ7d8nTJ6dzTup6lTuq7lxSlm5sX9u7g"
DRIVE_NSCA_STRENGTH_ID            = "1wOxG-JW_nZfETKrMFFTW2kvhFwE5gJJU"
DRIVE_VELOCITY_BASED_TRAINING_ID  = "1ls-foMxmMn0_5NursmVqc_ezJoyhP5mp"
DRIVE_CATAPULT_RESOURCES_ID       = "1DtdnqJN1Mbp5xBu6k4L-zyFv4Hvmp0O5"

# H. Revistas OA
DRIVE_JSSM_JOURNAL_ID             = "1ojhSAjU9jHvwMSdSqIBTahUUm2WC5Y3O"
DRIVE_SPORTS_MDPI_ID              = "15J2FpvGSIqVQO1hwnEjwdq5axmQ38N66"
DRIVE_FRONTIERS_SPORTS_ID         = "1LwY7FTPell4JQ7w8GXqjJbhe7dAuoHm9"
DRIVE_BMC_SPORTS_SCI_ID           = "1E3oI87qImzuX5T2DUNenNrY7oEIF2_29"
DRIVE_PEERJ_SPORTS_ID             = "1hmZb9OkH0V_Ymrbtf2wHggaDeGCtdLYY"
DRIVE_TRANSLATIONAL_SPORTS_MED_ID = "1p5XWyksDVV50CkEO3Cl-dNvMInWkWS2h"
DRIVE_INTL_J_SPORTS_PHYSIOL_ID    = "17YR0ywTDEzcux-8irSAhVciBXXPqoNwp"
DRIVE_JOURNAL_SPORT_SCIENCE_ID    = "1bJVVBpRDU2K5If3J19S9FO__YmU9Jb88"

# I. Institutos de élite
DRIVE_AIS_AUSTRALIA_ID            = "1QI6wpBlSH7XtVC-moYDOdJV_Bm_v3p6u"
DRIVE_INEF_SPAIN_ID               = "17sXNCD7mGAXpQjRCTq_sj0mw_8EeStMK"
DRIVE_ASPIRE_QATAR_ID             = "1w2H2wYysyEScVLtCGB-0dXiufUVxaEPi"
DRIVE_CANADIAN_SPORT_INSTITUTE_ID = "1Kc7W3EfgCyXWgAPoF0Gc0rRM3oRYcWs-"
DRIVE_SPORT_NEW_ZEALAND_ID        = "1QpNLkoMRDHrTL_ZPCeVnM5vJw5LphtbY"

# J. Bases de datos y recursos educativos (originales)
DRIVE_SIRC_CANADA_ID              = "1WRXUMyQyUDAtUeqijd4DY_QlVmKtDGju"
DRIVE_PUBMED_SPORTS_ID            = "1NOmRA3YFVAePvXFA120ZD6kedGYsKKj3"
DRIVE_COACH_EDUCATION_RESOURCES_ID = "1AMA3NQ1Wa9T8wrPLksByRe-LNQehE9QB"
DRIVE_STRENGTH_POWER_RESEARCH_ID  = "1OyDt367XpAvkq8lFJdCM_shinCnqTneZ"

# ── NUEVAS CARPETAS — Inventario Maestro 2026-07-25 ───────────────────────────
# Sección 1 — Antidopaje extendido
DRIVE_ITA_SPORT_ID                = "1bLN0axKebQQQ0mufAmrCGagyeAbJGO34"
DRIVE_INADO_ID                    = "12eKT-x_BuQh6D4vW6MPgaKHR85vO6noO"
DRIVE_CCES_CANADA_ID              = "1xNky3qny7zpDQXX-AYYAbUXKxdMNvh9J"
DRIVE_NADA_GERMANY_ID             = "1I4P-lnSmiPDK5HhLfYydnuVFGLbuH5JN"
DRIVE_AFLD_FRANCE_ID              = "1T-ie-ppjYJ0k7cqUEVAlcAzXepVhvudw"
DRIVE_CELAD_SPAIN_ID              = "1M1uKKtA4NgzxflqC1ZItymKRoF8riEUS"
DRIVE_JADA_JAPAN_ID               = "1Ixsu7R5d9C5p_dpESJ51REg0sDw-i9Oi"
DRIVE_SAIDS_AFRICA_ID             = "1Au7or7eE56ctjRqBMP6Grlu209s2hP-w"
DRIVE_ABCD_BRAZIL_ID              = "1WyiPnaOeQ2eP43xLMpzxzMrqCtTVEIDm"
DRIVE_WADA_RADOS_ID               = "10Q6MVafm2PLP4A6PdT4F5KJXg-5jVT21"
# Sección 2 — Fisiología
DRIVE_CASES_UK_ID                 = "1ytGR9IdhAGA28HnRHwOd3KiffwRIzBZn"
DRIVE_SPORTS_MED_OPEN_ID          = "1E-0WK8P-tUwpKUCghcUIUJpMvKMiVoKV"
DRIVE_JHK_JOURNAL_ID              = "1J0As1dpSg5AALZjv_w5urwC6jWrXNds0"
DRIVE_IJES_JOURNAL_ID             = "1Gz9q011xRmqeMlmEcZy-jhJZwuuJOLuw"
DRIVE_BIOLOGY_OF_SPORT_ID         = "1cXhqkW0Q0Me4mCV27CyZnDgU92IiBJmq"
# Sección 3 — S&C aplicado
DRIVE_ALTIS_SPRINT_ID             = "1-gZBNWjLqCfLT2EyD45Mv36HosyZpoeb"
DRIVE_SIMPLIFASTER_ID             = "1b7mTFBRSUiTO__nQ9FG8JpdEQcTR-eF3"
DRIVE_IJSC_JOURNAL_ID             = "1NmCQnEyNHQV9xYuN0t0_XOu6T8vo6j3V"
DRIVE_SPORT_PERF_REPORTS_ID       = "1hfskwnxZ1wjUZ-WU4r5uEfqSOdgbdxet"
DRIVE_JOURNAL_TRAINOLOGY_ID       = "17QGnGiGBkBV0x9G9sKVkI_wDQk7QiOTl"
DRIVE_STRONGER_BY_SCIENCE_ID      = "1z3GbPfA5OFyjDNFeSX7MrzblmyPBj9KJ"
DRIVE_SC_SOCIETY_ID               = "18MCqDY7yaa9BU5Udh7seIko8OmnMxkrZ"
DRIVE_ELITEFTS_EDU_ID             = "1plRlKRC7IebSTqOejuMasg5DgHu6nAnU"
# Sección 4 — Nutrición extendida
DRIVE_SPORTS_DIETITIANS_AU_ID     = "1EVDjXDls1V3CHZWy8SEi-b7rGBHr2oHJ"
DRIVE_ATHLETE_TRIAD_COALITION_ID  = "1LSeaIpmXJSfjBanjLfLh_Ynj610UGTGF"
DRIVE_AIS_NUTRITION_RECIPES_ID    = "1gEqCH8CjDKXwdQDdfNWDlVCUNZBYce2R"
# Sección 5 — Psicología
DRIVE_FRONTIERS_SPORT_PSYCH_ID    = "1DeEqr8yWDn4hRt8YdU0n6gRGhXnlgPa9"
DRIVE_NCAA_MENTAL_HEALTH_ID       = "1t_iLt9Nb3E0oRpwkqne4c0msviXb1NVG"
DRIVE_AIS_MENTAL_HEALTH_ID        = "1pkfrhn7GWRXFCPiCh0lGNYhm2ViQFsSn"
# Sección 6 — Biomecánica
DRIVE_ISB_WEB_ID                  = "1HTLMRbqf0bms2sN8hBHX51NAJyfH5zOK"
DRIVE_OPENSIM_ID                  = "1IgredYeK7I-0YkHueJbcfETDzoEDdb1z"
DRIVE_OPENCAP_ID                  = "1oHUljdsfuiQXlNNn-Jt9IzdcdoRTSVhA"
DRIVE_SIMTK_ID                    = "1DRrUORSyxRmydefen72iSCpUKvln1xLo"
DRIVE_KINOVEA_ID                  = "1xPenKwzGDgd9C3JYTexv_KsjJfEwM8Co"
DRIVE_VISUAL3D_WIKI_ID            = "1I1v2r6S23wiTSHxIPlhmypR8YRjXHXJv"
DRIVE_VICON_RESOURCES_ID          = "1h2J_bLN_CIQNAgFOhwRqHDyhlhwttvyT"
DRIVE_QUALISYS_RESOURCES_ID       = "1FWR3imhlzv20VYRqkzpi2wWqDseBpTkW"
# Sección 7 — Medicina deportiva extendida
DRIVE_JAT_JOURNAL_ID              = "1MUPrWp6yr8raV36uyo9FLZyi0jbb-Xh2"
DRIVE_ASPETAR_JOURNAL_ID          = "1aF1nrNSkNgGFoMTbUK3f3zGUkDqU9gyv"
DRIVE_OJSM_JOURNAL_ID             = "1PfYwVzfDG-mU7iSE_s3LxHIZsBZZtcuu"
DRIVE_CDC_HEADS_UP_ID             = "1JXDVGbQ4VpIjJ-rVWcf00Wh-LiqHXKYI"
DRIVE_IFSPT_ID                    = "1s7qL6NE_GBtRsF6nZZlQLQc315kCEFdx"
DRIVE_PHYSIOPEDIA_SPORTS_ID       = "15WGY1nSn4Oj5Uz9qLNaIpI7NFoLTWvxS"
# Sección 8 — Táctica y análisis de juego
DRIVE_FIFA_TRAINING_CENTRE_ID     = "1hPPqDz4sVusOZvbN4GkoCc01kEYOKW1q"
DRIVE_UEFA_TECHNICAL_REPORTS_ID   = "1ZANpaTeX5KgPf6a5z_SaSSC6Dj1D5iUY"
DRIVE_STATSBOMB_OPENDATA_ID       = "1hzUDvpB8ZgzIl7mlHE3wcG1uPiX4w2zD"
DRIVE_METRICA_SPORTS_ID           = "1A039mhq-Y5_r-ircw5EfHQHVFXo5Dhmi"
DRIVE_SKILLCORNER_OPENDATA_ID     = "1kXoUuVfCdfyLtkKXrFVbxmIj8QaXa7BN"
DRIVE_FRIENDS_OF_TRACKING_ID      = "1iMB4BHLxIutuQComJV_zhBwWGgFzA9tE"
DRIVE_KLOPPY_LIBRARY_ID           = "19aX93-kbmQWU3XnHfKtbmhz5LJ5JFmvw"
DRIVE_SOCCERACTION_LIB_ID         = "1YNEVSrtDtstnGDVogzXENUuJUqlRqRs3"
DRIVE_MIT_SLOAN_ANALYTICS_ID      = "1nR6S0XfSE3RSHTF4pTnrA-8cW0xA9Q6K"
DRIVE_FIVB_COACHES_RESOURCES_ID   = "1e-udwZD84J9oc8rjOuH4xX4okTiRxchj"
# Sección 9 — Federaciones extendidas
DRIVE_IFAB_LAWS_ID                = "1lmcNjQumOGS7iGY39Hx5MWkNrnpYZ0J8"
DRIVE_WORLD_SKATE_ID              = "1ANsMeEgsoINimhgYzkhKwFljJDA_ySeM"
DRIVE_IMMAF_ID                    = "1MMPXNRAC70mZLZitjyLtPWX7YkSqOEJ7"
DRIVE_WBSC_BASEBALL_ID            = "1tc6fMd-JfgIXj7ZmiPPVlWjetK1jKQ16"
DRIVE_IGF_GOLF_ID                 = "1KgBhnRDfuKPQwxx7Qp91U0pFFsdiggsm"
DRIVE_RANDA_GOLF_ID               = "1rxtOk8kVaKGJYmIS4wCnM2tk2Lj4tw6h"
DRIVE_WORLD_TRIATHLON_ID          = "1lbEOdsZaPV3crhKyMRbUzBbHwzTs8W6a"
DRIVE_FIE_FENCING_ID              = "1kjhKS6LtuW2ytpAXOw6kp1J0AzmXuqp6"
DRIVE_ISSF_SHOOTING_ID            = "18GKv4jJ44MGPjGffmXh6YhS3fN8bFFXR"
DRIVE_IWF_WEIGHTLIFTING_ID        = "1zKSb8pNOwTy8D81AUhiIQ7_Wf9Ja-1mu"
DRIVE_UWW_WRESTLING_ID            = "167hC9l2_8j5oDPmM_hI_4YjRCgJK-Jmx"
DRIVE_FIH_HOCKEY_ID               = "1HFnDK2LDZn6bGKQvlLbJ9_pCMEMJYZf9"
DRIVE_IIHF_ICEHOCKEY_ID           = "1KfjlAyvRjylcGfJf3ROALjeHQd-1m-kG"
DRIVE_WORLD_LACROSSE_ID           = "1NoN0G4tQ842lWEFlXI9NftiU6oTyQD8k"
DRIVE_ICC_CRICKET_ID              = "11P4Pr3DSv8krT7J_jwbPIIKSzyYHdton"
DRIVE_WORLD_ARCHERY_ID            = "1n0xPPB1pVvITbggDjDYtyHBMxT8uN3Kz"
DRIVE_ITTF_TABLETENNIS_ID         = "10kqMFlpQG6VkyBQwv-iVJHSVOglyIlB8"
DRIVE_ICF_CANOE_ID                = "1NuvmwUoLM3kf4j9mV3i5tE9MbAxUG9TA"
DRIVE_WORLD_SAILING_ID            = "1SYoxWptzaCM0eEv4Rx-XEIjn0kieSJb8"
DRIVE_IFSC_CLIMBING_ID            = "1TucCl68fbYgdr9lZALmNN68Kxwt-KvIz"
DRIVE_ISA_SURFING_ID              = "1USvI_n3bFSPLTL1E3ioWubVocqD73Ef6"
DRIVE_UIPM_PENTATHLON_ID          = "127iHJkdwNeE1_4KDcMvyOEgieA5YdAxt"
# Sección 10 — Paralímpico
DRIVE_IPC_PARALYMPIC_ID           = "1y-7o_2F6N-0IJTh5R856bjXNfXwVK61a"
DRIVE_WORLD_PARA_ATHLETICS_ID     = "1KCy-6zBoPlDPtVmE6jG6UcDfHIu7OkS8"
DRIVE_WORLD_PARA_SWIMMING_ID      = "1wFSqYRXfAvpfC65fSG1x3gy5kZqM2DUF"
DRIVE_WORLD_PARA_POWERLIFTING_ID  = "1Kzs9DV4sw4qU7YBqf_gwuR8p7jsJsFDw"
DRIVE_WORLD_BOCCIA_ID             = "1ctjXzvjVKGvkQ6PrXEP601vLs49ikM7x"
DRIVE_WORLD_WHEELCHAIR_RUGBY_ID   = "1hGi72qbxnJNCrIYDkoqhZdrjXIYy_-8M"
DRIVE_IWBF_WHEELCHAIR_BASKETBALL_ID = "1BOSogwuQLOfOcezsTic2DrWf7d9aMkQB"
DRIVE_IBSA_BLIND_SPORTS_ID        = "1pzFnY2G63mCkennTIXNxE0okEfflBmqU"
DRIVE_VIRTUS_SPORT_ID             = "1Slb12fp55V0fP8jnnWpeFaH_LiehIauA"
DRIVE_WORLD_ABILITYSPORT_ID       = "1zDV50CXxYMd8KB9BCN4Wn__ipwNQfllC"
DRIVE_PARAVOLLEY_ID               = "1CCNULzbwE6x2h59iPWRCEh0c1VUoO5ts"
DRIVE_PARALYMPICS_AUSTRALIA_ID    = "1bi5hCSI93MFuxaH0K3JKjSk2ZoVCVufv"
DRIVE_USOPC_PARALYMPIC_ID         = "1AgknHNzDOxnL334I3hlcidv8lzuuLAST"
# Sección 11 — Desarrollo de entrenadores
DRIVE_ICCE_COACHING_ID            = "1ZeOS8xpb0hNvjrqMlsmLl0lpfy5KHZZu"
DRIVE_UEFA_COACHING_CONVENTION_ID = "1GyhW-fz0ylqlg72EPsD6yZgBojcvt0EM"
DRIVE_CONMEBOL_EVOLUCION_ID       = "1pAd1FDRi1cgn5tafT3XLnDmwGbk35B1n"
DRIVE_ENGLAND_FOOTBALL_PUBLIC_ID  = "1rE2oCmowin-LuWQOfcrZmixWaL6v9vlc"
DRIVE_UK_COACHING_ID              = "1p-B2t8Q7dzDY_xmSqrUEodp46Nu4WvSN"
DRIVE_COACHING_ASSOC_CANADA_ID    = "1JGvwZe_YBaG_56-4IKnHqeUtmyaU5RGt"
DRIVE_SPORT_NZ_COACHING_ID        = "1TCvE2dGWR3FtXflg73caEtgDaNTSkNOd"
DRIVE_OLYMPIC_SOLIDARITY_ID       = "1ESawxdOMfEzqCPX8ayuu7FUlpKV0B365"
# Sección 12 — Tecnología deportiva
DRIVE_POLAR_SCIENCE_ID            = "1pMp5XLruf3CMuKr83gMepzzsudzwSNXl"
DRIVE_GARMIN_HEALTH_SCIENCE_ID    = "17lVKBOd1A0crOV2yaufkBhJddlNHDyQQ"
DRIVE_FIRSTBEAT_SCIENCE_ID        = "1fIaRy5ToQGyY6_O6a45nfYtCeomETSNC"
DRIVE_VALD_PERFORMANCE_ID         = "1nHDQjlm8OAmI1FQxpf0yUtipFSyy2z1w"
DRIVE_STATSPORTS_RESOURCES_ID     = "1fdLaQ1PBojVKLNRii1XPVd2jJVEJt3ke"
DRIVE_KINEXON_SPORTS_ID           = "1-gT1a_VcbZMjJq1f0IAb8VEVeNcS-ein"
DRIVE_KUBIOS_HRV_ID               = "1ooBHXxPVSSCIr4_qOPnH3K_8cpr3pbau"
DRIVE_HRV4TRAINING_ID             = "1lL0aDZIfK1U7I7vg1YbCcPF2SF9EWyXR"
DRIVE_HAWKIN_DYNAMICS_ID          = "1C0JaBR6lDnJJvwjrDSrjSg2r926bIeQ6"
DRIVE_DELSYS_KNOWLEDGE_ID         = "1VL-TkN31z90yG-YH3lBZCF6hepWie0m9"
DRIVE_NORAXON_RESOURCES_ID        = "1OTdmErxHvJOWCpmemOzJlRoTbXThZzUV"
DRIVE_COSMED_KNOWLEDGE_ID         = "1W7JR6Qfg2EDC6Wd2SwWESuVKiJ0sxeih"
DRIVE_NEUROKIT2_ID                = "1-9n76CFyiLhJOjJ-X27SQfBiBT4q6A8A"
DRIVE_BIOSPPY_ID                  = "1ttctvaBQEnRa-ea_w5J3i8akOCIiGJI3"
DRIVE_GOLDENCHEETAH_ID            = "1Jf0lXCaSgf3vzlkSm2yzOBgMIjdafMqT"
DRIVE_ATHLETEMONITORING_ID        = "15Yh6kY5RdgmDSPxOmd-L5p-Pj-0YDW3O"
DRIVE_TRAININGPEAKS_COACH_ID      = "1Lq_5tjcD7l2Rx-nDSm5CvRY0Wm0QIsMD"
# Sección 13 — Institutos extendidos
DRIVE_UKSI_INSTITUTE_ID           = "1I54xe2EriMqpsEiCF5mLJNTBL1JyjtOO"
DRIVE_INSEP_FRANCE_ID             = "1xWuq_tcCa3taoa2b7egGqaKUyi21fOq9"
DRIVE_INSEP_OPENEDITION_ID        = "1Bq3jkdaTRC3TalKfgvnzMhfmaF_I6SLm"
DRIVE_INEFC_CATALONIA_ID          = "1aNmjtfCPM2cLiF2ii5fvPhPmwOQGpjCm"
DRIVE_ASPETAR_INSTITUTE_ID        = "1YRTCQiB6ILOnkzouTqs9FMcfyyDUB-ke"
DRIVE_COPSIN_CANADA_ID            = "19qomHjwtHtt2HOTxdvwINGHjFKShiQdY"
DRIVE_CSI_PACIFIC_ID              = "1kEbddPG6AKKCwoVIk23pW6VdXq96YgXE"
DRIVE_HPSNZ_ID                    = "1d3zTy3jH-HhNdlgpyIUM1F87Tg3lA3Qq"
DRIVE_JISS_JAPAN_ID               = "1dG89wlUoIdo0dDXsLSOig_sDN2NvbfP_"
DRIVE_SINGAPORE_SPORT_INST_ID     = "1FswFhKJxsrkq6wyRqAGbbCDCnpu4AWmj"
DRIVE_KISS_KOREA_ID               = "1m11UFCv1uMzBE85W8ZktdxCsPpwHzoSx"
DRIVE_SPORT_IRELAND_INST_ID       = "18AgI0VOtyLtZKDPIlqr0oRUjEA7dtnTa"
DRIVE_OLYMPIATOPPEN_NORWAY_ID     = "1qmHpAGjRZRPlOApyctzUah52PQkouRrk"
DRIVE_BISP_GERMANY_ID             = "1ZvLDBERkM3bYLDpoahQnuA8aurn-0oSw"
DRIVE_SFISM_SWITZERLAND_ID        = "1UIcvmSCl2pkUTtxChLNukpt7L0MyMPET"
# Sección 14 — Bases de datos OA
DRIVE_CROSSREF_API_ID             = "1tc5mqyDn0J7ReUU6k0FnGf35f56Hc0ry"
DRIVE_UNPAYWALL_API_ID            = "1dsjmbfTHs-hhkShXH3mTogTIm9XSiZLc"
DRIVE_DOAJ_API_ID                 = "1lR_xWEH79siUkH1BBtsJy06S6JwCB9ny"
DRIVE_CORE_API_ID                 = "1dSuW-D6gEO79IYdterxKmaXq66-rpXQA"
DRIVE_OPENAIRE_API_ID             = "1PNRop6ORKQxpm7dUgITebHE2IyvK6Asd"
DRIVE_SEMANTIC_SCHOLAR_API_ID     = "1-CTL3GJkBt5w2fUst9_szbODQFfPivke"
DRIVE_DATACITE_API_ID             = "1TTA3njEP0YkIsAQTHWgUcdsi95vaf8O1"
DRIVE_ZENODO_API_ID               = "1hLtPuKTMYWUjOjohxKILJKNpzwOrxSOy"
DRIVE_OSF_API_ID                  = "1OLUbfrDfP5puj5yMNpAwNfdCxbox5Fc5"
DRIVE_SPORTRXIV_ID                = "1cDKMIq1wYSpYvvetG1xiCz5bQsAaXUOn"
DRIVE_FIGSHARE_API_ID             = "12oLVJICz69tR7QayF24JEKy_SaSomw6b"
DRIVE_HARVARD_DATAVERSE_ID        = "1i0nLmKtoP76_gyK6LsUdVxTx1qcQkAYd"
DRIVE_ARXIV_SPORTS_ID             = "1VAhKlEMAllxFemBB6y_fota_TeMQND_Z"
DRIVE_LA84_DIGITAL_LIBRARY_ID     = "1e5K9zKF1Zo5SFWxwWVC51Th3Utnsr92S"
DRIVE_OLYMPIC_WORLD_LIBRARY_ID    = "1HHFgUfN2S3tegMY2Y76DjFuf5zt-HjtY"
DRIVE_NCAA_RESEARCH_ID            = "1y9Fl7v30x7c3fg52jxzVX5WcCdwqNhYt"

PROGRESS_FILE = "progress_deporte.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SportsScienceBot/1.0; research use)",
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
    # BUGFIX 2026-07-29: reglas específicas de olympics.com que deben
    # comprobarse ANTES que la regla genérica de IOC (Sección A) — si no,
    # esa regla genérica captura cualquier URL de olympics.com primero y
    # DRIVE_IOC_NUTRITION_ID / DRIVE_OLYMPIC_SOLIDARITY_ID quedan
    # inalcanzables (dead routing). Ver también líneas ~364 y ~495 (ahora
    # comentarios) donde vivían antes estas reglas, sin efecto.
    if "olympics.com" in url and "nutrition" in url: return DRIVE_IOC_NUTRITION_ID
    if "olympics.com" in url and "olympic-solidarity" in url: return DRIVE_OLYMPIC_SOLIDARITY_ID
    # A. Antidopaje e IOC
    if "olympics.com"           in url or "olympic.org" in url: return DRIVE_IOC_OLYMPICS_ID
    if "wada-ama.org"           in url:  return DRIVE_WADA_ANTIDOPING_ID
    if "usada.org"              in url:  return DRIVE_USADA_ID
    if "ukad.org.uk"            in url:  return DRIVE_UKAD_ID
    if "globaldro.com"          in url:  return DRIVE_GLOBAL_DRO_ID
    # B. Federaciones
    if "worldathletics.org"     in url:  return DRIVE_WORLD_ATHLETICS_ID
    if "fifa.com"               in url:  return DRIVE_FIFA_FOOTBALL_ID
    if "fiba.basketball"        in url:  return DRIVE_FIBA_BASKETBALL_ID
    if "fivb.com"               in url:  return DRIVE_FIVB_VOLLEYBALL_ID
    if "worldaquatics.com"      in url:  return DRIVE_WORLD_AQUATICS_ID
    if "uci.org"                in url:  return DRIVE_UCI_CYCLING_ID
    if "itftennis.com"          in url:  return DRIVE_ITF_TENNIS_ID
    if "world.rugby"            in url:  return DRIVE_WORLD_RUGBY_ID
    if "ihf.info"               in url:  return DRIVE_IHF_HANDBALL_ID
    if "bwfbadminton.com"       in url:  return DRIVE_BWF_BADMINTON_ID
    if "worldtaekwondo.org"     in url:  return DRIVE_WORLD_TAEKWONDO_ID
    if "ijf.org"                in url:  return DRIVE_IJF_JUDO_ID
    if "isu.org"                in url:  return DRIVE_ISU_SKATING_ID
    if "fis-ski.com"            in url:  return DRIVE_FIS_SKIING_ID
    if "worldrowing.com"        in url:  return DRIVE_WORLD_ROWING_ID
    if "gymnastics.sport"       in url:  return DRIVE_WORLD_GYMNASTICS_ID
    if "iba-boxing.com"         in url or "worldboxing.sport" in url or "worldboxing.org" in url: return DRIVE_WORLD_BOXING_ID
    if "ufc.com"                in url or "mma"     in url:  return DRIVE_UFC_MMA_RESOURCES_ID
    # C. Ciencias del deporte
    if "acsm.org"               in url:  return DRIVE_ACSM_ID
    if "nsca.com"               in url:  return DRIVE_NSCA_ID
    if "ecss.de"                in url:  return DRIVE_ECSS_ID
    if "bases.org.uk"           in url:  return DRIVE_BASES_UK_ID
    if "strengthandconditioning.org" in url: return DRIVE_ASCA_AU_ID
    if "uksca.org.uk"           in url:  return DRIVE_UKSCA_ID
    if "conade.gob.mx"          in url:  return DRIVE_CONADE_MEXICO_ID
    if "clearinghouseforsport"  in url:  return DRIVE_SPORT_AUSTRALIA_CLEARINGHOUSE_ID
    if "uksport.gov.uk"         in url:  return DRIVE_UK_SPORT_ID
    if "usopc.org"              in url or "teamusa.org" in url: return DRIVE_USOPC_RESOURCES_ID
    # D. Medicina deportiva
    if "fims.org"               in url:  return DRIVE_FIMS_ID
    if "amssm.org"              in url:  return DRIVE_AMSSM_ID
    if "aossm.org"              in url:  return DRIVE_AOSSM_ID
    if "esska.org"              in url:  return DRIVE_ESSKA_ID
    if "bjsm.bmj.com"           in url:  return DRIVE_BJSM_ID
    if "sportshealth.org"       in url or "journals.sagepub.com/home/sph" in url: return DRIVE_SPORTS_HEALTH_JOURNAL_ID
    if "nata.org"               in url:  return DRIVE_NATA_ATHLETIC_TRAINING_ID
    # E. Nutrición deportiva
    if "jissn.biomedcentral.com" in url or "issn.org" in url: return DRIVE_ISSN_NUTRITION_ID
    # BUGFIX 2026-07-29: "ais.gov.au" a secas era demasiado genérico y
    # capturaba TODAS las URLs de ais.gov.au (recipes/mental-health/general
    # incluidas), dejando DRIVE_AIS_AUSTRALIA_ID, DRIVE_AIS_NUTRITION_RECIPES_ID
    # y DRIVE_AIS_MENTAL_HEALTH_ID inalcanzables (dead routing). Se acota por
    # path y se reordena de más a menos específico; el fallback genérico de
    # ais.gov.au sigue viviendo en la Sección I (DRIVE_AIS_AUSTRALIA_ID).
    if "ais.gov.au" in url and "recipe"    in url: return DRIVE_AIS_NUTRITION_RECIPES_ID
    if "ais.gov.au" in url and "mental"    in url: return DRIVE_AIS_MENTAL_HEALTH_ID
    if "ais.gov.au" in url and "nutrition" in url: return DRIVE_AIS_NUTRITION_ID
    if "gssiweb.org"            in url:  return DRIVE_GSSI_GATORADE_ID
    if "scandpg.org"            in url:  return DRIVE_SCAN_DIETITIANS_ID
    # NOTA 2026-07-29: la regla IOC Nutrition se movió al principio de la
    # función (antes de la Sección A) — aquí quedaba inalcanzable porque
    # "olympics.com" ya se captura de forma genérica más arriba.
    # F. Psicología
    if "appliedsportpsych.org"  in url:  return DRIVE_AASP_PSYCHOLOGY_ID
    if "issponline.org"         in url:  return DRIVE_ISSP_PSYCHOLOGY_ID
    if "fepsac.eu"              in url or "fepsac.com" in url: return DRIVE_FEPSAC_EUROPE_ID
    # G. Fuerza / biomecánica
    if "isbs.org"               in url:  return DRIVE_ISBS_BIOMECHANICS_ID
    if "vbt"                    in url or "velocity-based" in url: return DRIVE_VELOCITY_BASED_TRAINING_ID
    if "catapultsports.com"     in url:  return DRIVE_CATAPULT_RESOURCES_ID
    # H. Revistas OA
    if "jssm.org"               in url:  return DRIVE_JSSM_JOURNAL_ID
    if "mdpi.com/journal/sports" in url: return DRIVE_SPORTS_MDPI_ID
    # BUGFIX 2026-07-29: la regla de psicología debe ir ANTES que la regla
    # genérica "sports" de abajo — la mayoría de URLs de investigación de
    # Frontiers sobre psicología deportiva incluyen "sports-psychology" en el
    # slug, así que "sports" in url ya las capturaba primero y
    # DRIVE_FRONTIERS_SPORT_PSYCH_ID quedaba inalcanzable (dead routing).
    if "frontiersin.org" in url and "psychology" in url and "sport" in url: return DRIVE_FRONTIERS_SPORT_PSYCH_ID
    if "frontiersin.org"        in url and "sports" in url: return DRIVE_FRONTIERS_SPORTS_ID
    if "bmcsportsscimedrehabil"  in url: return DRIVE_BMC_SPORTS_SCI_ID
    if "peerj.com"              in url and "sport" in url: return DRIVE_PEERJ_SPORTS_ID
    if "translational-sports-medicine" in url: return DRIVE_TRANSLATIONAL_SPORTS_MED_ID
    if "ijspp.humankinetics.com" in url: return DRIVE_INTL_J_SPORTS_PHYSIOL_ID
    if "tandfonline.com/journals/rjsp" in url: return DRIVE_JOURNAL_SPORT_SCIENCE_ID
    # I. Institutos de élite
    if "clearinghouseforsport.gov.au" in url or ("ais.gov.au" in url and "nutrition" not in url): return DRIVE_AIS_AUSTRALIA_ID
    if "inef.upm.es"            in url:  return DRIVE_INEF_SPAIN_ID
    if "aspire.qa"              in url:  return DRIVE_ASPIRE_QATAR_ID
    if "canadiansportinstitute" in url or "csiontario.ca" in url: return DRIVE_CANADIAN_SPORT_INSTITUTE_ID
    # BUGFIX 2026-07-29: la regla específica de coaching debe ir ANTES que la
    # regla genérica de sportnz.org.nz — si no, cualquier URL de coaching
    # (que también contiene "sportnz.org.nz") se capturaba aquí primero y
    # DRIVE_SPORT_NZ_COACHING_ID quedaba inalcanzable (dead routing).
    if "sportnz.org.nz" in url and "coaching" in url: return DRIVE_SPORT_NZ_COACHING_ID
    if "sportnz.org.nz"         in url:  return DRIVE_SPORT_NEW_ZEALAND_ID
    # J. Bases de datos
    if "sirc.ca"                in url:  return DRIVE_SIRC_CANADA_ID
    if "pubmed.ncbi.nlm.nih.gov" in url: return DRIVE_PUBMED_SPORTS_ID
    # NOTA 2026-07-29: icce-office.org/coachingassociation.ca ya no
    # resuelven; ver icce.ws / coach.ca. DRIVE_ICCE_COACHING_ID y
    # DRIVE_COACHING_ASSOC_CANADA_ID están definidos pero NUNCA se alcanzan
    # aquí — fetch_coach_education_urls(), fetch_icce_coaching_urls() y
    # fetch_coaching_assoc_canada_urls() rastrean los MISMOS dos dominios
    # (icce.ws y coach.ca), así que sus URLs son indistinguibles entre sí
    # por contenido; los tres caen a este único folder por diseño previo
    # (no introducido por este fix). Diferenciarlos requeriría rediseñar
    # los fetchers, no solo el routing — dejado para revisión del equipo.
    if "icce-office.org"        in url or "coachingassociation.ca" in url or "icce.ws" in url or "coach.ca" in url: return DRIVE_COACH_EDUCATION_RESOURCES_ID
    # ── NUEVAS SECCIONES ──────────────────────────────────────────────────────
    # Sec 1 — Antidopaje extendido
    if "ita-sport.org"          in url or "ita.sport" in url: return DRIVE_ITA_SPORT_ID
    if "inado.net"              in url:  return DRIVE_INADO_ID
    if "cces.ca"                in url or "sportintegrity.ca" in url: return DRIVE_CCES_CANADA_ID
    if "nada.de"                in url:  return DRIVE_NADA_GERMANY_ID
    if "afld.fr"                in url:  return DRIVE_AFLD_FRANCE_ID
    if "celad.org"              in url or "celad.gob.es" in url: return DRIVE_CELAD_SPAIN_ID
    if "playtruejapan.org"      in url:  return DRIVE_JADA_JAPAN_ID
    if "saids.co.za"            in url or "saids.org.za" in url: return DRIVE_SAIDS_AFRICA_ID
    if "abcd.org.br"            in url:  return DRIVE_ABCD_BRAZIL_ID
    if "rados.wada-ama.org"     in url:  return DRIVE_WADA_RADOS_ID
    # Sec 2 — Fisiología
    if "casesportsscience.co.uk" in url or "cases.org.uk" in url: return DRIVE_CASES_UK_ID
    if "sportsmedicineopen"     in url:  return DRIVE_SPORTS_MED_OPEN_ID
    if "jhk.pl"                 in url or "jhk.termedia.pl" in url: return DRIVE_JHK_JOURNAL_ID
    if "ijes.info"              in url:  return DRIVE_IJES_JOURNAL_ID
    if "termedia.pl" in url and "Biology_of_Sport" in url: return DRIVE_BIOLOGY_OF_SPORT_ID
    # Sec 3 — S&C
    if "altis.world"            in url:  return DRIVE_ALTIS_SPRINT_ID
    if "simplifaster.com"       in url:  return DRIVE_SIMPLIFASTER_ID
    if "ijsc-journal.com"       in url:  return DRIVE_IJSC_JOURNAL_ID
    if "spr-journal.com"        in url:  return DRIVE_SPORT_PERF_REPORTS_ID
    if "trainology.org"         in url:  return DRIVE_JOURNAL_TRAINOLOGY_ID
    if "strongerbyscience.com"  in url:  return DRIVE_STRONGER_BY_SCIENCE_ID
    if "scsociety.org"          in url:  return DRIVE_SC_SOCIETY_ID
    if "elitefts.com"           in url:  return DRIVE_ELITEFTS_EDU_ID
    # Sec 4 — Nutrición
    if "sportsdietitians.com.au" in url: return DRIVE_SPORTS_DIETITIANS_AU_ID
    if "athletetriadcoalition.org" in url: return DRIVE_ATHLETE_TRIAD_COALITION_ID
    # NOTA 2026-07-29: reglas de ais.gov.au (recipe/mental) movidas a la
    # Sección E (más arriba) — aquí eran inalcanzables (dead routing), ver
    # comentario junto a DRIVE_AIS_NUTRITION_ID.
    # Sec 5 — Psicología extendida
    # NOTA 2026-07-29: regla de Frontiers Sport Psych movida antes de la
    # regla genérica de Frontiers Sports (Sección H) — aquí era inalcanzable
    # porque "sports" (plural) ya aparece en la mayoría de esas URLs.
    if "ncaa.org" in url and "mental" in url: return DRIVE_NCAA_MENTAL_HEALTH_ID
    # Sec 6 — Biomecánica
    if "isbweb.org"             in url:  return DRIVE_ISB_WEB_ID
    if "opensim.stanford.edu"   in url or "opensimconfluence.atlassian.net" in url: return DRIVE_OPENSIM_ID
    if "opencap.ai"             in url:  return DRIVE_OPENCAP_ID
    if "simtk.org"              in url:  return DRIVE_SIMTK_ID
    if "kinovea.org"            in url:  return DRIVE_KINOVEA_ID
    if "c-motion.com"           in url or "has-motion.ca" in url or "has-motion.com" in url: return DRIVE_VISUAL3D_WIKI_ID
    if "vicon.com"              in url:  return DRIVE_VICON_RESOURCES_ID
    if "qualisys.com"           in url:  return DRIVE_QUALISYS_RESOURCES_ID
    # Sec 7 — Medicina deportiva extendida
    if "natajournals.org"       in url:  return DRIVE_JAT_JOURNAL_ID
    if "aspetarjournal.com"     in url or "journal.aspetar.com" in url: return DRIVE_ASPETAR_JOURNAL_ID
    if "sagepub.com/toc/ojs"    in url:  return DRIVE_OJSM_JOURNAL_ID
    if "cdc.gov/headsup"        in url:  return DRIVE_CDC_HEADS_UP_ID
    if "ifspt.org"              in url:  return DRIVE_IFSPT_ID
    if "physio-pedia.com"       in url:  return DRIVE_PHYSIOPEDIA_SPORTS_ID
    # Sec 8 — Táctica
    if "training.fifa.com"      in url or "fifatrainingcentre.com" in url: return DRIVE_FIFA_TRAINING_CENTRE_ID
    # BUGFIX 2026-07-29: la regla de football-development/coaching (Sec 11)
    # debe comprobarse ANTES que esta regla de "documents or coaching" — el
    # seed de UEFA Coaching Convention vive bajo
    # insideuefa/football-development/coaching/, así que su URL contiene
    # "coaching" y esta regla más genérica la capturaba primero,
    # dejando DRIVE_UEFA_COACHING_CONVENTION_ID inalcanzable (dead routing).
    if "uefa.com" in url and "football-development" in url: return DRIVE_UEFA_COACHING_CONVENTION_ID
    if "uefa.com" in url and ("documents" in url or "coaching" in url): return DRIVE_UEFA_TECHNICAL_REPORTS_ID
    if "statsbomb.com"          in url:  return DRIVE_STATSBOMB_OPENDATA_ID
    if "metrica-sports.com"     in url:  return DRIVE_METRICA_SPORTS_ID
    if "skillcorner.com"        in url:  return DRIVE_SKILLCORNER_OPENDATA_ID
    if "kloppy.readthedocs.io"  in url:  return DRIVE_KLOPPY_LIBRARY_ID
    if "socceraction.readthedocs" in url: return DRIVE_SOCCERACTION_LIB_ID
    if "sloansportsconference.com" in url: return DRIVE_MIT_SLOAN_ANALYTICS_ID
    # Sec 9 — Federaciones extendidas
    if "theifab.com"            in url:  return DRIVE_IFAB_LAWS_ID
    if "worldskate.org"         in url:  return DRIVE_WORLD_SKATE_ID
    if "immaf.org"              in url:  return DRIVE_IMMAF_ID
    if "wbsc.org"               in url:  return DRIVE_WBSC_BASEBALL_ID
    if "igfgolf.org"            in url:  return DRIVE_IGF_GOLF_ID
    if "randa.org"              in url:  return DRIVE_RANDA_GOLF_ID
    if "triathlon.org"          in url:  return DRIVE_WORLD_TRIATHLON_ID
    if "fie.ch"                 in url or "fie.org" in url: return DRIVE_FIE_FENCING_ID
    if "issf-sports.org"        in url:  return DRIVE_ISSF_SHOOTING_ID
    if "iwf.sport"              in url:  return DRIVE_IWF_WEIGHTLIFTING_ID
    if "uww.org"                in url:  return DRIVE_UWW_WRESTLING_ID
    if "fih.ch"                 in url or "fih.hockey" in url: return DRIVE_FIH_HOCKEY_ID
    if "iihf.com"               in url:  return DRIVE_IIHF_ICEHOCKEY_ID
    if "worldlacrosse.sport"    in url:  return DRIVE_WORLD_LACROSSE_ID
    if "icc-cricket.com"        in url:  return DRIVE_ICC_CRICKET_ID
    if "worldarchery.sport"     in url:  return DRIVE_WORLD_ARCHERY_ID
    if "ittf.com"               in url:  return DRIVE_ITTF_TABLETENNIS_ID
    if "canoeicf.com"           in url:  return DRIVE_ICF_CANOE_ID
    if "sailing.org"            in url:  return DRIVE_WORLD_SAILING_ID
    if "ifsc-climbing.org"      in url:  return DRIVE_IFSC_CLIMBING_ID
    if "isasurf.org"            in url:  return DRIVE_ISA_SURFING_ID
    if "uipmworld.org"          in url:  return DRIVE_UIPM_PENTATHLON_ID
    # Sec 10 — Paralímpico
    # BUGFIX 2026-07-29: worldparaathletics.org/worldparaswimming.org/
    # worldparapowerlifting.org ya no resuelven (SSL SNI error) — esos
    # fetchers ahora usan paralympic.org/athletics|swimming|powerlifting.
    # Estas reglas específicas deben comprobarse ANTES que la regla
    # genérica de paralympic.org (abajo), si no la shadowean y
    # DRIVE_WORLD_PARA_ATHLETICS_ID / _SWIMMING_ID / _POWERLIFTING_ID
    # quedarían inalcanzables (dead routing).
    if "paralympic.org" in url and "/athletics" in url: return DRIVE_WORLD_PARA_ATHLETICS_ID
    if "paralympic.org" in url and "/swimming" in url: return DRIVE_WORLD_PARA_SWIMMING_ID
    if "paralympic.org" in url and "/powerlifting" in url: return DRIVE_WORLD_PARA_POWERLIFTING_ID
    if "paralympic.org"         in url:  return DRIVE_IPC_PARALYMPIC_ID
    if "worldparaathletics.org" in url:  return DRIVE_WORLD_PARA_ATHLETICS_ID
    if "worldparaswimming.org"  in url:  return DRIVE_WORLD_PARA_SWIMMING_ID
    if "worldparapowerlifting.org" in url: return DRIVE_WORLD_PARA_POWERLIFTING_ID
    if "bisfed.com"             in url:  return DRIVE_WORLD_BOCCIA_ID
    if "worldwheelchairrugby.org" in url or "worldwheelchair.rugby" in url: return DRIVE_WORLD_WHEELCHAIR_RUGBY_ID
    if "iwbf.org"               in url:  return DRIVE_IWBF_WHEELCHAIR_BASKETBALL_ID
    if "ibsasport.org"          in url:  return DRIVE_IBSA_BLIND_SPORTS_ID
    if "virtus.sport"           in url:  return DRIVE_VIRTUS_SPORT_ID
    if "worldabilitysport.org"  in url:  return DRIVE_WORLD_ABILITYSPORT_ID
    if "paravolley.com"         in url or "worldparavolley.org" in url: return DRIVE_PARAVOLLEY_ID
    if "paralympics.org.au"     in url:  return DRIVE_PARALYMPICS_AUSTRALIA_ID
    if "teamusa.org/us-paralympics" in url: return DRIVE_USOPC_PARALYMPIC_ID
    # Sec 11 — Entrenadores
    # NOTA 2026-07-29: reglas de UEFA Coaching Convention, Sport NZ Coaching
    # y Olympic Solidarity movidas más arriba en la función (eran
    # inalcanzables aquí, shadowed por reglas genéricas anteriores). Ver
    # comentarios junto a DRIVE_UEFA_COACHING_CONVENTION_ID,
    # DRIVE_SPORT_NZ_COACHING_ID y DRIVE_OLYMPIC_SOLIDARITY_ID.
    if "conmebol.com/evolucion" in url:  return DRIVE_CONMEBOL_EVOLUCION_ID
    if "thefa.com/football-learning" in url: return DRIVE_ENGLAND_FOOTBALL_PUBLIC_ID
    if "ukcoaching.org"         in url:  return DRIVE_UK_COACHING_ID
    # Sec 12 — Tecnología deportiva
    if "polar.com"              in url:  return DRIVE_POLAR_SCIENCE_ID
    if "garmin.com"             in url:  return DRIVE_GARMIN_HEALTH_SCIENCE_ID
    if "firstbeat.com"          in url:  return DRIVE_FIRSTBEAT_SCIENCE_ID
    if "valdperformance.com"    in url:  return DRIVE_VALD_PERFORMANCE_ID
    if "statsports.com"         in url:  return DRIVE_STATSPORTS_RESOURCES_ID
    if "kinexon.com"            in url:  return DRIVE_KINEXON_SPORTS_ID
    if "kubios.com"             in url:  return DRIVE_KUBIOS_HRV_ID
    if "hrv4training.com"       in url:  return DRIVE_HRV4TRAINING_ID
    if "hawkindynamics.com"     in url:  return DRIVE_HAWKIN_DYNAMICS_ID
    if "delsys.com"             in url:  return DRIVE_DELSYS_KNOWLEDGE_ID
    if "noraxon.com"            in url:  return DRIVE_NORAXON_RESOURCES_ID
    if "cosmed.com"             in url:  return DRIVE_COSMED_KNOWLEDGE_ID
    if "neurokit2.readthedocs"  in url or "neuropsychology.github.io" in url: return DRIVE_NEUROKIT2_ID
    if "biosppy.readthedocs"    in url:  return DRIVE_BIOSPPY_ID
    if "goldencheetah.org"      in url:  return DRIVE_GOLDENCHEETAH_ID
    if "athletemonitoring.com"  in url:  return DRIVE_ATHLETEMONITORING_ID
    if "trainingpeaks.com" in url and "coach" in url: return DRIVE_TRAININGPEAKS_COACH_ID
    # Sec 13 — Institutos extendidos
    if "uksportsinstitute.co.uk" in url: return DRIVE_UKSI_INSTITUTE_ID
    if "insep.fr"               in url:  return DRIVE_INSEP_FRANCE_ID
    if "openedition.org/insep"  in url:  return DRIVE_INSEP_OPENEDITION_ID
    if "inefc.cat"              in url or "inefc.gencat.cat" in url: return DRIVE_INEFC_CATALONIA_ID
    if "aspetar.com"            in url:  return DRIVE_ASPETAR_INSTITUTE_ID
    if "copsin.ca"              in url:  return DRIVE_COPSIN_CANADA_ID
    if "csipacific.ca"          in url:  return DRIVE_CSI_PACIFIC_ID
    if "hpsnz.org.nz"           in url:  return DRIVE_HPSNZ_ID
    if "jiss.naash.go.jp"       in url or "jpnsport.go.jp" in url: return DRIVE_JISS_JAPAN_ID
    if "sportsingapore.gov.sg"  in url:  return DRIVE_SINGAPORE_SPORT_INST_ID
    if "kiss.kspo.or.kr"        in url:  return DRIVE_KISS_KOREA_ID
    if "sportireland.ie"        in url:  return DRIVE_SPORT_IRELAND_INST_ID
    if "olympiatoppen.no"       in url:  return DRIVE_OLYMPIATOPPEN_NORWAY_ID
    if "bisp.de"                in url:  return DRIVE_BISP_GERMANY_ID
    if "sfism.ch"               in url:  return DRIVE_SFISM_SWITZERLAND_ID
    # Sec 14 — Bases de datos OA
    if "doi.org" in url and "|CROSSREF|" in url: return DRIVE_CROSSREF_API_ID
    if "doaj.org"               in url:  return DRIVE_DOAJ_API_ID
    if "zenodo.org"             in url:  return DRIVE_ZENODO_API_ID
    if "semanticscholar.org"    in url:  return DRIVE_SEMANTIC_SCHOLAR_API_ID
    if "osf.io/preprints/sportrxiv" in url: return DRIVE_SPORTRXIV_ID
    if "la84.org"               in url:  return DRIVE_LA84_DIGITAL_LIBRARY_ID
    if "library.olympics.com"   in url:  return DRIVE_OLYMPIC_WORLD_LIBRARY_ID
    if "ncaa.org" in url and "research" in url: return DRIVE_NCAA_RESEARCH_ID
    return DRIVE_STRENGTH_POWER_RESEARCH_ID  # fallback


def upload_file(service, url, name, content):
    folder_id = folder_for_url(url)
    media = MediaInMemoryUpload(content.encode("utf-8"), mimetype="text/plain")
    service.files().create(
        body={"name": name, "parents": [folder_id]},
        media_body=media, fields="id"
    ).execute()


# ── Helpers de URL discovery ───────────────────────────────────────────────────

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
        from urllib.parse import urljoin
        for a in soup.find_all("a", href=True):
            href = a["href"]
            # BUGFIX 2026-07-29: solo se resolvían los enlaces que empezaban
            # con "/" (root-relative). Muchos sitios de documentación
            # (Sphinx/GitHub Pages/Confluence, etc.) usan enlaces
            # path-relative sin "/" inicial (p.ej. "introduction.html",
            # "examples/index.html") — esos se descartaban en silencio
            # porque nunca empezaban con "http". urljoin() ya maneja
            # correctamente los casos absolutos, root-relative y
            # path-relative por igual, así que se aplica siempre.
            if not href.startswith(("http://", "https://")):
                href = urljoin(seed, href)
            if domain_prefix in href and href.startswith("http"):
                urls.add(href)
        time.sleep(delay)
        return list(urls)
    except Exception:
        return []


# ── Fetchers por fuente ────────────────────────────────────────────────────────

# A. IOC y antidopaje
def fetch_ioc_urls():
    urls = _fetch_sitemap_index_urls("https://www.olympics.com/sitemap.xml",
        url_filter=lambda u: any(k in u for k in ["athlete", "sport", "news", "medical", "education"]),
        delay=1.5)
    return urls

def fetch_wada_urls():
    return _crawl_one_level("https://www.wada-ama.org/en/resources", "wada-ama.org", delay=3.0)

def fetch_usada_urls():
    return _crawl_one_level("https://www.usada.org/resources/", "usada.org", delay=3.0)

def fetch_ukad_urls():
    # BUGFIX 2026-07-29: /resources daba 404 (sitio Drupal reestructurado);
    # el sitemap real está en la raíz.
    urls = fetch_urls_from_sitemap("https://www.ukad.org.uk/sitemap.xml")
    return [u for u in urls if any(k in u for k in ["resource", "article", "news", "guidance"])]

def fetch_global_dro_urls():
    return _crawl_one_level("https://www.globaldro.com/", "globaldro.com", delay=3.0)

# B. Federaciones
def fetch_world_athletics_urls():
    # Investigado 2026-07-29: "/sitemap.xml" da 404 (JSON/HTML de su app).
    # robots.txt SÍ lista el sitemap real en
    # "https://worldathletics.org/sitemap/sitemapindex.xml", pero esa URL
    # también 404s vía su router, y "/sitemap/sitemap.xml" (variante probada)
    # devuelve un 403 "AccessDenied" con RequestId/HostId — es un error
    # nativo de S3, es decir, el archivo del sitemap vive en un bucket S3
    # sin acceso público. La homepage sí responde 200 (no es bloqueo WAF de
    # dominio), pero no hay ningún sitemap accesible para acotar el rastreo
    # — no evadir (no es un bucket nuestro). Dejado como estaba.
    return _fetch_sitemap_index_urls("https://worldathletics.org/sitemap.xml",
        url_filter=lambda u: any(k in u for k in ["news", "athlete", "records", "disciplines", "about"]),
        delay=1.5)

def fetch_fifa_urls():
    # Investigado 2026-07-29: "/football-development/" da 404 — fifa.com se
    # reestructuró completamente sobre una API CXM (cxm-api.fifa.com). Su
    # nuevo sitemap real (via robots.txt: fifa.com/sitemap -> redirige a la
    # API) SÍ funciona pero es enorme (357 sub-sitemaps, decenas de miles de
    # URLs, casi todo contenido de torneos, no de desarrollo/coaching — un
    # muestreo de 15 sub-sitemaps solo encontró 2 URLs con "development" o
    # "technical"). No existe ya una sección de football-development/
    # coaching equivalente a la original. Se toman solo los primeros
    # sub-sitemaps (no los 357) para evitar un fetch desproporcionado.
    sub_sitemaps = fetch_urls_from_sitemap("https://www.fifa.com/sitemap")
    urls = []
    for sm in sub_sitemaps[:3]:
        urls.extend(fetch_urls_from_sitemap(sm))
        time.sleep(0.5)
    return urls

def fetch_fiba_urls():
    return _crawl_one_level("https://www.fiba.basketball/pages/eng/fa/news/p/id/NWSVL.html", "fiba.basketball", delay=3.0)

def fetch_fivb_urls():
    return _crawl_one_level("https://www.fivb.com/en/volleyball/resources", "fivb.com", delay=3.0)

def fetch_world_aquatics_urls():
    return _crawl_one_level("https://www.worldaquatics.com/news", "worldaquatics.com", delay=3.0)

def fetch_uci_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.uci.org/media-publications/1qiwynsDdy4m9RTsk34XPc -> 65 URLs.
    return _crawl_one_level("https://www.uci.org/media-publications/1qiwynsDdy4m9RTsk34XPc", "uci.org", delay=3.0)

def fetch_itf_urls():
    # Confirmado bloqueado por WAF (2026-07-29): esta ruta específica
    # devuelve HTTP 200 pero el cuerpo es solo un challenge JS de Incapsula
    # (`<meta content="noindex,nofollow">` + `/_Incapsula_Resource?...`,
    # 212 bytes). La homepage sí carga contenido real, pero esta sección
    # concreta está protegida — no evadir.
    return _crawl_one_level("https://www.itftennis.com/en/about-us/science-and-technical/", "itftennis.com", delay=3.0)

def fetch_world_rugby_urls():
    return _crawl_one_level("https://www.world.rugby/the-game/player-welfare/", "world.rugby", delay=3.0)

def fetch_ihf_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.ihf.info/about/education -> 70 URLs.
    return _crawl_one_level("https://www.ihf.info/about/education", "ihf.info", delay=3.0)

def fetch_bwf_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://bwfbadminton.com/news/ -> 47 URLs.
    return _crawl_one_level("https://bwfbadminton.com/news/", "bwfbadminton.com", delay=3.0)

def fetch_world_taekwondo_urls():
    # BUGFIX 2026-07-29: "/education/" devuelve HTTP 400 con un error JSON
    # en coreano ("서버에서 오류가 발생하였습니다" / error de servidor, code S001)
    # — el sitio se reestructuró y ya no tiene una sección de "education" en
    # su navegación actual. Se usa la sección de noticias, que sí carga.
    return _crawl_one_level("https://www.worldtaekwondo.org/news/NS/list", "worldtaekwondo.org", delay=3.0)

def fetch_ijf_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.ijf.org/news/show/technical-development-a-different-angle -> 69 URLs.
    return _crawl_one_level("https://www.ijf.org/news/show/technical-development-a-different-angle", "ijf.org", delay=3.0)

def fetch_isu_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.isu.org/news/figure-skating-loses-a-coaching-legend-viktor-kudriavtsev-passes-away-at-88 -> 53 URLs.
    return _crawl_one_level("https://www.isu.org/news/figure-skating-loses-a-coaching-legend-viktor-kudriavtsev-passes-away-at-88/", "isu.org", delay=3.0)

def fetch_fis_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.fis-ski.com/news -> 18 URLs.
    return _crawl_one_level("https://www.fis-ski.com/news", "fis-ski.com", delay=3.0)

def fetch_world_rowing_urls():
    return _crawl_one_level("https://worldrowing.com/technical/", "worldrowing.com", delay=3.0)

def fetch_world_gymnastics_urls():
    return _crawl_one_level("https://www.gymnastics.sport/site/rules.php", "gymnastics.sport", delay=3.0)

def fetch_world_boxing_urls():
    # BUGFIX 2026-07-29: iba-boxing.com ya no resuelve (dominio muerto — la
    # federación es ahora "World Boxing", no IBA). El comentario del código
    # en folder_for_url() ya sugería "worldboxing.sport" como alternativa,
    # pero ESE dominio tampoco resuelve; el dominio real y en vivo es
    # worldboxing.org.
    return _crawl_one_level("https://worldboxing.org/news/", "worldboxing.org", delay=3.0)

# C. Ciencias del deporte
def fetch_acsm_urls():
    return _fetch_sitemap_index_urls("https://www.acsm.org/sitemap.xml",
        url_filter=lambda u: any(k in u for k in ["articles", "news", "education", "research", "resource"]),
        delay=1.5)

def fetch_nsca_urls():
    # BUGFIX 2026-07-29: /education/resources/ daba 404 (sitio reestructurado).
    urls = fetch_urls_from_sitemap("https://www.nsca.com/sitemap.xml")
    return [u for u in urls if any(k in u for k in ["article", "education", "certification"])]

def fetch_ecss_urls():
    # Investigado 2026-07-29: ecss.de tiene un certificado TLS EXPIRADO
    # (CERTIFICATE_VERIFY_FAILED: certificate has expired) y no responde en
    # HTTP plano (connection refused) — el sitio real está inaccesible sin
    # desactivar la verificación TLS, algo que no se debe hacer para
    # evadir un problema de seguridad del sitio de destino. No se encontró
    # dominio alternativo. Dejado como estaba — necesita más investigación
    # o esperar a que ECSS renueve su certificado.
    return _crawl_one_level("https://www.ecss.de/publications/", "ecss.de", delay=3.0)

def fetch_bases_uk_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.bases.org.uk/spage-professional_development-supervised_experience.html -> 31 URLs.
    return _crawl_one_level("https://www.bases.org.uk/spage-professional_development-supervised_experience.html", "bases.org.uk", delay=3.0)

def fetch_asca_au_urls():
    return _crawl_one_level("https://www.strengthandconditioning.org/resources/", "strengthandconditioning.org", delay=3.0)

def fetch_uksca_urls():
    return _crawl_one_level("https://www.uksca.org.uk/resources", "uksca.org.uk", delay=3.0)

def fetch_conade_urls():
    # Investigado 2026-07-29: dos bugs. (1) domain_prefix mismatch —
    # "conade.gob.mx" no es un dominio real, CONADE vive bajo la ruta
    # gob.mx/conade (portal unificado del gobierno mexicano), así que el
    # filtro nunca podía coincidir con nada. (2) "/conade/articulos" da 404
    # — la home de gob.mx/conade usa navegación por anclas hash
    # (#15837, #15839...) resueltas por JS, no enlaces <a href> reales, así
    # que ni con el domain_prefix corregido hay mucho que rastrear
    # estáticamente (probado: solo 1 URL real en la home). Se corrige el
    # domain_prefix por consistencia aunque el rendimiento siga siendo bajo;
    # requeriría un scraper con JS para más contenido — fuera de alcance.
    return _crawl_one_level("https://www.gob.mx/conade", "gob.mx/conade", delay=3.0)

def fetch_sport_australia_clearinghouse_urls():
    # Investigado 2026-07-29: "/sitemap.xml" y "/robots.txt" devuelven
    # ambos HTTP 200 pero con el MISMO HTML del shell de la SPA (Next.js/
    # React) — el sitio no tiene fallback de servidor para esas rutas y
    # sirve el index.html para cualquier path no reconocido por su router
    # cliente. No es un bloqueo WAF; es que el contenido real se renderiza
    # en el cliente y no está presente en el HTML servido — un scraper
    # estático (BeautifulSoup) no puede extraer enlaces reales de aquí sin
    # ejecutar JS, fuera de alcance para este fetcher. Dejado como estaba.
    return _fetch_sitemap_index_urls("https://www.clearinghouseforsport.gov.au/sitemap.xml", delay=1.5)

def fetch_uk_sport_urls():
    return _crawl_one_level("https://www.uksport.gov.uk/resources", "uksport.gov.uk", delay=2.0)

def fetch_usopc_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.usopc.org/coaching-education -> 61 URLs.
    return _crawl_one_level("https://www.usopc.org/coaching-education", "usopc.org", delay=3.0)

# D. Medicina deportiva
def fetch_fims_urls():
    return _crawl_one_level("https://www.fims.org/resources/", "fims.org", delay=3.0)

def fetch_amssm_urls():
    return _crawl_one_level("https://www.amssm.org/Content.aspx?ID=197", "amssm.org", delay=3.0)

def fetch_aossm_urls():
    return _crawl_one_level("https://www.aossm.org/education/", "aossm.org", delay=3.0)

def fetch_esska_urls():
    return _crawl_one_level("https://www.esska.org/library/", "esska.org", delay=3.0)

def fetch_bjsm_urls():
    return _fetch_sitemap_index_urls("https://bjsm.bmj.com/sitemap.xml",
        url_filter=lambda u: "content" in u,
        delay=1.0)

def fetch_sports_health_urls():
    return _crawl_one_level("https://journals.sagepub.com/toc/spha/current", "sagepub.com", delay=2.0)

def fetch_nata_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.nata.org/news-publications/press-room -> 146 URLs.
    return _crawl_one_level("https://www.nata.org/news-publications/press-room", "nata.org", delay=3.0)

def _fetch_springer_journal_articles(journal_slug, max_pages=20, delay=2.0):
    """BUGFIX 2026-07-29: *.biomedcentral.com/*.springeropen.com/sitemap.xml
    redirige al sitemap GLOBAL de Springer (todas sus revistas, millones de
    URLs) — no sirve para acotar a una sola revista (se detectó con ISSN
    Nutrition devolviendo 9,968,660 URLs). El subdominio dedicado de cada
    revista sí está bien acotado; se recorre su listado paginado de
    artículos en su lugar."""
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


# E. Nutrición deportiva
def fetch_issn_nutrition_urls():
    return _fetch_springer_journal_articles("jissn")

def fetch_ais_nutrition_urls():
    return _crawl_one_level("https://www.ais.gov.au/nutrition/", "ais.gov.au", delay=2.0)

def fetch_gssi_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.gssiweb.org/en/about -> 15 URLs.
    return _crawl_one_level("https://www.gssiweb.org/en/about", "gssiweb.org", delay=2.0)

def fetch_scan_urls():
    # Investigado 2026-07-29: scandpg.org tiene un certificado TLS con
    # hostname mismatch y el dominio ahora redirige (vía HTTP plano) a
    # higherlogic.com, una plataforma de comunidades genérica sin
    # contenido específico de SCAN accesible en la home. No se encontró un
    # dominio/URL de reemplazo con contenido real. Dejado como estaba —
    # necesita más investigación.
    return _crawl_one_level("https://www.scandpg.org/sports-nutrition/", "scandpg.org", delay=3.0)

def fetch_ioc_nutrition_urls():
    return _crawl_one_level("https://www.olympics.com/ioc/nutrition", "olympics.com", delay=3.0)

# F. Psicología del deporte
def fetch_aasp_urls():
    return _crawl_one_level("https://www.appliedsportpsych.org/resources/", "appliedsportpsych.org", delay=3.0)

def fetch_issp_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://issponline.org/about/history/ -> 52 URLs.
    return _crawl_one_level("https://issponline.org/about/history/", "issponline.org", delay=3.0)

def fetch_fepsac_urls():
    # BUGFIX 2026-07-29: fepsac.eu tiene un certificado TLS roto (falla la
    # verificación de cadena). La federación se mudó de dominio a
    # fepsac.com (confirmado: http://www.fepsac.eu redirige ahí sin TLS).
    # Verificado en vivo: 42 URLs.
    return _crawl_one_level("https://fepsac.com/", "fepsac.com", delay=3.0)

# G. Fuerza, acondicionamiento y biomecánica
def fetch_isbs_urls():
    # BUGFIX 2026-07-29: el seed (ojs.ub.uni-konstanz.de) no coincidía con el
    # filtro de dominio ("isbs.org") — nunca podía devolver nada. El archivo
    # real de proceedings de ISBS vive en el repositorio de NMU.
    return _crawl_one_level("https://commons.nmu.edu/isbs/", "commons.nmu.edu", delay=2.0)

def fetch_catapult_urls():
    return _crawl_one_level("https://www.catapultsports.com/resources", "catapultsports.com", delay=3.0)

# H. Revistas OA
def fetch_jssm_urls():
    # BUGFIX 2026-07-29: jssm.org/sitemap.xml es un sitemap PLANO
    # (<urlset>) no un índice (<sitemapindex>). _fetch_sitemap_index_urls()
    # trataba cada una de sus ~4700 URLs de página como si fuera a su vez
    # un sub-sitemap XML — al no serlo, el parseo fallaba en silencio para
    # cada una (0 URLs, y quemaba muchísimo tiempo intentándolo con delay
    # en cada una). Se usa fetch_urls_from_sitemap() directamente.
    # Nota: 4,701 URLs es alto (>3000), pero es el sitemap completo y
    # legítimo de esta única revista (incluye décadas de números
    # atrasados), no una contaminación cross-sitio como el bug de
    # BioMedCentral — se deja sin acotar.
    return fetch_urls_from_sitemap("https://www.jssm.org/sitemap.xml")

def fetch_sports_mdpi_urls():
    return _fetch_sitemap_index_urls("https://www.mdpi.com/sitemap/sitemap-sports.xml",
        url_filter=lambda u: "/sports/" in u and "/article" in u,
        delay=1.0)

def fetch_frontiers_sports_urls():
    return _fetch_sitemap_index_urls(
        "https://www.frontiersin.org/sitemap.xml",
        url_filter=lambda u: "sports" in u and "article" in u,
        delay=1.0,
    )

def fetch_bmc_sports_sci_urls():
    return _fetch_springer_journal_articles("bmcsportsscimedrehabil")

def fetch_peerj_sports_urls():
    # Investigado 2026-07-29: el filtro nunca puede coincidir — los artículos
    # de PeerJ usan URLs numéricas sin slug de tema (p.ej.
    # "peerj.com/articles/16241/"), así que "sport" jamás aparece en la URL
    # (confirmado: 50,000+ URLs en sitemap1.xml, ninguna contiene "sport").
    # PeerJ tampoco tiene páginas de listado por materia navegables
    # (/subjects/kinesiology.../ da 404) y su página de búsqueda
    # (/search/?q=sport) carga resultados vía JS — el HTML estático no trae
    # enlaces reales, así que _crawl_one_level tampoco sirve. Necesitaría la
    # API de búsqueda de PeerJ (fuera de alcance de este arreglo). Dejado
    # como estaba — fuente que sigue devolviendo 0 hasta rediseñar el
    # fetcher con esa API.
    return _fetch_sitemap_index_urls(
        "https://peerj.com/sitemap.xml",
        url_filter=lambda u: "sport" in u.lower() and "article" in u,
        delay=1.0,
    )

def fetch_translational_sports_med_urls():
    # Investigado 2026-07-29: dos bugs. (1) domain_prefix mismatch — el
    # filtro "translational-sports" no es un dominio real, así que nunca
    # podía coincidir con URLs de onlinelibrary.wiley.com de todos modos.
    # (2) esta ruta específica del journal devuelve 403 (Wiley bloquea el
    # acceso automatizado a páginas de journal individuales — la home de
    # onlinelibrary.wiley.com sí responde 200, así que no es un bloqueo de
    # dominio completo, pero no se encontró una ruta alternativa accesible
    # para este journal en particular). Se corrige el domain_prefix por
    # consistencia; el 403 en la ruta del journal queda sin resolver —
    # confirmado bloqueado (2026-07-29), no evadir.
    return _crawl_one_level("https://onlinelibrary.wiley.com/journal/25738488", "onlinelibrary.wiley.com", delay=2.0)

# I. Institutos de élite
def fetch_ais_australia_urls():
    return _crawl_one_level("https://www.ais.gov.au/resources/", "ais.gov.au", delay=2.0)

def fetch_inef_spain_urls():
    # BUGFIX 2026-07-29: "/publicaciones/" da 404 (sitio reestructurado).
    # Verificado en vivo con la home: 20 URLs.
    return _crawl_one_level("https://www.inef.upm.es/", "inef.upm.es", delay=3.0)

def fetch_aspire_qatar_urls():
    return _crawl_one_level("https://www.aspire.qa/research/", "aspire.qa", delay=3.0)

def fetch_canadian_sport_institute_urls():
    # Investigado 2026-07-29: canadiansportinstitute.ca ya no resuelve
    # (NXDOMAIN). Canadá tiene varios institutos regionales (CSI Pacific,
    # CSI Ontario, CSI Calgary, etc.) pero no se encontró un dominio
    # "nacional" unificado de reemplazo evidente. Dejado como estaba —
    # necesita más investigación (podría requerir apuntar a uno de los
    # institutos regionales en su lugar, decisión de producto más que bug).
    return _crawl_one_level("https://www.canadiansportinstitute.ca/resources/", "canadiansportinstitute", delay=3.0)

def fetch_sport_nz_urls():
    return _crawl_one_level("https://www.sportnz.org.nz/resources/", "sportnz.org.nz", delay=2.0)

# J. Bases de datos y recursos educativos
def fetch_sirc_urls():
    return _crawl_one_level("https://sirc.ca/resources/", "sirc.ca", delay=3.0)

def fetch_pubmed_sports_urls():
    """PubMed E-utilities — artículos de sports medicine (MeSH)."""
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "term": '"sports medicine"[MeSH] OR "athletic performance"[MeSH] OR "exercise"[MeSH Major Topic] OR "strength training"[MeSH]',
        "retmax": 2000,
        "retmode": "json",
        "usehistory": "y",
    }
    try:
        r = requests.get(base, params=params, headers=HEADERS, timeout=30)
        data = r.json()
        webenv = data["esearchresult"]["webenv"]
        ids = data["esearchresult"]["idlist"]
        return [f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" for pmid in ids]
    except Exception:
        return []

def fetch_coach_education_urls():
    # BUGFIX 2026-07-29: icce-office.org y coachingassociation.ca ya no
    # resuelven (NXDOMAIN). ICCE se mudó a icce.ws; la Coaching Association
    # of Canada se mudó a coach.ca.
    urls = _crawl_one_level("https://icce.ws/", "icce.ws", delay=3.0)
    urls += _crawl_one_level("https://coach.ca/", "coach.ca", delay=3.0)
    return urls


# ── NUEVAS FUENTES — Inventario Maestro 2026-07-25 ────────────────────────────

# Sección 1 — Antidopaje extendido
def fetch_ita_sport_urls():
    # BUGFIX 2026-07-29: ita-sport.org ya no resuelve (dominio muerto). El
    # dominio real y en vivo es ita.sport. Verificado en vivo: 53 URLs.
    return _crawl_one_level("https://ita.sport/", "ita.sport", delay=3.0)

def fetch_inado_urls():
    # Investigado 2026-07-29: inado.net da connect timeout consistente
    # (~15-30s, no NXDOMAIN ni connection refused — el DNS resuelve pero el
    # servidor no responde). No se encontró dominio alternativo. Dejado
    # como estaba — necesita más investigación.
    return _crawl_one_level("https://www.inado.net/resources/", "inado.net", delay=3.0)

def fetch_cces_canada_urls():
    # BUGFIX 2026-07-29: cces.ca ahora redirige (rebrand) a
    # sportintegrity.ca — "Sport Integrity Canada" es el sucesor del CCES.
    # Verificado en vivo: 123 URLs.
    return _crawl_one_level("https://sportintegrity.ca", "sportintegrity.ca", delay=3.0)

def fetch_nada_germany_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.nada.de/impressum -> 74 URLs.
    return _crawl_one_level("https://www.nada.de/impressum", "nada.de", delay=3.0)

def fetch_afld_france_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.afld.fr/documentation/ -> 59 URLs.
    return _crawl_one_level("https://www.afld.fr/documentation/", "afld.fr", delay=3.0)

def fetch_celad_spain_urls():
    # BUGFIX 2026-07-29: celad.org ya no resuelve (NXDOMAIN). Es una agencia
    # gubernamental española; el dominio real es celad.gob.es. Verificado
    # en vivo: 45 URLs.
    return _crawl_one_level("https://www.celad.gob.es/", "celad.gob.es", delay=3.0)

def fetch_jada_japan_urls():
    return _crawl_one_level("https://www.playtruejapan.org/", "playtruejapan.org", delay=3.0)

def fetch_saids_africa_urls():
    # BUGFIX 2026-07-29: saids.co.za ya no resuelve (NXDOMAIN); el dominio
    # real es saids.org.za. Verificado en vivo: 4 URLs (sitio pequeño).
    return _crawl_one_level("https://www.saids.org.za/", "saids.org.za", delay=3.0)

def fetch_abcd_brazil_urls():
    return _crawl_one_level("https://www.abcd.org.br/", "abcd.org.br", delay=3.0)

def fetch_wada_rados_urls():
    # Investigado 2026-07-29: rados.wada-ama.org ya no resuelve (NXDOMAIN),
    # aunque www.wada-ama.org (dominio principal) sí funciona. RADOS es la
    # herramienta de exención de uso terapéutico de WADA; no se encontró
    # una URL/subdominio de reemplazo público (podría requerir login, dado
    # que es una herramienta operativa, no contenido editorial). Dejado
    # como estaba — necesita más investigación.
    return _crawl_one_level("https://rados.wada-ama.org/en", "rados.wada-ama.org", delay=3.0)

# Sección 2 — Fisiología extendida
def fetch_cases_uk_urls():
    # BUGFIX 2026-07-29: casesportsscience.co.uk nunca resuelve (NXDOMAIN)
    # y probablemente nunca existió con ese nombre. Descubierto en vivo:
    # BASES (British Association of Sport and Exercise Sciences) se
    # rebrandeó a "CASES" (The Chartered Association of Sport and Exercise
    # Sciences) — bases.org.uk redirige a cases.org.uk. Nota: esto hace que
    # esta fuente y "BASES UK" (fetch_bases_uk_urls) sean ahora la MISMA
    # organización real; se mantiene el path distinto al de BASES UK para
    # minimizar solapamiento de contenido, con su propio folder dedicado
    # (DRIVE_CASES_UK_ID). Verificado en vivo: 192 URLs.
    return _crawl_one_level("https://www.cases.org.uk/", "cases.org.uk", delay=3.0)

def fetch_sports_med_open_urls():
    # BUGFIX 2026-07-29: el dominio real lleva guión (sportsmedicineopen.
    # springeropen.com, sin guión, da 404 — no redirige a ningún lado).
    return _fetch_springer_journal_articles("sportsmedicine-open")

def fetch_jhk_journal_urls():
    # BUGFIX 2026-07-29: jhk.pl NO es el Journal of Human Kinetics — es una
    # marca de ropa deportiva polaca no relacionada (su sitemap real lista
    # "bluzy", "koszule", "kurtki"... = "hoodies", "shirts", "jackets").
    # Confirmado por búsqueda: la revista real vive en jhk.termedia.pl
    # (johk.pl es el sitio archivístico pero da SSL error). Se cambia de
    # sitemap-index a crawl directo (el journal no expone un sitemap propio
    # en termedia.pl). Verificado en vivo: 173 URLs.
    return _crawl_one_level("https://jhk.termedia.pl/", "jhk.termedia.pl", delay=1.0)

def fetch_ijes_journal_urls():
    return _crawl_one_level("https://ijes.info/", "ijes.info", delay=2.0)

def fetch_biology_of_sport_urls():
    # BUGFIX 2026-07-29: el ID de revista cambió (Biology_of_Sport-23 ->
    # Biology_of_Sport-78) Y el subsistema de sitemap.xml por-revista de
    # termedia.pl está caído (devuelve una página "przerwa techniczna" /
    # mantenimiento con HTTP 400 para CUALQUIER revista, no solo esta). La
    # página de la revista en sí carga bien, así que se hace crawl directo
    # en vez de depender del sitemap.
    return _crawl_one_level(
        "https://www.termedia.pl/Czasopismo/Biology_of_Sport-78",
        "termedia.pl", delay=1.0)

# Sección 3 — S&C aplicado
def fetch_altis_sprint_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://altis.world/digital-education/articles/ -> 86 URLs.
    return _crawl_one_level("https://altis.world/digital-education/articles/", "altis.world", delay=3.0)

def fetch_simplifaster_urls():
    return _fetch_sitemap_index_urls(
        "https://simplifaster.com/sitemap_index.xml",
        url_filter=lambda u: "/articles/" in u or "/blog/" in u, delay=1.5)

def fetch_ijsc_journal_urls():
    # Investigado 2026-07-29: ijsc-journal.com ya no resuelve (NXDOMAIN).
    # No se encontró dominio de reemplazo evidente para este journal.
    # Dejado como estaba — necesita más investigación.
    return _crawl_one_level("https://www.ijsc-journal.com/", "ijsc-journal.com", delay=2.0)

def fetch_sport_perf_reports_urls():
    # Investigado 2026-07-29: spr-journal.com ya no resuelve (NXDOMAIN). No
    # se encontró dominio de reemplazo evidente. Dejado como estaba —
    # necesita más investigación.
    return _crawl_one_level("https://spr-journal.com/", "spr-journal.com", delay=2.0)

def fetch_journal_trainology_urls():
    # BUGFIX 2026-07-29: trainology.org tiene un certificado TLS con
    # hostname mismatch (roto), pero el sitio responde bien en HTTP plano —
    # se usa ese esquema para evitar el error de verificación TLS.
    return _crawl_one_level("http://trainology.org/", "trainology.org", delay=2.0)

def fetch_stronger_by_science_urls():
    return _fetch_sitemap_index_urls(
        "https://www.strongerbyscience.com/sitemap_index.xml",
        url_filter=lambda u: any(k in u for k in ["/p/", "/article", "/blog"]), delay=1.5)

def fetch_sc_society_urls():
    # Investigado 2026-07-29: scsociety.org ya no resuelve (NXDOMAIN). No
    # se encontró dominio de reemplazo evidente (probado
    # strengthandconditioningsociety.org.uk y scscoach.org, ambos también
    # NXDOMAIN). Dejado como estaba — necesita más investigación.
    return _crawl_one_level("https://scsociety.org/resources/", "scsociety.org", delay=3.0)

def fetch_elitefts_edu_urls():
    # BUGFIX 2026-07-29: "www.elitefts.com/sitemap_index.xml" daba 404 — el
    # sitio ahora es Shopify y el sitemap real (sin "www") vive en
    # "elitefts.com/sitemap.xml". Además el filtro antiguo ("/education/" o
    # "/article") nunca coincidía con la estructura Shopify real
    # ("/blogs/<categoria>/<slug>"), por lo que el fetcher siempre devolvía 0.
    # El corpus completo de posts (11 sub-sitemaps de blog) suma ~27,500 URLs
    # — muy por encima de lo típico para una sola fuente aquí — así que se
    # acota a un máximo razonable.
    urls = _fetch_sitemap_index_urls(
        "https://elitefts.com/sitemap.xml",
        url_filter=lambda u: "/blogs/" in u and u.count("/") > 4, delay=1.5)
    return urls[:2000]

# Sección 4 — Nutrición deportiva extendida
def fetch_sports_dietitians_au_urls():
    # BUGFIX 2026-07-29: sportsdietitians.com.au/sitemap.xml es un sitemap
    # PLANO (<urlset>, 16 URLs reales) no un índice (<sitemapindex>) de
    # sub-sitemaps. _fetch_sitemap_index_urls() trataba cada una de esas 16
    # URLs de página como si fuera a su vez un sitemap XML — al no serlo,
    # el parseo fallaba en silencio para cada una (0 URLs, ~66s
    # desperdiciados en 16 requests con delay). Se usa fetch_urls_from_sitemap()
    # directamente, que sí maneja sitemaps planos.
    return fetch_urls_from_sitemap("https://www.sportsdietitians.com.au/sitemap.xml")

def fetch_athlete_triad_coalition_urls():
    # Investigado 2026-07-29: athletetriadcoalition.org ya no resuelve
    # (NXDOMAIN). Probado femaleathletetriad.org como posible sucesor,
    # también NXDOMAIN. No se encontró dominio de reemplazo. Dejado como
    # estaba — necesita más investigación.
    return _crawl_one_level("https://www.athletetriadcoalition.org/", "athletetriadcoalition.org", delay=3.0)

def fetch_ais_nutrition_recipes_urls():
    return _crawl_one_level("https://www.ais.gov.au/nutrition/recipes", "ais.gov.au", delay=2.0)

# Sección 5 — Psicología extendida
def fetch_frontiers_sport_psych_urls():
    return _fetch_sitemap_index_urls(
        "https://www.frontiersin.org/sitemap.xml",
        url_filter=lambda u: "psychology" in u and "sport" in u and "article" in u, delay=1.0)

def fetch_ncaa_mental_health_urls():
    return _crawl_one_level("https://www.ncaa.org/sports/2014/11/5/mental-health-best-practices.aspx", "ncaa.org", delay=3.0)

def fetch_ais_mental_health_urls():
    return _crawl_one_level("https://www.ais.gov.au/mental-health", "ais.gov.au", delay=2.0)

# Sección 6 — Biomecánica y análisis del movimiento
def fetch_isb_web_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://isbweb.org/news/news -> 67 URLs.
    return _crawl_one_level("https://isbweb.org/news/news", "isbweb.org", delay=3.0)

def fetch_opensim_urls():
    # BUGFIX 2026-07-29: "/support/" da 404, y aunque cargara, la
    # documentación de OpenSim se mudó por completo fuera del dominio
    # opensim.stanford.edu — la home solo enlaza a su nuevo wiki en
    # Confluence (opensimconfluence.atlassian.net), así que el
    # domain_prefix original nunca podía coincidir con nada tampoco.
    # Verificado en vivo: 44 URLs en el wiki nuevo.
    return _crawl_one_level("https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/overview",
                             "opensimconfluence.atlassian.net", delay=2.0)

def fetch_opencap_urls():
    return _crawl_one_level("https://www.opencap.ai/", "opencap.ai", delay=2.0)

def fetch_simtk_urls():
    # Investigado 2026-07-29: simtk.org da connect timeout consistente
    # (~15-30s, DNS resuelve pero el servidor no responde en el puerto
    # 443). No es un bloqueo WAF (no hay respuesta HTTP en absoluto).
    # Dejado como estaba — necesita más investigación o podría ser un
    # problema temporal del servidor.
    return _crawl_one_level("https://simtk.org/projects/", "simtk.org", delay=2.0)

def fetch_kinovea_urls():
    return _crawl_one_level("https://www.kinovea.org/", "kinovea.org", delay=2.0)

def fetch_visual3d_wiki_urls():
    # BUGFIX 2026-07-29: c-motion.com se rebrandeó y redirige a
    # has-motion.ca; el wiki real vive en el subdominio dedicado
    # wiki.has-motion.com (encontrado en el nav de la nueva home).
    # Verificado en vivo: 29 URLs.
    return _crawl_one_level("https://wiki.has-motion.com/doku.php?id=main_page",
                             "wiki.has-motion.com", delay=2.0)

def fetch_vicon_resources_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.vicon.com/news/blog/ -> 90 URLs.
    return _crawl_one_level("https://www.vicon.com/news/blog/", "vicon.com", delay=2.0)

def fetch_qualisys_resources_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.qualisys.com/life-sciences/sports-research/ -> 104 URLs.
    return _crawl_one_level("https://www.qualisys.com/life-sciences/sports-research/", "qualisys.com", delay=2.0)

# Sección 7 — Medicina deportiva extendida
def fetch_jat_journal_urls():
    # Investigado 2026-07-29: natajournals.org/sitemap.xml SÍ es un índice
    # válido (<sitemapindex>, 200 OK), pero tiene TRES niveles, no dos:
    # índice -> 2 sitemaps "de categoría" (content/static-pages) -> cientos
    # de sitemaps por mes/número (p.ej. ".../2006/01/ARTICLE-1.xml") -> ahí
    # sí viven las URLs de artículos reales. _fetch_sitemap_index_urls()
    # solo maneja dos niveles, así que el segundo nivel (URLs de MÁS
    # sitemaps, no de artículos) pasaba por el filtro tal cual — y como
    # esas URLs usan "ARTICLE" en mayúsculas, ni siquiera coincidían con el
    # filtro (case-sensitive), resultando en 0. Arreglarlo bien requiere un
    # crawler de sitemap de 3 niveles, fuera de alcance de este fix
    # puntual — dejado como estaba, necesita más investigación.
    return _fetch_sitemap_index_urls(
        "https://www.natajournals.org/sitemap.xml",
        url_filter=lambda u: "article" in u or "abstract" in u, delay=1.0)

def fetch_aspetar_journal_urls():
    # BUGFIX 2026-07-29: aspetarjournal.com ya no resuelve (dominio muerto).
    # El journal se mudó al subdominio journal.aspetar.com. Verificado en
    # vivo: 39 URLs.
    return _crawl_one_level("https://journal.aspetar.com/en/home", "journal.aspetar.com", delay=2.0)

def fetch_ojsm_journal_urls():
    return _crawl_one_level("https://journals.sagepub.com/toc/ojsc/current", "sagepub.com/toc/ojs", delay=2.0)

def fetch_cdc_heads_up_urls():
    return _crawl_one_level("https://www.cdc.gov/headsup/", "cdc.gov/headsup", delay=2.0)

def fetch_ifspt_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://ifspt.org/research/support-resources -> 57 URLs.
    return _crawl_one_level("https://ifspt.org/research/support-resources", "ifspt.org", delay=3.0)

def fetch_physiopedia_sports_urls():
    # Confirmado bloqueado por WAF a nivel de dominio (2026-07-29): la
    # homepage de physio-pedia.com también devuelve HTTP 403 (no es solo
    # esta página) — no evadir.
    return _crawl_one_level("https://www.physio-pedia.com/Sports_Medicine", "physio-pedia.com", delay=2.0)

# Sección 8 — Entrenamiento táctico y análisis de juego
def fetch_fifa_training_centre_urls():
    # BUGFIX 2026-07-29: training.fifa.com ya no resuelve (NXDOMAIN). El
    # contenido de entrenamiento/coaching de FIFA vive ahora en el dominio
    # dedicado fifatrainingcentre.com. Verificado en vivo: 47 URLs.
    return _crawl_one_level("https://www.fifatrainingcentre.com/en/", "fifatrainingcentre.com", delay=3.0)

def fetch_uefa_technical_reports_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.uefa.com/news-media/ -> 35 URLs.
    return _crawl_one_level("https://www.uefa.com/news-media/", "uefa.com", delay=3.0)

def fetch_statsbomb_opendata_urls():
    return _crawl_one_level("https://statsbomb.com/what-we-do/hub/free-data/", "statsbomb.com", delay=3.0)

def fetch_metrica_sports_urls():
    return _crawl_one_level("https://www.metrica-sports.com/resources/", "metrica-sports.com", delay=3.0)

def fetch_skillcorner_opendata_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://skillcorner.com/articles/skillcorner-releases-new-peak-velocity-metric?utm_source=sk_article -> 28 URLs.
    return _crawl_one_level("https://skillcorner.com/articles/skillcorner-releases-new-peak-velocity-metric?utm_source=sk_articles&utm_medium=news_banner", "skillcorner.com", delay=3.0)

def fetch_friends_of_tracking_urls():
    # AMBIGUO 2026-07-29: esta función está definida pero NUNCA se llama
    # desde get_all_urls() — pese a que el docstring del archivo (Sección
    # 8) sí lista "Friends of Tracking" como fuente esperada. Investigado:
    # (1) el handle "@Friendsoftracking" da 404 (probadas variantes de
    # capitalización, todas 404); (2) aunque el handle fuera correcto, las
    # páginas de canal de YouTube son una SPA renderizada en cliente — el
    # HTML estático no contiene los enlaces reales a videos, así que
    # BeautifulSoup no podría extraer nada útil de todos modos. No se
    # rewire a get_all_urls() porque añadiría una fuente que siempre
    # devuelve 0 — se deja fuera y documentado aquí para que el equipo
    # decida si vale la pena una fuente basada en la API de YouTube en su
    # lugar.
    return _crawl_one_level("https://www.youtube.com/@Friendsoftracking", "youtube.com", delay=3.0)

def fetch_kloppy_library_urls():
    return _crawl_one_level("https://kloppy.readthedocs.io/en/latest/", "kloppy.readthedocs.io", delay=2.0)

def fetch_socceraction_lib_urls():
    return _crawl_one_level("https://socceraction.readthedocs.io/en/latest/", "socceraction.readthedocs.io", delay=2.0)

def fetch_mit_sloan_analytics_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.sloansportsconference.com/about/mission-and-history -> 32 URLs.
    return _crawl_one_level("https://www.sloansportsconference.com/about/mission-and-history", "sloansportsconference.com", delay=3.0)

def fetch_fivb_coaches_resources_urls():
    return _crawl_one_level("https://www.fivb.com/en/volleyball/coaches", "fivb.com", delay=3.0)

# Sección 9 — Federaciones extendidas
def fetch_ifab_laws_urls():
    return _crawl_one_level("https://www.theifab.com/laws/", "theifab.com", delay=3.0)

def fetch_world_skate_urls():
    return _crawl_one_level("https://www.worldskate.org/", "worldskate.org", delay=3.0)

def fetch_immaf_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://immaf.org/about/history/ -> 30 URLs.
    return _crawl_one_level("https://immaf.org/about/history/", "immaf.org", delay=3.0)

def fetch_wbsc_baseball_urls():
    return _crawl_one_level("https://www.wbsc.org/news", "wbsc.org", delay=3.0)

def fetch_igf_golf_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.igfgolf.org/about/golf-for-athletes-with-a-disability/golf-for-athletes-with-a-disabilit -> 5 URLs.
    return _crawl_one_level("https://www.igfgolf.org/about/golf-for-athletes-with-a-disability/golf-for-athletes-with-a-disability-covered-competition", "igfgolf.org", delay=3.0)

def fetch_randa_golf_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.randa.org/about-us -> 18 URLs.
    return _crawl_one_level("https://www.randa.org/about-us", "randa.org", delay=3.0)

def fetch_world_triathlon_urls():
    return _crawl_one_level("https://www.triathlon.org/news", "triathlon.org", delay=3.0)

def fetch_fie_fencing_urls():
    # BUGFIX 2026-07-29: fie.ch ya no responde (connection refused). El
    # dominio real y en vivo es fie.org. Verificado en vivo: 54 URLs.
    return _crawl_one_level("https://fie.org/", "fie.org", delay=3.0)

def fetch_issf_shooting_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.issf-sports.org/news -> 34 URLs.
    return _crawl_one_level("https://www.issf-sports.org/news", "issf-sports.org", delay=3.0)

def fetch_iwf_weightlifting_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://iwf.sport/news-and-media/news/ -> 79 URLs.
    return _crawl_one_level("https://iwf.sport/news-and-media/news/", "iwf.sport", delay=3.0)

def fetch_uww_wrestling_urls():
    return _crawl_one_level("https://uww.org/news", "uww.org", delay=3.0)

def fetch_fih_hockey_urls():
    # BUGFIX 2026-07-29: fih.ch tiene un certificado TLS roto (falla
    # verificación de cadena). El dominio real y en vivo es fih.hockey.
    # Verificado en vivo: 75 URLs.
    return _crawl_one_level("https://www.fih.hockey/news", "fih.hockey", delay=3.0)

def fetch_iihf_icehockey_urls():
    return _crawl_one_level("https://www.iihf.com/iihf-home/the-iihf/hockey-development/", "iihf.com", delay=3.0)

def fetch_world_lacrosse_urls():
    return _crawl_one_level("https://worldlacrosse.sport/news/", "worldlacrosse.sport", delay=3.0)

def fetch_icc_cricket_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.icc-cricket.com/about/contact-us/social-media -> 63 URLs.
    return _crawl_one_level("https://www.icc-cricket.com/about/contact-us/social-media", "icc-cricket.com", delay=3.0)

def fetch_world_archery_urls():
    return _crawl_one_level("https://www.worldarchery.sport/news", "worldarchery.sport", delay=3.0)

def fetch_ittf_tabletennis_urls():
    return _crawl_one_level("https://www.ittf.com/coaching/", "ittf.com", delay=3.0)

def fetch_icf_canoe_urls():
    return _crawl_one_level("https://www.canoeicf.com/news", "canoeicf.com", delay=3.0)

def fetch_world_sailing_urls():
    return _crawl_one_level("https://www.sailing.org/news/", "sailing.org", delay=3.0)

def fetch_ifsc_climbing_urls():
    return _crawl_one_level("https://www.ifsc-climbing.org/", "ifsc-climbing.org", delay=3.0)

def fetch_isa_surfing_urls():
    return _crawl_one_level("https://www.isasurf.org/news/", "isasurf.org", delay=3.0)

def fetch_uipm_pentathlon_urls():
    return _crawl_one_level("https://www.uipmworld.org/news/", "uipmworld.org", delay=3.0)

# Sección 10 — Deportes paralímpicos
def fetch_ipc_paralympic_urls():
    return _crawl_one_level("https://www.paralympic.org/news", "paralympic.org", delay=3.0)

def fetch_world_para_athletics_urls():
    # BUGFIX 2026-07-29: worldparaathletics.org da SSL error
    # (TLSV1_UNRECOGNIZED_NAME) — el dominio dedicado se retiró; el
    # contenido vive ahora bajo paralympic.org. Verificado en vivo: 45 URLs.
    return _crawl_one_level("https://www.paralympic.org/athletics", "paralympic.org", delay=3.0)

def fetch_world_para_swimming_urls():
    # BUGFIX 2026-07-29: mismo caso que World Para Athletics — dominio
    # dedicado retirado, contenido bajo paralympic.org. 44 URLs.
    return _crawl_one_level("https://www.paralympic.org/swimming", "paralympic.org", delay=3.0)

def fetch_world_para_powerlifting_urls():
    # BUGFIX 2026-07-29: mismo caso — dominio dedicado retirado, contenido
    # bajo paralympic.org. 43 URLs.
    return _crawl_one_level("https://www.paralympic.org/powerlifting", "paralympic.org", delay=3.0)

def fetch_world_boccia_urls():
    return _crawl_one_level("https://www.bisfed.com/news/", "bisfed.com", delay=3.0)

def fetch_world_wheelchair_rugby_urls():
    # BUGFIX 2026-07-29: worldwheelchairrugby.org ya no resuelve. La
    # federación (antes IWRF) vive ahora en worldwheelchair.rugby.
    # Verificado en vivo: 38 URLs.
    return _crawl_one_level("https://worldwheelchair.rugby/", "worldwheelchair.rugby", delay=3.0)

def fetch_iwbf_wheelchair_basketball_urls():
    return _crawl_one_level("https://www.iwbf.org/news/", "iwbf.org", delay=3.0)

def fetch_ibsa_blind_sports_urls():
    return _crawl_one_level("https://www.ibsasport.org/sports/", "ibsasport.org", delay=3.0)

def fetch_virtus_sport_urls():
    return _crawl_one_level("https://virtus.sport/news/", "virtus.sport", delay=3.0)

def fetch_world_abilitysport_urls():
    return _crawl_one_level("https://www.worldabilitysport.org/", "worldabilitysport.org", delay=3.0)

def fetch_paravolley_urls():
    # BUGFIX 2026-07-29: paravolley.com expiró y ahora es una página de
    # dominio en venta (HugeDomains.com parking page, HTTP 200 pero sin
    # contenido real). La federación vive ahora en worldparavolley.org.
    return _crawl_one_level("https://worldparavolley.org/news/", "worldparavolley.org", delay=3.0)

def fetch_paralympics_australia_urls():
    return _crawl_one_level("https://www.paralympics.org.au/news/", "paralympics.org.au", delay=3.0)

def fetch_usopc_paralympic_urls():
    return _crawl_one_level("https://www.teamusa.org/us-paralympics", "teamusa.org", delay=3.0)

# Sección 11 — Desarrollo de entrenadores
def fetch_icce_coaching_urls():
    # BUGFIX 2026-07-29: icce-office.org ya no resuelve (NXDOMAIN); ICCE se
    # mudó a icce.ws. Verificado en vivo: 41 URLs.
    return _crawl_one_level("https://icce.ws/", "icce.ws", delay=3.0)

def fetch_uefa_coaching_convention_urls():
    # BUGFIX 2026-07-29: seed antiguo (football-development/coaching/) daba
    # 404. La sección "UEFA Coaching Convention" dedicada ya no parece
    # existir en el sitio actual; se usa el hub general de
    # football-development como sustituto más cercano (distinto del seed de
    # UEFA Technical Reports para no duplicar contenido). Verificado en
    # vivo: 42 URLs, aunque la mayoría no contendrán "football-development"
    # en el path, así que caerán al fallback genérico de folder_for_url()
    # en vez de DRIVE_UEFA_COACHING_CONVENTION_ID — limitación conocida, no
    # un bug silencioso.
    return _crawl_one_level("https://www.uefa.com/insideuefa/football-development/", "uefa.com", delay=3.0)

def fetch_conmebol_evolucion_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.conmebol.com/documentos/ -> 105 URLs.
    return _crawl_one_level("https://www.conmebol.com/documentos/", "conmebol.com", delay=3.0)

def fetch_england_football_public_urls():
    return _crawl_one_level("https://www.thefa.com/football-learning", "thefa.com", delay=3.0)

def fetch_uk_coaching_urls():
    return _crawl_one_level("https://www.ukcoaching.org/resources/", "ukcoaching.org", delay=3.0)

def fetch_coaching_assoc_canada_urls():
    # BUGFIX 2026-07-29: coachingassociation.ca ya no resuelve (NXDOMAIN);
    # se mudó a coach.ca. Verificado en vivo: 56 URLs.
    return _crawl_one_level("https://coach.ca/", "coach.ca", delay=3.0)

def fetch_sport_nz_coaching_urls():
    # BUGFIX 2026-07-29: seed antiguo ("/growing-sport/coaching/") da 404 —
    # no se encontró una sección de coaching dedicada equivalente en el
    # sitio actual (probadas varias rutas, todas 404). Se usa el hub
    # general de noticias como sustituto. Verificado en vivo: 553 URLs,
    # pero solo ~5 contienen "coaching" en el path, así que la mayoría
    # caerán a DRIVE_SPORT_NEW_ZEALAND_ID (fallback genérico) en vez de
    # DRIVE_SPORT_NZ_COACHING_ID — limitación conocida, no un bug
    # silencioso.
    return _crawl_one_level("https://www.sportnz.org.nz/about/news-and-media/", "sportnz.org.nz", delay=2.0)

def fetch_olympic_solidarity_urls():
    return _crawl_one_level("https://www.olympics.com/ioc/olympic-solidarity", "olympics.com", delay=3.0)

# Sección 12 — Tecnología deportiva
def fetch_polar_science_urls():
    return _crawl_one_level("https://www.polar.com/en/innovation/research", "polar.com", delay=3.0)

def fetch_garmin_health_science_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.garmin.com/es-MX/blog/category/press-release/ -> 168 URLs.
    return _crawl_one_level("https://www.garmin.com/es-MX/blog/category/press-release/", "garmin.com", delay=3.0)

def fetch_firstbeat_science_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.firstbeat.com/en/firstbeat-press-media/ -> 54 URLs.
    return _crawl_one_level("https://www.firstbeat.com/en/firstbeat-press-media/", "firstbeat.com", delay=3.0)

def fetch_vald_performance_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.valdperformance.com/news -> 20 URLs.
    return _crawl_one_level("https://www.valdperformance.com/news", "valdperformance.com", delay=3.0)

def fetch_statsports_resources_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://statsports.com/about -> 24 URLs.
    return _crawl_one_level("https://statsports.com/about", "statsports.com", delay=3.0)

def fetch_kinexon_sports_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://kinexon.com/resources/blog -> 65 URLs.
    return _crawl_one_level("https://kinexon.com/resources/blog", "kinexon.com", delay=3.0)

def fetch_kubios_hrv_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.kubios.com/blog/about-physiological-age/ -> 31 URLs.
    return _crawl_one_level("https://www.kubios.com/blog/about-physiological-age/", "kubios.com", delay=3.0)

def fetch_hrv4training_urls():
    return _crawl_one_level("https://www.hrv4training.com/blog", "hrv4training.com", delay=3.0)

def fetch_hawkin_dynamics_urls():
    return _crawl_one_level("https://www.hawkindynamics.com/blog/", "hawkindynamics.com", delay=3.0)

def fetch_delsys_knowledge_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://delsys.com/news/ -> 159 URLs.
    return _crawl_one_level("https://delsys.com/news/", "delsys.com", delay=3.0)

def fetch_noraxon_resources_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.noraxon.com/research-education -> 44 URLs.
    return _crawl_one_level("https://www.noraxon.com/research-education", "noraxon.com", delay=3.0)

def fetch_cosmed_knowledge_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.cosmed.com/en/resources/science -> 73 URLs.
    return _crawl_one_level("https://www.cosmed.com/en/resources/science", "cosmed.com", delay=3.0)

def fetch_neurokit2_urls():
    # BUGFIX 2026-07-29: "readthedocs.io/en/stable/" y "/en/latest/" dan 404
    # (esa versión ya no existe en RTD); "/en/legacy_docs/" sí carga pero
    # solo enlaza afuera a la doc real, que se mudó a GitHub Pages.
    # Verificado en vivo: 61 URLs.
    return _crawl_one_level("https://neuropsychology.github.io/NeuroKit/", "neuropsychology.github.io", delay=2.0)

def fetch_biosppy_urls():
    return _crawl_one_level("https://biosppy.readthedocs.io/en/stable/", "biosppy.readthedocs.io", delay=2.0)

def fetch_goldencheetah_urls():
    return _crawl_one_level("https://www.goldencheetah.org/", "goldencheetah.org", delay=2.0)

def fetch_athletemonitoring_urls():
    return _crawl_one_level("https://www.athletemonitoring.com/blog/", "athletemonitoring.com", delay=3.0)

def fetch_trainingpeaks_coach_urls():
    # BUGFIX 2026-07-29: el filtro "/coach/" en url capturaba ~4,725 páginas
    # de perfil de coaches del marketplace (p.ej. /coach/jesse-moore) —
    # directorios de perfil de bajo contenido, no artículos — de un total de
    # 5,386 URLs (>3000, señal de alerta). Solo ~661 eran artículos reales
    # de /coach-blog/. Se acota al blog, que es el contenido educativo real.
    return _fetch_sitemap_index_urls(
        "https://www.trainingpeaks.com/sitemap.xml",
        url_filter=lambda u: "/coach-blog/" in u, delay=1.5)

# Sección 13 — Institutos nacionales extendidos
def fetch_uksi_institute_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://uksportsinstitute.co.uk/news/ -> 92 URLs.
    return _crawl_one_level("https://uksportsinstitute.co.uk/news/", "uksportsinstitute.co.uk", delay=3.0)

def fetch_insep_france_urls():
    return _crawl_one_level("https://www.insep.fr/en/research/publications/", "insep.fr", delay=3.0)

def fetch_insep_openedition_urls():
    return _crawl_one_level("https://journals.openedition.org/insep/", "openedition.org/insep", delay=2.0)

def fetch_inefc_catalonia_urls():
    # BUGFIX 2026-07-29: inefc.cat tiene un certificado TLS con hostname
    # mismatch (roto). El sitio real vive en el subdominio del gobierno
    # catalán inefc.gencat.cat. Verificado en vivo: 110 URLs.
    return _crawl_one_level("https://inefc.gencat.cat/ca/inici", "inefc.gencat.cat", delay=3.0)

def fetch_aspetar_institute_urls():
    return _crawl_one_level("https://www.aspetar.com/research/publications/", "aspetar.com", delay=3.0)

def fetch_copsin_canada_urls():
    # BUGFIX 2026-07-29: "/resources/" da 404 (sitio de una sola página con
    # anclas internas, sin subpáginas). Se usa la home, que sí trae
    # documentos reales (PDFs). Verificado en vivo: 17 URLs.
    return _crawl_one_level("https://copsin.ca/", "copsin.ca", delay=3.0)

def fetch_csi_pacific_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.csipacific.ca/press-releases/csi-pacific-and-viasport-welcome-blast-media-print-as-progr -> 54 URLs.
    return _crawl_one_level("https://www.csipacific.ca/press-releases/csi-pacific-and-viasport-welcome-blast-media-print-as-program-supporter-sponsor-of-the-bc-athlete-ambassador-program/", "csipacific.ca", delay=3.0)

def fetch_hpsnz_urls():
    return _crawl_one_level("https://www.hpsnz.org.nz/insights/", "hpsnz.org.nz", delay=3.0)

def fetch_jiss_japan_urls():
    # BUGFIX 2026-07-29: jiss.naash.go.jp ya no resuelve (NXDOMAIN). JISS
    # (Japan Institute of Sports Sciences) se reorganizó como HPSC (High
    # Performance Sport Center) bajo Japan Sport Council, en
    # jpnsport.go.jp/hpsc/ (confirmado por el <title> de la página: "ハイパ
    # フォーマンススポーツセンター | 日本スポーツ振興センター"). Verificado
    # en vivo: 46 URLs.
    return _crawl_one_level("https://www.jpnsport.go.jp/hpsc/", "jpnsport.go.jp", delay=3.0)

def fetch_singapore_sport_inst_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.sportsingapore.gov.sg/sport-education/about/ -> 15 URLs.
    return _crawl_one_level("https://www.sportsingapore.gov.sg/sport-education/about/", "sportsingapore.gov.sg", delay=3.0)

def fetch_kiss_korea_urls():
    # Investigado 2026-07-29: kiss.kspo.or.kr ya no resuelve (NXDOMAIN).
    # Probado sports.re.kr (404) y eng.sports.re.kr (NXDOMAIN) como
    # posibles sucesores, sin éxito. Dejado como estaba — necesita más
    # investigación.
    return _crawl_one_level("https://kiss.kspo.or.kr/", "kiss.kspo.or.kr", delay=3.0)

def fetch_sport_ireland_inst_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://www.sportireland.ie/about-us/publications/annual-reports -> 75 URLs.
    return _crawl_one_level("https://www.sportireland.ie/about-us/publications/annual-reports", "sportireland.ie", delay=3.0)

def fetch_olympiatoppen_norway_urls():
    # Investigado 2026-07-29: olympiatoppen.no tiene un certificado TLS
    # roto (missing issuer cert) y tampoco responde en HTTP plano
    # (connection refused). No se encontró dominio alternativo. Dejado
    # como estaba — necesita más investigación o esperar a que renueven su
    # certificado.
    return _crawl_one_level("https://www.olympiatoppen.no/", "olympiatoppen.no", delay=3.0)

def fetch_bisp_germany_urls():
    # BUGFIX 2026-07-29: "/EN/publications/" da 404. La home usa enlaces
    # relativos tipo "EN/Home/home_node.html" (sin "/" inicial) — con seed
    # "https://www.bisp.de/EN/" (con barra final) esto resolvía mal a un
    # path duplicado "EN/EN/..." (404); usando "https://www.bisp.de/EN"
    # (sin barra final) urljoin() resuelve correctamente. Verificado en
    # vivo: 42 URLs.
    return _crawl_one_level("https://www.bisp.de/EN", "bisp.de", delay=3.0)

def fetch_sfism_switzerland_urls():
    return _crawl_one_level("https://www.sfism.ch/en/research/", "sfism.ch", delay=3.0)

# Sección 14 — Bases de datos OA y repositorios
def fetch_crossref_sport_urls():
    try:
        r = requests.get(
            "https://api.crossref.org/works",
            params={"query": "sports training performance", "rows": 100},
            headers=HEADERS, timeout=30)
        items = r.json().get("message", {}).get("items", [])
        urls = []
        for it in items:
            doi = it.get("DOI", "")
            title = (it.get("title") or [""])[0]
            urls.append(f"https://doi.org/{doi}|CROSSREF|{json.dumps({'title': title, 'doi': doi})}")
        return urls
    except Exception:
        return []

def fetch_doaj_sport_urls():
    # Confirmado bloqueado por WAF a nivel de API (2026-07-29): doaj.org
    # devuelve 403 Forbidden (nginx) en este endpoint — no evadir.
    try:
        r = requests.get(
            "https://doaj.org/api/search/articles/sports+science",
            params={"pageSize": 100},
            headers=HEADERS, timeout=30)
        results = r.json().get("results", [])
        urls = []
        for it in results:
            doi = it.get("bibjson", {}).get("identifier", [{}])[0].get("id", "")
            title = it.get("bibjson", {}).get("title", "")
            urls.append(f"https://doaj.org/article/{it.get('id','')}|DOAJ|{json.dumps({'title': title, 'doi': doi})}")
        return urls
    except Exception:
        return []

def fetch_zenodo_sport_urls():
    try:
        r = requests.get(
            "https://zenodo.org/api/records/",
            # BUGFIX 2026-07-29: size=100 devolvía 400 Bad Request — la API
            # de Zenodo limita "size" a 25 para requests sin autenticar.
            params={"q": "sports training exercise", "size": 25},
            headers=HEADERS, timeout=30)
        hits = r.json().get("hits", {}).get("hits", [])
        urls = []
        for h in hits:
            doi = h.get("doi", "")
            title = h.get("metadata", {}).get("title", "")
            urls.append(f"https://zenodo.org/record/{h.get('id','')}|ZENODO|{json.dumps({'title': title, 'doi': doi})}")
        return urls
    except Exception:
        return []

def fetch_semantic_scholar_sport_urls():
    # NOTA 2026-07-29: la API pública de Semantic Scholar sin API key tiene
    # un rate limit muy estricto (429 "Too Many Requests" observado en
    # pruebas) — no se intenta evadir con reintentos agresivos ni API key.
    # Si esto se vuelve recurrente en producción, considerar solicitar una
    # key oficial (ver mensaje de error) en vez de forzar el límite.
    try:
        r = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params={"query": "sports training athletic performance", "limit": 100,
                    "fields": "title,externalIds,year"},
            headers=HEADERS, timeout=30)
        papers = r.json().get("data", [])
        urls = []
        for p in papers:
            title = p.get("title", "")
            doi = p.get("externalIds", {}).get("DOI", "")
            pid = p.get("paperId", "")
            urls.append(f"https://www.semanticscholar.org/paper/{pid}|S2|{json.dumps({'title': title, 'doi': doi})}")
        return urls
    except Exception:
        return []

def fetch_sportrxiv_urls():
    try:
        # BUGFIX 2026-07-29: "osf.io/api/v2/..." devuelve el HTML del
        # frontend de OSF (200 pero sin JSON) — la API real vive en el
        # subdominio dedicado "api.osf.io".
        r = requests.get("https://api.osf.io/v2/preprints/",
            params={"filter[provider]": "sportrxiv", "page[size]": 100},
            headers=HEADERS, timeout=30)
        data = r.json().get("data", [])
        urls = []
        for item in data:
            attrs = item.get("attributes", {})
            title = attrs.get("title", "")
            doi = attrs.get("doi", "")
            pid = item.get("id", "")
            urls.append(f"https://osf.io/preprints/sportrxiv/{pid}|SPORTRXIV|{json.dumps({'title': title, 'doi': doi})}")
        return urls
    except Exception:
        return []

def fetch_la84_digital_library_urls():
    # BUGFIX 2026-07-29: seed antiguo daba 404/400 (sitio reestructurado).
    # Verificado en vivo: https://la84.org/news-and-events -> 18 URLs.
    return _crawl_one_level("https://la84.org/news-and-events", "la84.org", delay=2.0)

def fetch_olympic_world_library_urls():
    return _crawl_one_level("https://library.olympics.com/Default/search.aspx", "library.olympics.com", delay=2.0)

def fetch_ncaa_research_urls():
    return _crawl_one_level("https://www.ncaa.org/sports/2013/11/1/research.aspx", "ncaa.org", delay=3.0)


def extract_inline_content_deporte(inline_str):
    """Convierte registro inline API a texto legible."""
    try:
        url_part, rtype, json_str = inline_str.split("|", 2)
        data = json.loads(json_str)
        title = data.get("title", "Untitled")
        doi = data.get("doi", "")
        return f"{title}\n{'='*len(title)}\n\nURL: {url_part}\nDOI: {doi}\nType: {rtype}\n"
    except Exception:
        return inline_str


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
            print(f"  → {len(found)} URLs", flush=True)
            urls.extend(found)
        except Exception as e:
            print(f"  ERROR: {e}", flush=True)
    return urls


def get_all_urls():
    all_urls = []

    # A. Antidopaje e IOC
    all_urls += _load_source("IOC Olympics",            fn=fetch_ioc_urls)
    all_urls += _load_source("WADA Antidoping",         fn=fetch_wada_urls)
    all_urls += _load_source("USADA",                   fn=fetch_usada_urls)
    all_urls += _load_source("UKAD",                    fn=fetch_ukad_urls)
    all_urls += _load_source("Global DRO",              fn=fetch_global_dro_urls)

    # B. Federaciones internacionales
    all_urls += _load_source("World Athletics",         fn=fetch_world_athletics_urls)
    all_urls += _load_source("FIFA Football",           fn=fetch_fifa_urls)
    all_urls += _load_source("FIBA Basketball",         fn=fetch_fiba_urls)
    all_urls += _load_source("FIVB Volleyball",         fn=fetch_fivb_urls)
    all_urls += _load_source("World Aquatics",          fn=fetch_world_aquatics_urls)
    all_urls += _load_source("UCI Cycling",             fn=fetch_uci_urls)
    all_urls += _load_source("ITF Tennis",              fn=fetch_itf_urls)
    all_urls += _load_source("World Rugby",             fn=fetch_world_rugby_urls)
    all_urls += _load_source("IHF Handball",            fn=fetch_ihf_urls)
    all_urls += _load_source("BWF Badminton",           fn=fetch_bwf_urls)
    all_urls += _load_source("World Taekwondo",         fn=fetch_world_taekwondo_urls)
    all_urls += _load_source("IJF Judo",                fn=fetch_ijf_urls)
    all_urls += _load_source("ISU Skating",             fn=fetch_isu_urls)
    all_urls += _load_source("FIS Skiing",              fn=fetch_fis_urls)
    all_urls += _load_source("World Rowing",            fn=fetch_world_rowing_urls)
    all_urls += _load_source("World Gymnastics",        fn=fetch_world_gymnastics_urls)
    all_urls += _load_source("World Boxing",            fn=fetch_world_boxing_urls)

    # C. Ciencias del deporte
    all_urls += _load_source("ACSM",                    fn=fetch_acsm_urls)
    all_urls += _load_source("NSCA",                    fn=fetch_nsca_urls)
    all_urls += _load_source("ECSS",                    fn=fetch_ecss_urls)
    all_urls += _load_source("BASES UK",                fn=fetch_bases_uk_urls)
    all_urls += _load_source("ASCA Australia",          fn=fetch_asca_au_urls)
    all_urls += _load_source("UKSCA",                   fn=fetch_uksca_urls)
    all_urls += _load_source("CONADE Mexico",           fn=fetch_conade_urls)
    all_urls += _load_source("Sport Australia Clearinghouse", fn=fetch_sport_australia_clearinghouse_urls)
    all_urls += _load_source("UK Sport",                fn=fetch_uk_sport_urls)
    all_urls += _load_source("USOPC Resources",         fn=fetch_usopc_urls)

    # D. Medicina deportiva
    all_urls += _load_source("FIMS",                    fn=fetch_fims_urls)
    all_urls += _load_source("AMSSM",                   fn=fetch_amssm_urls)
    all_urls += _load_source("AOSSM",                   fn=fetch_aossm_urls)
    all_urls += _load_source("ESSKA",                   fn=fetch_esska_urls)
    all_urls += _load_source("BJSM",                    fn=fetch_bjsm_urls)
    all_urls += _load_source("Sports Health Journal",   fn=fetch_sports_health_urls)
    all_urls += _load_source("NATA Athletic Training",  fn=fetch_nata_urls)

    # E. Nutrición deportiva
    all_urls += _load_source("ISSN Nutrition",          fn=fetch_issn_nutrition_urls)
    all_urls += _load_source("AIS Nutrition",           fn=fetch_ais_nutrition_urls)
    all_urls += _load_source("GSSI / Gatorade",         fn=fetch_gssi_urls)
    all_urls += _load_source("SCAN Dietitians",         fn=fetch_scan_urls)
    all_urls += _load_source("IOC Nutrition",           fn=fetch_ioc_nutrition_urls)

    # F. Psicología del deporte
    all_urls += _load_source("AASP Psychology",         fn=fetch_aasp_urls)
    all_urls += _load_source("ISSP Psychology",         fn=fetch_issp_urls)
    all_urls += _load_source("FEPSAC Europe",           fn=fetch_fepsac_urls)

    # G. Fuerza y biomecánica
    all_urls += _load_source("ISBS Biomechanics",       fn=fetch_isbs_urls)
    all_urls += _load_source("Catapult Resources",      fn=fetch_catapult_urls)

    # H. Revistas OA
    all_urls += _load_source("JSSM",                    fn=fetch_jssm_urls)
    all_urls += _load_source("Sports MDPI",             fn=fetch_sports_mdpi_urls)
    all_urls += _load_source("Frontiers Sports",        fn=fetch_frontiers_sports_urls)
    all_urls += _load_source("BMC Sports Sci",          fn=fetch_bmc_sports_sci_urls)
    all_urls += _load_source("PeerJ Sports",            fn=fetch_peerj_sports_urls)
    all_urls += _load_source("Translational Sports Med",fn=fetch_translational_sports_med_urls)

    # I. Institutos de élite
    all_urls += _load_source("AIS Australia",           fn=fetch_ais_australia_urls)
    all_urls += _load_source("INEF Spain",              fn=fetch_inef_spain_urls)
    all_urls += _load_source("Aspire Qatar",            fn=fetch_aspire_qatar_urls)
    all_urls += _load_source("Canadian Sport Institute",fn=fetch_canadian_sport_institute_urls)
    all_urls += _load_source("Sport New Zealand",       fn=fetch_sport_nz_urls)

    # J. Bases de datos y recursos educativos
    all_urls += _load_source("SIRC Canada",             fn=fetch_sirc_urls)
    all_urls += _load_source("PubMed Sports Medicine",  fn=fetch_pubmed_sports_urls)
    all_urls += _load_source("Coach Education (ICCE)",  fn=fetch_coach_education_urls)

    # ── NUEVAS SECCIONES — Inventario Maestro 2026-07-25 ──────────────────────

    # Sección 1 — Antidopaje extendido
    all_urls += _load_source("ITA Sport",               fn=fetch_ita_sport_urls)
    all_urls += _load_source("INADO",                   fn=fetch_inado_urls)
    all_urls += _load_source("CCES Canada",             fn=fetch_cces_canada_urls)
    all_urls += _load_source("NADA Germany",            fn=fetch_nada_germany_urls)
    all_urls += _load_source("AFLD France",             fn=fetch_afld_france_urls)
    all_urls += _load_source("CELAD Spain",             fn=fetch_celad_spain_urls)
    all_urls += _load_source("JADA Japan",              fn=fetch_jada_japan_urls)
    all_urls += _load_source("SAIDS Africa",            fn=fetch_saids_africa_urls)
    all_urls += _load_source("ABCD Brazil",             fn=fetch_abcd_brazil_urls)
    all_urls += _load_source("WADA RADOS",              fn=fetch_wada_rados_urls)

    # Sección 2 — Fisiología extendida
    all_urls += _load_source("CASES UK",                fn=fetch_cases_uk_urls)
    all_urls += _load_source("Sports Med Open",         fn=fetch_sports_med_open_urls)
    all_urls += _load_source("JHK Journal",             fn=fetch_jhk_journal_urls)
    all_urls += _load_source("IJES Journal",            fn=fetch_ijes_journal_urls)
    all_urls += _load_source("Biology of Sport",        fn=fetch_biology_of_sport_urls)

    # Sección 3 — S&C aplicado
    all_urls += _load_source("ALTIS Sprint",            fn=fetch_altis_sprint_urls)
    all_urls += _load_source("SimpliFaster",            fn=fetch_simplifaster_urls)
    all_urls += _load_source("IJSC Journal",            fn=fetch_ijsc_journal_urls)
    all_urls += _load_source("Sport Perf Reports",      fn=fetch_sport_perf_reports_urls)
    all_urls += _load_source("Journal Trainology",      fn=fetch_journal_trainology_urls)
    all_urls += _load_source("Stronger by Science",     fn=fetch_stronger_by_science_urls)
    all_urls += _load_source("S&C Society",             fn=fetch_sc_society_urls)
    all_urls += _load_source("EliteFTS Education",      fn=fetch_elitefts_edu_urls)

    # Sección 4 — Nutrición deportiva extendida
    all_urls += _load_source("Sports Dietitians AU",    fn=fetch_sports_dietitians_au_urls)
    all_urls += _load_source("Athlete Triad Coalition", fn=fetch_athlete_triad_coalition_urls)
    all_urls += _load_source("AIS Nutrition Recipes",   fn=fetch_ais_nutrition_recipes_urls)

    # Sección 5 — Psicología extendida
    all_urls += _load_source("Frontiers Sport Psych",   fn=fetch_frontiers_sport_psych_urls)
    all_urls += _load_source("NCAA Mental Health",      fn=fetch_ncaa_mental_health_urls)
    all_urls += _load_source("AIS Mental Health",       fn=fetch_ais_mental_health_urls)

    # Sección 6 — Biomecánica y análisis del movimiento
    all_urls += _load_source("ISB Web",                 fn=fetch_isb_web_urls)
    all_urls += _load_source("OpenSim",                 fn=fetch_opensim_urls)
    all_urls += _load_source("OpenCap",                 fn=fetch_opencap_urls)
    all_urls += _load_source("SimTK",                   fn=fetch_simtk_urls)
    all_urls += _load_source("Kinovea",                 fn=fetch_kinovea_urls)
    all_urls += _load_source("Visual3D Wiki",           fn=fetch_visual3d_wiki_urls)
    all_urls += _load_source("Vicon Resources",         fn=fetch_vicon_resources_urls)
    all_urls += _load_source("Qualisys Resources",      fn=fetch_qualisys_resources_urls)

    # Sección 7 — Medicina deportiva extendida
    all_urls += _load_source("JAT Journal",             fn=fetch_jat_journal_urls)
    all_urls += _load_source("Aspetar Journal",         fn=fetch_aspetar_journal_urls)
    all_urls += _load_source("OJSM Journal",            fn=fetch_ojsm_journal_urls)
    all_urls += _load_source("CDC HEADS UP",            fn=fetch_cdc_heads_up_urls)
    all_urls += _load_source("IFSPT",                   fn=fetch_ifspt_urls)
    all_urls += _load_source("Physiopedia Sports",      fn=fetch_physiopedia_sports_urls)

    # Sección 8 — Entrenamiento táctico y análisis de juego
    all_urls += _load_source("FIFA Training Centre",    fn=fetch_fifa_training_centre_urls)
    all_urls += _load_source("UEFA Technical Reports",  fn=fetch_uefa_technical_reports_urls)
    all_urls += _load_source("StatsBomb OpenData",      fn=fetch_statsbomb_opendata_urls)
    all_urls += _load_source("Metrica Sports",          fn=fetch_metrica_sports_urls)
    all_urls += _load_source("SkillCorner OpenData",    fn=fetch_skillcorner_opendata_urls)
    all_urls += _load_source("Kloppy Library",          fn=fetch_kloppy_library_urls)
    all_urls += _load_source("socceraction lib",        fn=fetch_socceraction_lib_urls)
    all_urls += _load_source("MIT Sloan Analytics",     fn=fetch_mit_sloan_analytics_urls)
    all_urls += _load_source("FIVB Coaches Resources",  fn=fetch_fivb_coaches_resources_urls)

    # Sección 9 — Federaciones extendidas
    all_urls += _load_source("IFAB Laws",               fn=fetch_ifab_laws_urls)
    all_urls += _load_source("World Skate",             fn=fetch_world_skate_urls)
    all_urls += _load_source("IMMAF",                   fn=fetch_immaf_urls)
    all_urls += _load_source("WBSC Baseball",           fn=fetch_wbsc_baseball_urls)
    all_urls += _load_source("IGF Golf",                fn=fetch_igf_golf_urls)
    all_urls += _load_source("R&A Golf",                fn=fetch_randa_golf_urls)
    all_urls += _load_source("World Triathlon",         fn=fetch_world_triathlon_urls)
    all_urls += _load_source("FIE Fencing",             fn=fetch_fie_fencing_urls)
    all_urls += _load_source("ISSF Shooting",           fn=fetch_issf_shooting_urls)
    all_urls += _load_source("IWF Weightlifting",       fn=fetch_iwf_weightlifting_urls)
    all_urls += _load_source("UWW Wrestling",           fn=fetch_uww_wrestling_urls)
    all_urls += _load_source("FIH Hockey",              fn=fetch_fih_hockey_urls)
    all_urls += _load_source("IIHF Ice Hockey",         fn=fetch_iihf_icehockey_urls)
    all_urls += _load_source("World Lacrosse",          fn=fetch_world_lacrosse_urls)
    all_urls += _load_source("ICC Cricket",             fn=fetch_icc_cricket_urls)
    all_urls += _load_source("World Archery",           fn=fetch_world_archery_urls)
    all_urls += _load_source("ITTF Table Tennis",       fn=fetch_ittf_tabletennis_urls)
    all_urls += _load_source("ICF Canoe",               fn=fetch_icf_canoe_urls)
    all_urls += _load_source("World Sailing",           fn=fetch_world_sailing_urls)
    all_urls += _load_source("IFSC Climbing",           fn=fetch_ifsc_climbing_urls)
    all_urls += _load_source("ISA Surfing",             fn=fetch_isa_surfing_urls)
    all_urls += _load_source("UIPM Pentathlon",         fn=fetch_uipm_pentathlon_urls)

    # Sección 10 — Deportes paralímpicos
    all_urls += _load_source("IPC Paralympic",          fn=fetch_ipc_paralympic_urls)
    all_urls += _load_source("World Para Athletics",    fn=fetch_world_para_athletics_urls)
    all_urls += _load_source("World Para Swimming",     fn=fetch_world_para_swimming_urls)
    all_urls += _load_source("World Para Powerlifting", fn=fetch_world_para_powerlifting_urls)
    all_urls += _load_source("World Boccia",            fn=fetch_world_boccia_urls)
    all_urls += _load_source("World Wheelchair Rugby",  fn=fetch_world_wheelchair_rugby_urls)
    all_urls += _load_source("IWBF Wheelchair Basketball", fn=fetch_iwbf_wheelchair_basketball_urls)
    all_urls += _load_source("IBSA Blind Sports",       fn=fetch_ibsa_blind_sports_urls)
    all_urls += _load_source("Virtus Sport",            fn=fetch_virtus_sport_urls)
    all_urls += _load_source("WorldAbilitySport",       fn=fetch_world_abilitysport_urls)
    all_urls += _load_source("ParaVolley",              fn=fetch_paravolley_urls)
    all_urls += _load_source("Paralympics Australia",   fn=fetch_paralympics_australia_urls)
    all_urls += _load_source("USOPC Paralympic",        fn=fetch_usopc_paralympic_urls)

    # Sección 11 — Desarrollo de entrenadores
    all_urls += _load_source("ICCE Coaching",           fn=fetch_icce_coaching_urls)
    all_urls += _load_source("UEFA Coaching Convention",fn=fetch_uefa_coaching_convention_urls)
    all_urls += _load_source("CONMEBOL Evolución",      fn=fetch_conmebol_evolucion_urls)
    all_urls += _load_source("England Football Learning",fn=fetch_england_football_public_urls)
    all_urls += _load_source("UK Coaching",             fn=fetch_uk_coaching_urls)
    all_urls += _load_source("Coaching Assoc Canada",   fn=fetch_coaching_assoc_canada_urls)
    all_urls += _load_source("Sport NZ Coaching",       fn=fetch_sport_nz_coaching_urls)
    all_urls += _load_source("Olympic Solidarity",      fn=fetch_olympic_solidarity_urls)

    # Sección 12 — Tecnología deportiva
    all_urls += _load_source("Polar Science",           fn=fetch_polar_science_urls)
    all_urls += _load_source("Garmin Health Science",   fn=fetch_garmin_health_science_urls)
    all_urls += _load_source("Firstbeat Science",       fn=fetch_firstbeat_science_urls)
    all_urls += _load_source("VALD Performance",        fn=fetch_vald_performance_urls)
    all_urls += _load_source("STATSports Resources",    fn=fetch_statsports_resources_urls)
    all_urls += _load_source("KINEXON Sports",          fn=fetch_kinexon_sports_urls)
    all_urls += _load_source("Kubios HRV",              fn=fetch_kubios_hrv_urls)
    all_urls += _load_source("HRV4Training",            fn=fetch_hrv4training_urls)
    all_urls += _load_source("Hawkin Dynamics",         fn=fetch_hawkin_dynamics_urls)
    all_urls += _load_source("Delsys Knowledge",        fn=fetch_delsys_knowledge_urls)
    all_urls += _load_source("Noraxon Resources",       fn=fetch_noraxon_resources_urls)
    all_urls += _load_source("COSMED Knowledge",        fn=fetch_cosmed_knowledge_urls)
    all_urls += _load_source("NeuroKit2",               fn=fetch_neurokit2_urls)
    all_urls += _load_source("BioPPy",                  fn=fetch_biosppy_urls)
    all_urls += _load_source("GoldenCheetah",           fn=fetch_goldencheetah_urls)
    all_urls += _load_source("AthleteMonitoring",       fn=fetch_athletemonitoring_urls)
    all_urls += _load_source("TrainingPeaks Coach",     fn=fetch_trainingpeaks_coach_urls)

    # Sección 13 — Institutos nacionales extendidos
    all_urls += _load_source("UKSI Institute",          fn=fetch_uksi_institute_urls)
    all_urls += _load_source("INSEP France",            fn=fetch_insep_france_urls)
    all_urls += _load_source("INSEP OpenEdition",       fn=fetch_insep_openedition_urls)
    all_urls += _load_source("INEFC Catalonia",         fn=fetch_inefc_catalonia_urls)
    all_urls += _load_source("Aspetar Institute",       fn=fetch_aspetar_institute_urls)
    all_urls += _load_source("COPSIN Canada",           fn=fetch_copsin_canada_urls)
    all_urls += _load_source("CSI Pacific",             fn=fetch_csi_pacific_urls)
    all_urls += _load_source("HPSNZ",                   fn=fetch_hpsnz_urls)
    all_urls += _load_source("JISS Japan",              fn=fetch_jiss_japan_urls)
    all_urls += _load_source("Singapore Sport Inst",    fn=fetch_singapore_sport_inst_urls)
    all_urls += _load_source("KISS Korea",              fn=fetch_kiss_korea_urls)
    all_urls += _load_source("Sport Ireland Inst",      fn=fetch_sport_ireland_inst_urls)
    all_urls += _load_source("Olympiatoppen Norway",    fn=fetch_olympiatoppen_norway_urls)
    all_urls += _load_source("BISp Germany",            fn=fetch_bisp_germany_urls)
    all_urls += _load_source("SFISM Switzerland",       fn=fetch_sfism_switzerland_urls)

    # Sección 14 — Bases de datos OA y repositorios
    all_urls += _load_source("Crossref Sport",          fn=fetch_crossref_sport_urls)
    all_urls += _load_source("DOAJ Sport",              fn=fetch_doaj_sport_urls)
    all_urls += _load_source("Zenodo Sport",            fn=fetch_zenodo_sport_urls)
    all_urls += _load_source("Semantic Scholar Sport",  fn=fetch_semantic_scholar_sport_urls)
    all_urls += _load_source("SportRxiv",               fn=fetch_sportrxiv_urls)
    all_urls += _load_source("LA84 Digital Library",    fn=fetch_la84_digital_library_urls)
    all_urls += _load_source("Olympic World Library",   fn=fetch_olympic_world_library_urls)
    all_urls += _load_source("NCAA Research",           fn=fetch_ncaa_research_urls)

    print(f"\nTotal URLs objetivo: {len(all_urls)}", flush=True)
    return all_urls


# ── Scraping ───────────────────────────────────────────────────────────────────

def delay_for_url(url):
    if any(d in url for d in ["wada-ama.org", "usada.org", "fifa.com", "uci.org",
                               "worldathletics.org", "world.rugby", "theifab.com",
                               "iihf.com", "iwf.sport", "worldparaathletics.org",
                               "paralympic.org", "conmebol.com", "thefa.com"]):
        return 4.0
    if any(d in url for d in ["bjsm.bmj.com", "acsm.org", "nsca.com",
                               "simplifaster.com", "elitefts.com", "trainingpeaks.com",
                               "clearinghouseforsport", "sportsmedicineopen"]):
        return 2.0
    # API inline records — no HTTP request needed
    if "|CROSSREF|" in url or "|DOAJ|" in url \
            or "|ZENODO|" in url or "|S2|" in url or "|SPORTRXIV|" in url:
        return 0.1
    return 1.5


def scrape_page(url):
    # Inline API records — no HTTP needed
    if any(m in url for m in ["|CROSSREF|", "|DOAJ|", "|ZENODO|", "|S2|", "|SPORTRXIV|"]):
        text = extract_inline_content_deporte(url)
        title = text.split("\n")[0] or "record"
        return {"title": title, "full_text": text}
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

    return {"title": title, "full_text": f"{title}\n{'='*len(title)}\n\nURL: {url}\n\n{summary}\n\n{body}".strip()}


def url_to_filename(url):
    if "olympics.com"           in url:  prefix = "ioc"
    elif "wada-ama.org"         in url:  prefix = "wada"
    elif "usada.org"            in url:  prefix = "usada"
    elif "ukad.org.uk"          in url:  prefix = "ukad"
    elif "globaldro.com"        in url:  prefix = "globaldro"
    elif "worldathletics.org"   in url:  prefix = "worldathletics"
    elif "fifa.com"             in url:  prefix = "fifa"
    elif "fiba.basketball"      in url:  prefix = "fiba"
    elif "fivb.com"             in url:  prefix = "fivb"
    elif "worldaquatics.com"    in url:  prefix = "worldaquatics"
    elif "uci.org"              in url:  prefix = "uci"
    elif "itftennis.com"        in url:  prefix = "itf"
    elif "world.rugby"          in url:  prefix = "worldrugby"
    elif "ihf.info"             in url:  prefix = "ihf"
    elif "bwfbadminton.com"     in url:  prefix = "bwf"
    elif "worldtaekwondo.org"   in url:  prefix = "taekwondo"
    elif "ijf.org"              in url:  prefix = "ijf"
    elif "isu.org"              in url:  prefix = "isu"
    elif "fis-ski.com"          in url:  prefix = "fis"
    elif "worldrowing.com"      in url:  prefix = "worldrowing"
    elif "gymnastics.sport"     in url:  prefix = "gymnastics"
    elif "iba-boxing.com"       in url or "worldboxing.org" in url: prefix = "boxing"
    elif "acsm.org"             in url:  prefix = "acsm"
    elif "nsca.com"             in url:  prefix = "nsca"
    elif "ecss.de"              in url:  prefix = "ecss"
    elif "bases.org.uk"         in url:  prefix = "bases"
    elif "strengthandconditioning.org" in url: prefix = "asca"
    elif "uksca.org.uk"         in url:  prefix = "uksca"
    elif "conade.gob.mx"        in url:  prefix = "conade"
    elif "clearinghouseforsport" in url: prefix = "clearinghouse_sport"
    elif "uksport.gov.uk"       in url:  prefix = "uksport"
    elif "usopc.org"            in url:  prefix = "usopc"
    elif "fims.org"             in url:  prefix = "fims"
    elif "amssm.org"            in url:  prefix = "amssm"
    elif "aossm.org"            in url:  prefix = "aossm"
    elif "esska.org"            in url:  prefix = "esska"
    elif "bjsm.bmj.com"         in url:  prefix = "bjsm"
    elif "sportshealth.org"     in url:  prefix = "sportshealth"
    elif "nata.org"             in url:  prefix = "nata"
    elif "jissn.biomedcentral"  in url:  prefix = "issn"
    elif "ais.gov.au"           in url and "nutrition" in url: prefix = "ais_nutrition"
    elif "gssiweb.org"          in url:  prefix = "gssi"
    elif "scandpg.org"          in url:  prefix = "scan"
    elif "appliedsportpsych.org" in url: prefix = "aasp"
    elif "issponline.org"       in url:  prefix = "issp"
    elif "fepsac.eu"            in url or "fepsac.com" in url: prefix = "fepsac"
    elif "isbs.org"             in url:  prefix = "isbs"
    elif "catapultsports.com"   in url:  prefix = "catapult"
    elif "jssm.org"             in url:  prefix = "jssm"
    elif "mdpi.com"             in url:  prefix = "sports_mdpi"
    elif "frontiersin.org"      in url:  prefix = "frontiers_sports"
    elif "bmcsportssci"         in url:  prefix = "bmc_sports"
    elif "peerj.com"            in url:  prefix = "peerj_sports"
    elif "ais.gov.au"           in url:  prefix = "ais_au"
    elif "inef.upm.es"          in url:  prefix = "inef"
    elif "aspire.qa"            in url:  prefix = "aspire"
    elif "canadiansportinstitute" in url: prefix = "csi"
    elif "sportnz.org.nz"       in url:  prefix = "sportnz"
    elif "sirc.ca"              in url:  prefix = "sirc"
    elif "pubmed.ncbi"          in url:  prefix = "pubmed_sport"
    elif "icce-office.org"      in url or "icce.ws" in url: prefix = "icce"
    elif "coach.ca"              in url: prefix = "coaching_assoc_ca"
    # Nuevas secciones
    elif "ita-sport.org"        in url or "ita.sport" in url: prefix = "ita_sport"
    elif "inado.net"            in url:  prefix = "inado"
    elif "cces.ca"              in url or "sportintegrity.ca" in url: prefix = "cces"
    elif "nada.de"              in url:  prefix = "nada_de"
    elif "afld.fr"              in url:  prefix = "afld"
    elif "celad.org"            in url or "celad.gob.es" in url: prefix = "celad"
    elif "playtruejapan.org"    in url:  prefix = "jada"
    elif "saids.co.za"          in url or "saids.org.za" in url: prefix = "saids"
    elif "abcd.org.br"          in url:  prefix = "abcd"
    elif "rados.wada-ama.org"   in url:  prefix = "wada_rados"
    elif "casesportsscience"    in url or "cases.org.uk" in url: prefix = "cases_uk"
    elif "sportsmedicineopen"   in url:  prefix = "sports_med_open"
    elif "jhk.pl"               in url or "jhk.termedia.pl" in url: prefix = "jhk"
    elif "ijes.info"            in url:  prefix = "ijes"
    elif "termedia.pl"          in url:  prefix = "biology_of_sport"
    elif "altis.world"          in url:  prefix = "altis"
    elif "simplifaster.com"     in url:  prefix = "simplifaster"
    elif "ijsc-journal.com"     in url:  prefix = "ijsc"
    elif "spr-journal.com"      in url:  prefix = "spr"
    elif "trainology.org"       in url:  prefix = "trainology"
    elif "strongerbyscience.com" in url: prefix = "sbs"
    elif "scsociety.org"        in url:  prefix = "sc_society"
    elif "elitefts.com"         in url:  prefix = "elitefts"
    elif "sportsdietitians.com.au" in url: prefix = "sports_diet_au"
    elif "athletetriadcoalition" in url: prefix = "athlete_triad"
    elif "ais.gov.au" in url and "recipe" in url: prefix = "ais_recipes"
    elif "isbweb.org"           in url:  prefix = "isb"
    elif "opensim.stanford.edu" in url or "opensimconfluence.atlassian.net" in url: prefix = "opensim"
    elif "opencap.ai"           in url:  prefix = "opencap"
    elif "simtk.org"            in url:  prefix = "simtk"
    elif "kinovea.org"          in url:  prefix = "kinovea"
    elif "c-motion.com"         in url or "has-motion.ca" in url or "has-motion.com" in url: prefix = "visual3d"
    elif "vicon.com"            in url:  prefix = "vicon"
    elif "qualisys.com"         in url:  prefix = "qualisys"
    elif "natajournals.org"     in url:  prefix = "jat"
    elif "aspetarjournal.com"   in url or "journal.aspetar.com" in url: prefix = "aspetar_j"
    elif "sagepub.com/toc/ojs"  in url:  prefix = "ojsm"
    elif "cdc.gov/headsup"      in url:  prefix = "cdc_headsup"
    elif "ifspt.org"            in url:  prefix = "ifspt"
    elif "physio-pedia.com"     in url:  prefix = "physiopedia"
    elif "training.fifa.com"    in url or "fifatrainingcentre.com" in url: prefix = "fifa_tc"
    elif "statsbomb.com"        in url:  prefix = "statsbomb"
    elif "metrica-sports.com"   in url:  prefix = "metrica"
    elif "skillcorner.com"      in url:  prefix = "skillcorner"
    elif "kloppy.readthedocs"   in url:  prefix = "kloppy"
    elif "socceraction.readthedocs" in url: prefix = "socceraction"
    elif "sloansportsconference" in url: prefix = "mit_sloan"
    elif "theifab.com"          in url:  prefix = "ifab"
    elif "worldskate.org"       in url:  prefix = "worldskate"
    elif "immaf.org"            in url:  prefix = "immaf"
    elif "wbsc.org"             in url:  prefix = "wbsc"
    elif "igfgolf.org"          in url:  prefix = "igf"
    elif "randa.org"            in url:  prefix = "randa"
    elif "triathlon.org"        in url:  prefix = "triathlon"
    elif "fie.ch"               in url or "fie.org" in url: prefix = "fie"
    elif "issf-sports.org"      in url:  prefix = "issf"
    elif "iwf.sport"            in url:  prefix = "iwf"
    elif "uww.org"              in url:  prefix = "uww"
    elif "fih.ch"               in url or "fih.hockey" in url: prefix = "fih"
    elif "iihf.com"             in url:  prefix = "iihf"
    elif "worldlacrosse.sport"  in url:  prefix = "lacrosse"
    elif "icc-cricket.com"      in url:  prefix = "icc"
    elif "worldarchery.sport"   in url:  prefix = "archery"
    elif "ittf.com"             in url:  prefix = "ittf"
    elif "canoeicf.com"         in url:  prefix = "icf"
    elif "sailing.org"          in url:  prefix = "sailing"
    elif "ifsc-climbing.org"    in url:  prefix = "ifsc"
    elif "isasurf.org"          in url:  prefix = "isa"
    elif "uipmworld.org"        in url:  prefix = "uipm"
    elif "paralympic.org" in url and "/athletics" in url: prefix = "para_athletics"
    elif "paralympic.org" in url and "/swimming" in url: prefix = "para_swimming"
    elif "paralympic.org" in url and "/powerlifting" in url: prefix = "para_powerlifting"
    elif "paralympic.org"       in url:  prefix = "ipc"
    elif "worldparaathletics.org" in url: prefix = "para_athletics"
    elif "worldparaswimming.org" in url: prefix = "para_swimming"
    elif "worldparapowerlifting" in url: prefix = "para_powerlifting"
    elif "bisfed.com"           in url:  prefix = "boccia"
    elif "worldwheelchairrugby" in url or "worldwheelchair.rugby" in url: prefix = "wheelchair_rugby"
    elif "iwbf.org"             in url:  prefix = "iwbf"
    elif "ibsasport.org"        in url:  prefix = "ibsa"
    elif "virtus.sport"         in url:  prefix = "virtus"
    elif "worldabilitysport.org" in url: prefix = "ability_sport"
    elif "paravolley.com"       in url or "worldparavolley.org" in url: prefix = "paravolley"
    elif "paralympics.org.au"   in url:  prefix = "para_au"
    elif "ukcoaching.org"       in url:  prefix = "uk_coaching"
    elif "ukcoaching.org"       in url:  prefix = "uk_coaching"
    elif "thefa.com"            in url:  prefix = "england_fa"
    elif "conmebol.com"         in url:  prefix = "conmebol"
    elif "polar.com"            in url:  prefix = "polar"
    elif "garmin.com"           in url:  prefix = "garmin"
    elif "firstbeat.com"        in url:  prefix = "firstbeat"
    elif "valdperformance.com"  in url:  prefix = "vald"
    elif "statsports.com"       in url:  prefix = "statsports"
    elif "kinexon.com"          in url:  prefix = "kinexon"
    elif "kubios.com"           in url:  prefix = "kubios"
    elif "hrv4training.com"     in url:  prefix = "hrv4training"
    elif "hawkindynamics.com"   in url:  prefix = "hawkin"
    elif "delsys.com"           in url:  prefix = "delsys"
    elif "noraxon.com"          in url:  prefix = "noraxon"
    elif "cosmed.com"           in url:  prefix = "cosmed"
    elif "neurokit2.readthedocs" in url or "neuropsychology.github.io" in url: prefix = "neurokit2"
    elif "biosppy.readthedocs"  in url:  prefix = "biosppy"
    elif "goldencheetah.org"    in url:  prefix = "goldencheetah"
    elif "athletemonitoring.com" in url: prefix = "athletemonitoring"
    elif "trainingpeaks.com"    in url:  prefix = "trainingpeaks"
    elif "uksportsinstitute.co.uk" in url: prefix = "uksi"
    elif "insep.fr"             in url:  prefix = "insep"
    elif "openedition.org"      in url:  prefix = "insep_oe"
    elif "inefc.cat"            in url or "inefc.gencat.cat" in url: prefix = "inefc"
    elif "aspetar.com"          in url:  prefix = "aspetar"
    elif "copsin.ca"            in url:  prefix = "copsin"
    elif "csipacific.ca"        in url:  prefix = "csi_pacific"
    elif "hpsnz.org.nz"         in url:  prefix = "hpsnz"
    elif "jiss.naash.go.jp"     in url or "jpnsport.go.jp" in url: prefix = "jiss"
    elif "sportsingapore.gov.sg" in url: prefix = "sis"
    elif "kiss.kspo.or.kr"      in url:  prefix = "kiss"
    elif "sportireland.ie"      in url:  prefix = "sport_ireland"
    elif "olympiatoppen.no"     in url:  prefix = "olympiatoppen"
    elif "bisp.de"              in url:  prefix = "bisp"
    elif "sfism.ch"             in url:  prefix = "sfism"
    elif "|CROSSREF|"           in url:  prefix = "crossref"
    elif "doaj.org"             in url:  prefix = "doaj"
    elif "zenodo.org"           in url:  prefix = "zenodo"
    elif "semanticscholar.org"  in url:  prefix = "s2"
    elif "osf.io/preprints/sportrxiv" in url: prefix = "sportrxiv"
    elif "la84.org"             in url:  prefix = "la84"
    elif "library.olympics.com" in url:  prefix = "olympic_lib"
    else:                                prefix = "deporte"
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
            eta = (len(remaining) - i) / rate / 60 if rate > 0 else 0
            print(f"[{i}/{len(remaining)}] {rate:.1f} pág/s — ETA {eta:.0f} min", flush=True)

        time.sleep(delay_for_url(url))

    save_progress(progress)
    print(f"\nFinalizado. {len(progress['done'])} páginas subidas.", flush=True)
