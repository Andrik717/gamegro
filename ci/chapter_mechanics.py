from pathlib import Path

def apply_chapter_mechanics(root: Path) -> None:
    game = root / "scripts" / "game.gd"
    source = game.read_text(encoding="utf-8")

    def once(old: str, new: str, label: str) -> None:
        nonlocal source
        count = source.count(old)
        if count != 1:
            raise SystemExit(f"Chapter mechanics patch: {label}: expected one match, got {count}")
        source = source.replace(old, new, 1)

    challenge_data = '''const CHALLENGE_DATA := [
    {},
    {"mode":"sequence","title":"Руны древнего храма","prompt":"Повтори порядок: Луна → Солнце → Земля → Вода","buttons":["Солнце","Вода","Луна","Земля"],"solution":[2,0,3,1]},
    {"mode":"sequence","title":"Свет кристальной пещеры","prompt":"Зажги кристаллы по подсказке: Голубой → Белый → Зелёный → Золотой","buttons":["Голубой","Золотой","Белый","Зелёный"],"solution":[0,2,3,1]},
    {"mode":"code","title":"Замок капитана","prompt":"В журнале: 3 мачты, 1 якорь, 4 колокола. Введи код.","buttons":["1","2","3","4"],"solution":[2,0,3]},
    {"mode":"sequence","title":"Путь морского течения","prompt":"Открой ворота в порядке: Раковина → Коралл → Жемчуг","buttons":["Жемчуг","Раковина","Водоросли","Коралл"],"solution":[1,3,0]},
    {"mode":"dial","title":"Кузница вулкана","prompt":"Настрой клапаны на II, IV и III положение","buttons":["Клапан 1","Клапан 2","Клапан 3"],"solution":[1,3,2]},
    {"mode":"sequence","title":"Созвездие хранителей","prompt":"Соедини звёзды: Вега → Полярная → Сириус → Денеб","buttons":["Сириус","Денеб","Вега","Полярная"],"solution":[2,3,0,1]},
    {"mode":"pairs","title":"Ледяные кристаллы","prompt":"Найди три одинаковые пары кристаллов","buttons":["Лёд","Снег","Сияние","Сияние","Лёд","Снег"],"pairs":[0,1,2,2,0,1]},
    {"mode":"sequence","title":"Печати древнего города","prompt":"Порядок печатей: Вода → Солнце → Луна → Земля","buttons":["Луна","Вода","Земля","Солнце"],"solution":[1,3,0,2]},
    {"mode":"dial","title":"Сердце последнего маяка","prompt":"Выставь зеркала на III, II и IV положение","buttons":["Зеркало 1","Зеркало 2","Зеркало 3"],"solution":[2,1,3]}
]
'''.replace("    ", "\t")
    once("var background: Texture2D", challenge_data + "\nvar background: Texture2D", "challenge definitions")
    once("var map_open := false\n", "var map_open := false\nvar puzzle_active := false\nvar puzzle_step := 0\nvar puzzle_feedback := \"\"\nvar puzzle_dials := [0, 0, 0]\nvar puzzle_first_pick := -1\nvar puzzle_matched := []\n", "challenge state")
    once("\twon = false\n\tqueue_redraw()", "\twon = false\n\tpuzzle_active = false\n\tpuzzle_step = 0\n\tpuzzle_feedback = \"\"\n\tpuzzle_dials = [0, 0, 0]\n\tpuzzle_first_pick = -1\n\tpuzzle_matched.clear()\n\tqueue_redraw()", "reset challenge state")
    once("\tif map_open:\n\t\t_draw_map(view)\n\tif paused:", "\tif puzzle_active:\n\t\t_draw_challenge(view)\n\tif map_open:\n\t\t_draw_map(view)\n\tif paused:", "draw challenge overlay")
    once("\tif paused:\n\t\t_handle_settings_tap(point, view)\n\t\treturn\n\tif won:", "\tif paused:\n\t\t_handle_settings_tap(point, view)\n\t\treturn\n\tif puzzle_active:\n\t\t_handle_challenge_tap(point, view)\n\t\treturn\n\tif won:", "route challenge input")
    once("\t\t\tif found.size() == chapter_items.size():\n\t\t\t\twon = true", "\t\t\tif found.size() == chapter_items.size():\n\t\t\t\tif current_level == 0:\n\t\t\t\t\twon = true\n\t\t\t\telse:\n\t\t\t\t\tpuzzle_active = true\n\t\t\t\t\tpuzzle_step = 0\n\t\t\t\t\tpuzzle_feedback = \"Артефакт почти у тебя. Реши задачу главы!\"\n\t\t\t\t\tpuzzle_dials = [0, 0, 0]\n\t\t\t\t\tpuzzle_first_pick = -1\n\t\t\t\t\tpuzzle_matched.clear()", "require chapter challenge after searching")
    # A completed campaign returns to the first island while keeping every chapter unlocked.
    once("\telse:\n\t\tcurrent_level = LEVEL_DATA.size()-1\n\t\tunlocked_level_count = LEVEL_DATA.size()\n\t_load_chapter(current_level)", "\telse:\n\t\tcurrent_level = 0\n\t\tunlocked_level_count = LEVEL_DATA.size()\n\t_load_chapter(current_level)", "campaign replay")
    once('_center_text("СЛЕДУЮЩАЯ ЛОКАЦИЯ", r.replay.get_center()+Vector2(0,9), 22, CREAM)', 'var next_label := "ПОВТОРИТЬ ПУТЕШЕСТВИЕ" if current_level == LEVEL_DATA.size()-1 else "СЛЕДУЮЩАЯ ЛОКАЦИЯ"\n\t_center_text(next_label, r.replay.get_center()+Vector2(0,9), 20, CREAM)', "final chapter button")

    source += '''

func _challenge_panel_rect(view: Vector2) -> Rect2:
    var center := view * 0.5
    var w := minf(900.0, view.x - 28.0)
    var h := minf(520.0, view.y - 28.0)
    return Rect2(center.x-w*0.5, center.y-h*0.5, w, h)

func _challenge_button_rect(index: int, view: Vector2) -> Rect2:
    var panel := _challenge_panel_rect(view)
    var data: Dictionary = CHALLENGE_DATA[current_level]
    var mode := str(data.mode)
    if mode == "pairs":
        var gap := 10.0
        var w := (panel.size.x - 64.0 - gap*2.0) / 3.0
        var h := minf(88.0, (panel.size.y - 250.0) * 0.5)
        return Rect2(panel.position.x+22.0+float(index%3)*(w+gap), panel.position.y+205.0+float(int(index/3))*(h+gap), w, h)
    var count: int = data.buttons.size()
    var gap := 10.0
    var w := (panel.size.x - 64.0 - gap*float(count-1)) / float(count)
    var h := minf(104.0, panel.size.y*0.24)
    return Rect2(panel.position.x+32.0+float(index)*(w+gap), panel.position.y+panel.size.y*0.48-h*0.5, w, h)

func _challenge_confirm_rect(view: Vector2) -> Rect2:
    var panel := _challenge_panel_rect(view)
    return Rect2(panel.get_center().x-130.0, panel.position.y+panel.size.y-100.0, 260.0, 54.0)

func _draw_challenge(view: Vector2) -> void:
    var data: Dictionary = CHALLENGE_DATA[current_level]
    var mode := str(data.mode)
    var panel := _challenge_panel_rect(view)
    draw_rect(Rect2(Vector2.ZERO, view), Color(0.01,0.04,0.08,0.82), true)
    draw_style_box(_rounded_style(Color("#102d4d"), GOLD, 28, 18), panel)
    _center_text(str(data.title), Vector2(view.x*0.5, panel.position.y+54.0), 27, GOLD)
    _center_text(str(data.prompt), Vector2(view.x*0.5, panel.position.y+105.0), 17, CREAM)
    var progress_text := ""
    if mode == "pairs":
        progress_text = "Найдено пар: %d / 3" % puzzle_matched.size()
    elif mode == "dial":
        progress_text = "Положение каждого механизма меняется нажатием"
    else:
        progress_text = "Шаг: %d / %d" % [puzzle_step, data.solution.size()]
    _center_text(progress_text, Vector2(view.x*0.5, panel.position.y+155.0), 17, Color("#a9edc9"))
    if mode == "pairs":
        for i in range(6):
            var r := _challenge_button_rect(i, view)
            var pair_id: int = data.pairs[i]
            var revealed := puzzle_first_pick == i or puzzle_matched.has(pair_id)
            var label := str(data.buttons[i]) if revealed else "?"
            var fill := Color("#246b70") if revealed else Color("#1c4d68")
            var edge := Color("#78c8a4") if revealed else Color("#bd8c48")
            draw_style_box(_rounded_style(fill, edge, 16, 8), r)
            _center_text(label, r.get_center()+Vector2(0,8), 18, CREAM)
    elif mode == "dial":
        for i in range(3):
            var r := _challenge_button_rect(i, view)
            draw_style_box(_rounded_style(Color("#1c4d68"), Color("#bd8c48"), 18, 8), r)
            _center_text(str(data.buttons[i]), Vector2(r.get_center().x, r.position.y+r.size.y*0.38), 17, CREAM)
            _center_text("ПОЛОЖЕНИЕ %d" % [int(puzzle_dials[i])+1], Vector2(r.get_center().x, r.position.y+r.size.y*0.70), 16, GOLD)
        var confirm := _challenge_confirm_rect(view)
        draw_style_box(_rounded_style(Color("#9a692e"), GOLD, 18, 8), confirm)
        _center_text("ПРОВЕРИТЬ", confirm.get_center()+Vector2(0,7), 19, CREAM)
    else:
        for i in range(data.buttons.size()):
            var r := _challenge_button_rect(i, view)
            var active: bool = mode == "sequence" and puzzle_step < data.solution.size() and i == int(data.solution[puzzle_step])
            draw_style_box(_rounded_style(Color("#246b70") if active else Color("#1c4d68"), GOLD if active else Color("#bd8c48"), 16, 8), r)
            _center_text(str(data.buttons[i]), r.get_center()+Vector2(0,8), 17, CREAM)
    if not puzzle_feedback.is_empty():
        _center_text(puzzle_feedback, Vector2(view.x*0.5, panel.position.y+panel.size.y-28.0), 15, Color("#ffe1a0"))

func _handle_challenge_tap(point: Vector2, view: Vector2) -> void:
    if point.y < 76.0 and point.x < 86.0:
        paused = true
        queue_redraw()
        return
    var data: Dictionary = CHALLENGE_DATA[current_level]
    var mode := str(data.mode)
    if mode == "pairs":
        for i in range(6):
            if not _challenge_button_rect(i, view).has_point(point):
                continue
            var pair_id: int = data.pairs[i]
            if puzzle_matched.has(pair_id) or puzzle_first_pick == i:
                return
            if puzzle_first_pick < 0:
                puzzle_first_pick = i
                puzzle_feedback = "Теперь найди такой же кристалл"
            else:
                var first_pair: int = data.pairs[puzzle_first_pick]
                puzzle_first_pick = -1
                if first_pair == pair_id:
                    puzzle_matched.append(pair_id)
                    puzzle_feedback = "Пара найдена!"
                    if puzzle_matched.size() == 3:
                        _finish_challenge()
                else:
                    puzzle_feedback = "Не совпало. Попробуй другую пару."
            queue_redraw()
            return
        return
    if mode == "dial":
        for i in range(3):
            if _challenge_button_rect(i, view).has_point(point):
                puzzle_dials[i] = (int(puzzle_dials[i])+1)%4
                puzzle_feedback = "Настрой остальные механизмы"
                queue_redraw()
                return
        if _challenge_confirm_rect(view).has_point(point):
            var solution: Array = data.solution
            if puzzle_dials == solution:
                _finish_challenge()
            else:
                puzzle_feedback = "Механизм не совпал. Измени положения и проверь снова."
            queue_redraw()
        return
    for i in range(data.buttons.size()):
        if not _challenge_button_rect(i, view).has_point(point):
            continue
        var solution: Array = data.solution
        if puzzle_step < solution.size() and i == int(solution[puzzle_step]):
            puzzle_step += 1
            puzzle_feedback = "Верно! Продолжай."
            if puzzle_step >= solution.size():
                _finish_challenge()
        else:
            puzzle_step = 0
            puzzle_feedback = "Порядок сбился. Начни последовательность заново."
        queue_redraw()
        return

func _finish_challenge() -> void:
    puzzle_active = false
    won = true
    puzzle_feedback = "Артефакт восстановлен!"
    unlocked_level_count = mini(LEVEL_DATA.size(), maxi(unlocked_level_count, current_level+2))
    _save_progress()
    queue_redraw()
'''.replace("    ", "\t")
    game.write_text(source, encoding="utf-8")
