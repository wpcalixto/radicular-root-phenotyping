#!/usr/bin/env python3
"""
Title:
    Paired enlargements of diagnostic cases
File type:
    Script
Purpose:
    Selects, for each diagnostic case, the 500-pixel window that maximises M1/M2 disagreement and
    writes paired panels with identical spatial limits and the window table.
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
    - metricas/A5_casos.csv
Outputs:
    - Artigo_revista/21_figura_resultado_<1-6><a-d>.pdf
    - metricas/A15_janelas.csv
Dependencies:
    - cv2
    - matplotlib
    - numpy
    - local: config, estilo_figuras
Execution:
    python scripts/A15_ampliacoes.py (from a workspace prepared with tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Verification in v1.0.0: re-executed through scripts/auxiliary/run_A15_pad010.py; PDFs pixel-
    identical (72 dpi) to the RSOS files. Environment of the verification: Python 3.9.6 (macOS) with
    the versions listed in requirements.txt.
Warnings:
    The approved PDFs were produced with savefig.pad_inches = 0.10; use
    scripts/auxiliary/run_A15_pad010.py.
"""
# Original module notes (Portuguese) are preserved below.
"""
A15 — Ampliações pareadas dos casos selecionados, em janela escolhida por critério objetivo.

Motivação (auditoria 2026-07-30, item 32): as figuras de casos e de composição comparam as
máscaras em quadro cheio, escala em que raízes finas e modos de erro ficam abaixo do limite
de resolução da página. A auditoria pede ampliações pareadas, com limites espaciais
idênticos entre os painéis de uma mesma linha.

Critério objetivo da janela (sem escolha manual de região): para cada caso, computa-se o
mapa de discordância entre os dois ramos, $D = \\text{M1} \\oplus \\text{M2}$, e seleciona-se a
janela quadrada de lado L que maximiza a contagem de pixels discordantes. É a região em que
os dois segmentadores mais divergem e, portanto, aquela em que a composição de M3 é
decidida. A mesma janela é aplicada aos quatro painéis do caso, o que torna a comparação
espacialmente pareada.

Saídas: Artigo_revista/21_figura_resultado_<1-6><a-d>.pdf  (6 casos x 4 painéis)
        metricas/A15_janelas.csv  (coordenadas e discordância de cada janela)
"""
import os
import sys
import csv

import numpy as np
import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
import estilo_figuras as E

BASE = C.SAIDAS
OUT = C.ROOT / "Artigo_revista"
CSV_CASOS = C.METRICAS / "A5_casos.csv"
OUT_CSV = C.METRICAS / "A15_janelas.csv"

LADO = 500          # lado da janela de ampliação, em pixels
VERDE = [0.15, 0.85, 0.15]

E.aplicar(usetex=False)     # painéis de imagem: sem texto, usetex desnecessário


def caminho(sub, data, img, masks=True):
    """
    Purpose:
        Build the path of an image or mask of a given stage.
    Parameters:
        sub: stage directory
        data: collection date
        img: identifier
        masks: mask flag
    Returns:
        pathlib.Path
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    p = BASE / sub
    if masks:
        p = p / "masks"
    return p / data / (img + ".png")


def ler_mascara(p, shape):
    """
    Purpose:
        Read a mask resized to a reference shape.
    Parameters:
        p: mask path
        shape: target shape
    Returns:
        numpy bool array
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    m = cv2.imread(str(p), 0)
    if m is None:
        return None
    m = m > 127
    if m.shape != shape:
        m = cv2.resize(m.astype(np.uint8), (shape[1], shape[0]),
                       interpolation=cv2.INTER_NEAREST) > 0
    return m


def janela_max_discordancia(m1, m2, lado):
    """Janela quadrada de lado `lado` que maximiza a discordância M1 XOR M2.

    Usa imagem integral: soma em qualquer janela em tempo constante."""
    D = np.logical_xor(m1, m2).astype(np.float32)
    H, W = D.shape
    lado = int(min(lado, H, W))
    ii = cv2.integral(D)                       # (H+1, W+1)
    # soma na janela (y, x) -> ii[y+l, x+l] - ii[y, x+l] - ii[y+l, x] + ii[y, x]
    S = (ii[lado:, lado:] - ii[:-lado, lado:]
         - ii[lado:, :-lado] + ii[:-lado, :-lado])
    y, x = np.unravel_index(int(np.argmax(S)), S.shape)
    return int(y), int(x), lado, float(S[y, x]), float(D.sum())


def painel(rgb, mask, y, x, lado, caminho_saida):
    """
    Purpose:
        Write one enlarged panel of the selected window.
    Parameters:
        rgb: image
        mask: mask
        y, x: window origin
        lado: window side
        caminho_saida: output path
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    rec = rgb[y:y + lado, x:x + lado].copy()
    if mask is not None:
        rec[mask[y:y + lado, x:x + lado]] = VERDE
    fig = plt.figure(figsize=(4, 4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(np.clip(rec, 0, 1))
    ax.set_axis_off()
    fig.savefig(str(caminho_saida), format="pdf", dpi=300)
    plt.close(fig)


def main():
    """
    Purpose:
        Run the script end to end: read inputs, compute results and write the outputs listed in the header.
    Parameters:
        none (some scripts accept an optional limit or command-line argument)
    Returns:
        None
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    if not CSV_CASOS.exists():
        print("[A15] Rode antes o A5_casos.py."); return
    casos = list(csv.DictReader(open(CSV_CASOS, encoding="utf-8")))
    linhas = []
    for idx, c in enumerate(casos, 1):
        img = c["image_id"]
        data = "_".join(img.split("_")[1:])
        p_cond = BASE / "05A_tratadas" / data / (img + ".png")
        rgb = np.asarray(plt.imread(str(p_cond)))[:, :, :3].astype(float)
        if rgb.max() > 1:
            rgb /= 255.0
        shape = rgb.shape[:2]
        m1 = ler_mascara(caminho("07_frangi", data, img), shape)
        m2 = ler_mascara(caminho("06C_inferencia", data, img), shape)
        m3 = ler_mascara(caminho("08_combinado_limpo", data, img), shape)

        y, x, lado, disc, disc_total = janela_max_discordancia(m1, m2, LADO)
        frac = 100.0 * disc / disc_total if disc_total else 0.0
        print("  [%d] %-16s janela (y=%4d, x=%4d, %dpx)  discordância na janela: "
              "%.0f px (%.1f%% do total da imagem)" % (idx, img, y, x, lado, disc, frac))

        for lab, m in (("a", None), ("b", m1), ("c", m2), ("d", m3)):
            painel(rgb, m, y, x, lado,
                   OUT / f"21_figura_resultado_{idx}{lab}.pdf")

        linhas.append({"caso": idx, "regra": c["regra"], "image_id": img,
                       "y": y, "x": x, "lado_px": lado,
                       "discordancia_janela_px": int(disc),
                       "discordancia_imagem_px": int(disc_total),
                       "fracao_pct": round(frac, 2)})

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)
    print(f"\n[A15] {len(linhas)} casos x 4 painéis -> 21_figura_resultado_<1-6><a-d>.pdf")
    print(f"[A15] {OUT_CSV.name} gravado.")


if __name__ == "__main__":
    main()
