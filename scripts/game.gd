extends Node2D

const WORLD_SIZE := Vector2(1536.0, 864.0)
const BAR_HEIGHT := 144.0
const MIN_ZOOM := 1.0
const MAX_ZOOM := 2.6
const TOUCH_TAP_SLOP := 18.0
const CREAM := Color("#fff1ce")
const GOLD := Color("#f6c66c")
const NAVY := Color("#102d4d")
const BLUE := Color("#173d5d")
const PANEL := Color("#09213a")
const GREEN := Color("#397d68")

var ITEM_COUNT := 0
var ITEM_DATA: Array[Dictionary] = []
var levels: Array = []
var current_level_index := 0
var current_level_name := ""
var background: Texture2D
var item_textures: Array[Texture2D] = []
var layout_store: Dictionary = {}
const LAYOUT_SAVE_PATH := "user://level_layouts.json"
const LAYOUT_MARGIN := 54.0
const LAYOUT_GAP := 9.0
var found := {}
var display_order: Array[int] = []
var completed_levels: Dictionary = {}
var elapsed := 0.0
var zoom := 1.0
var camera_offset := Vector2.ZERO
var touches := {}
var pinch_distance := 0.0
var pinch_center := Vector2.ZERO
var one_finger_start := Vector2.ZERO
var one_finger_last := Vector2.ZERO
var dragging := false
var touch_started_on_hud := false
var multi_touch_gesture := false
var sound_enabled := true
var hint_id := -1
var hint_time := 0.0
var celebration_time := 0.0
var found_effect_position := Vector2.ZERO
var paused := false
var map_open := false
var won := false
var ui_font: Font
var audio_found: AudioStreamPlayer
var audio_hint: AudioStreamPlayer
var audio_surf: AudioStreamPlayer

func _ready() -> void:
	randomize()
	_create_ui_font()
	_load_story()
	_load_layout_store()
	_load_level(0)
	_make_audio()
	_reset_round()
	set_process(true)
	get_viewport().size_changed.connect(queue_redraw)
	queue_redraw()

func _create_ui_font() -> void:
	# Explicit system-font fallbacks include Cyrillic glyphs on Android and desktop.
	var system_font := SystemFont.new()
	system_font.font_names = PackedStringArray(["Noto Sans", "Roboto", "Arial"])
	ui_font = system_font

func _load_story() -> void:
	var file := FileAccess.open("res://game_data/story.json", FileAccess.READ)
	if file == null:
		push_error("Не удалось открыть game_data/story.json")
		return
	var parsed: Variant = JSON.parse_string(file.get_as_text())
	if parsed is Dictionary and parsed.get("levels") is Array:
		levels = parsed.get("levels", [])
	else:
		push_error("Некорректный формат game_data/story.json")

func _load_level(level_index: int) -> void:
	if levels.is_empty():
		return
	current_level_index = clampi(level_index, 0, levels.size() - 1)
	var level: Dictionary = levels[current_level_index]
	current_level_name = str(level.get("name", "Локация %d" % (current_level_index + 1)))
	var background_path := str(level.get("background_path", ""))
	var loaded_background: Resource = null
	if background_path.begins_with("res://") and ResourceLoader.exists(background_path):
		loaded_background = load(background_path)
	if loaded_background is Texture2D:
		background = loaded_background as Texture2D
	else:
		push_warning("Фон локации недоступен, используется резервный: " + background_path)
		background = load("res://assets/backgrounds/tropical_cove.png") as Texture2D
	if background == null:
		push_error("Не удалось загрузить основной или резервный фон локации")
	ITEM_DATA.clear()
	item_textures.clear()
	for entry in level.get("items", []):
		if not entry is Dictionary:
			continue
		var image_path := str(entry.get("image", ""))
		var texture: Texture2D = load(image_path) if ResourceLoader.exists(image_path) else null
		if texture == null:
			push_warning("Не найдена картинка предмета: " + image_path)
			continue
		ITEM_DATA.append({
			"id": ITEM_DATA.size(),
			"slug": str(entry.get("slug", "")),
			"name": str(entry.get("name", "Предмет")),
			"pos": Vector2.ZERO,
			"size": Vector2(48.0, 48.0),
			"rotation": 0.0
		})
		item_textures.append(texture)
	ITEM_COUNT = ITEM_DATA.size()
	if ITEM_COUNT > 0:
		_apply_level_layout(level)
	else:
		push_error("В локации нет загружаемых предметов: " + current_level_name)

func _load_layout_store() -> void:
	if not FileAccess.file_exists(LAYOUT_SAVE_PATH):
		layout_store = {}
		return
	var file := FileAccess.open(LAYOUT_SAVE_PATH, FileAccess.READ)
	if file == null:
		layout_store = {}
		return
	var parsed: Variant = JSON.parse_string(file.get_as_text())
	layout_store = parsed if parsed is Dictionary else {}

func _save_layout_store() -> void:
	var file := FileAccess.open(LAYOUT_SAVE_PATH, FileAccess.WRITE)
	if file == null:
		push_warning("Не удалось сохранить расположение предметов")
		return
	file.store_string(JSON.stringify(layout_store))

func _apply_level_layout(level: Dictionary) -> void:
	var level_key := str(level.get("id", current_level_index + 1))
	var saved: Variant = layout_store.get(level_key, [])
	if saved is Array and saved.size() == ITEM_COUNT:
		var valid := true
		for i in range(ITEM_COUNT):
			if not saved[i] is Dictionary:
				valid = false
				break
			for key in ["x", "y", "w", "h", "r"]:
				if not saved[i].has(key):
					valid = false
					break
			if not valid:
				break
		if valid:
			for i in range(ITEM_COUNT):
				var data: Dictionary = saved[i]
				ITEM_DATA[i].pos = Vector2(float(data.x), float(data.y))
				ITEM_DATA[i].size = Vector2(float(data.w), float(data.h))
				ITEM_DATA[i].rotation = float(data.r)
				if not Rect2(Vector2.ZERO, WORLD_SIZE).has_point(ITEM_DATA[i].pos):
					valid = false
					break
			if valid:
				return
	_generate_level_layout()
	var result: Array = []
	for item in ITEM_DATA:
		result.append({
			"x": item.pos.x,
			"y": item.pos.y,
			"w": item.size.x,
			"h": item.size.y,
			"r": item.rotation
		})
	layout_store[level_key] = result
	_save_layout_store()

func _generate_level_layout() -> void:
	var placed: Array[Rect2] = []
	for i in range(ITEM_COUNT):
		var texture_size := Vector2(item_textures[i].get_size())
		var aspect := texture_size.x / maxf(1.0, texture_size.y)
		var longest := randf_range(42.0, 66.0)
		var item_size := Vector2(longest, longest)
		if aspect >= 1.0:
			item_size.y = longest / maxf(0.35, aspect)
		else:
			item_size.x = longest * aspect
		var angle := deg_to_rad(randf_range(-13.0, 13.0))
		var found_spot := false
		for attempt in range(3500):
			var candidate := Vector2(
				randf_range(LAYOUT_MARGIN + item_size.x, WORLD_SIZE.x - LAYOUT_MARGIN - item_size.x),
				randf_range(LAYOUT_MARGIN + item_size.y, WORLD_SIZE.y - LAYOUT_MARGIN - item_size.y)
			)
			var candidate_rect := _layout_rect(candidate, item_size, angle)
			var overlaps := false
			for previous in placed:
				if candidate_rect.intersects(previous):
					overlaps = true
					break
			if not overlaps:
				ITEM_DATA[i].pos = candidate
				ITEM_DATA[i].size = item_size
				ITEM_DATA[i].rotation = angle
				placed.append(candidate_rect)
				found_spot = true
				break
			if attempt == 2000:
				item_size *= 0.88
		if not found_spot:
			push_warning("Не удалось найти свободное место для предмета: " + str(ITEM_DATA[i].name))
			ITEM_DATA[i].pos = Vector2(
				randf_range(LAYOUT_MARGIN, WORLD_SIZE.x - LAYOUT_MARGIN),
				randf_range(LAYOUT_MARGIN, WORLD_SIZE.y - LAYOUT_MARGIN)
			)
			ITEM_DATA[i].size = item_size
			ITEM_DATA[i].rotation = angle

func _layout_rect(center: Vector2, item_size: Vector2, angle: float) -> Rect2:
	var c := absf(cos(angle))
	var sn := absf(sin(angle))
	var bounds := Vector2(
		c * item_size.x + sn * item_size.y,
		sn * item_size.x + c * item_size.y
	)
	return Rect2(center - bounds * 0.5 - Vector2.ONE * (LAYOUT_GAP * 0.5), bounds + Vector2.ONE * LAYOUT_GAP)

func _make_audio() -> void:
	# There is deliberately no tap/click player: touching the screen is silent.
	audio_found = _player("res://assets/audio/found.wav", false)
	audio_hint = _player("res://assets/audio/hint.wav", false)
	audio_surf = _player("res://assets/audio/surf.wav", true)
	audio_surf.volume_db = -17.0
	if sound_enabled:
		audio_surf.play()

func _player(path: String, looped: bool) -> AudioStreamPlayer:
	var p := AudioStreamPlayer.new()
	var stream: AudioStream = load(path)
	if stream == null:
		push_warning("Не удалось загрузить аудио: " + path)
		return p
	if looped and stream is AudioStreamWAV:
		var wav_stream := stream as AudioStreamWAV
		wav_stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
	p.stream = stream
	p.volume_db = -5.0
	add_child(p)
	return p

func _reset_round() -> void:
	found.clear()
	display_order.clear()
	for i in range(ITEM_COUNT):
		display_order.append(i)
	display_order.shuffle()
	elapsed = 0.0
	zoom = 1.0
	camera_offset = Vector2.ZERO
	hint_id = -1
	hint_time = 0.0
	celebration_time = 0.0
	paused = false
	map_open = false
	won = false
	queue_redraw()

func _process(delta: float) -> void:
	if not paused and not map_open and not won:
		elapsed += delta
	if hint_time > 0.0:
		hint_time = maxf(0.0, hint_time - delta)
		if hint_time == 0.0:
			hint_id = -1
	if celebration_time > 0.0:
		celebration_time = maxf(0.0, celebration_time - delta)
	queue_redraw()

func _viewport_layout() -> Dictionary:
	var view := get_viewport_rect().size
	var world_area := Rect2(Vector2.ZERO, Vector2(view.x, maxf(1.0, view.y - BAR_HEIGHT)))
	var base_scale := minf(world_area.size.x / WORLD_SIZE.x, world_area.size.y / WORLD_SIZE.y)
	var origin := (world_area.size - WORLD_SIZE * base_scale) * 0.5 + camera_offset
	return {"view": view, "area": world_area, "base": base_scale, "scale": base_scale * zoom, "origin": origin}

func _draw() -> void:
	var layout := _viewport_layout()
	var view: Vector2 = layout.view
	draw_rect(Rect2(Vector2.ZERO, view), Color("#09253a"), true)
	var origin: Vector2 = layout.origin
	var scale_factor: float = layout.scale
	draw_set_transform(origin, 0.0, Vector2.ONE * scale_factor)
	if background != null:
		draw_texture_rect(background, Rect2(Vector2.ZERO, WORLD_SIZE), false)
	else:
		draw_rect(Rect2(Vector2.ZERO, WORLD_SIZE), Color("#31566a"), true)
	for i in range(ITEM_COUNT):
		if found.has(i):
			continue
		var item: Dictionary = ITEM_DATA[i]
		var item_size: Vector2 = item.size
		if hint_id == i and hint_time > 0.0:
			var pulse := 1.0 + 0.12 * sin(Time.get_ticks_msec() * 0.012)
			draw_circle(item.pos, maxf(item_size.x, item_size.y) * 0.72, Color(1.0, 0.82, 0.2, 0.22))
			item_size *= pulse
		draw_set_transform(origin + item.pos * scale_factor, float(item.rotation), Vector2.ONE * scale_factor)
		draw_texture_rect(item_textures[i], Rect2(-item_size * 0.5, item_size), false)
		draw_set_transform(origin, 0.0, Vector2.ONE * scale_factor)
	if celebration_time > 0.0:
		var progress := 1.0 - celebration_time / 0.55
		var radius := 18.0 + progress * 78.0
		var alpha := 1.0 - progress
		draw_arc(found_effect_position, radius, 0.0, TAU, 48, Color(1.0, 0.88, 0.38, alpha), 6.0 * (1.0 - progress) + 1.0)
		for particle in range(10):
			var angle := TAU * float(particle) / 10.0 + progress * 1.8
			var distance := 18.0 + progress * 62.0
			var sparkle := found_effect_position + Vector2(cos(angle), sin(angle)) * distance
			draw_circle(sparkle, 4.0 * (1.0 - progress) + 1.0, Color(1.0, 0.94, 0.64, alpha))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	_draw_hud(view)
	if map_open:
		_draw_map(view)
	elif paused:
		_draw_pause(view)
	elif won:
		_draw_win(view)

func _draw_hud(view: Vector2) -> void:
	var bar := Rect2(0.0, view.y - BAR_HEIGHT, view.x, BAR_HEIGHT)
	draw_rect(bar, PANEL, true)
	draw_rect(Rect2(0.0, bar.position.y, view.x, 4.0), GOLD, true)

	# Bottom inventory cards use wrapped labels instead of one clipped text line.
	_draw_text(current_level_name.to_upper(), Vector2(20.0, bar.position.y + 25.0), 17, GOLD, HORIZONTAL_ALIGNMENT_LEFT, minf(view.x * 0.48, 480.0))
	_draw_text("%02d / %02d НАЙДЕНО" % [found.size(), ITEM_COUNT], Vector2(view.x - 220.0, bar.position.y + 25.0), 16, CREAM, HORIZONTAL_ALIGNMENT_RIGHT, 200.0)

	var slot_width := (view.x - 40.0) / 5.0
	for slot in range(mini(5, ITEM_COUNT - found.size())):
		var id := _next_visible_item(slot)
		if id < 0:
			continue
		var x := 20.0 + slot * slot_width
		var card := Rect2(x + 3.0, bar.position.y + 34.0, slot_width - 6.0, 100.0)
		draw_rect(card, Color("#173d5d"), true)
		draw_rect(card, Color("#bd8c48"), false, 2.0)
		draw_texture_rect(item_textures[id], Rect2(x + slot_width * 0.5 - 22.0, bar.position.y + 39.0, 44.0, 42.0), false)
		var lines := _wrap_two_lines(str(ITEM_DATA[id].name), slot_width - 12.0, 13)
		if lines.size() == 1:
			_draw_text(lines[0], Vector2(x + slot_width * 0.5, bar.position.y + 104.0), 13, CREAM, HORIZONTAL_ALIGNMENT_CENTER, slot_width - 12.0)
		elif lines.size() >= 2:
			_draw_text(lines[0], Vector2(x + slot_width * 0.5, bar.position.y + 94.0), 12, CREAM, HORIZONTAL_ALIGNMENT_CENTER, slot_width - 12.0)
			_draw_text(lines[1], Vector2(x + slot_width * 0.5, bar.position.y + 110.0), 12, CREAM, HORIZONTAL_ALIGNMENT_CENTER, slot_width - 12.0)

	var top := 12.0
	_draw_button(_pause_rect(), "ПАУЗА", 13)
	_draw_button(_map_button_rect(), "КАРТА", 14)
	_draw_button(_hint_rect(view), "ПОДСКАЗКА", 12)
	_draw_button(_sound_rect(view), "ЗВУК " + ("ВКЛ" if sound_enabled else "ВЫКЛ"), 11)
	_draw_text(_time_text(), Vector2(210.0, top + 38.0), 22, CREAM, HORIZONTAL_ALIGNMENT_LEFT, 100.0)
	_draw_text("%d%%" % int(zoom * 100.0), Vector2(view.x * 0.5, top + 36.0), 16, CREAM, HORIZONTAL_ALIGNMENT_CENTER, 90.0)

func _draw_button(rect: Rect2, label: String, font_size := 16) -> void:
	draw_rect(rect, BLUE, true)
	draw_rect(rect, GOLD, false, 2.0)
	_draw_text(label, rect.position + Vector2(rect.size.x * 0.5, rect.size.y * 0.5 + float(font_size) * 0.34), font_size, CREAM, HORIZONTAL_ALIGNMENT_CENTER, rect.size.x - 8.0)

func _draw_text(value: String, baseline: Vector2, font_size: int, color: Color, alignment := HORIZONTAL_ALIGNMENT_LEFT, width := -1.0) -> void:
	draw_string(ui_font, baseline, value, alignment, width, font_size, color)

func _wrap_two_lines(value: String, max_width: float, font_size: int) -> Array[String]:
	var words := value.split(" ", false)
	var lines: Array[String] = []
	var current := ""
	for word in words:
		var candidate := word if current.is_empty() else current + " " + word
		if ui_font.get_string_size(candidate, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x <= max_width:
			current = candidate
		elif current.is_empty():
			current = word
		else:
			lines.append(current)
			current = word
	if not current.is_empty():
		lines.append(current)
	if lines.size() > 2:
		lines.resize(2)
		lines[1] = _fit_ellipsis(lines[1], max_width, font_size)
	return lines

func _fit_ellipsis(value: String, max_width: float, font_size: int) -> String:
	var result := value
	while not result.is_empty() and ui_font.get_string_size(result + "…", HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x > max_width:
		result = result.substr(0, result.length() - 1)
	return result + "…"

func _pause_rect() -> Rect2:
	return Rect2(14.0, 12.0, 72.0, 56.0)

func _map_button_rect() -> Rect2:
	return Rect2(94.0, 12.0, 94.0, 56.0)

func _hint_rect(view: Vector2) -> Rect2:
	return Rect2(view.x - 164.0, 12.0, 72.0, 56.0)

func _sound_rect(view: Vector2) -> Rect2:
	return Rect2(view.x - 82.0, 12.0, 68.0, 56.0)

func _pause_resume_rect(view: Vector2) -> Rect2:
	return Rect2(view.x * 0.5 - 218.0, view.y * 0.5 + 24.0, 204.0, 66.0)

func _pause_map_rect(view: Vector2) -> Rect2:
	return Rect2(view.x * 0.5 + 14.0, view.y * 0.5 + 24.0, 204.0, 66.0)

func _draw_pause(view: Vector2) -> void:
	draw_rect(Rect2(Vector2.ZERO, view), Color(0.0, 0.0, 0.0, 0.72), true)
	var panel := Rect2(view.x * 0.5 - 250.0, view.y * 0.5 - 105.0, 500.0, 220.0)
	draw_rect(panel, PANEL, true)
	draw_rect(panel, GOLD, false, 3.0)
	_draw_text("ИГРА ПРИОСТАНОВЛЕНА", Vector2(view.x * 0.5, view.y * 0.5 - 38.0), 27, GOLD, HORIZONTAL_ALIGNMENT_CENTER, 460.0)
	_draw_button(_pause_resume_rect(view), "ПРОДОЛЖИТЬ", 15)
	_draw_button(_pause_map_rect(view), "КАРТА УРОВНЕЙ", 14)

func _map_card_rect(index: int, view: Vector2) -> Rect2:
	var gap := 12.0
	var margin := 24.0
	var width := (view.x - margin * 2.0 - gap) * 0.5
	var available_height := view.y - 170.0
	var height := minf(104.0, (available_height - gap * 4.0) / 5.0)
	var col := index % 2
	var row := int(index / 2)
	return Rect2(margin + col * (width + gap), 94.0 + row * (height + gap), width, height)

func _draw_map(view: Vector2) -> void:
	draw_rect(Rect2(Vector2.ZERO, view), Color(0.015, 0.055, 0.09, 0.96), true)
	_draw_text("КАРТА МИРА", Vector2(view.x * 0.5, 48.0), 30, GOLD, HORIZONTAL_ALIGNMENT_CENTER, view.x - 180.0)
	_draw_text("Выберите локацию для продолжения приключения", Vector2(view.x * 0.5, 76.0), 15, CREAM, HORIZONTAL_ALIGNMENT_CENTER, view.x - 80.0)
	_draw_button(Rect2(view.x - 104.0, 16.0, 84.0, 48.0), "НАЗАД", 13)

	for i in range(levels.size()):
		var card := _map_card_rect(i, view)
		var is_current := i == current_level_index
		var is_completed := completed_levels.has(i)
		var fill := Color("#174b63")
		var border := Color("#6597a8")
		var status := "ОТКРЫТА"
		if is_completed:
			fill = Color("#245d50")
			border = Color("#8ed0a7")
			status = "ПРОЙДЕНА"
		if is_current:
			fill = Color("#604b2a")
			border = GOLD
			status = "ТЕКУЩАЯ"
		draw_rect(card, fill, true)
		draw_rect(card, border, false, 3.0 if is_current else 2.0)
		var number_center := Vector2(card.position.x + 42.0, card.position.y + card.size.y * 0.5)
		draw_circle(number_center, minf(27.0, card.size.y * 0.28), Color("#092d43"))
		_draw_text("%02d" % (i + 1), number_center + Vector2(0.0, 7.0), 20, GOLD, HORIZONTAL_ALIGNMENT_CENTER, 54.0)
		var text_x := card.position.x + 82.0
		var text_width := card.size.x - 98.0
		_draw_text(str(levels[i].get("name", "Локация %d" % (i + 1))), Vector2(text_x, card.position.y + card.size.y * 0.5 - 3.0), 17, CREAM, HORIZONTAL_ALIGNMENT_LEFT, text_width)
		_draw_text(status, Vector2(text_x, card.position.y + card.size.y * 0.5 + 23.0), 11, border, HORIZONTAL_ALIGNMENT_LEFT, text_width)

	_draw_text("Нажмите на карточку, чтобы открыть уровень", Vector2(view.x * 0.5, view.y - 18.0), 13, CREAM, HORIZONTAL_ALIGNMENT_CENTER, view.x - 40.0)

func _draw_win(view: Vector2) -> void:
	draw_rect(Rect2(Vector2.ZERO, view), Color(0.0, 0.0, 0.0, 0.76), true)
	var panel := Rect2(view.x * 0.5 - 270.0, view.y * 0.5 - 150.0, 540.0, 300.0)
	draw_rect(panel, PANEL, true)
	draw_rect(panel, GOLD, false, 3.0)
	_draw_text("УРОВЕНЬ ПРОЙДЕН!", Vector2(view.x * 0.5, view.y * 0.5 - 82.0), 30, GOLD, HORIZONTAL_ALIGNMENT_CENTER, 500.0)
	_draw_text("Найдены все %d предметов" % ITEM_COUNT, Vector2(view.x * 0.5, view.y * 0.5 - 38.0), 20, CREAM, HORIZONTAL_ALIGNMENT_CENTER, 500.0)
	_draw_button(_win_map_rect(view), "КАРТА УРОВНЕЙ", 14)
	_draw_button(_win_next_rect(view), "СЛЕДУЮЩИЙ УРОВЕНЬ", 13)

func _win_map_rect(view: Vector2) -> Rect2:
	return Rect2(view.x * 0.5 - 218.0, view.y * 0.5 + 22.0, 204.0, 66.0)

func _win_next_rect(view: Vector2) -> Rect2:
	return Rect2(view.x * 0.5 + 14.0, view.y * 0.5 + 22.0, 204.0, 66.0)

func _next_visible_item(slot: int) -> int:
	var shown := 0
	for id in display_order:
		if found.has(id):
			continue
		if shown == slot:
			return id
		shown += 1
	return -1

func _time_text() -> String:
	var total := int(elapsed)
	return "%02d:%02d" % [total / 60, total % 60]

func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE:
			if map_open:
				map_open = false
			else:
				paused = not paused
			queue_redraw()
			get_viewport().set_input_as_handled()
			return
		if event.keycode == KEY_M:
			map_open = not map_open
			paused = false
			queue_redraw()
			get_viewport().set_input_as_handled()
			return
	if event is InputEventScreenTouch:
		_touch_event(event.index, event.position, event.pressed)
	elif event is InputEventScreenDrag:
		_drag_event(event.index, event.position)
	elif event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_WHEEL_UP:
			_zoom_at(event.position, 1.12)
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			_zoom_at(event.position, 0.89)
		elif event.button_index == MOUSE_BUTTON_LEFT:
			_handle_tap(event.position)

func _touch_event(index: int, pos: Vector2, pressed: bool) -> void:
	if pressed:
		touches[index] = pos
		if touches.size() == 1:
			one_finger_start = pos
			one_finger_last = pos
			dragging = false
			touch_started_on_hud = _is_hud_button(pos, get_viewport_rect().size) or map_open or paused or won
		elif touches.size() == 2:
			multi_touch_gesture = true
			var points: Array = touches.values()
			pinch_distance = points[0].distance_to(points[1])
			pinch_center = (points[0] + points[1]) * 0.5
	else:
		if touches.has(index):
			var was_single := touches.size() == 1
			touches.erase(index)
			if was_single and not dragging and not multi_touch_gesture:
				var tap_pos := one_finger_start if touch_started_on_hud and one_finger_start.distance_to(pos) <= 36.0 else pos
				_handle_tap(tap_pos)
		if touches.is_empty():
			multi_touch_gesture = false
			touch_started_on_hud = false
		if touches.size() == 1:
			var remaining: Vector2 = touches.values()[0]
			one_finger_start = remaining
			one_finger_last = remaining
			dragging = false
			touch_started_on_hud = _is_hud_button(remaining, get_viewport_rect().size) or map_open or paused or won

func _is_hud_button(point: Vector2, view: Vector2) -> bool:
	return _pause_rect().has_point(point) \
		or _map_button_rect().has_point(point) \
		or _hint_rect(view).has_point(point) \
		or _sound_rect(view).has_point(point)

func _drag_event(index: int, pos: Vector2) -> void:
	if not touches.has(index):
		return
	touches[index] = pos
	if touches.size() >= 2:
		var points: Array = touches.values()
		var new_distance: float = points[0].distance_to(points[1])
		if pinch_distance > 1.0:
			var center: Vector2 = (points[0] + points[1]) * 0.5
			var factor := new_distance / pinch_distance
			_zoom_at(pinch_center, factor, center - pinch_center)
			pinch_distance = new_distance
			pinch_center = center
	elif touches.size() == 1:
		if zoom > 1.02 and not touch_started_on_hud and one_finger_start.distance_to(pos) > TOUCH_TAP_SLOP:
			if not dragging:
				dragging = true
				camera_offset += pos - one_finger_start
			else:
				camera_offset += pos - one_finger_last
			_clamp_camera()
			queue_redraw()
		one_finger_last = pos

func _zoom_at(point: Vector2, factor: float, pan_delta := Vector2.ZERO) -> void:
	var layout := _viewport_layout()
	var old_scale: float = layout.scale
	var new_zoom := clampf(zoom * factor, MIN_ZOOM, MAX_ZOOM)
	var world_anchor: Vector2 = (point - layout.origin) / old_scale
	var base_origin: Vector2 = (layout.area.size - WORLD_SIZE * layout.base) * 0.5
	zoom = new_zoom
	camera_offset = point - base_origin - world_anchor * (layout.base * zoom) + pan_delta
	_clamp_camera()
	queue_redraw()

func _clamp_camera() -> void:
	var layout := _viewport_layout()
	var area: Rect2 = layout.area
	var scaled: Vector2 = WORLD_SIZE * layout.scale
	var min_x: float = area.size.x - scaled.x
	var min_y: float = area.size.y - scaled.y
	camera_offset.x = clampf(camera_offset.x, min_x, 0.0) if min_x < 0.0 else 0.0
	camera_offset.y = clampf(camera_offset.y, min_y, 0.0) if min_y < 0.0 else 0.0

func _handle_tap(point: Vector2) -> void:
	var view := get_viewport_rect().size
	if map_open:
		_handle_map_tap(point, view)
		return
	if paused:
		if _pause_resume_rect(view).has_point(point):
			paused = false
		elif _pause_map_rect(view).has_point(point):
			paused = false
			map_open = true
		queue_redraw()
		return
	if won:
		if _win_map_rect(view).has_point(point):
			map_open = true
		elif _win_next_rect(view).has_point(point):
			_open_next_level()
		queue_redraw()
		return
	if _pause_rect().has_point(point):
		paused = true
		queue_redraw()
		return
	if _map_button_rect().has_point(point):
		map_open = true
		queue_redraw()
		return
	if _hint_rect(view).has_point(point):
		_use_hint()
		return
	if _sound_rect(view).has_point(point):
		sound_enabled = not sound_enabled
		if sound_enabled:
			audio_surf.play()
		else:
			audio_surf.stop()
		queue_redraw()
		return
	if point.y > view.y - BAR_HEIGHT:
		return
	var layout := _viewport_layout()
	var world_pos: Vector2 = (point - layout.origin) / layout.scale
	# Only the five items currently listed in the bottom task bar are searchable.
	# All other sprites remain visible in the scene but cannot be collected yet.
	# Check eligible items from the last drawn to the first to respect visual overlap.
	for item_index in range(ITEM_COUNT - 1, -1, -1):
		var item: Dictionary = ITEM_DATA[item_index]
		var id: int = int(item.id)
		if found.has(id) or not _is_active_target(id):
			continue
		var local_hit: Vector2 = (world_pos - item.pos).rotated(-float(item.rotation))
		if Rect2(-item.size * 0.5, item.size).has_point(local_hit):
			found[id] = true
			hint_id = id
			hint_time = 0.0
			found_effect_position = item.pos
			celebration_time = 0.55
			if sound_enabled and audio_found != null:
				audio_found.play()
			if found.size() == ITEM_COUNT:
				won = true
				completed_levels[current_level_index] = true
			queue_redraw()
			return

func _handle_map_tap(point: Vector2, view: Vector2) -> void:
	if Rect2(view.x - 104.0, 16.0, 84.0, 48.0).has_point(point):
		map_open = false
		queue_redraw()
		return
	for i in range(levels.size()):
		if _map_card_rect(i, view).has_point(point):
			map_open = false
			paused = false
			_load_level(i)
			_reset_round()
			return

func _open_next_level() -> void:
	if current_level_index < levels.size() - 1:
		_load_level(current_level_index + 1)
	else:
		_load_level(0)
	_reset_round()

func _is_active_target(item_id: int) -> bool:
	for slot in range(mini(5, ITEM_COUNT - found.size())):
		if _next_visible_item(slot) == item_id:
			return true
	return false

func _use_hint() -> void:
	var id := _next_visible_item(0)
	if id >= 0:
		hint_id = id
		hint_time = 2.5
		if sound_enabled and audio_hint != null:
			audio_hint.play()
		queue_redraw()
