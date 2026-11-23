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
s = s.replace('window/stretch/mode="canvas_items"', 'window/stretch/mode="canvas_items"\\nwindow/stretch/aspect="expand"')
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

replace_once("var sound_enabled := true\n", "var sound_enabled := true\nvar music_enabled := true\n", "music state")
replace_once("const BAR_HEIGHT := 116.0", "const BAR_HEIGHT := 150.0", "roomier inventory panel")
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
    '''	var bar := Rect2(0, view.y - BAR_HEIGHT, view.x, BAR_HEIGHT)
	_draw_round_panel(Rect2(16, bar.position.y+4, view.x-32, BAR_HEIGHT-8), Color(0.035, 0.09, 0.15, 0.86), Color(0.82, 0.68, 0.43, 0.72), 24, 2)
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
		var card := Rect2(x+3, bar.position.y+37, slot_w-6, 102)
		_draw_round_panel(card, Color(0.09, 0.20, 0.29, 0.72), Color(0.74, 0.58, 0.34, 0.82), 17, 2)
		draw_texture_rect(item_textures[id], Rect2(x+slot_w*0.5-27, bar.position.y+42, 54, 52), false)
		var label := _fit_label(_short_name(ITEM_DATA[id].name), slot_w-14.0, 14)
		draw_string(font, Vector2(x+slot_w*0.5, bar.position.y+128), label, HORIZONTAL_ALIGNMENT_CENTER, slot_w-12, 14, CREAM)''',
    "restyle and enlarge inventory panel",
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
\t_draw_round_panel(rect, Color("#173d5d"), GOLD, 23, 2)
\tvar font := ThemeDB.fallback_font
\tvar text_size := font.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, 24)
\tdraw_string(font, rect.position + (rect.size-text_size)*0.5 + Vector2(0, 19), label, HORIZONTAL_ALIGNMENT_LEFT, -1, 24, CREAM)

func _draw_round_panel(rect: Rect2, fill: Color, border: Color = Color(0,0,0,0), radius: int = 18, border_width: int = 1) -> void:
\tvar style := StyleBoxFlat.new()
\tstyle.bg_color = fill
\tstyle.set_corner_radius_all(radius)
\tstyle.border_color = border
\tstyle.set_border_width_all(border_width)
\tstyle.shadow_color = Color(0.0, 0.015, 0.03, 0.28)
\tstyle.shadow_size = 9
\tstyle.shadow_offset = Vector2(0, 3)
\tdraw_style_box(style, rect)''',
    "rounded buttons and panels",
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
    "victory screen replay button",
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

func _win_rects(view: Vector2) -> Dictionary:
\tvar center := view * 0.5
\treturn {"panel":Rect2(center.x-300,center.y-190,600,380),"replay":Rect2(center.x-150,center.y+82,300,68)}

func _draw_win(view: Vector2) -> void:
\tdraw_rect(Rect2(Vector2.ZERO, view), Color(0.01,0.04,0.08,0.78), true)
\tvar r := _win_rects(view)
\t_draw_round_panel(r.panel, Color("#102d4d"), Color("#f6c66c"), 30, 3)
\t_center_text("ОСТРОВ СПАСЁН!", Vector2(view.x*0.5,view.y*0.5-112), 38, GOLD)
\t_center_text("Все 30 сокровищ найдены", Vector2(view.x*0.5,view.y*0.5-55), 25, CREAM)
\t_center_text("Время: " + _time_text(), Vector2(view.x*0.5,view.y*0.5-12), 23, Color("#bcebd0"))
\t_draw_round_panel(r.replay, Color("#bd762d"), Color("#ffe1a0"), 24, 2)
\t_center_text("ИГРАТЬ ЕЩЁ", r.replay.get_center()+Vector2(0,9), 24, CREAM)

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
\t_draw_round_panel(r.panel, Color("#102d4d"), GOLD, 30, 3)
\t_center_text("ПАУЗА", Vector2(view.x*0.5, view.y*0.5-125), 36, GOLD)
\t_draw_round_panel(r.sound, Color("#1d5272"), Color("#79cbb2"), 20, 2)
\tvar sound_text := "ЗВУК: ВКЛ" if sound_enabled else "ЗВУК: ВЫКЛ"
\t_center_text(sound_text, r.sound.get_center()+Vector2(0,8), 21, CREAM)
\t_draw_round_panel(r.music, Color("#1d5272"), Color("#79cbb2"), 20, 2)
\tvar music_text := "МУЗЫКА: ВКЛ" if music_enabled else "МУЗЫКА: ВЫКЛ"
\t_center_text(music_text, r.music.get_center()+Vector2(0,8), 21, CREAM)
\t_draw_round_panel(r.resume, Color("#9a692e"), GOLD, 23, 2)
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
if "func _settings_rects(" in source:
    raise SystemExit("Settings functions already exist; refusing to patch twice")
source += settings_code
game.write_text(source, encoding="utf-8")
make_music(root / "assets/audio/music.wav")
print("Original tropical-cove project patched without replacing its art or game scene.")
