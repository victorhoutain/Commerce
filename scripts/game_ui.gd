extends CanvasLayer
## Interface autonome de Petit Nid — aucun asset IA ou externe.
## Ce script rend le jeu utilisable depuis Windows, souris et clavier.

var game: Node3D
var hud: Control
var menu_layer: Control
var dialogue: PanelContainer
var dialogue_body: VBoxContainer
var objective: Label
var top_status: Label
var top_zone: Label
var action_hint: Label
var notice: Label
var last_notice: String = ""
var elapsed: float = 0.0
var menu_mode: String = "title"
var start_used: bool = false
var title_label: Label

const INK = Color("#38536A")
const ROSE = Color("#F7B8CC")
const WHITE = Color("#FFFDF6")
const DARK = Color("#253949")

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	game = get_parent()
	_create_hud()
	_create_menu()
	get_tree().paused = true
	_show_menu("title")
	_refresh()

func _panel_style(bg: Color, radius: int = 18, border: Color = Color.TRANSPARENT) -> StyleBoxFlat:
	var style = StyleBoxFlat.new()
	style.bg_color = bg
	style.set_corner_radius_all(radius)
	style.set_border_width_all(2 if border.a > 0.01 else 0)
	style.border_color = border
	style.set_content_margin_all(12)
	return style

func _label(text_value: String, size: int = 21, color: Color = INK) -> Label:
	var result = Label.new()
	result.text = text_value
	result.add_theme_font_size_override("font_size", size)
	result.add_theme_color_override("font_color", color)
	result.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	return result

func _button(text_value: String, callback: Callable, color: Color = Color("#FFE0A8")) -> Button:
	var result = Button.new()
	result.text = text_value
	result.custom_minimum_size = Vector2(130, 46)
	result.add_theme_font_size_override("font_size", 17)
	result.add_theme_color_override("font_color", DARK)
	result.add_theme_color_override("font_hover_color", DARK)
	result.add_theme_color_override("font_pressed_color", DARK)
	result.add_theme_stylebox_override("normal", _panel_style(color, 13))
	result.add_theme_stylebox_override("hover", _panel_style(color.lightened(0.15), 13))
	result.add_theme_stylebox_override("pressed", _panel_style(color.darkened(0.14), 13))
	result.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	result.pressed.connect(callback)
	return result

func _create_hud() -> void:
	hud = Control.new()
	hud.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	hud.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(hud)

	var header = PanelContainer.new()
	header.anchor_right = 1
	header.offset_left = 16
	header.offset_top = 14
	header.offset_right = -16
	header.offset_bottom = 101
	header.add_theme_stylebox_override("panel", _panel_style(Color("#FFFDF2ED")))
	hud.add_child(header)
	var info = HBoxContainer.new()
	info.add_theme_constant_override("separation", 24)
	header.add_child(info)
	var brand = _label("PETIT NID", 29, Color("#C27089"))
	brand.custom_minimum_size.x = 196
	info.add_child(brand)
	top_status = _label("", 20, INK)
	top_status.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	info.add_child(top_status)
	top_zone = _label("", 19, Color("#497A69"))
	info.add_child(top_zone)

	var objectives_panel = PanelContainer.new()
	objectives_panel.position = Vector2(16, 116)
	objectives_panel.custom_minimum_size = Vector2(325, 130)
	objectives_panel.add_theme_stylebox_override("panel", _panel_style(Color("#FFFDF4E8"), 20))
	hud.add_child(objectives_panel)
	var obj_stack = VBoxContainer.new()
	obj_stack.add_theme_constant_override("separation", 6)
	objectives_panel.add_child(obj_stack)
	obj_stack.add_child(_label("TA PROCHAINE MISSION", 15, Color("#C47E94")))
	objective = _label("", 19)
	obj_stack.add_child(objective)

	var hint_panel = PanelContainer.new()
	hint_panel.anchor_top = 1
	hint_panel.anchor_bottom = 1
	hint_panel.anchor_right = 1
	hint_panel.offset_left = 16
	hint_panel.offset_right = -16
	hint_panel.offset_top = -164
	hint_panel.offset_bottom = -84
	hint_panel.add_theme_stylebox_override("panel", _panel_style(Color("#FFFDF1F5"), 15))
	hud.add_child(hint_panel)
	action_hint = _label("", 20, Color("#705572"))
	hint_panel.add_child(action_hint)

	var bar = HBoxContainer.new()
	bar.anchor_top = 1
	bar.anchor_bottom = 1
	bar.anchor_right = 1
	bar.offset_left = 16
	bar.offset_right = -16
	bar.offset_top = -69
	bar.offset_bottom = -14
	bar.alignment = BoxContainer.ALIGNMENT_CENTER
	bar.add_theme_constant_override("separation", 12)
	hud.add_child(bar)
	bar.add_child(_button("NID [B]", func(): _home(), Color("#FAD3BD")))
	bar.add_child(_button("CARTE [M]", func(): _show_menu("map"), Color("#CBEEE2")))
	bar.add_child(_button("CREATURES [K]", func(): _show_menu("pets"), Color("#DDD2FF")))
	bar.add_child(_button("AIDE [H]", func(): _show_menu("help"), Color("#F9E6AF")))
	bar.add_child(_button("PAUSE [ESC]", func(): _show_menu("pause"), Color("#E8E9F0")))

	notice = _label("", 20, Color("#D15D83"))
	notice.anchor_left = 0.3
	notice.anchor_right = 0.78
	notice.offset_top = 116
	notice.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hud.add_child(notice)

func _create_menu() -> void:
	menu_layer = Control.new()
	menu_layer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	menu_layer.mouse_filter = Control.MOUSE_FILTER_STOP
	add_child(menu_layer)
	var shade = ColorRect.new()
	shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	shade.color = Color("#20384DCC")
	shade.mouse_filter = Control.MOUSE_FILTER_STOP
	menu_layer.add_child(shade)
	dialogue = PanelContainer.new()
	dialogue.anchor_left = 0.5
	dialogue.anchor_top = 0.5
	dialogue.anchor_right = 0.5
	dialogue.anchor_bottom = 0.5
	dialogue.offset_left = -335
	dialogue.offset_right = 335
	dialogue.offset_top = -275
	dialogue.offset_bottom = 275
	dialogue.add_theme_stylebox_override("panel", _panel_style(WHITE, 26, Color("#E9B5C7")))
	menu_layer.add_child(dialogue)
	var scroll = ScrollContainer.new()
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	dialogue.add_child(scroll)
	dialogue_body = VBoxContainer.new()
	dialogue_body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	dialogue_body.add_theme_constant_override("separation", 12)
	scroll.add_child(dialogue_body)

func _clear_dialogue() -> void:
	for child in dialogue_body.get_children():
		dialogue_body.remove_child(child)
		child.queue_free()

func _heading(main_text: String, subtitle: String) -> void:
	dialogue_body.add_child(_label(main_text, 37, Color("#C27089")))
	dialogue_body.add_child(_label(subtitle, 18, Color("#6E7E87")))
	dialogue_body.add_child(HSeparator.new())

func _buttons_row() -> HBoxContainer:
	var row = HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	dialogue_body.add_child(row)
	return row

func _play() -> void:
	get_tree().paused = false
	menu_layer.visible = false
	menu_mode = ""
	start_used = true

func _home() -> void:
	if menu_layer.visible:
		_play()
	game._return_home()

func _show_menu(mode: String) -> void:
	menu_mode = mode
	get_tree().paused = true
	menu_layer.visible = true
	_clear_dialogue()
	match mode:
		"title":
			_heading("PETIT NID", "Une aventure douce pour collectionner des oeufs et des compagnons.")
			dialogue_body.add_child(_label("Explore quatre mondes colores. Ramene tes oeufs au nid, fais grandir des creatures et agrandis ta collection.", 22))
			dialogue_body.add_child(_label("Commence a la prairie, juste a cote de ton nid !", 18, Color("#688977")))
			var row = _buttons_row()
			row.add_child(_button("COMMENCER", func(): _play(), Color("#BFEACF")))
			row.add_child(_button("COMMENT JOUER", func(): _show_menu("help"), Color("#F9E6AF")))
		"pause":
			_heading("PAUSE", "Ton aventure est sauvegardee automatiquement.")
			dialogue_body.add_child(_label("Profite de ton petit univers a ton rythme. Aucun chronometre, aucune penalite !", 21))
			var row = _buttons_row()
			row.add_child(_button("REPRENDRE", func(): _play(), Color("#BFEACF")))
			row.add_child(_button("CARTE", func(): _show_menu("map"), Color("#CBEEE2")))
			row.add_child(_button("AIDE", func(): _show_menu("help"), Color("#F9E6AF")))
			var row2 = _buttons_row()
			row2.add_child(_button("RETOUR AU NID", func(): _home(), Color("#FAD3BD")))
			row2.add_child(_button("QUITTER LE JEU", func(): _quit(), Color("#E8E9F0")))
		"help":
			_heading("COMMENT JOUER ?", "Les cinq etapes de ton aventure.")
			for entry in [
				"1. BOUGER : utilise ZQSD, WASD ou les fleches du clavier.",
				"2. RAMASSER : rapproche-toi d'un oeuf et appuie sur E.",
				"3. ECLORE : rapporte les oeufs au nid dans ta base et appuie sur E.",
				"4. AMELIORER : dans la boutique, E agrandit le sac et F augmente ta vitesse.",
				"5. GRANDIR : pres de la mangeoire, G nourrit ta premiere creature encore jeune.",
				"Bonus : B revient a la base, C choisit un compagnon, K ouvre la collection.",
				"Le tapis roulant propose des oeufs speciaux contre des pieces.",
				"Pour entrer dans la zone suivante, approche-toi du portail et appuie sur E."
			]:
				dialogue_body.add_child(_label(entry, 19))
			dialogue_body.add_child(_button("JOUER", func(): _play(), Color("#BFEACF")))
		"map":
			_heading("CARTE DES MONDES", "Clique sur une destination deja ouverte pour y aller.")
			for i in range(game.zones.size()):
				var zone: Dictionary = game.zones[i]
				var row = _buttons_row()
				var name_text = str(i + 1) + ". " + str(zone["name"])
				if i > game.unlocked_zone:
					name_text += "  -  FERME"
					var locked = _label(name_text, 18, Color("#9A99A6"))
					row.add_child(locked)
					row.add_child(_label("%d pieces + %d eclosions" % [int(zone["unlocks_for_coins"]), int(zone["unlocks_after_hatches"])], 16))
				else:
					var zone_i = i
					row.add_child(_button(name_text, func(): _teleport(zone_i), Color("#DDF3E6")))
			dialogue_body.add_child(_button("RETOUR AU JEU", func(): _play(), Color("#F9E6AF")))
		"pets":
			_heading("MES PETITES CREATURES", "%d creatures • jusqu'a 3 compagnons." % game.pets.size())
			if game.pets.is_empty():
				dialogue_body.add_child(_label("Ta collection est encore vide. Ramasse un oeuf et rapporte-le au nid !", 22))
			else:
				for i in range(mini(game.pets.size(), 60)):
					var pet: Dictionary = game.pets[i]
					var which = clampi(int(pet["kind"]), 0, 3)
					var growth = clampi(int(pet["growth"]), 0, 2)
					var stages = ["Bebe", "Jeune", "Adulte"]
					var line = _buttons_row()
					var equipped = game.follower_slots.has(i)
					line.add_child(_label("%02d  %s - %s" % [i + 1, game.SPECIES[which], stages[growth]], 17))
					var pet_i = i
					line.add_child(_button("RETIRER" if equipped else "EQUIPER", func(): _equip(pet_i), Color("#BFEACF") if equipped else Color("#DDD2FF")))
				if game.pets.size() > 60:
					dialogue_body.add_child(_label("Les 60 premieres creatures sont affichees.", 17))
			dialogue_body.add_child(_button("RETOUR AU JEU", func(): _play(), Color("#F9E6AF")))
		"reset":
			_heading("RECOMMENCER ?", "Cette action efface toute ta progression.")
			dialogue_body.add_child(_label("Tes creatures, tes pieces et tes zones seront perdues.", 22))
			var row = _buttons_row()
			row.add_child(_button("ANNULER", func(): _show_menu("pause"), Color("#BFEACF")))
			row.add_child(_button("OUI, EFFACER", func(): _reset_save(), Color("#F5B8B8")))

func _teleport(index: int) -> void:
	var area: Dictionary = game.zones[index]
	var x_target = float(area["x_min"]) + 11.0
	if index == 0:
		x_target = -20.6
	game.player.position = Vector3(x_target, 0.8, 4.5)
	game.player.velocity = Vector3.ZERO
	_play()
	game._show_toast("Bienvenue : " + str(area["name"]) + " !")

func _equip(index: int) -> void:
	game._toggle_follower(index)
	_show_menu("pets")

func _quit() -> void:
	game._save_progress()
	get_tree().paused = false
	get_tree().quit()

func _reset_save() -> void:
	DirAccess.remove_absolute(ProjectSettings.globalize_path(game.SAVE_PATH))
	get_tree().paused = false
	get_tree().reload_current_scene()

func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_ESCAPE:
				if menu_layer.visible:
					if menu_mode == "title" and not start_used:
						return
					_play()
				else:
					_show_menu("pause")
				get_viewport().set_input_as_handled()
			KEY_M:
				_show_menu("map")
				get_viewport().set_input_as_handled()
			KEY_K:
				_show_menu("pets")
				get_viewport().set_input_as_handled()
			KEY_H:
				_show_menu("help")
				get_viewport().set_input_as_handled()

func _process(delta: float) -> void:
	elapsed += delta
	if elapsed < 0.16:
		return
	elapsed = 0
	_refresh()

func _refresh() -> void:
	if not is_instance_valid(game.hud_hint):
		return
	top_status.text = "PIECES  %d    SAC  %d/%d    VITESSE  %d" % [game.coins, game.cargo.size(), game.capacities[game.capacity_tier], game.speed_level + 1]
	var ix = game._zone_for_x(game.player.position.x)
	top_zone.text = "%s  |  %d / 4" % [str(game.zones[ix]["name"]), ix + 1]
	action_hint.text = game.hud_hint.text
	notice.text = game.hud_toast.text
	if game.pets.is_empty():
		objective.text = "Trouve un oeuf dans la prairie.\nRamene-le au nid pour le faire eclore."
	elif game.speed_level == 0:
		objective.text = "Ta premiere creature est nee !\nAmeliore ta vitesse a la boutique."
	elif game.unlocked_zone < game.zones.size() - 1:
		var area: Dictionary = game.zones[game.unlocked_zone + 1]
		objective.text = "Debloque : %s\n%d / %d eclosions • %d / %d pieces" % [str(area["name"]), game.total_hatched, int(area["unlocks_after_hatches"]), game.coins, int(area["unlocks_for_coins"])]
	else:
		objective.text = "Tous les mondes sont ouverts !\nCollectionne les creatures mythiques."
