"""
Kingdom Rush – Pixel Art Asset Generator
Generates all sprites for assets/ directory.
Each sprite is carefully drawn with shading, outlines, highlights.
"""

from PIL import Image, ImageDraw, ImageFilter
import math, os, random

# ─── Output directory ───────────────────────────────────────────────
BASE = "/home/claude/assets"
for d in ["towers","enemies","hero","ui","terrain"]:
    os.makedirs(f"{BASE}/{d}", exist_ok=True)

# ─── Utility helpers ────────────────────────────────────────────────
def px(img, draw=None):
    """Return (img, ImageDraw) pair."""
    if draw is None:
        draw = ImageDraw.Draw(img)
    return img, draw

def new(w, h):
    img = Image.new("RGBA", (w, h), (0,0,0,0))
    return img, ImageDraw.Draw(img)

def shade(col, factor):
    """Darken or lighten a color tuple."""
    return tuple(max(0,min(255,int(c*factor))) for c in col)

def lerp_col(a, b, t):
    return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(len(a)))

def outline(draw, pts, col=(0,0,0,255), w=1):
    draw.line(pts+[pts[0]], fill=col, width=w)

def ellipse_aa(draw, bbox, fill, outline_col=None, ow=1):
    draw.ellipse(bbox, fill=fill, outline=outline_col, width=ow)

def rect_aa(draw, bbox, fill, outline_col=None, ow=1):
    draw.rectangle(bbox, fill=fill, outline=outline_col, width=ow)

def poly(draw, pts, fill, outline_col=None, ow=1):
    draw.polygon(pts, fill=fill, outline=outline_col)

def save(img, path):
    full = f"{BASE}/{path}"
    img.save(full, "PNG")
    print(f"  ✓ {path}")

# ─────────────────────────────────────────────────────────────────────
#  TERRAIN TILES
# ─────────────────────────────────────────────────────────────────────
def make_grass():
    img, d = new(40, 40)
    rng = random.Random(42)
    # Base gradient
    for y in range(40):
        t = y/39
        c = lerp_col((38,110,38),(28,80,28),t)
        d.line([(0,y),(39,y)], fill=(*c,255))
    # Checkerboard variation
    for x in range(0,40,2):
        for y in range(0,40,2):
            if (x//2+y//2)%2==0:
                c2 = (42,118,42,60)
                d.rectangle([x,y,x+1,y+1], fill=c2)
    # Grass tufts
    for _ in range(14):
        gx = rng.randint(2,37); gy = rng.randint(4,36)
        bright = rng.randint(10,30)
        gc = (48+bright,130+bright,48,255)
        d.line([(gx,gy),(gx+rng.randint(-2,2),gy-rng.randint(3,6))], fill=gc, width=1)
    # Small flowers
    for _ in range(4):
        fx = rng.randint(3,36); fy = rng.randint(3,36)
        fc = rng.choice([(230,210,80,255),(200,200,255,255),(255,180,160,255)])
        d.ellipse([fx-1,fy-1,fx+1,fy+1], fill=fc)
    # Subtle vignette edges
    for i in range(3):
        alpha = 20*(i+1)
        d.rectangle([i,i,39-i,39-i], outline=(0,0,0,alpha), width=1)
    return img

def make_cobblestone():
    img, d = new(40, 40)
    rng = random.Random(99)
    # Mortar background
    d.rectangle([0,0,39,39], fill=(72,62,50,255))
    # Draw individual stones
    stones = [
        (2,2,17,10),(20,2,37,10),(2,13,12,21),(15,13,29,21),(32,13,37,21),
        (2,24,19,32),(22,24,37,32),(2,35,13,38),(16,35,37,38),(20,2,37,10),
    ]
    for (x1,y1,x2,y2) in stones:
        if x2>39: x2=39
        if y2>39: y2=39
        shade_v = rng.randint(-18,18)
        base = (130+shade_v,118+shade_v//2,90+shade_v//3,255)
        dark = shade(base[:3]+(255,), 0.6)
        light = tuple(min(255,c+50) for c in base[:3])+(255,)
        # shadow offset
        d.rectangle([x1+1,y1+1,x2+1,y2+1], fill=dark)
        d.rectangle([x1,y1,x2,y2], fill=base)
        # top/left highlight
        d.line([(x1+1,y1+1),(x2-1,y1+1)], fill=light, width=1)
        d.line([(x1+1,y1+1),(x1+1,y2-1)], fill=light, width=1)
        # moss patches occasionally
        if rng.random() < 0.25:
            mx = rng.randint(x1+2,max(x1+3,x2-3))
            my = rng.randint(y1+2,max(y1+3,y2-2))
            d.ellipse([mx,my,mx+3,my+2], fill=(80,120,60,140))
    return img

# ─────────────────────────────────────────────────────────────────────
#  UI ICONS
# ─────────────────────────────────────────────────────────────────────
def make_gold_icon():
    img, d = new(22, 22)
    # Coin glow
    for r in range(11,5,-1):
        alpha = int(60*(1-r/11))
        d.ellipse([11-r,11-r,11+r,11+r], fill=(240,200,0,alpha))
    # Coin body with gradient
    for y in range(4,18):
        t = (y-4)/13
        c = lerp_col((255,230,60),(200,160,20),t)
        d.line([(4,y),(17,y)], fill=(*c,255))
    d.ellipse([3,3,18,18], fill=None, outline=(160,120,10,255), width=2)
    # Shine
    d.ellipse([6,5,12,9], fill=(255,245,140,160))
    # Inner ring
    d.ellipse([6,6,15,15], fill=None, outline=(180,140,20,120), width=1)
    # "$" symbol  
    d.line([(10,7),(10,14)], fill=(160,110,0,200), width=1)
    d.arc([7,8,13,12], 0, 180, fill=(160,110,0,200), width=1)
    d.arc([7,10,13,14], 180, 0, fill=(160,110,0,200), width=1)
    return img

def make_heart_icon():
    img, d = new(22, 22)
    # Heart shape via two circles + triangle
    # Glow
    for r in range(10,4,-1):
        alpha = int(50*(1-r/10))
        d.ellipse([11-r,11-r,11+r,11+r], fill=(255,0,60,alpha))
    # Heart body
    pts_heart = []
    for i in range(360):
        angle = math.radians(i)
        # Cardioid parametric
        x = 11 + 8*(math.sin(angle)**3)
        y = 11 - (7*math.cos(angle)-3*math.cos(2*angle)-math.cos(3*angle)-0.5*math.cos(4*angle))
        pts_heart.append((x,y))
    d.polygon(pts_heart, fill=(220,40,60,255))
    # Highlight
    d.ellipse([7,5,13,10], fill=(255,120,140,180))
    # Dark outline
    d.polygon(pts_heart, fill=None, outline=(140,10,30,255))
    return img

# ─────────────────────────────────────────────────────────────────────
#  TOWERS  (64×80)
# ─────────────────────────────────────────────────────────────────────

def draw_tower_base(d, W, H, stone_col=(130,118,95), mortar_col=(70,62,50)):
    """Draw a stone tower base / platform."""
    # Ground shadow
    d.ellipse([W//2-22, H-12, W//2+22, H-2], fill=(0,0,0,60))
    # Base platform
    base_pts = [(W//2-24,H-6),(W//2+24,H-6),(W//2+20,H-18),(W//2-20,H-18)]
    d.polygon(base_pts, fill=shade(stone_col,0.7))
    d.polygon(base_pts, outline=shade(mortar_col,0.8), width=1)

def draw_stone_tower_body(d, W, H, cx, base_y, top_y, w_bot, w_top,
                          stone_col=(128,116,92), mortar=(70,62,50)):
    """Draw a tapered stone tower body with coursed stones."""
    body_pts = [
        (cx-w_bot//2, base_y),
        (cx+w_bot//2, base_y),
        (cx+w_top//2, top_y),
        (cx-w_top//2, top_y),
    ]
    # Shadow side
    shadow_pts = [
        (cx+w_bot//2, base_y),
        (cx+w_bot//2+4, base_y+2),
        (cx+w_top//2+4, top_y+2),
        (cx+w_top//2, top_y),
    ]
    d.polygon(shadow_pts, fill=shade(stone_col, 0.55))
    d.polygon(body_pts, fill=stone_col)
    # Stone courses (horizontal mortar lines)
    for y in range(top_y+6, base_y, 8):
        t = (y-top_y)/(base_y-top_y)
        lx = int(cx - (w_bot//2*t + w_top//2*(1-t)))
        rx = int(cx + (w_bot//2*t + w_top//2*(1-t)))
        d.line([(lx,y),(rx,y)], fill=mortar, width=1)
    # Vertical mortar (staggered)
    row = 0
    for y in range(top_y+6, base_y, 8):
        t = (y-top_y)/(base_y-top_y)
        lx = int(cx - (w_bot//2*t + w_top//2*(1-t)))
        rx = int(cx + (w_bot//2*t + w_top//2*(1-t)))
        w = rx-lx
        offset = (row%2) * 6
        for vx in range(lx+offset, rx, 10):
            d.line([(vx,y),(vx,min(y+8,base_y))], fill=mortar, width=1)
        row += 1
    # Highlight edge
    d.line([(cx-w_top//2,top_y),(cx-w_bot//2,base_y)], fill=shade(stone_col,1.3), width=1)
    # Outline
    d.polygon(body_pts, outline=mortar, width=1)

def draw_battlements(d, cx, y, w, count=4, stone_col=(128,116,92), mortar=(70,62,50)):
    """Draw crenellated top."""
    slot_w = w // count
    for i in range(count):
        x1 = cx - w//2 + i*slot_w
        # Merlon (raised part)
        if i%2==0:
            d.rectangle([x1+1,y-8,x1+slot_w-1,y+4], fill=stone_col, outline=mortar, width=1)
            # Top highlight
            d.line([(x1+2,y-7),(x1+slot_w-2,y-7)], fill=shade(stone_col,1.3), width=1)
        else:
            # Crenel (gap)
            d.rectangle([x1,y-2,x1+slot_w,y+4], fill=shade(stone_col,0.7), outline=mortar, width=1)

# ── ARCHER TOWER ────────────────────────────────────────────────────
def make_archer_lv(level):
    W,H = 64,80
    img, d = new(W,H)
    SC = (132,120,96)   # stone color
    MO = (72,64,52)     # mortar

    draw_tower_base(d, W, H, SC, MO)
    # Tower body
    bots = [22,24,26][level-1]
    tops = [16,18,20][level-1]
    top_y = [38,30,22][level-1]
    draw_stone_tower_body(d, W, H, W//2, H-18, top_y, bots*2, tops*2, SC, MO)

    # Platform ledge
    ply = top_y+2
    d.rectangle([W//2-tops-3, ply, W//2+tops+3, ply+5], fill=shade(SC,0.85), outline=MO, width=1)

    # Battlements
    draw_battlements(d, W//2, top_y-4, tops*2+6, count=4+level, stone_col=SC, mortar=MO)

    # Archer figure
    ax, ay = W//2, top_y-2
    body_col = (80,50,25,255)    # brown leather
    skin_col = (220,175,130,255)
    hood_col = (40,80,40,255)    # forest green
    if level==1:
        # Simple archer
        d.ellipse([ax-4,ay-16,ax+4,ay-8], fill=skin_col, outline=(160,110,80,255))  # head
        d.ellipse([ax-5,ay-17,ax+5,ay-7], fill=None, outline=(80,60,20,255), width=1)  # hair outline
        d.rectangle([ax-5,ay-8,ax+5,ay+2], fill=body_col, outline=(50,30,10,255))  # body
        # Hood
        d.polygon([(ax-5,ay-12),(ax+5,ay-12),(ax+3,ay-18),(ax-3,ay-18)], fill=hood_col)
    elif level==2:
        # Archer with cape
        d.ellipse([ax-5,ay-18,ax+5,ay-8], fill=skin_col)
        d.polygon([(ax-5,ay-14),(ax+5,ay-14),(ax+4,ay-20),(ax-4,ay-20)], fill=hood_col)
        d.rectangle([ax-6,ay-8,ax+6,ay+4], fill=body_col, outline=(50,30,10,255))
        # Cape
        d.polygon([(ax+6,ay-6),(ax+6,ay+4),(ax+12,ay+6),(ax+12,ay-8)], fill=(100,30,30,220))
        # Bow arm
        d.line([(ax-6,ay-4),(ax-14,ay-8)], fill=(120,80,40,255), width=2)
    else:
        # Elite archer with full equipment
        d.ellipse([ax-5,ay-20,ax+5,ay-10], fill=skin_col)
        d.polygon([(ax-6,ay-15),(ax+6,ay-15),(ax+5,ay-22),(ax-5,ay-22)], fill=(20,60,20,255))
        # Feather on hood
        d.line([(ax+3,ay-22),(ax+8,ay-28)], fill=(200,200,50,255), width=2)
        d.rectangle([ax-7,ay-10,ax+7,ay+5], fill=(60,40,15,255))
        d.rectangle([ax-5,ay-9,ax+5,ay+4], fill=body_col)
        # Quiver
        d.rectangle([ax+7,ay-8,ax+12,ay+2], fill=(90,60,20,255), outline=(50,30,10,255))
        for i in range(3):
            d.line([(ax+8+i,ay-10),(ax+8+i,ay-8)], fill=(180,140,60,255), width=1)
        # Bow
        d.arc([ax-18,ay-10,ax-6,ay+2], 270, 90, fill=(120,80,30,255), width=2)
        # Arrow
        d.line([(ax-14,ay-4),(ax-2,ay-4)], fill=(160,120,40,255), width=1)
        d.polygon([(ax-2,ay-5),(ax-2,ay-3),(ax+1,ay-4)], fill=(180,50,50,255))

    # Arrow slits
    for i, sy in enumerate(range(top_y+12, H-22, 10)):
        sx = W//2 + (i%2)*0-0
        d.rectangle([sx-1,sy,sx+1,sy+5], fill=(20,15,10,255))

    # Level indicator dots
    for i in range(level):
        d.ellipse([W//2-6+i*5-((level-1)*2), H-6, W//2-3+i*5-((level-1)*2), H-3],
                  fill=(240,200,40,255), outline=(160,120,0,255))
    return img

# ── MAGE TOWER ──────────────────────────────────────────────────────
def make_mage_lv(level):
    W,H = 64,80
    img, d = new(W,H)
    SC = (90,70,120,255)   # purple stone
    SC3 = (90,70,120)
    MO = (50,40,70,255)
    MO3 = (50,40,70)
    GLOW = [(80,60,180),(110,80,220),(150,100,255)][level-1]

    draw_tower_base(d, W, H, (100,80,130), (55,42,72))

    # Tower body - more elegant, narrower
    tops = [14,16,18][level-1]
    top_y = [32,24,16][level-1]
    draw_stone_tower_body(d, W, H, W//2, H-18, top_y, 26, tops*2, (95,75,128), (52,42,72))

    # Glowing runes on tower body
    rune_col = (*GLOW, 180)
    rune_positions = [(W//2-4, top_y+14), (W//2+4, top_y+22), (W//2-3, top_y+30)]
    for i, (rx,ry) in enumerate(rune_positions[:1+level]):
        # Rune glow
        d.ellipse([rx-4,ry-4,rx+4,ry+4], fill=(*GLOW,40))
        # Rune symbol
        if i%3==0:
            d.line([(rx-3,ry),(rx+3,ry)], fill=rune_col, width=1)
            d.line([(rx,ry-3),(rx,ry+3)], fill=rune_col, width=1)
        elif i%3==1:
            d.polygon([(rx,ry-3),(rx+3,ry+2),(rx-3,ry+2)], fill=None, outline=rune_col)
        else:
            d.ellipse([rx-3,ry-3,rx+3,ry+3], fill=None, outline=rune_col)

    # Pointed roof / spire
    spire_pts = [(W//2, top_y-22+level*4),(W//2-tops-2, top_y),(W//2+tops+2, top_y)]
    d.polygon(spire_pts, fill=(60,45,90,255))
    d.polygon(spire_pts, outline=(80,60,120,255), width=1)
    # Spire bands
    for b in range(1,4):
        by = top_y - 5*b
        bw = max(2, tops*(1-b/5)+1)
        d.line([(W//2-int(bw),by),(W//2+int(bw),by)], fill=(*GLOW,120), width=1)

    # Crystal orb at top
    ox, oy = W//2, top_y-22+level*4-6
    for r in range(7,0,-1):
        alpha = int(180*(1-r/7))
        d.ellipse([ox-r,oy-r,ox+r,oy+r], fill=(*GLOW,alpha))
    d.ellipse([ox-5,oy-5,ox+5,oy+5], fill=(*GLOW,220), outline=(200,180,255,255))
    d.ellipse([ox-2,oy-3,ox+2,oy+1], fill=(255,255,255,160))  # shine

    # Mage figure
    ax, ay = W//2, top_y+2
    robe_col = (70,40,100,255)
    d.ellipse([ax-4,ay-16,ax+4,ay-8], fill=(220,180,140,255))  # face
    # Hat
    d.polygon([(ax,ay-24),(ax-6,ay-16),(ax+6,ay-16)], fill=(40,20,70,255))
    d.rectangle([ax-7,ay-16,ax+7,ay-14], fill=(50,30,80,255))
    # Star on hat
    d.text((ax-3,ay-22), "✦", fill=(*GLOW,255)) if level==3 else None
    d.rectangle([ax-5,ay-8,ax+5,ay+3], fill=robe_col, outline=(40,20,60,255))
    # Staff
    d.line([(ax+6,ay-6),(ax+6,ay+4)], fill=(100,70,30,255), width=2)
    d.ellipse([ax+3,ay-10,ax+9,ay-4], fill=(*GLOW,200), outline=(200,180,255,200))

    # Window openings
    for wy in [top_y+10, top_y+20]:
        d.rectangle([W//2-2,wy,W//2+2,wy+6], fill=(15,10,25,255))
        d.arc([W//2-2,wy,W//2+2,wy+2], 0, 180, fill=(*GLOW,80), width=1)

    # Level stars
    for i in range(level):
        sx = W//2 - 5 + i*5
        d.polygon([(sx,H-7),(sx-2,H-3),(sx+2,H-3)], fill=(*GLOW,220))
    return img

# ── ARTILLERY TOWER ─────────────────────────────────────────────────
def make_artillery_lv(level):
    W,H = 64,80
    img, d = new(W,H)
    SC = (110,100,85)
    MO = (65,58,48)
    metal = (80,80,90)
    barrel_col = (60,60,68)

    draw_tower_base(d, W, H, SC, MO)
    top_y = [36,28,20][level-1]
    draw_stone_tower_body(d, W, H, W//2, H-18, top_y, 30, 28, SC, MO)

    # Heavy parapet
    d.rectangle([W//2-17,top_y-4,W//2+17,top_y+6], fill=shade(SC,0.9), outline=MO, width=1)
    draw_battlements(d, W//2, top_y-4, 34, count=5, stone_col=SC, mortar=MO)

    # Cannon turret base
    tx, ty = W//2, top_y-6
    d.ellipse([tx-12,ty-8,tx+12,ty+4], fill=metal, outline=(40,40,48,255))
    d.ellipse([tx-10,ty-7,tx+10,ty+2], fill=shade(metal,1.2))

    # Barrel
    angle_deg = -35 - level*5
    blen = [18,20,22][level-1]
    bw = [5,5,6][level-1]
    bx = math.cos(math.radians(angle_deg))*blen
    by = math.sin(math.radians(angle_deg))*blen
    # Barrel body
    d.line([(tx,ty-2),(int(tx+bx),int(ty+by-2))], fill=barrel_col, width=bw)
    d.line([(tx,ty-2),(int(tx+bx),int(ty+by-2))], fill=shade(barrel_col,1.5), width=bw-2)
    # Muzzle
    d.ellipse([int(tx+bx)-3,int(ty+by)-5,int(tx+bx)+3,int(ty+by)+1], fill=(30,30,36,255))
    # Barrel bands
    for band in [0.3,0.6,0.85]:
        bx2 = int(tx+bx*band); by2 = int(ty+by*band-2)
        d.ellipse([bx2-bw//2-1,by2-2,bx2+bw//2+1,by2+2], fill=(50,50,60,255))

    # Operator figure
    ox, oy = W//2-8, top_y-2
    d.ellipse([ox-3,oy-12,ox+3,oy-6], fill=(210,170,130,255))
    d.rectangle([ox-4,oy-6,ox+4,oy+2], fill=(100,60,20,255), outline=(60,35,10,255))
    # Helmet
    d.ellipse([ox-4,oy-14,ox+4,oy-8], fill=(80,80,90,255))
    # Arm reaching to cannon
    d.line([(ox+4,oy-4),(tx-2,ty)], fill=(80,55,20,255), width=2)

    # Smoke puffs (level 2+)
    if level >= 2:
        for i, (sx2,sy2) in enumerate([(int(tx+bx)+4,int(ty+by)-4),(int(tx+bx)+8,int(ty+by)-8)]):
            alpha = 80-i*30
            d.ellipse([sx2-4,sy2-4,sx2+4,sy2+4], fill=(180,180,180,alpha))

    # Level bolts (metalwork detail)
    for i in range(level):
        bx3 = W//2-5+i*5
        d.ellipse([bx3,H-7,bx3+3,H-4], fill=(160,160,170,255))
    return img

# ── ICE TOWER ───────────────────────────────────────────────────────
def make_ice_lv(level):
    W,H = 64,80
    img, d = new(W,H)
    SC = (100,140,180)  # icy blue stone
    MO = (60,100,140)
    ICE = (160,220,255)
    DEEP = (40,80,140)

    draw_tower_base(d, W, H, (90,130,170), (55,95,135))
    top_y = [34,26,18][level-1]
    draw_stone_tower_body(d, W, H, W//2, H-18, top_y, 28, 26, SC, MO)

    # Ice crystal clusters on tower
    def draw_crystal(cx2,cy2,size,angle):
        pts = []
        for a in [angle-20,angle,angle+20]:
            pts.append((cx2+math.cos(math.radians(a))*size,
                         cy2+math.sin(math.radians(a))*size))
        pts.append((cx2,cy2+2))
        d.polygon(pts, fill=(*ICE,160), outline=(*DEEP,200))
        # Inner shine
        d.line([(cx2,cy2),(cx2+math.cos(math.radians(angle))*size*0.6,
                            cy2+math.sin(math.radians(angle))*size*0.6)],
               fill=(255,255,255,120), width=1)

    for i, (cx2,cy2,sz,ang) in enumerate([
        (W//2-8,top_y+15,10,-100),(W//2+8,top_y+15,8,-80),
        (W//2,top_y+22,12,-90),(W//2-5,top_y+28,7,-110),
    ][:1+level]):
        draw_crystal(cx2,cy2,sz,ang)

    # Icy crown / parapet
    crown_pts = []
    for i in range(7):
        x2 = W//2-15+i*5
        h2 = 6 if i%2==0 else 2
        crown_pts.extend([(x2,top_y-h2),(x2+4,top_y-h2),(x2+4,top_y+4)])
    d.rectangle([W//2-16,top_y,W//2+16,top_y+4], fill=shade(SC,0.8), outline=MO, width=1)

    # Large central ice spire
    spire_y = top_y - 20 - level*4
    d.polygon([(W//2,spire_y),(W//2-7,top_y),(W//2+7,top_y)], fill=(*ICE,220), outline=(*DEEP,255))
    # Spire internal lines
    for t2 in [0.3,0.6]:
        sy2 = int(spire_y + (top_y-spire_y)*t2)
        sw2 = int(7*t2)
        d.line([(W//2-sw2,sy2),(W//2+sw2,sy2)], fill=(255,255,255,100), width=1)
    # Spire tip glow
    d.ellipse([W//2-4,spire_y-4,W//2+4,spire_y+4], fill=(*ICE,80))
    d.ellipse([W//2-2,spire_y-2,W//2+2,spire_y+2], fill=(220,240,255,200))

    # Snowflake pattern on tower face
    sfx,sfy = W//2, top_y+35
    for ang in range(0,360,60):
        ex2 = sfx+math.cos(math.radians(ang))*5
        ey2 = sfy+math.sin(math.radians(ang))*5
        d.line([(sfx,sfy),(int(ex2),int(ey2))], fill=(*ICE,120), width=1)

    # Level crystals
    for i in range(level):
        cx3 = W//2-5+i*5
        d.polygon([(cx3,H-8),(cx3-2,H-4),(cx3+2,H-4)], fill=(*ICE,220), outline=(*DEEP,255))
    return img

# ── BARRACKS TOWER ──────────────────────────────────────────────────
def make_barracks_lv(level):
    W,H = 64,80
    img, d = new(W,H)
    SC = (120,108,88)
    MO = (68,60,48)
    RED = (180,40,40)
    GOLD2 = (220,180,40)

    draw_tower_base(d, W, H, SC, MO)
    top_y = [32,24,16][level-1]
    draw_stone_tower_body(d, W, H, W//2, H-18, top_y, 32, 30, SC, MO)

    # Fort platform
    d.rectangle([W//2-19,top_y,W//2+19,top_y+6], fill=shade(SC,0.85), outline=MO, width=1)
    draw_battlements(d, W//2, top_y, 38, count=6, stone_col=SC, mortar=MO)

    # Flag pole
    fpy = top_y-18-level*3
    d.line([(W//2,fpy),(W//2,top_y)], fill=(100,70,30,255), width=2)
    d.line([(W//2+1,fpy),(W//2+1,top_y)], fill=(140,100,50,255), width=1)
    # Flag
    d.polygon([(W//2,fpy),(W//2+14,fpy+5),(W//2,fpy+10)], fill=(*RED,255))
    d.polygon([(W//2,fpy+1),(W//2+12,fpy+5),(W//2,fpy+9)], fill=(220,60,60,255))
    if level==3:
        # Gold emblem on flag
        d.ellipse([W//2+4,fpy+3,W//2+8,fpy+7], fill=(*GOLD2,255))

    # Soldiers (level determines count & quality)
    soldier_positions = [(W//2-8,top_y+2),(W//2+5,top_y+2),(W//2-2,top_y-4)]
    for j, (sx3,sy3) in enumerate(soldier_positions[:level]):
        armor = (90,90,100,255) if level==1 else (70,70,82,255) if level==2 else (50,50,64,255)
        skin = (210,170,130,255)
        # Body
        d.rectangle([sx3-4,sy3-6,sx3+4,sy3+2], fill=armor, outline=(30,30,40,255))
        # Head
        d.ellipse([sx3-3,sy3-13,sx3+3,sy3-7], fill=skin)
        # Helmet
        d.ellipse([sx3-4,sy3-14,sx3+4,sy3-8], fill=armor, outline=(20,20,30,255))
        # Shield (right side soldiers)
        if j==0 or level>=2:
            shield_pts = [(sx3-7,sy3-5),(sx3-7,sy3+2),(sx3-4,sy3+4),(sx3-2,sy3+2),(sx3-2,sy3-5)]
            d.polygon(shield_pts, fill=(*RED,255), outline=(100,20,20,255))
            if level==3:
                d.line([(sx3-5,sy3-4),(sx3-3,sy3+3)], fill=(*GOLD2,200), width=1)
        # Spear
        d.line([(sx3+4,sy3-14),(sx3+4,sy3+4)], fill=(110,80,30,255), width=1)
        d.polygon([(sx3+3,sy3-18),(sx3+4,sy3-14),(sx3+5,sy3-18)], fill=(160,160,180,255))

    # Gate arch on tower face
    gy = top_y+18
    d.rectangle([W//2-7,gy,W//2+7,gy+12], fill=(20,15,10,255))
    d.arc([W//2-7,gy-4,W//2+7,gy+4], 0, 180, fill=(20,15,10,255))
    # Portcullis bars
    for bx2 in range(W//2-6,W//2+7,3):
        d.line([(bx2,gy),(bx2,gy+11)], fill=(60,50,40,255), width=1)
    d.line([(W//2-6,gy+4),(W//2+6,gy+4)], fill=(60,50,40,255), width=1)
    d.line([(W//2-6,gy+8),(W//2+6,gy+8)], fill=(60,50,40,255), width=1)

    # Level shields on base
    for i in range(level):
        bx2 = W//2-4+i*5
        d.polygon([(bx2,H-8),(bx2-2,H-5),(bx2,H-3),(bx2+2,H-5)], fill=(*RED,200))
    return img

# ─────────────────────────────────────────────────────────────────────
#  ENEMIES
# ─────────────────────────────────────────────────────────────────────

def make_goblin():
    W,H = 28,28
    img, d = new(W,H)
    cx,cy = 14,16
    skin = (80,170,60,255)
    dark = (40,100,30,255)
    eye_col = (255,60,60,255)
    # Shadow
    d.ellipse([cx-9,cy+6,cx+9,cy+10], fill=(0,0,0,50))
    # Body
    d.ellipse([cx-6,cy-4,cx+6,cy+8], fill=skin, outline=dark)
    # Head
    d.ellipse([cx-7,cy-13,cx+7,cy-1], fill=skin, outline=dark)
    # Ears (pointy)
    d.polygon([(cx-7,cy-10),(cx-12,cy-12),(cx-7,cy-6)], fill=skin, outline=dark)
    d.polygon([(cx+7,cy-10),(cx+12,cy-12),(cx+7,cy-6)], fill=skin, outline=dark)
    # Eyes
    d.ellipse([cx-5,cy-10,cx-1,cy-7], fill=(255,255,200,255), outline=dark)
    d.ellipse([cx+1,cy-10,cx+5,cy-7], fill=(255,255,200,255), outline=dark)
    d.ellipse([cx-4,cy-10,cx-2,cy-8], fill=eye_col)
    d.ellipse([cx+2,cy-10,cx+4,cy-8], fill=eye_col)
    # Nose
    d.ellipse([cx-1,cy-8,cx+1,cy-6], fill=dark)
    # Teeth/grin
    d.arc([cx-4,cy-7,cx+4,cy-4], 0, 180, fill=dark, width=1)
    d.rectangle([cx-2,cy-6,cx-1,cy-5], fill=(240,240,240,255))
    d.rectangle([cx+1,cy-6,cx+2,cy-5], fill=(240,240,240,255))
    # Loincloth
    d.polygon([(cx-5,cy+2),(cx+5,cy+2),(cx+4,cy+8),(cx-4,cy+8)], fill=(80,50,20,255), outline=(50,30,10,255))
    # Arms
    d.line([(cx-6,cy-2),(cx-10,cy+3)], fill=skin, width=3)
    d.line([(cx+6,cy-2),(cx+10,cy+3)], fill=skin, width=3)
    # Dagger
    d.line([(cx+10,cy+3),(cx+14,cy-1)], fill=(180,180,200,255), width=1)
    d.polygon([(cx+14,cy-3),(cx+14,cy-1),(cx+16,cy-2)], fill=(220,220,240,255))
    # Legs
    d.line([(cx-3,cy+8),(cx-4,cy+13)], fill=skin, width=3)
    d.line([(cx+3,cy+8),(cx+4,cy+13)], fill=skin, width=3)
    # Feet
    d.ellipse([cx-6,cy+11,cx-2,cy+14], fill=(50,30,10,255))
    d.ellipse([cx+2,cy+11,cx+6,cy+14], fill=(50,30,10,255))
    return img

def make_orc():
    W,H = 36,36
    img, d = new(W,H)
    cx,cy = 18,20
    skin = (130,100,40,255)
    dark_skin = (80,60,20,255)
    armor_col = (80,80,90,255)
    eye_col = (255,80,20,255)
    # Shadow
    d.ellipse([cx-12,cy+9,cx+12,cy+14], fill=(0,0,0,60))
    # Body (stocky)
    d.ellipse([cx-9,cy-4,cx+9,cy+12], fill=skin, outline=dark_skin)
    # Shoulder pads
    d.ellipse([cx-12,cy-6,cx-4,cy+2], fill=armor_col, outline=(40,40,50,255))
    d.ellipse([cx+4,cy-6,cx+12,cy+2], fill=armor_col, outline=(40,40,50,255))
    # Head (heavy jaw)
    d.ellipse([cx-8,cy-16,cx+8,cy-2], fill=skin, outline=dark_skin)
    # Lower jaw extension
    d.ellipse([cx-7,cy-10,cx+7,cy-3], fill=shade((130,100,40),0.9)+(255,))
    # Eyes
    d.ellipse([cx-6,cy-13,cx-1,cy-10], fill=(255,200,100,255), outline=dark_skin)
    d.ellipse([cx+1,cy-13,cx+6,cy-10], fill=(255,200,100,255), outline=dark_skin)
    d.ellipse([cx-5,cy-13,cx-2,cy-11], fill=eye_col)
    d.ellipse([cx+2,cy-13,cx+5,cy-11], fill=eye_col)
    # Nose (broad)
    d.ellipse([cx-2,cy-11,cx+2,cy-9], fill=dark_skin)
    d.ellipse([cx-3,cy-10,cx-1,cy-9], fill=(30,10,0,200))
    d.ellipse([cx+1,cy-10,cx+3,cy-9], fill=(30,10,0,200))
    # Tusks
    d.polygon([(cx-4,cy-7),(cx-6,cy-4),(cx-3,cy-4)], fill=(240,230,210,255), outline=(180,170,150,255))
    d.polygon([(cx+4,cy-7),(cx+6,cy-4),(cx+3,cy-4)], fill=(240,230,210,255), outline=(180,170,150,255))
    # Breastplate
    d.rectangle([cx-7,cy-4,cx+7,cy+6], fill=armor_col, outline=(40,40,50,255))
    d.line([(cx,cy-4),(cx,cy+6)], fill=(50,50,60,255), width=1)
    # Arms + weapon
    d.line([(cx-9,cy-2),(cx-14,cy+5)], fill=skin, width=4)
    d.line([(cx+9,cy-2),(cx+14,cy-6)], fill=skin, width=4)
    # Axe
    d.line([(cx+13,cy-9),(cx+15,cy+4)], fill=(100,80,40,255), width=2)
    d.polygon([(cx+11,cy-10),(cx+17,cy-10),(cx+17,cy-5),(cx+14,cy-6)], fill=(160,160,180,255), outline=(80,80,100,255))
    # Belt
    d.rectangle([cx-8,cy+4,cx+8,cy+7], fill=(60,40,15,255), outline=(40,25,8,255))
    d.ellipse([cx-2,cy+4,cx+2,cy+7], fill=(180,140,40,255))
    # Legs
    d.line([(cx-4,cy+12),(cx-5,cy+18)], fill=skin, width=4)
    d.line([(cx+4,cy+12),(cx+5,cy+18)], fill=skin, width=4)
    d.ellipse([cx-8,cy+16,cx-2,cy+20], fill=(70,50,20,255))
    d.ellipse([cx+2,cy+16,cx+8,cy+20], fill=(70,50,20,255))
    return img

def make_troll():
    W,H = 44,44
    img, d = new(W,H)
    cx,cy = 22,26
    skin = (60,130,80,255)
    dark_s = (30,80,45,255)
    # Shadow
    d.ellipse([cx-16,cy+12,cx+16,cy+18], fill=(0,0,0,70))
    # Very large body
    d.ellipse([cx-13,cy-8,cx+13,cy+16], fill=skin, outline=dark_s, width=2)
    # Hump back
    d.ellipse([cx-5,cy-14,cx+14,cy+2], fill=skin, outline=dark_s)
    # Large head
    d.ellipse([cx-11,cy-24,cx+11,cy-6], fill=skin, outline=dark_s, width=2)
    # Nose (huge)
    d.ellipse([cx-3,cy-17,cx+5,cy-12], fill=shade((60,130,80),1.2)+(255,))
    d.ellipse([cx-4,cy-16,cx-1,cy-14], fill=(20,50,25,200))
    d.ellipse([cx+2,cy-16,cx+5,cy-14], fill=(20,50,25,200))
    # Ears
    d.ellipse([cx-14,cy-22,cx-9,cy-14], fill=skin, outline=dark_s)
    d.ellipse([cx+9,cy-22,cx+14,cy-14], fill=skin, outline=dark_s)
    # Small eyes
    d.ellipse([cx-7,cy-22,cx-2,cy-18], fill=(255,160,40,255), outline=dark_s)
    d.ellipse([cx+2,cy-22,cx+7,cy-18], fill=(255,160,40,255), outline=dark_s)
    d.ellipse([cx-6,cy-22,cx-3,cy-19], fill=(200,60,20,255))
    d.ellipse([cx+3,cy-22,cx+6,cy-19], fill=(200,60,20,255))
    # Wide mouth
    d.arc([cx-8,cy-14,cx+8,cy-8], 10, 170, fill=dark_s, width=2)
    # Club / tree trunk weapon
    d.line([(cx+12,cy-8),(cx+16,cy+14)], fill=(90,60,25,255), width=5)
    d.ellipse([cx+10,cy-14,cx+20,cy-6], fill=(110,80,40,255), outline=(70,50,20,255))
    # Nails/spikes on club
    for nail_y in [cy-11,cy-8,cy-5]:
        d.line([(cx+10,nail_y),(cx+8,nail_y-2)], fill=(180,170,160,255), width=1)
    # Arms
    d.line([(cx-13,cy-4),(cx-18,cy+6)], fill=skin, width=5)
    d.line([(cx+13,cy-4),(cx+17,cy+4)], fill=skin, width=5)
    # Legs
    d.line([(cx-6,cy+16),(cx-8,cy+24)], fill=skin, width=6)
    d.line([(cx+6,cy+16),(cx+8,cy+24)], fill=skin, width=6)
    d.ellipse([cx-12,cy+22,cx-4,cy+28], fill=(40,80,50,255))
    d.ellipse([cx+4,cy+22,cx+12,cy+28], fill=(40,80,50,255))
    # Mossy patches
    for mx2,my2 in [(cx-8,cy+2),(cx+6,cy-2),(cx,cy+10)]:
        d.ellipse([mx2-3,my2-2,mx2+3,my2+2], fill=(40,120,40,120))
    return img

def make_demon():
    W,H = 32,32
    img, d = new(W,H)
    cx,cy = 16,18
    skin = (200,40,40,255)
    dark_s = (120,10,10,255)
    wing_col = (140,20,20,200)
    # Shadow
    d.ellipse([cx-10,cy+8,cx+10,cy+13], fill=(0,0,0,60))
    # Wings (behind body)
    d.polygon([(cx-2,cy-8),(cx-18,cy-18),(cx-14,cy+4)], fill=wing_col, outline=dark_s)
    d.polygon([(cx+2,cy-8),(cx+18,cy-18),(cx+14,cy+4)], fill=wing_col, outline=dark_s)
    # Wing membrane lines
    for t2 in [0.3,0.6]:
        wx2 = int((cx-2)+((-18)-(cx-2))*t2)
        wy2 = int((cy-8)+((-18)-(cy-8))*t2)
        wx3 = int((cx-14)+((-14)-(cx-14))*t2)
        wy3 = int((cy+4)+((4)-(cy+4))*t2)
        d.line([(wx2,cy-8+(wy2-(cy-8))),(wx3,cy+4+(wy3-(cy+4)))], fill=(100,10,10,150), width=1)
    # Body
    d.ellipse([cx-7,cy-6,cx+7,cy+10], fill=skin, outline=dark_s)
    # Head
    d.ellipse([cx-7,cy-16,cx+7,cy-3], fill=skin, outline=dark_s)
    # Horns
    d.polygon([(cx-5,cy-15),(cx-9,cy-22),(cx-2,cy-14)], fill=(80,10,10,255), outline=dark_s)
    d.polygon([(cx+5,cy-15),(cx+9,cy-22),(cx+2,cy-14)], fill=(80,10,10,255), outline=dark_s)
    # Eyes (glowing)
    d.ellipse([cx-5,cy-13,cx-1,cy-10], fill=(255,255,0,255), outline=dark_s)
    d.ellipse([cx+1,cy-13,cx+5,cy-10], fill=(255,255,0,255), outline=dark_s)
    d.ellipse([cx-4,cy-13,cx-2,cy-11], fill=(255,50,0,255))
    d.ellipse([cx+2,cy-13,cx+4,cy-11], fill=(255,50,0,255))
    # Nose
    d.polygon([(cx-1,cy-10),(cx+1,cy-10),(cx,cy-8)], fill=dark_s)
    # Grin with fangs
    d.arc([cx-5,cy-9,cx+5,cy-6], 10, 170, fill=dark_s, width=1)
    d.polygon([(cx-3,cy-8),(cx-2,cy-6),(cx-1,cy-8)], fill=(240,230,220,255))
    d.polygon([(cx+3,cy-8),(cx+2,cy-6),(cx+1,cy-8)], fill=(240,230,220,255))
    # Tail
    d.line([(cx-6,cy+8),(cx-12,cy+12),(cx-14,cy+8)], fill=dark_s, width=2)
    d.polygon([(cx-15,cy+6),(cx-14,cy+8),(cx-12,cy+7)], fill=dark_s)
    # Claws
    d.line([(cx-7,cy+2),(cx-11,cy+5)], fill=skin, width=3)
    d.line([(cx+7,cy+2),(cx+11,cy+5)], fill=skin, width=3)
    d.polygon([(cx-12,cy+4),(cx-13,cy+6),(cx-10,cy+6)], fill=(80,10,10,255))
    d.polygon([(cx+12,cy+4),(cx+13,cy+6),(cx+10,cy+6)], fill=(80,10,10,255))
    return img

def make_golem():
    W,H = 52,52
    img, d = new(W,H)
    cx,cy = 26,32
    rock = (110,110,130,255)
    rock_d = (60,60,80,255)
    rock_l = (160,160,180,255)
    glue = (80,80,100,255)
    glow_col = (100,180,255,255)
    # Shadow (large)
    d.ellipse([cx-20,cy+15,cx+20,cy+24], fill=(0,0,0,80))
    # Main body (assembled rock chunks)
    # Torso
    d.ellipse([cx-14,cy-10,cx+14,cy+18], fill=rock, outline=rock_d, width=2)
    d.ellipse([cx-12,cy-8,cx+12,cy+14], fill=rock_l)  # light face
    # Rock seams
    d.arc([cx-12,cy-8,cx+12,cy+14], 20, 160, fill=glue, width=2)
    d.arc([cx-10,cy-2,cx+10,cy+14], 200, 340, fill=glue, width=1)
    # Shoulders (big rocks)
    d.ellipse([cx-22,cy-12,cx-6,cy+4], fill=rock, outline=rock_d, width=2)
    d.ellipse([cx+6,cy-12,cx+22,cy+4], fill=rock, outline=rock_d, width=2)
    # Head (block)
    d.rectangle([cx-10,cy-26,cx+10,cy-8], fill=rock, outline=rock_d, width=2)
    d.rectangle([cx-8,cy-24,cx+8,cy-10], fill=rock_l)
    # Head seam
    d.line([(cx-8,cy-17),(cx+8,cy-17)], fill=glue, width=2)
    # Eyes (magical glowing)
    d.ellipse([cx-8,cy-24,cx-2,cy-18], fill=(40,40,60,255), outline=rock_d)
    d.ellipse([cx+2,cy-24,cx+8,cy-18], fill=(40,40,60,255), outline=rock_d)
    for ex2,ey2 in [(cx-5,cy-21),(cx+5,cy-21)]:
        d.ellipse([ex2-3,ey2-3,ex2+3,ey2+3], fill=(60,140,220,200))
        d.ellipse([ex2-2,ey2-2,ex2+2,ey2+2], fill=(120,200,255,255))
        d.ellipse([ex2-1,ey2-1,ex2+1,ey2+1], fill=(220,240,255,255))
    # Crack lines on body
    for (x1,y1),(x2,y2) in [((cx-8,cy-4),(cx-12,cy+6)),((cx+6,cy),(cx+10,cy+8)),((cx-2,cy+2),(cx+4,cy+12))]:
        d.line([(x1,y1),(x2,y2)], fill=rock_d, width=1)
    # Arms (rock chunks)
    d.ellipse([cx-24,cy+2,cx-10,cy+14], fill=rock, outline=rock_d, width=1)  # fist L
    d.ellipse([cx+10,cy+2,cx+24,cy+14], fill=rock, outline=rock_d, width=1)  # fist R
    d.rectangle([cx-20,cy+4,cx-12,cy+12], fill=rock_l)
    d.rectangle([cx+12,cy+4,cx+20,cy+12], fill=rock_l)
    # Legs
    d.ellipse([cx-12,cy+16,cx-2,cy+32], fill=rock, outline=rock_d, width=2)
    d.ellipse([cx+2,cy+16,cx+12,cy+32], fill=rock, outline=rock_d, width=2)
    d.ellipse([cx-14,cy+28,cx-0,cy+38], fill=rock, outline=rock_d, width=1)  # feet
    d.ellipse([cx+0,cy+28,cx+14,cy+38], fill=rock, outline=rock_d, width=1)
    # Magic core (chest glow)
    d.ellipse([cx-5,cy-2,cx+5,cy+8], fill=(40,40,70,255), outline=rock_d)
    d.ellipse([cx-4,cy-1,cx+4,cy+7], fill=(80,140,220,200))
    d.ellipse([cx-2,cy+1,cx+2,cy+5], fill=(180,220,255,255))
    return img

def make_harpy():
    W,H = 36,32
    img, d = new(W,H)
    cx,cy = 18,20
    feather = (200,140,200,255)
    feather_d = (140,80,150,255)
    feather_l = (240,190,240,255)
    skin = (230,180,150,255)
    # Shadow
    d.ellipse([cx-12,cy+8,cx+12,cy+13], fill=(0,0,0,40))
    # Wings (large, spread)
    # Left wing
    wing_L = [(cx-2,cy-6),(cx-18,cy-14),(cx-22,cy-2),(cx-16,cy+6),(cx-6,cy+2)]
    d.polygon(wing_L, fill=feather, outline=feather_d)
    # Wing feather details L
    for i,t2 in enumerate([0.3,0.6,0.85]):
        px2 = int((cx-2)+((-22)-(cx-2))*t2)
        py2 = int((cy-6)+((-2)-(cy-6))*t2)
        d.line([(px2,py2),(px2-4+i,py2+5)], fill=feather_d, width=1)
    # Right wing
    wing_R = [(cx+2,cy-6),(cx+18,cy-14),(cx+22,cy-2),(cx+16,cy+6),(cx+6,cy+2)]
    d.polygon(wing_R, fill=feather, outline=feather_d)
    for i,t2 in enumerate([0.3,0.6,0.85]):
        px2 = int((cx+2)+((22)-(cx+2))*t2)
        py2 = int((cy-6)+((-2)-(cy-6))*t2)
        d.line([(px2,py2),(px2+4-i,py2+5)], fill=feather_d, width=1)
    # Body
    d.ellipse([cx-6,cy-6,cx+6,cy+8], fill=feather, outline=feather_d)
    # Head
    d.ellipse([cx-6,cy-16,cx+6,cy-5], fill=skin, outline=feather_d)
    # Hair/crest
    for i in range(3):
        hx = cx-4+i*4
        d.line([(hx,cy-16),(hx+i-1,cy-22)], fill=feather_d, width=2)
        d.ellipse([hx-1,cy-23,hx+1,cy-21], fill=feather_l)
    # Eyes
    d.ellipse([cx-4,cy-14,cx-1,cy-11], fill=(255,220,150,255), outline=feather_d)
    d.ellipse([cx+1,cy-14,cx+4,cy-11], fill=(255,220,150,255), outline=feather_d)
    d.ellipse([cx-3,cy-14,cx-2,cy-12], fill=(30,20,80,255))
    d.ellipse([cx+2,cy-14,cx+3,cy-12], fill=(30,20,80,255))
    # Beak
    d.polygon([(cx-2,cy-11),(cx+2,cy-11),(cx,cy-9)], fill=(220,180,40,255), outline=(160,120,20,255))
    # Talons
    d.line([(cx-4,cy+8),(cx-6,cy+13)], fill=skin, width=2)
    d.line([(cx+4,cy+8),(cx+6,cy+13)], fill=skin, width=2)
    for tx2,ty2 in [(cx-8,cy+13),(cx-5,cy+14),(cx+5,cy+13),(cx+8,cy+14)]:
        d.polygon([(tx2-1,ty2),(tx2+1,ty2),(tx2,ty2+3)], fill=(180,140,80,255))
    return img

# ─────────────────────────────────────────────────────────────────────
#  HERO  (44×52)
# ─────────────────────────────────────────────────────────────────────

def make_hero():
    W,H = 44,52
    img, d = new(W,H)
    cx,cy = 22,32
    armor = (60,80,160,255)         # blue steel
    armor_l = (100,130,210,255)     # highlight
    armor_d = (30,40,100,255)       # shadow
    GOLD2 = (220,190,50,255)
    skin = (220,175,130,255)
    cape_col = (180,30,30,255)
    cape_d = (110,10,10,255)

    # Shadow
    d.ellipse([cx-16,cy+16,cx+16,cy+22], fill=(0,0,0,70))

    # Cape (behind everything)
    cape_pts = [(cx-8,cy-14),(cx+8,cy-14),(cx+12,cy+16),(cx-12,cy+16)]
    d.polygon(cape_pts, fill=cape_col, outline=cape_d)
    # Cape fold lines
    for i in range(3):
        lx = cx-6+i*4
        d.line([(lx,cy-12),(lx-1+i,cy+14)], fill=cape_d, width=1)

    # Legs
    d.rectangle([cx-8,cy+6,cx-2,cy+18], fill=armor, outline=armor_d)
    d.rectangle([cx+2,cy+6,cx+8,cy+18], fill=armor, outline=armor_d)
    # Greaves (leg armor)
    d.rectangle([cx-8,cy+10,cx-2,cy+16], fill=armor_l, outline=armor_d)
    d.rectangle([cx+2,cy+10,cx+8,cy+16], fill=armor_l, outline=armor_d)
    # Boots
    d.rectangle([cx-9,cy+16,cx-1,cy+20], fill=armor_d, outline=(10,10,30,255))
    d.rectangle([cx+1,cy+16,cx+9,cy+20], fill=armor_d, outline=(10,10,30,255))

    # Torso / breastplate
    d.rectangle([cx-9,cy-6,cx+9,cy+8], fill=armor, outline=armor_d, width=2)
    d.rectangle([cx-7,cy-4,cx+7,cy+6], fill=armor_l)
    # Breastplate center line
    d.line([(cx,cy-4),(cx,cy+6)], fill=armor_d, width=1)
    # Pauldrons (shoulder guards)
    d.ellipse([cx-14,cy-8,cx-4,cy+0], fill=armor, outline=armor_d, width=2)
    d.ellipse([cx+4,cy-8,cx+14,cy+0], fill=armor, outline=armor_d, width=2)
    # Gold trim on armor
    d.line([(cx-7,cy-4),(cx+7,cy-4)], fill=GOLD2, width=1)
    d.line([(cx-7,cy+4),(cx+7,cy+4)], fill=GOLD2, width=1)

    # Head
    d.ellipse([cx-7,cy-22,cx+7,cy-8], fill=skin, outline=(160,120,80,255))
    # Helmet
    d.rectangle([cx-8,cy-24,cx+8,cy-16], fill=armor, outline=armor_d, width=2)
    d.ellipse([cx-8,cy-26,cx+8,cy-18], fill=armor, outline=armor_d, width=2)
    # Visor
    d.rectangle([cx-7,cy-22,cx+7,cy-18], fill=armor_d, outline=(10,10,30,255))
    # Helmet plume
    d.line([(cx,cy-26),(cx,cy-34)], fill=(180,30,30,255), width=3)
    d.ellipse([cx-3,cy-36,cx+3,cy-30], fill=(220,50,50,255))
    # Gold crown on helmet
    d.line([(cx-7,cy-25),(cx+7,cy-25)], fill=GOLD2, width=1)
    d.polygon([(cx-5,cy-26),(cx-3,cy-29),(cx-1,cy-26)], fill=GOLD2)
    d.polygon([(cx+1,cy-26),(cx+3,cy-29),(cx+5,cy-26)], fill=GOLD2)

    # Eyes (visible through visor gap)
    d.ellipse([cx-4,cy-22,cx-1,cy-19], fill=(255,255,200,255))
    d.ellipse([cx+1,cy-22,cx+4,cy-19], fill=(255,255,200,255))
    d.ellipse([cx-3,cy-22,cx-2,cy-20], fill=(30,80,200,255))
    d.ellipse([cx+2,cy-22,cx+3,cy-20], fill=(30,80,200,255))

    # Sword arm (right, raised)
    d.line([(cx+9,cy-4),(cx+16,cy-14)], fill=armor_l, width=4)
    # Sword
    d.line([(cx+16,cy-14),(cx+22,cy-28)], fill=(200,210,230,255), width=3)  # blade
    d.line([(cx+17,cy-14),(cx+23,cy-28)], fill=(240,240,255,255), width=1)  # shine
    d.rectangle([cx+14,cy-16,cx+20,cy-14], fill=GOLD2, outline=(160,130,20,255))  # crossguard
    d.ellipse([cx+16,cy-18,cx+20,cy-14], fill=(160,120,20,255))  # pommel
    # Sword glow
    for r in range(5,0,-1):
        d.ellipse([cx+19-r,cy-27-r,cx+23+r,cy-25+r], fill=(200,220,255,max(0,20-r*3)))

    # Shield arm (left, defensive)
    d.line([(cx-9,cy-4),(cx-16,cy+4)], fill=armor_l, width=4)
    shield_pts = [(cx-20,cy-4),(cx-14,cy-10),(cx-10,cy+2),(cx-14,cy+8),(cx-20,cy+4)]
    d.polygon(shield_pts, fill=armor, outline=armor_d, width=2)
    d.polygon(shield_pts, fill=None, outline=armor_l, width=1)
    # Shield emblem (gold cross)
    d.line([(cx-18,cy),(cx-12,cy)], fill=GOLD2, width=2)
    d.line([(cx-15,cy-4),(cx-15,cy+4)], fill=GOLD2, width=2)

    return img

# ─────────────────────────────────────────────────────────────────────
#  GENERATE ALL
# ─────────────────────────────────────────────────────────────────────
print("\n🎨 Generating Kingdom Rush pixel art sprites...\n")

# Terrain
print("── Terrain ──────────────────────")
save(make_grass(),       "terrain/grass.png")
save(make_cobblestone(), "terrain/cobblestone.png")

# UI
print("── UI Icons ─────────────────────")
save(make_gold_icon(),  "ui/gold_icon.png")
save(make_heart_icon(), "ui/heart_icon.png")

# Towers
print("── Towers ───────────────────────")
for lv in range(1,4):
    save(make_archer_lv(lv),    f"towers/archer_lv{lv}.png")
    save(make_mage_lv(lv),      f"towers/mage_lv{lv}.png")
    save(make_artillery_lv(lv), f"towers/artillery_lv{lv}.png")
    save(make_ice_lv(lv),       f"towers/ice_lv{lv}.png")
    save(make_barracks_lv(lv),  f"towers/barracks_lv{lv}.png")

# Enemies
print("── Enemies ──────────────────────")
save(make_goblin(), "enemies/goblin.png")
save(make_orc(),    "enemies/orc.png")
save(make_troll(),  "enemies/troll.png")
save(make_demon(),  "enemies/demon.png")
save(make_golem(),  "enemies/golem.png")
save(make_harpy(),  "enemies/harpy.png")

# Hero
print("── Hero ─────────────────────────")
save(make_hero(), "hero/hero.png")

# Count
total = sum(len(os.listdir(f"{BASE}/{d}")) for d in ["towers","enemies","hero","ui","terrain"])
print(f"\n✅ Done! {total} sprites written to {BASE}/")
