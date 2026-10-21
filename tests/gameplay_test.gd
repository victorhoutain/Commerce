extends SceneTree
## Test fonctionnel 0.3, lance par GitHub Actions et sous Godot en mode headless.

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var scene = load("res://scenes/main.tscn")
	if scene == null:
		_fail("scene principale absente")
		return
	var game = scene.instantiate()
	root.add_child(game)
	await process_frame
	var ui = game.get_node_or_null("Interface de jeu")
	if ui == null:
		_fail("interface et menu manquants")
		return
	if ui.menu_mode != "title":
		_fail("menu initial absent")
		return
	ui._play()
	if paused:
		_fail("le jeu reste en pause apres JOUER")
		return
	var first_count: int = game.pets.size()
	game.pets.append({"kind": 1, "growth": 0})
	game._make_pet_model(first_count)
	game._toggle_follower(first_count)
	if not game.follower_slots.has(first_count):
		_fail("impossible d'equiper le compagnon")
		return
	game._toggle_follower(first_count)
	if game.follower_slots.has(first_count):
		_fail("impossible de retirer le compagnon")
		return
	ui._show_menu("pets")
	if ui.menu_mode != "pets" or not paused:
		_fail("la collection n'ouvre pas un panneau jouable")
		return
	ui._show_menu("map")
	if ui.menu_mode != "map":
		_fail("carte indisponible")
		return
	game.coins = 2000
	game.total_hatched = 40
	game.unlocked_zone = 0
	game._unlock_next_zone()
	if game.unlocked_zone != 1:
		_fail("progression des zones bloquee")
		return
	ui._teleport(1)
	if game.player.position.x < 38 or paused:
		_fail("teleportation et retour au jeu impossibles")
		return
	game._return_home()
	if game.player.position.x > 0:
		_fail("impossible de rentrer a la base")
		return
	game.unlocked_zone = 3
	game.total_hatched = 25
	game.pets.append({"kind": 3, "growth": 0})
	game._check_victory()
	if not game.victory_unlocked or ui.menu_mode != "victory":
		_fail("victoire finale inaccessible")
		return
	print("PETIT NID 0.3 : progression et interface OK")
	paused = false
	quit(0)

func _fail(message: String) -> void:
	push_error("PETIT NID 0.3 : " + message)
	paused = false
	quit(1)
