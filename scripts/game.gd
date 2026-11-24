extends Node2D

const DESIGN := Vector2(1672, 941)
const LEVELS := [
    {
        "title": "Затерянный остров",
        "background": "res://assets/backgrounds/level1_tropical_bay.png",
        "targets": [
            {"id":"star", "name":"Звезда", "rect":Rect2(180,710,180,170)},
            {"id":"shell", "name":"Ракушка", "rect":Rect2(610,690,200,170)},
            {"id":"key", "name":"Ключ", "rect":Rect2(900,690,180,150)},
            {"id":"pineapple", "name":"Ананас", "rect":Rect2(1120,650,190,220)},
            {"id":"crab", "name":"Краб", "rect":Rect2(1310,660,250,220)}
        ]
    },
    {
        "title": "Древние джунгли",
        "background": "res://assets/backgrounds/bg_02.png",
        "targets": [
            {"id":"резной_тотем", "name":"Резной тотем", "rect":Rect2(160,245,140,110)},
            {"id":"дневник_исследователя", "name":"Дневник исследователя", "rect":Rect2(1080,605,140,110)},
            {"id":"каменный_ключ", "name":"Каменный ключ", "rect":Rect2(1290,205,140,110)},
            {"id":"золотой_идол", "name":"Золотой идол", "rect":Rect2(730,465,140,110)},
            {"id":"сломанный_компас", "name":"Сломанный компас", "rect":Rect2(450,645,140,110)}
        ]
    },
    {
        "title": "Пещера водопада",
        "background": "res://assets/levels/waterfall_cave.svg",
        "targets": [
            {"id":"светящийся_кристалл", "name":"Светящийся кристалл", "rect":Rect2(180,185,140,110)},
            {"id":"старинный_фонарь", "name":"Старинный фонарь", "rect":Rect2(1120,195,140,110)},
            {"id":"кристальная_чаша", "name":"Кристальная чаша", "rect":Rect2(690,595,140,110)},
            {"id":"серебряный_ключ", "name":"Серебряный ключ", "rect":Rect2(1270,545,140,110)},
            {"id":"жемчужина", "name":"Жемчужина", "rect":Rect2(440,415,140,110)}
        ]
    },
    {
        "title": "Пиратская бухта",
        "background": "res://assets/backgrounds/bg_04.png",
        "targets": [
            {"id":"капитанский_журнал", "name":"Капитанский журнал", "rect":Rect2(180,475,140,110)},
            {"id":"подзорная_труба", "name":"Подзорная труба", "rect":Rect2(1210,195,140,110)},
            {"id":"пиратская_печать", "name":"Пиратская печать", "rect":Rect2(680,325,140,110)},
            {"id":"судовой_колокол", "name":"Судовой колокол", "rect":Rect2(1010,635,140,110)},
            {"id":"сундук_с_картой", "name":"Сундук с картой", "rect":Rect2(350,675,140,110)}
        ]
    },
    {
        "title": "Подводная лагуна",
        "background": "res://assets/backgrounds/bg_05.png",
        "targets": [
            {"id":"трезубец", "name":"Трезубец", "rect":Rect2(190,245,140,110)},
            {"id":"морская_корона", "name":"Морская корона", "rect":Rect2(1190,225,140,110)},
            {"id":"древняя_амфора", "name":"Древняя амфора", "rect":Rect2(690,445,140,110)},
            {"id":"золотая_раковина", "name":"Золотая раковина", "rect":Rect2(350,645,140,110)},
            {"id":"сердце_океана", "name":"Сердце океана", "rect":Rect2(1250,635,140,110)}
        ]
    },
    {
        "title": "Остров огня",
        "background": "res://assets/levels/volcano_forge.svg",
        "targets": [
            {"id":"молот_кузнеца", "name":"Молот кузнеца", "rect":Rect2(180,565,140,110)},
            {"id":"лавовый_кристалл", "name":"Лавовый кристалл", "rect":Rect2(700,185,140,110)},
            {"id":"огненная_руна", "name":"Огненная руна", "rect":Rect2(1220,245,140,110)},
            {"id":"клещи", "name":"Клещи", "rect":Rect2(1040,635,140,110)},
            {"id":"пылающий_медальон", "name":"Пылающий медальон", "rect":Rect2(440,395,140,110)}
        ]
    },
    {
        "title": "Небесная обсерватория",
        "background": "res://assets/levels/sky_observatory.svg",
        "targets": [
            {"id":"астролябия", "name":"Астролябия", "rect":Rect2(210,585,140,110)},
            {"id":"звёздная_карта", "name":"Звёздная карта", "rect":Rect2(1120,605,140,110)},
            {"id":"лунный_камень", "name":"Лунный камень", "rect":Rect2(680,215,140,110)},
            {"id":"телескоп", "name":"Телескоп", "rect":Rect2(1260,305,140,110)},
            {"id":"звёздный_компас", "name":"Звёздный компас", "rect":Rect2(450,375,140,110)}
        ]
    },
    {
        "title": "Ледяное королевство",
        "background": "res://assets/levels/ice_kingdom.svg",
        "targets": [
            {"id":"ледяная_корона", "name":"Ледяная корона", "rect":Rect2(180,245,140,110)},
            {"id":"замёрзшее_письмо", "name":"Замёрзшее письмо", "rect":Rect2(1200,225,140,110)},
            {"id":"синий_кристалл", "name":"Синий кристалл", "rect":Rect2(690,485,140,110)},
            {"id":"старинный_ключ", "name":"Старинный ключ", "rect":Rect2(340,645,140,110)},
            {"id":"кристалл_памяти", "name":"Кристалл памяти", "rect":Rect2(1260,635,140,110)}
        ]
    },
    {
        "title": "Древний город",
        "background": "res://assets/levels/lost_city.svg",
        "targets": [
            {"id":"печать_хранителей", "name":"Печать хранителей", "rect":Rect2(180,565,140,110)},
            {"id":"книга_летописей", "name":"Книга летописей", "rect":Rect2(1180,225,140,110)},
            {"id":"золотая_маска", "name":"Золотая маска", "rect":Rect2(690,365,140,110)},
            {"id":"солнечный_диск", "name":"Солнечный диск", "rect":Rect2(350,235,140,110)},
            {"id":"сердце_архипелага", "name":"Сердце архипелага", "rect":Rect2(1260,645,140,110)}
        ]
    },
    {
        "title": "Последний маяк",
        "background": "res://assets/levels/final_lighthouse.svg",
        "targets": [
            {"id":"линза_маяка", "name":"Линза маяка", "rect":Rect2(690,205,140,110)},
            {"id":"серебряный_рычаг", "name":"Серебряный рычаг", "rect":Rect2(180,615,140,110)},
            {"id":"последний_фрагмент_карты", "name":"Последний фрагмент карты", "rect":Rect2(1180,595,140,110)},
            {"id":"ключ_хранителя", "name":"Ключ хранителя", "rect":Rect2(360,365,140,110)},
            {"id":"свет_архипелага", "name":"Свет архипелага", "rect":Rect2(1250,215,140,110)}
        ]
    }
]
const CREAM := Color("#fff2d0")
const PANEL := Color(0.055, 0.12, 0.16, 0.92)

var level_index := 0
var background: Texture2D
var targets: Array[Dictionary] = []
var found: Array[String] = []
var elapsed := 0.0
var hint_target := -1
var hint_left := 0.0
var paused := false
var won := false
var hint_rect := Rect2(1390, 855, 220, 62)
var pause_rect := Rect2(1530, 0, 140, 120)
var action_rect := Rect2(665, 545, 340, 78)

func _ready() -> void:
    _load_level(0)
    get_viewport().size_changed.connect(queue_redraw)

func _load_level(index: int) -> void:
    level_index = clampi(index, 0, LEVELS.size() - 1)
    background = load(LEVELS[level_index].background)
    targets = LEVELS[level_index].targets
    found.clear()
    elapsed = 0.0
    hint_target = -1
    hint_left = 0.0
    paused = false
    won = false
    queue_redraw()

func _process(delta: float) -> void:
    if not paused and not won:
        elapsed += delta
    if hint_left > 0.0:
        hint_left = maxf(0.0, hint_left - delta)
        if hint_left == 0.0:
            hint_target = -1
    queue_redraw()

func _draw() -> void:
    if background == null:
        return
    var view := get_viewport_rect().size
    var scale_factor := minf(view.x / DESIGN.x, view.y / DESIGN.y)
    var origin := (view - DESIGN * scale_factor) * 0.5
    draw_set_transform(origin, 0.0, Vector2.ONE * scale_factor)
    draw_texture_rect(background, Rect2(Vector2.ZERO, DESIGN), false)
    _draw_hud()
    if hint_target >= 0 and hint_left > 0.0:
        var target_rect: Rect2 = targets[hint_target].rect
        var pulse := 0.5 + 0.5 * sin(Time.get_ticks_msec() / 120.0)
        draw_rect(target_rect.grow(10), Color(1.0, 0.82, 0.25, 0.25 + pulse * 0.3), false, 7.0)
    if paused and not won:
        draw_rect(Rect2(Vector2.ZERO, DESIGN), Color(0.01, 0.03, 0.05, 0.68), true)
        draw_string(ThemeDB.fallback_font, Vector2(590, 480), "ПАУЗА — НАЖМИТЕ, ЧТОБЫ ПРОДОЛЖИТЬ", HORIZONTAL_ALIGNMENT_LEFT, -1, 30, CREAM)
    if won:
        _draw_win()
    draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)

func _draw_hud() -> void:
    draw_string(ThemeDB.fallback_font, Vector2(48, 55), "УРОВЕНЬ %d: %s" % [level_index + 1, LEVELS[level_index].title], HORIZONTAL_ALIGNMENT_LEFT, -1, 28, CREAM)
    var panel := Rect2(28, 842, 1616, 78)
    draw_rect(panel, PANEL, true)
    draw_rect(panel, Color("#edbd60"), false, 3.0)
    var font := ThemeDB.fallback_font
    draw_string(font, Vector2(58, 890), "НАЙДЕНО: %d / %d" % [found.size(), targets.size()], HORIZONTAL_ALIGNMENT_LEFT, -1, 25, CREAM)
    draw_string(font, Vector2(330, 890), "ВРЕМЯ: " + _time_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, 25, CREAM)
    var x := 565.0
    var slot := 155.0
    for item in targets:
        var done: bool = found.has(item.id)
        var color := Color("#8ee0a1") if done else CREAM
        var mark := "✓ " if done else "○ "
        draw_string(font, Vector2(x, 890), mark + item.name, HORIZONTAL_ALIGNMENT_LEFT, -1, 17, color)
        x += slot
    draw_rect(hint_rect, Color("#bd762d"), true)
    draw_rect(hint_rect, Color("#ffe1a0"), false, 3.0)
    draw_string(font, Vector2(1432, 896), "ПОДСКАЗКА", HORIZONTAL_ALIGNMENT_LEFT, -1, 23, CREAM)
    draw_circle(Vector2(1600, 58), 47, Color("#8d5228"), true)
    draw_circle(Vector2(1600, 58), 47, Color("#ffe1a0"), false, 4.0)
    draw_rect(Rect2(1584, 34, 10, 48), CREAM, true)
    draw_rect(Rect2(1606, 34, 10, 48), CREAM, true)

func _draw_win() -> void:
    draw_rect(Rect2(Vector2.ZERO, DESIGN), Color(0.01, 0.03, 0.05, 0.72), true)
    var card := Rect2(470, 300, 732, 370)
    draw_rect(card, Color("#193b45"), true)
    draw_rect(card, Color("#f7c96b"), false, 5.0)
    var font := ThemeDB.fallback_font
    var heading := "ЛОКАЦИЯ ПРОЙДЕНА!"
    draw_string(font, Vector2(585, 405), heading, HORIZONTAL_ALIGNMENT_LEFT, -1, 34, CREAM)
    draw_string(font, Vector2(650, 465), "Ты нашёл все предметы!", HORIZONTAL_ALIGNMENT_LEFT, -1, 30, Color("#bcebd0"))
    draw_string(font, Vector2(760, 510), "Время: " + _time_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, 26, CREAM)
    draw_rect(action_rect, Color("#bd762d"), true)
    draw_rect(action_rect, Color("#ffe1a0"), false, 3.0)
    var action_text := "СЛЕДУЮЩИЙ УРОВЕНЬ" if level_index + 1 < LEVELS.size() else "ПОВТОРИТЬ ИГРУ"
    draw_string(font, Vector2(700, 595), action_text, HORIZONTAL_ALIGNMENT_LEFT, -1, 27, CREAM)

func _time_text() -> String:
    var total := int(elapsed)
    return "%02d:%02d" % [total / 60, total % 60]

func _input(event: InputEvent) -> void:
    var point := Vector2.ZERO
    if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
        point = event.position
    elif event is InputEventScreenTouch and event.pressed:
        point = event.position
    else:
        return
    var view := get_viewport_rect().size
    var scale_factor := minf(view.x / DESIGN.x, view.y / DESIGN.y)
    var origin := (view - DESIGN * scale_factor) * 0.5
    var click_pos := (point - origin) / scale_factor
    if won:
        if action_rect.has_point(click_pos):
            if level_index + 1 < LEVELS.size():
                _load_level(level_index + 1)
            else:
                _load_level(0)
        return
    if pause_rect.has_point(click_pos):
        paused = not paused
        return
    if paused:
        paused = false
        return
    if hint_rect.has_point(click_pos):
        _hint()
        return
    for i in range(targets.size()):
        var item: Dictionary = targets[i]
        if not found.has(item.id) and item.rect.has_point(click_pos):
            found.append(item.id)
            hint_target = -1
            hint_left = 0.0
            if found.size() == targets.size():
                won = true
            get_viewport().set_input_as_handled()
            queue_redraw()
            return

func _hint() -> void:
    for i in range(targets.size()):
        if not found.has(targets[i].id):
            hint_target = i
            hint_left = 3.0
            return
