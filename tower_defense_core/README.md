# 🏰 Tower Defense Core - Game Template Chuẩn Kiến Trúc

Game Tower Defense hoàn chỉnh được xây dựng theo specification với đầy đủ các core systems.

## 📋 Features Implemented

### ✅ Core Systems (100% Complete)
- **GameManager** - Điều khiển game loop và state
- **MapSystem** - Map với path và build nodes
- **WaveSystem** - Spawn enemy theo wave
- **EnemySystem** - 3 loại enemy (Goblin, Orc, Boss)
- **TowerSystem** - 2 loại tower (Archer, Cannon)
- **ProjectileSystem** - Đạn thường và AOE
- **CombatSystem** - Damage formula với armor
- **ResourceSystem** - Gold và Lives
- **RenderSystem** - Canvas rendering với layer order

### 🎮 Gameplay Features
- ✨ Enemy animation (color cycling)
- ✨ Tower attack animation
- ✨ Projectile trail effects
- ✨ HP bars cho enemy
- ✨ Build node system
- ✨ Tower placement preview
- ✨ Range indicator
- ✨ Wave progression (3 waves)
- ✨ Win/Lose conditions

## 🚀 How to Run

1. Mở file `index.html` trong browser
2. Hoặc dùng local server:
```bash
# Với Python 3
python -m http.server 8000

# Với Node.js
npx serve .
```

3. Truy cập `http://localhost:8000`

## 🎯 Controls

- **Click vào build nodes** (vòng tròn trắng) để đặt tower
- **Chọn tower type** ở panel dưới (Archer/Cannon)
- **Click "Start Wave"** để bắt đầu wave enemy
- **Mục tiêu**: Ngăn enemy không cho thoát đến cuối path

## 📊 Game Stats

### Towers
| Tower | Cost | Damage | Range | Attack Speed | Special |
|-------|------|--------|-------|--------------|---------|
| Archer | 50g | 25 | 150 | 1.0/s | Single target |
| Cannon | 100g | 50 | 120 | 0.5/s | AOE (60px radius) |

### Enemies
| Enemy | HP | Speed | Armor | Gold Drop |
|-------|-----|-------|-------|-----------|
| Goblin | 100 | 60 | 2 | 10g |
| Orc | 200 | 40 | 5 | 20g |
| Boss | 500 | 30 | 10 | 50g |

### Waves
- **Wave 1**: 5 Goblins
- **Wave 2**: 8 Goblins + 3 Orcs
- **Wave 3**: 10 Goblins + 5 Orcs + 1 Boss

## 🏗️ Architecture

```
Core Loop:
├── Handle Input
├── Update Wave System → Spawn Enemies
├── Update Enemies → Move along path
├── Update Towers → Find targets & fire
├── Update Projectiles → Collision detection
├── Combat Resolution → Damage calculation
└── Render Frame → Draw all entities

Layer Order:
1. Map (background + path)
2. Build nodes
3. Enemies
4. Towers
5. Projectiles
6. UI overlay
```

## 📁 File Structure

```
tower_defense_core/
├── index.html          # Main HTML + CSS
├── src/
│   └── game.js         # All game logic
└── assets/             # (Optional) Sprite folder
    ├── map/
    ├── enemy/
    ├── tower/
    ├── projectile/
    └── ui/
```

## 🎨 Graphics

Hiện tại sử dụng **procedural graphics** (vẽ bằng canvas API):
- Enemy: Circles với color animation
- Tower: Circles với base rectangles
- Projectile: Circles với trail effects
- Path: Lines với dashed center

### To Add Sprites (Optional):
Tham khảo free assets tại:
- [Kenney Tower Defense Kit](https://kenney.nl/assets/tower-defense-kit)
- [itch.io Tower Defense Assets](https://itch.io/game-assets/free/tag-tower-defense)
- [OpenGameArt](https://opengameart.org)

## 🔧 Customization

### Add New Tower
```javascript
const TOWER_TEMPLATES = {
    newTower: {
        id: "newTower",
        color: "#COLOR",
        damage: 30,
        range: 140,
        attack_speed: 1.5,
        projectile: "newProjectile",
        cost: 75,
        size: 42
    }
};
```

### Add New Enemy
```javascript
const ENEMY_TEMPLATES = {
    newEnemy: {
        id: "newEnemy",
        color: "#COLOR",
        hp: 150,
        speed: 50,
        armor: 3,
        gold_drop: 15,
        type: "ground",
        size: 32
    }
};
```

### Add New Wave
```javascript
const WAVE_TEMPLATES = [
    // ... existing waves
    {
        wave: 4,
        enemies: [
            {type: "goblin", count: 15, spawn_delay: 0.8},
            {type: "orc", count: 8, spawn_delay: 1.2},
            {type: "boss", count: 2, spawn_delay: 2.5}
        ]
    }
];
```

## 💡 Tips for Players

1. **Early game**: Đặt 1-2 Archer towers gần đầu path
2. **Mid game**: Nâng cấp lên Cannon để deal với Orcs
3. **Late game**: Kết hợp cả 2 loại, Cannon near corners
4. **Gold management**: Đừng spend hết gold, giữ ~50g emergency
5. **Positioning**: Đặt tower ở corners để maximize coverage

## 🎯 Roadmap Extensions

- [ ] Thêm sprite assets
- [ ] Thêm sound effects
- [ ] Thêm nhiều tower types (Slow, Splash, Sniper)
- [ ] Thêm nhiều enemy types (Fast, Tank, Flying)
- [ ] Thêm tower upgrades
- [ ] Thêm abilities/skills
- [ ] Thêm high score system
- [ ] Thêm particle effects

---

**Built with ❤️ following the CORE GAME TEMPLATE specification**
