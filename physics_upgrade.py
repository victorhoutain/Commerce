#!/usr/bin/env python3
"""Petit Nid 0.5: collisions physiques, objets accessibles et camera confortable."""
from pathlib import Path
p = Path("game/scripts/world.gd")
s = p.read_text(encoding="utf-8")
def replace(before, after):
    global s
    if before not in s:
        raise RuntimeError("Ancre absente: " + repr(before[:90]))
    s = s.replace(before, after, 1)

replace("var egg_parent: Node3D\n", "var egg_parent: Node3D\nvar obstacle_points: Array = []\n")
replace("\t_build_belt()\n\t_build_player()", "\t_build_belt()\n\t_register_building_collisions()\n\t_make_roofs_transparent()\n\t_build_player()")
replace("func _tree(at: Vector3, seed_value: int) -> void:\n",
        "func _tree(at: Vector3, seed_value: int) -> void:\n\t_add_collision_cylinder(at, 0.63, 2.0, \"Tronc arbre\")\n".replace('\\"','"'))
replace("\t\t\tadd_child(detail)\n\nfunc _check_victory()",
        "\t\t\tadd_child(detail)\n\t\t\tif i % 3 == 0:\n\t\t\t\t_add_collision_cylinder(Vector3(x, 0.0, z), 0.65, 1.1, \"Roche\")\n\nfunc _check_victory()".replace('\\"','"'))
replace("\t\tvar rarity = _roll_zone_rarity(zone_id)\n\t\t_make_egg(rarity, Vector3(x, 0.68, z), false)",
        "\t\tif not _egg_position_accessible(x, z):\n\t\t\tcontinue\n\t\tvar rarity = _roll_zone_rarity(zone_id)\n\t\t_make_egg(rarity, Vector3(x, 0.68, z), false)")
replace("\tvar best_distance = 2.1\n\tfor egg in eggs:", "\tvar best_distance = 3.2\n\tfor egg in eggs:")
replace("\t\tif distance_now < best_distance:\n\t\t\tbest_distance = distance_now\n\t\t\tresult = egg",
        "\t\tvar interaction_range = 3.2 if bool(egg[\"belt\"]) else 2.1\n\t\tif distance_now < interaction_range and distance_now < best_distance:\n\t\t\tbest_distance = distance_now\n\t\t\tresult = egg".replace('\\"','"'))
replace("\t_belt_spawn()\n\t_make_world_pretty()",
        "\t_belt_spawn()\n\t_make_egg(0, Vector3(-14.4, 0.68, 4.4), false)\n\t_sign(\"1. UN OEUF ! [E]\", Vector3(-14.4, 2.4, 4.4), Color(\"795c8d\"), 23)\n\t_make_world_pretty()".replace('\\"','"'))
replace("func _unhandled_input(event: InputEvent) -> void:\n", """func _unhandled_input(event: InputEvent) -> void:
\tif event is InputEventMouseButton and event.pressed:
\t\tif event.button_index == MOUSE_BUTTON_WHEEL_UP:
\t\t\tcamera.size = maxf(16.0, camera.size - 1.5)
\t\t\treturn
\t\telif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
\t\t\tcamera.size = minf(34.0, camera.size + 1.5)
\t\t\treturn
""")
insert = """func _add_collision_cylinder(at: Vector3, radius: float, height: float, label: String) -> StaticBody3D:
\tvar solid := StaticBody3D.new()
\tsolid.name = "Obstacle - " + label
\tsolid.collision_layer = 1
\tsolid.collision_mask = 1
\tsolid.position = Vector3(at.x, at.y + height * 0.5, at.z)
\tvar collision := CollisionShape3D.new()
\tvar shape := CylinderShape3D.new()
\tshape.radius = radius
\tshape.height = height
\tcollision.shape = shape
\tsolid.add_child(collision)
\tadd_child(solid)
\tobstacle_points.append(Vector3(at.x, radius, at.z))
\treturn solid

func _add_collision_box(at: Vector3, volume: Vector3, label: String) -> StaticBody3D:
\tvar solid := StaticBody3D.new()
\tsolid.name = "Obstacle - " + label
\tsolid.collision_layer = 1
\tsolid.collision_mask = 1
\tsolid.position = at
\tvar collision := CollisionShape3D.new()
\tvar shape := BoxShape3D.new()
\tshape.size = volume
\tcollision.shape = shape
\tsolid.add_child(collision)
\tadd_child(solid)
\tif label != "Limite de la carte":
\t\tobstacle_points.append(Vector3(at.x, maxf(volume.x, volume.z) * 0.52, at.z))
\treturn solid

func _register_building_collisions() -> void:
\t_add_collision_box(Vector3(-30, 1.25, 13.1), Vector3(3.5, 2.5, 3.4), "Maison")
\t_add_collision_cylinder(Vector3(-26, 0, 5.5), 1.3, 1.0, "Incubateur")
\t_add_collision_box(Vector3(-19.5, 0.48, 11.4), Vector3(2.9, 0.9, 1.6), "Mangeoire")
\t_add_collision_box(Vector3(-12, 1.0, -6.1), Vector3(4.6, 0.85, 1.0), "Comptoir")
\tfor x in [-14.15, -9.85]:
\t\tfor z in [-6.5, -2.5]:
\t\t\t_add_collision_cylinder(Vector3(x, 0, z), 0.22, 2.5, "Poteau boutique")
\t_add_collision_box(Vector3(20, 0.55, -11), Vector3(21.6, 1.1, 3.45), "Tapis roulant")
\tfor x in [-37.8, 193.8]:
\t\t_add_collision_box(Vector3(x, 1.0, 0), Vector3(0.35, 2.0, 55.0), "Limite de la carte")
\tfor z in [-27.4, 27.4]:
\t\t_add_collision_box(Vector3(78, 1.0, z), Vector3(232.0, 2.0, 0.35), "Limite de la carte")

func _egg_position_accessible(x: float, z: float) -> bool:
\tfor spot in obstacle_points:
\t\tif Vector2(x, z).distance_to(Vector2(spot.x, spot.z)) < spot.y + 1.2:
\t\t\treturn false
\treturn true

func _make_roofs_transparent() -> void:
\tfor part in get_children():
\t\tif not (part is MeshInstance3D):
\t\t\tcontinue
\t\tif part.name == "Toit boutique" or part.name == "Toiture":
\t\t\tvar translucent := StandardMaterial3D.new()
\t\t\ttranslucent.albedo_color = Color("eab9cb", 0.50)
\t\t\ttranslucent.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
\t\t\ttranslucent.roughness = 0.9
\t\t\tpart.material_override = translucent

"""
marker="func _load_balance() -> void:\n"
if marker not in s: raise RuntimeError("Ancre de fonctions absente")
s=s.replace(marker,insert+marker,1)
replace("\tsunlight.light_energy = 0.8", "\tsunlight.light_energy = 0.8\n\tsunlight.shadow_enabled = true")
p.write_text(s, encoding="utf-8")
print("PETIT NID 0.5 : collisions et collecte securisee")
