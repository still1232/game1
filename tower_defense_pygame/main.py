"""
TOWER DEFENSE GAME - PYTHON + PYGAME
Core Game Template Implementation

🎮 Core Loop: Init → Handle Input → Update → Render → Check Win/Lose
🧩 Core Systems: GameManager, MapSystem, WaveSystem, EnemySystem, TowerSystem, ProjectileSystem, CombatSystem, ResourceSystem, RenderSystem
"""

import pygame
import math
import json
import random
from enum import Enum
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path

# Initialize Pygame
pygame.init()
# Skip mixer init for headless environments (can be enabled if audio is available)
try:
    pygame.mixer.init()
except:
    print("Warning: Audio mixer not available, running without sound")

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Asset paths
ASSETS_DIR = Path(__file__).parent / "assets"
ENEMY_SPRITES_DIR = ASSETS_DIR / "enemy"
TOWER_SPRITES_DIR = ASSETS_DIR / "tower"
PROJECTILE_SPRITES_DIR = ASSETS_DIR / "projectile"
MAP_SPRITES_DIR = ASSETS_DIR / "map"

# Sprite cache
SPRITE_CACHE = {}

def load_sprite(path: Path, size: Tuple[int, int] = None) -> Optional[pygame.Surface]:
    """Load a sprite from file with optional resizing"""
    if path in SPRITE_CACHE:
        return SPRITE_CACHE[path]
    
    try:
        if path.exists():
            sprite = pygame.image.load(str(path)).convert_alpha()
            if size:
                sprite = pygame.transform.smoothscale(sprite, size)
            SPRITE_CACHE[path] = sprite
            return sprite
    except Exception as e:
        print(f"Warning: Could not load sprite {path}: {e}")
    return None

def get_enemy_sprite(enemy_type: str, size: int) -> Optional[pygame.Surface]:
    """Get sprite for enemy type"""
    sprite_files = {
        "goblin": ENEMY_SPRITES_DIR / "goblin.png",
        "orc": ENEMY_SPRITES_DIR / "orc.png",
        "boss": ENEMY_SPRITES_DIR / "orc.png"  # Use orc as fallback for boss
    }
    path = sprite_files.get(enemy_type)
    if path:
        return load_sprite(path, (size, size))
    return None

def get_tower_sprite(tower_type: str, size: int) -> Optional[pygame.Surface]:
    """Get sprite for tower type"""
    sprite_files = {
        "archer": TOWER_SPRITES_DIR / "archer.png",
        "cannon": TOWER_SPRITES_DIR / "cannon.png"
    }
    path = sprite_files.get(tower_type)
    if path:
        return load_sprite(path, (size, size))
    return None

def get_projectile_sprite(projectile_type: str, size: int) -> Optional[pygame.Surface]:
    """Get sprite for projectile type"""
    sprite_files = {
        "arrow": PROJECTILE_SPRITES_DIR / "arrow.png",
        "cannonball": PROJECTILE_SPRITES_DIR / "cannonball.png"
    }
    path = sprite_files.get(projectile_type)
    if path:
        return load_sprite(path, (size, size))
    return None

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)
DARK_GREEN = (34, 139, 34)
LIGHT_GREEN = (144, 238, 144)
BROWN = (139, 69, 19)
SAND = (244, 164, 96)

# ============================================================================
# DATA TEMPLATES
# ============================================================================

MAP_TEMPLATE = {
    "map_id": "grassland",
    "background_color": DARK_GREEN,
    "path_color": SAND,
    "path_width": 40,
    "path": [
        [50, 384],
        [200, 384],
        [200, 200],
        [400, 200],
        [400, 500],
        [600, 500],
        [600, 300],
        [800, 300],
        [800, 400],
        [950, 400]
    ],
    "build_nodes": [
        {"x": 150, "y": 300},
        {"x": 250, "y": 450},
        {"x": 350, "y": 150},
        {"x": 450, "y": 350},
        {"x": 550, "y": 450},
        {"x": 650, "y": 250},
        {"x": 750, "y": 350}
    ]
}

ENEMY_TEMPLATES = {
    "goblin": {
        "id": "goblin",
        "color": GREEN,
        "hp": 100,
        "speed": 60,
        "armor": 2,
        "gold_drop": 10,
        "type": "ground",
        "size": 24,
        "animation_frames": 4
    },
    "orc": {
        "id": "orc",
        "color": ORANGE,
        "hp": 200,
        "speed": 40,
        "armor": 5,
        "gold_drop": 20,
        "type": "ground",
        "size": 32,
        "animation_frames": 4
    },
    "boss": {
        "id": "boss",
        "color": PURPLE,
        "hp": 500,
        "speed": 30,
        "armor": 10,
        "gold_drop": 50,
        "type": "ground",
        "size": 40,
        "animation_frames": 4
    }
}

TOWER_TEMPLATES = {
    "archer": {
        "id": "archer",
        "color": BLUE,
        "damage": 25,
        "range": 150,
        "attack_speed": 1.0,
        "projectile": "arrow",
        "cost": 50,
        "size": 32
    },
    "cannon": {
        "id": "cannon",
        "color": RED,
        "damage": 50,
        "range": 120,
        "attack_speed": 2.0,
        "projectile": "cannonball",
        "cost": 100,
        "size": 40,
        "aoe_radius": 60
    }
}

PROJECTILE_TEMPLATES = {
    "arrow": {
        "id": "arrow",
        "color": YELLOW,
        "speed": 300,
        "damage": 25,
        "aoe": False,
        "size": 8
    },
    "cannonball": {
        "id": "cannonball",
        "color": BLACK,
        "speed": 200,
        "damage": 50,
        "aoe": True,
        "aoe_radius": 60,
        "size": 12
    }
}

WAVE_TEMPLATES = [
    {
        "wave": 1,
        "enemies": [
            {"type": "goblin", "count": 10, "spawn_delay": 1.0}
        ]
    },
    {
        "wave": 2,
        "enemies": [
            {"type": "goblin", "count": 15, "spawn_delay": 0.8},
            {"type": "orc", "count": 5, "spawn_delay": 2.0}
        ]
    },
    {
        "wave": 3,
        "enemies": [
            {"type": "goblin", "count": 20, "spawn_delay": 0.6},
            {"type": "orc", "count": 10, "spawn_delay": 1.5},
            {"type": "boss", "count": 2, "spawn_delay": 5.0}
        ]
    }
]


# ============================================================================
# ENUMS & STATE MACHINES
# ============================================================================

class EnemyState(Enum):
    SPAWN = 1
    MOVE = 2
    BLOCKED = 3
    ATTACK = 4
    DEAD = 5
    ESCAPE = 6


class TowerState(Enum):
    IDLE = 1
    FIND_TARGET = 2
    ATTACK = 3
    COOLDOWN = 4


class GameState(Enum):
    INIT = 1
    PLAYING = 2
    WAVE_COMPLETE = 3
    GAME_OVER = 4
    VICTORY = 5


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Vector2:
    x: float
    y: float
    
    def distance_to(self, other: 'Vector2') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def direction_to(self, other: 'Vector2') -> Tuple[float, float]:
        dx = other.x - self.x
        dy = other.y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0:
            return (0, 0)
        return (dx / dist, dy / dist)


@dataclass
class Enemy:
    id: str
    position: Vector2
    hp: int
    max_hp: int
    speed: float
    armor: int
    gold_drop: int
    enemy_type: str
    size: int
    state: EnemyState = EnemyState.SPAWN
    current_waypoint: int = 0
    animation_frame: int = 0
    animation_timer: float = 0
    spawn_invincible: float = 0.5  # seconds


@dataclass
class Tower:
    id: str
    position: Vector2
    tower_type: str
    damage: int
    range: float
    attack_speed: float
    projectile_type: str
    cost: int
    size: int
    state: TowerState = TowerState.IDLE
    current_target: Optional[Enemy] = None
    cooldown_timer: float = 0
    animation_frame: int = 0
    animation_timer: float = 0
    aoe_radius: float = 0


@dataclass
class Projectile:
    id: str
    position: Vector2
    target: Enemy
    projectile_type: str
    speed: float
    damage: int
    aoe: bool
    aoe_radius: float = 0
    size: int = 8
    active: bool = True


@dataclass 
class Resource:
    gold: int = 150
    lives: int = 20
    wave: int = 0


# ============================================================================
# CORE SYSTEMS
# ============================================================================

class MapSystem:
    """Handles map rendering and path navigation"""
    
    def __init__(self, map_data: Dict):
        self.map_data = map_data
        self.path_points = [Vector2(p[0], p[1]) for p in map_data["path"]]
        self.build_nodes = [Vector2(n["x"], n["y"]) for n in map_data["build_nodes"]]
        
    def get_spawn_point(self) -> Vector2:
        return self.path_points[0]
    
    def get_end_point(self) -> Vector2:
        return self.path_points[-1]
    
    def is_on_path(self, pos: Vector2, tolerance: float = 30) -> bool:
        """Check if position is on the path"""
        for i in range(len(self.path_points) - 1):
            p1 = self.path_points[i]
            p2 = self.path_points[i + 1]
            
            # Distance from point to line segment
            dist = self._point_to_segment_distance(pos, p1, p2)
            if dist <= tolerance:
                return True
        return False
    
    def _point_to_segment_distance(self, p: Vector2, a: Vector2, b: Vector2) -> float:
        """Calculate distance from point p to line segment ab"""
        ap_x = p.x - a.x
        ap_y = p.y - a.y
        ab_x = b.x - a.x
        ab_y = b.y - a.y
        
        ab_len_sq = ab_x**2 + ab_y**2
        if ab_len_sq == 0:
            return p.distance_to(a)
        
        t = max(0, min(1, (ap_x * ab_x + ap_y * ab_y) / ab_len_sq))
        proj_x = a.x + t * ab_x
        proj_y = a.y + t * ab_y
        
        return math.sqrt((p.x - proj_x)**2 + (p.y - proj_y)**2)
    
    def is_valid_build_position(self, pos: Vector2, tower_size: int) -> bool:
        """Check if tower can be built at position"""
        # Must be on a build node
        for node in self.build_nodes:
            if pos.distance_to(node) < tower_size:
                return True
        return False
    
    def render(self, screen: pygame.Surface):
        """Render the map"""
        # Background
        screen.fill(self.map_data["background_color"])
        
        # Draw path
        path_points = [(p.x, p.y) for p in self.path_points]
        if len(path_points) > 1:
            pygame.draw.lines(screen, self.map_data["path_color"], False, path_points, self.map_data["path_width"])
            # Draw path border
            pygame.draw.lines(screen, BROWN, False, path_points, self.map_data["path_width"] + 4, 2)
        
        # Draw build nodes
        for node in self.build_nodes:
            # Base platform
            pygame.draw.circle(screen, GRAY, (int(node.x), int(node.y)), 25)
            pygame.draw.circle(screen, WHITE, (int(node.x), int(node.y)), 25, 2)
        
        # Draw start and end markers
        spawn = self.get_spawn_point()
        end = self.get_end_point()
        
        pygame.draw.circle(screen, GREEN, (int(spawn.x), int(spawn.y)), 20)
        pygame.draw.circle(screen, RED, (int(end.x), int(end.y)), 20)
        
        # Draw arrows on path
        font = pygame.font.Font(None, 24)
        start_text = font.render("START", True, BLACK)
        end_text = font.render("END", True, BLACK)
        screen.blit(start_text, (spawn.x - 30, spawn.y - 30))
        screen.blit(end_text, (end.x - 20, end.y - 30))


class EnemySystem:
    """Handles enemy spawning, movement, and state machine"""
    
    def __init__(self, map_system: MapSystem):
        self.map_system = map_system
        self.enemies: List[Enemy] = []
        self.spawn_queue: List[Dict] = []
        self.spawn_timer: float = 0
        
    def add_wave(self, wave_data: Dict):
        """Add enemies from wave to spawn queue"""
        for enemy_info in wave_data["enemies"]:
            template = ENEMY_TEMPLATES[enemy_info["type"]]
            for _ in range(enemy_info["count"]):
                self.spawn_queue.append({
                    "type": enemy_info["type"],
                    "delay": enemy_info["spawn_delay"],
                    "template": template
                })
    
    def spawn_enemy(self, enemy_type: str, template: Dict):
        """Spawn a new enemy"""
        spawn_pos = self.map_system.get_spawn_point()
        enemy = Enemy(
            id=enemy_type,
            position=Vector2(spawn_pos.x, spawn_pos.y),
            hp=template["hp"],
            max_hp=template["hp"],
            speed=template["speed"],
            armor=template["armor"],
            gold_drop=template["gold_drop"],
            enemy_type=enemy_type,
            size=template["size"]
        )
        enemy.state = EnemyState.MOVE
        self.enemies.append(enemy)
    
    def update(self, dt: float):
        """Update all enemies"""
        # Handle spawning
        if self.spawn_queue:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                next_enemy = self.spawn_queue.pop(0)
                self.spawn_enemy(next_enemy["type"], next_enemy["template"])
                self.spawn_timer = next_enemy["delay"]
        
        # Update each enemy
        for enemy in self.enemies[:]:
            self._update_enemy(enemy, dt)
    
    def _update_enemy(self, enemy: Enemy, dt: float):
        """Update single enemy"""
        if enemy.state == EnemyState.DEAD or enemy.state == EnemyState.ESCAPE:
            return
        
        # Animation
        enemy.animation_timer += dt
        if enemy.animation_timer >= 0.15:  # Change frame every 150ms
            enemy.animation_frame = (enemy.animation_frame + 1) % enemy_templates[enemy.enemy_type]["animation_frames"]
            enemy.animation_timer = 0
        
        # Movement
        if enemy.state == EnemyState.MOVE:
            self._move_enemy(enemy, dt)
    
    def _move_enemy(self, enemy: Enemy, dt: float):
        """Move enemy along path"""
        if enemy.current_waypoint >= len(self.map_system.path_points) - 1:
            # Reached end
            enemy.state = EnemyState.ESCAPE
            return
        
        target = self.map_system.path_points[enemy.current_waypoint + 1]
        direction = enemy.position.direction_to(target)
        
        move_distance = enemy.speed * dt
        enemy.position.x += direction[0] * move_distance
        enemy.position.y += direction[1] * move_distance
        
        # Check if reached waypoint
        if enemy.position.distance_to(target) < 10:
            enemy.current_waypoint += 1
    
    def take_damage(self, enemy: Enemy, damage: int) -> int:
        """Apply damage to enemy, return actual damage dealt"""
        actual_damage = max(1, damage - enemy.armor)
        enemy.hp -= actual_damage
        
        if enemy.hp <= 0:
            enemy.state = EnemyState.DEAD
        
        return actual_damage
    
    def remove_dead(self) -> List[Enemy]:
        """Remove dead/enemy escaped enemies and return them"""
        removed = []
        self.enemies = [e for e in self.enemies if e.state not in [EnemyState.DEAD, EnemyState.ESCAPE]]
        return removed
    
    def has_active_enemies(self) -> bool:
        """Check if there are active enemies"""
        return len(self.enemies) > 0 or len(self.spawn_queue) > 0
    
    def render(self, screen: pygame.Surface):
        """Render all enemies"""
        for enemy in self.enemies:
            if enemy.state in [EnemyState.DEAD, EnemyState.ESCAPE]:
                continue
            
            # Try to load sprite first, fallback to procedural drawing
            sprite = get_enemy_sprite(enemy.enemy_type, enemy.size)
            
            if sprite:
                # Draw sprite centered on enemy position
                rect = sprite.get_rect(center=(int(enemy.position.x), int(enemy.position.y)))
                screen.blit(sprite, rect)
            else:
                # Fallback: Draw enemy body with animation wobble
                wobble = math.sin(enemy.animation_frame * math.pi / 2) * 3
                size = enemy.size + int(wobble)
                
                pygame.draw.circle(screen, enemy_templates[enemy.enemy_type]["color"], 
                                 (int(enemy.position.x), int(enemy.position.y)), size // 2)
                
                # Draw eyes
                eye_offset = size // 6
                pygame.draw.circle(screen, WHITE, 
                                 (int(enemy.position.x) - eye_offset, int(enemy.position.y) - eye_offset//2), size // 6)
                pygame.draw.circle(screen, WHITE, 
                                 (int(enemy.position.x) + eye_offset, int(enemy.position.y) - eye_offset//2), size // 6)
            
            # HP bar (always drawn)
            hp_bar_width = enemy.size
            hp_bar_height = 4
            hp_percent = enemy.hp / enemy.max_hp
            
            pygame.draw.rect(screen, RED, 
                           (enemy.position.x - hp_bar_width//2, enemy.position.y - enemy.size//2 - 10, 
                            hp_bar_width, hp_bar_height))
            pygame.draw.rect(screen, GREEN, 
                           (enemy.position.x - hp_bar_width//2, enemy.position.y - enemy.size//2 - 10, 
                            hp_bar_width * hp_percent, hp_bar_height))


class TowerSystem:
    """Handles tower placement, targeting, and attacks"""
    
    def __init__(self, map_system: MapSystem, resource_system: 'ResourceSystem'):
        self.map_system = map_system
        self.resource_system = resource_system
        self.towers: List[Tower] = []
        self.selected_tower_type: Optional[str] = None
        self.preview_position: Optional[Vector2] = None
        
    def select_tower(self, tower_type: str):
        """Select tower type for placement"""
        self.selected_tower_type = tower_type
    
    def try_place_tower(self, pos: Vector2) -> bool:
        """Try to place tower at position"""
        if not self.selected_tower_type:
            return False
        
        template = TOWER_TEMPLATES[self.selected_tower_type]
        
        # Check resources
        if self.resource_system.gold < template["cost"]:
            return False
        
        # Check if position is valid
        if not self.map_system.is_valid_build_position(pos, template["size"]):
            return False
        
        # Check if tower already exists at position
        for tower in self.towers:
            if pos.distance_to(tower.position) < tower.size:
                return False
        
        # Place tower
        tower = Tower(
            id=self.selected_tower_type,
            position=Vector2(pos.x, pos.y),
            tower_type=self.selected_tower_type,
            damage=template["damage"],
            range=template["range"],
            attack_speed=template["attack_speed"],
            projectile_type=template["projectile"],
            cost=template["cost"],
            size=template["size"],
            aoe_radius=template.get("aoe_radius", 0)
        )
        
        self.towers.append(tower)
        self.resource_system.deduct_gold(template["cost"])
        self.selected_tower_type = None
        
        return True
    
    def update(self, dt: float, enemies: List[Enemy]) -> List[Projectile]:
        """Update all towers and return projectiles to spawn"""
        projectiles = []
        
        for tower in self.towers:
            proj = self._update_tower(tower, dt, enemies)
            if proj:
                projectiles.append(proj)
        
        return projectiles
    
    def _update_tower(self, tower: Tower, dt: float, enemies: List[Enemy]) -> Optional[Projectile]:
        """Update single tower"""
        # Cooldown
        if tower.cooldown_timer > 0:
            tower.cooldown_timer -= dt
            if tower.cooldown_timer <= 0:
                tower.state = TowerState.FIND_TARGET
        
        # Find target
        if tower.state in [TowerState.IDLE, TowerState.FIND_TARGET]:
            tower.current_target = self._find_target(tower, enemies)
            if tower.current_target:
                tower.state = TowerState.ATTACK
        
        # Attack
        if tower.state == TowerState.ATTACK and tower.current_target:
            # Check if target still valid
            if tower.current_target.state in [EnemyState.DEAD, EnemyState.ESCAPE]:
                tower.current_target = None
                tower.state = TowerState.FIND_TARGET
            elif tower.position.distance_to(tower.current_target.position) <= tower.range:
                # Fire!
                tower.state = TowerState.COOLDOWN
                tower.cooldown_timer = tower.attack_speed
                tower.animation_frame = 1
                tower.animation_timer = 0
                
                return Projectile(
                    id=tower.projectile_type,
                    position=Vector2(tower.position.x, tower.position.y),
                    target=tower.current_target,
                    projectile_type=tower.projectile_type,
                    speed=PROJECTILE_TEMPLATES[tower.projectile_type]["speed"],
                    damage=tower.damage,
                    aoe=PROJECTILE_TEMPLATES[tower.projectile_type].get("aoe", False),
                    aoe_radius=PROJECTILE_TEMPLATES[tower.projectile_type].get("aoe_radius", 0),
                    size=PROJECTILE_TEMPLATES[tower.projectile_type]["size"]
                )
        
        # Animation
        if tower.animation_timer >= 0.1:
            tower.animation_frame = 0
            tower.animation_timer = 0
        else:
            tower.animation_timer += dt
        
        return None
    
    def _find_target(self, tower: Tower, enemies: List[Enemy]) -> Optional[Enemy]:
        """Find closest enemy in range"""
        closest = None
        closest_dist = tower.range
        
        for enemy in enemies:
            if enemy.state in [EnemyState.DEAD, EnemyState.ESCAPE]:
                continue
            
            dist = tower.position.distance_to(enemy.position)
            if dist <= closest_dist:
                closest_dist = dist
                closest = enemy
        
        return closest
    
    def set_preview_position(self, pos: Vector2):
        """Set preview position for tower placement"""
        self.preview_position = pos
    
    def render(self, screen: pygame.Surface):
        """Render all towers"""
        # Render placed towers
        for tower in self.towers:
            # Try to load sprite first, fallback to procedural drawing
            sprite = get_tower_sprite(tower.tower_type, tower.size)
            
            if sprite:
                # Draw sprite centered on tower position
                rect = sprite.get_rect(center=(int(tower.position.x), int(tower.position.y)))
                
                # Apply attack animation scaling if attacking
                if tower.animation_frame == 1:
                    scaled_sprite = pygame.transform.smoothscale(sprite, (int(tower.size * 1.2), int(tower.size * 1.2)))
                    rect = scaled_sprite.get_rect(center=(int(tower.position.x), int(tower.position.y)))
                    screen.blit(scaled_sprite, rect)
                else:
                    screen.blit(sprite, rect)
            else:
                # Fallback: Draw tower base
                pygame.draw.circle(screen, GRAY, (int(tower.position.x), int(tower.position.y)), tower.size // 2 + 5)
                
                # Draw tower body with animation
                color = TOWER_TEMPLATES[tower.tower_type]["color"]
                size = tower.size // 2
                
                if tower.animation_frame == 1:
                    # Attack animation - slightly larger
                    size = int(size * 1.2)
                
                pygame.draw.circle(screen, color, (int(tower.position.x), int(tower.position.y)), size)
            
            # Draw turret direction (if has target) - always drawn
            if tower.current_target:
                direction = tower.position.direction_to(tower.current_target.position)
                end_x = tower.position.x + direction[0] * (tower.range * 0.3)
                end_y = tower.position.y + direction[1] * (tower.range * 0.3)
                pygame.draw.line(screen, BLACK, 
                               (tower.position.x, tower.position.y), 
                               (end_x, end_y), 4)
        
        # Render preview
        if self.selected_tower_type and self.preview_position:
            template = TOWER_TEMPLATES[self.selected_tower_type]
            can_build = self.map_system.is_valid_build_position(self.preview_position, template["size"])
            
            # Draw range circle
            surf = pygame.Surface((template["range"] * 2, template["range"] * 2), pygame.SRCALPHA)
            color_preview = (*template["color"], 100) if can_build else (*RED, 100)
            pygame.draw.circle(surf, color_preview, (template["range"], template["range"]), template["range"])
            screen.blit(surf, (self.preview_position.x - template["range"], self.preview_position.y - template["range"]))
            
            # Draw tower preview
            color = template["color"] if can_build else RED
            pygame.draw.circle(screen, color, (int(self.preview_position.x), int(self.preview_position.y)), template["size"] // 2, 2)


class ProjectileSystem:
    """Handles projectile movement and collision"""
    
    def __init__(self, enemy_system: EnemySystem, combat_system: 'CombatSystem'):
        self.enemy_system = enemy_system
        self.combat_system = combat_system
        self.projectiles: List[Projectile] = []
    
    def spawn(self, projectile: Projectile):
        """Spawn a new projectile"""
        self.projectiles.append(projectile)
    
    def update(self, dt: float) -> List[Enemy]:
        """Update projectiles and return killed enemies"""
        killed_enemies = []
        
        for proj in self.projectiles[:]:
            if not proj.active:
                continue
            
            # Move towards target
            if proj.target.state in [EnemyState.DEAD, EnemyState.ESCAPE]:
                proj.active = False
                continue
            
            direction = proj.position.direction_to(proj.target.position)
            move_distance = proj.speed * dt
            
            proj.position.x += direction[0] * move_distance
            proj.position.y += direction[1] * move_distance
            
            # Check collision
            if proj.position.distance_to(proj.target.position) < proj.target.size // 2 + proj.size:
                # Hit!
                self.combat_system.apply_damage(proj.target, proj.damage, proj.aoe, proj.aoe_radius)
                proj.active = False
                
                if proj.target.state == EnemyState.DEAD:
                    killed_enemies.append(proj.target)
        
        # Remove inactive projectiles
        self.projectiles = [p for p in self.projectiles if p.active]
        
        return killed_enemies
    
    def render(self, screen: pygame.Surface):
        """Render all projectiles"""
        for proj in self.projectiles:
            if not proj.active:
                continue
            
            # Try to load sprite first, fallback to procedural drawing
            sprite = get_projectile_sprite(proj.projectile_type, proj.size)
            
            if sprite:
                # Draw sprite centered on projectile position
                rect = sprite.get_rect(center=(int(proj.position.x), int(proj.position.y)))
                screen.blit(sprite, rect)
            else:
                # Fallback: Draw colored circle
                color = PROJECTILE_TEMPLATES[proj.projectile_type]["color"]
                size = proj.size
                
                pygame.draw.circle(screen, color, (int(proj.position.x), int(proj.position.y)), size // 2)
            
            # Trail effect (always drawn)
            direction = proj.position.direction_to(proj.target.position)
            trail_length = proj.size * 2
            trail_x = proj.position.x - direction[0] * trail_length
            trail_y = proj.position.y - direction[1] * trail_length
            trail_color = PROJECTILE_TEMPLATES[proj.projectile_type]["color"]
            pygame.draw.line(screen, trail_color, 
                           (proj.position.x, proj.position.y), 
                           (trail_x, trail_y), proj.size // 3)


class CombatSystem:
    """Handles combat calculations and events"""
    
    def __init__(self, enemy_system: EnemySystem):
        self.enemy_system = enemy_system
        self.damage_events = []
    
    def apply_damage(self, enemy: Enemy, damage: int, aoe: bool = False, aoe_radius: float = 0):
        """Apply damage to enemy (and nearby enemies if AOE)"""
        if aoe and aoe_radius > 0:
            # AOE damage
            for e in self.enemy_system.enemies:
                if e.position.distance_to(enemy.position) <= aoe_radius:
                    actual_damage = self.enemy_system.take_damage(e, damage)
                    self.damage_events.append({
                        "enemy": e,
                        "damage": actual_damage,
                        "is_aoe": True
                    })
        else:
            # Single target
            actual_damage = self.enemy_system.take_damage(enemy, damage)
            self.damage_events.append({
                "enemy": enemy,
                "damage": actual_damage,
                "is_aoe": False
            })
    
    def clear_events(self):
        """Clear damage event log"""
        self.damage_events = []


class WaveSystem:
    """Handles wave progression"""
    
    def __init__(self, enemy_system: EnemySystem):
        self.enemy_system = enemy_system
        self.current_wave_index = -1
        self.wave_complete = False
        self.between_waves_timer = 0
        self.wave_delay = 3.0  # seconds between waves
    
    def start_next_wave(self) -> bool:
        """Start next wave, return False if no more waves"""
        if self.current_wave_index >= len(WAVE_TEMPLATES) - 1:
            return False
        
        self.current_wave_index += 1
        wave_data = WAVE_TEMPLATES[self.current_wave_index]
        self.enemy_system.add_wave(wave_data)
        self.wave_complete = False
        
        return True
    
    def update(self, dt: float) -> bool:
        """Update wave system, return True if wave completed"""
        if self.current_wave_index < 0:
            return False
        
        if not self.enemy_system.has_active_enemies():
            if not self.wave_complete:
                self.wave_complete = True
                self.between_waves_timer = self.wave_delay
            else:
                self.between_waves_timer -= dt
                if self.between_waves_timer <= 0:
                    return True  # Ready for next wave
        
        return False
    
    def get_current_wave_number(self) -> int:
        """Get current wave number (1-indexed)"""
        return self.current_wave_index + 1
    
    def get_total_waves(self) -> int:
        """Get total number of waves"""
        return len(WAVE_TEMPLATES)


class ResourceSystem:
    """Handles game resources (gold, lives)"""
    
    def __init__(self):
        self.gold = 150
        self.lives = 20
    
    def add_gold(self, amount: int):
        """Add gold"""
        self.gold += amount
    
    def deduct_gold(self, amount: int) -> bool:
        """Deduct gold, return False if insufficient"""
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False
    
    def lose_life(self, amount: int = 1):
        """Lose lives"""
        self.lives -= amount
    
    def is_game_over(self) -> bool:
        """Check if game over"""
        return self.lives <= 0
    
    def render(self, screen: pygame.Surface):
        """Render resource UI"""
        font = pygame.font.Font(None, 36)
        
        # Gold
        gold_text = font.render(f"Gold: {self.gold}", True, YELLOW)
        screen.blit(gold_text, (10, 10))
        
        # Lives
        lives_text = font.render(f"Lives: {self.lives}", True, RED)
        screen.blit(lives_text, (10, 50))


class RenderSystem:
    """Handles all rendering operations"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 24)
    
    def render_ui(self, resource_system: ResourceSystem, wave_system: WaveSystem, 
                  tower_system: TowerSystem, selected_node: int = 0):
        """Render game UI"""
        # Wave info
        wave_text = self.font_small.render(f"Wave {wave_system.get_current_wave_number()}/{wave_system.get_total_waves()}", True, WHITE)
        self.screen.blit(wave_text, (SCREEN_WIDTH - 150, 10))
        
        # Tower selection panel
        panel_y = SCREEN_HEIGHT - 100
        pygame.draw.rect(self.screen, GRAY, (0, panel_y, SCREEN_WIDTH, 100))
        pygame.draw.line(self.screen, WHITE, (0, panel_y), (SCREEN_WIDTH, panel_y), 2)
        
        # Tower buttons
        tower_types = list(TOWER_TEMPLATES.keys())
        button_width = 120
        spacing = 20
        
        for i, tower_type in enumerate(tower_types):
            template = TOWER_TEMPLATES[tower_type]
            x = spacing + i * (button_width + spacing)
            
            # Button background
            color = template["color"]
            if tower_system.selected_tower_type == tower_type:
                pygame.draw.rect(self.screen, WHITE, (x, panel_y + 10, button_width, 80), 3)
            
            pygame.draw.rect(self.screen, color, (x, panel_y + 10, button_width, 80))
            
            # Tower info
            name_text = self.font_small.render(tower_type.capitalize(), True, WHITE)
            cost_text = self.font_small.render(f"{template['cost']}g", True, YELLOW)
            
            self.screen.blit(name_text, (x + 10, panel_y + 15))
            self.screen.blit(cost_text, (x + 10, panel_y + 45))
        
        # Instructions
        if tower_system.selected_tower_type:
            inst_text = self.font_small.render("Click on a build node to place tower", True, WHITE)
            self.screen.blit(inst_text, (SCREEN_WIDTH // 2 - 150, panel_y - 30))
    
    def render_game_over(self, victory: bool):
        """Render game over screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        if victory:
            text = self.font_large.render("VICTORY!", True, GREEN)
        else:
            text = self.font_large.render("GAME OVER", True, RED)
        
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(text, text_rect)
        
        restart_text = self.font_small.render("Press R to restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(restart_text, restart_rect)
    
    def render_start_screen(self):
        """Render start screen"""
        self.screen.fill(DARK_GREEN)
        
        title = self.font_large.render("TOWER DEFENSE", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_medium.render("Defend your base!", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 60))
        self.screen.blit(subtitle, subtitle_rect)
        
        start_text = self.font_medium.render("Press SPACE to start", True, GREEN)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(start_text, start_rect)
        
        # Instructions
        instructions = [
            "Build towers on gray nodes",
            "Stop enemies from reaching the end",
            "Earn gold by defeating enemies",
            "Survive all waves!"
        ]
        
        for i, inst in enumerate(instructions):
            text = self.font_small.render(inst, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100 + i * 30))
            self.screen.blit(text, text_rect)


class GameManager:
    """Main game controller - implements core loop"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tower Defense - Python PyGame")
        self.clock = pygame.time.Clock()
        
        self.state = GameState.INIT
        self.running = True
        
        # Initialize systems
        self.map_system = MapSystem(MAP_TEMPLATE)
        self.resource_system = ResourceSystem()
        self.enemy_system = EnemySystem(self.map_system)
        self.tower_system = TowerSystem(self.map_system, self.resource_system)
        self.projectile_system = ProjectileSystem(self.enemy_system, None)  # Will set combat_system after
        self.combat_system = CombatSystem(self.enemy_system)
        self.wave_system = WaveSystem(self.enemy_system)
        self.render_system = RenderSystem(self.screen)
        
        # Link combat system to projectile system
        self.projectile_system.combat_system = self.combat_system
        
        # Mouse position
        self.mouse_pos = Vector2(0, 0)
    
    def init_game(self):
        """Initialize game state"""
        self.resource_system = ResourceSystem()
        self.enemy_system = EnemySystem(self.map_system)
        self.tower_system = TowerSystem(self.map_system, self.resource_system)
        self.projectile_system = ProjectileSystem(self.enemy_system, self.combat_system)
        self.combat_system = CombatSystem(self.enemy_system)
        self.wave_system = WaveSystem(self.enemy_system)
        self.projectile_system.combat_system = self.combat_system
        
        self.state = GameState.PLAYING
        
        # Start first wave
        self.wave_system.start_next_wave()
    
    def handle_input(self):
        """Handle player input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state == GameState.INIT:
                        self.init_game()
                    elif self.state in [GameState.GAME_OVER, GameState.VICTORY]:
                        self.init_game()
                
                if event.key == pygame.K_r:
                    if self.state in [GameState.GAME_OVER, GameState.VICTORY]:
                        self.init_game()
                
                # Tower selection hotkeys
                if self.state == GameState.PLAYING:
                    if event.key == pygame.K_1:
                        self.tower_system.select_tower("archer")
                    elif event.key == pygame.K_2:
                        self.tower_system.select_tower("cannon")
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == GameState.PLAYING:
                    if event.button == 1:  # Left click
                        # Try place tower
                        if not self.tower_system.try_place_tower(self.mouse_pos):
                            # If failed, check if clicked on tower button
                            self._handle_tower_button_click()
                    
                    if event.button == 3:  # Right click
                        self.tower_system.selected_tower_type = None
            
            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = Vector2(event.pos[0], event.pos[1])
                if self.state == GameState.PLAYING:
                    self.tower_system.set_preview_position(self.mouse_pos)
    
    def _handle_tower_button_click(self):
        """Handle clicks on tower selection buttons"""
        panel_y = SCREEN_HEIGHT - 100
        tower_types = list(TOWER_TEMPLATES.keys())
        button_width = 120
        spacing = 20
        
        for i, tower_type in enumerate(tower_types):
            x = spacing + i * (button_width + spacing)
            if (x <= self.mouse_pos.x <= x + button_width and 
                panel_y + 10 <= self.mouse_pos.y <= panel_y + 90):
                self.tower_system.select_tower(tower_type)
                return
    
    def update(self, dt: float):
        """Update game state"""
        if self.state != GameState.PLAYING:
            return
        
        # Update systems
        self.enemy_system.update(dt)
        projectiles = self.tower_system.update(dt, self.enemy_system.enemies)
        
        # Spawn projectiles
        for proj in projectiles:
            self.projectile_system.spawn(proj)
        
        # Update projectiles
        killed_enemies = self.projectile_system.update(dt)
        
        # Reward for kills
        for enemy in killed_enemies:
            self.resource_system.add_gold(enemy.gold_drop)
        
        # Remove dead enemies
        escaped_enemies = [e for e in self.enemy_system.enemies if e.state == EnemyState.ESCAPE]
        for enemy in escaped_enemies:
            self.resource_system.lose_life(1)
        
        self.enemy_system.remove_dead()
        
        # Check wave completion
        if self.wave_system.update(dt):
            if not self.wave_system.start_next_wave():
                # All waves complete
                if not self.enemy_system.has_active_enemies():
                    self.state = GameState.VICTORY
        
        # Check game over
        if self.resource_system.is_game_over():
            self.state = GameState.GAME_OVER
    
    def render(self):
        """Render game frame"""
        if self.state == GameState.INIT:
            self.render_system.render_start_screen()
        else:
            # Render game objects in correct order
            self.map_system.render(self.screen)
            self.enemy_system.render(self.screen)
            self.tower_system.render(self.screen)
            self.projectile_system.render(self.screen)
            self.render_system.render_ui(self.resource_system, self.wave_system, self.tower_system)
            
            # Render game over / victory
            if self.state in [GameState.GAME_OVER, GameState.VICTORY]:
                self.render_system.render_game_over(self.state == GameState.VICTORY)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        print("=" * 60)
        print("TOWER DEFENSE - PYTHON PYGAME")
        print("=" * 60)
        print("\nControls:")
        print("  1 - Select Archer Tower (50g)")
        print("  2 - Select Cannon Tower (100g)")
        print("  Left Click - Place tower / Select tower type")
        print("  Right Click - Cancel tower selection")
        print("  SPACE - Start game / Restart")
        print("  R - Restart (when game over)")
        print("\nObjective: Survive all waves!")
        print("=" * 60)
        
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            
            self.handle_input()
            self.update(dt)
            self.render()
        
        pygame.quit()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    game = GameManager()
    game.run()
