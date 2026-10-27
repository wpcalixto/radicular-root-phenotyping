# -*- coding: utf-8 -*-
"""
Title:
    Central configuration
File type:
    Module
Purpose:
    Defines the relative directory tree, experimental constants (sowing date, rhizotrons,
    collections, Wenner spacing) and processing parameters imported by all scripts.
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0 (distribution); historical source dated 2026-07-31
Date:
    2026-07-31
Developer:
    Prof. Wesley Pacheco Calixto
Authors:
    Wesley Pacheco Calixto; Universidade de Coimbra (UC), Portugal; Universidade Federal de Goiás
    (UFG), Brazil; Instituto Federal de Educação, Ciência e Tecnologia de Goiás (IFG), Brazil
Corresponding author:
    Wesley Pacheco Calixto
License:
    MIT (see LICENSE)
Citation:
    If you use this code, please cite the Radicular Software record on Zenodo (DOI 10.5281/zenodo.23679263) and the related publication.
Related publication:
    Auditable longitudinal root phenotyping in rhizotrons using Frangi--U-Net fusion and apparent
    conductivity (manuscript in preparation for submission to Royal Society Open Science)
Inputs:
    - none detected by static analysis
Outputs:
    - printed results only
Dependencies:
    - Python standard library
Execution:
    Imported by the pipeline scripts; not executed directly.
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Verification in v1.0.0: imported by every re-executed script. Environment of the verification:
    Python 3.9.6 (macOS) with the versions listed in requirements.txt.
Warnings:
    None specific to this file.
"""
# Original module notes (Portuguese) are preserved below.
"""
Configuração central do pipeline radicular (Fases 00–14).
Fonte única de caminhos, constantes do experimento e parâmetros.
Todos os scripts NN_*.py importam este módulo.
"""
import os
import sys
import datetime
from pathlib import Path

# ----------------------------------------------------------------------
# Caminhos (derivados da localização deste arquivo: Nova_versao/scripts/)
# ----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent          # .../Nova_versao
ENTRADAS   = ROOT / "entradas"
SAIDAS     = ROOT / "saidas"
SCRIPTS    = ROOT / "scripts"
TABDATAS   = ROOT / "tabdatas"
TABELAS    = ROOT / "tabelas"
CONFIG     = ROOT / "config"
METRICAS   = ROOT / "metricas"
MODELOS    = ROOT / "modelos"
PREDICAO   = ROOT / "predicao"
FIGURES    = ROOT / "figures"
FIGDATA    = ROOT / "figdata"
CHECKPOINT = ROOT / "checkpoint"
AUDITORIA  = ROOT / "auditoria"
MANIFESTOS = ROOT / "manifestos"

# ----------------------------------------------------------------------
# Delineamento experimental
# ----------------------------------------------------------------------
DATA_PLANTIO = datetime.date(2025, 4, 23)               # origem temporal (DAP=0) — semeadura nos rizotrons
RIZOTRONS = [f"R{n:02d}" for n in range(1, 13)]         # R01..R12

# Datas de coleta (= datas das IMAGENS), na ordem dos registros 1..7
COLETAS = ["23_05_2025", "31_05_2025", "07_06_2025",
           "14_06_2025", "21_06_2025", "28_06_2025", "05_07_2025"]

DELTA_T_REF = 7                                          # intervalo semanal esperado (dias)

# ----------------------------------------------------------------------
# Arranjo de Wenner (medições elétricas)
# ----------------------------------------------------------------------
# Espaçamento FÍSICO entre hastes, medido na instalação: quatro eletrodos ao longo
# dos 80 cm de altura, dividindo-a em cinco intervalos iguais de 16 cm
# (as hastes ocupam os quatro pontos internos de divisão):
#     16 + 16 + 16 + 16 + 16 = 80 cm  ->  a = 0,16 m
# Penetração no substrato: haste de 17 cm menos 1,5 cm de espessura do compensado = 15,5 cm.
# ATENÇÃO: as planilhas de Resistividade recebidas foram calculadas com a = 0,2667 m
# (= 80/3, supondo as hastes distribuídas de borda a borda, sem margens). Esse valor
# é INCORRETO. A Fase 10 recalcula rho_a e sigma_a a partir da resistência medida
# usando WENNER_A, e mantém os valores das planilhas apenas para auditoria.
WENNER_A = 0.16          # m
WENNER_A_PLANILHA = 0.2667   # m — valor (incorreto) implícito nas planilhas recebidas

# Esquema de adubação por tratamento (dias após plantio previstos)
ADUBACAO_PREVISTA = {"REF": None, "T1": 0, "T2": 30, "T3": 60}

# ----------------------------------------------------------------------
# Parâmetros de QC de imagem (Fase 04)
# ----------------------------------------------------------------------
QC_TAU_OVER  = 0.95     # limiar de superexposição (L_n)
QC_TAU_UNDER = 0.05     # limiar de subexposição (L_n)
QC_TAU_SAT   = 0.90     # limiar de saturação para glare (L_n)
QC_CENTRAL   = (0.35, 0.65, 0.35, 0.65)   # (a1, a2, b1, b2) região central Ω_c
QC_GAMMA1    = 0.05     # glare moderado se G_c >= γ1
QC_GAMMA2    = 0.20     # glare intenso  se G_c >= γ2
QC_B_MIN     = 1e-5     # nitidez mínima (Var do Laplaciano em L_n) — calibrável
QC_FOVER_MAX = 0.05     # fração máx. de superexposição global tolerada
QC_FUNDER_MAX = 0.40    # fração máx. de subexposição global tolerada

# ----------------------------------------------------------------------
# Registro e recorte geométrico (Fase 05)
# ----------------------------------------------------------------------
# ATENÇÃO (calibração): o enquadramento NÃO inclui as bordas do rizotron nem
# marcador fiducial/métrico. Não há, portanto, escala espacial absoluta confiável
# (uma conversão px->cm exigiria s_x = s_y isotrópico, o que 60/W_px != 80/H_px NÃO
# satisfaz). Por isso os descritores são reportados em PIXELS, PROPORÇÃO da área
# válida e PROFUNDIDADE NORMALIZADA (0–1). As dimensões nominais do painel abaixo
# ficam apenas como CONTEXTO documental — NÃO são usadas como calibração.
W_REAL_CM = 60.0          # largura nominal do painel (contexto; NÃO usada p/ calibrar)
H_REAL_CM = 80.0          # profundidade nominal do painel (contexto; NÃO usada p/ calibrar)
CROP_MARGIN_FRAC = 0.02   # recorte FIXO e CENTRADO: fração removida de cada borda
TOP_IS_SURFACE = True     # topo da imagem = superfície do solo (y=0) — a confirmar
N_CAMADAS = 10            # nº de faixas de profundidade normalizada (10 bandas iguais)

# ----------------------------------------------------------------------
# Pré-tratamento — remoção do flash/glare especular (Fase 05A)
# ----------------------------------------------------------------------
# Inpainting por Deep Learning (LaMa) do glare especular (núcleo + halo saturado).
# Princípio (melhor visual SEM perder a ciência): só se aciona onde há um núcleo
# ESPECULAR GENUÍNO (quase-branco estourado, V>=DEFLASH_SEED_V) — assim raízes/solo
# brilhantes NÃO viram semente. A partir do núcleo, cresce pelo "halo lavado"
# (glareness = excesso de brilho OU déficit de saturação vs. fundo), CONFINADO a um
# disco ao redor do núcleo (impede disparar por raiz/solo) e fechado em FECHO CONVEXO
# (região compacta). Raiz que cruza o glare é reconstruída (dado ali já está perdido).
# O halo difuso remanescente fica para o flat-field da Fase 07.
# IMPORTANTE (ciência): a máscara é salva (auditoria) e a área inpintada (flash_pct) é
# registrada para ser EXCLUÍDA das estatísticas quantitativas de densidade radicular.
DEFLASH_SEED_V      = 0.955   # brilho mín. do NÚCLEO especular (0-1) — só flash estourado
DEFLASH_SEED_S      = 0.25    # saturação máx. do núcleo (especular = desaturado)
DEFLASH_SEED_AREA   = 200     # área mín. do núcleo (px) p/ acionar (evita reflexos ínfimos)
DEFLASH_BG_SIGMA    = 160     # sigma do fundo de larga escala (V e S) p/ glareness
DEFLASH_GLARE_THR   = 0.20    # limiar de glareness (0-1) p/ crescer o halo
DEFLASH_DISC_K      = 7       # raio do disco-limite = K * raio_do_núcleo
DEFLASH_DISC_CAP    = 480     # raio máx. do disco-limite (px) — teto p/ não inpintar demais
DEFLASH_HULL_AREA   = 400     # área mín. do blob crescido p/ virar fecho convexo (px)
DEFLASH_FINAL_DILATE = 13     # dilatação final p/ suavizar a borda (px)
DEFLASH_MAX_SIDE    = 1600    # lado máx. p/ rodar a LaMa na CPU (evita OOM); recompõe full-res
DEFLASH_BLEND_SIGMA = 12      # suavização da borda na recomposição (px)

# ----------------------------------------------------------------------
# Parâmetros de segmentação (Fase 07 — Frangi)
# ----------------------------------------------------------------------
FRANGI_SIGMAS = range(2, 10)      # baseline clássico: forte em raízes finas
FRANGI_BLACK_RIDGES = False
FRANGI_THRESHOLD = 0.1
# pré-processamento fotométrico + glare + limiar (Fase 07)
FLATFIELD_SIGMA = 60          # sigma gaussiano do campo de iluminação (larga escala)
CLAHE_CLIP = 0.01             # clip do CLAHE (equalize_adapthist)
GLARE_TAU_L = 0.92            # limiar de glare no L_clahe (0-1)
THRESH_METHOD = "otsu"        # "otsu" | "percentile"
THRESH_PERCENTILE = 92        # usado se THRESH_METHOD == "percentile"
A_MIN = 80                    # remover componentes conectados menores que isto (px)
# ramo de inpainting do glare LIMITADO (metodologia Fase 07): reconstrói a região de glare
# residual em vez de só invalidá-la. Núcleos pequenos p/ NÃO apagar raízes finas.
GLARE_INPAINT_MAX = 0.05      # fração máx. de glare p/ tratar por inpaint ("limitado")
GLARE_INPAINT_RADIUS = 5      # raio do inpaint (px)
# morfologia da máscara radicular final (metodologia Fase 07): abertura -> fechamento.
# ATENÇÃO: abertura morfológica (erosão) APAGA raízes finas de 1-2 px (força do Frangi) —
# reduziu a cobertura à metade nos testes. Por isso a "abertura" é feita por ÁREA
# (remove_small_objects, sem erodir a largura) e mantém-se só o fechamento.
MORPH_OPEN_R = 0             # 0 = SEM abertura por erosão (preserva raízes finas)
MORPH_CLOSE_R = 1           # raio do fechamento (px) — conecta lacunas curtas

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def num_rizotron(riz: str) -> int:
    """'R04' -> 4"""
    return int(str(riz).lstrip("Rr"))

def tratamento(riz: str):
    """Retorna (codigo, nome) do tratamento do rizotron."""
    n = num_rizotron(riz)
    if 1 <= n <= 3:   return ("REF", "Referencia")
    if 4 <= n <= 6:   return ("T1", "Tratamento 1")
    if 7 <= n <= 9:   return ("T2", "Tratamento 2")
    if 10 <= n <= 12: return ("T3", "Tratamento 3")
    return ("?", "desconhecido")

def replicata(riz: str) -> int:
    """Repetição biológica 1..3 dentro do tratamento."""
    return ((num_rizotron(riz) - 1) % 3) + 1

def parse_data_pasta(nome: str) -> datetime.date:
    """'23_05_2025' -> date(2025,5,23)"""
    d, m, y = nome.split("_")
    return datetime.date(int(y), int(m), int(d))

def dap(data: datetime.date) -> int:
    """Dias após plantio."""
    return (data - DATA_PLANTIO).days

def arquivos_eletricos(data_pasta: str):
    """Nomes esperados dos xlsx elétricos para uma data de coleta."""
    d, m, y = data_pasta.split("_")
    return {
        "conductivity_file": f"Condutividade_Eletrica_{d}_{m}_{y[2:]}.xlsx",
        "resistance_file":   f"Resistencia_{d}_{m}_{y}.xlsx",
        "resistivity_file":  f"Resistividade_{d}_{m}_{y}.xlsx",
    }

TARGET_FILE = "Massa_full.xlsx"   # alvos finais (massa aérea/radicular)
