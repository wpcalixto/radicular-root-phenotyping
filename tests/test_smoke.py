#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title:
    Smoke tests of the Radicular distribution
File type:
    Test
Purpose:
    Check that every script compiles, that notebooks are valid JSON notebooks, that config.py imports and,
    when the Dataset is available, that its checksums match and that a fast analysis (A9b_Ed_ic.py)
    reproduces its expected output; with --compare <workspace>, compare all regenerated outputs of a
    workspace with tests/expected_outputs_sha256.csv.
Repository:
    Software_Radicular_v1.0.0
Version:
    v1.0.0
Date:
    2026-10-26
Developer:
    Prof. Wesley Pacheco Calixto
Authors:
    Wesley Pacheco Calixto; Universidade de Coimbra (UC), Portugal; Universidade Federal de Goiás (UFG), Brazil;
    Instituto Federal de Educação, Ciência e Tecnologia de Goiás (IFG), Brazil (direction). Code prepared with an
    AI coding assistant (Claude, Anthropic) under the author's direction for the v1.0.0 distribution
Corresponding author:
    Wesley Pacheco Calixto
License:
    MIT (see LICENSE)
Citation:
    Radicular Software record on Zenodo (DOI 10.5281/zenodo.23679263)
Related publication:
    Auditable longitudinal root phenotyping in rhizotrons using Frangi--U-Net fusion and apparent conductivity
Inputs:
    - scripts/, tools/
    - optional environment variable RADICULAR_DATASET: path to Dataset_Radicular_v1.0.0
Outputs:
    - test report on standard output; a temporary directory removed at the end
Dependencies:
    - Python standard library; numpy (imported by A9b_Ed_ic.py)
Execution:
    python tests/test_smoke.py   (or: python -m pytest tests/test_smoke.py)
Portability notes:
    Paths are relative to this file; no machine-specific path is used.
Reproducibility notes:
    A9b_Ed_ic.py uses seed 42 and B = 5000.
Warnings:
    Dataset tests are skipped when RADICULAR_DATASET is not set.
"""
import hashlib
import json
import os
import py_compile
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET = os.environ.get("RADICULAR_DATASET", "")


def sha256(path):
    """
    Purpose:
        Compute the SHA-256 checksum of a file.
    Parameters:
        path (str): File path.
    Returns:
        str: Hexadecimal digest.
    Raises:
        OSError: If the file cannot be read.
    Notes:
        Reads the file in 1 MiB blocks.
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def test_compile():
    """
    Purpose:
        Compile every Python file of scripts/ and tools/.
    Parameters:
        None.
    Returns:
        None
    Raises:
        AssertionError: If any file fails to compile.
    Notes:
        Bytecode is written to a temporary directory.
    """
    tmp = tempfile.mkdtemp()
    n = 0
    for base in ("scripts", "tools", "tests"):
        for d, _, fs in os.walk(os.path.join(ROOT, base)):
            for f in fs:
                if f.endswith(".py"):
                    py_compile.compile(os.path.join(d, f), cfile=os.path.join(tmp, f + "c"), doraise=True)
                    n += 1
    shutil.rmtree(tmp)
    assert n >= 79, n


def test_notebooks():
    """
    Purpose:
        Check that notebooks are valid JSON with nbformat 4 structure and a header cell.
    Parameters:
        None.
    Returns:
        None
    Raises:
        AssertionError: If a notebook is malformed.
    Notes:
        Shell commands (!pip) inside code cells are notebook syntax and are not compiled as Python.
    """
    for f in os.listdir(os.path.join(ROOT, "scripts")):
        if f.endswith(".ipynb"):
            nb = json.load(open(os.path.join(ROOT, "scripts", f), encoding="utf-8"))
            assert nb.get("nbformat") == 4 and nb["cells"][0]["cell_type"] == "markdown", f


def test_config():
    """
    Purpose:
        Import scripts/config.py and check the directory constants.
    Parameters:
        None.
    Returns:
        None
    Raises:
        AssertionError: If config.py does not define the expected tree.
    Notes:
        Importing config.py has no side effects.
    """
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import config as C
    assert C.ROOT == __import__("pathlib").Path(ROOT).resolve() and len(C.RIZOTRONS) == 12 and len(C.COLETAS) == 7


def test_dataset_checksums():
    """
    Purpose:
        Verify the Dataset checksum file when the Dataset path is given.
    Parameters:
        None.
    Returns:
        None
    Raises:
        AssertionError: If any checksum differs.
    Notes:
        Skipped when RADICULAR_DATASET is not set.
    """
    if not DATASET:
        print("  skipped: RADICULAR_DATASET not set")
        return
    bad = 0
    for line in open(os.path.join(DATASET, "checksums", "checksums_sha256.txt"), encoding="utf-8"):
        if line.strip() and not line.startswith("#"):
            h, rel = line.rstrip("\n").split("  ", 1)
            bad += sha256(os.path.join(DATASET, rel)) != h
    assert bad == 0, bad


def test_a9b_reproduction():
    """
    Purpose:
        Re-run A9b_Ed_ic.py in a temporary workspace and compare its output with the Dataset.
    Parameters:
        None.
    Returns:
        None
    Raises:
        AssertionError: If the regenerated A9b_Ed_ic.csv differs from the archived file.
    Notes:
        Skipped when RADICULAR_DATASET is not set.
    """
    if not DATASET:
        print("  skipped: RADICULAR_DATASET not set")
        return
    ws = os.path.join(tempfile.mkdtemp(), "ws")
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "prepare_workspace.py"), "--dataset", DATASET,
                    "--software", ROOT, "--workspace", ws, "--parts", "metrics"], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable, os.path.join(ws, "scripts", "A9b_Ed_ic.py")], check=True, cwd=ws, stdout=subprocess.DEVNULL)
    ok = sha256(os.path.join(ws, "metricas", "A9b_Ed_ic.csv")) == EXPECTED["metricas/A9b_Ed_ic.csv"][0]
    shutil.rmtree(os.path.dirname(ws))
    assert ok


EXPECTED = {}
for _r in __import__("csv").DictReader(open(os.path.join(ROOT, "tests", "expected_outputs_sha256.csv"), encoding="utf-8")):
    EXPECTED[_r["workspace_path"]] = (_r["sha256"], _r["comparison"])


def compare(ws):
    """
    Purpose:
        Compare the regenerated outputs of a workspace with tests/expected_outputs_sha256.csv.
    Parameters:
        ws (str): Workspace in which the pipeline was executed.
    Returns:
        int: Number of outputs that differ or are missing.
    Raises:
        No exception is raised explicitly.
    Notes:
        Entries marked 'tolerance' or 'pixel' are reported but are not expected to match byte for byte.
    """
    bad = 0
    for rel, (h, how) in sorted(EXPECTED.items()):
        p = os.path.join(ws, rel)
        if not os.path.exists(p):
            print("MISSING", rel); bad += how == "sha256"; continue
        if sha256(p) != h:
            print(("DIFFERS " if how == "sha256" else "EXPECTED-DIFF (" + how + ") ") + rel); bad += how == "sha256"
    print("compared:", len(EXPECTED), "| unexpected differences:", bad)
    return bad


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--compare":
        sys.exit(1 if compare(sys.argv[2]) else 0)
    for t in (test_compile, test_notebooks, test_config, test_dataset_checksums, test_a9b_reproduction):
        t()
        print("PASS", t.__name__)
