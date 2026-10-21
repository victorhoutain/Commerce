#!/usr/bin/env python3
"""Importer uniquement des ressources 3D du kit Nature de Kenney (CC0)."""
from pathlib import Path
from zipfile import ZipFile
import json, sys

if len(sys.argv) != 2:
    raise SystemExit("Usage : import_human_art.py kenney_nature-kit.zip")
zip_path = Path(sys.argv[1])
game = Path("game")
folder = game / "assets" / "kenney_nature"
folder.mkdir(parents=True, exist_ok=True)
categories = {
    "trees": ("tree", 8),
    "bushes": ("bush", 4),
    "rocks": ("rock", 5),
}
picked = {}
with ZipFile(zip_path) as archive:
    files = sorted(name for name in archive.namelist() if name.lower().endswith(".glb"))
    if not files:
        raise SystemExit("Le ZIP Kenney ne contient aucun modele GLB.")
    for category, (keyword, count) in categories.items():
        matches = [x for x in files if keyword in Path(x).stem.lower()]
        if not matches:
            raise SystemExit("Modeles Kenney absents : " + keyword)
        # Espacer les choix pour varier les formes et les silhouettes.
        offsets = [round(i * (len(matches) - 1) / max(1, min(count,len(matches)) - 1)) for i in range(min(count,len(matches)))]
        picked[category] = []
        for index, offset in enumerate(offsets):
            original = matches[offset]
            suffix = f"{category}_{index:02d}.glb"
            (folder / suffix).write_bytes(archive.read(original))
            picked[category].append("res://assets/kenney_nature/" + suffix)
metadata=game/"data"/"human_art.json"
metadata.write_text(json.dumps(picked,indent=2),encoding="utf-8")
(game / "CREDITS_ART_HUMAIN.txt").write_text(
    "PETIT NID - RESSOURCES HUMAINES\\n\\n"
    "Decors 3D : Kenney, Nature Kit, version originale 2020.\\n"
    "Source : https://kenney.nl/assets/nature-kit\\n"
    "Licence : Creative Commons CC0 1.0.\\n"
    "Aucune ressource graphique generee par IA n'a ete utilisee.\\n"
    "Modeles importes sans creation ou retouche generative.\\n",
    encoding="utf-8"
)
print("Arbres, buissons et rochers Kenney importes :", {k:len(v) for k,v in picked.items()})
