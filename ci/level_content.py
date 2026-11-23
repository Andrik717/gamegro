from pathlib import Path
import json, math, random
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

PALETTES=[
("#153d38","#4b8760","#b8c98b","#f3c477"),("#122c42","#267a91","#4eb8bd","#e9c78b"),
("#182e43","#9a6041","#d39a59","#f4d18b"),("#063b50","#087d91","#49c4bd","#f1d28a"),
("#431f24","#9c3e2d","#e1783f","#ffc16b"),("#1b3555","#547ba1","#a8c7d8","#f7d99a"),
("#243b58","#729bb6","#c7e3ed","#f6f3e8"),("#34324d","#8d6b58","#d0a47b","#e8c28a"),
("#172e45","#477d8d","#9bc0b4","#f0d18d")]
KINDS=["idol","book","key","idol","disk","gem","lantern","disk","key","gem","book","telescope","disk","bell","map","trident","crown","amphora","shell","heart","hammer","gem","rune","lever","disk","disk","map","gem","telescope","disk","crown","book","gem","key","gem","disk","book","mask","disk","heart","gem","lever","map","key","disk"]

def rgb(h): return tuple(bytes.fromhex(h.lstrip("#")))
def blend(a,b,t): return tuple(round(x+(y-x)*t) for x,y in zip(rgb(a),rgb(b)))
def gradient(size,a,b):
    im=Image.new("RGB",size); px=im.load()
    for y in range(size[1]):
        c=blend(a,b,y/(size[1]-1))
        for x in range(size[0]): px[x,y]=c
    return im

def make_background_from_source(source,path):
    with Image.open(source) as original:
        im=original.convert("RGB")
        w,h=im.size
        scale=max(1920/w,1080/h)
        im=im.resize((round(w*scale),round(h*scale)),Image.Resampling.LANCZOS)
        x=(im.width-1920)//2; y=(im.height-1080)//2
        im=im.crop((x,y,x+1920,y+1080))
        # Subtle cinematic grade and sharpen after the cover crop.
        im=ImageEnhance.Color(im).enhance(1.08)
        im=ImageEnhance.Contrast(im).enhance(1.06)
        im=im.filter(ImageFilter.UnsharpMask(radius=2,percent=115,threshold=3))
        im.save(path,"PNG",optimize=True)

def make_background(path,idx):
    W,H=1920,1080; top,mid,land,glow=PALETTES[idx]; random.seed(1800+idx)
    im=gradient((W,H),top,mid).convert("RGBA")
    haze=Image.new("RGBA",(W,H),(0,0,0,0)); hd=ImageDraw.Draw(haze)
    hd.ellipse((1120,-250,1940,570),fill=rgb(glow)+(100,))
    im=Image.alpha_composite(im,haze.filter(ImageFilter.GaussianBlur(95)))
    d=ImageDraw.Draw(im,"RGBA")
    for layer in range(3):
        base=520+layer*95; pts=[(0,H),(0,base)]; x=0
        while x<=W:
            y=base+random.randint(-75,75)+int(24*math.sin(x/145+idx))
            pts.append((x,y)); x+=random.randint(100,190)
        pts.append((W,H)); c=[top,mid,land][layer]
        d.polygon(pts,fill=rgb(c)+( [150,190,235][layer],))
    if idx==0:
        for x in [170,370,1490,1720]:
            d.rectangle((x,260,x+75,790),fill=(22,65,48,255))
            for k in range(6):
                y=260+k*72; d.ellipse((x-110,y-80,x+180,y+85),fill=(30,94+k*4,57,220))
        d.rectangle((620,430,1300,780),fill=(93,91,65,255),outline=(190,160,103,255),width=12)
        d.rectangle((740,520,1180,780),fill=(19,37,36,255))
        for x in range(650,1300,95): d.line((x,450,x+25,780),fill=(190,157,99,105),width=8)
        for x in range(80,1840,125):
            y=random.randint(500,900); d.line((x,y,x+random.randint(-80,80),y-160),fill=(38,115,66,255),width=9)
            for j in range(5):
                ex=x+random.randint(-80,80); ey=y-random.randint(80,210)
                d.ellipse((ex-45,ey-25,ex+45,ey+25),fill=(41,119+random.randint(0,55),69,235))
    elif idx==1:
        d.polygon([(0,0),(400,0),(570,260),(360,600),(0,690)],fill=(10,31,48,240))
        d.polygon([(1920,0),(1510,0),(1340,260),(1550,620),(1920,700)],fill=(10,31,48,240))
        for x in [230,410,1430,1660]:
            d.polygon([(x,770),(x+75,420),(x+150,770)],fill=(50,145,170,220),outline=(155,230,233,255))
            d.line((x+75,460,x+75,770),fill=(230,255,255,170),width=9)
        d.rectangle((760,260,1150,850),fill=(42,128,153,210)); d.line((955,280,955,840),fill=(183,242,240,230),width=65)
        d.ellipse((600,760,1320,980),fill=(28,103,131,230),outline=(123,220,220,220),width=10)
    elif idx==2:
        d.polygon([(0,650),(360,500),(600,610),(930,530),(1260,620),(1600,480),(1920,610),(1920,1080),(0,1080)],fill=(17,64,85,255))
        d.polygon([(390,510),(1460,510),(1290,790),(600,790)],fill=(67,42,34,255),outline=(204,151,83,255))
        d.line((900,500,900,160),fill=(44,39,34,255),width=26)
        d.polygon([(920,190),(1280,360),(920,420)],fill=(218,202,164,235)); d.polygon([(870,210),(580,380),(870,440)],fill=(187,163,126,235))
        for x in range(650,1350,120): d.ellipse((x,580,x+55,635),fill=(20,29,32,255),outline=(183,137,76,255),width=7)
        for x in [90,1720]: d.polygon([(x,0),(x+240,0),(x+160,550),(x-40,650)],fill=(34,76,61,255))
    elif idx==3:
        for x in range(100,1900,150):
            y=random.randint(300,760); d.line((x,1080,x+random.randint(-80,80),y),fill=(26,139,139,190),width=random.randint(12,28))
            for k in range(3): d.ellipse((x-55,y-70-k*45,x+55,y-k*45),fill=(31,159+random.randint(0,55),144,210))
        d.rectangle((560,430,1360,900),fill=(80,121,118,245),outline=(224,193,120,255),width=14)
        d.polygon([(500,450),(960,180),(1420,450)],fill=(110,145,132,255),outline=(231,202,137,255))
        d.rectangle((850,610,1070,900),fill=(7,46,63,255))
        for x in [640,1260]: d.rectangle((x,520,x+90,880),fill=(114,146,130,255),outline=(230,200,131,255),width=8)
        for k in range(40):
            x=random.randint(0,W); y=random.randint(100,H); d.ellipse((x,y,x+random.randint(4,13),y+random.randint(4,13)),outline=(173,241,230,120),width=3)
    elif idx==4:
        d.polygon([(0,800),(280,400),(560,650),(900,140),(1220,630),(1570,300),(1920,780),(1920,1080),(0,1080)],fill=(49,34,39,255))
        d.polygon([(760,900),(920,530),(1040,900)],fill=(231,85,36,255)); d.polygon([(850,900),(940,660),(1000,900)],fill=(255,185,70,255))
        for k in range(80):
            x=random.randint(0,W); y=random.randint(150,850); r=random.randint(2,8)
            d.ellipse((x-r,y-r,x+r,y+r),fill=(255,156+random.randint(0,90),64,random.randint(90,230)))
        d.rectangle((620,610,1300,890),fill=(62,51,49,255),outline=(202,113,64,255),width=15)
        d.ellipse((820,660,1100,920),fill=(247,106,37,255),outline=(255,194,87,255),width=12)
    elif idx==5:
        d.polygon([(0,700),(350,420),(620,700),(950,350),(1260,720),(1580,430),(1920,700),(1920,1080),(0,1080)],fill=(42,67,91,255))
        d.rectangle((650,470,1270,900),fill=(71,88,104,255),outline=(216,190,139,255),width=12)
        d.polygon([(600,480),(960,210),(1320,480)],fill=(101,120,129,255),outline=(229,203,151,255))
        d.ellipse((820,300,1100,580),fill=(28,49,72,255),outline=(239,208,147,255),width=12)
        d.line((960,300,960,580),fill=(235,199,131,255),width=12); d.line((820,440,1100,440),fill=(235,199,131,255),width=12)
        for k in range(90):
            x=random.randint(0,W); y=random.randint(0,560); r=random.randint(1,4)
            d.ellipse((x-r,y-r,x+r,y+r),fill=(255,244,206,random.randint(90,240)))
    elif idx==6:
        d.polygon([(0,720),(260,280),(520,720),(900,120),(1250,730),(1600,260),(1920,710),(1920,1080),(0,1080)],fill=(137,184,206,240))
        d.polygon([(720,900),(720,450),(960,220),(1200,450),(1200,900)],fill=(177,218,232,255),outline=(236,252,255,255))
        d.polygon([(830,480),(960,270),(1090,480)],fill=(229,247,251,255)); d.rectangle((850,580,1070,900),fill=(54,103,132,255))
        for x in range(100,1850,190): d.line((x,0,x+random.randint(-60,60),random.randint(300,700)),fill=(234,251,255,115),width=5)
    elif idx==7:
        for x in [150,420,1350,1620]:
            d.rectangle((x,320,x+150,900),fill=(111,104,94,255),outline=(211,177,129,255),width=10)
            d.polygon([(x-30,340),(x+75,220),(x+180,340)],fill=(142,126,104,255))
            for yy in [450,590,730]: d.rectangle((x+45,yy,x+105,yy+110),fill=(41,48,50,255))
        d.rectangle((640,440,1280,920),fill=(125,115,92,255),outline=(228,193,132,255),width=12)
        d.polygon([(590,450),(960,180),(1330,450)],fill=(153,132,99,255)); d.rectangle((860,590,1060,920),fill=(37,42,43,255))
        for k in range(25):
            x=random.randint(0,W); y=random.randint(750,H); d.ellipse((x,y,x+random.randint(40,140),y+random.randint(10,30)),fill=(36,92,61,130))
    else:
        d.polygon([(0,700),(260,510),(560,700),(880,440),(1230,700),(1580,500),(1920,680),(1920,1080),(0,1080)],fill=(29,67,80,255))
        d.polygon([(770,840),(850,330),(1070,330),(1150,840)],fill=(214,204,174,255),outline=(87,83,72,255))
        d.rectangle((840,280,1080,360),fill=(64,76,78,255),outline=(240,211,143,255),width=9)
        d.polygon([(820,285),(960,170),(1100,285)],fill=(48,58,62,255))
        d.ellipse((900,205,1020,325),fill=(255,233,163,255),outline=(255,255,225,255),width=9)
        for a in [-25,0,25]:
            d.line((960,265,960+int(math.cos(math.radians(a))*850),265+int(math.sin(math.radians(a))*850)),fill=(255,233,165,42),width=35)
    for side in [0,1]:
        for k in range(45):
            x=random.randint(0,260) if side==0 else random.randint(W-260,W); y=random.randint(300,H); r=random.randint(20,75)
            c=(24,75+random.randint(0,70),57,random.randint(130,230)) if idx in [0,2,3,7] else (65,95,112,random.randint(100,190))
            d.ellipse((x-r,y-r,x+r,y+r),fill=c)
    for k in range(9500):
        x=random.randrange(W); y=random.randrange(H); r=random.choice([1,1,2,3]); a=random.randint(8,35)
        d.ellipse((x,y,x+r,y+r),fill=(245,226,180,a) if k%2 else (10,25,31,a))
    im.convert("RGB").save(path,"PNG",optimize=True)

def draw_item(path,kind,color,dark,seed):
    S=384; im=Image.new("RGBA",(S,S),(0,0,0,0)); random.seed(seed)
    gold=(238,195,111,255); edge=rgb(dark)+(255,); main=rgb(color)+(255,); light=(255,244,204,255)
    sh=Image.new("RGBA",(S,S),(0,0,0,0)); ImageDraw.Draw(sh).ellipse((65,315,325,355),fill=(0,0,0,85))
    im=Image.alpha_composite(im,sh.filter(ImageFilter.GaussianBlur(14))); d=ImageDraw.Draw(im)
    def poly(p,f=main,o=edge,w=10):
        d.polygon(p,fill=f)
        if o: d.line(p+[p[0]],fill=o,width=w,joint="curve")
    def line(p,f=gold,w=12): d.line(p,fill=f,width=w,joint="curve")
    def el(b,f=main,o=edge,w=10): d.ellipse(b,fill=f,outline=o,width=w)
    if kind=="gem":
        poly([(192,35),(300,115),(270,285),(192,340),(114,285),(84,115)])
        poly([(192,35),(192,340),(114,285),(84,115)],(255,226,157,210),None)
        line([(84,115),(192,150),(300,115)],light,8); line([(192,150),(192,340)],gold,8)
    elif kind=="disk":
        el((55,55,329,329)); el((88,88,296,296),(0,0,0,0),gold,8)
        for a in range(12):
            ang=a*math.pi/6; line([(192+int(math.cos(ang)*112),192+int(math.sin(ang)*112)),(192+int(math.cos(ang)*145),192+int(math.sin(ang)*145))],gold,8)
        el((165,165,219,219),light,edge,5)
    elif kind=="heart":
        poly([(192,320),(70,205),(58,130),(95,75),(155,78),(192,125),(230,78),(290,75),(326,130),(314,205)])
        line([(112,112),(151,108),(176,132)],light,10); line([(192,155),(192,286)],gold,7)
    elif kind=="shell":
        poly([(60,260),(70,155),(120,85),(192,58),(264,85),(314,155),(324,260),(192,315)])
        for x in [110,150,192,234,274]: line([(192,300),(x,105)],gold,8)
        line([(70,250),(314,250)],light,8)
    elif kind=="mask":
        poly([(70,80),(314,80),(294,260),(192,330),(90,260)])
        poly([(92,150),(158,142),(168,188),(110,198)],(35,35,45,255),gold,5)
        poly([(292,150),(226,142),(216,188),(274,198)],(35,35,45,255),gold,5); line([(145,250),(192,272),(239,250)],light,9)
    elif kind=="idol":
        poly([(192,38),(280,118),(258,295),(192,342),(126,295),(104,118)])
        el((135,145,170,180),gold,None,1); el((214,145,249,180),gold,None,1)
        line([(145,225),(192,250),(239,225)],edge,12); line([(130,105),(192,130),(254,105)],light,8)
    elif kind=="rune":
        poly([(192,35),(300,115),(280,250),(192,345),(104,250),(84,115)],(0,0,0,0),gold,18)
        poly([(192,88),(250,192),(192,294),(134,192)]); line([(192,88),(192,294)],light,7)
    elif kind=="key":
        el((55,65,210,220),(0,0,0,0),gold,25); el((100,110,165,175),dark,None,1)
        line([(185,185),(315,315)],gold,30); line([(260,260),(300,220)],light,12); line([(290,290),(330,250)],edge,14)
    elif kind=="lever":
        line([(105,290),(270,80)],gold,36); el((220,35,325,140),main,edge,14); el((70,255,145,330),dark,gold,12); line([(120,270),(245,110)],light,8)
    elif kind=="hammer":
        poly([(55,70),(320,70),(320,150),(55,150)]); poly([(165,135),(225,135),(240,335),(150,335)],(132,82,48,255))
        line([(176,165),(184,300)],(225,177,107,255),8); line([(72,82),(300,82)],light,8)
    elif kind=="telescope":
        poly([(65,105),(275,165),(245,245),(35,185)]); poly([(260,160),(330,185),(300,285),(230,260)],gold)
        line([(125,205),(80,325)],(142,96,55,255),14); line([(185,220),(225,330)],(142,96,55,255),14); line([(90,125),(260,180)],light,8)
    elif kind=="trident":
        line([(192,70),(192,330)],gold,22); line([(192,125),(95,45)],gold,20); line([(192,125),(290,45)],gold,20)
        line([(95,45),(95,110)],light,14); line([(290,45),(290,110)],light,14); line([(192,70),(192,30)],light,10)
    elif kind in ("book","map"):
        if kind=="book":
            poly([(55,75),(185,100),(192,315),(55,290)]); poly([(329,75),(200,100),(192,315),(329,290)],(176,120,67,255))
            line([(192,100),(192,315)],gold,12)
            for y in [145,190,235]: line([(82,y),(160,y+12)],light,6); line([(225,y+12),(300,y)],light,6)
            el((164,50,220,106),gold,edge,6)
        else:
            poly([(65,75),(150,45),(235,75),(320,45),(320,300),(235,330),(150,300),(65,330)],(208,175,117,255))
            line([(150,50),(150,300)],gold,8); line([(235,75),(235,330)],gold,8)
            line([(90,245),(150,175),(210,220),(285,125)],(142,77,46,255),10); el((250,95,285,130),(196,56,43,255),gold,6)
    elif kind in ("lantern","bell"):
        if kind=="lantern":
            line([(125,95),(125,55),(259,55),(259,95)],gold,12); poly([(110,105),(274,105),(292,290),(92,290)])
            poly([(145,135),(239,135),(252,260),(132,260)],(255,218,129,235),gold,6)
            line([(192,140),(192,250)],light,9); line([(92,290),(292,290)],gold,14)
        else:
            el((100,80,284,275)); poly([(85,115),(299,115),(260,260),(124,260)])
            line([(192,45),(192,85)],gold,14); el((168,265,216,315),gold,edge,8); line([(120,155),(264,155)],light,8)
    elif kind in ("amphora","crown"):
        if kind=="amphora":
            poly([(145,50),(239,50),(225,120),(275,180),(250,300),(192,340),(134,300),(109,180),(159,120)])
            line([(145,50),(239,50)],gold,16); line([(132,180),(252,180)],light,9)
            el((110,145,160,205),(0,0,0,0),gold,10); el((224,145,274,205),(0,0,0,0),gold,10)
        else:
            poly([(60,125),(110,190),(150,80),(192,170),(245,75),(295,190),(325,125),(295,290),(90,290)])
            line([(90,250),(295,250)],gold,12)
            for x in [110,192,274]: el((x-12,180,x+12,204),light,None,1)
    else:
        el((75,75,309,309)); line([(115,192),(269,192)],gold,12)
    d=ImageDraw.Draw(im); d.arc((90,65,290,260),195,285,fill=light,width=7)
    for x,y in [(85,80),(300,110),(280,300)]: d.ellipse((x-5,y-5,x+5,y+5),fill=light)
    im.save(path,"PNG",optimize=True)

def enhance_game(root):
    base=Path(__file__).resolve().parent.parent
    story_path=base/"game_data/story.json"; story=json.loads(story_path.read_text(encoding="utf-8"))
    levels=story["levels"]
    if len(levels)!=10 or sum(len(x.get("items",[])) for x in levels[1:])!=45: raise SystemExit("Expected 45 chapter targets")
    # Preserve level 1 and its existing PNG background exactly.
    for p in (root/"assets").rglob("*.svg"): p.unlink()
    backgrounds=root/"assets/backgrounds"; backgrounds.mkdir(parents=True,exist_ok=True)
    items_dir=root/"assets/items"; items_dir.mkdir(parents=True,exist_ok=True)
    source_map={
        "jungle_ruins":"source_meadow.jpg",
        "pirate_cove":"source_port_hayalang3.png",
        "sky_observatory":"source_wizardtower.png",
        "ice_kingdom":"source_coldmountain.png",
        "lost_city":"source_desert_clouds.png",
        "final_lighthouse":"source_port_hayalang4.png",
    }
    for i,level in enumerate(levels[1:]):
        level["background_path"]=f"res://assets/backgrounds/{level['scene']}.png"
        target=backgrounds/f"{level['scene']}.png"
        source=base/"assets/backgrounds"/source_map.get(level["scene"],"")
        if level["scene"] in source_map and source.is_file():
            make_background_from_source(source,target)
        else:
            make_background(target,i)
    story_path.write_text(json.dumps(story,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    palette=[("#b86b3d","#633d32"),("#67d9e8","#276b91"),("#d8a34e","#77502e"),("#3dbfc4","#176f8c"),("#f16d42","#872d2b"),("#d8b36b","#765332"),("#9fd6ed","#4c829f"),("#d4b36c","#785634"),("#bde5ee","#5e91a3")]
    rows=[]; n=0
    for li,level in enumerate(levels[1:]):
        color,dark=palette[li]; row=[]
        for item in level["items"]:
            slug=item["slug"]; x,y=item["position"]; draw_item(items_dir/f"{slug}.png",KINDS[n],color,dark,li*10+n)
            row.append(f'{{"id":{item["id"]},"slug":"{slug}","name":"{item["name"]}","pos":Vector2({x},{y})}}'); n+=1
        rows.append("\t[\n\t\t"+",\n\t\t".join(row)+"\n\t]")
    src=root/"scripts/game.gd"; s=src.read_text(encoding="utf-8")
    s=s.replace("res://assets/levels/","res://assets/backgrounds/").replace(".svg",".png")
    if "const CHAPTER_ITEMS :=" not in s:
        if s.count("const CREAM :=")!=1: raise SystemExit("Missing color constant anchor")
        s=s.replace("const CREAM :=","const CHAPTER_ITEMS := [\n"+",\n".join(rows)+"\n]\nconst CREAM :=",1)
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
    new='''func _load_current_level() -> void:\n\t_load_chapter(current_level)\n\nfunc _load_chapter(index: int) -> void:\n\tcurrent_level = clampi(index,0,LEVEL_DATA.size()-1)\n\tbackground = load(LEVEL_DATA[current_level].background)\n\tchapter_items = ITEM_DATA if current_level == 0 else CHAPTER_ITEMS[current_level-1]\n\tchapter_textures.clear()\n\tif current_level == 0:\n\t\tfor texture in item_textures: chapter_textures.append(texture)\n\telse:\n\t\tfor item in chapter_items:\n\t\t\tvar path := "res://assets/items/%s.png" % item.slug\n\t\t\tvar texture := load(path) as Texture2D\n\t\t\tif texture == null: push_error("Missing item artwork: " + path)\n\t\t\telse: chapter_textures.append(texture)\n\tif background == null: push_error("Missing chapter background: " + LEVEL_DATA[current_level].background)\n\t_save_progress()\n\nfunc _load_progress() -> void:\n\tvar cfg := ConfigFile.new()\n\tif cfg.load("user://magicworld_progress.cfg") == OK:\n\t\tcurrent_level = clampi(int(cfg.get_value("progress","current_level",0)),0,LEVEL_DATA.size()-1)\n\t\tunlocked_level_count = clampi(int(cfg.get_value("progress","unlocked_level_count",1)),1,LEVEL_DATA.size())\n\nfunc _save_progress() -> void:\n\tvar cfg := ConfigFile.new()\n\tcfg.set_value("progress","current_level",current_level)\n\tcfg.set_value("progress","unlocked_level_count",unlocked_level_count)\n\tcfg.save("user://magicworld_progress.cfg")'''
    once(old,new,"chapter loader")
    old='''func _advance_level() -> void:\n\tif current_level < LEVEL_DATA.size()-1:\n\t\tcurrent_level += 1\n\t\tunlocked_level_count = maxi(unlocked_level_count, current_level+1)\n\telse:\n\t\tcurrent_level = 0\n\t\tunlocked_level_count = LEVEL_DATA.size()\n\t_load_current_level()\n\t_reset_round()'''
    new='''func _advance_level() -> void:\n\tif current_level < LEVEL_DATA.size()-1:\n\t\tcurrent_level += 1\n\t\tunlocked_level_count = maxi(unlocked_level_count,current_level+1)\n\telse:\n\t\tcurrent_level = LEVEL_DATA.size()-1\n\t\tunlocked_level_count = LEVEL_DATA.size()\n\t_load_chapter(current_level)\n\t_save_progress()\n\t_reset_round()'''
    once(old,new,"progression")
    s=s.replace('"%02d / 30" % found.size()','"%02d / %02d" % [found.size(),chapter_items.size()]')
    s=s.replace('"Найден первый фрагмент карты"','"Артефакт: " + LEVEL_DATA[current_level].artifact')
    s=s.replace('"Все 30 сокровищ найдены"','"Все предметы этой локации найдены"')
    src.write_text(s,encoding="utf-8")
    leftovers=list((root/"assets").rglob("*.svg"))
    if leftovers: raise SystemExit("SVG files remain: "+", ".join(str(p.relative_to(root)) for p in leftovers))
    if ".svg" in s: raise SystemExit("SVG runtime path remains in game.gd: "+repr([line for line in s.splitlines() if ".svg" in line]))
