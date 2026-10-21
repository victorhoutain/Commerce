#!/usr/bin/env python3
"""Petit Nid 0.3 — transition vers jeu jouable a menus."""
from pathlib import Path
import json

game = Path("game")
path = game / "scripts/world.gd"
src = path.read_text(encoding="utf-8")

def change(old, new, count=1):
    global src
    if new in src:
        return
    assert old in src, f"Impossible de trouver la cible : {old[:90]!r}"
    src = src.replace(old, new, count)

change("var selected_pet = -1\n", "var selected_pet = -1\nvar follower_slots: Array = []\nvar victory_unlocked: bool = false\n")

change("\t_build_hud()\n\tegg_parent = Node3D.new()",
       "\t_build_hud()\n\t# L'ancien HUD reste present pour fournir les interactions contextuelles.\n\tfor node in get_children():\n\t\tif node is CanvasLayer:\n\t\t\tnode.visible = false\n\tegg_parent = Node3D.new()")

change("\t_belt_spawn()\n\t_show_toast(",
       "\t_belt_spawn()\n\t_make_world_pretty()\n\tvar overlay = CanvasLayer.new()\n\toverlay.name = \"Interface de jeu\"\n\toverlay.set_script(load(\"res://scripts/game_ui.gd\"))\n\tadd_child(overlay)\n\t_show_toast(")

change("\tif selected_pet == -1:\n\t\t_show_toast(",
       "\tfollower_slots = [selected_pet] if selected_pet >= 0 else []\n\tif selected_pet == -1:\n\t\t_show_toast(")

change("\t\tif i == selected_pet:\n\t\t\tvar offset = Vector3(1.25, 0.0, 1.45)\n\t\t\ttarget_pos = player.position + offset",
       "\t\tif follower_slots.has(i):\n\t\t\tvar slot: int = follower_slots.find(i)\n\t\t\tvar offset = Vector3(1.1 + float(slot) * 0.9, 0.0, 1.35 + float(slot) * 0.35)\n\t\t\ttarget_pos = player.position + offset")

change("\t\t\"selected_pet\": selected_pet,\n\t\t\"total_hatched\":",
       "\t\t\"selected_pet\": selected_pet,\n\t\t\"followers\": follower_slots,\n\t\t\"total_hatched\":")

change("\tselected_pet = clampi(int(parsed.get(\"selected_pet\", -1)), -1, pets.size() - 1)\n",
       """\tselected_pet = clampi(int(parsed.get("selected_pet", -1)), -1, pets.size() - 1)
\tfollower_slots.clear()
\tvar saved_followers = parsed.get("followers", [])
\tif typeof(saved_followers) == TYPE_ARRAY:
\t\tfor follower in saved_followers:
\t\t\tvar slot_id: int = int(follower)
\t\t\tif slot_id >= 0 and slot_id < pets.size() and not follower_slots.has(slot_id) and follower_slots.size() < 3:
\t\t\t\tfollower_slots.append(slot_id)
\tif follower_slots.is_empty() and selected_pet >= 0:
\t\tfollower_slots.append(selected_pet)
\tselected_pet = int(follower_slots[0]) if not follower_slots.is_empty() else -1
""")

# Progression finissable, sans supprimer le mode collection libre.
change('\t\t"followers": follower_slots,\n\t\t"total_hatched":',
       '\t\t"followers": follower_slots,\n\t\t"victory_unlocked": victory_unlocked,\n\t\t"total_hatched":')
change('\tselected_pet = int(follower_slots[0]) if not follower_slots.is_empty() else -1\n',
       '\tselected_pet = int(follower_slots[0]) if not follower_slots.is_empty() else -1\n\tvictory_unlocked = bool(parsed.get("victory_unlocked", false))\n')
change('\t_show_toast("Bienvenue dans %s !" % str(zone["name"]), 5)',
       '\t_show_toast("Bienvenue dans %s !" % str(zone["name"]), 5)\n\t_check_victory()')
change('\t_show_toast("%d creature(s) nee(s) !  +%d pieces" % [count, gained], 5)',
       '\t_show_toast("%d creature(s) nee(s) !  +%d pieces" % [count, gained], 5)\n\t_check_victory()')

# Decors humains Kenney : remplacement des silhouettes de test.
change('var follower_slots: Array = []\n',
       'var follower_slots: Array = []\nvar human_trees: Array = []\nvar human_bushes: Array = []\nvar human_rocks: Array = []\n')
change('\t_load_balance()\n\t_register_controls()',
       '\t_load_balance()\n\t_load_human_art()\n\t_register_controls()')
change('func _tree(at: Vector3, seed_value: int) -> void:\n',
       'func _tree(at: Vector3, seed_value: int) -> void:\n\tif human_trees.size() > 0:\n\t\tvar tree = human_trees[seed_value % human_trees.size()].instantiate()\n\t\ttree.position = at\n\t\ttree.scale = Vector3.ONE * 4.0\n\t\tadd_child(tree)\n\t\treturn\n')
change('\t_belt_spawn()\n\t_make_world_pretty()',
       '\t_belt_spawn()\n\t_make_world_pretty()\n\t_place_natural_details()')

# Ajouter fonctions avant le modele d'animaux.
marker="func _make_pet_model(index: int) -> void:\n"
extra="""func _load_human_art() -> void:
\tvar file_path = "res://data/human_art.json"
\tif not FileAccess.file_exists(file_path):
\t\treturn
\tvar file = FileAccess.open(file_path, FileAccess.READ)
\tif file == null:
\t\treturn
\tvar art_data = JSON.parse_string(file.get_as_text())
\tfile.close()
\tif typeof(art_data) != TYPE_DICTIONARY:
\t\treturn
\tfor item in art_data.get("trees", []):
\t\tvar resource = load(str(item))
\t\tif resource is PackedScene:
\t\t\thuman_trees.append(resource)
\tfor item in art_data.get("bushes", []):
\t\tvar resource = load(str(item))
\t\tif resource is PackedScene:
\t\t\thuman_bushes.append(resource)
\tfor item in art_data.get("rocks", []):
\t\tvar resource = load(str(item))
\t\tif resource is PackedScene:
\t\t\thuman_rocks.append(resource)

func _place_natural_details() -> void:
\tfor zone_i in range(zones.size()):
\t\tvar zone = zones[zone_i]
\t\tvar left = float(zone["x_min"]) + 5.0
\t\tvar right = float(zone["x_max"]) - 5.0
\t\tfor i in range(13):
\t\t\tvar x = rng.randf_range(left, right)
\t\t\tvar z = rng.randf_range(-22, 22)
\t\t\tif absf(z - 2.0) < 3.2:
\t\t\t\tcontinue
\t\t\tvar scene: PackedScene = null
\t\t\tvar factor: float = 2.8
\t\t\tif i % 3 == 0 and not human_rocks.is_empty():
\t\t\t\tscene = human_rocks[(i + zone_i) % human_rocks.size()]
\t\t\t\tfactor = 2.6
\t\t\telif not human_bushes.is_empty():
\t\t\t\tscene = human_bushes[(i + zone_i) % human_bushes.size()]
\t\t\tif scene == null:
\t\t\t\tcontinue
\t\t\tvar detail = scene.instantiate()
\t\t\tdetail.position = Vector3(x, 0, z)
\t\t\tdetail.scale = Vector3.ONE * factor
\t\t\tdetail.rotation.y = rng.randf_range(0, TAU)
\t\t\tadd_child(detail)

func _check_victory() -> void:
\tif victory_unlocked or unlocked_zone < zones.size() - 1 or total_hatched < 20:
\t\treturn
\tvar found_mythic: bool = false
\tfor item in pets:
\t\tif int(item["kind"]) == 3:
\t\t\tfound_mythic = true
\t\t\tbreak
\tif not found_mythic:
\t\treturn
\tvictory_unlocked = true
\tcoins += 500
\t_save_progress()
\tvar layer = get_node_or_null("Interface de jeu")
\tif layer != null:
\t\tlayer._show_menu("victory")

func _toggle_follower(index: int) -> void:
\tif index < 0 or index >= pets.size():
\t\treturn
\tif follower_slots.has(index):
\t\tfollower_slots.erase(index)
\t\t_show_toast("Compagnon retourne au jardin.")
\telif follower_slots.size() >= 3:
\t\t_show_toast("Maximum 3 compagnons. Retire-en un avant.")
\t\treturn
\telse:
\t\tfollower_slots.append(index)
\t\t_show_toast("Une nouvelle creature t'accompagne !")
\tselected_pet = int(follower_slots[0]) if not follower_slots.is_empty() else -1
\t_save_progress()

func _make_world_pretty() -> void:
\t# Decoration geometrique de developpement, sans ressources IA.
\t# Les futurs vrais decors proviendront de packs humains valides.
\tvar colors = [
\t\tColor("#F6D7B4"), Color("#F1D4EC"), Color("#B5E9DB"),
\t\tColor("#D5D9F4")
\t]
\tfor zindex in range(zones.size()):
\t\tvar zone: Dictionary = zones[zindex]
\t\tvar start_x: float = float(zone["x_min"])
\t\tvar end_x: float = float(zone["x_max"])
\t\tvar center: float = (start_x + end_x) / 2.0
\t\t# Tapis de petites pierres pour rejoindre les mondes.
\t\tfor k in range(12):
\t\t\tvar stone_x: float = start_x + 3.0 + float(k) * (end_x - start_x - 6.0) / 12.0
\t\t\t_cylinder(self, "Pave", Vector3(stone_x, 0.045, 2), 0.8, 0.08, colors[zindex])
\t\t# Un rond-point fleuri distinct par zone.
\t\t_cylinder(self, "Rond point fleuri", Vector3(center, 0.035, 15), 3.1, 0.08, colors[zindex])
\t\tfor petal in range(8):
\t\t\tvar angle: float = TAU * float(petal) / 8.0
\t\t\tvar pos = Vector3(center + cos(angle) * 2.0, 0.35, 15 + sin(angle) * 2.0)
\t\t\t_sphere(self, "Fleur geante", pos, 0.38, Color("#FFE8F3") if zindex % 2 == 0 else Color("#FAE9B0"), 0.5)
\t\t# Point de repere dans la zone.
\t\t_sign("%d / 4" % (zindex + 1), Vector3(center, 3.2, 15.0), Color("#596B7A"), 37)
\t# Petits points lumineux decoratifs autour de la base.
\tfor m in range(11):
\t\tvar star_angle: float = TAU * float(m) / 11.0
\t\t_sphere(self, "Perle de jardin", Vector3(-25.0 + cos(star_angle) * 6.6, 0.25, 8.5 + sin(star_angle) * 5), 0.22, Color("#FFF6DE"))
\t# Promenade principale lisible dans chaque zone.
\t_sign("BOUTIQUE : SAC + VITESSE", Vector3(-12, 4.35, -4.5), Color("#98707F"), 26)
\t_sign("LA CARTE [M]  |  COLLECTION [K]", Vector3(-22, 4.2, 11.0), Color("#476C68"), 23)

"""
assert marker in src
src=src.replace(marker, extra+marker, 1)
path.write_text(src, encoding="utf-8")

balance_path=game/"data/balance.json"
balance=json.loads(balance_path.read_text(encoding="utf-8"))
balance["bag_upgrade_costs"]=[20,45,100,210]
balance["speed_price_base"]=15
balance["hatch_rewards"]=[16,33,72,160]
balance["passive_income_interval"]=6.0
balance["field_spawn_interval"]=1.8
balance["belt_spawn_interval"]=7.0
for zone,price,hatches in zip(balance["zones"],[0,80,260,700],[0,2,8,17]):
    zone["unlocks_for_coins"]=price
    zone["unlocks_after_hatches"]=hatches
balance_path.write_text(json.dumps(balance,ensure_ascii=False,indent=2)+"\n", encoding="utf-8")

config=game/"project.godot"
proj=config.read_text(encoding="utf-8")
proj=proj.replace('config/name="Petit Nid — Prototype"','config/name="Petit Nid"')
proj=proj.replace('config/description="Un petit jeu 3D de collecte d\'oeufs et de compagnons"','config/description="Jeu 3D de collection, exploration et creatures"')
config.write_text(proj, encoding="utf-8")
print("Petit Nid 0.3 : menu, collection, suiveurs, objectifs et 4 mondes OK")
