from pathlib import Path
import json

def icon(slug, color, dark, kind):
    forms={
    "gem":'<path d="M128 25 188 84 160 216 96 216 68 84Z"/><path d="M128 25V216M68 84l60 35 60-35M96 216l32-97 32 97" fill="none" stroke="#efffff" stroke-width="9"/>',
    "key":'<circle cx="86" cy="91" r="38" fill="none" stroke="#fff0bd" stroke-width="17"/><path d="m120 118 83 83-20 20-21-21-17 16-19-20 19-19-41-41Z"/>',
    "book":'<path d="M48 49q44-21 80 9 36-30 80-9v155q-44-20-80 9-36-29-80-9Z"/><path d="M128 58v155M68 84h44m-44 28h44m32-28h44m-44 28h44" fill="none" stroke="#f5dfb2" stroke-width="8"/>',
    "crown":'<path d="m48 88 34 40 29-61 34 61 39-63 23 23-18 95H65Z"/><path d="M66 155h124" stroke="#fff0ae" stroke-width="9"/>',
    "heart":'<path d="M128 204Q38 140 59 84q21-49 69-2 48-47 69 2 21 56-69 120Z"/><path d="M128 82v106m-54-96 54 36 54-36" fill="none" stroke="#d9fff0" stroke-width="9"/>',
    "shell":'<path d="M45 173Q48 69 128 50q80 19 83 123-83 48-166 0Z"/><path d="M128 54v130M90 70l15 120m61-120-15 120M61 105l30 92m104-92-30 92" fill="none" stroke="#fff0b2" stroke-width="9"/>',
    "mask":'<path d="M55 60Q128 25 201 60l-16 115q-57 47-114 0Z"/><path d="M76 98q22-22 43 4l-7 20H83Zm84 4q21-26 40-4l-7 24h-29Z" fill="#49372f"/>',
    "bell":'<path d="M85 93q0-41 43-41t43 41l16 80q-59 32-118 0Z"/><path d="M59 174q69 30 138 0M112 50q16-28 32 0" fill="none" stroke="#fff0ba" stroke-width="12"/>',
    "hammer":'<path d="M60 75h134v55H60Z"/><path d="M117 122h22l12 99h-46Z"/>',
    "telescope":'<path d="m63 76 111 36-17 51-111-36Z"/><path d="m171 112 33 11-19 56-32-14Z"/><path d="m100 142-27 73m68-59 23 59m-48-69 1 69" fill="none" stroke="#cba36a" stroke-width="12"/>',
    "map":'<path d="m47 58 52-16 51 16 53-16v155l-53 16-51-16-52 16Z"/><path d="M99 42v155m51-139v155" fill="none" stroke="#f5dfb2" stroke-width="8"/><path d="m70 160 40-48 32 27 36-51" fill="none" stroke="#8c633d" stroke-width="8"/>',
    "trident":'<path d="M128 54v164M128 82Q87 82 77 43M128 82q41 0 51-39M77 43 58 22m19 21 20-21m82 21-19-21m19 21 20-21" fill="none" stroke="#fff0b7" stroke-width="15"/>',
    "lantern":'<path d="M93 76h70l12 107q-47 37-94 0Z"/><path d="M106 93h44l7 80H99Z" fill="#fff0b0"/><path d="M88 72h86l-12-19h-62Z M128 31v22" fill="none" stroke="#f6d58f" stroke-width="12"/>',
    "amphora":'<path d="M100 38h56l-6 35q43 29 27 101-49 48-98 0Q63 102 106 73Z"/><path d="M100 38h56M102 77q26 21 52 0m-66 78q40 22 80 0" fill="none" stroke="#f5c995" stroke-width="10"/>',
    "disk":'<circle cx="128" cy="128" r="58"/><g stroke="#fff0b7" stroke-width="14"><path d="M128 25v27m0 152v27M25 128h27m152 0h27M55 55l20 20m106 106 20 20M201 55l-20 20M75 181l-20 20"/></g>',
    "lever":'<path d="M65 190 180 65" stroke="#edf8f7" stroke-width="22"/><circle cx="183" cy="61" r="29"/><circle cx="65" cy="190" r="23" fill="#f1d28d"/>',
    "idol":'<path d="m128 28 48 49-12 116q-36 31-72 0L80 77Z"/><path d="m98 96 18 15-18 15m60-30-18 15 18 15m-54 32q24 22 48 0" fill="none" stroke="#71452d" stroke-width="10"/>',
    "rune":'<path d="m128 30 57 50-15 94-42 46-42-46-15-94Z" fill="none" stroke="#ffdf91" stroke-width="16"/><path d="m128 65 23 50-23 70-23-70Z"/>'
    }
    body=forms[kind]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256"><defs><linearGradient id="g" x1="0" y1="0" x2=".9" y2="1"><stop stop-color="#fff" stop-opacity=".55"/><stop offset=".3" stop-color="{color}"/><stop offset="1" stop-color="{dark}"/></linearGradient><filter id="s" x="-30%" y="-30%" width="160%" height="180%"><feGaussianBlur stdDeviation="7"/></filter></defs><ellipse cx="130" cy="224" rx="67" ry="11" fill="#071b29" opacity=".25" filter="url(#s)"/><g fill="url(#g)" stroke="{dark}" stroke-width="8" stroke-linejoin="round" stroke-linecap="round">{body}</g><path d="M82 54q28-28 65-11" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round" opacity=".6"/></svg>'''

def enhance_game(root):
    base=Path(__file__).resolve().parent.parent
    levels=json.loads((base/"game_data/story.json").read_text(encoding="utf-8"))["levels"]
    src=root/"scripts/game.gd"
    s=src.read_text(encoding="utf-8")
    palette=[("#b86b3d","#633d32"),("#67d9e8","#276b91"),("#d8a34e","#77502e"),("#3dbfc4","#176f8c"),("#f16d42","#872d2b"),("#d8b36b","#765332"),("#9fd6ed","#4c829f"),("#d4b36c","#785634"),("#bde5ee","#5e91a3")]
    kinds=["idol","book","key","idol","disk","gem","lantern","disk","key","gem","book","telescope","disk","bell","map","trident","crown","amphora","shell","heart","hammer","gem","rune","lever","disk","disk","map","gem","telescope","disk","crown","book","gem","key","gem","disk","book","mask","disk","heart","gem","lever","map","key","disk"]
    if len(levels)!=10 or sum(len(x.get("items",[])) for x in levels[1:])!=45: raise SystemExit("Expected 45 chapter targets across levels 2-10")
    art=root/"assets/items"; art.mkdir(parents=True,exist_ok=True)
    blocks=[]; n=0
    for li,level in enumerate(levels[1:]):
        color,dark=palette[li]; rows=[]
        for item in level["items"]:
            slug=item["slug"]; x,y=item["position"]
            (art/f"{slug}.svg").write_text(icon(slug,color,dark,kinds[n]),encoding="utf-8")
            rows.append(f'{{"id":{item["id"]},"slug":"{slug}","name":"{item["name"]}","pos":Vector2({x},{y})}}'); n+=1
        blocks.append("\t[\n\t\t"+",\n\t\t".join(rows)+"\n\t]")
    if "const CHAPTER_ITEMS :=" not in s:
        if s.count("const CREAM :=")!=1: raise SystemExit("Missing color constant anchor")
        s=s.replace("const CREAM :=","const CHAPTER_ITEMS := [\n"+",\n".join(blocks)+"\n]\nconst CREAM :=",1)
    def once(a,b,label):
        nonlocal s
        if s.count(a)!=1: raise SystemExit(f"{label}: expected one match, got {s.count(a)}")
        s=s.replace(a,b,1)
    once("var current_level := 0\nvar unlocked_level_count := 1\nvar map_open := false","var current_level := 0\nvar unlocked_level_count := 1\nvar map_open := false\nvar chapter_items: Array = []\nvar chapter_textures: Array[Texture2D] = []","chapter vars")
    once("\t_make_audio()\n\t_reset_round()","\t_make_audio()\n\t_load_progress()\n\t_load_chapter(current_level)\n\t_reset_round()","restore progress")
    once("\tfor i in range(ITEM_COUNT):\n\t\tdisplay_order.append(i)","\tfor i in range(chapter_items.size()):\n\t\tdisplay_order.append(i)","round length")
    once("\tfor i in range(ITEM_COUNT):\n\t\tif found.has(i):\n\t\t\tcontinue\n\t\tvar p: Vector2 = _item_position(ITEM_DATA[i])\n\t\tvar texture: Texture2D = item_textures[i]","\tfor i in range(chapter_items.size()):\n\t\tif found.has(i):\n\t\t\tcontinue\n\t\tvar p: Vector2 = chapter_items[i].pos\n\t\tvar texture: Texture2D = chapter_textures[i]","draw chapter objects")
    once("\tvar slots := mini(5, ITEM_COUNT - found.size())","\tvar slots := mini(5, chapter_items.size() - found.size())","HUD targets")
    once("\t\tdraw_texture_rect(item_textures[id], Rect2(x+slot_w*0.5-27, bar.position.y+42, 54, 52), false)\n\t\tvar label := _fit_label(_short_name(ITEM_DATA[id].name), slot_w-14.0, 14)","\t\tdraw_texture_rect(chapter_textures[id], Rect2(x+slot_w*0.5-27, bar.position.y+42, 54, 52), false)\n\t\tvar label := _fit_label(_short_name(chapter_items[id].name), slot_w-14.0, 14)","HUD artwork")
    once("\tfor item in ITEM_DATA:\n\t\tvar id: int = item.id","\tfor item in chapter_items:\n\t\tvar id: int = item.id","hit tests")
    once("\t\tvar item_pos := _item_position(item)\n\t\tif Rect2(item_pos-Vector2.ONE*radius,Vector2.ONE*radius*2).has_point(world_pos):","\t\tvar item_pos: Vector2 = item.pos\n\t\tif Rect2(item_pos-Vector2.ONE*radius,Vector2.ONE*radius*2).has_point(world_pos):","manual hitboxes")
    once("\t\t\tif found.size() == ITEM_COUNT:","\t\t\tif found.size() == chapter_items.size():","win condition")
    once("\tvar original: Vector2 = item.pos\n\tif current_level == 0:\n\t\treturn original\n\tvar center := WORLD_SIZE * 0.5\n\tvar rotated := (original-center).rotated(float(current_level)*0.39)\n\tvar drift := Vector2(sin(float(item.id)*1.7+current_level)*18.0, cos(float(item.id)*1.3+current_level)*16.0)\n\tvar point := center + rotated + drift\n\treturn Vector2(clampf(point.x, 64.0, WORLD_SIZE.x-64.0), clampf(point.y, 64.0, WORLD_SIZE.y-64.0)","\treturn item.pos","no random transforms")
    once("\t\t\tcurrent_level = i\n\t\t\tmap_open = false\n\t\t\t_load_current_level()\n\t\t\t_reset_round()","\t\t\tmap_open = false\n\t\t\t_load_chapter(i)\n\t\t\t_reset_round()","map selection")
    old='''func _load_current_level() -> void:\n\tbackground = load(LEVEL_DATA[current_level].background)\n\tif background == null:\n\t\tpush_error("Missing level background: " + LEVEL_DATA[current_level].background)'''
    new='''func _load_current_level() -> void:\n\t_load_chapter(current_level)\n\nfunc _load_chapter(index: int) -> void:\n\tcurrent_level = clampi(index,0,LEVEL_DATA.size()-1)\n\tbackground = load(LEVEL_DATA[current_level].background)\n\tchapter_items = ITEM_DATA if current_level == 0 else CHAPTER_ITEMS[current_level-1]\n\tchapter_textures.clear()\n\tif current_level == 0:\n\t\tfor texture in item_textures: chapter_textures.append(texture)\n\telse:\n\t\tfor item in chapter_items:\n\t\t\tvar path := "res://assets/items/%s.svg" % item.slug\n\t\t\tvar texture := load(path) as Texture2D\n\t\t\tif texture == null: push_error("Missing item artwork: " + path)\n\t\t\telse: chapter_textures.append(texture)\n\tif background == null: push_error("Missing chapter background: " + LEVEL_DATA[current_level].background)\n\t_save_progress()\n\nfunc _load_progress() -> void:\n\tvar cfg := ConfigFile.new()\n\tif cfg.load("user://magicworld_progress.cfg") == OK:\n\t\tcurrent_level = clampi(int(cfg.get_value("progress","current_level",0)),0,LEVEL_DATA.size()-1)\n\t\tunlocked_level_count = clampi(int(cfg.get_value("progress","unlocked_level_count",1)),1,LEVEL_DATA.size())\n\nfunc _save_progress() -> void:\n\tvar cfg := ConfigFile.new()\n\tcfg.set_value("progress","current_level",current_level)\n\tcfg.set_value("progress","unlocked_level_count",unlocked_level_count)\n\tcfg.save("user://magicworld_progress.cfg")'''
    once(old,new,"chapter loader")
    old='''func _advance_level() -> void:\n\tif current_level < LEVEL_DATA.size()-1:\n\t\tcurrent_level += 1\n\t\tunlocked_level_count = maxi(unlocked_level_count, current_level+1)\n\telse:\n\t\tcurrent_level = 0\n\t\tunlocked_level_count = LEVEL_DATA.size()\n\t_load_current_level()\n\t_reset_round()'''
    new='''func _advance_level() -> void:\n\tif current_level < LEVEL_DATA.size()-1:\n\t\tcurrent_level += 1\n\t\tunlocked_level_count = maxi(unlocked_level_count,current_level+1)\n\telse:\n\t\tcurrent_level = LEVEL_DATA.size()-1\n\t\tunlocked_level_count = LEVEL_DATA.size()\n\t_load_chapter(current_level)\n\t_save_progress()\n\t_reset_round()'''
    once(old,new,"progression")
    s=s.replace('"%02d / 30" % found.size()','"%02d / %02d" % [found.size(),chapter_items.size()]')
    s=s.replace('"Найден первый фрагмент карты"','"Артефакт: " + LEVEL_DATA[current_level].artifact')
    s=s.replace('"Все 30 сокровищ найдены"','"Все предметы этой локации найдены"')
    src.write_text(s,encoding="utf-8")
