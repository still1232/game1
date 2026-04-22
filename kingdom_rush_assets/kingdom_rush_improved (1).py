import pygame
import sys
import math
import random
import time
from enum import Enum

pygame.init()
try:
    pygame.mixer.init()
except:
    pass

# ═══════════════════════════════════════════════════════════════
#  SPRITE / ASSET LOADER
#  ───────────────────────────────────────────────────────────────
#  Đặt ảnh vào thư mục  assets/  cạnh file .py này.
#  Cấu trúc thư mục:
#
#  assets/
#    towers/
#      archer_lv1.png   archer_lv2.png   archer_lv3.png
#      mage_lv1.png     mage_lv2.png     mage_lv3.png
#      artillery_lv1.png ... lv3.png
#      ice_lv1.png      ... lv3.png
#      barracks_lv1.png ... lv3.png
#    enemies/
#      goblin.png   orc.png   troll.png
#      demon.png    golem.png  harpy.png
#    hero/
#      hero.png
#    ui/
#      panel_bg.png   (320 × 720, optional wood texture)
#      gold_icon.png  (32 × 32)
#      heart_icon.png (32 × 32)
#      btn_normal.png btn_hover.png  (optional)
#    terrain/
#      grass.png        (40 × 40 tile, optional)
#      cobblestone.png  (40 × 40 tile, optional)
#
#  Mọi ảnh đều có fallback vẽ bằng code nên KHÔNG BẮT BUỘC.
#  Kích thước đề nghị: tower 64×80px, enemy 32×32px, hero 40×48px.
#  Định dạng PNG có kênh alpha (trong suốt).
# ═══════════════════════════════════════════════════════════════

import os as _os
_ASSET_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "assets")

def _load_img(rel_path, size=None):
    """Load an image from assets/. Returns scaled Surface or None if not found."""
    full = _os.path.join(_ASSET_DIR, rel_path)
    if not _os.path.isfile(full):
        return None
    try:
        img = pygame.image.load(full).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        return None

# Pre-load all sprites into dictionaries (None = use procedural fallback)
TOWER_SPRITES  = {}   # key: "archer_lv1", "mage_lv2", ...
ENEMY_SPRITES  = {}   # key: "goblin", "orc", ...
HERO_SPRITE    = None
UI_SPRITES     = {}   # key: "panel_bg", "gold_icon", "heart_icon"
TERRAIN_SPRITES = {}  # key: "grass", "cobblestone"

def load_all_assets():
    """Call once after pygame.display.set_mode()."""
    global HERO_SPRITE
    # Towers
    for ttype in ("archer", "mage", "artillery", "ice", "barracks"):
        for lv in (1, 2, 3):
            key = f"{ttype}_lv{lv}"
            TOWER_SPRITES[key] = _load_img(f"towers/{key}.png", (64, 80))
    # Enemies
    for etype in ("goblin", "orc", "troll", "demon", "golem", "harpy"):
        sz = {"goblin":(28,28),"orc":(36,36),"troll":(44,44),
              "demon":(32,32),"golem":(52,52),"harpy":(36,32)}.get(etype, (32,32))
        ENEMY_SPRITES[etype] = _load_img(f"enemies/{etype}.png", sz)
    # Hero
    HERO_SPRITE = _load_img("hero/hero.png", (44, 52))
    # UI
    for key, fname, sz in [
        ("panel_bg",   "ui/panel_bg.png",   (320, 720)),
        ("gold_icon",  "ui/gold_icon.png",  (22, 22)),
        ("heart_icon", "ui/heart_icon.png", (22, 22)),
        ("btn_normal", "ui/btn_normal.png", None),
        ("btn_hover",  "ui/btn_hover.png",  None),
    ]:
        UI_SPRITES[key] = _load_img(fname, sz)
    # Terrain tiles
    TERRAIN_SPRITES["grass"]       = _load_img("terrain/grass.png",       (40, 40))
    TERRAIN_SPRITES["cobblestone"] = _load_img("terrain/cobblestone.png", (40, 40))

    loaded = sum(1 for v in list(TOWER_SPRITES.values())
                            + list(ENEMY_SPRITES.values())
                            + list(UI_SPRITES.values())
                            + list(TERRAIN_SPRITES.values())
                 if v is not None) + (1 if HERO_SPRITE else 0)
    print(f"[Assets] Loaded {loaded} sprite(s). Missing = procedural fallback.")

# ─────────────────────────────────────────────────────────────────
#  SPRITE DRAW HELPERS
# ─────────────────────────────────────────────────────────────────
def blit_centered(surf, img, cx, cy, flip_x=False):
    """Blit img centered on (cx, cy), optionally flipped."""
    if flip_x:
        img = pygame.transform.flip(img, True, False)
    surf.blit(img, (cx - img.get_width()//2, cy - img.get_height()//2))

# ─────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────
SCREEN_W, SCREEN_H = 1280, 720
FPS = 60
TILE = 40

# Color palette – earthy fantasy tones
C_BG         = (18, 28, 18)
C_GRASS1     = (34, 68, 34)
C_GRASS2     = (42, 82, 42)
C_PATH       = (140, 110, 70)
C_PATH_EDGE  = (110, 85, 50)
C_UI_BG      = (12, 18, 12)
C_UI_BORDER  = (80, 140, 60)
C_UI_GOLD    = (240, 200, 60)
C_UI_RED     = (220, 60, 60)
C_UI_BLUE    = (60, 120, 220)
C_UI_GREEN   = (60, 200, 100)
C_UI_PURPLE  = (160, 60, 200)
C_WHITE      = (255, 255, 255)
C_BLACK      = (0, 0, 0)
C_SHADOW     = (0, 0, 0, 120)

# Extended palette for improved visuals
C_SKY_TOP    = (28, 52, 88)
C_SKY_BOT    = (22, 48, 30)
C_MTN_FAR    = (38, 58, 48)
C_MTN_NEAR   = (26, 44, 26)
C_STONE1     = (140, 128, 108)
C_STONE2     = (118, 106, 88)
C_STONE3     = (96,  86, 70)
C_MORTAR     = (78,  70, 58)
C_WOOD_DARK  = (55,  35, 18)
C_WOOD_MID   = (80,  52, 28)
C_WOOD_LIGHT = (110, 74, 40)
C_PANEL_BG   = (28,  20, 12)
C_PANEL_WOOD = (48,  32, 16)

# Game area
GAME_W = 960
GAME_H = SCREEN_H
PANEL_X = GAME_W
PANEL_W = SCREEN_W - GAME_W

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Kingdom Rush – Tower Defense")
clock = pygame.time.Clock()
load_all_assets()   # load sprites (falls back gracefully if missing)

# ─────────────────────────────────────────
# FONTS
# ─────────────────────────────────────────
def load_font(size, bold=False):
    try:
        return pygame.font.SysFont("Georgia", size, bold=bold)
    except:
        return pygame.font.Font(None, size)

F_TITLE  = load_font(36, True)
F_LARGE  = load_font(26, True)
F_MED    = load_font(20, True)
F_SMALL  = load_font(16)
F_TINY   = load_font(13)

# ─────────────────────────────────────────
# DRAW HELPERS
# ─────────────────────────────────────────
def draw_rounded_rect(surf, color, rect, radius=8, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)

def draw_glow(surf, color, pos, radius, alpha=80):
    glow = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    for r in range(radius, 0, -4):
        a = int(alpha * (1 - r/radius))
        pygame.draw.circle(glow, (*color[:3], a), (radius, radius), r)
    surf.blit(glow, (pos[0]-radius, pos[1]-radius))

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))

def draw_health_bar(surf, x, y, w, h, ratio, col_full=(60,220,80), col_empty=(180,30,30)):
    pygame.draw.rect(surf, (20, 20, 20), (x, y, w, h), border_radius=2)
    if ratio > 0:
        color = lerp_color(col_empty, col_full, ratio)
        pygame.draw.rect(surf, color, (x, y, int(w*ratio), h), border_radius=2)
    pygame.draw.rect(surf, (0,0,0), (x, y, w, h), 1, border_radius=2)

# Cached vignette surface
_vignette_surf = None
def draw_vignette(surf, w, h, alpha=90):
    global _vignette_surf
    if _vignette_surf is None or _vignette_surf.get_size() != (w, h):
        _vignette_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cx, cy = w//2, h//2
        max_r = math.hypot(cx, cy)
        for r in range(int(max_r), 0, -8):
            a = int(alpha * (1 - r/max_r) ** 1.8)
            pygame.draw.ellipse(_vignette_surf, (0,0,0,a),
                (cx-r, cy-int(r*h/w), r*2, int(r*2*h/w)))
    surf.blit(_vignette_surf, (0, 0))

# ─────────────────────────────────────────
# PARTICLE SYSTEM
# ─────────────────────────────────────────
class Particle:
    def __init__(self, x, y, vx, vy, color, size, life, fade=True, gravity=0):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.color = color
        self.size = size
        self.life = self.max_life = life
        self.fade = fade
        self.gravity = gravity

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.life -= dt
        return self.life > 0

    def draw(self, surf):
        ratio = self.life / self.max_life
        alpha = int(255 * ratio) if self.fade else 255
        s = max(1, int(self.size * ratio))
        col = (*self.color[:3], alpha)
        ps = pygame.Surface((s*2, s*2), pygame.SRCALPHA)
        pygame.draw.circle(ps, col, (s, s), s)
        surf.blit(ps, (int(self.x)-s, int(self.y)-s))

particles = []

def spawn_particles(x, y, color, count=8, speed=60, size=4, life=0.6, gravity=80):
    for _ in range(count):
        angle = random.uniform(0, math.tau)
        spd = random.uniform(speed*0.5, speed)
        particles.append(Particle(x, y,
            math.cos(angle)*spd, math.sin(angle)*spd,
            color, size, life + random.uniform(-0.1, 0.1),
            gravity=gravity))

def spawn_explosion(x, y, color=(255,140,40), count=20):
    spawn_particles(x, y, color, count, speed=120, size=6, life=0.9, gravity=120)
    spawn_particles(x, y, (255,220,100), count//2, speed=60, size=3, life=0.5, gravity=40)

# ─────────────────────────────────────────
# FLOATING TEXT
# ─────────────────────────────────────────
class FloatText:
    def __init__(self, x, y, text, color, size=16, life=1.2):
        self.x, self.y = float(x), float(y)
        self.text = text
        self.color = color
        self.font = load_font(size, True)
        self.life = self.max_life = life

    def update(self, dt):
        self.y -= 40 * dt
        self.life -= dt
        return self.life > 0

    def draw(self, surf):
        ratio = self.life / self.max_life
        alpha = int(255 * min(ratio * 3, 1))
        rendered = self.font.render(self.text, True, self.color)
        rendered.set_alpha(alpha)
        surf.blit(rendered, (int(self.x) - rendered.get_width()//2, int(self.y)))

float_texts = []

# ─────────────────────────────────────────
# MAP & PATH
# ─────────────────────────────────────────
# Waypoints for enemy path (pixel coords)
WAYPOINTS = [
    (-40, 360),
    (80, 360), (80, 200),
    (240, 200), (240, 520),
    (440, 520), (440, 240),
    (640, 240), (640, 480),
    (800, 480), (800, 280),
    (960, 280),
]

# Build-able tile positions (not on path)
BUILDABLE = []
_path_cells = set()
for i in range(len(WAYPOINTS)-1):
    x1,y1 = WAYPOINTS[i]; x2,y2 = WAYPOINTS[i+1]
    steps = max(abs(x2-x1), abs(y2-y1)) // TILE + 2
    for s in range(steps+1):
        t = s/max(steps,1)
        cx = int((x1 + (x2-x1)*t)//TILE)
        cy = int((y1 + (y2-y1)*t)//TILE)
        for dx in range(-1,2):
            for dy in range(-1,2):
                _path_cells.add((cx+dx, cy+dy))

for col in range(GAME_W//TILE):
    for row in range(GAME_H//TILE):
        if (col, row) not in _path_cells:
            BUILDABLE.append((col*TILE + TILE//2, row*TILE + TILE//2))

# ─────────────────────────────────────────
# DRAW MAP  (improved)
# ─────────────────────────────────────────
_map_static_cache = None   # pre-rendered static layer

def _draw_tree(surf, tx, ty, rng):
    """Draw a detailed tree at position."""
    h_var = rng.randint(-6, 6)
    # Ground shadow
    pygame.draw.ellipse(surf, (10, 22, 10), (tx-18, ty+14, 36, 10))
    # Trunk
    trunk_w = rng.randint(5, 8)
    pygame.draw.rect(surf, (70, 45, 18), (tx-trunk_w//2, ty, trunk_w, 22))
    pygame.draw.rect(surf, (90, 60, 28), (tx-trunk_w//2+1, ty+2, trunk_w-2, 18))
    # Dark base canopy
    pygame.draw.circle(surf, (18, 65, 18), (tx, ty-4+h_var), 24)
    # Mid canopy
    pygame.draw.circle(surf, (24, 92, 24), (tx-5, ty-12+h_var), 18)
    pygame.draw.circle(surf, (24, 92, 24), (tx+5, ty-12+h_var), 18)
    # Bright canopy
    pygame.draw.circle(surf, (38, 120, 38), (tx-4, ty-14+h_var), 14)
    pygame.draw.circle(surf, (38, 120, 38), (tx+4, ty-14+h_var), 14)
    # Top highlight
    pygame.draw.circle(surf, (58, 148, 50), (tx, ty-20+h_var), 10)
    pygame.draw.circle(surf, (78, 168, 65), (tx-2, ty-22+h_var), 6)


def _build_static_map(surf):
    """Build the non-animated map layer once."""
    rng = random.Random(77)   # fixed seed → deterministic

    # ── Sky gradient ──────────────────────────────────────────────
    for row in range(SCREEN_H):
        t = row / SCREEN_H
        r = int(C_SKY_TOP[0] + (C_SKY_BOT[0]-C_SKY_TOP[0])*t)
        g = int(C_SKY_TOP[1] + (C_SKY_BOT[1]-C_SKY_TOP[1])*t)
        b = int(C_SKY_TOP[2] + (C_SKY_BOT[2]-C_SKY_TOP[2])*t)
        pygame.draw.line(surf, (r, g, b), (0, row), (GAME_W, row))

    # ── Far mountain silhouette ────────────────────────────────────
    pts_far = [(0, SCREEN_H)]
    x = 0
    while x <= GAME_W:
        h = int(90 + 70*math.sin(x*0.008) + 50*math.sin(x*0.021 + 1.3))
        pts_far.append((x, SCREEN_H//2 - h))
        x += 18
    pts_far.append((GAME_W, SCREEN_H))
    pygame.draw.polygon(surf, C_MTN_FAR, pts_far)

    # ── Near hill silhouette ───────────────────────────────────────
    pts_near = [(0, SCREEN_H)]
    x = 0
    while x <= GAME_W:
        h = int(50 + 40*math.sin(x*0.012 + 0.5) + 30*math.sin(x*0.033 + 2.1))
        pts_near.append((x, SCREEN_H//2 + 30 - h))
        x += 12
    pts_near.append((GAME_W, SCREEN_H))
    pygame.draw.polygon(surf, C_MTN_NEAR, pts_near)

    # ── Grass tiles ───────────────────────────────────────────────
    for col in range(GAME_W//TILE + 1):
        for row2 in range(SCREEN_H//TILE + 1):
            color = C_GRASS1 if (col+row2)%2==0 else C_GRASS2
            pygame.draw.rect(surf, color, (col*TILE, row2*TILE, TILE, TILE))
    # Subtle grass blade tufts
    for _ in range(260):
        gx = rng.randint(0, GAME_W-1)
        gy = rng.randint(0, SCREEN_H-1)
        bright = rng.randint(8, 22)
        col2 = (C_GRASS2[0]+bright, C_GRASS2[1]+bright, C_GRASS2[2])
        pygame.draw.line(surf, col2, (gx, gy), (gx+rng.randint(-2,2), gy-rng.randint(3,7)), 1)
    # Small wildflowers
    for _ in range(80):
        fx = rng.randint(0, GAME_W-1)
        fy = rng.randint(0, SCREEN_H-1)
        fc = rng.choice([(220,200,80),(200,200,240),(255,180,160)])
        pygame.draw.circle(surf, fc, (fx, fy), 2)

    # ── Cobblestone path base (border/mortar) ─────────────────────
    for i in range(len(WAYPOINTS)-1):
        x1,y1 = WAYPOINTS[i]; x2,y2 = WAYPOINTS[i+1]
        pygame.draw.line(surf, (78, 62, 44), (x1,y1), (x2,y2), 56)
    for wp in WAYPOINTS[1:-1]:
        pygame.draw.circle(surf, (78, 62, 44), wp, 30)
    # Slightly lighter inner path base
    for i in range(len(WAYPOINTS)-1):
        x1,y1 = WAYPOINTS[i]; x2,y2 = WAYPOINTS[i+1]
        pygame.draw.line(surf, (110, 90, 68), (x1,y1), (x2,y2), 46)
    for wp in WAYPOINTS[1:-1]:
        pygame.draw.circle(surf, (110, 90, 68), wp, 24)

    # ── Individual cobblestones ───────────────────────────────────
    for i in range(len(WAYPOINTS)-1):
        x1,y1 = WAYPOINTS[i]; x2,y2 = WAYPOINTS[i+1]
        seg_len = math.hypot(x2-x1, y2-y1)
        if seg_len < 1: continue
        dx = (x2-x1)/seg_len; dy = (y2-y1)/seg_len
        px_n = -dy; py_n = dx   # perpendicular

        steps = max(1, int(seg_len / 13))
        for s in range(steps):
            t = (s + 0.5) / steps
            cx = x1 + dx*seg_len*t
            cy = y1 + dy*seg_len*t
            for row3 in range(-1, 2):
                stagger = (7 * (s % 2)) * (1 if row3 != 0 else 0)
                ox = px_n*row3*14 + stagger*dx + rng.uniform(-2, 2)
                oy = py_n*row3*14 + stagger*dy + rng.uniform(-2, 2)
                sw = rng.randint(10, 16); sh = rng.randint(7, 11)
                shade = rng.randint(0, 28)
                v = 122 + shade
                if rng.random() < 0.11:
                    sc = (v-22, v-5, v-32)        # mossy
                elif rng.random() < 0.08:
                    sc = (v+18, v+14, v+8)         # pale limestone
                else:
                    sc = (v, v-10, v-26)           # standard
                sxp = int(cx+ox-sw//2); syp = int(cy+oy-sh//2)
                # shadow
                pygame.draw.rect(surf, tuple(max(0,c-42) for c in sc),
                    (sxp+1, syp+1, sw, sh), border_radius=2)
                # stone body
                pygame.draw.rect(surf, sc, (sxp, syp, sw, sh), border_radius=2)
                # highlight edge
                hl = tuple(min(255,c+44) for c in sc)
                pygame.draw.line(surf, hl, (sxp+1,syp+1), (sxp+sw-3,syp+1), 1)

    # Junction cobblestones
    for wp in WAYPOINTS[1:-1]:
        wx, wy = wp
        for _ in range(18):
            ox = rng.uniform(-20, 20); oy = rng.uniform(-20, 20)
            sw = rng.randint(10, 15); sh = rng.randint(7, 11)
            v = 122 + rng.randint(0, 28)
            sc = (v, v-10, v-26)
            sxp = int(wx+ox-sw//2); syp = int(wy+oy-sh//2)
            pygame.draw.rect(surf, tuple(max(0,c-42) for c in sc),
                (sxp+1,syp+1,sw,sh), border_radius=2)
            pygame.draw.rect(surf, sc, (sxp,syp,sw,sh), border_radius=2)

    # ── Trees & rocks ─────────────────────────────────────────────
    tree_positions = [
        (55,75),(72,90),(185,555),(170,540),(315,115),(325,130),
        (375,398),(392,412),(498,76),(512,90),(558,598),(572,582),
        (698,98),(712,112),(758,598),(772,580),(855,118),(868,130),
        (898,558),(912,540),(40,300),(920,440),
    ]
    for tx, ty in tree_positions:
        _draw_tree(surf, tx, ty, rng)

    # Rocks
    for _ in range(18):
        rx = rng.randint(20, GAME_W-20)
        ry = rng.randint(20, SCREEN_H-20)
        rw = rng.randint(8, 18); rh = rng.randint(5, 12)
        rc = rng.randint(70, 110)
        pygame.draw.ellipse(surf, (rc-20, rc-20, rc-20), (rx+1,ry+1,rw,rh))
        pygame.draw.ellipse(surf, (rc, rc-5, rc-15), (rx, ry, rw, rh))
        pygame.draw.ellipse(surf, (rc+20, rc+15, rc+5), (rx+1, ry+1, rw-3, rh-3))


def draw_map(surf, tick):
    global _map_static_cache

    # Build static layer once
    if _map_static_cache is None:
        _map_static_cache = pygame.Surface((GAME_W, SCREEN_H))
        _build_static_map(_map_static_cache)

    surf.blit(_map_static_cache, (0, 0))

    # ── Animated grass shimmer ─────────────────────────────────────
    t = tick * 0.0008
    for i in range(22):
        gx = (i * 137 % GAME_W)
        gy = (i * 97 % SCREEN_H)
        bright = int(18 + 10*math.sin(t + i))
        col2 = (C_GRASS2[0]+bright, C_GRASS2[1]+bright, C_GRASS2[2])
        pygame.draw.circle(surf, col2, (gx, gy), 2)

    # ── Spawn flag ─────────────────────────────────────────────────
    sx, sy = WAYPOINTS[1][0], WAYPOINTS[1][1]
    # Flag pole
    pygame.draw.line(surf, (90, 60, 25), (sx-2, sy+2), (sx-2, sy-42), 4)
    pygame.draw.line(surf, (130, 90, 40), (sx-2, sy), (sx-2, sy-40), 3)
    # Flag
    flag_wave = math.sin(tick*0.05) * 3
    pts = [(sx-2, sy-40), (sx+22, sy-33+flag_wave), (sx-2, sy-26)]
    pygame.draw.polygon(surf, (180, 30, 30), pts)
    pygame.draw.polygon(surf, (220, 55, 55), [(sx-2, sy-40),(sx+20, sy-34+flag_wave),(sx-2, sy-28)])
    lbl = F_TINY.render("SPAWN", True, (255, 200, 180))
    surf.blit(lbl, (sx-lbl.get_width()//2, sy-60))

    # ── End portal (castle gate) ───────────────────────────────────
    ex, ey = WAYPOINTS[-1][0]-20, WAYPOINTS[-1][1]
    pulse = int(10*math.sin(tick*0.05))
    # Outer rings
    for r in range(4, 0, -1):
        alpha_col = (20+pulse*r//2, 70+pulse*r, 180+pulse)
        pygame.draw.circle(surf, alpha_col, (ex, ey), 20+r*5+pulse)
    # Inner portal
    pygame.draw.circle(surf, (60, 140, 240), (ex, ey), 20)
    pygame.draw.circle(surf, (120, 190, 255), (ex, ey), 13)
    pygame.draw.circle(surf, (200, 230, 255), (ex, ey), 7)
    pygame.draw.circle(surf, (255, 250, 255), (ex, ey), 3)
    lbl = F_TINY.render("BASE", True, (180, 220, 255))
    surf.blit(lbl, (ex-lbl.get_width()//2, ey-42))

# ─────────────────────────────────────────
# ENEMY DEFINITIONS
# ─────────────────────────────────────────
ENEMY_DEFS = {
    "goblin":  dict(hp=80,  speed=90,  armor=0,  magic_res=0,  gold=8,  color=(80,180,60),  size=11, reward_xp=5),
    "orc":     dict(hp=220, speed=55,  armor=10, magic_res=0,  gold=15, color=(140,100,40),  size=15, reward_xp=12),
    "troll":   dict(hp=500, speed=38,  armor=20, magic_res=5,  gold=30, color=(60,120,80),   size=18, reward_xp=25),
    "demon":   dict(hp=350, speed=70,  armor=5,  magic_res=20, gold=25, color=(200,50,50),   size=13, reward_xp=20),
    "golem":   dict(hp=900, speed=28,  armor=30, magic_res=10, gold=50, color=(120,120,140),  size=22, reward_xp=50),
    "harpy":   dict(hp=160, speed=100, armor=0,  magic_res=0,  gold=12, color=(220,140,200),  size=10, reward_xp=10, flying=True),
}

class Enemy:
    def __init__(self, etype, path_start_offset=0):
        d = ENEMY_DEFS[etype]
        self.etype = etype
        self.max_hp = d["hp"]
        self.hp = d["hp"]
        self.speed = d["speed"]
        self.armor = d["armor"]
        self.magic_res = d["magic_res"]
        self.gold = d["gold"]
        self.color = d["color"]
        self.size = d["size"]
        self.reward_xp = d["reward_xp"]
        self.flying = d.get("flying", False)
        self.path_index = 0
        self.x = float(WAYPOINTS[0][0]) - path_start_offset
        self.y = float(WAYPOINTS[0][1])
        self.alive = True
        self.reached_end = False
        self.slowed = 0.0  # slow duration remaining
        self.slow_factor = 1.0
        self.stunned = 0.0
        self.blocked_by = None  # soldier blocking
        self.anim_tick = random.randint(0, 100)
        self.wobble = random.uniform(-2, 2)
        self.shadow_alpha = 80

    @property
    def progress(self):
        return self.path_index + (self._sub_progress() if self.path_index < len(WAYPOINTS)-1 else 1)

    def _sub_progress(self):
        if self.path_index >= len(WAYPOINTS)-1:
            return 1.0
        tx, ty = WAYPOINTS[self.path_index+1]
        dist = math.hypot(tx-self.x, ty-self.y)
        seg_len = math.hypot(tx-WAYPOINTS[self.path_index][0], ty-WAYPOINTS[self.path_index][1])
        return 1 - dist/max(seg_len, 1)

    def update(self, dt):
        self.anim_tick += dt * 60
        if self.slowed > 0:
            self.slowed -= dt
            self.slow_factor = 0.45
        else:
            self.slow_factor = 1.0
        if self.stunned > 0:
            self.stunned -= dt
            return

        if self.blocked_by and self.blocked_by.alive:
            return  # blocked by soldier

        if self.path_index >= len(WAYPOINTS)-1:
            self.reached_end = True
            return

        tx, ty = WAYPOINTS[self.path_index+1]
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)
        move = self.speed * self.slow_factor * dt

        if dist <= move:
            self.x, self.y = float(tx), float(ty)
            self.path_index += 1
        else:
            self.x += dx/dist * move
            self.y += dy/dist * move

    def take_damage(self, dmg, dtype="physical"):
        if dtype == "physical":
            effective = max(1, dmg - self.armor)
        elif dtype == "magic":
            effective = max(1, dmg - self.magic_res)
        else:  # true
            effective = dmg
        self.hp -= effective
        if self.hp <= 0:
            self.alive = False
        return effective

    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        s = self.size
        bob = math.sin(self.anim_tick * 0.15) * 2 if not self.blocked_by else 0
        by = int(y + bob)
        walk = math.sin(self.anim_tick * 0.18) * 1.5

        # Shadow
        shadow_s = pygame.Surface((s*4, s), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_s, (0,0,0,55), (0,0,s*4,s))
        surf.blit(shadow_s, (x-s*2, by+s-2))

        # Slow effect aura
        if self.slowed > 0:
            draw_glow(surf, (80, 160, 255), (x, by), s+8, 55)

        # Low-HP tint
        body_color = self.color
        if self.hp < self.max_hp * 0.3:
            body_color = lerp_color(self.color, (220,30,30), 0.55)

        # ── Use sprite if available ──────────────────────────────
        spr = ENEMY_SPRITES.get(self.etype)
        if spr:
            flip = False
            if self.path_index < len(WAYPOINTS)-1:
                tx2, _ = WAYPOINTS[self.path_index+1]
                flip = tx2 < self.x
            blit_centered(surf, spr, x, by - s//2, flip_x=flip)
            # HP bar
            bar_w = s*2+10
            draw_health_bar(surf, x-bar_w//2, by-s-13, bar_w, 5, self.hp/self.max_hp)
            if self.flying:
                lbl = F_TINY.render("✦", True, (220,220,100))
                surf.blit(lbl, (x-4, by-s-26))
            return   # skip procedural drawing

        if self.etype == "goblin":
            # ── Goblin ─────────────────────────────────────────
            # Legs
            pygame.draw.line(surf, (60, 140, 45), (x-3, by+4), (x-4+int(walk), by+12), 3)
            pygame.draw.line(surf, (60, 140, 45), (x+3, by+4), (x+4-int(walk), by+12), 3)
            # Body
            pygame.draw.circle(surf, (0,0,0), (x+1, by+1), s)
            pygame.draw.ellipse(surf, body_color, (x-s, by-s//2, s*2, int(s*1.6)))
            # Arms
            pygame.draw.line(surf, body_color, (x-s,  by-2), (x-s-5, by+6), 3)
            pygame.draw.line(surf, body_color, (x+s,  by-2), (x+s+5, by+6), 3)
            # Dagger
            pygame.draw.line(surf, (180,180,200), (x+s+5, by+4), (x+s+10, by-2), 2)
            # Head
            pygame.draw.circle(surf, (0,0,0),   (x+1, by-s-3+1), s-2)
            pygame.draw.circle(surf, body_color, (x,   by-s-3),   s-2)
            # Big ears
            pygame.draw.ellipse(surf, body_color, (x-s-4, by-s-8, 7, 10))
            pygame.draw.ellipse(surf, body_color, (x+s-3, by-s-8, 7, 10))
            # Eyes
            pygame.draw.circle(surf, (255, 60, 60), (x-3, by-s-4), 3)
            pygame.draw.circle(surf, (255, 60, 60), (x+3, by-s-4), 3)
            pygame.draw.circle(surf, (30, 0, 0),    (x-3, by-s-4), 1)
            pygame.draw.circle(surf, (30, 0, 0),    (x+3, by-s-4), 1)
            # Teeth
            pygame.draw.line(surf, (240,235,200), (x-2, by-s+1), (x-2, by-s+4), 1)
            pygame.draw.line(surf, (240,235,200), (x+2, by-s+1), (x+2, by-s+4), 1)

        elif self.etype == "orc":
            # ── Orc ────────────────────────────────────────────
            # Legs (armored)
            for lx, lw in [(-4, int(-walk)), (4, int(walk))]:
                pygame.draw.line(surf, (95, 72, 28), (x+lx, by+4), (x+lx+lw, by+14), 5)
                pygame.draw.line(surf, (115, 88, 40), (x+lx, by+4), (x+lx+lw, by+13), 3)
            # Body with armor plate
            pygame.draw.circle(surf, (0,0,0), (x+1, by+1), s)
            pygame.draw.circle(surf, body_color, (x, by), s)
            pygame.draw.ellipse(surf, (80, 60, 22), (x-s+2, by-s//2, s*2-4, s))  # armor
            pygame.draw.ellipse(surf, (110, 85, 32), (x-s+4, by-s//2, s*2-8, s-2))
            # Arms holding axe
            pygame.draw.line(surf, body_color, (x-s, by-4), (x-s-8, by+8), 5)
            pygame.draw.line(surf, body_color, (x+s, by-4), (x+s+8, by+8), 5)
            # Battle axe
            pygame.draw.line(surf, (100, 80, 40), (x+s+6, by-4), (x+s+6, by+12), 3)
            pygame.draw.polygon(surf, (170, 170, 185), [
                (x+s+3, by-4),(x+s+10, by-4),(x+s+12, by+4),(x+s+3, by+2)])
            # Head
            pygame.draw.circle(surf, (0,0,0),   (x+1, by-s-2+1), s-1)
            pygame.draw.circle(surf, body_color, (x,   by-s-2),   s-1)
            # Helmet
            pygame.draw.rect(surf, (70, 55, 18), (x-s, by-s-8, s*2, 7), border_radius=2)
            pygame.draw.rect(surf, (95, 75, 28), (x-s+1, by-s-9, s*2-2, 7), border_radius=2)
            # Tusks
            pygame.draw.line(surf, (220, 210, 170), (x-3, by-s+2), (x-5, by-s+8), 2)
            pygame.draw.line(surf, (220, 210, 170), (x+3, by-s+2), (x+5, by-s+8), 2)
            # Eyes
            pygame.draw.circle(surf, (38, 28, 8), (x-3, by-s-3), 3)
            pygame.draw.circle(surf, (38, 28, 8), (x+3, by-s-3), 3)
            pygame.draw.circle(surf, (220, 60, 0), (x-3, by-s-3), 2)
            pygame.draw.circle(surf, (220, 60, 0), (x+3, by-s-3), 2)

        elif self.etype == "troll":
            # ── Troll ──────────────────────────────────────────
            s2 = s + 2
            # Legs (heavy, lumbering)
            for lx, lw in [(-6, int(-walk*0.6)), (6, int(walk*0.6))]:
                pygame.draw.line(surf, (42, 95, 58), (x+lx, by+6), (x+lx+lw, by+18), 8)
                pygame.draw.line(surf, (55, 115, 72), (x+lx, by+6), (x+lx+lw, by+17), 5)
            # Body
            pygame.draw.circle(surf, (0,0,0), (x+1, by+2), s2)
            pygame.draw.circle(surf, body_color, (x, by), s2)
            # Warts
            for wx, wy in [(-7,-3),(6,-6),(0,6),(-4,8),(8,2)]:
                pygame.draw.circle(surf, (30,78,40), (x+wx, by+wy), 3)
                pygame.draw.circle(surf, (48,100,58), (x+wx, by+wy), 2)
            # Arms with club
            pygame.draw.line(surf, body_color, (x-s2, by), (x-s2-10, by+10), 7)
            pygame.draw.line(surf, body_color, (x+s2, by), (x+s2+10, by+10), 7)
            # Club
            pygame.draw.line(surf, (70, 48, 20), (x+s2+8, by-6), (x+s2+14, by+14), 4)
            pygame.draw.ellipse(surf, (90, 62, 28), (x+s2+6, by+8, 14, 10))
            # Head
            pygame.draw.circle(surf, (0,0,0),   (x+1, by-s2-2+1), s2-2)
            pygame.draw.circle(surf, body_color, (x,   by-s2-2),   s2-2)
            # Brow ridge
            pygame.draw.rect(surf, (35, 90, 48), (x-s2+2, by-s2-6, s2*2-4, 4), border_radius=2)
            # Eyes
            pygame.draw.circle(surf, (255, 100, 0), (x-4, by-s2-3), 3)
            pygame.draw.circle(surf, (255, 100, 0), (x+4, by-s2-3), 3)
            pygame.draw.circle(surf, (0,0,0), (x-4, by-s2-3), 1)
            pygame.draw.circle(surf, (0,0,0), (x+4, by-s2-3), 1)

        elif self.etype == "demon":
            # ── Demon ──────────────────────────────────────────
            # Legs with fire trail
            for lx, lw in [(-4, int(-walk)), (4, int(walk))]:
                pygame.draw.line(surf, (160, 40, 30), (x+lx, by+4), (x+lx+lw, by+12), 4)
            # Wings
            pygame.draw.polygon(surf, (130, 28, 28), [
                (x-s*2, by+2), (x-s-2, by-s*2), (x, by-2)])
            pygame.draw.polygon(surf, (130, 28, 28), [
                (x+s*2, by+2), (x+s+2, by-s*2), (x, by-2)])
            pygame.draw.polygon(surf, (170, 40, 40), [
                (x-s*2+2, by+2), (x-s, by-s*2+4), (x, by-2)])
            pygame.draw.polygon(surf, (170, 40, 40), [
                (x+s*2-2, by+2), (x+s, by-s*2+4), (x, by-2)])
            # Body
            pygame.draw.circle(surf, (0,0,0), (x+1, by+1), s)
            pygame.draw.circle(surf, body_color, (x, by), s)
            # Fire glow on body
            draw_glow(surf, (255, 80, 20), (x, by), s+4, 40)
            # Head
            pygame.draw.circle(surf, (0,0,0),   (x+1, by-s-2+1), s-2)
            pygame.draw.circle(surf, body_color, (x,   by-s-2),   s-2)
            # Horns
            pygame.draw.polygon(surf, (140, 30, 30), [
                (x-5, by-s-4),(x-9, by-s-16),(x-2, by-s-4)])
            pygame.draw.polygon(surf, (140, 30, 30), [
                (x+5, by-s-4),(x+9, by-s-16),(x+2, by-s-4)])
            # Glowing eyes
            pygame.draw.circle(surf, (255, 180, 0), (x-4, by-s-3), 3)
            pygame.draw.circle(surf, (255, 180, 0), (x+4, by-s-3), 3)
            pygame.draw.circle(surf, (255, 80, 0),  (x-4, by-s-3), 2)
            pygame.draw.circle(surf, (255, 80, 0),  (x+4, by-s-3), 2)

        elif self.etype == "golem":
            # ── Golem ──────────────────────────────────────────
            s3 = s + 4
            # Legs (stone blocks)
            for lx, lw in [(-8, int(-walk*0.4)), (8, int(walk*0.4))]:
                pygame.draw.rect(surf, (65, 65, 82), (x+lx-6, by+4, 12, 16), border_radius=2)
                pygame.draw.rect(surf, (88, 88, 108), (x+lx-5, by+3, 10, 15), border_radius=2)
            # Body (large stone)
            pygame.draw.circle(surf, (0,0,0), (x+2, by+2), s3)
            pygame.draw.circle(surf, (72, 72, 92), (x, by), s3)
            pygame.draw.circle(surf, (95, 95, 118), (x, by), s3-3)
            # Stone cracks (light emanating)
            for ca in range(0, 360, 55):
                cx2 = x + int(math.cos(math.radians(ca)) * (s3-5))
                cy2 = by + int(math.sin(math.radians(ca)) * (s3-5))
                pygame.draw.line(surf, (180, 200, 255), (x, by), (cx2, cy2), 1)
            # Arms
            pygame.draw.rect(surf, (72, 72, 92), (x-s3-8, by-6, 14, 20), border_radius=3)
            pygame.draw.rect(surf, (72, 72, 92), (x+s3-6, by-6, 14, 20), border_radius=3)
            # Head
            pygame.draw.circle(surf, (72, 72, 92), (x, by-s3-2), s3-4)
            pygame.draw.circle(surf, (88, 88, 108),(x, by-s3-2), s3-6)
            # Glowing eye
            draw_glow(surf, (160, 200, 255), (x, by-s3-2), 8, 80)
            pygame.draw.circle(surf, (180, 220, 255), (x, by-s3-2), 5)
            pygame.draw.circle(surf, (230, 245, 255), (x, by-s3-2), 2)

        elif self.etype == "harpy":
            # ── Harpy (flying) ──────────────────────────────────
            fly_bob = math.sin(self.anim_tick * 0.22) * 4  # faster wing beat
            # Wing beat animation
            wing_angle = math.sin(self.anim_tick * 0.22) * 0.4
            # Left wing
            pygame.draw.polygon(surf, (150, 80, 130), [
                (x, int(by+fly_bob)),
                (x-s*3, int(by+fly_bob-s*2+wing_angle*20)),
                (x-s, int(by+fly_bob+4))])
            # Right wing
            pygame.draw.polygon(surf, (150, 80, 130), [
                (x, int(by+fly_bob)),
                (x+s*3, int(by+fly_bob-s*2-wing_angle*20)),
                (x+s, int(by+fly_bob+4))])
            # Wing highlights
            pygame.draw.polygon(surf, (190, 120, 170), [
                (x-2, int(by+fly_bob)),
                (x-s*2+4, int(by+fly_bob-s*2+8+wing_angle*15)),
                (x-s+2, int(by+fly_bob+2))])
            pygame.draw.polygon(surf, (190, 120, 170), [
                (x+2, int(by+fly_bob)),
                (x+s*2-4, int(by+fly_bob-s*2+8-wing_angle*15)),
                (x+s-2, int(by+fly_bob+2))])
            # Body
            pygame.draw.ellipse(surf, (0,0,0),
                (x-s+1, int(by+fly_bob-s//2)+1, s*2, int(s*1.5)))
            pygame.draw.ellipse(surf, body_color,
                (x-s, int(by+fly_bob-s//2), s*2, int(s*1.5)))
            # Head
            pygame.draw.circle(surf, (0,0,0),   (x+1, int(by+fly_bob-s-1)+1), s-2)
            pygame.draw.circle(surf, body_color, (x,   int(by+fly_bob-s-1)),   s-2)
            # Eyes
            pygame.draw.circle(surf, (255, 220, 60), (x-3, int(by+fly_bob-s-2)), 3)
            pygame.draw.circle(surf, (255, 220, 60), (x+3, int(by+fly_bob-s-2)), 3)
            pygame.draw.circle(surf, (0,0,0),         (x-3, int(by+fly_bob-s-2)), 1)
            pygame.draw.circle(surf, (0,0,0),         (x+3, int(by+fly_bob-s-2)), 1)
            # Talons
            for tx2 in [x-4, x+4]:
                pygame.draw.line(surf, (180, 150, 100), (tx2, int(by+fly_bob+4)), (tx2-2, int(by+fly_bob+12)), 2)

        # ── HP bar ───────────────────────────────────────────────
        bar_w = s*2+10
        draw_health_bar(surf, x-bar_w//2, by-s-13, bar_w, 5, self.hp/self.max_hp)

        # Flying star indicator
        if self.flying:
            lbl = F_TINY.render("✦", True, (220, 220, 100))
            surf.blit(lbl, (x-4, by-s-26))

# ─────────────────────────────────────────
# PROJECTILE
# ─────────────────────────────────────────
class Projectile:
    def __init__(self, x, y, target, damage, speed, dtype, color, size=4, aoe=0, tower=None):
        self.x, self.y = float(x), float(y)
        self.target = target
        self.damage = damage
        self.speed = speed
        self.dtype = dtype
        self.color = color
        self.size = size
        self.aoe = aoe
        self.tower = tower
        self.alive = True
        self.trail = []

    def update(self, dt, enemies):
        if not self.target.alive:
            self.alive = False
            return
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        if dist < self.speed * dt + 5:
            self.hit(enemies)
        else:
            move = self.speed * dt
            self.trail.append((int(self.x), int(self.y)))
            if len(self.trail) > 8:
                self.trail.pop(0)
            self.x += dx/dist * move
            self.y += dy/dist * move

    def hit(self, enemies):
        self.alive = False
        if self.aoe > 0:
            spawn_explosion(int(self.x), int(self.y))
            for e in enemies:
                if e.alive and math.hypot(e.x-self.x, e.y-self.y) < self.aoe:
                    dmg = e.take_damage(self.damage, self.dtype)
                    float_texts.append(FloatText(e.x, e.y-20, f"-{dmg}", (255,180,60), 14))
                    spawn_particles(int(e.x), int(e.y), (255,140,40), 6)
        else:
            dmg = self.target.take_damage(self.damage, self.dtype)
            col = {"physical": (255,255,100), "magic": (180,100,255), "true": (255,100,100)}.get(self.dtype, (255,255,100))
            float_texts.append(FloatText(self.target.x, self.target.y-20, f"-{dmg}", col, 14))
            spawn_particles(int(self.target.x), int(self.target.y), self.color, 5)
            if self.dtype == "slow" and hasattr(self.target, "slowed"):
                self.target.slowed = 2.0

    def draw(self, surf):
        # Trail
        for i, (tx,ty) in enumerate(self.trail):
            alpha = int(160 * (i+1)/len(self.trail))
            r = max(1, self.size-2)
            ts = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(ts, (*self.color, alpha), (r,r), r)
            surf.blit(ts, (tx-r, ty-r))

        ix, iy = int(self.x), int(self.y)

        # Compute flight angle for oriented projectiles
        if self.target and self.target.alive:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            ang = math.atan2(dy, dx)
        else:
            ang = 0.0

        if self.dtype == "physical" and self.aoe == 0:
            # Arrow – elongated shape
            tip_x = ix + int(math.cos(ang) * 10)
            tip_y = iy + int(math.sin(ang) * 10)
            tail_x = ix - int(math.cos(ang) * 7)
            tail_y = iy - int(math.sin(ang) * 7)
            # Shaft
            pygame.draw.line(surf, (180, 140, 70), (tail_x, tail_y), (tip_x, tip_y), 2)
            # Arrowhead
            pygame.draw.circle(surf, (200, 200, 215), (tip_x, tip_y), 2)
            # Fletching
            fang = ang + math.pi * 0.75
            f1x = tail_x + int(math.cos(fang) * 4)
            f1y = tail_y + int(math.sin(fang) * 4)
            f2x = tail_x + int(math.cos(ang + math.pi * 1.25) * 4)
            f2y = tail_y + int(math.sin(ang + math.pi * 1.25) * 4)
            pygame.draw.line(surf, (200, 180, 100), (tail_x, tail_y), (f1x, f1y), 1)
            pygame.draw.line(surf, (200, 180, 100), (tail_x, tail_y), (f2x, f2y), 1)

        elif self.dtype == "magic":
            # Magic orb – glowing sphere
            draw_glow(surf, self.color, (ix, iy), self.size+6, 120)
            pygame.draw.circle(surf, self.color, (ix, iy), self.size)
            pygame.draw.circle(surf, (240, 210, 255), (ix, iy), max(1, self.size-2))
            # Orbiting sparkle
            oa = time.time() * 8
            for si in range(2):
                soa = oa + si * math.pi
                sox = ix + int(math.cos(soa) * (self.size+2))
                soy = iy + int(math.sin(soa) * (self.size+2))
                pygame.draw.circle(surf, (220, 190, 255), (sox, soy), 2)

        elif self.aoe > 0:
            # Cannonball – dark sphere with shine
            pygame.draw.circle(surf, (0,0,0), (ix+1, iy+1), self.size)
            pygame.draw.circle(surf, (50, 42, 28), (ix, iy), self.size)
            pygame.draw.circle(surf, (80, 70, 45), (ix, iy), self.size-2)
            pygame.draw.circle(surf, (100, 90, 60), (ix-2, iy-2), max(1, self.size-4))

        elif self.dtype == "slow":
            # Ice shard – crystalline
            draw_glow(surf, (80, 200, 255), (ix, iy), self.size+5, 90)
            # Crystal points
            for sp in range(4):
                sa = ang + sp * math.pi/2
                ex3 = ix + int(math.cos(sa) * (self.size+3))
                ey3 = iy + int(math.sin(sa) * (self.size+3))
                pygame.draw.line(surf, self.color, (ix, iy), (ex3, ey3), 2)
                pygame.draw.circle(surf, (200, 240, 255), (ex3, ey3), 1)
            pygame.draw.circle(surf, (180, 230, 255), (ix, iy), self.size-1)
            pygame.draw.circle(surf, C_WHITE, (ix, iy), max(1, self.size-3))

        else:
            # Generic glow projectile
            draw_glow(surf, self.color, (ix, iy), self.size+4, 100)
            pygame.draw.circle(surf, self.color, (ix, iy), self.size)
            pygame.draw.circle(surf, C_WHITE, (ix, iy), max(1, self.size-2))

# ─────────────────────────────────────────
# TOWER DEFINITIONS
# ─────────────────────────────────────────
TOWER_DEFS = {
    "archer": {
        "name": "Archer Tower",
        "levels": [
            dict(damage=18, range=120, attack_speed=1.2, cost=80,  dtype="physical", proj_color=(240,200,60),  proj_speed=320, proj_size=3),
            dict(damage=28, range=140, attack_speed=1.4, cost=100, dtype="physical", proj_color=(240,200,60),  proj_speed=360, proj_size=3),
            dict(damage=42, range=160, attack_speed=1.6, cost=140, dtype="physical", proj_color=(255,220,80),  proj_speed=400, proj_size=4),
        ],
        "color": (180,140,60),
        "base_color": (100,80,40),
        "icon": "🏹",
        "desc": "Fast physical damage.\nTargets first enemy."
    },
    "mage": {
        "name": "Mage Tower",
        "levels": [
            dict(damage=35, range=130, attack_speed=0.6, cost=120, dtype="magic", proj_color=(160,80,255), proj_speed=260, proj_size=5),
            dict(damage=55, range=150, attack_speed=0.7, cost=140, dtype="magic", proj_color=(180,100,255), proj_speed=280, proj_size=6),
            dict(damage=80, range=170, attack_speed=0.8, cost=180, dtype="magic", proj_color=(200,120,255), proj_speed=300, proj_size=7),
        ],
        "color": (140,80,220),
        "base_color": (80,50,140),
        "icon": "🔮",
        "desc": "Magic damage.\nIgnores armor."
    },
    "artillery": {
        "name": "Artillery",
        "levels": [
            dict(damage=60, range=150, attack_speed=0.35, cost=160, dtype="physical", proj_color=(220,140,40), proj_speed=200, proj_size=7, aoe=60),
            dict(damage=90, range=170, attack_speed=0.40, cost=180, dtype="physical", proj_color=(230,160,50), proj_speed=220, proj_size=8, aoe=70),
            dict(damage=130,range=190, attack_speed=0.45, cost=220, dtype="physical", proj_color=(255,180,60), proj_speed=240, proj_size=9, aoe=80),
        ],
        "color": (160,120,60),
        "base_color": (90,70,30),
        "icon": "💣",
        "desc": "Slow but AOE damage.\nDestroys groups."
    },
    "ice": {
        "name": "Ice Tower",
        "levels": [
            dict(damage=12, range=110, attack_speed=0.9, cost=100, dtype="slow", proj_color=(80,200,255), proj_speed=280, proj_size=4),
            dict(damage=20, range=130, attack_speed=1.0, cost=120, dtype="slow", proj_color=(100,220,255), proj_speed=300, proj_size=5),
            dict(damage=30, range=150, attack_speed=1.1, cost=160, dtype="slow", proj_color=(140,240,255), proj_speed=320, proj_size=6),
        ],
        "color": (80,180,240),
        "base_color": (50,120,160),
        "icon": "❄",
        "desc": "Slows enemies.\nGreat support tower."
    },
}

class Tower:
    def __init__(self, ttype, x, y):
        self.ttype = ttype
        self.x, self.y = x, y
        self.level = 0
        self.d = TOWER_DEFS[ttype]
        self.stats = self.d["levels"][0]
        self.cooldown = 0.0
        self.target = None
        self.anim_tick = 0
        self.selected = False
        self.shoot_anim = 0.0
        self._muzzle_x = x
        self._muzzle_y = y
        self.total_damage = 0
        self.kills = 0

    @property
    def max_level(self):
        return len(self.d["levels"]) - 1

    @property
    def upgrade_cost(self):
        if self.level >= self.max_level:
            return None
        return self.d["levels"][self.level+1]["cost"]

    @property
    def sell_value(self):
        total = sum(self.d["levels"][i]["cost"] for i in range(self.level+1))
        return int(total * 0.65)

    def upgrade(self):
        if self.level < self.max_level:
            self.level += 1
            self.stats = self.d["levels"][self.level]
            spawn_particles(self.x, self.y, (255,255,100), 12, speed=80)
            float_texts.append(FloatText(self.x, self.y-30, "UPGRADED!", (255,220,80), 18))
            return True
        return False

    def get_target(self, enemies):
        best = None
        best_prog = -1
        for e in enemies:
            if not e.alive: continue
            if e.flying and self.ttype not in ("archer","mage","ice"): continue
            dist = math.hypot(e.x-self.x, e.y-self.y)
            if dist <= self.stats["range"]:
                if e.progress > best_prog:
                    best_prog = e.progress
                    best = e
        return best

    def update(self, dt, enemies, projectiles):
        self.anim_tick += dt * 60
        self.shoot_anim = max(0, self.shoot_anim - dt * 3)
        self.cooldown = max(0, self.cooldown - dt)

        if self.cooldown <= 0:
            self.target = self.get_target(enemies)
            if self.target:
                self.cooldown = 1.0 / self.stats["attack_speed"]
                self.shoot_anim = 1.0
                aoe = self.stats.get("aoe", 0)
                proj = Projectile(
                    self.x, self.y - 20,
                    self.target,
                    self.stats["damage"],
                    self.stats.get("proj_speed", 300),
                    self.stats["dtype"],
                    self.stats["proj_color"],
                    self.stats.get("proj_size", 4),
                    aoe, self
                )
                projectiles.append(proj)
                self.total_damage += self.stats["damage"]

    def draw(self, surf):
        x, y = self.x, self.y
        d = self.d
        color = d["color"]
        base_color = d["base_color"]
        lv = self.level

        # ── Use sprite if available ───────────────────────────────
        sprite_key = f"{self.ttype}_lv{lv+1}"
        spr = TOWER_SPRITES.get(sprite_key)
        if spr:
            # Range ring
            if self.selected:
                rs = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                pygame.draw.circle(rs, (*color, 28), (x, y), self.stats["range"])
                pygame.draw.circle(rs, (*color, 90), (x, y), self.stats["range"], 2)
                surf.blit(rs, (0, 0))
            # Shadow
            pygame.draw.ellipse(surf, (0,0,0,60), (x-20, y+16, 40, 12))
            blit_centered(surf, spr, x, y - spr.get_height()//4)
            # Level stars
            for i in range(lv+1):
                sx2 = x - lv*6 + i*12
                pygame.draw.circle(surf, C_UI_GOLD, (sx2, y+22), 4)
            return   # skip procedural drawing below

        # Range ring (if selected)
        if self.selected:
            range_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            pygame.draw.circle(range_surf, (*color, 28), (x, y), self.stats["range"])
            pygame.draw.circle(range_surf, (*color, 90), (x, y), self.stats["range"], 2)
            surf.blit(range_surf, (0, 0))

        # Ground shadow
        pygame.draw.ellipse(surf, (0, 0, 0, 70), (x-20, y+16, 40, 12))

        # ── Stone base platform ──────────────────────────────────
        # Outer stone base
        pygame.draw.rect(surf, C_STONE3, (x-18, y+6, 36, 14), border_radius=4)
        pygame.draw.rect(surf, C_STONE2, (x-16, y+4, 32, 14), border_radius=3)
        # Base stone highlight
        pygame.draw.line(surf, C_STONE1, (x-14, y+5), (x+14, y+5), 1)
        # Mortar lines on base
        pygame.draw.line(surf, C_MORTAR, (x-2, y+4), (x-2, y+18), 1)
        pygame.draw.line(surf, C_MORTAR, (x+6, y+4), (x+6, y+18), 1)

        if self.ttype == "archer":
            # ── Archer Tower ─────────────────────────────────────
            # Tower body (stone masonry)
            pygame.draw.rect(surf, C_STONE3, (x-13, y-22, 26, 30), border_radius=2)
            pygame.draw.rect(surf, C_STONE2, (x-11, y-24, 22, 30), border_radius=2)
            # Masonry lines
            for my2 in range(y-22, y+6, 8):
                pygame.draw.line(surf, C_MORTAR, (x-11, my2), (x+11, my2), 1)
            pygame.draw.line(surf, C_MORTAR, (x-2, y-22), (x-2, y+4), 1)
            pygame.draw.line(surf, C_MORTAR, (x+5, y-22+4), (x+5, y+4), 1)
            # Arrow slit window
            pygame.draw.rect(surf, (15, 12, 8), (x-2, y-18, 4, 10), border_radius=1)
            pygame.draw.rect(surf, (30, 25, 15), (x-1, y-17, 2, 8))
            # Battlement (merlons)
            for bx in (-11, -5, 1, 7):
                pygame.draw.rect(surf, C_STONE3, (x+bx, y-28, 5, 8))
                pygame.draw.rect(surf, C_STONE2, (x+bx, y-28, 4, 7))
            # Tower wall top (between merlons)
            pygame.draw.rect(surf, C_STONE2, (x-11, y-22, 22, 3))
            # Archer flag
            flag_wave = math.sin(self.anim_tick*0.08) * 3
            pygame.draw.line(surf, (70, 48, 20), (x+2, y-28), (x+2, y-46), 2)
            pygame.draw.polygon(surf, (180, 40, 40), [
                (x+2, y-46), (x+18, y-40+flag_wave), (x+2, y-34)])
            pygame.draw.polygon(surf, (220, 65, 65), [
                (x+2, y-44), (x+16, y-39+flag_wave), (x+2, y-34)])
            # Cross emblem on flag
            if lv >= 1:
                pygame.draw.line(surf, (255,220,80), (x+2,y-46),(x+2,y-34),1)

        elif self.ttype == "mage":
            # ── Mage Tower ───────────────────────────────────────
            # Tower body – slender, dark stone
            pygame.draw.rect(surf, (55, 38, 100), (x-9, y-28, 18, 36), border_radius=3)
            pygame.draw.rect(surf, (75, 52, 130), (x-7, y-30, 14, 36), border_radius=2)
            # Rune-etched window
            pulse = int(10*math.sin(self.anim_tick*0.12))
            win_col = (100+pulse, 60+pulse//2, 200+pulse//3)
            pygame.draw.rect(surf, win_col, (x-4, y-22, 8, 10), border_radius=2)
            pygame.draw.rect(surf, (200, 160, 255), (x-3, y-21, 6, 8), border_radius=1)
            # Conical roof
            pygame.draw.polygon(surf, (55, 32, 110), [(x-11, y-28),(x+11, y-28),(x, y-54)])
            pygame.draw.polygon(surf, (80, 50, 150), [(x-9, y-28),(x+9, y-28),(x, y-52)])
            # Roof stars
            for si in range(3+lv):
                ang = self.anim_tick*0.03 + si * math.tau/(3+lv)
                sr = 5 + si*2
                spx = x + math.cos(ang)*sr
                spy = y - 40 + math.sin(ang)*sr * 0.4
                pygame.draw.circle(surf, (200+si*10, 180, 255), (int(spx), int(spy)), 1)
            # Glowing orb on top
            draw_glow(surf, (180, 100, 255), (x, y-52+pulse//4), 10+pulse//3, 90)
            pygame.draw.circle(surf, (200, 120, 255), (x, y-52), 5+lv)
            pygame.draw.circle(surf, (240, 210, 255), (x, y-52), 2)

        elif self.ttype == "artillery":
            # ── Artillery Tower ───────────────────────────────────
            # Bunker base
            pygame.draw.rect(surf, C_STONE3, (x-16, y-12, 32, 20), border_radius=4)
            pygame.draw.rect(surf, C_STONE2, (x-14, y-14, 28, 20), border_radius=3)
            # Masonry lines
            pygame.draw.line(surf, C_MORTAR, (x-14, y-6), (x+14, y-6), 1)
            pygame.draw.line(surf, C_MORTAR, (x+0,  y-14),(x+0,  y+4), 1)
            # Cannon carriage (wood)
            pygame.draw.rect(surf, C_WOOD_DARK, (x-12, y-4, 24, 10), border_radius=2)
            pygame.draw.rect(surf, C_WOOD_MID,  (x-11, y-5, 22, 10), border_radius=2)
            pygame.draw.line(surf, C_WOOD_LIGHT,(x-10, y-3),(x+10, y-3), 1)
            # Cannon barrel
            angle = -math.pi/4 + self.shoot_anim * 0.35
            blen = 22 + lv*3
            ex2 = x + math.cos(angle)*blen
            ey2 = y - 6 + math.sin(angle)*blen
            # Barrel shadow
            pygame.draw.line(surf, (30, 22, 10),
                (x+2, y-5+2), (int(ex2)+2, int(ey2)+2), 10)
            # Barrel body
            pygame.draw.line(surf, (48, 38, 22), (x, y-6), (int(ex2), int(ey2)), 9)
            pygame.draw.line(surf, (75, 60, 35), (x, y-6), (int(ex2), int(ey2)), 7)
            # Barrel highlight
            pygame.draw.line(surf, (110, 90, 55),
                (x, y-8), (int(ex2), int(ey2)-2), 2)
            # Muzzle ring
            pygame.draw.circle(surf, (90, 72, 42), (int(ex2), int(ey2)), 5)
            pygame.draw.circle(surf, (120, 100, 60), (int(ex2), int(ey2)), 4)
            # Muzzle flash
            if self.shoot_anim > 0.6:
                draw_glow(surf, (255,160,40), (int(ex2), int(ey2)), 12, int(self.shoot_anim*120))
            # Wheels
            for wx2, wy2 in [(x-11, y+8), (x+11, y+8)]:
                pygame.draw.circle(surf, (45, 32, 14), (wx2, wy2), 7)
                pygame.draw.circle(surf, (70, 52, 24), (wx2, wy2), 6)
                # Spokes
                for a in range(0, 360, 60):
                    ax = int(wx2 + math.cos(math.radians(a))*5)
                    ay = int(wy2 + math.sin(math.radians(a))*5)
                    pygame.draw.line(surf, (100, 75, 38), (wx2, wy2), (ax, ay), 1)
                pygame.draw.circle(surf, (110, 85, 45), (wx2, wy2), 2)

        elif self.ttype == "ice":
            # ── Ice / Crystal Tower ───────────────────────────────
            # Frost base
            pygame.draw.rect(surf, (35, 90, 130), (x-10, y-14, 20, 22), border_radius=2)
            pygame.draw.rect(surf, (50, 115, 158), (x-8, y-16, 16, 22), border_radius=2)
            # Crystal spires (height varies by level)
            spire_data = [(-7, 18), (0, 22+lv*3), (7, 18)]
            for si, (ox, h) in enumerate(spire_data):
                cx2 = x + ox
                # Spire body
                pygame.draw.polygon(surf, (55, 140, 190),
                    [(cx2-5, y-14), (cx2+5, y-14), (cx2+2, y-14-h), (cx2-2, y-14-h)])
                # Bright face
                pygame.draw.polygon(surf, (90, 185, 230),
                    [(cx2-4, y-14), (cx2+1, y-14), (cx2, y-14-h+4)])
                # Icy tip
                pygame.draw.polygon(surf, (200, 240, 255),
                    [(cx2-2, y-14-h+4), (cx2+2, y-14-h+4), (cx2, y-14-h)])
            # Ice glow aura
            pulse = int(8*math.sin(self.anim_tick*0.10))
            draw_glow(surf, (80, 200, 255), (x, y-20), 12+pulse//2, 65)
            # Frost particles (static sparkles)
            for si in range(4+lv*2):
                ang = self.anim_tick*0.04 + si * math.tau/(4+lv*2)
                pr = 14+si*2
                ppx = x + math.cos(ang)*pr
                ppy = y - 20 + math.sin(ang)*pr*0.5
                pygame.draw.circle(surf, (180, 230, 255), (int(ppx), int(ppy)), 1)

        # ── Level stars ──────────────────────────────────────────
        for i in range(lv+1):
            sx2 = x - lv*6 + i*12
            pygame.draw.circle(surf, C_UI_GOLD,       (sx2, y+22), 4)
            pygame.draw.circle(surf, (255, 240, 140),  (sx2, y+22), 2)

        # Shoot flash (generic)
        if self.ttype != "artillery" and self.shoot_anim > 0.7:
            draw_glow(surf, self.stats["proj_color"], (x, y-20), 12, int(self.shoot_anim*100))

# ─────────────────────────────────────────
# SOLDIER (Barracks unit)
# ─────────────────────────────────────────
class Soldier:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.max_hp = 80
        self.hp = self.max_hp
        self.damage = 15
        self.attack_speed = 1.2
        self.cooldown = 0.0
        self.alive = True
        self.target = None
        self.anim_tick = random.randint(0,100)
        self.col = (180, 150, 100)

    def update(self, dt, enemies):
        self.anim_tick += dt * 60
        self.cooldown = max(0, self.cooldown - dt)
        # Find nearby enemy
        best = None
        best_dist = 40
        for e in enemies:
            if not e.alive: continue
            dist = math.hypot(e.x-self.x, e.y-self.y)
            if dist < best_dist:
                best_dist = dist
                best = e
        self.target = best
        if best:
            best.blocked_by = self
        if self.target and self.cooldown <= 0:
            self.cooldown = 1.0/self.attack_speed
            dmg = self.target.take_damage(self.damage, "physical")
            spawn_particles(int(self.target.x), int(self.target.y), (255,200,60), 3)

    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        bob = math.sin(self.anim_tick*0.12)*1.5
        by = int(y + bob)
        # Shadow
        pygame.draw.ellipse(surf, (0,0,0,55), (x-10, by+10, 20, 7))
        # Legs (simple)
        pygame.draw.rect(surf, (100, 80, 50), (x-5, by+4, 4, 8))
        pygame.draw.rect(surf, (100, 80, 50), (x+1, by+4, 4, 8))
        # Body / tunic
        pygame.draw.rect(surf, (160, 135, 90), (x-8, by-6, 16, 14), border_radius=2)
        pygame.draw.rect(surf, (185, 158, 110), (x-6, by-8, 12, 14), border_radius=2)
        # Chainmail shine line
        pygame.draw.line(surf, (220, 200, 150), (x-5, by-6), (x+5, by-6), 1)
        # Shield (left side)
        pygame.draw.rect(surf, (55, 40, 110), (x+7, by-7, 7, 13), border_radius=2)
        pygame.draw.rect(surf, (80, 58, 150), (x+7, by-7, 6, 12), border_radius=2)
        pygame.draw.circle(surf, (140, 110, 200), (x+10, by-1), 2)
        # Spear
        pygame.draw.line(surf, (90, 65, 30), (x-7, by+5), (x-11, by-20), 2)
        pygame.draw.polygon(surf, (190, 190, 200), [
            (x-12, by-20),(x-10, by-20),(x-11, by-28)])
        # Head
        pygame.draw.circle(surf, (0,0,0),         (x+1, by-14+1), 7)
        pygame.draw.circle(surf, (215, 180, 138), (x,   by-14),    7)
        # Helmet
        pygame.draw.rect(surf,   (130, 112, 72), (x-7, by-18, 14, 5))
        pygame.draw.rect(surf,   (158, 138, 90), (x-6, by-21, 12, 8), border_radius=3)
        # Plume on helmet
        pygame.draw.line(surf, (200, 50, 50), (x, by-21), (x+2, by-30), 2)
        # HP bar
        draw_health_bar(surf, x-9, by-34, 18, 3, self.hp/self.max_hp)

# ─────────────────────────────────────────
# BARRACKS TOWER
# ─────────────────────────────────────────
class BarracksTower:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.level = 0
        self.soldiers = []
        self.spawn_timer = 3.0
        self.max_soldiers = 2
        self.selected = False
        self.ttype = "barracks"
        self.d = {"color": (160,120,60), "name":"Barracks", "icon":"⚔"}
        self.stats = {"range": 80, "attack_speed":0, "damage":0, "dtype":"physical"}
        self.upgrade_cost_val = 100
        self.total_damage = 0
        self.kills = 0

    @property
    def max_level(self): return 2

    @property
    def upgrade_cost(self):
        if self.level >= self.max_level: return None
        return [100, 140][self.level]

    @property
    def sell_value(self):
        base = [80, 100, 140][self.level]
        return int(base * 0.65)

    def upgrade(self):
        if self.level < self.max_level:
            self.level += 1
            self.max_soldiers = 2 + self.level
            spawn_particles(self.x, self.y, (255,255,100), 12)
            float_texts.append(FloatText(self.x, self.y-30, "UPGRADED!", (255,220,80), 18))
            return True
        return False

    def update(self, dt, enemies, projectiles):
        self.spawn_timer -= dt
        for s in self.soldiers[:]:
            if not s.alive:
                self.soldiers.remove(s)
        for s in self.soldiers:
            s.update(dt, enemies)
            if s.hp <= 0:
                s.alive = False

        if self.spawn_timer <= 0 and len(self.soldiers) < self.max_soldiers:
            offset = (len(self.soldiers) - self.max_soldiers//2) * 20
            sx = self.x + offset
            sy = self.y + 20
            self.soldiers.append(Soldier(sx, sy))
            self.spawn_timer = 5.0

    def draw(self, surf):
        x, y = self.x, self.y
        if self.selected:
            range_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            pygame.draw.circle(range_surf, (160,120,60,28), (x,y), self.stats["range"])
            pygame.draw.circle(range_surf, (160,120,60,85), (x,y), self.stats["range"], 2)
            surf.blit(range_surf, (0,0))

        # Ground shadow
        pygame.draw.ellipse(surf, (0,0,0,70), (x-22, y+16, 44, 12))

        # Stone base / foundation
        pygame.draw.rect(surf, C_STONE3, (x-18, y+6, 36, 14), border_radius=3)
        pygame.draw.rect(surf, C_STONE2, (x-16, y+4, 32, 14), border_radius=3)
        pygame.draw.line(surf, C_MORTAR, (x-16, y+10), (x+16, y+10), 1)

        # Main building walls (stone)
        pygame.draw.rect(surf, C_STONE3, (x-16, y-22, 32, 28), border_radius=2)
        pygame.draw.rect(surf, C_STONE2, (x-14, y-24, 28, 28), border_radius=2)
        # Masonry lines
        for my2 in range(y-22, y+4, 7):
            pygame.draw.line(surf, C_MORTAR, (x-14, my2), (x+14, my2), 1)
        pygame.draw.line(surf, C_MORTAR, (x+2, y-24), (x+2, y+4), 1)
        pygame.draw.line(surf, C_MORTAR, (x-6, y-24+3), (x-6, y+4), 1)
        # Gate arch / door
        pygame.draw.rect(surf, (18, 12, 6), (x-6, y-8, 12, 14), border_radius=3)
        pygame.draw.ellipse(surf, (18, 12, 6), (x-6, y-14, 12, 12))
        # Door frame
        pygame.draw.rect(surf, C_WOOD_MID, (x-7, y-8, 2, 14))
        pygame.draw.rect(surf, C_WOOD_MID, (x+5, y-8, 2, 14))

        # Roof (gabled)
        pygame.draw.polygon(surf, (130, 48, 30), [(x-16, y-22),(x+16, y-22),(x, y-44)])
        pygame.draw.polygon(surf, (158, 62, 40), [(x-14, y-22),(x+14, y-22),(x, y-42)])
        # Roof highlight
        pygame.draw.line(surf, (180, 80, 55), (x-13, y-23), (x, y-41), 1)

        # Side towers
        for tx2, tw in [(x-14, 8), (x+14, 8)]:
            pygame.draw.rect(surf, C_STONE3, (tx2-tw//2, y-26, tw, 30), border_radius=2)
            pygame.draw.rect(surf, C_STONE2, (tx2-tw//2+1, y-28, tw-2, 30), border_radius=1)
            # Merlon tops
            for bx2 in range(0, tw, 4):
                pygame.draw.rect(surf, C_STONE2, (tx2-tw//2+bx2, y-32, 3, 6))

        # Flag pole and banner
        pygame.draw.line(surf, C_WOOD_DARK, (x, y-44), (x, y-58), 2)
        flag_wave = math.sin(self.anim_tick*0.07) * 2
        pygame.draw.polygon(surf, (200, 190, 50), [
            (x, y-58),(x+14, y-53+flag_wave),(x, y-48)])
        pygame.draw.polygon(surf, (230, 220, 80), [
            (x, y-56),(x+12, y-52+flag_wave),(x, y-48)])

        # Level stars
        for i in range(self.level+1):
            sx2 = x - (self.level*6) + i*12
            pygame.draw.circle(surf, C_UI_GOLD, (sx2, y+24), 4)
            pygame.draw.circle(surf, (255,240,140), (sx2, y+24), 2)

        # Soldiers
        for s in self.soldiers:
            s.draw(surf)

# ─────────────────────────────────────────
# HERO
# ─────────────────────────────────────────
class Hero:
    def __init__(self):
        self.x, self.y = 400.0, 350.0
        self.max_hp = 400
        self.hp = self.max_hp
        self.damage = 60
        self.speed = 140
        self.level = 1
        self.xp = 0
        self.xp_next = 100
        self.attack_range = 50
        self.attack_speed = 0.9
        self.cooldown = 0.0
        self.moving_to = None
        self.skill_cd = 0.0
        self.skill_max_cd = 8.0
        self.alive = True
        self.anim_tick = 0
        self.face_dir = 1

    def gain_xp(self, amount):
        self.xp += amount
        while self.xp >= self.xp_next:
            self.xp -= self.xp_next
            self.level += 1
            self.max_hp += 50
            self.hp = min(self.hp + 80, self.max_hp)
            self.damage += 10
            self.xp_next = int(self.xp_next * 1.4)
            float_texts.append(FloatText(self.x, self.y-40, f"LEVEL UP! {self.level}", C_UI_GOLD, 20))
            spawn_particles(int(self.x), int(self.y), (255,220,80), 20, speed=100)

    def use_skill(self, enemies):
        if self.skill_cd > 0: return False
        self.skill_cd = self.skill_max_cd
        count = 0
        for e in enemies:
            if e.alive and math.hypot(e.x-self.x, e.y-self.y) < 100:
                e.take_damage(self.damage*3, "true")
                count += 1
                spawn_particles(int(e.x), int(e.y), (255,220,80), 15)
        spawn_explosion(int(self.x), int(self.y), (255,200,80), 30)
        float_texts.append(FloatText(self.x, self.y-50, "WAR CRY!", (255,220,80), 22))
        return True

    def update(self, dt, enemies):
        self.anim_tick += dt * 60
        self.cooldown = max(0, self.cooldown - dt)
        self.skill_cd = max(0, self.skill_cd - dt)

        if self.moving_to:
            tx, ty = self.moving_to
            dx, dy = tx - self.x, ty - self.y
            dist = math.hypot(dx, dy)
            if dist < 5:
                self.moving_to = None
            else:
                move = self.speed * dt
                self.face_dir = 1 if dx > 0 else -1
                self.x += dx/dist * min(move, dist)
                self.y += dy/dist * min(move, dist)

        # Attack nearest enemy
        if self.cooldown <= 0:
            best = None
            best_dist = self.attack_range
            for e in enemies:
                if not e.alive: continue
                dist = math.hypot(e.x-self.x, e.y-self.y)
                if dist < best_dist:
                    best_dist = dist
                    best = e
            if best:
                self.cooldown = 1.0/self.attack_speed
                dmg = best.take_damage(self.damage, "true")
                self.gain_xp(best.reward_xp // 5)
                spawn_particles(int(best.x), int(best.y), (255,220,100), 5, speed=60)
                float_texts.append(FloatText(best.x, best.y-25, f"-{dmg}", (255,180,60), 15))

    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        bob = math.sin(self.anim_tick * 0.13) * 2
        fd = self.face_dir
        by = int(y + bob)

        # Skill ready aura
        if self.skill_cd <= 0:
            pulse = int(6*math.sin(self.anim_tick*0.15))
            draw_glow(surf, (255, 220, 80), (x, by), 22+pulse, 55)

        # Ground shadow
        pygame.draw.ellipse(surf, (0,0,0,60), (x-16, by+16, 32, 10))

        # ── Use sprite if available ───────────────────────────────
        if HERO_SPRITE:
            blit_centered(surf, HERO_SPRITE, x, by - 6, flip_x=(fd == -1))
            draw_health_bar(surf, x-14, by-34, 28, 5, self.hp/self.max_hp)
            return   # skip procedural drawing

        # Legs
        walk = math.sin(self.anim_tick * 0.16) * 3
        pygame.draw.line(surf, (120, 100, 60), (x-4, by+8), (x-5+int(walk), by+18), 5)
        pygame.draw.line(surf, (120, 100, 60), (x+4, by+8), (x+5-int(walk), by+18), 5)
        pygame.draw.line(surf, (160, 135, 88), (x-4, by+8), (x-5+int(walk), by+17), 3)
        pygame.draw.line(surf, (160, 135, 88), (x+4, by+8), (x+5-int(walk), by+17), 3)

        # Cape (behind body)
        cape_wave = math.sin(self.anim_tick*0.08) * 3
        pygame.draw.polygon(surf, (100, 30, 140), [
            (x-10, by), (x+10, by),
            (x+8+int(cape_wave*0.4), by+20),
            (x-8-int(cape_wave*0.4), by+20)])
        pygame.draw.polygon(surf, (130, 45, 175), [
            (x-8, by), (x+8, by),
            (x+6+int(cape_wave*0.3), by+18),
            (x-6-int(cape_wave*0.3), by+18)])

        # Body armor (plate mail)
        pygame.draw.rect(surf, (130, 115, 75), (x-10, by-8, 20, 18), border_radius=3)
        pygame.draw.rect(surf, (165, 148, 98), (x-8,  by-10, 16, 18), border_radius=2)
        # Chest plate highlight
        pygame.draw.line(surf, (195, 178, 120), (x-7, by-9), (x+7, by-9), 1)
        # Gold trim (collar)
        pygame.draw.rect(surf, C_UI_GOLD, (x-8, by-10, 16, 3), border_radius=1)
        # Gold belt
        pygame.draw.rect(surf, C_UI_GOLD, (x-8, by+6,  16, 2))
        # Shield (on off-hand side)
        if fd == 1:
            pygame.draw.rect(surf, (55, 42, 110), (x-18, by-10, 10, 16), border_radius=2)
            pygame.draw.rect(surf, (78, 60, 148),  (x-17, by-10, 8,  14), border_radius=2)
            pygame.draw.line(surf, (140, 120, 200), (x-16, by-9), (x-10, by-9), 1)
            pygame.draw.circle(surf, C_UI_GOLD, (x-13, by-3), 3)
        else:
            pygame.draw.rect(surf, (55, 42, 110), (x+8,  by-10, 10, 16), border_radius=2)
            pygame.draw.rect(surf, (78, 60, 148),  (x+9,  by-10, 8,  14), border_radius=2)
            pygame.draw.circle(surf, C_UI_GOLD, (x+13, by-3), 3)

        # Sword arm + sword
        sword_x = x + fd * 12
        pygame.draw.line(surf, (70, 55, 25), (x+fd*8, by), (x+fd*12, by+12), 5)  # arm
        pygame.draw.line(surf, (105, 85, 40), (x+fd*8, by), (x+fd*12, by+11), 3)
        # Sword blade
        pygame.draw.line(surf, (50, 42, 20), (sword_x, by-4), (sword_x+fd*18, by-22), 4)
        pygame.draw.line(surf, (195, 200, 215), (sword_x, by-4), (sword_x+fd*18, by-22), 3)
        pygame.draw.line(surf, (230, 235, 248), (sword_x+fd*2, by-6), (sword_x+fd*16, by-20), 1)  # shine
        # Crossguard
        pygame.draw.line(surf, C_UI_GOLD, (sword_x-fd*4, by-2), (sword_x+fd*4, by-2), 3)
        # Sword pommel
        pygame.draw.circle(surf, C_UI_GOLD, (sword_x, by-1), 3)

        # Head
        pygame.draw.circle(surf, (0,0,0),          (x+1, by-17+1), 9)
        pygame.draw.circle(surf, (218, 178, 135), (x,   by-17),    9)

        # Helmet (full plate)
        pygame.draw.polygon(surf, (130, 112, 72),
            [(x-10, by-17), (x+10, by-17), (x+9, by-28), (x-9, by-28)])
        pygame.draw.polygon(surf, (160, 140, 90),
            [(x-8, by-17), (x+8, by-17), (x+7, by-27), (x-7, by-27)])
        # Visor slit
        pygame.draw.rect(surf, (20, 15, 5), (x-6, by-22, 12, 3))
        # Helmet nose guard
        pygame.draw.rect(surf, (140, 120, 78), (x-1, by-22, 3, 5))
        # Plume
        plume_col = (200, 50, 50)
        for pi in range(5):
            px2 = x + fd*(pi-2)*2
            py2 = by - 28 - pi*4
            pygame.draw.line(surf, plume_col,
                (px2, py2), (px2+fd*3, py2-6), 2)
        # Crest
        pygame.draw.rect(surf, C_UI_GOLD, (x-8, by-28, 16, 2))

        # HP bar
        draw_health_bar(surf, x-14, by-34, 28, 5, self.hp/self.max_hp)

# ─────────────────────────────────────────
# WAVE SYSTEM
# ─────────────────────────────────────────
WAVE_DEFINITIONS = [
    [("goblin",8,0.8)],
    [("goblin",10,0.7),("orc",3,1.5)],
    [("orc",6,1.2),("goblin",6,0.6)],
    [("troll",2,3.0),("orc",8,1.0),("goblin",10,0.5)],
    [("harpy",6,0.6),("orc",6,1.0)],
    [("demon",4,1.2),("troll",3,2.5)],
    [("golem",1,8.0),("demon",6,0.8),("harpy",8,0.5)],
    [("golem",2,5.0),("troll",4,2.0),("demon",8,0.7),("goblin",15,0.4)],
]

class WaveManager:
    def __init__(self):
        self.wave_index = 0
        self.phase_index = 0
        self.spawn_timer = 0.0
        self.active = False
        self.done = False
        self.between_timer = 0.0
        self.between_wait = 6.0
        self.spawn_count = 0

    def start_wave(self):
        if self.wave_index < len(WAVE_DEFINITIONS):
            self.active = True
            self.phase_index = 0
            self.spawn_timer = 0.0
            self.spawn_count = 0
            self.between_timer = 0.0

    @property
    def current_wave_num(self):
        return self.wave_index + 1

    @property
    def total_waves(self):
        return len(WAVE_DEFINITIONS)

    def update(self, dt, enemies):
        if not self.active: return []
        new_enemies = []
        phases = WAVE_DEFINITIONS[self.wave_index]

        if self.phase_index >= len(phases):
            # Check if all enemies from this wave are dead
            if len([e for e in enemies if e.alive]) == 0:
                self.active = False
                self.wave_index += 1
                if self.wave_index >= len(WAVE_DEFINITIONS):
                    self.done = True
            return new_enemies

        etype, count, delay = phases[self.phase_index]
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            offset = self.spawn_count * 10
            new_enemies.append(Enemy(etype, offset))
            self.spawn_count += 1
            self.spawn_timer = delay
            if self.spawn_count >= count:
                self.spawn_count = 0
                self.phase_index += 1

        return new_enemies

    def get_next_wave_preview(self):
        if self.wave_index >= len(WAVE_DEFINITIONS): return []
        return [(e,c) for e,c,_ in WAVE_DEFINITIONS[self.wave_index]]

# ─────────────────────────────────────────
# GLOBAL SKILLS
# ─────────────────────────────────────────
class GlobalSkill:
    def __init__(self, name, icon, cooldown, color, desc):
        self.name = name
        self.icon = icon
        self.max_cd = cooldown
        self.cd = 0.0
        self.color = color
        self.desc = desc
        self.active = False  # waiting for click placement

    def use(self):
        if self.cd <= 0:
            self.active = True
            return True
        return False

    def trigger(self, x, y, enemies):
        self.cd = self.max_cd
        self.active = False
        if self.name == "Meteor":
            spawn_explosion(x, y, (255,120,30), 40)
            spawn_particles(x, y, (255,60,20), 30, speed=200, size=8, life=1.2, gravity=200)
            killed = 0
            for e in enemies:
                if e.alive and math.hypot(e.x-x, e.y-y) < 100:
                    e.take_damage(300, "true")
                    killed += 1
            float_texts.append(FloatText(x, y-50, f"METEOR! -{killed} hp", (255,140,40), 20))
        elif self.name == "Freeze":
            for e in enemies:
                if e.alive and math.hypot(e.x-x, e.y-y) < 120:
                    e.slowed = 4.0
                    e.stunned = 1.5
                    spawn_particles(int(e.x), int(e.y), (80,200,255), 8)
            float_texts.append(FloatText(x, y-50, "FROZEN!", (80,200,255), 20))
            draw_glow(screen, (80,200,255), (x,y), 120, 120)

GLOBAL_SKILLS = [
    GlobalSkill("Meteor", "☄", 25, (255,120,40), "Deal 300 true dmg\nin AoE 100"),
    GlobalSkill("Freeze",  "❄", 20, (80,200,255), "Stun+slow enemies\nin AoE 120"),
]

# ─────────────────────────────────────────
# GAME STATE
# ─────────────────────────────────────────
class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    VICTORY = "victory"

class Game:
    def __init__(self):
        self.state = GameState.MENU
        self.reset()

    def reset(self):
        self.enemies = []
        self.towers = []
        self.projectiles = []
        self.wave_manager = WaveManager()
        self.hero = Hero()
        self.gold = 160
        self.lives = 20
        self.selected_tower_type = None
        self.selected_tower = None
        self.game_surf = pygame.Surface((GAME_W, GAME_H))
        self.tick = 0
        self.total_gold_earned = 0
        self.total_kills = 0
        self.score = 0
        particles.clear()
        float_texts.clear()

    def start(self):
        global _map_static_cache
        self.state = GameState.PLAYING
        _map_static_cache = None  # rebuild map cache
        self.reset()

    def buy_tower(self, ttype, x, y):
        if ttype == "barracks":
            cost = 100
            if self.gold < cost: return False
            self.gold -= cost
            self.towers.append(BarracksTower(x, y))
            float_texts.append(FloatText(x, y-30, f"-{cost}g", C_UI_GOLD, 15))
            spawn_particles(x, y, (255,220,80), 8)
            return True
        else:
            if ttype not in TOWER_DEFS: return False
            cost = TOWER_DEFS[ttype]["levels"][0]["cost"]
            if self.gold < cost: return False
            self.gold -= cost
            self.towers.append(Tower(ttype, x, y))
            float_texts.append(FloatText(x, y-30, f"-{cost}g", C_UI_GOLD, 15))
            spawn_particles(x, y, (255,220,80), 8)
            return True

    def update(self, dt):
        if self.state != GameState.PLAYING: return
        self.tick += 1

        # Skills global
        for sk in GLOBAL_SKILLS:
            sk.cd = max(0, sk.cd - dt)

        # Wave
        new_enemies = self.wave_manager.update(dt, self.enemies)
        self.enemies.extend(new_enemies)

        # Enemies
        for e in self.enemies:
            if not e.alive: continue
            e.blocked_by = None  # reset
        for e in self.enemies:
            e.update(dt)
            if e.reached_end:
                e.alive = False
                e.reached_end = False
                self.lives -= 1
                float_texts.append(FloatText(WAYPOINTS[-1][0]-20, WAYPOINTS[-1][1]-30, "-1 LIFE!", C_UI_RED, 18))
                spawn_particles(WAYPOINTS[-1][0]-20, WAYPOINTS[-1][1], C_UI_RED, 10)
            if not e.alive and not e.reached_end:
                if e.hp <= 0 and not e.reached_end:
                    self.gold += e.gold
                    self.total_gold_earned += e.gold
                    self.total_kills += 1
                    self.score += e.gold * 10
                    self.hero.gain_xp(e.reward_xp)
                    float_texts.append(FloatText(e.x, e.y-30, f"+{e.gold}g", C_UI_GOLD, 14))
                    spawn_particles(int(e.x), int(e.y), (255,220,80), 8, speed=60)
        self.enemies = [e for e in self.enemies if e.alive or e.reached_end == False]
        self.enemies = [e for e in self.enemies if e.alive]

        # Towers
        for t in self.towers:
            t.update(dt, self.enemies, self.projectiles)

        # Projectiles
        for p in self.projectiles:
            p.update(dt, self.enemies)
        self.projectiles = [p for p in self.projectiles if p.alive]

        # Hero
        self.hero.update(dt, self.enemies)

        # Particles
        particles[:] = [p for p in particles if p.update(dt)]
        float_texts[:] = [f for f in float_texts if f.update(dt)]

        # Check lives
        if self.lives <= 0:
            self.state = GameState.GAME_OVER

        # Check victory
        if self.wave_manager.done and len(self.enemies) == 0:
            self.state = GameState.VICTORY

    def handle_click(self, mx, my, button):
        if self.state != GameState.PLAYING: return

        # Global skill placement
        for sk in GLOBAL_SKILLS:
            if sk.active and button == 1 and mx < GAME_W:
                sk.trigger(mx, my, self.enemies)
                return

        # Hero right-click move
        if button == 3 and mx < GAME_W:
            self.hero.moving_to = (mx, my)
            spawn_particles(mx, my, (255,220,80), 5, speed=40, size=3, life=0.4, gravity=0)
            return

        # Click on game area
        if button == 1 and mx < GAME_W:
            # Check tower selection — larger radius = easier to click
            clicked_tower = None
            best_dist = 32   # increased from 22 → much easier to click
            for t in self.towers:
                d = math.hypot(t.x-mx, t.y-my)
                if d < best_dist:
                    best_dist = d
                    clicked_tower = t
            if clicked_tower:
                if self.selected_tower == clicked_tower:
                    self.selected_tower = None
                    clicked_tower.selected = False
                else:
                    if self.selected_tower:
                        self.selected_tower.selected = False
                    self.selected_tower = clicked_tower
                    clicked_tower.selected = True
                self.selected_tower_type = None
                return

            # Deselect
            if self.selected_tower:
                self.selected_tower.selected = False
                self.selected_tower = None

            # Place tower
            if self.selected_tower_type:
                # Check not on path
                on_path = False
                for i in range(len(WAYPOINTS)-1):
                    x1,y1 = WAYPOINTS[i]; x2,y2 = WAYPOINTS[i+1]
                    dist = self._point_line_dist(mx, my, x1,y1,x2,y2)
                    if dist < 36:
                        on_path = True
                        break
                if not on_path:
                    # Check not overlapping
                    overlap = any(math.hypot(t.x-mx, t.y-my) < 36 for t in self.towers)
                    if not overlap:
                        self.buy_tower(self.selected_tower_type, mx, my)

    def _point_line_dist(self, px,py,x1,y1,x2,y2):
        dx,dy = x2-x1, y2-y1
        if dx==dy==0: return math.hypot(px-x1, py-y1)
        t = max(0, min(1, ((px-x1)*dx+(py-y1)*dy)/(dx*dx+dy*dy)))
        return math.hypot(px-(x1+t*dx), py-(y1+t*dy))

    def draw(self):
        # Game surface
        gs = self.game_surf
        gs.fill(C_BG)
        draw_map(gs, self.tick)

        # Tower range previews during placement
        if self.selected_tower_type and self.selected_tower_type != "barracks":
            mx, my = pygame.mouse.get_pos()
            if mx < GAME_W:
                d = TOWER_DEFS[self.selected_tower_type]
                rng = d["levels"][0]["range"]
                rs = pygame.Surface((GAME_W, GAME_H), pygame.SRCALPHA)
                pygame.draw.circle(rs, (*d["color"], 30), (mx, my), rng)
                pygame.draw.circle(rs, (*d["color"], 80), (mx, my), rng, 2)
                gs.blit(rs, (0,0))

        # Towers (bottom layer)
        mx_h, my_h = pygame.mouse.get_pos()
        for t in self.towers:
            # Draw hover ring if mouse is near and no placement mode active
            if not self.selected_tower_type and math.hypot(t.x-mx_h, t.y-my_h) < 32:
                hs = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                pygame.draw.circle(hs, (255, 255, 255, 35), (t.x, t.y), 26)
                pygame.draw.circle(hs, (255, 255, 180, 90), (t.x, t.y), 26, 2)
                gs.blit(hs, (0, 0))
            t.draw(gs)

        # Enemies
        for e in sorted(self.enemies, key=lambda e: e.y):
            e.draw(gs)

        # Hero
        self.hero.draw(gs)

        # Projectiles
        for p in self.projectiles:
            p.draw(gs)

        # Particles
        for p in particles:
            p.draw(gs)

        # Float texts
        for f in float_texts:
            f.draw(gs)

        screen.blit(gs, (0, 0))

        # Vignette over game area
        draw_vignette(screen, GAME_W, SCREEN_H, alpha=70)

        # Draw panel
        self.draw_panel()

    def draw_panel(self):
        px = PANEL_X + 10
        pw = PANEL_W - 20

        # ── Panel wood background ─────────────────────────────────
        panel_rect = pygame.Rect(PANEL_X, 0, PANEL_W, SCREEN_H)
        pygame.draw.rect(screen, C_PANEL_BG, panel_rect)

        # Wood grain vertical lines
        for xi in range(PANEL_X+4, SCREEN_W-2, 7):
            shade = random.randint(-8, 8) if not hasattr(self, '_wood_shades') else 0
            pygame.draw.line(screen, C_PANEL_WOOD, (xi, 0), (xi, SCREEN_H), 1)

        # Left border (ornate)
        pygame.draw.rect(screen, (100, 70, 28), (PANEL_X, 0, 4, SCREEN_H))
        pygame.draw.rect(screen, (140, 100, 44), (PANEL_X+1, 0, 2, SCREEN_H))

        # ── Title bar ─────────────────────────────────────────────
        title_bg = pygame.Rect(PANEL_X, 0, PANEL_W, 44)
        pygame.draw.rect(screen, (40, 28, 10), title_bg)
        pygame.draw.rect(screen, (160, 120, 44), (PANEL_X, 42, PANEL_W, 2))  # gold border
        title_surf = F_LARGE.render("⚔ KINGDOM RUSH", True, C_UI_GOLD)
        screen.blit(title_surf, (PANEL_X + PANEL_W//2 - title_surf.get_width()//2, 10))

        y = 52

        # ── Resource bar ─────────────────────────────────────────
        res_rect = pygame.Rect(px, y, pw, 48)
        pygame.draw.rect(screen, (22, 14, 6), res_rect, border_radius=5)
        pygame.draw.rect(screen, (120, 88, 32), res_rect, 2, border_radius=5)

        # Gold
        gold_bg = pygame.Rect(px+4, y+4, pw//2-6, 40)
        pygame.draw.rect(screen, (35, 24, 6), gold_bg, border_radius=4)
        pygame.draw.circle(screen, (220, 175, 40), (px+18, y+24), 10)
        pygame.draw.circle(screen, (255, 220, 80), (px+18, y+24), 8)
        pygame.draw.circle(screen, (255, 240, 130), (px+14, y+21), 3)  # shine
        gold_txt = F_MED.render(str(self.gold), True, C_UI_GOLD)
        screen.blit(gold_txt, (px+32, y+13))

        # Lives
        lives_bg = pygame.Rect(px+pw//2+2, y+4, pw//2-6, 40)
        pygame.draw.rect(screen, (35, 10, 10), lives_bg, border_radius=4)
        # Heart symbol
        hx, hy = px+pw//2+16, y+24
        pygame.draw.circle(screen, (200, 40, 40), (hx-4, hy-2), 5)
        pygame.draw.circle(screen, (200, 40, 40), (hx+4, hy-2), 5)
        pygame.draw.polygon(screen, (200, 40, 40), [(hx-8, hy-2),(hx+8, hy-2),(hx, hy+8)])
        pygame.draw.circle(screen, (240, 80, 80), (hx-5, hy-3), 3)
        lives_txt = F_MED.render(str(self.lives), True, (220, 80, 80))
        screen.blit(lives_txt, (px+pw//2+26, y+13))

        y += 56

        # Wave info strip
        wave_bg = pygame.Rect(px, y, pw, 26)
        pygame.draw.rect(screen, (18, 28, 10), wave_bg, border_radius=4)
        pygame.draw.rect(screen, C_UI_BORDER, wave_bg, 1, border_radius=4)
        wave_txt = F_SMALL.render(
            f"Wave {self.wave_manager.current_wave_num}/{self.wave_manager.total_waves}", True, C_UI_GREEN)
        screen.blit(wave_txt, (px+6, y+5))
        score_txt = F_TINY.render(f"Score: {self.score}", True, (140, 190, 140))
        screen.blit(score_txt, (px+pw-score_txt.get_width()-4, y+7))
        y += 32

        # ── Wave control button ───────────────────────────────────
        if not self.wave_manager.active and not self.wave_manager.done:
            btn_rect = pygame.Rect(px, y, pw, 32)
            mx2, my2 = pygame.mouse.get_pos()
            hover = btn_rect.collidepoint(mx2, my2)
            bg = (55, 140, 40) if hover else (38, 105, 28)
            pygame.draw.rect(screen, bg, btn_rect, border_radius=5)
            pygame.draw.rect(screen, C_UI_GREEN, btn_rect, 1, border_radius=5)
            if hover:
                draw_glow(screen, C_UI_GREEN, btn_rect.center, 30, 40)
            lbl = F_MED.render("▶  SEND WAVE", True, C_WHITE)
            screen.blit(lbl, (btn_rect.centerx-lbl.get_width()//2, btn_rect.centery-lbl.get_height()//2))
        elif self.wave_manager.active:
            prog_rect = pygame.Rect(px, y, pw, 32)
            pygame.draw.rect(screen, (28, 42, 20), prog_rect, border_radius=5)
            pygame.draw.rect(screen, C_UI_BORDER, prog_rect, 1, border_radius=5)
            ecount = len([e for e in self.enemies if e.alive])
            lbl = F_MED.render(f"⚔ Enemies: {ecount}", True, (220, 185, 75))
            screen.blit(lbl, (prog_rect.centerx-lbl.get_width()//2, prog_rect.centery-lbl.get_height()//2))
        y += 38

        # Divider ornament
        pygame.draw.line(screen, (100, 70, 28), (PANEL_X+6, y), (SCREEN_W-6, y), 1)
        pygame.draw.line(screen, (160, 120, 44), (PANEL_X+6, y+1), (SCREEN_W-6, y+1), 1)
        y += 7

        # ── BUILD TOWERS section ──────────────────────────────────
        build_lbl = F_SMALL.render("BUILD TOWERS", True, (200, 175, 110))
        screen.blit(build_lbl, (px, y))
        y += 20

        tower_types = [
            ("archer",    "Archer",    TOWER_DEFS["archer"]["levels"][0]["cost"],    TOWER_DEFS["archer"]["color"],    "🏹"),
            ("mage",      "Mage",      TOWER_DEFS["mage"]["levels"][0]["cost"],      TOWER_DEFS["mage"]["color"],      "🔮"),
            ("artillery", "Artillery", TOWER_DEFS["artillery"]["levels"][0]["cost"], TOWER_DEFS["artillery"]["color"], "💣"),
            ("ice",       "Ice",       TOWER_DEFS["ice"]["levels"][0]["cost"],       TOWER_DEFS["ice"]["color"],       "❄"),
            ("barracks",  "Barracks",  100,                                           (160,120,60),                     "⚔"),
        ]
        btn_w = (pw - 4) // 2
        mx2, my2 = pygame.mouse.get_pos()
        for i, (ttype, name, cost, col, icon) in enumerate(tower_types):
            bx = px + (i%2) * (btn_w+4)
            by2 = y + (i//2) * 46
            selected = self.selected_tower_type == ttype
            can_afford = self.gold >= cost
            # Button bg
            bg_col = (int(col[0]*0.3+8), int(col[1]*0.3+8), int(col[2]*0.3+8))
            if selected:
                bg_col = (int(col[0]*0.5+10), int(col[1]*0.5+10), int(col[2]*0.5+10))
            hover = pygame.Rect(bx, by2, btn_w, 42).collidepoint(mx2, my2)
            if hover: bg_col = tuple(min(255, c+18) for c in bg_col)
            draw_rounded_rect(screen, bg_col, (bx, by2, btn_w, 42), 4,
                2 if selected else 1,
                col if (selected or hover) else ((80, 60, 28) if can_afford else (50,50,50)))
            if selected:
                draw_glow(screen, col, (bx+btn_w//2, by2+21), 22, 45)
            # Icon and name
            icon_s = F_SMALL.render(icon, True, C_WHITE if can_afford else (80,80,80))
            screen.blit(icon_s, (bx+5, by2+5))
            name_s = F_SMALL.render(name, True, C_WHITE if can_afford else (90,90,90))
            screen.blit(name_s, (bx+24, by2+5))
            # Cost
            cost_s = F_TINY.render(f"💰{cost}g", True, C_UI_GOLD if can_afford else (100,90,40))
            screen.blit(cost_s, (bx+5, by2+24))

        y += ((len(tower_types)+1)//2) * 46 + 4

        # Divider
        pygame.draw.line(screen, (100, 70, 28), (PANEL_X+6, y), (SCREEN_W-6, y), 1)
        pygame.draw.line(screen, (160, 120, 44), (PANEL_X+6, y+1), (SCREEN_W-6, y+1), 1)
        y += 7

        # ── Selected tower info ───────────────────────────────────
        if self.selected_tower:
            t = self.selected_tower
            info_rect = pygame.Rect(px, y, pw, 116)
            pygame.draw.rect(screen, (18, 28, 14), info_rect, border_radius=5)
            pygame.draw.rect(screen, (100, 140, 60), info_rect, 1, border_radius=5)
            # Title
            tname = t.d.get("name", "Tower")
            ns = F_MED.render(f"{t.d.get('icon','⬛')} {tname}  Lv{t.level+1}", True, C_UI_GOLD)
            screen.blit(ns, (px+6, y+5))
            # Stats
            if hasattr(t, "stats") and "damage" in t.stats:
                s2 = t.stats
                lines2 = [
                    f"DMG: {s2['damage']}   SPD: {s2['attack_speed']:.1f}/s",
                    f"Range: {s2['range']}   Type: {s2['dtype']}",
                    f"Kills: {t.kills}   Dealt: {t.total_damage}",
                ]
                for li, line in enumerate(lines2):
                    ls = F_TINY.render(line, True, (175, 215, 175))
                    screen.blit(ls, (px+6, y+27+li*16))
            # Upgrade button
            uc = t.upgrade_cost
            if uc:
                can_upg = self.gold >= uc
                upg_rect = pygame.Rect(px+4, y+80, 92, 28)
                pygame.draw.rect(screen, (35,90,30) if can_upg else (45,45,45), upg_rect, border_radius=4)
                pygame.draw.rect(screen, C_UI_GREEN if can_upg else (70,70,70), upg_rect, 1, border_radius=4)
                us = F_SMALL.render(f"↑ Upgrade {uc}g", True, C_WHITE if can_upg else (90,90,90))
                screen.blit(us, (upg_rect.centerx-us.get_width()//2, upg_rect.centery-us.get_height()//2))
            # Sell button
            sell_rect = pygame.Rect(px+pw-96, y+80, 88, 28)
            pygame.draw.rect(screen, (90, 22, 22), sell_rect, border_radius=4)
            pygame.draw.rect(screen, C_UI_RED, sell_rect, 1, border_radius=4)
            ss2 = F_SMALL.render(f"💰 Sell {t.sell_value}g", True, C_WHITE)
            screen.blit(ss2, (sell_rect.centerx-ss2.get_width()//2, sell_rect.centery-ss2.get_height()//2))
            y += 124
        else:
            y += 4

        # Divider
        pygame.draw.line(screen, (100, 70, 28), (PANEL_X+6, y), (SCREEN_W-6, y), 1)
        pygame.draw.line(screen, (160, 120, 44), (PANEL_X+6, y+1), (SCREEN_W-6, y+1), 1)
        y += 7

        # ── Global Skills ─────────────────────────────────────────
        sk_lbl = F_SMALL.render("GLOBAL SKILLS", True, (200, 175, 110))
        screen.blit(sk_lbl, (px, y))
        y += 20

        for i, sk in enumerate(GLOBAL_SKILLS):
            sx2 = px + i*(pw//2+2)
            sk_rect = pygame.Rect(sx2, y, pw//2-4, 48)
            ready = sk.cd <= 0
            bg = (50, 88, 130) if sk.active else ((25, 55, 25) if ready else (22, 22, 35))
            border = (80, 200, 255) if sk.active else (C_UI_GREEN if ready else (55, 55, 75))
            pygame.draw.rect(screen, bg, sk_rect, border_radius=4)
            pygame.draw.rect(screen, border, sk_rect, 2 if sk.active else 1, border_radius=4)
            icon_s = F_LARGE.render(sk.icon, True, sk.color if ready else (90,90,110))
            screen.blit(icon_s, (sx2+6, y+6))
            name_s = F_TINY.render(sk.name, True, C_WHITE)
            screen.blit(name_s, (sx2+32, y+7))
            if ready:
                rd_s = F_TINY.render("READY", True, C_UI_GREEN)
                screen.blit(rd_s, (sx2+32, y+22))
            else:
                cd_s = F_TINY.render(f"{sk.cd:.1f}s", True, (150,150,175))
                screen.blit(cd_s, (sx2+32, y+22))
                # CD progress bar
                bar_r = pygame.Rect(sx2+4, y+40, pw//2-12, 4)
                pygame.draw.rect(screen, (35, 35, 55), bar_r, border_radius=2)
                ratio = 1 - sk.cd/sk.max_cd
                pygame.draw.rect(screen, sk.color,
                    (bar_r.x, bar_r.y, int(bar_r.w*ratio), bar_r.h), border_radius=2)
        y += 56

        # Divider
        pygame.draw.line(screen, (100, 70, 28), (PANEL_X+6, y), (SCREEN_W-6, y), 1)
        pygame.draw.line(screen, (160, 120, 44), (PANEL_X+6, y+1), (SCREEN_W-6, y+1), 1)
        y += 7

        # ── Hero panel ────────────────────────────────────────────
        hero_rect = pygame.Rect(px, y, pw, 80)
        pygame.draw.rect(screen, (18, 18, 32), hero_rect, border_radius=5)
        pygame.draw.rect(screen, (80, 55, 190), hero_rect, 1, border_radius=5)
        h = self.hero
        hero_lbl = F_SMALL.render(f"🛡  Hero  —  Level {h.level}", True, C_UI_GOLD)
        screen.blit(hero_lbl, (px+5, y+4))
        # HP bar with label
        draw_health_bar(screen, px+5, y+22, pw-10, 7, h.hp/h.max_hp)
        hp_s = F_TINY.render(f"HP {h.hp}/{h.max_hp}", True, (175, 215, 175))
        screen.blit(hp_s, (px+5, y+32))
        # XP bar
        pygame.draw.rect(screen, (28, 18, 46), (px+5, y+50, pw-10, 5), border_radius=2)
        if h.xp_next > 0:
            xp_w = int((pw-10)*h.xp/h.xp_next)
            pygame.draw.rect(screen, (115, 75, 195), (px+5, y+50, xp_w, 5), border_radius=2)
        xp_s = F_TINY.render(f"XP {h.xp}/{h.xp_next}", True, (130, 95, 195))
        screen.blit(xp_s, (px+5, y+57))
        skill_txt = f"War Cry: {'READY!' if h.skill_cd<=0 else f'{h.skill_cd:.1f}s'}"
        sc_col = C_UI_GOLD if h.skill_cd <= 0 else (130, 115, 70)
        sc_s = F_TINY.render(skill_txt, True, sc_col)
        screen.blit(sc_s, (px+pw-sc_s.get_width()-4, y+4))
        y += 86

        # ── Controls hint ─────────────────────────────────────────
        hints = [
            "Left-click: Build/Select",
            "Right-click: Move Hero",
            "H: Hero War Cry",
            "Space: Pause  |  ESC: Cancel",
        ]
        for hint in hints:
            hs = F_TINY.render(hint, True, (90, 120, 90))
            screen.blit(hs, (px, y))
            y += 13

# ─────────────────────────────────────────
# MENU SCREEN
# ─────────────────────────────────────────
def draw_menu(tick):
    # ── Sky gradient background ───────────────────────────────────
    for row in range(SCREEN_H):
        t2 = row / SCREEN_H
        r = int(18 + (45-18)*t2)
        g = int(30 + (62-30)*t2)
        b = int(55 + (25-55)*t2)
        pygame.draw.line(screen, (r, g, b), (0, row), (SCREEN_W, row))

    # Stars in upper sky
    star_rng = random.Random(99)
    for i in range(80):
        sx = star_rng.randint(0, SCREEN_W)
        sy = star_rng.randint(0, SCREEN_H//3)
        twinkle = int(128 + 127*math.sin(tick*0.03 + i*0.8))
        sc = (twinkle, twinkle, min(255, twinkle+40))
        pygame.draw.circle(screen, sc, (sx, sy), 1 if star_rng.random() > 0.3 else 2)

    # ── Mountain silhouettes ──────────────────────────────────────
    pts2 = [(0, SCREEN_H)]
    for xi in range(0, SCREEN_W+20, 16):
        h2 = int(110 + 85*math.sin(xi*0.007) + 55*math.sin(xi*0.019+1.4))
        pts2.append((xi, SCREEN_H//2+20-h2))
    pts2.append((SCREEN_W, SCREEN_H))
    pygame.draw.polygon(screen, (35, 52, 42), pts2)

    pts3 = [(0, SCREEN_H)]
    for xi in range(0, SCREEN_W+12, 10):
        h3 = int(65 + 45*math.sin(xi*0.011+0.6) + 35*math.sin(xi*0.028+2.2))
        pts3.append((xi, SCREEN_H//2+80-h3))
    pts3.append((SCREEN_W, SCREEN_H))
    pygame.draw.polygon(screen, (24, 40, 24), pts3)

    # ── Ground / grass strip ─────────────────────────────────────
    pygame.draw.rect(screen, (32, 62, 28), (0, SCREEN_H*2//3, SCREEN_W, SCREEN_H//3))
    # Grass blades
    for i in range(60):
        gx2 = (i*173 + tick//4) % SCREEN_W
        gy2 = SCREEN_H*2//3
        pygame.draw.line(screen, (50, 90, 42), (gx2, gy2), (gx2+random.randint(-2,2), gy2-random.randint(4,12)), 1)

    # ── Decorative towers ─────────────────────────────────────────
    for tx2, ty2, ttype in [(260, 430, "archer"), (640, 420, "mage"), (1020, 430, "artillery")]:
        dummy = Tower(ttype, tx2, ty2)
        dummy.anim_tick = tick
        dummy.draw(screen)

    # ── Title banner ──────────────────────────────────────────────
    # Banner background
    banner_rect = pygame.Rect(SCREEN_W//2-320, 120, 640, 120)
    ban_surf = pygame.Surface((640, 120), pygame.SRCALPHA)
    pygame.draw.rect(ban_surf, (0, 0, 0, 140), (0, 0, 640, 120), border_radius=12)
    pygame.draw.rect(ban_surf, (160, 120, 44, 200), (0, 0, 640, 120), 2, border_radius=12)
    screen.blit(ban_surf, banner_rect.topleft)

    # Corner ornaments
    for cx2, cy2 in [(banner_rect.left+14, banner_rect.top+14), (banner_rect.right-14, banner_rect.top+14),
                     (banner_rect.left+14, banner_rect.bottom-14), (banner_rect.right-14, banner_rect.bottom-14)]:
        pygame.draw.circle(screen, C_UI_GOLD, (cx2, cy2), 6)
        pygame.draw.circle(screen, (255, 240, 120), (cx2, cy2), 3)

    t1 = F_TITLE.render("⚔  KINGDOM RUSH  ⚔", True, C_UI_GOLD)
    screen.blit(t1, (SCREEN_W//2 - t1.get_width()//2, 140))
    t2_txt = F_MED.render("Tower Defense", True, (200, 230, 160))
    screen.blit(t2_txt, (SCREEN_W//2 - t2_txt.get_width()//2, 192))

    # Subtitle
    sub = F_SMALL.render("Defend your kingdom from the relentless horde!", True, (160, 195, 155))
    screen.blit(sub, (SCREEN_W//2 - sub.get_width()//2, 260))

    # ── Start button ──────────────────────────────────────────────
    pulse = int(8*math.sin(tick*0.06))
    btn_rect = pygame.Rect(SCREEN_W//2-130, 500, 260, 58)
    mx3, my3 = pygame.mouse.get_pos()
    hover = btn_rect.collidepoint(mx3, my3)
    bg = (58+pulse, 145+pulse//2, 42) if hover else (38, 105, 28)
    pygame.draw.rect(screen, bg, btn_rect, border_radius=10)
    pygame.draw.rect(screen, C_UI_GREEN, btn_rect, 2, border_radius=10)
    if hover:
        draw_glow(screen, C_UI_GREEN, btn_rect.center, 44, 65)
    lbl = F_LARGE.render("▶  START GAME", True, C_WHITE)
    screen.blit(lbl, (btn_rect.centerx-lbl.get_width()//2, btn_rect.centery-lbl.get_height()//2))

    # Info tips
    info_lines = [
        "🏹 Build towers to stop the enemy advance",
        "🛡 Command your Hero with right-click",
        "💰 Kill enemies to earn gold",
        "☄ Unleash powerful global skills",
    ]
    for i, line in enumerate(info_lines):
        s2 = F_SMALL.render(line, True, (130, 175, 128))
        screen.blit(s2, (SCREEN_W//2 - s2.get_width()//2, 578 + i*22))

    return btn_rect

def draw_game_over(score):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0,0,0,180))
    screen.blit(overlay, (0,0))
    t = F_TITLE.render("💀 GAME OVER 💀", True, (220,60,60))
    screen.blit(t, (SCREEN_W//2-t.get_width()//2, 250))
    s2 = F_LARGE.render(f"Score: {score}", True, C_UI_GOLD)
    screen.blit(s2, (SCREEN_W//2-s2.get_width()//2, 320))
    btn = pygame.Rect(SCREEN_W//2-110, 400, 220, 50)
    draw_rounded_rect(screen, (100,20,20), btn, 8, 2, (220,60,60))
    bl = F_LARGE.render("↺  RETRY", True, C_WHITE)
    screen.blit(bl, (btn.centerx-bl.get_width()//2, btn.centery-bl.get_height()//2))
    return btn

def draw_victory(score):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0,0,0,160))
    screen.blit(overlay, (0,0))
    t = F_TITLE.render("✨ VICTORY! ✨", True, C_UI_GOLD)
    screen.blit(t, (SCREEN_W//2-t.get_width()//2, 230))
    s2 = F_LARGE.render("Kingdom is saved!", True, (160,220,160))
    screen.blit(s2, (SCREEN_W//2-s2.get_width()//2, 290))
    s3 = F_LARGE.render(f"Final Score: {score}", True, C_UI_GOLD)
    screen.blit(s3, (SCREEN_W//2-s3.get_width()//2, 340))
    btn = pygame.Rect(SCREEN_W//2-110, 420, 220, 50)
    draw_rounded_rect(screen, (30,90,30), btn, 8, 2, C_UI_GREEN)
    bl = F_LARGE.render("↺  PLAY AGAIN", True, C_WHITE)
    screen.blit(bl, (btn.centerx-bl.get_width()//2, btn.centery-bl.get_height()//2))
    return btn

def draw_pause():
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0,0,0,120))
    screen.blit(overlay, (0,0))
    t = F_TITLE.render("⏸ PAUSED", True, C_WHITE)
    screen.blit(t, (SCREEN_W//2-t.get_width()//2, SCREEN_H//2-40))
    s2 = F_MED.render("Press SPACE to resume", True, (160,200,160))
    screen.blit(s2, (SCREEN_W//2-s2.get_width()//2, SCREEN_H//2+20))

# ─────────────────────────────────────────
# PANEL CLICK HANDLER  (Y coords synced with draw_panel)
# ─────────────────────────────────────────
def _panel_layout(game):
    """Return dict of Y positions matching draw_panel layout exactly."""
    px  = PANEL_X + 10
    pw  = PANEL_W - 20
    y   = 52
    y  += 56   # resource bar (h=48) + gap
    y  += 32   # wave info strip (h=26) + gap
    wave_y = y          # ← SEND WAVE button starts here (h=32)
    y  += 38   # wave btn (h=32) + gap
    y  += 7    # divider
    y  += 20   # BUILD TOWERS label
    tower_y = y         # ← tower buttons start here
    btn_w = (pw - 4) // 2
    tower_rows = (5 + 1) // 2   # 3 rows
    y  += tower_rows * 46 + 4
    y  += 7    # divider
    sel_y = y           # ← selected-tower info starts here (if any)
    if game.selected_tower:
        upg_y    = sel_y + 80
        sell_x   = px + pw - 96
        y       += 124
    else:
        upg_y    = None
        sell_x   = None
        y       += 4
    y  += 7    # divider
    y  += 20   # GLOBAL SKILLS label
    skill_y = y         # ← skill buttons start here
    return dict(px=px, pw=pw, btn_w=btn_w,
                wave_y=wave_y, tower_y=tower_y,
                sel_y=sel_y, upg_y=upg_y, sell_x=sell_x,
                skill_y=skill_y)


def handle_panel_click(game, mx, my):
    L  = _panel_layout(game)
    px = L["px"]; pw = L["pw"]; btn_w = L["btn_w"]

    # ── SEND WAVE button ──────────────────────────────────────────
    wave_btn = pygame.Rect(px, L["wave_y"], pw, 32)
    if wave_btn.collidepoint(mx, my):
        if not game.wave_manager.active and not game.wave_manager.done:
            game.wave_manager.start_wave()
        return

    # ── Tower build buttons ───────────────────────────────────────
    tower_types = ["archer", "mage", "artillery", "ice", "barracks"]
    for i, ttype in enumerate(tower_types):
        bx = px + (i % 2) * (btn_w + 4)
        by = L["tower_y"] + (i // 2) * 46
        if pygame.Rect(bx, by, btn_w, 42).collidepoint(mx, my):
            if game.selected_tower_type == ttype:
                game.selected_tower_type = None
            else:
                game.selected_tower_type = ttype
                if game.selected_tower:
                    game.selected_tower.selected = False
                    game.selected_tower = None
            return

    # ── Selected tower: Upgrade / Sell ────────────────────────────
    if game.selected_tower and L["upg_y"] is not None:
        t  = game.selected_tower
        upg_rect  = pygame.Rect(px + 4,          L["upg_y"], 92,  28)
        sell_rect = pygame.Rect(L["sell_x"],      L["upg_y"], 88,  28)
        if upg_rect.collidepoint(mx, my):
            uc = t.upgrade_cost
            if uc and game.gold >= uc:
                game.gold -= uc
                t.upgrade()
            return
        if sell_rect.collidepoint(mx, my):
            game.gold += t.sell_value
            float_texts.append(FloatText(t.x, t.y - 30, f"+{t.sell_value}g", C_UI_GOLD, 15))
            game.towers.remove(t)
            game.selected_tower = None
            return

    # ── Global skill buttons ──────────────────────────────────────
    sk_w = pw // 2 - 4
    for i, sk in enumerate(GLOBAL_SKILLS):
        sx2 = px + i * (pw // 2 + 2)
        sk_rect = pygame.Rect(sx2, L["skill_y"], sk_w, 48)
        if sk_rect.collidepoint(mx, my):
            sk.use()
            return

# ─────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────
def main():
    game = Game()
    menu_tick = 0

    while True:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)  # cap delta time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if game.state == GameState.MENU:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    btn = draw_menu(menu_tick)
                    if btn.collidepoint(event.pos):
                        game.start()

            elif game.state == GameState.PLAYING:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if mx >= PANEL_X:
                        handle_panel_click(game, mx, my)
                    else:
                        game.handle_click(mx, my, event.button)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game.selected_tower_type = None
                        if game.selected_tower:
                            game.selected_tower.selected = False
                            game.selected_tower = None
                        for sk in GLOBAL_SKILLS:
                            sk.active = False
                    elif event.key == pygame.K_SPACE:
                        game.state = GameState.PAUSED
                    elif event.key == pygame.K_h:
                        game.hero.use_skill(game.enemies)
                    elif event.key == pygame.K_1:
                        game.selected_tower_type = "archer"
                    elif event.key == pygame.K_2:
                        game.selected_tower_type = "mage"
                    elif event.key == pygame.K_3:
                        game.selected_tower_type = "artillery"
                    elif event.key == pygame.K_4:
                        game.selected_tower_type = "ice"
                    elif event.key == pygame.K_5:
                        game.selected_tower_type = "barracks"

            elif game.state == GameState.PAUSED:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game.state = GameState.PLAYING

            elif game.state in (GameState.GAME_OVER, GameState.VICTORY):
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    game.start()
                    game.state = GameState.PLAYING
                    game.wave_manager.start_wave()

        # Update
        if game.state == GameState.MENU:
            menu_tick += 1
            screen.fill((8,14,8))
            draw_menu(menu_tick)
        elif game.state == GameState.PLAYING:
            game.update(dt)
            game.draw()
        elif game.state == GameState.PAUSED:
            game.draw()
            draw_pause()
        elif game.state == GameState.GAME_OVER:
            game.draw()
            draw_game_over(game.score)
        elif game.state == GameState.VICTORY:
            game.draw()
            # Victory particles
            if random.random() < 0.3:
                spawn_particles(
                    random.randint(0, SCREEN_W),
                    random.randint(0, SCREEN_H//2),
                    random.choice([(255,220,60),(80,200,255),(200,60,255)]),
                    8, speed=100, size=5, life=1.5, gravity=50)
            for p in particles:
                p.update(dt)
                p.draw(screen)
            draw_victory(game.score)

        pygame.display.flip()

if __name__ == "__main__":
    main()
