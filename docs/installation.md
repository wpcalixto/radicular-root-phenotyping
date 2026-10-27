# Installation

1. Install Python 3.9 (the verification used 3.9.6).
2. `python -m pip install -r requirements.txt`.
3. For figures with LaTeX labels, install a TeX distribution providing `latex` and `dvipng`.
4. For LaMa conditioning (05A_pretratamento.py) the first run downloads `big-lama.pt` (205,803,670 bytes, release v0.1.0 of
   simple-lama-inpainting, Apache-2.0; LaMa, Apache-2.0) or uses the file given by the environment variable `LAMA_MODEL`.
5. For the PRMI scripts (06A, 06B, 08A, A8, sel_prmi_artigo), download PRMI from Zenodo 10.5281/zenodo.5974905 (CC0 1.0).
6. For 06B training, use Google Colab or an equivalent GPU environment (see docs/06B_training_provenance.md).
