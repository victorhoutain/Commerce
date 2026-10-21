extends SceneTree
# Tests de collisions du jeu 0.5, sans triche sur la physique Godot.

func _initialize() -> void:
	call_deferred("_check")

func _fail(msg: String) -> void:
	push_error("PETIT NID PHYSIQUE : " + msg)
	paused = false
	quit(1)

func _check() -> void:
	var root_scene = load("res://scenes/main.tscn")
	if root_scene == null:
		_fail("Scene principale absente")
		return
	var world = root_scene.instantiate()
	root.add_child(world)
	await physics_frame
	var overlay = world.get_node_or_null("Interface de jeu")
	if overlay == null:
		_fail("Interface non presente")
		return
	overlay._play()
	var solids: int = 0
	for item in world.get_children():
		if item is StaticBody3D:
			solids += 1
	if solids < 60:
		_fail("Decors non solides : seulement %d obstacles" % solids)
		return
	if world._egg_position_accessible(-30.0, 13.1):
		_fail("La maison peut recevoir des oeufs inaccessibles")
		return
	for egg in world.eggs:
		if bool(egg["belt"]):
			continue
		var point = egg["node"].position
		if absf(point.x + 14.4) < 0.01:
			continue
		if not world._egg_position_accessible(point.x, point.z):
			_fail("Oeuf apparu a l'interieur d'un obstacle")
			return
	world.player.global_position = Vector3(-30, 0.8, 9)
	await physics_frame
	var hit_house = world.player.move_and_collide(Vector3(0, 0, 5), true)
	if hit_house == null:
		_fail("Le personnage traverse la maison")
		return
	world.player.global_position = Vector3(20, 0.8, -7)
	await physics_frame
	var hit_belt = world.player.move_and_collide(Vector3(0, 0, -7), true)
	if hit_belt == null:
		_fail("Le personnage traverse le tapis roulant")
		return
	world.player.global_position = Vector3(-14.4, 0.8, 4.4)
	await physics_frame
	var egg_near = world._nearest_egg()
	if egg_near == null:
		_fail("Premier oeuf non accessible")
		return
	world._interact()
	if world.cargo.is_empty():
		_fail("Impossible de ramasser l'oeuf")
		return
	world._return_home()
	world._hatch_cargo()
	if world.pets.size() < 1:
		_fail("Impossible de faire eclore l'oeuf")
		return
	print("PETIT NID 0.5 : collisions, oeufs, eclosion et mouvement OK")
	paused = false
	quit(0)
