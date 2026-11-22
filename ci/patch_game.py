from pathlib import Path
import re, shutil, sys

root = Path(sys.argv[1])
project = root / "project.godot"
preset = root / "export_presets.cfg"
game = root / "scripts/game.gd"

# Include the splash image in the packaged Godot project (no network dependency at runtime).
source_splash = Path("assets/cat_splash.jpg")
if source_splash.is_file():
    (root / "assets").mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_splash, root / "assets/cat_splash.jpg")
else:
    raise SystemExit("Required splash image assets/cat_splash.jpg is missing from repository.")

# Android landscape.
s = project.read_text(encoding="utf-8")
if "[display]" not in s:
    s += "\n[display]\n"
if re.search(r"(?m)^window/handheld/orientation=", s):
    s = re.sub(r"(?m)^window/handheld/orientation=.*$", "window/handheld/orientation=0", s)
else:
    s = s.replace("[display]", "[display]\nwindow/handheld/orientation=0", 1)
project.write_text(s, encoding="utf-8")
if preset.exists():
    s = preset.read_text(encoding="utf-8")
    if re.search(r"(?m)^screen/orientation=", s):
        s = re.sub(r"(?m)^screen/orientation=.*$", "screen/orientation=0", s)
    preset.write_text(s, encoding="utf-8")

game_source = r'''extends Node2D

const DESIGN := Vector2(1672, 941)
const BG_PATH := "res://assets/tropical_island.svg"
const SPLASH_PATH := "res://assets/cat_splash.jpg"
const TARGETS := [
    {"id":"star", "name":"Звезда", "rect":Rect2(180, 710, 180, 170), "patch":Rect2(390, 700, 150, 130)},
    {"id":"shell", "name":"Ракушка", "rect":Rect2(610, 690, 200, 170), "patch":Rect2(800, 680, 150, 130)},
    {"id":"key", "name":"Ключ", "rect":Rect2(900, 690, 180, 150), "patch":Rect2(800, 680, 150, 130)},
    {"id":"pineapple", "name":"Ананас", "rect":Rect2(1120, 650, 190, 220), "patch":Rect2(800, 680, 150, 130)},
    {"id":"crab", "name":"Краб", "rect":Rect2(1310, 660, 250, 220), "patch":Rect2(800, 680, 150, 130)}
]
const CREAM := Color("#fff2d0")
const PANEL := Color(0.055, 0.12, 0.16, 0.94)
const MIN_ZOOM := 1.0
const MAX_ZOOM := 3.0

var background: Texture2D
var splash: Texture2D
var splash_left := 3.0
var found: Array[String] = []
var elapsed := 0.0
var hint_target := -1
var hint_left := 0.0
var paused := false
var won := false
var zoom := 1.0
var camera_offset := Vector2.ZERO
var touches: Dictionary = {}
var pinch_distance := 0.0
var mouse_dragging := false
var mouse_last := Vector2.ZERO
var hint_rect := Rect2(1390, 855, 220, 62)
var pause_rect := Rect2(1530, 0, 140, 120)
var replay_rect := Rect2(665, 545, 340, 78)

func _ready() -> void:
    background = load(BG_PATH)
    splash = load(SPLASH_PATH)
    get_viewport().size_changed.connect(queue_redraw)
    queue_redraw()

func _process(delta: float) -> void:
    if splash_left > 0.0:
        splash_left = maxf(0.0, splash_left - delta)
    elif not paused and not won:
        elapsed += delta
    if hint_left > 0.0:
        hint_left = maxf(0.0, hint_left - delta)
        if hint_left == 0.0:
            hint_target = -1
    queue_redraw()

func _draw() -> void:
    var view := get_viewport_rect().size
    var scale_factor := minf(view.x / DESIGN.x, view.y / DESIGN.y)
    var origin := (view - DESIGN * scale_factor) * 0.5

    if splash_left > 0.0 and splash != null:
        draw_set_transform(origin, 0.0, Vector2.ONE * scale_factor)
        draw_texture_rect(splash, Rect2(Vector2.ZERO, DESIGN), false)
        var fade := clampf((3.0 - splash_left) / 0.45, 0.0, 1.0)
        if fade > 0.0:
            draw_rect(Rect2(Vector2.ZERO, DESIGN), Color(0.0, 0.0, 0.0, fade), true)
        draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
        return

    if background == null:
        return

    # Only the scene is zoomed/panned; the HUD remains fixed to the screen.
    draw_set_transform(origin + camera_offset * scale_factor, 0.0, Vector2.ONE * (scale_factor * zoom))
    draw_texture_rect(background, Rect2(Vector2.ZERO, DESIGN), false)
    for item in TARGETS:
        if found.has(item.id):
            draw_texture_rect_region(background, item.rect, item.patch, Color.WHITE, false)
    if hint_target >= 0 and hint_left > 0.0:
        var target_rect: Rect2 = TARGETS[hint_target].rect
        var pulse := 0.5 + 0.5 * sin(Time.get_ticks_msec() / 120.0)
        draw_rect(target_rect.grow(10), Color(1.0, 0.82, 0.25, 0.25 + pulse * 0.3), false, 7.0)
    draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)

    _draw_hud(view, origin, scale_factor)
    if paused and not won:
        draw_rect(Rect2(Vector2.ZERO, view), Color(0.01, 0.03, 0.05, 0.68), true)
        _center_text("ПАУЗА — НАЖМИТЕ, ЧТОБЫ ПРОДОЛЖИТЬ", view * 0.5, 30, CREAM)
    if won:
        draw_set_transform(origin, 0.0, Vector2.ONE * scale_factor)
        _draw_win()
        draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)

func _draw_hud(view: Vector2, origin: Vector2, scale_factor: float) -> void:
    # HUD coordinates are authored in design space, scaled to fit the actual viewport.
    draw_set_transform(origin, 0.0, Vector2.ONE * scale_factor)
    var panel := Rect2(28, 842, 1616, 78)
    draw_rect(panel, PANEL, true)
    draw_rect(panel, Color("#edbd60"), false, 3.0)
    var font := ThemeDB.fallback_font
    draw_string(font, Vector2(48, 890), "НАЙДЕНО: %d / 5" % found.size(), HORIZONTAL_ALIGNMENT_LEFT, 290, 28, CREAM)
    draw_string(font, Vector2(340, 890), "ВРЕМЯ: " + _time_text(), HORIZONTAL_ALIGNMENT_LEFT, 190, 28, CREAM)

    # Five equal-width target slots: larger, centered labels with an explicit width limit.
    var slot_x := 535.0
    var slot_w := 164.0
    for i in range(TARGETS.size()):
        var item: Dictionary = TARGETS[i]
        var done: bool = found.has(item.id)
        var slot := Rect2(slot_x + i * slot_w, 852, slot_w - 5, 58)
        draw_rect(slot, Color(0.10, 0.20, 0.22, 0.92), true)
        draw_rect(slot, Color("#8ee0a1") if done else Color("#b88b4d"), false, 2.0)
        var label := ("✓ " if done else "○ ") + str(item.name)
        draw_string(font, Vector2(slot.position.x + 4, 890), label, HORIZONTAL_ALIGNMENT_CENTER, slot.size.x - 8, 24, Color("#8ee0a1") if done else CREAM)

    draw_rect(hint_rect, Color("#bd762d"), true)
    draw_rect(hint_rect, Color("#ffe1a0"), false, 3.0)
    draw_string(font, Vector2(1400, 896), "ПОДСКАЗКА", HORIZONTAL_ALIGNMENT_CENTER, 200, 25, CREAM)
    draw_circle(Vector2(1600, 58), 47, Color("#8d5228"), true)
    draw_circle(Vector2(1600, 58), 47, Color("#ffe1a0"), false, 4.0)
    draw_rect(Rect2(1584, 34, 10, 48), CREAM, true)
    draw_rect(Rect2(1606, 34, 10, 48), CREAM, true)
    draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)

func _draw_win() -> void:
    draw_rect(Rect2(Vector2.ZERO, DESIGN), Color(0.01, 0.03, 0.05, 0.72), true)
    var card := Rect2(470, 300, 732, 370)
    draw_rect(card, Color("#193b45"), true)
    draw_rect(card, Color("#f7c96b"), false, 5.0)
    var font := ThemeDB.fallback_font
    draw_string(font, Vector2(585, 405), "ОСТРОВ РАСКРЫЛ СВОИ СЕКРЕТЫ!", HORIZONTAL_ALIGNMENT_LEFT, 620, 34, CREAM)
    draw_string(font, Vector2(650, 465), "Ты нашёл все сокровища!", HORIZONTAL_ALIGNMENT_LEFT, 500, 30, Color("#bcebd0"))
    draw_string(font, Vector2(760, 510), "Время: " + _time_text(), HORIZONTAL_ALIGNMENT_LEFT, 300, 26, CREAM)
    draw_rect(replay_rect, Color("#bd762d"), true)
    draw_rect(replay_rect, Color("#ffe1a0"), false, 3.0)
    draw_string(font, Vector2(730, 595), "ИГРАТЬ ЕЩЁ", HORIZONTAL_ALIGNMENT_LEFT, 300, 30, CREAM)

func _center_text(value: String, center: Vector2, size: int, color: Color) -> void:
    var font := ThemeDB.fallback_font
    var width := font.get_string_size(value, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
    draw_string(font, center - Vector2(width * 0.5, -size * 0.35), value, HORIZONTAL_ALIGNMENT_LEFT, -1, size, color)

func _time_text() -> String:
    var total := int(elapsed)
    return "%02d:%02d" % [total / 60, total % 60]

func _to_design(screen_pos: Vector2) -> Vector2:
    var view := get_viewport_rect().size
    var scale_factor := minf(view.x / DESIGN.x, view.y / DESIGN.y)
    var origin := (view - DESIGN * scale_factor) * 0.5
    return (screen_pos - origin) / scale_factor

func _zoom_at(anchor: Vector2, factor: float) -> void:
    var old_zoom := zoom
    zoom = clampf(zoom * factor, MIN_ZOOM, MAX_ZOOM)
    var world_at_anchor := (anchor - camera_offset) / old_zoom
    camera_offset = anchor - world_at_anchor * zoom
    if zoom <= 1.001:
        zoom = 1.0
        camera_offset = Vector2.ZERO
    _clamp_camera()
    queue_redraw()

func _clamp_camera() -> void:
    var min_offset := DESIGN * (1.0 - zoom)
    camera_offset.x = clampf(camera_offset.x, min_offset.x, 0.0)
    camera_offset.y = clampf(camera_offset.y, min_offset.y, 0.0)

func _input(event: InputEvent) -> void:
    if splash_left > 0.0:
        return

    if event is InputEventScreenTouch:
        var touch_pos: Vector2 = _to_design(event.position)
        if event.pressed:
            touches[event.index] = touch_pos
            if touches.size() == 1:
                mouse_last = touch_pos
        else:
            touches.erase(event.index)
        if touches.size() == 2:
            var initial_points: Array = touches.values()
            pinch_distance = initial_points[0].distance_to(initial_points[1])
        elif touches.size() < 2:
            pinch_distance = 0.0
        if event.pressed and touches.size() == 1:
            _handle_tap(event.position)
        get_viewport().set_input_as_handled()
        return

    if event is InputEventScreenDrag:
        var pos: Vector2 = _to_design(event.position)
        if touches.has(event.index):
            touches[event.index] = pos
        if touches.size() >= 2:
            var points: Array = touches.values()
            var midpoint: Vector2 = (points[0] + points[1]) * 0.5
            var distance: float = points[0].distance_to(points[1])
            if pinch_distance > 1.0 and distance > 1.0:
                _zoom_at(midpoint, distance / pinch_distance)
            pinch_distance = distance
        elif touches.size() == 1 and zoom > 1.001:
            camera_offset += pos - mouse_last
            _clamp_camera()
        mouse_last = pos
        queue_redraw()
        get_viewport().set_input_as_handled()
        return

    if event is InputEventMouseButton:
        if event.button_index == MOUSE_BUTTON_WHEEL_UP and event.pressed:
            _zoom_at(_to_design(event.position), 1.15)
            return
        if event.button_index == MOUSE_BUTTON_WHEEL_DOWN and event.pressed:
            _zoom_at(_to_design(event.position), 1.0 / 1.15)
            return
        if event.button_index == MOUSE_BUTTON_LEFT:
            mouse_dragging = event.pressed
            mouse_last = _to_design(event.position)
            if event.pressed:
                _handle_tap(event.position)
            return

    if event is InputEventMouseMotion and mouse_dragging and zoom > 1.001:
        var pos: Vector2 = _to_design(event.position)
        camera_offset += pos - mouse_last
        mouse_last = pos
        _clamp_camera()
        queue_redraw()
        return

func _handle_tap(screen_pos: Vector2) -> void:
    var design_pos := _to_design(screen_pos)
    var view := get_viewport_rect().size
    var scale_factor := minf(view.x / DESIGN.x, view.y / DESIGN.y)
    var origin := (view - DESIGN * scale_factor) * 0.5
    var hud_pos := (screen_pos - origin) / scale_factor
    if won:
        if replay_rect.has_point(design_pos):
            _restart()
        return
    if pause_rect.has_point(hud_pos):
        paused = not paused
        return
    if paused:
        paused = false
        return
    if hint_rect.has_point(hud_pos):
        _hint()
        return

    var world_pos := (design_pos - camera_offset) / zoom
    for i in range(TARGETS.size()):
        var item: Dictionary = TARGETS[i]
        if not found.has(item.id) and item.rect.has_point(world_pos):
            found.append(item.id)
            hint_target = -1
            hint_left = 0.0
            if found.size() == TARGETS.size():
                won = true
            queue_redraw()
            return

func _hint() -> void:
    for i in range(TARGETS.size()):
        if not found.has(TARGETS[i].id):
            hint_target = i
            hint_left = 3.0
            return

func _restart() -> void:
    found.clear()
    elapsed = 0.0
    hint_target = -1
    hint_left = 0.0
    paused = false
    won = false
    zoom = 1.0
    camera_offset = Vector2.ZERO
    queue_redraw()
'''
game.write_text(game_source, encoding="utf-8")
print("Added cat splash, larger bounded target labels, pinch zoom and one-finger panning while zoomed.")
