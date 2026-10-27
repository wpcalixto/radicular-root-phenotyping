#!/usr/bin/env python3
"""
Title:
    Figure style module
File type:
    Module
Purpose:
    Implements the figure protocol (vector PDF, embedded fonts, English labels, colours and markers)
    shared by the fig_*.py scripts and switches between preview and recording mode (FIG_GRAVAR).
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0 (distribution); historical source dated 2026-08-01
Date:
    2026-08-01
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
    - matplotlib
Execution:
    Imported by the pipeline scripts; not executed directly.
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Verification in v1.0.0: imported by every re-executed figure script. Environment of the
    verification: Python 3.9.6 (macOS) with the versions listed in requirements.txt.
Warnings:
    None specific to this file.
"""
# Original module notes (Portuguese) are preserved below.
"""
Estilo único das figuras do artigo — implementa o protocolo de figuras.

Regras implementadas (uma vez, para todos os scripts `fig_*.py`):
  1.  PDF vetorial com 300 dpi para elementos rasterizados e fontes embutidas
      (`pdf.fonttype = 42`).
  2.  Sem título dentro da figura: o título vai no `\\caption` do LaTeX.
  3.  Rótulos em inglês, com a capitalização do artigo (sentence case).
  6.  Sem texto explicativo dentro da figura.
  9.  Todas as fontes com o mesmo tamanho: letras, números e símbolos.
  10. Tamanho de fonte entre 18 pt e 22 pt (adotado: 18 pt).
  11. Símbolos matemáticos renderizados pelo próprio LaTeX (`text.usetex`),
      idênticos aos do corpo do artigo; unidades entre colchetes.
  12. Paleta Okabe-Ito (colorblind-safe), com hexadecimais fixos.

Regras que dependem de cada figura e são apoiadas por helpers daqui:
  4.  Multi-painel = um arquivo por painel, montado no `.tex` por `\\subfigure`.
  5.  Legenda apenas no primeiro painel (`legenda_primeiro_painel`).
  7.  Cor fixa por entidade ao longo de todo o artigo (dicionários COR_*).
  8.  Marcador fixo por entidade ao longo de todo o artigo (dicionários MARCA_*).

NOTA SOBRE A REGRA 7. O artigo distingue 12 entidades (4 tratamentos, 3 métodos de
segmentação e 5 configurações/fontes preditivas) e a paleta Okabe-Ito oferece 8 cores,
das quais o amarelo tem contraste insuficiente sobre branco. Não é possível, portanto,
uma cor exclusiva por entidade. A solução adotada preserva a regra dentro de cada
família (nenhuma cor se repete entre tratamentos, nem entre métodos, nem entre
configurações) e torna a IDENTIFICAÇÃO GLOBALMENTE ÚNICA pelo par (cor, marcador):
o marcador é exclusivo de cada uma das 12 entidades em todo o artigo. Ver MARCA_GLOBAL.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# Paleta Okabe-Ito — hexadecimais fixos
# ----------------------------------------------------------------------
OKABE_ITO = {
    "preto":     "#000000",
    "laranja":   "#E69F00",
    "azul_ceu":  "#56B4E9",
    "verde":     "#009E73",
    "amarelo":   "#F0E442",   # baixo contraste sobre branco: só com borda escura
    "azul":      "#0072B2",
    "vermelhao": "#D55E00",
    "purpura":   "#CC79A7",
}

# --- Família 1: tratamentos (aparecem juntos em fig 09, 10, 14, 16, 13) ---
COR_TRAT = {
    "REF": OKABE_ITO["azul"],        # #0072B2
    "T1":  OKABE_ITO["laranja"],     # #E69F00
    "T2":  OKABE_ITO["verde"],       # #009E73
    "T3":  OKABE_ITO["vermelhao"],   # #D55E00
}
MARCA_TRAT = {"REF": "o", "T1": "s", "T2": "^", "T3": "D"}
LINHA_TRAT = {"REF": "-", "T1": "--", "T2": "-.", "T3": (0, (3, 1, 1, 1))}

# --- Família 2: métodos de segmentação (fig 07, 15, 19, 20) ---
COR_MET = {
    "M1": OKABE_ITO["azul_ceu"],     # #56B4E9
    "M2": OKABE_ITO["purpura"],      # #CC79A7
    "M3": OKABE_ITO["preto"],        # #000000  (método selecionado)
}
MARCA_MET = {"M1": "v", "M2": "P", "M3": "X"}
LINHA_MET = {"M1": "--", "M2": "-.", "M3": "-"}
HACHURA_MET = {"M1": "//", "M2": "\\\\", "M3": ""}

# --- Família 3: fontes e configurações preditivas (fig 11, 12, 17) ---
COR_FONTE = {
    "optical":              OKABE_ITO["verde"],
    "electrical":           OKABE_ITO["azul"],
    "management":           OKABE_ITO["purpura"],
    "optical + electrical": OKABE_ITO["laranja"],
    "full":                 OKABE_ITO["preto"],
    "reference":            "#8C8C8C",
}
MARCA_FONTE = {
    "optical": "*", "electrical": "h", "management": "p",
    "optical + electrical": "<", "full": ">", "reference": ".",
}
LINHA_FONTE = {
    "optical": "-", "electrical": "--", "management": "-.",
    "optical + electrical": (0, (5, 1)), "full": (0, (1, 1)), "reference": ":",
}
HACHURA_FONTE = {"optical": "//", "electrical": "\\\\", "management": "xx",
                 "optical + electrical": "..", "full": "", "reference": "--"}

# --- Família 4: algoritmos preditivos (fig 17 suplementar) ---
# Regra 7: nenhuma cor se repete DENTRO da família. Regra 8: marcador exclusivo em
# todo o artigo. A referência pela média é a MESMA entidade de COR_FONTE["reference"]
# e conserva cor e marcador.
COR_ALGO = {
    "Ridge":        OKABE_ITO["azul"],
    "Lasso":        OKABE_ITO["laranja"],
    "PLS":          OKABE_ITO["verde"],
    "RandomForest": OKABE_ITO["purpura"],
    "SVR":          OKABE_ITO["vermelhao"],
    "baseline":     COR_FONTE["reference"],
}
MARCA_ALGO = {
    "Ridge": "8", "Lasso": "d", "PLS": "H",
    "RandomForest": "+", "SVR": "x", "baseline": MARCA_FONTE["reference"],
}
LINHA_ALGO = {
    "Ridge": "--", "Lasso": "-.", "PLS": (0, (3, 1, 1, 1)),
    "RandomForest": (0, (5, 2)), "SVR": (0, (1, 1)), "baseline": "-",
}
LAB_ALGO = {
    "Ridge": "Ridge", "Lasso": "Lasso", "PLS": "PLS",
    "RandomForest": "Random forest", "SVR": "SVR", "baseline": "Mean baseline",
}

# --- Família 5: alvos preditos (fig 12) ---
# Estes três aparecem na MESMA figura composta que os quatro tratamentos, de modo
# que cor e marcador precisam diferir dos de COR_TRAT/MARCA_TRAT — antes as duas
# famílias usavam as mesmas três cores e as mesmas três formas, permutadas. As
# formas são polígonos ainda não usados por nenhuma família e mutuamente
# distintas à distância: estrela de quatro pontas, heptágono e asterisco.
COR_ALVO = {
    "M_R":  OKABE_ITO["azul_ceu"],
    "M_PA": OKABE_ITO["purpura"],
    "Q":    OKABE_ITO["preto"],
}
MARCA_ALVO = {"M_R": (4, 1, 0), "M_PA": (7, 0, 0), "Q": (5, 2, 0)}
LINHA_ALVO = {"M_R": "-", "M_PA": "--", "Q": "-."}
LAB_ALVO = {
    "M_R":  r"Root mass $M_{\mathrm{R}}$",
    "M_PA": r"Shoot mass $M_{\mathrm{PA}}$",
    "Q":    "Shoot/root ratio",
}

# --- Marcador globalmente único (regra 8): 15 entidades, 15 formas distintas ---
MARCA_GLOBAL = {}
MARCA_GLOBAL.update({f"trat:{k}": v for k, v in MARCA_TRAT.items()})
MARCA_GLOBAL.update({f"met:{k}": v for k, v in MARCA_MET.items()})
MARCA_GLOBAL.update({f"fonte:{k}": v for k, v in MARCA_FONTE.items()})
MARCA_GLOBAL.update({f"algo:{k}": v for k, v in MARCA_ALGO.items()
                     if k != "baseline"})
MARCA_GLOBAL.update({f"alvo:{k}": v for k, v in MARCA_ALVO.items()})

CINZA = "#8C8C8C"
NEUTRO = "#000000"

FONTE_PT = 18          # regra 10: entre 18 e 22 pt


def aplicar(usetex=True, tamanho=FONTE_PT):
    """rcParams do protocolo. Chamar uma vez, no topo de cada script de figura."""
    plt.rcParams.update({
        # regra 11: símbolos renderizados pelo LaTeX, iguais aos do artigo
        "text.usetex": usetex,
        "font.family": "serif",
        "mathtext.fontset": "cm",
        # regras 9 e 10: tudo no mesmo tamanho, 18 pt
        "font.size": tamanho,
        "axes.labelsize": tamanho,
        "axes.titlesize": tamanho,
        "xtick.labelsize": tamanho,
        "ytick.labelsize": tamanho,
        "legend.fontsize": tamanho,
        "figure.titlesize": tamanho,
        # regra 1: 300 dpi e fontes embutidas
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "pdf.compression": 6,
        # layout
        "figure.constrained_layout.use": True,
        "savefig.bbox": "tight",
        # O bbox "tight" subestima a extensão de rótulos longos girados (usetex) e
        # trunca o final — p. ex. "[pp day$^{-1}$]" saía como "[pp day". 0,15 pol
        # cobre a diferença; a margem extra é irrelevante porque o .tex escala por
        # \linewidth.
        "savefig.pad_inches": 0.15,
        "savefig.format": "pdf",
        "legend.frameon": False,
        "axes.grid": False,
    })
    if usetex:
        # Sem `fontenc[T1]`: as fontes EC não estão instaladas nesta máquina e o
        # travessão (`--`) sai como glifo vazio, apagando faixas como "0--4" e
        # "C1--C$h$". Em OT1 o travessão é renderizado corretamente. Os rótulos
        # são todos em inglês (regra 3), de modo que T1 não é necessário.
        plt.rcParams["text.latex.preamble"] = (
            r"\usepackage[utf8]{inputenc}\usepackage{amsmath}"
        )


# ----------------------------------------------------------------------
# Modo de prévia (padrão): grava PNG em Artigo_revista/_previa/ para inspeção
# visual e NÃO grava o PDF. Só com --gravar o PDF entra na pasta do artigo.
#   python3 scripts/fig_x.py            -> só a prévia PNG
#   python3 scripts/fig_x.py --gravar   -> grava o PDF definitivo
# ----------------------------------------------------------------------
import os as _os
import sys as _sys

DIR_PREVIA = "_previa"
PREVIA_DPI = 150
_GRAVAR = ("--gravar" in _sys.argv) or (_os.environ.get("FIG_GRAVAR") == "1")


def modo():
    """
    Purpose:
        Return the figure mode: recording (FIG_GRAVAR set) or preview.
    Parameters:
        none
    Returns:
        str
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return "gravar" if _GRAVAR else "previa"


def _caminho_previa(caminho):
    caminho = str(caminho)
    d = _os.path.join(_os.path.dirname(caminho), DIR_PREVIA)
    _os.makedirs(d, exist_ok=True)
    base = _os.path.splitext(_os.path.basename(caminho))[0]
    return _os.path.join(d, base + ".png")


def _rotulos_longos(fig, eixos):
    """Rótulos de eixo perto do limite da figura, que saem truncados no PDF.

    A extensão relatada pelo matplotlib para texto `usetex` girado subestima o
    que é de fato desenhado (medido: cerca de 9%), e `bbox_inches="tight"` corta
    o final do rótulo. O limiar de 0,85 sinaliza o rótulo antes de ele estourar;
    a correção é quebrá-lo em duas linhas com "\\n".
    """
    fig.canvas.draw()
    ren = fig.canvas.get_renderer()
    cx = fig.get_window_extent(ren)
    achados = []
    for a in eixos:
        for nome, t in (("ylabel", a.yaxis.label), ("xlabel", a.xaxis.label)):
            if not t.get_text():
                continue
            e = t.get_window_extent(ren)
            if e.height > 0.85 * cx.height or e.width > 0.85 * cx.width:
                achados.append((nome, t.get_text()))
    return achados


def finalizar(fig, ax, caminho):
    """Remove spines, checa a regra 2 e grava.

    Em modo de prévia grava apenas o PNG de inspeção; em modo --gravar grava
    o PDF definitivo. Devolve o caminho efetivamente escrito.
    """
    eixos = ax if isinstance(ax, (list, tuple)) else [ax]
    for a in eixos:
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
        if a.get_title():
            raise ValueError(f"regra 2 violada: título dentro da figura ({a.get_title()!r})")
    if fig._suptitle is not None:
        raise ValueError("regra 2 violada: suptitle dentro da figura")
    for nome, texto in _rotulos_longos(fig, eixos):
        print(f"  !! rótulo no limite em {_os.path.basename(str(caminho))}: "
              f"{nome} = {texto!r}")
    if _GRAVAR:
        fig.savefig(str(caminho), format="pdf", dpi=300)
        escrito = str(caminho)
    else:
        escrito = _caminho_previa(caminho)
        fig.savefig(escrito, format="png", dpi=PREVIA_DPI)
    plt.close(fig)
    return escrito


def legenda_primeiro_painel(ax, painel, **kw):
    """Regra 5: legenda apenas no primeiro painel de um conjunto multi-painel."""
    if str(painel).lower() in ("a", "0", "1", "primeiro"):
        kw.setdefault("frameon", False)
        kw.setdefault("fontsize", FONTE_PT)
        return ax.legend(**kw)
    return None


def rotulo(texto, unidade=None):
    """Regra 11: unidade entre colchetes; símbolos em modo matemático do LaTeX."""
    return f"{texto} [{unidade}]" if unidade else texto
