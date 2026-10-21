extends SceneTree

func _initialize() -> void:
	call_deferred("_run")

func _fail(detail: String) -> void:
	push_error("PETIT NID 0.6 : " + detail)
	paused = false
	quit(1)

func _run() -> void:
	var scene: PackedScene = load("res://scenes/main.tscn")
	if scene == null:
		_fail("La scene est introuvable")
		return
	var world = scene.instantiate()
	root.add_child(world)
	await physics_frame
	var overlay = world.get_node_or_null("Interface de jeu")
	if overlay == null:
		_fail("Interface principale absente")
		return
	overlay._play()
	if world.step_left == null or world.step_right == null:
		_fail("Animation du personnage absente")
		return
	if world.step_left.get_parent() != world.player_visual:
		_fail("Pieds non relies au modele du personnage")
		return
	if not InputMap.has_action("go_left"):
		_fail("Commandes de jeu manquantes")
		return
	var controller_events: int = 0
	for mapped in InputMap.action_get_events("go_left"):
		if mapped is InputEventJoypadMotion or mapped is InputEventJoypadButton:
			controller_events += 1
	if controller_events < 2:
		_fail("Controles manette non enregistres")
		return
	world.player.velocity = Vector3(4.5, 0, 0)
	world._animate_player(0.2)
	if world.walk_phase <= 0:
		_fail("Animation de deplacement inactive")
		return
	var phase_before: float = world.walk_phase
	world._animate_player(0.1)
	if world.walk_phase <= phase_before:
		_fail("Animation de marche non continue")
		return
	var fx_before: int = 0
	for child in world.get_children():
		if child.name == "Effet ramassage":
			fx_before += 1
	world._burst_fx(Vector3(-20, 1, 4), Color("f8d7a2"), 6)
	var fx_after: int = 0
	for child in world.get_children():
		if child.name == "Effet ramassage":
			fx_after += 1
	if fx_after <= fx_before:
		_fail("Effets de ramassage absents")
		return
	# Regression check : les collisions et les 4 zones doivent rester.
	if world.zones.size() != 4 or world.obstacle_points.size() < 60:
		_fail("Zones ou collisions perdues")
		return
	world.pets.append({"kind": 1, "growth": 0})
	world._make_pet_model(world.pets.size() - 1)
	world._next_companion()
	if world.follower_slots.is_empty():
		_fail("La commande de selection de compagnon ne fonctionne plus")
		return
	print("PETIT NID 0.6 : animations, interface, collision et manette OK")
	paused = false
	quit(0)
