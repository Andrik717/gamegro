from pathlib import Path
import math
import struct
import sys
import wave

root = Path(sys.argv[1])
project = root / "project.godot"
preset = root / "export_presets.cfg"
game = root / "scripts/game.gd"

# Patch the original tropical-cove project in place. Never replace its scene,
# artwork, item layout, or game UI with a prototype.
s = project.read_text(encoding="utf-8").replace("window/handheld/orientation=1", "window/handheld/orientation=0")
# Expand the visible canvas to the device aspect ratio instead of letterboxing.
s = s.replace('window/stretch/mode="canvas_items"', 'window/stretch/mode="canvas_items"\nwindow/stretch/aspect="expand"')
if "window/handheld/orientation=0" not in s:
    s = s.replace("[display]", "[display]\nwindow/handheld/orientation=0", 1)
project.write_text(s, encoding="utf-8")
s = preset.read_text(encoding="utf-8").replace("screen/orientation=1", "screen/orientation=0")
if "screen/orientation=0" not in s:
    raise SystemExit("Android landscape orientation was not configured")
preset.write_text(s, encoding="utf-8")

source = game.read_text(encoding="utf-8")
def replace_once(old: str, new: str, label: str) -> None:
    global source
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one match for {label}, got {count}")
    source = source.replace(old, new, 1)

replace_once(
    """func _viewport_layout() -> Dictionary:
	var view := get_viewport_rect().size
	var world_area := Rect2(Vector2.ZERO, Vector2(view.x, maxf(1.0, view.y - BAR_HEIGHT)))
	var base_scale := minf(world_area.size.x / WORLD_SIZE.x, world_area.size.y / WORLD_SIZE.y)
	var drawn := WORLD_SIZE * base_scale * zoom
	var origin := (world_area.size - WORLD_SIZE * base_scale) * 0.5 + camera_offset
	return {"view":view,"area":world_area,"base":base_scale,"scale":base_scale*zoom,"origin":origin}""",
    """func _viewport_layout() -> Dictionary:
	var view := get_viewport_rect().size
	# Fill the complete display with artwork; crop edges rather than showing navy bars.
	var world_area := Rect2(Vector2.ZERO, view)
	var base_scale := maxf(world_area.size.x / WORLD_SIZE.x, world_area.size.y / WORLD_SIZE.y)
	var origin := (world_area.size - WORLD_SIZE * base_scale) * 0.5 + camera_offset
	return {"view":view,"area":world_area,"base":base_scale,"scale":base_scale*zoom,"origin":origin}""",
    "fill the viewport with the scene background"
)

replace_once("var sound_enabled := true\n", "var sound_enabled := true\nvar music_enabled := true\n", "music state")
replace_once("const BAR_HEIGHT := 116.0", "const BAR_HEIGHT := 178.0", "roomier inventory panel")
replace_once("var audio_surf: AudioStreamPlayer\n", "var audio_surf: AudioStreamPlayer\nvar audio_music: AudioStreamPlayer\n", "music player")
replace_once(
    '''\taudio_surf = _player("res://assets/audio/surf.wav", true)
\taudio_surf.volume_db = -17.0
\tif sound_enabled:
\t\taudio_surf.play()''',
    '''\taudio_surf = _player("res://assets/audio/surf.wav", true)
\taudio_music = _player("res://assets/audio/music.wav", true)
\taudio_surf.volume_db = -14.0
\taudio_music.volume_db = -8.0
\tif music_enabled:
\t\taudio_surf.play()
\t\taudio_music.play()''',
    "audio setup",
)
replace_once('\t_draw_button(Rect2(view.x-158,top,64,56),"♫")', '\t_draw_button(Rect2(view.x-158,top,64,56),"♫" if music_enabled else "×")', "music icon")
replace_once(
    '''	var bar := Rect2(0, view.y - BAR_HEIGHT, view.x, BAR_HEIGHT)
	draw_rect(bar, Color("#09213a"), true)
	draw_rect(Rect2(0, bar.position.y, view.x, 5), GOLD, true)
	draw_string(font, Vector2(22, bar.position.y+25), "НАЙДИ ПРЕДМЕТЫ", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, GOLD)
	draw_string(font, Vector2(view.x-190, bar.position.y+25), "%02d / 30" % found.size(), HORIZONTAL_ALIGNMENT_LEFT, -1, 22, CREAM)
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
		draw_string(font, Vector2(x+slot_w*0.5, bar.position.y+94), _short_name(ITEM_DATA[id].name), HORIZONTAL_ALIGNMENT_CENTER, slot_w-8, 12, CREAM)''',
    '''	var bar := Rect2(24, view.y - BAR_HEIGHT - 14, view.x - 48, BAR_HEIGHT)
	draw_style_box(_rounded_style(Color(0.035, 0.09, 0.15, 0.72), Color(0.82, 0.68, 0.43, 0.82), 26, 18), bar)
	draw_string(font, Vector2(22, bar.position.y+27), "НАЙДИ ПРЕДМЕТЫ", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, CREAM)
	draw_string(font, Vector2(view.x-190, bar.position.y+27), "%02d / 30" % found.size(), HORIZONTAL_ALIGNMENT_LEFT, -1, 22, CREAM)
	var slots := mini(5, ITEM_COUNT - found.size())
	var slot_w := minf(128.0, (view.x-56.0)/5.0)
	var first_x := (view.x - slot_w*5.0)/2.0
	for slot in range(slots):
		var id := _next_visible_item(slot)
		if id < 0:
			continue
		var x := first_x + slot*slot_w
		var card := Rect2(x+3, bar.position.y+36, slot_w-6, 130)
		draw_style_box(_rounded_style(Color(0.09, 0.20, 0.29, 0.70), Color(0.74, 0.58, 0.34, 0.78), 16, 9), card)
		draw_texture_rect(item_textures[id], Rect2(x+slot_w*0.5-36, bar.position.y+39, 72, 72), false)
		_draw_fit_label(font, ITEM_DATA[id].name, x+slot_w*0.5, bar.position.y+157, slot_w-14.0, 12)''',
    "restyle and enlarge inventory panel",
)
replace_once(
    '''\tfor item in ITEM_DATA:
\t\tvar id: int = item.id
\t\tif found.has(id):
\t\t\tcontinue
\t\tvar radius := 34.0''',
    '''\tfor item in ITEM_DATA:
\t\tvar id: int = item.id
\t\tif found.has(id):
\t\t\tcontinue
\t\tif not _is_current_search_target(id):
\t\t\tcontinue
\t\tvar radius := 34.0''',
    "only accept items in the active five-item search queue",
)
replace_once(
    '''func _use_hint() -> void:
\tfor id in display_order:
\t\tif not found.has(id):
\t\t\thint_id = id
\t\t\thint_time = 2.5
\t\t\tif sound_enabled:
\t\t\t\taudio_hint.play()
\t\t\treturn''',
    '''func _use_hint() -> void:
\t# Hints must point only to one of the five currently requested items.
\tfor slot in range(5):
\t\tvar id := _next_visible_item(slot)
\t\tif id < 0:
\t\t\treturn
\t\thint_id = id
\t\thint_time = 2.5
\t\tif sound_enabled:
\t\t\taudio_hint.play()
\t\treturn''',
    "restrict hints to the active five-item queue",
)
replace_once(
    '''func _next_visible_item(slot: int) -> int:
\tvar shown := 0
\tfor id in display_order:
\t\tif found.has(id):
\t\t\tcontinue
\t\tif shown == slot:
\t\t\treturn id
\t\tshown += 1
\treturn -1''',
    '''func _next_visible_item(slot: int) -> int:
\tvar shown := 0
\tfor id in display_order:
\t\tif found.has(id):
\t\t\tcontinue
\t\tif shown == slot:
\t\t\treturn id
\t\tshown += 1
\treturn -1

func _is_current_search_target(item_id: int) -> bool:
\tfor slot in range(5):
\t\tif _next_visible_item(slot) == item_id:
\t\t\treturn true
\treturn false''',
    "identify only the five visible search targets",
)

replace_once(
    '''func _handle_tap(point: Vector2) -> void:
\tif sound_enabled and audio_tap != null:
\t\taudio_tap.play()
\tvar view := get_viewport_rect().size''',
    '''func _handle_tap(point: Vector2) -> void:
\t# Ignore generic screen taps; keep only meaningful gameplay audio.
\tvar view := get_viewport_rect().size''',
    "remove generic tap sound",
)

replace_once(
    '''func _short_name(value: String) -> String:
\treturn value if value.length() <= 12 else value.substr(0,11)+"…"''',
    '''func _short_name(value: String) -> String:
\treturn value if value.length() <= 12 else value.substr(0,11)+"…"

func _fit_label(value: String, max_width: float, base_size: int) -> String:
\tvar result := value
\tvar font := ThemeDB.fallback_font
\twhile result.length() > 3 and font.get_string_size(result, HORIZONTAL_ALIGNMENT_LEFT, -1, base_size).x > max_width:
\t\tresult = result.left(result.length() - 2) + "…"
\treturn result''',
    "measured label fit",
)
replace_once(
    '''func _draw_button(rect: Rect2, label: String) -> void:
\tdraw_rect(rect, Color("#173d5d"), true)
\tdraw_rect(rect, GOLD, false, 3.0)
\tdraw_string(ThemeDB.fallback_font, rect.position+Vector2(rect.size.x*0.5-10,rect.size.y*0.5+10), label, HORIZONTAL_ALIGNMENT_LEFT, -1, 24, CREAM)''',
    '''func _draw_button(rect: Rect2, label: String) -> void:
\tdraw_style_box(_rounded_style(Color("#173d5d"), GOLD, 23, 12), rect)
\tvar font := ThemeDB.fallback_font
\tvar text_size := font.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, 24)
\tdraw_string(font, rect.position + (rect.size-text_size)*0.5 + Vector2(0, 19), label, HORIZONTAL_ALIGNMENT_LEFT, -1, 24, CREAM)''',
    "rounded top controls",
)
replace_once(
    '\t\t\t_zoom_at(pinch_center, factor, center-pinch_center)',
    '\t\t\t_zoom_at(pinch_center, factor)',
    "pinch zoom without gesture panning",
)
replace_once(
    '''\telif touches.size() == 1:
\t\tif zoom > 1.02:
\t\t\tcamera_offset += relative
\t\t\tdragging = true
\t\tone_finger_last = pos''',
    '''\telif touches.size() == 1:
\t\t# Pan only after zooming in; at the base scale the scene stays fixed.
\t\tif zoom > 1.02:
\t\t\tcamera_offset += relative
\t\t\tdragging = true
\t\telse:
\t\t\tdragging = false
\t\tone_finger_last = pos''',
    "allow panning only while zoomed",
)
replace_once(
    '''\tif paused:
\t\tpaused = false
\t\treturn
\tif won:''',
    '''\tif paused:
\t\t_handle_settings_tap(point, view)
\t\treturn
\tif won:''',
    "settings touch handling",
)
replace_once(
    '''\t\tif point.x > view.x-166.0:
\t\t\tsound_enabled = not sound_enabled
\t\t\tif sound_enabled:
\t\t\t\taudio_surf.play()
\t\t\telse:
\t\t\t\taudio_surf.stop()
\t\t\treturn''',
    '''\t\tif point.x > view.x-166.0:
\t\t\t_toggle_music()
\t\t\treturn''',
    "top bar music toggle",
)
replace_once(
    '''\tif paused:
\t\tdraw_rect(Rect2(Vector2.ZERO, view), Color(0,0,0,0.62), true)
\t\t_center_text("ПАУЗА  •  КОСНИТЕСЬ, ЧТОБЫ ПРОДОЛЖИТЬ", view * 0.5, 30, CREAM)''',
    '''\tif paused:
\t\t_draw_settings(view)''',
    "settings panel draw",
)

replace_once(
    '''\tif won:
\t\tdraw_rect(Rect2(Vector2.ZERO, view), Color(0,0,0,0.68), true)
\t\t_center_text("ВСЕ 30 СОКРОВИЩ НАЙДЕНЫ!", view*0.5-Vector2(0,35), 38, GOLD)
\t\t_center_text("Коснитесь экрана, чтобы сыграть ещё раз", view*0.5+Vector2(0,22), 24, CREAM)''',
    '''\tif won:
\t\t_draw_win(view)''',
    "modern victory screen",
)
replace_once(
    '''\tif won:
\t\t_reset_round()
\t\treturn''',
    '''\tif won:
\t\tvar win_rects := _win_rects(view)
\t\tif win_rects.replay.has_point(point):
\t\t\t_reset_round()
\t\treturn''',
    "victory replay button",
)

# Generate a small original looped tropical marimba cue; the source archive
# only contains surf ambience, not a music track.
def make_music(path: Path) -> None:
    rate, duration = 22050, 16.0
    chords = [[261.63,329.63,392.00,493.88],[220.00,261.63,329.63,392.00],[174.61,220.00,261.63,329.63],[196.00,246.94,293.66,392.00]]
    events = []
    melody = [0,2,1,3,2,1,0,2,3,1,2,0,1,3,2,1]
    for i, note in enumerate(melody):
        events.append((i*0.5, chords[i//4][note], 0.19, 1.05, -0.35 if i%2 else 0.35))
    for bar in range(4):
        root_note = chords[bar][0]/2.0
        events.extend([(bar*2.0,root_note,0.12,1.8,0.0),(bar*2.0+1.0,root_note*1.5,0.055,0.8,0.0)])
    frames = bytearray()
    for n in range(int(rate*duration)):
        t = n/rate
        chord = chords[int(t//4.0)%4]
        pad = sum(math.sin(2*math.pi*f*0.5*t)*0.012 for f in chord[:3])
        left = right = pad*(0.82+0.18*math.sin(2*math.pi*0.25*t))
        for start,freq,amp,decay,pan in events:
            age=t-start
            if 0 <= age < decay:
                env=math.exp(-4.2*age/decay)
                tone=(math.sin(2*math.pi*freq*age)+0.22*math.sin(2*math.pi*freq*2.01*age))*amp*env
                left += tone*(1.0-pan*0.35)
                right += tone*(1.0+pan*0.35)
        edge=min(1.0,t/0.04,(duration-t)/0.08)
        left=max(-0.85,min(0.85,left*edge))
        right=max(-0.85,min(0.85,right*edge))
        frames += struct.pack("<hh",int(left*32767),int(right*32767))
    path.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(path),"wb") as out:
        out.setnchannels(2); out.setsampwidth(2); out.setframerate(rate); out.writeframes(frames)

settings_code = '''

func _rounded_style(fill: Color, border: Color, radius: int = 18, shadow: int = 10) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = fill
	style.border_color = border
	style.set_border_width_all(1)
	style.set_corner_radius_all(radius)
	style.shadow_color = Color(0.0, 0.0, 0.0, 0.28)
	style.shadow_size = shadow
	style.shadow_offset = Vector2(0, 4)
	return style

func _toggle_music() -> void:
\tmusic_enabled = not music_enabled
\tif music_enabled:
\t\tif audio_surf != null and not audio_surf.playing:
\t\t\taudio_surf.play()
\t\tif audio_music != null and not audio_music.playing:
\t\t\taudio_music.play()
\telse:
\t\tif audio_surf != null:
\t\t\taudio_surf.stop()
\t\tif audio_music != null:
\t\t\taudio_music.stop()
\tqueue_redraw()

func _win_rects(view: Vector2) -> Dictionary:
\tvar center := view * 0.5
\treturn {"panel":Rect2(center.x-300,center.y-190,600,380),"replay":Rect2(center.x-150,center.y+82,300,68)}

func _draw_win(view: Vector2) -> void:
\tdraw_rect(Rect2(Vector2.ZERO, view), Color(0.01,0.04,0.08,0.78), true)
\tvar r := _win_rects(view)
\tdraw_style_box(_rounded_style(Color("#102d4d"), Color("#f6c66c"), 30, 18), r.panel)
\t_center_text("ОСТРОВ СПАСЁН!", Vector2(view.x*0.5,view.y*0.5-112), 38, GOLD)
\t_center_text("Все 30 сокровищ найдены", Vector2(view.x*0.5,view.y*0.5-55), 25, CREAM)
\t_center_text("Время: " + _time_text(), Vector2(view.x*0.5,view.y*0.5-12), 23, Color("#bcebd0"))
\tdraw_style_box(_rounded_style(Color("#bd762d"), Color("#ffe1a0"), 24, 14), r.replay)
\t_center_text("ИГРАТЬ ЕЩЁ", r.replay.get_center()+Vector2(0,9), 24, CREAM)

func _settings_rects(view: Vector2) -> Dictionary:
\tvar center := view * 0.5
\treturn {
\t\t"panel": Rect2(center.x-245, center.y-190, 490, 380),
\t\t"sound": Rect2(center.x-190, center.y-68, 380, 58),
\t\t"music": Rect2(center.x-190, center.y+2, 380, 58),
\t\t"resume": Rect2(center.x-190, center.y+82, 380, 66)
\t}

func _draw_settings(view: Vector2) -> void:
\tdraw_rect(Rect2(Vector2.ZERO, view), Color(0.01,0.04,0.08,0.78), true)
\tvar r := _settings_rects(view)
\tdraw_style_box(_rounded_style(Color("#102d4d"), GOLD, 30, 18), r.panel)
\t_center_text("ПАУЗА", Vector2(view.x*0.5, view.y*0.5-125), 36, GOLD)
\tdraw_style_box(_rounded_style(Color("#1d5272"), Color("#79cbb2"), 20, 12), r.sound)
\tvar sound_text := "ЗВУК: ВКЛ" if sound_enabled else "ЗВУК: ВЫКЛ"
\t_center_text(sound_text, r.sound.get_center()+Vector2(0,8), 21, CREAM)
\tdraw_style_box(_rounded_style(Color("#1d5272"), Color("#79cbb2"), 20, 12), r.music)
\tvar music_text := "МУЗЫКА: ВКЛ" if music_enabled else "МУЗЫКА: ВЫКЛ"
\t_center_text(music_text, r.music.get_center()+Vector2(0,8), 21, CREAM)
\tdraw_style_box(_rounded_style(Color("#9a692e"), GOLD, 23, 14), r.resume)
\t_center_text("ПРОДОЛЖИТЬ", r.resume.get_center()+Vector2(0,8), 23, CREAM)

func _handle_settings_tap(point: Vector2, view: Vector2) -> void:
\tvar r := _settings_rects(view)
\tif r.sound.has_point(point):
\t\tsound_enabled = not sound_enabled
\telif r.music.has_point(point):
\t\t_toggle_music()
\telif r.resume.has_point(point):
\t\tpaused = false
\tqueue_redraw()
'''

source += '''

func _draw_fit_label(font: Font, value: String, center_x: float, baseline_y: float, max_width: float, base_size: int) -> void:
	# Keep a consistent readable font size. Wrap the full item name onto two
	# centered lines instead of shrinking or clipping it to fit a narrow card.
	var words := value.split(" ", false)
	var lines: Array[String] = [""]
	for word in words:
		var candidate := word if lines[-1].is_empty() else lines[-1] + " " + word
		if font.get_string_size(candidate, HORIZONTAL_ALIGNMENT_LEFT, -1, base_size).x <= max_width:
			lines[-1] = candidate
		elif lines.size() < 2:
			lines.append(word)
		else:
			lines[1] += "…"
			break
	var line_height := font.get_height(base_size)
	var start_y := baseline_y - float(lines.size()-1) * line_height * 0.5
	for i in range(lines.size()):
		var line := lines[i]
		var width := font.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, base_size).x
		draw_string(font, Vector2(center_x-width*0.5, start_y + float(i)*line_height), line, HORIZONTAL_ALIGNMENT_LEFT, -1, base_size, CREAM)
'''

if "func _settings_rects(" in source:
    raise SystemExit("Settings functions already exist; refusing to patch twice")
source += settings_code

# Story layer: preserve the existing island scene and introduce the first chapter.
replace_once("var won := false", "var won := false\nvar story_intro_pending := true", "story intro state")
replace_once(
    '''\t_draw_hud(view)
\tif paused:''',
    '''\t_draw_hud(view)
\tif story_intro_pending:
\t\t_draw_story_intro(view)
\tif paused:''',
    "show the opening story card",
)
replace_once(
    '''\tvar view := get_viewport_rect().size
\tif paused:
\t\t_handle_settings_tap(point, view)''',
    '''\tvar view := get_viewport_rect().size
\tif story_intro_pending:
\t\tstory_intro_pending = false
\t\tqueue_redraw()
\t\treturn
\tif paused:
\t\t_handle_settings_tap(point, view)''',
    "dismiss the opening story card",
)
source += '''

func _draw_story_intro(view: Vector2) -> void:
\tdraw_rect(Rect2(Vector2.ZERO, view), Color(0.01,0.04,0.08,0.70), true)
\tvar panel := Rect2(view.x*0.5-420, view.y*0.5-190, 840, 380)
\tdraw_style_box(_rounded_style(Color("#102d4d"), Color("#f6c66c"), 30, 20), panel)
\t_center_text("ТАЙНА ЗАТЕРЯННОГО АРХИПЕЛАГА", Vector2(view.x*0.5,view.y*0.5-112), 31, GOLD)
\t_center_text("Шторм выбросил тебя на неизвестный остров.", Vector2(view.x*0.5,view.y*0.5-45), 23, CREAM)
\t_center_text("В бутылке найдено письмо смотрителя маяка.", Vector2(view.x*0.5,view.y*0.5-7), 23, CREAM)
\t_center_text("Десять артефактов помогут вернуть свет архипелагу.", Vector2(view.x*0.5,view.y*0.5+31), 22, CREAM)
\tdraw_style_box(_rounded_style(Color("#9a692e"), GOLD, 22, 14), Rect2(view.x*0.5-210,view.y*0.5+91,420,62))
\t_center_text("НАЧАТЬ ПУТЕШЕСТВИЕ", Vector2(view.x*0.5,view.y*0.5+130), 22, CREAM)
'''
source = source.replace("ОСТРОВ СПАСЁН!", "ПЕРВАЯ ГЛАВА ПРОЙДЕНА!")
source = source.replace("Все 30 сокровищ найдены", "Найден первый фрагмент карты")
# Package the canonical story data alongside the exported game.
story_source = Path(__file__).resolve().parent.parent / "game_data" / "story.json"
if not story_source.is_file():
    raise SystemExit("Missing game_data/story.json")
story_target = root / "data" / "story.json"
story_target.parent.mkdir(parents=True, exist_ok=True)
story_target.write_text(story_source.read_text(encoding="utf-8"), encoding="utf-8")
# Chapter backgrounds are PNG files under assets/backgrounds.
background_dir = root / "assets" / "backgrounds"
required_backgrounds = ["tropical_cove.png", "bg_02.png", "bg_03.png", "bg_04.png", "bg_05.png"]
missing_backgrounds = [name for name in required_backgrounds if not (background_dir / name).is_file()]
if missing_backgrounds:
    raise SystemExit("Missing existing chapter PNG backgrounds: " + ", ".join(missing_backgrounds))

replace_once("const CREAM :=", "const LEVEL_DATA := [
	{\"name\":\"Затерянный остров\",\"background\":\"res://assets/backgrounds/tropical_cove.png\",\"artifact\":\"Фрагмент карты\"},
	{\"name\":\"Древние джунгли\",\"background\":\"res://assets/backgrounds/bg_02.png\",\"artifact\":\"Камень памяти\"},
	{\"name\":\"Пещера водопада\",\"background\":\"res://assets/backgrounds/bg_03.png\",\"artifact\":\"Жемчужина приливов\"},
	{\"name\":\"Бухта пиратов\",\"background\":\"res://assets/backgrounds/bg_04.png\",\"artifact\":\"Печать капитана\"},
	{\"name\":\"Затонувшая лагуна\",\"background\":\"res://assets/backgrounds/bg_05.png\",\"artifact\":\"Сердце океана\"},
	{\"name\":\"Остров огня\",\"background\":\"res://assets/backgrounds/volcano_forge.png\",\"artifact\":\"Огненный кристалл\"},
	{\"name\":\"Небесная обсерватория\",\"background\":\"res://assets/backgrounds/sky_observatory.png\",\"artifact\":\"Звёздный компас\"},
	{\"name\":\"Ледяное королевство\",\"background\":\"res://assets/backgrounds/ice_kingdom.png\",\"artifact\":\"Кристалл памяти\"},
	{\"name\":\"Затерянный город\",\"background\":\"res://assets/backgrounds/lost_city.png\",\"artifact\":\"Сердце архипелага\"},
	{\"name\":\"Последний маяк\",\"background\":\"res://assets/backgrounds/final_lighthouse.png\",\"artifact\":\"Свет архипелага\"}
]
const CREAM :=", "ten playable chapter definitions")
replace_once("var story_intro_pending := true", "var story_intro_pending := true\nvar current_level := 0\nvar unlocked_level_count := 1\nvar map_open := false", "chapter progress state")
replace_once('background = load("res://assets/backgrounds/tropical_cove.png")', "_load_current_level()", "load the selected chapter background")
replace_once("var p: Vector2 = ITEM_DATA[i].pos", "var p: Vector2 = _item_position(ITEM_DATA[i])", "level-specific object positions in draw")
replace_once('''\t\tvar radius := 34.0\n\t\tif Rect2(item.pos-Vector2.ONE*radius,Vector2.ONE*radius*2).has_point(world_pos):''', '''\t\tvar radius := 34.0\n\t\tvar item_pos := _item_position(item)\n\t\tif Rect2(item_pos-Vector2.ONE*radius,Vector2.ONE*radius*2).has_point(world_pos):''', "level-specific object hitboxes")
replace_once('''\tif story_intro_pending:\n\t\t_draw_story_intro(view)\n\tif paused:''', '''\tif story_intro_pending:\n\t\t_draw_story_intro(view)\n\tif map_open:\n\t\t_draw_map(view)\n\tif paused:''', "draw the archipelago map")
replace_once('''\tif story_intro_pending:\n\t\tstory_intro_pending = false\n\t\tqueue_redraw()\n\t\treturn\n\tif paused:''', '''\tif story_intro_pending:\n\t\tstory_intro_pending = false\n\t\tqueue_redraw()\n\t\treturn\n\tif map_open:\n\t\t_handle_map_tap(point, view)\n\t\treturn\n\tif paused:''', "handle map interactions")
replace_once('''\t_draw_button(Rect2(view.x-158,top,64,56),"♫" if music_enabled else "×")''', '''\t_draw_button(Rect2(view.x-158,top,64,56),"♫" if music_enabled else "×")\n\t_draw_button(Rect2(view.x-240,top,68,56),"M")''', "add map control")
replace_once('''\t\tif point.x > view.x-166.0:\n\t\t\t_toggle_music()\n\t\t\treturn''', '''\t\tif point.x > view.x-240.0 and point.x <= view.x-166.0:\n\t\t\tmap_open = true\n\t\t\tqueue_redraw()\n\t\t\treturn\n\t\tif point.x > view.x-166.0:\n\t\t\t_toggle_music()\n\t\t\treturn''', "open map from top bar")
replace_once('''\tif won:\n\t\tvar win_rects := _win_rects(view)\n\t\tif win_rects.replay.has_point(point):\n\t\t\t_reset_round()\n\t\treturn''', '''\tif won:\n\t\tvar win_rects := _win_rects(view)\n\t\tif win_rects.replay.has_point(point):\n\t\t\t_advance_level()\n\t\treturn''', "advance to the next unlocked chapter")
source = source.replace("_center_text(\"ПЕРВАЯ ГЛАВА ПРОЙДЕНА!\", Vector2(view.x*0.5,view.y*0.5-112), 38, GOLD)", "_center_text(\"ГЛАВА %02d ПРОЙДЕНА\" % [current_level+1], Vector2(view.x*0.5,view.y*0.5-112), 34, GOLD)")
source = source.replace("_center_text(\"Найден первый фрагмент карты\", Vector2(view.x*0.5,view.y*0.5-55), 25, CREAM)", "_center_text(\"Артефакт: \" + LEVEL_DATA[current_level].artifact, Vector2(view.x*0.5,view.y*0.5-55), 23, CREAM)")
source = source.replace("_center_text(\"ИГРАТЬ ЕЩЁ\", r.replay.get_center()+Vector2(0,9), 24, CREAM)", "_center_text(\"СЛЕДУЮЩАЯ ЛОКАЦИЯ\", r.replay.get_center()+Vector2(0,9), 22, CREAM)")

source += """
func _load_current_level() -> void:
	background = load(LEVEL_DATA[current_level].background)
	if background == null:
		push_error("Missing level background: " + LEVEL_DATA[current_level].background)

func _item_position(item: Dictionary) -> Vector2:
	var original: Vector2 = item.pos
	if current_level == 0:
		return original
	var center := WORLD_SIZE * 0.5
	var rotated := (original-center).rotated(float(current_level)*0.39)
	var drift := Vector2(sin(float(item.id)*1.7+current_level)*18.0, cos(float(item.id)*1.3+current_level)*16.0)
	var point := center + rotated + drift
	return Vector2(clampf(point.x, 64.0, WORLD_SIZE.x-64.0), clampf(point.y, 64.0, WORLD_SIZE.y-64.0))

func _advance_level() -> void:
	if current_level < LEVEL_DATA.size()-1:
		current_level += 1
		unlocked_level_count = maxi(unlocked_level_count, current_level+1)
	else:
		current_level = 0
		unlocked_level_count = LEVEL_DATA.size()
	_load_current_level()
	_reset_round()

func _map_card_rect(index: int, view: Vector2) -> Rect2:
	var panel_left := view.x*0.5-575.0
	var panel_top := view.y*0.5-275.0
	var col := index % 5
	var row := int(index / 5)
	return Rect2(panel_left+28.0+float(col)*218.0, panel_top+112.0+float(row)*166.0, 204.0, 148.0)

func _draw_map(view: Vector2) -> void:
	draw_rect(Rect2(Vector2.ZERO,view),Color(0.01,0.04,0.08,0.82),true)
	var panel := Rect2(view.x*0.5-575.0,view.y*0.5-275.0,1150.0,550.0)
	draw_style_box(_rounded_style(Color("#102d4d"),Color("#f6c66c"),30,20),panel)
	_center_text("КАРТА ЗАТЕРЯННОГО АРХИПЕЛАГА",Vector2(view.x*0.5,view.y*0.5-220.0),30,GOLD)
	for i in range(LEVEL_DATA.size()):
		var r := _map_card_rect(i,view)
		var open := i < unlocked_level_count
		var active := i == current_level
		var fill := Color("#246b70") if active else (Color("#1c4d68") if open else Color("#202e3b"))
		var edge := GOLD if active else (Color("#78c8a4") if open else Color("#53616d"))
		draw_style_box(_rounded_style(fill,edge,18,8),r)
		_center_text("%02d" % (i+1),Vector2(r.get_center().x,r.position.y+42),27,GOLD if open else Color("#89949b"))
		var title: String = str(LEVEL_DATA[i].name)
		_center_text(title,Vector2(r.get_center().x,r.position.y+82),15,CREAM if open else Color("#89949b"))
		_center_text("ОТКРЫТО" if open else "ЗАКРЫТО",Vector2(r.get_center().x,r.position.y+119),12,Color("#a9edc9") if open else Color("#89949b"))
	_draw_button(Rect2(panel.position.x+panel.size.x-82,panel.position.y+18,56,48),"×")

func _handle_map_tap(point: Vector2, view: Vector2) -> void:
	var panel := Rect2(view.x*0.5-575.0,view.y*0.5-275.0,1150.0,550.0)
	if Rect2(panel.position.x+panel.size.x-92,panel.position.y+12,76,60).has_point(point):
		map_open = false
		queue_redraw()
		return
	for i in range(unlocked_level_count):
		if _map_card_rect(i,view).has_point(point):
			current_level = i
			map_open = false
			_load_current_level()
			_reset_round()
			return
"""

game.write_text(source, encoding="utf-8")
make_music(root / "assets/audio/music.wav")
from level_content import enhance_game
enhance_game(root)

# Keep the story card inside short landscape displays.
source = game.read_text(encoding="utf-8")
old_intro = """func _draw_story_intro(view: Vector2) -> void:
	draw_rect(Rect2(Vector2.ZERO, view), Color(0.01,0.04,0.08,0.70), true)
	var panel := Rect2(view.x*0.5-420, view.y*0.5-190, 840, 380)
	draw_style_box(_rounded_style(Color("#102d4d"), Color("#f6c66c"), 30, 20), panel)
	_center_text("ТАЙНА ЗАТЕРЯННОГО АРХИПЕЛАГА", Vector2(view.x*0.5,view.y*0.5-112), 31, GOLD)
	_center_text("Шторм выбросил тебя на неизвестный остров.", Vector2(view.x*0.5,view.y*0.5-45), 23, CREAM)
	_center_text("В бутылке найдено письмо смотрителя маяка.", Vector2(view.x*0.5,view.y*0.5-7), 23, CREAM)
	_center_text("Десять артефактов помогут вернуть свет архипелагу.", Vector2(view.x*0.5,view.y*0.5+31), 22, CREAM)
	draw_style_box(_rounded_style(Color("#9a692e"), GOLD, 22, 14), Rect2(view.x*0.5-210,view.y*0.5+91,420,62))
	_center_text("НАЧАТЬ ПУТЕШЕСТВИЕ", Vector2(view.x*0.5,view.y*0.5+130), 22, CREAM)"""
new_intro = """func _draw_story_intro(view: Vector2) -> void:
	draw_rect(Rect2(Vector2.ZERO, view), Color(0.01,0.04,0.08,0.70), true)
	var center := view * 0.5
	var panel_w := minf(840.0, view.x-32.0)
	var panel_h := minf(380.0, view.y-32.0)
	var panel := Rect2(center.x-panel_w*0.5,center.y-panel_h*0.5,panel_w,panel_h)
	var factor := minf(1.0,minf(panel_w/840.0,panel_h/380.0))
	draw_style_box(_rounded_style(Color("#102d4d"), Color("#f6c66c"), 24, 12), panel)
	_center_text("ТАЙНА ЗАТЕРЯННОГО АРХИПЕЛАГА", center+Vector2(0,-panel_h*0.29), maxi(15,int(31*factor)), GOLD)
	_center_text("Шторм выбросил тебя на неизвестный остров.", center+Vector2(0,-panel_h*0.12), maxi(12,int(23*factor)), CREAM)
	_center_text("В бутылке найдено письмо смотрителя маяка.", center+Vector2(0,-panel_h*0.01), maxi(12,int(23*factor)), CREAM)
	_center_text("Десять артефактов помогут вернуть свет архипелагу.", center+Vector2(0,panel_h*0.10), maxi(12,int(22*factor)), CREAM)
	var button := Rect2(center.x-minf(210.0,panel_w*0.34),center.y+panel_h*0.25,minf(420.0,panel_w*0.68),minf(62.0,panel_h*0.19))
	draw_style_box(_rounded_style(Color("#9a692e"), GOLD, 18, 8), button)
	_center_text("НАЧАТЬ ПУТЕШЕСТВИЕ", button.get_center()+Vector2(0,8), maxi(12,int(22*factor)), CREAM)"""
if source.count(old_intro) != 1:
    raise SystemExit("Story intro anchor mismatch")
source = source.replace(old_intro,new_intro,1)
game.write_text(source,encoding="utf-8")

# Make the map and modal panels fit compact landscape viewports.
def replace_gd_function(text, signature, next_signature, body):
    start = text.index(signature)
    try:
        end = text.index(next_signature, start)
    except ValueError:
        end = len(text)
    return text[:start] + body.rstrip() + ("\n\n" + text[end:] if end < len(text) else "\n")

source = replace_gd_function(source, "func _win_rects(view: Vector2)", "func _draw_win(view: Vector2)", """func _win_rects(view: Vector2) -> Dictionary:
	var center := view * 0.5
	var panel_w := minf(600.0, view.x-32.0)
	var panel_h := minf(380.0, view.y-32.0)
	var panel := Rect2(center.x-panel_w*0.5,center.y-panel_h*0.5,panel_w,panel_h)
	var button_w := minf(300.0,panel_w-40.0)
	return {"panel":panel,"replay":Rect2(center.x-button_w*0.5,panel.position.y+panel.size.y-78.0,button_w,58.0)}""")
source = replace_gd_function(source, "func _settings_rects(view: Vector2)", "func _draw_settings(view: Vector2)", """func _settings_rects(view: Vector2) -> Dictionary:
	var center := view * 0.5
	var panel_w := minf(490.0,view.x-32.0)
	var panel_h := minf(380.0,view.y-32.0)
	var panel := Rect2(center.x-panel_w*0.5,center.y-panel_h*0.5,panel_w,panel_h)
	var button_w := panel_w-56.0
	var button_h := minf(58.0,(panel_h-112.0)/3.0)
	var first_y := panel.position.y+68.0
	return {"panel":panel,"sound":Rect2(center.x-button_w*0.5,first_y,button_w,button_h),"music":Rect2(center.x-button_w*0.5,first_y+button_h+10.0,button_w,button_h),"resume":Rect2(center.x-button_w*0.5,first_y+2.0*(button_h+10.0),button_w,button_h)}""")
source = replace_gd_function(source, "func _map_card_rect(index: int, view: Vector2)", "func _draw_map(view: Vector2)", """func _map_panel_rect(view: Vector2) -> Rect2:
	return Rect2(16.0,16.0,maxf(1.0,view.x-32.0),maxf(1.0,view.y-32.0))

func _map_card_rect(index: int, view: Vector2) -> Rect2:
	var panel := _map_panel_rect(view)
	var gap := 10.0
	var card_w := (panel.size.x-50.0)/2.0
	var card_h := minf(86.0,(panel.size.y-104.0-4.0*gap)/5.0)
	var col := index % 2
	var row := int(index / 2)
	return Rect2(panel.position.x+20.0+float(col)*(card_w+gap),panel.position.y+78.0+float(row)*(card_h+gap),card_w,card_h)""")
source = replace_gd_function(source, "func _draw_map(view: Vector2)", "func _handle_map_tap(point: Vector2, view: Vector2)", """func _draw_map(view: Vector2) -> void:
	draw_rect(Rect2(Vector2.ZERO,view),Color(0.01,0.04,0.08,0.84),true)
	var panel := _map_panel_rect(view)
	draw_style_box(_rounded_style(Color("#102d4d"),Color("#f6c66c"),24,14),panel)
	_center_text("КАРТА АРХИПЕЛАГА",Vector2(view.x*0.5,panel.position.y+48.0),minf(26.0,view.y*0.055),GOLD)
	for i in range(LEVEL_DATA.size()):
		var r := _map_card_rect(i,view)
		var open := i < unlocked_level_count
		var active := i == current_level
		var fill := Color("#246b70") if active else (Color("#1c4d68") if open else Color("#202e3b"))
		var edge := GOLD if active else (Color("#78c8a4") if open else Color("#53616d"))
		draw_style_box(_rounded_style(fill,edge,14,6),r)
		var fs := clampi(int(r.size.y*0.30),12,22)
		_center_text("%02d  %s" % [i+1,str(LEVEL_DATA[i].name)],Vector2(r.get_center().x,r.position.y+r.size.y*0.48),fs,CREAM if open else Color("#89949b"))
		_center_text("ОТКРЫТО" if open else "ЗАКРЫТО",Vector2(r.get_center().x,r.position.y+r.size.y*0.80),clampi(fs-3,10,16),Color("#a9edc9") if open else Color("#89949b"))
	_draw_button(Rect2(panel.position.x+panel.size.x-58.0,panel.position.y+12.0,44.0,42.0),"×")""")
source = replace_gd_function(source, "func _handle_map_tap(point: Vector2, view: Vector2)", "func _draw_story_intro(view: Vector2)", """func _handle_map_tap(point: Vector2, view: Vector2) -> void:
	var panel := _map_panel_rect(view)
	if Rect2(panel.position.x+panel.size.x-66.0,panel.position.y+6.0,60.0,54.0).has_point(point):
		map_open = false
		queue_redraw()
		return
	for i in range(unlocked_level_count):
		if _map_card_rect(i,view).has_point(point):
			current_level = i
			map_open = false
			_load_current_level()
			_reset_round()
			return""")
game.write_text(source,encoding="utf-8")

# Apply interactive chapter puzzles after every other generated-script rewrite.
from chapter_mechanics import apply_chapter_mechanics
apply_chapter_mechanics(root)

# Copy the normalized story only after level_content has converted every chapter
# background reference from SVG to the final PNG paths used by the game.
story_target.write_text(story_source.read_text(encoding="utf-8"), encoding="utf-8")

print("Original tropical-cove project patched without replacing its art or game scene.")
