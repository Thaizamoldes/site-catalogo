#!/usr/bin/env python3
"""Gera as imagens otimizadas do catálogo.

Uso:
    pip install pillow pillow-heif
    python3 build.py

Lê as fotos originais em fotos/<Categoria>/<Nome do modelo>.(jpg|png|heif...)
e gera, dentro de docs/ (a pasta publicada do site):
  - docs/img/<slug>-400.webp   miniatura da grade
  - docs/img/<slug>-800.webp   miniatura para telas de alta densidade
  - docs/img/<slug>-1200.webp  foto ampliada (ao clicar)
  - docs/modelos.js            lista de modelos usada pelo site

Para adicionar um modelo novo basta colocar a foto na pasta da categoria
(ou criar uma pasta nova) e rodar o script de novo.
"""
import json
import os
import re
import unicodedata

from PIL import Image, ImageOps

try:
    import pillow_heif

    pillow_heif.register_heif_opener()
except ImportError:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
FOTOS = os.path.join(ROOT, "fotos")
OUT = os.path.join(ROOT, "docs")
IMG = os.path.join(OUT, "img")
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heif", ".heic"}
SIZES = (400, 800, 1200)
RATIO = 4 / 3  # todas as fotos são exibidas em retrato 3:4

# Ordem em que as categorias aparecem no site; pastas fora da lista vão ao final.
ORDEM = [
    "Vestidos",
    "Saias",
    "Calças, Shorts e Macacões",
    "Blusas, Camisas e Coletes",
    "Casacos e Jaquetas",
]


def slug(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def load(path):
    im = ImageOps.exif_transpose(Image.open(path))
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, "white")
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert("RGB")
    # Recorta para 3:4 (centralizado) para a grade ficar uniforme.
    w, h = im.size
    if abs(h / w - RATIO) > 0.02:
        if h / w > RATIO:
            nh = round(w * RATIO)
            top = (h - nh) // 2
            im = im.crop((0, top, w, top + nh))
        else:
            nw = round(h / RATIO)
            left = (w - nw) // 2
            im = im.crop((left, 0, left + nw, h))
    return im


def main():
    os.makedirs(IMG, exist_ok=True)
    cats = sorted(
        (d for d in os.listdir(FOTOS) if os.path.isdir(os.path.join(FOTOS, d))),
        key=lambda c: (ORDEM.index(c) if c in ORDEM else len(ORDEM), c),
    )
    modelos, usados = [], set()
    for cat in cats:
        files = sorted(
            f for f in os.listdir(os.path.join(FOTOS, cat))
            if os.path.splitext(f)[1].lower() in EXTS
        )
        for f in files:
            nome = unicodedata.normalize("NFC", os.path.splitext(f)[0]).strip()
            s = slug(nome)
            usados.add(s)
            im = load(os.path.join(FOTOS, cat, f))
            larguras = []
            for size in SIZES:
                # Nunca amplia: fotos pequenas ficam no tamanho original.
                w = min(size, im.width)
                dest = os.path.join(IMG, f"{s}-{size}.webp")
                if w not in larguras:
                    larguras.append(w)
                im.resize((w, round(w * RATIO)), Image.LANCZOS).save(
                    dest, "WEBP", quality=78 if size > 400 else 72, method=6
                )
            modelos.append({"n": nome, "c": cat, "s": s, "w": im.width})
            print(f"{cat:20} {nome}")

    # Remove imagens de modelos que não existem mais.
    for f in os.listdir(IMG):
        if f.rsplit("-", 1)[0] not in usados:
            os.remove(os.path.join(IMG, f))

    with open(os.path.join(OUT, "modelos.js"), "w", encoding="utf-8") as fh:
        fh.write("window.MODELOS=")
        json.dump(modelos, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write(";\n")
    print(f"\n{len(modelos)} modelos em {len(cats)} categorias.")


if __name__ == "__main__":
    main()
