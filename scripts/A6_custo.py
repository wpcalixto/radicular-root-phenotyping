#!/usr/bin/env python3
"""
Title:
    Processing time and computational repeatability
File type:
    Script
Purpose:
    Times each processing stage per image using the production functions and checks repeatability of
    outputs by hashing.
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0 (distribution); historical source dated 2026-07-14
Date:
    2026-07-14
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
    - modelos/external_final_model_PRMI_all.pt
    - saidas/05A_tratadas/_mascaras
    - saidas/05_registradas/**
Outputs:
    - metricas/A6_custo.csv
    - metricas/A6_repetibilidade.csv
Dependencies:
    - cv2
    - numpy
    - platform
    - scipy
    - segmentation_models_pytorch
    - torch
    - local: config
Execution:
    python scripts/A6_custo.py (from a workspace prepared with tools/prepare_workspace.py)
Portability notes:
    Paths are resolved relative to the repository root through scripts/config.py; build the expected
    tree with tools/prepare_workspace.py.
Reproducibility notes:
    Not re-executed in the v1.0.0 verification. Environment of the verification: Python 3.9.6
    (macOS) with the versions listed in requirements.txt.
Warnings:
    Timings depend on hardware and are not expected to be reproduced exactly.
"""
# Original module notes (Portuguese) are preserved below.
"""
Resultado adicional A6 — tempo de processamento e reprodutibilidade computacional.
Cronometra, por imagem, o tempo de parede (wall-clock) de cada estágio de PROCESSAMENTO
(NÃO inclui leitura/gravação em disco — não é "ponta a ponta"), usando as MESMAS funções
dos scripts de produção (05A/07/06C/08+08E/09), sobre as 82 imagens. Estágios:
  1. Remoção do reflexo (LaMa, CPU): detecção do núcleo + máscara + downscale (<=1600px)
     + inferência LaMa em resolução reduzida + reamostragem + recomposição full-res.
  2. Segmentação Frangi (M1, CPU) -> 07_frangi.segmentar.
  3. Inferência U-Net (M2)        -> 06C, mediana de N_REP repetições com sincronização MPS
                                     (torch.mps.synchronize antes/depois); e também em CPU.
  4. Combinação/refino (M3, CPU)  -> 08E_refinamento.denoise_frangi + união + fecho.
  5. Quantificação (CPU)          -> 09_descritores.descritores (esqueleto + descritores).
Auditorias: (a) correlação do tempo de deflash com nº de núcleos e fração reconstruída;
            (b) repetibilidade — 3 passagens em subconjunto, diffs máximos e identidade MD5.
Saídas: metricas/A6_custo.csv (por imagem) + metricas/A6_repetibilidade.csv + resumo stdout.
"""
import os, sys, time, glob, csv, platform, hashlib, resource, importlib.util
import statistics as st
import numpy as np, cv2, torch
from scipy.stats import spearmanr
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
import segmentation_models_pytorch as smp

OUT = C.METRICAS / "A6_custo.csv"
OUT_REP = C.METRICAS / "A6_repetibilidade.csv"
N_SAMPLE = int(os.environ.get("A6_N", "0"))       # 0 = todas as 82 imagens
N_REP = int(os.environ.get("A6_REP", "7"))         # repetições de cronometragem do U-Net (mediana)
N_REPET = int(os.environ.get("A6_REPET", "6"))     # imagens no teste de repetibilidade
ENCODER, LONG, THR = "resnet34", 1024, 0.5
IMEAN = np.array([0.485, 0.456, 0.406], np.float32)
ISTD = np.array([0.229, 0.224, 0.225], np.float32)
FECHA = 3


def load_mod(name, path):
    """
    Purpose:
        Import a pipeline script as a module from its file path without executing its main function.
    Parameters:
        name: module name
        path: script path
    Returns:
        module
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def prep(rgb, dev):
    """
    Purpose:
        Resize an image to the inference size and prepare a tensor.
    Parameters:
        rgb: image
        dev: torch device
    Returns:
        tuple
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    H0, W0 = rgb.shape[:2]; s = LONG / max(H0, W0)
    Hn = max(32, int(round(H0 * s / 32)) * 32); Wn = max(32, int(round(W0 * s / 32)) * 32)
    img = cv2.resize(rgb, (Wn, Hn)).astype(np.float32) / 255.0
    x = torch.from_numpy(((img - IMEAN) / ISTD).transpose(2, 0, 1)).unsqueeze(0).to(dev)
    return x, (H0, W0)


def unet_infer(model, dev, rgb, sync):
    """Estágio M2 completo: prep (resize+transfer) + forward + pós (resize+limiar)."""
    x, (H0, W0) = prep(rgb, dev)
    if sync: torch.mps.synchronize()
    with torch.inference_mode():
        prob = torch.sigmoid(model(x))[0, 0].float().cpu().numpy()
    if sync: torch.mps.synchronize()
    prob = cv2.resize(prob, (W0, H0))
    return prob, (prob >= THR)


def timed_unet(model, dev, rgb, sync, reps):
    """Mediana de `reps` cronometragens do estágio M2 (sincronizando o MPS a cada uma)."""
    ts, last = [], None
    for _ in range(reps):
        if sync: torch.mps.synchronize()
        t = time.perf_counter()
        prob, mask = unet_infer(model, dev, rgb, sync)
        if sync: torch.mps.synchronize()
        ts.append(time.perf_counter() - t); last = (prob, mask)
    return st.median(ts), last


def full_chain(pre, fr, ref, des, model, dev, sync, p, bgr, rgb, inpaint):
    """Uma passagem completa de segmentação/quantificação (para o teste de repetibilidade)."""
    _, m1, _, _, _ = fr.segmentar(p)
    _, m2 = unet_infer(model, dev, rgb, sync)
    m1d = ref.denoise_frangi(m1); comb = m1d | m2
    comb = cv2.morphologyEx(comb.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((FECHA, FECHA), np.uint8)).astype(bool)
    tratada, _, _, _ = pre.deflash(bgr)
    d, _ = des.descritores(comb, inpaint)
    return m1, m2, comb, d, tratada


def md5(a):
    """
    Purpose:
        MD5 of an array content.
    Parameters:
        a: numpy array
    Returns:
        str
    Raises:
        No exception is raised explicitly; errors of called libraries propagate.
    Notes:
        Parameter types are not annotated in the original code.
    """
    return hashlib.md5(np.ascontiguousarray(a).tobytes()).hexdigest()


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
    pre = load_mod("pre", str(C.SCRIPTS / "05A_pretratamento.py"))
    fr = load_mod("fr", str(C.SCRIPTS / "07_frangi.py"))
    ref = load_mod("ref", str(C.SCRIPTS / "08E_refinamento.py"))
    des = load_mod("des", str(C.SCRIPTS / "09_descritores.py"))

    regs = sorted(glob.glob(str(C.SAIDAS / "05_registradas" / "**" / "*.png"), recursive=True))
    if N_SAMPLE and N_SAMPLE < len(regs):
        idx = np.linspace(0, len(regs) - 1, N_SAMPLE).round().astype(int)
        sample = [regs[i] for i in dict.fromkeys(idx)]
    else:
        sample = regs
    H, W = cv2.imread(sample[0]).shape[:2]
    mps_ok = torch.backends.mps.is_available()
    dev = torch.device("mps") if mps_ok else torch.device("cpu")
    print(f"[A6] {len(sample)} imagens ({H}x{W}) | host: {platform.processor() or platform.machine()}"
          f" | torch {torch.__version__} | MPS={mps_ok} | N_REP={N_REP}")

    t = time.perf_counter(); pre._get_lama(); t_lama_load = time.perf_counter() - t
    t = time.perf_counter()
    model = smp.Unet(encoder_name=ENCODER, encoder_weights=None, in_channels=3, classes=1).to(dev)
    wpath = C.MODELOS / "external_final_model_PRMI_all.pt"
    model.load_state_dict(torch.load(str(wpath), map_location=dev)); model.eval()
    t_unet_load = time.perf_counter() - t
    model_cpu = smp.Unet(encoder_name=ENCODER, encoder_weights=None, in_channels=3, classes=1)
    model_cpu.load_state_dict(torch.load(str(wpath), map_location="cpu")); model_cpu.eval()
    print(f"[A6] carga única: LaMa {t_lama_load:.2f}s | U-Net {t_unet_load:.2f}s "
          f"| pesos {wpath.stat().st_size/1e6:.1f} MB")

    # warm-up (exclui overhead de 1ª chamada: JIT/alocação/MPS)
    w = cv2.imread(sample[0]); wrgb = cv2.cvtColor(w, cv2.COLOR_BGR2RGB)
    pre.deflash(w); fr.segmentar(sample[0])
    timed_unet(model, dev, wrgb, mps_ok, 2); timed_unet(model_cpu, torch.device("cpu"), wrgb, False, 2)

    rows = []
    for k, p in enumerate(sample, 1):
        img_id = os.path.splitext(os.path.basename(p))[0]
        data = os.path.basename(os.path.dirname(p))
        bgr = cv2.imread(p); rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        r = {"image_id": img_id, "data": data, "H": bgr.shape[0], "W": bgr.shape[1]}

        t = time.perf_counter(); _, mask_inp, flash_pct, n_blobs = pre.deflash(bgr); r["t_deflash_s"] = time.perf_counter() - t
        r["n_nucleos"] = n_blobs; r["flash_pct"] = round(flash_pct, 3)

        t = time.perf_counter(); _, m1, _, _, _ = fr.segmentar(p); r["t_frangi_s"] = time.perf_counter() - t

        r["t_unet_mps_s"], (_, m2) = timed_unet(model, dev, rgb, mps_ok, N_REP)
        r["t_unet_cpu_s"], _ = timed_unet(model_cpu, torch.device("cpu"), rgb, False, N_REP)

        t = time.perf_counter()
        m1d = ref.denoise_frangi(m1); comb = m1d | m2
        comb = cv2.morphologyEx(comb.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((FECHA, FECHA), np.uint8)).astype(bool)
        r["t_combina_s"] = time.perf_counter() - t

        ipp = C.SAIDAS / "05A_tratadas" / "_mascaras" / data / (img_id + ".png")
        inpaint = (cv2.imread(str(ipp), 0) > 127) if ipp.exists() else np.zeros_like(comb)
        if inpaint.shape != comb.shape:
            inpaint = cv2.resize(inpaint.astype(np.uint8), (comb.shape[1], comb.shape[0]), interpolation=cv2.INTER_NEAREST) > 0
        t = time.perf_counter(); des.descritores(comb, inpaint); r["t_quant_s"] = time.perf_counter() - t

        r["t_total_mps_s"] = r["t_deflash_s"] + r["t_frangi_s"] + r["t_unet_mps_s"] + r["t_combina_s"] + r["t_quant_s"]
        r["t_total_cpu_s"] = r["t_total_mps_s"] - r["t_unet_mps_s"] + r["t_unet_cpu_s"]
        rows.append(r)
        if k % 10 == 0 or k == len(sample):
            print(f"  [{k}/{len(sample)}] {img_id}: total(mps)={r['t_total_mps_s']:.2f}s")

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

    def stats(k):
        v = sorted(r[k] for r in rows)
        q = np.percentile(v, [25, 50, 75])
        return st.mean(v), (st.pstdev(v) if len(v) > 1 else 0), q[1], q[0], q[2], v[0], v[-1]
    print("\n[A6] RESUMO — média±dp | mediana [Q1–Q3] | min–máx (s/imagem):")
    for k, lab in [("t_deflash_s", "1. Remoção do reflexo (LaMa, CPU)"), ("t_frangi_s", "2. Frangi M1 (CPU)"),
                   ("t_unet_mps_s", "3. U-Net M2 (MPS)"), ("t_unet_cpu_s", "3'. U-Net M2 (CPU)"),
                   ("t_combina_s", "4. Combinacao M3 (CPU)"), ("t_quant_s", "5. Quantificacao (CPU)"),
                   ("t_total_mps_s", "TOTAL (U-Net em MPS)"), ("t_total_cpu_s", "TOTAL (tudo em CPU)")]:
        m, s, md, q1, q3, lo, hi = stats(k)
        print(f"   {lab:34s} {m:7.3f}±{s:.3f} | {md:6.3f} [{q1:.3f}–{q3:.3f}] | {lo:.3f}–{hi:.3f}")

    tot = [r["t_total_mps_s"] for r in rows]; tot_sum = sum(tot)
    print(f"\n[A6] tempo TOTAL observado ({len(rows)} imagens): {tot_sum:.1f}s = {tot_sum/60:.2f} min "
          f"| throughput {3600/st.mean(tot):.0f} imagens/h")
    print(f"[A6] cargas únicas (excluídas do total): LaMa {t_lama_load:.2f}s + U-Net {t_unet_load:.2f}s = {t_lama_load+t_unet_load:.2f}s")
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9  # macOS: bytes
    print(f"[A6] pico de RSS do processo: {rss:.2f} GB")
    # (a) correlacao do custo de deflash com nucleos e fracao reconstruida
    td = [r["t_deflash_s"] for r in rows]
    print(f"[A6] Spearman t_deflash × n_núcleos = {spearmanr(td, [r['n_nucleos'] for r in rows])[0]:+.2f} ; "
          f"× fração reconstruída = {spearmanr(td, [r['flash_pct'] for r in rows])[0]:+.2f}")

    # (b) repetibilidade: 3 passagens completas em subconjunto -> diffs máximos + identidade MD5
    sub = [sample[i] for i in np.linspace(0, len(sample) - 1, min(N_REPET, len(sample))).round().astype(int)]
    print(f"\n[A6] REPETIBILIDADE — 3 passagens em {len(sub)} imagens:")
    rep_rows = []
    for p in sub:
        img_id = os.path.splitext(os.path.basename(p))[0]
        data = os.path.basename(os.path.dirname(p))
        bgr = cv2.imread(p); rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        ipp = C.SAIDAS / "05A_tratadas" / "_mascaras" / data / (img_id + ".png")
        H0, W0 = bgr.shape[:2]
        inp = (cv2.imread(str(ipp), 0) > 127) if ipp.exists() else np.zeros((H0, W0), bool)
        if inp.shape != (H0, W0):
            inp = cv2.resize(inp.astype(np.uint8), (W0, H0), interpolation=cv2.INTER_NEAREST) > 0
        outs = [full_chain(pre, fr, ref, des, model, dev, mps_ok, p, bgr, rgb, inp) for _ in range(3)]
        m1h = {md5(o[0]) for o in outs}; m2h = {md5(o[1]) for o in outs}; m3h = {md5(o[2]) for o in outs}
        lamah = {md5(o[4]) for o in outs}
        # diffs de descritores
        keys = ["O_ocupacao", "L_skel_px", "N_br"]
        dd = {kk: max(abs(o[3][kk] - outs[0][3][kk]) for o in outs) for kk in keys}
        rr = {"image_id": img_id, "m1_bitident": len(m1h) == 1, "m2_bitident": len(m2h) == 1,
              "m3_bitident": len(m3h) == 1, "lama_bitident": len(lamah) == 1,
              "max_dO": dd["O_ocupacao"], "max_dLskel": dd["L_skel_px"], "max_dNbr": dd["N_br"]}
        rep_rows.append(rr)
        print(f"  {img_id}: M1={rr['m1_bitident']} M2={rr['m2_bitident']} M3={rr['m3_bitident']} "
              f"LaMa={rr['lama_bitident']} | ΔO={dd['O_ocupacao']:.2e} ΔL={dd['L_skel_px']:.2e} ΔNbr={dd['N_br']}")
    with open(OUT_REP, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rep_rows[0].keys())); w.writeheader(); w.writerows(rep_rows)
    allbit = all(x["m1_bitident"] and x["m2_bitident"] and x["m3_bitident"] and x["lama_bitident"] for x in rep_rows)
    print(f"[A6] repetibilidade bit-a-bit em TODAS as máscaras/{len(sub)} imagens: {allbit}")
    print(f"[A6] -> {OUT.relative_to(C.ROOT)} + {OUT_REP.relative_to(C.ROOT)}")


if __name__ == "__main__":
    main()
