#!/usr/bin/env python3
"""Correctif 0.2.1 de Petit Nid : camera + test de chargement."""
from pathlib import Path

game = Path("game")
code = game / "scripts/world.gd"
source = code.read_text(encoding="utf-8")
old = "\tcamera.look_at(player.position, Vector3.UP)\n\tcamera.current = true\n\tadd_child(camera)"
new = "\tadd_child(camera)\n\tcamera.look_at(player.position, Vector3.UP)\n\tcamera.current = true"
if old not in source:
    if new not in source:
        raise SystemExit("Emplacement de la camera introuvable : echec ferme")
else:
    source = source.replace(old, new, 1)
    code.write_text(source, encoding="utf-8")

smoke = game / "tests/smoke_test.gd"
text = smoke.read_text(encoding="utf-8")
probe = '''\tif not game.camera.is_inside_tree():
\t\t_fail("Camera hors de la scene")
\t\treturn
\tvar toward_player: Vector3 = (game.player.global_position - game.camera.global_position).normalized()
\tif game.camera.global_basis.z.dot(-toward_player) < 0.95:
\t\t_fail("Camera mal orientee")
\t\treturn
'''
needle = "\tif game.zones.size() != 4:"
if probe not in text:
    if needle not in text:
        raise SystemExit("Test de camera : insertion impossible")
    text = text.replace(needle, probe + needle, 1)
    smoke.write_text(text, encoding="utf-8")

readme = game / "README.md"
with readme.open("a", encoding="utf-8") as f:
    f.write("\n\n## Correctif 0.2.1\nCamera orientee apres entree dans l'arbre de scene ; tests de camera ajoutes.\n")
print("Petit Nid correctif camera + test : OK")
