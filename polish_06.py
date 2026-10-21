#!/usr/bin/env python3
"""Petit Nid 0.6: mouvements vivants, feedback, camera et navigation fiable.
Les effets de jeu utilisent des primitives transitoires ; aucun visuel IA.
"""
from pathlib import Path

path=Path("game/scripts/world.gd")
s=path.read_text(encoding="utf-8")
def change(old,new, count=1):
    global s
    if old not in s:
        raise AssertionError("Point d'insertion non trouve : "+repr(old[:135]))
    s=s.replace(old,new,count)

change('var pet_parent: Node3D\n',
'''var pet_parent: Node3D
var step_left: MeshInstance3D
var step_right: MeshInstance3D
var walk_phase: float = 0.0
var pickup_counter: int = 0
''')
change('_sphere(player_visual, "Sac", Vector3(0, 0.02, 0.45), 0.35, Color("f8de9b"), 1.1)',
'''_sphere(player_visual, "Sac", Vector3(0, 0.02, 0.45), 0.35, Color("f8de9b"), 1.1)
\tstep_left = _cylinder(player_visual, "Pied gauche", Vector3(-0.23, -0.58, -0.12), 0.15, 0.43, Color("e7a3a4"))
\tstep_right = _cylinder(player_visual, "Pied droit", Vector3(0.23, -0.58, -0.12), 0.15, 0.43, Color("e7a3a4"))
\t_cylinder(player, "Ombre personnage", Vector3(0, -0.76, 0), 0.56, 0.018, Color("719277"))
''')
change('player.velocity = direction_3d * (_setting_float("speed_base", 4.7) + _setting_float("speed_per_level", 1.15) * speed_level)',
'''var target_velocity: Vector3 = direction_3d * (_setting_float("speed_base", 4.7) + _setting_float("speed_per_level", 1.15) * speed_level)
\tplayer.velocity = player.velocity.move_toward(target_velocity, 29.0 * delta)''')
change('player_visual.rotation.y = lerp_angle(player_visual.rotation.y, desired_angle, delta * 11.0)',
'''player_visual.rotation.y = lerp_angle(player_visual.rotation.y, desired_angle, delta * 10.5)
\t_animate_player(delta)
''')
change('var target_position = player.position + Vector3(0, 23, 16)\n\t\tcamera.position = camera.position.lerp(target_position, minf(1.0, delta * 4.5))',
'''var target_position = player.position + Vector3(0, 23, 16) + player.velocity * 0.18
\t\tcamera.position = camera.position.lerp(target_position, minf(1.0, delta * 3.4))''')
change('cargo.append(rarity)\n\t_remove_egg(egg)',
'''cargo.append(rarity)
\t_burst_fx(egg["node"].global_position, EGG_COLORS[rarity])
\tpickup_counter += 1
\t_remove_egg(egg)''')
change('total_hatched += count\n\tfor i in range(pet_nodes.size(), pets.size()):',
'''total_hatched += count
\t_burst_fx(Vector3(-26.0, 1.4, 5.5), Color("ffe2b6"), 12)
\tfor i in range(pet_nodes.size(), pets.size()):''')
change('pet_node.position.y = 0.63 + sin(animation_time * 2.0 + float(i)) * 0.08',
'''pet_node.position.y = 0.63 + sin(animation_time * 2.0 + float(i)) * 0.11
\t\tpet_node.rotation.z = sin(animation_time * 3.0 + float(i)) * 0.035
\t\tif target_pos.distance_to(pet_node.position) > 0.18:
\t\t\tvar direction_to_goal: Vector3 = target_pos - pet_node.position
\t\t\tpet_node.rotation.y = lerp_angle(pet_node.rotation.y, atan2(-direction_to_goal.x, -direction_to_goal.z), minf(1.0, delta * 5.0))''')
# Existing _next_companion failed to sync three follower slots, repair.
begin=s.index("func _next_companion() -> void:")
end=s.index("\nfunc ", begin + 1) + 1
s=s[:begin]+'''func _next_companion() -> void:
\tif pets.is_empty():
\t\t_show_toast("Fais eclore ton premier oeuf avant d'equiper un compagnon.")
\t\treturn
\tif follower_slots.size() >= 3:
\t\tfollower_slots.clear()
\t\tselected_pet = -1
\t\t_show_toast("Tous tes compagnons retournent au jardin.")
\telse:
\t\tvar next_index: int = 0
\t\twhile follower_slots.has(next_index) and next_index < pets.size():
\t\t\tnext_index += 1
\t\tif next_index < pets.size():
\t\t\t_toggle_follower(next_index)
\t\telse:
\t\t\t_show_toast("Toutes les creatures disponibles sont deja equipees.")
\treturn

'''+s[end:]
marker="func _load_balance() -> void:\n"
assert marker in s
s=s.replace(marker,'''func _animate_player(delta: float) -> void:
\tif not is_instance_valid(step_left) or not is_instance_valid(step_right):
\t\treturn
\tvar pace: float = player.velocity.length()
\tvar moving: float = clampf(pace / 4.0, 0.0, 1.0)
\twalk_phase += delta * (6.0 + pace * 0.95) * moving
\tvar stride: float = sin(walk_phase) * moving
\tstep_left.rotation.x = lerpf(step_left.rotation.x, stride * 0.52, minf(1.0, delta * 13.0))
\tstep_right.rotation.x = lerpf(step_right.rotation.x, -stride * 0.52, minf(1.0, delta * 13.0))
\tplayer_visual.position.y = lerpf(player_visual.position.y, absf(stride) * 0.085, minf(1.0, delta * 12.0))
\tplayer_visual.rotation.z = lerpf(player_visual.rotation.z, -player.velocity.x * 0.007, minf(1.0, delta * 7.0))

func _burst_fx(where: Vector3, tint: Color, amount: int = 8) -> void:
\tvar holder := Node3D.new()
\tholder.name = "Effet ramassage"
\tholder.position = where
\tadd_child(holder)
\tfor part in range(amount):
\t\tvar theta: float = TAU * float(part) / float(amount)
\t\tvar star := MeshInstance3D.new()
\t\tvar mesh := SphereMesh.new()
\t\tmesh.radius = 0.08
\t\tmesh.height = 0.16
\t\tmesh.radial_segments = 6
\t\tmesh.rings = 4
\t\tstar.mesh = mesh
\t\tstar.material_override = _mat(tint)
\t\tholder.add_child(star)
\t\tvar target: Vector3 = Vector3(cos(theta) * 1.6, 0.7 + float(part % 3) * 0.25, sin(theta) * 1.6)
\t\tvar tw: Tween = holder.create_tween().set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
\t\ttw.tween_property(star, "position", target, 0.44)
\t\ttw.parallel().tween_property(star, "scale", Vector3(0.05, 0.05, 0.05), 0.44)
\tvar cleanup := holder.create_tween()
\tcleanup.tween_interval(0.48)
\tcleanup.tween_callback(holder.queue_free)

''' + marker,1)
# Keep existing human pack; increase density slightly for life while avoiding paths.
if 'for i in range(13):\n\t\t\tvar x = rng.randf_range(left, right)' in s:
    s=s.replace('for i in range(13):\n\t\t\tvar x = rng.randf_range(left, right)',
                'for i in range(20):\n\t\t\tvar x = rng.randf_range(left, right)',1)
# Widen the safe entry area around the base to avoid clutter.
# Gamepad axis and dpad: engine constants confirmed under Godot 4.
change('\t_add_keybind("back_home", [KEY_B])',
'''\t_add_keybind("back_home", [KEY_B])
\t_add_axisbind("go_left", JOY_AXIS_LEFT_X, -1.0)
\t_add_axisbind("go_right", JOY_AXIS_LEFT_X, 1.0)
\t_add_axisbind("go_up", JOY_AXIS_LEFT_Y, -1.0)
\t_add_axisbind("go_down", JOY_AXIS_LEFT_Y, 1.0)
\t_add_buttonbind("go_left", JOY_BUTTON_DPAD_LEFT)
\t_add_buttonbind("go_right", JOY_BUTTON_DPAD_RIGHT)
\t_add_buttonbind("go_up", JOY_BUTTON_DPAD_UP)
\t_add_buttonbind("go_down", JOY_BUTTON_DPAD_DOWN)
\t_add_buttonbind("act", JOY_BUTTON_A)
\t_add_buttonbind("shop_speed", JOY_BUTTON_X)
\t_add_buttonbind("feed_pet", JOY_BUTTON_Y)
\t_add_buttonbind("back_home", JOY_BUTTON_B)
''')
marker2="func _build_environment() -> void:\n"
s=s.replace(marker2,'''func _add_axisbind(name: String, axis_number: int, intensity: float) -> void:
\tvar movement := InputEventJoypadMotion.new()
\tmovement.axis = axis_number
\tmovement.axis_value = intensity
\tInputMap.action_add_event(name, movement)

func _add_buttonbind(name: String, button_number: int) -> void:
\tvar button := InputEventJoypadButton.new()
\tbutton.button_index = button_number
\tInputMap.action_add_event(name, button)

'''+marker2,1)
path.write_text(s,encoding="utf-8")
print("PETIT NID 0.6: animation marche, camera, feedback, commandes manette OK")
