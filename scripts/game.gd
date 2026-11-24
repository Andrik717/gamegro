extends Node2D

const WORLD_SIZE := Vector2(1536, 864)
const BAR_HEIGHT := 116.0
const MIN_ZOOM := 1.0
const MAX_ZOOM := 2.6
const TOUCH_TAP_SLOP := 18.0
var ITEM_COUNT := 0
var ITEM_DATA: Array[Dictionary] = []
var levels: Array = []
var current_level_index := 0
var current_level_name := ""
const CREAM := Color("#fff1ce")
const GOLD := Color("#f6c66c")
const NAVY := Color("#102d4d")

var background: Texture2D
var item_textures: Array[Texture2D] = []
var found := {}
var display_order: Array[int] = []
var elapsed := 0.0
var zoom := 1.0
var camera_offset := Vector2.ZERO
var touches := {}
var pinch_distance := 0.0
var pinch_zoom := 1.0
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
var won := false
var audio_found: AudioStreamPlayer
var audio_tap: AudioStreamPlayer
var audio_hint: AudioStreamPlayer
var audio_surf: AudioStreamPlayer

func _ready() -> void:
	_load_story()
	_load_level(0)
	_make_audio()
	_reset_round()
	set_process(true)
	get_viewport().size_changed.connect(queue_redraw)
	queue_redraw()

func _load_story() -> void:
	var file := FileAccess.open("res://game_data/story.json", FileAccess.READ)
	if file == null:
		push_error("Не удалось открыть game_data/story.json")
		return
	var parsed: Variant = JSON.parse_string(file.get_as_text())
	if parsed is Dictionary and parsed.has("levels") and parsed.levels is Array:
		levels = parsed.levels
	else:
		push_error("Некорректный формат game_data/story.json")

func _load_level(level_index: int) -> void:
	if levels.is_empty():
		return
	current_level_index = clampi(level_index, 0, levels.size() - 1)
	var level: Dictionary = levels[current_level_index]
	current_level_name = str(level.get("name", "Локация %d" % (current_level_index + 1)))
	var background_path := str(level.get("background_path", ""))
	if background_path.begins_with("res://") and ResourceLoader.exists(background_path):
		background = load(background_path)
	else:
		# Некоторые главы пока не имеют отдельного фона: используем доступный фон игры.
		background = load("res://assets/backgrounds/tropical_cove.png")
	ITEM_DATA.clear()
	item_textures.clear()
	for entry in level.get("items", []):
		if not entry is Dictionary:
			continue
		var coords: Array = entry.get("position", [768, 432])
		var item := {
			"id": ITEM_DATA.size(),
			"slug": str(entry.get("slug", "")),
			"name": str(entry.get("name", "Предмет")),
			"pos": Vector2(float(coords[0]), float(coords[1]))
		}
		var image_path := str(entry.get("image", ""))
		var texture: Texture2D = load(image_path) if ResourceLoader.exists(image_path) else null
		if texture == null:
			push_warning("Не найдена картинка предмета: " + image_path)
			continue
		ITEM_DATA.append(item)
		item_textures.append(texture)
	ITEM_COUNT = ITEM_DATA.size()
	if ITEM_COUNT == 0:
		push_error("В локации нет загружаемых предметов: " + current_level_name)

func _make_audio() -> void:
	audio_found = _player("res://assets/audio/found.wav", false)
	audio_tap = _player("res://assets/audio/tap.wav", false)
	audio_hint = _player("res://assets/audio/hint.wav", false)
	audio_surf = _player("res://assets/audio/surf.wav", true)
	audio_surf.volume_db = -17.0
	if sound_enabled:
		audio_surf.play()

func _player(path: String, looped: bool) -> AudioStreamPlayer:
	var p := AudioStreamPlayer.new()
	var stream: AudioStream = load(path)
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
	# Stable shuffle makes each new game feel different without losing reproducibility.
	display_order.shuffle()
	elapsed = 0.0
	zoom = 1.0
	camera_offset = Vector2.ZERO
	hint_id = -1
	hint_time = 0.0
	celebration_time = 0.0
	paused = false
	won = false
	queue_redraw()

func _process(delta: float) -> void:
	if not paused and not won:
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
	var drawn := WORLD_SIZE * base_scale * zoom
	var origin := (world_area.size - WORLD_SIZE * base_scale) * 0.5 + camera_offset
	return {"view":view,"area":world_area,"base":base_scale,"scale":base_scale*zoom,"origin":origin}

func _draw() -> void:
	var layout := _viewport_layout()
	var view: Vector2 = layout.view
	draw_rect(Rect2(Vector2.ZERO, view), Color("#09253a"), true)
	var origin: Vector2 = layout.origin
	var s: float = layout.scale
	draw_set_transform(origin, 0.0, Vector2.ONE * s)
	draw_texture_rect(background, Rect2(Vector2.ZERO, WORLD_SIZE), false)
	for i in range(ITEM_COUNT):
		if found.has(i):
			continue
		var p: Vector2 = ITEM_DATA[i].pos
		var texture: Texture2D = item_textures[i]
		var size := Vector2(48, 48)
		if hint_id == i and hint_time > 0.0:
			var pulse := 1.0 + 0.12 * sin(Time.get_ticks_msec() * 0.012)
			size *= pulse
			draw_circle(p, 36.0, Color(1.0,0.82,0.2,0.22))
		draw_texture_rect(texture, Rect2(p - size*0.5, size), false)
	if celebration_time > 0.0:
		var progress := 1.0 - celebration_time / 0.55
		var radius := 18.0 + progress * 78.0
		var alpha := 1.0 - progress
		draw_arc(found_effect_position, radius, 0.0, TAU, 48, Color(1.0,0.88,0.38,alpha), 6.0*(1.0-progress)+1.0)
		for particle in range(10):
			var angle := TAU * float(particle) / 10.0 + progress * 1.8
			var distance := 18.0 + progress * 62.0
			var sparkle := found_effect_position + Vector2(cos(angle),sin(angle))*distance
			draw_circle(sparkle, 4.0*(1.0-progress)+1.0, Color(1.0,0.94,0.64,alpha))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	_draw_hud(view)
	if paused:
		draw_rect(Rect2(Vector2.ZERO, view), Color(0,0,0,0.62), true)
		_center_text("ПАУЗА  •  КОСНИТЕСЬ, ЧТОБЫ ПРОДОЛЖИТЬ", view * 0.5, 30, CREAM)
	if won:
		draw_rect(Rect2(Vector2.ZERO, view), Color(0,0,0,0.68), true)
		_center_text("ВСЕ %d ПРЕДМЕТОВ НАЙДЕНЫ!" % ITEM_COUNT, view*0.5-Vector2(0,58), 36, GOLD)
		_center_text(current_level_name, view*0.5-Vector2(0,12), 27, CREAM)
		var next_text := "Коснитесь, чтобы открыть следующую локацию" if current_level_index < levels.size() - 1 else "Архипелаг восстановлен! Коснитесь, чтобы начать заново"
		_center_text(next_text, view*0.5+Vector2(0,38), 21, CREAM)

func _draw_hud(view: Vector2) -> void:
	var font := ThemeDB.fallback_font
	var bar := Rect2(0, view.y - BAR_HEIGHT, view.x, BAR_HEIGHT)
	draw_rect(bar, Color("#09213a"), true)
	draw_rect(Rect2(0, bar.position.y, view.x, 5), GOLD, true)
	draw_string(font, Vector2(22, bar.position.y+25), current_level_name.to_upper(), HORIZONTAL_ALIGNMENT_LEFT, minf(view.x * 0.48, 420.0), 18, GOLD)
	draw_string(font, Vector2(view.x-190, bar.position.y+25), "%02d / %02d" % [found.size(), ITEM_COUNT], HORIZONTAL_ALIGNMENT_LEFT, -1, 22, CREAM)
	var slots := mini(5, ITEM_COUNT - found.size())
	var slot_w := minf(112.0, (view.x-48.0)/5.0)
	var first_x := (view.x - slot_w*5.0)/2.0
	for slot in range(slots):
		var id := _next_visible_item(slot)
		if id < 0:
			continue
		var x := first_x + slot*slot_w
		draw_rect(Rect2(x+3, bar.position.y+32, slot_w-6, 76), Color("#173d5d"), true)
		draw_rect(Rect2(x+3, bar.position.y+32, slot_w-6, 76), Color("#bd8c48"), false, 2)
		draw_texture_rect(item_textures[id], Rect2(x+slot_w*0.5-22, bar.position.y+35, 44, 42), false)
		draw_string(font, Vector2(x+slot_w*0.5, bar.position.y+94), _short_name(ITEM_DATA[id].name), HORIZONTAL_ALIGNMENT_CENTER, slot_w-8, 12, CREAM)
	var top := 12.0
	_draw_button(Rect2(14,top,64,56),"Ⅱ")
	_draw_button(Rect2(view.x-82,top,68,56),"💡")
	_draw_button(Rect2(view.x-158,top,64,56),"♫")
	draw_string(font, Vector2(92,top+38), _time_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, 26, CREAM)
	draw_string(font, Vector2(view.x*0.5-82,top+36), "МАСШТАБ  %d%%" % int(zoom*100.0), HORIZONTAL_ALIGNMENT_LEFT, -1, 17, CREAM)

func _draw_button(rect: Rect2, label: String) -> void:
	draw_rect(rect, Color("#173d5d"), true)
	draw_rect(rect, GOLD, false, 3.0)
	draw_string(ThemeDB.fallback_font, rect.position+Vector2(rect.size.x*0.5-10,rect.size.y*0.5+10), label, HORIZONTAL_ALIGNMENT_LEFT, -1, 24, CREAM)

func _center_text(value: String, point: Vector2, size: int, color: Color) -> void:
	var font := ThemeDB.fallback_font
	var width := font.get_string_size(value, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	draw_string(font, point-Vector2(width*0.5,0), value, HORIZONTAL_ALIGNMENT_LEFT, -1, size, color)

func _short_name(value: String) -> String:
	return value if value.length() <= 12 else value.substr(0,11)+"…"

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
	return "%02d:%02d" % [total/60,total%60]

func _input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		_touch_event(event.index, event.position, event.pressed)
	elif event is InputEventScreenDrag:
		_drag_event(event.index, event.position, event.screen_relative)
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
			touch_started_on_hud = _is_hud_button(pos, get_viewport_rect().size)
		elif touches.size() == 2:
			multi_touch_gesture = true
			var points: Array = touches.values()
			pinch_distance = points[0].distance_to(points[1])
			pinch_zoom = zoom
			pinch_center = (points[0]+points[1])*0.5
	else:
		if touches.has(index):
			var was_single := touches.size() == 1
			var start := one_finger_start
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
			touch_started_on_hud = _is_hud_button(remaining, get_viewport_rect().size)

func _is_hud_button(point: Vector2, view: Vector2) -> bool:
	return Rect2(14, 12, 64, 56).has_point(point) \
		or Rect2(view.x - 82, 12, 68, 56).has_point(point) \
		or Rect2(view.x - 158, 12, 64, 56).has_point(point)

func _drag_event(index: int, pos: Vector2, relative: Vector2) -> void:
	if not touches.has(index):
		return
	touches[index] = pos
	if touches.size() >= 2:
		var points: Array = touches.values()
		var new_distance: float = points[0].distance_to(points[1])
		if pinch_distance > 1.0:
			var center: Vector2 = (points[0]+points[1])*0.5
			var factor := new_distance / pinch_distance
			_zoom_at(pinch_center, factor, center-pinch_center)
			pinch_distance = new_distance
			pinch_center = center
	elif touches.size() == 1:
		# Ignore tiny finger drift so an ordinary tap is not mistaken for a pan.
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
	var new_zoom := clampf(zoom*factor, MIN_ZOOM, MAX_ZOOM)
	var world_anchor: Vector2 = (point-layout.origin)/old_scale
	var base_origin: Vector2 = (layout.area.size-WORLD_SIZE*layout.base)*0.5
	zoom = new_zoom
	camera_offset = point - base_origin - world_anchor*(layout.base*zoom) + pan_delta
	_clamp_camera()
	queue_redraw()

func _clamp_camera() -> void:
	var layout := _viewport_layout()
	var area: Rect2 = layout.area
	var scaled: Vector2 = WORLD_SIZE * layout.scale
	var min_x: float = area.size.x-scaled.x
	var min_y: float = area.size.y-scaled.y
	camera_offset.x = clampf(camera_offset.x, min_x, 0.0) if min_x < 0 else 0.0
	camera_offset.y = clampf(camera_offset.y, min_y, 0.0) if min_y < 0 else 0.0

func _handle_tap(point: Vector2) -> void:
	if sound_enabled and audio_tap != null:
		audio_tap.play()
	var view := get_viewport_rect().size
	if paused:
		paused = false
		return
	if won:
		if current_level_index < levels.size() - 1:
			_load_level(current_level_index + 1)
		else:
			_load_level(0)
		_reset_round()
		return
	if point.y > view.y-BAR_HEIGHT:
		return
	if Rect2(14, 12, 64, 56).has_point(point):
		paused = true
		return
	if Rect2(view.x - 82, 12, 68, 56).has_point(point):
		_use_hint()
		return
	if Rect2(view.x - 158, 12, 64, 56).has_point(point):
		sound_enabled = not sound_enabled
		if sound_enabled:
			audio_surf.play()
		else:
			audio_surf.stop()
		return
	var layout := _viewport_layout()
	var world_pos: Vector2 = (point-layout.origin)/layout.scale
	for item in ITEM_DATA:
		var id: int = item.id
		if found.has(id):
			continue
		var radius := 34.0
		if Rect2(item.pos-Vector2.ONE*radius,Vector2.ONE*radius*2).has_point(world_pos):
			found[id] = true
			hint_id = id
			hint_time = 0.0
			found_effect_position = item.pos
			celebration_time = 0.55
			if sound_enabled:
				audio_found.play()
			if found.size() == ITEM_COUNT:
				won = true
			queue_redraw()
			return

func _use_hint() -> void:
	for id in display_order:
		if not found.has(id):
			hint_id = id
			hint_time = 2.5
			if sound_enabled:
				audio_hint.play()
			return

# Inventory is always the next five unfound objects from the shuffled current-level queue.
# Finding one removes it from the scene and immediately pulls the next queued item into the bar.
