from pathlib import Path
import re, sys

root = Path(sys.argv[1])
project = root / "project.godot"
preset = root / "export_presets.cfg"
game = root / "scripts/game.gd"

# Android landscape: Godot orientation enum 0 = landscape.
s = project.read_text(encoding="utf-8")
s = re.sub(r'(?m)^window/handheld/orientation=.*$', 'window/handheld/orientation=0', s)
if "window/handheld/orientation=" not in s:
    s += '\n[display]\nwindow/handheld/orientation=0\n'
project.write_text(s, encoding="utf-8")

if preset.exists():
    s = preset.read_text(encoding="utf-8")
    s = re.sub(r'(?m)^screen/orientation=.*$', 'screen/orientation=0', s)
    preset.write_text(s, encoding="utf-8")

s = game.read_text(encoding="utf-8")

# Keep the background still: one-finger dragging is disabled; pinch zoom stays centered.
s = s.replace('_zoom_at(pinch_center, factor, center-pinch_center)', '_zoom_at(get_viewport_rect().size * 0.5, factor)')
old = '''\telif touches.size() == 1:
\t\tif zoom > 1.02:
\t\t\tcamera_offset += relative
\t\t\tdragging = true
\t\tone_finger_last = pos'''
new = '''\telif touches.size() == 1:
\t\t# The scene is fixed in place; only two-finger pinch may change zoom.
\t\tone_finger_last = pos'''
if old in s:
    s = s.replace(old, new)
else:
    # Be tolerant of whitespace variations.
    s = re.sub(r'(?m)^\s*elif touches\.size\(\) == 1:\n\s*if zoom > 1\.02:\n\s*camera_offset \+= relative\n\s*dragging = true\n\s*one_finger_last = pos',
               '\telif touches.size() == 1:\n\t\t# Fixed background: one-finger panning disabled.\n\t\tone_finger_last = pos', s)

# Make target labels fit their own cards; use shorter font and clipping width.
s = s.replace('slot_w-8, 12, CREAM)', 'slot_w-12, 10, CREAM)')

# Give the existing looping ambience an audible level and provide a music toggle in pause/settings.
s = s.replace('audio_surf.volume_db = -17.0', 'audio_surf.volume_db = -7.0')
if 'var settings_open := false' not in s:
    s = s.replace('var paused := false', 'var paused := false\nvar settings_open := false')
# Show an explicit settings row in the pause overlay.
old_pause = '''\tif paused:
\t\tdraw_rect(Rect2(Vector2.ZERO, view), Color(0,0,0,0.62), true)
\t\t_center_text("ПАУЗА  •  КОСНИТЕСЬ, ЧТОБЫ ПРОДОЛЖИТЬ", view * 0.5, 30, CREAM)'''
new_pause = '''\tif paused:
\t\tdraw_rect(Rect2(Vector2.ZERO, view), Color(0,0,0,0.72), true)
\t\t_center_text("ПАУЗА", view * 0.5 - Vector2(0, 48), 34, CREAM)
\t\t_center_text("НАСТРОЙКИ", view * 0.5 + Vector2(0, 2), 25, GOLD)
\t\t_center_text("ФОНОВЫЙ ЗВУК: " + ("ВКЛ" if sound_enabled else "ВЫКЛ"), view * 0.5 + Vector2(0, 42), 22, CREAM)
\t\t_center_text("Нажмите ниже, чтобы продолжить", view * 0.5 + Vector2(0, 88), 18, CREAM)'''
if old_pause in s:
    s = s.replace(old_pause, new_pause)

old_input = '''\tif paused:
\t\tpaused = false
\t\treturn'''
new_input = '''\tif paused:
\t\tvar center := view * 0.5
\t\tif absf(point.x - center.x) < 260.0 and absf(point.y - (center.y + 42.0)) < 38.0:
\t\t\tsound_enabled = not sound_enabled
\t\t\tif sound_enabled:
\t\t\t\tif audio_surf.stream and not audio_surf.playing:
\t\t\t\t\taudio_surf.play()
\t\t\telse:
\t\t\t\taudio_surf.stop()
\t\telse:
\t\t\tpaused = false
\t\treturn'''
if old_input in s:
    s = s.replace(old_input, new_input)

# The top sound icon remains a quick toggle; the pause screen now exposes the same setting.
game.write_text(s, encoding="utf-8")
print("Patched landscape orientation, fixed background gestures, fitted labels, and pause/settings sound toggle.")
