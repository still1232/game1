# 🎮 Tower Defense Game - Python PyGame

Triển khai **Tower Defense** theo **CORE GAME TEMPLATE** sử dụng Python và PyGame.

## 📋 Yêu cầu hệ thống

- Python 3.8+
- PyGame 2.0+

## 🚀 Cài đặt

```bash
pip install pygame
```

## ▶️ Chạy game

```bash
python main.py
```

## 🎯 Controls

| Phím | Chức năng |
|------|-----------|
| `1` | Chọn Archer Tower (50 gold) |
| `2` | Chọn Cannon Tower (100 gold) |
| `Left Click` | Đặt tower / Chọn tower type |
| `Right Click` | Hủy chọn tower |
| `SPACE` | Bắt đầu game / Restart |
| `R` | Restart (khi game over) |

## 🏗️ Kiến trúc Core Systems

### 1. **GameManager** - Điều khiển game loop
```
Init → Handle Input → Update → Render → Check Win/Lose
```

### 2. **MapSystem** - Quản lý bản đồ
- Path waypoints cho enemy di chuyển
- Build nodes để đặt tower
- Render background, path, markers

### 3. **WaveSystem** - Quản lý waves
- Spawn enemies theo wave template
- Timer giữa các waves
- Check wave completion

### 4. **EnemySystem** - Quản lý kẻ địch
- State Machine: SPAWN → MOVE → DEAD/ESCAPE
- Di chuyển theo path waypoints
- Animation wobble effect
- HP bars

### 5. **TowerSystem** - Quản lý tháp
- State: IDLE → FIND_TARGET → ATTACK → COOLDOWN
- Target finding (closest enemy in range)
- Placement validation
- Attack animation

### 6. **ProjectileSystem** - Đạn đạo
- Bay từ tower → target
- Collision detection
- Trail effects
- Single target & AOE damage

### 7. **CombatSystem** - Tính toán combat
- Damage Formula: `DamageTaken = Damage - Armor`
- AOE damage calculation
- Damage events logging

### 8. **ResourceSystem** - Tài nguyên
- Gold: + khi kill enemy, - khi build tower
- Lives: - khi enemy escape
- Game over check

### 9. **RenderSystem** - Hiển thị
- Layer order: Map → Enemy → Tower → Projectile → UI
- Start screen
- Game Over / Victory screens
- UI panel với tower selection

## 📊 Game Data Templates

### Enemies

| Type | HP | Speed | Armor | Gold Drop | Size |
|------|----|-------|-------|-----------|------|
| Goblin | 100 | 60 | 2 | 10 | 24 |
| Orc | 200 | 40 | 5 | 20 | 32 |
| Boss | 500 | 30 | 10 | 50 | 40 |

### Towers

| Type | Cost | Damage | Range | Attack Speed | Special |
|------|------|--------|-------|--------------|---------|
| Archer | 50g | 25 | 150 | 1.0s | Fast attack |
| Cannon | 100g | 50 | 120 | 2.0s | AOE (60 radius) |

### Waves

**Wave 1:** 10 Goblins  
**Wave 2:** 15 Goblins + 5 Orcs  
**Wave 3:** 20 Goblins + 10 Orcs + 2 Bosses

## 🗺️ Map Configuration

```json
{
  "map_id": "grassland",
  "path": [[50,384],[200,384],[200,200],...],
  "build_nodes": [
    {"x": 150, "y": 300},
    {"x": 250, "y": 450},
    ...
  ]
}
```

- **Path**: Enemy spawn tại điểm đầu, di chuyển qua waypoints, đến điểm cuối
- **Build Nodes**: 7 vị trí có thể đặt tower (vòng xám trên map)

## 🎨 Graphics

### Sprites đã tích hợp sẵn! 🎉

Game hiện đã được tích hợp sprite assets:

```
assets/
├── enemy/
│   ├── goblin.png    ✓
│   └── orc.png       ✓
├── tower/
│   ├── archer.png    ✓
│   └── cannon.png    ✓
├── projectile/
│   ├── arrow.png     ✓
│   └── cannonball.png ✓
└── map/
    └── (background vẽ procedural)
```

**Sprite System:**
- Tự động load sprites khi game start
- Cache sprites để tối ưu performance
- Fallback về procedural graphics nếu sprite không tồn tại
- Attack animation với scaling effect cho towers
- HP bars luôn được vẽ lên trên sprites

### Thêm Sprite Assets (Optional)

Bạn có thể thay thế sprites bằng assets từ:

Link sprite free:
- [Kenney.nl Tower Defense Kit](https://kenney.nl/assets/tower-defense-kit)
- [itch.io Tower Defense Assets](https://itch.io/game-assets/free/tag-tower-defense)
- [OpenGameArt](https://opengameart.org)

Chỉ cần đặt file PNG vào thư mục `assets/` tương ứng và game sẽ tự động sử dụng!

## 🔧 Customization

### Thêm Enemy mới

```python
ENEMY_TEMPLATES["dragon"] = {
    "id": "dragon",
    "color": (255, 100, 100),
    "hp": 300,
    "speed": 50,
    "armor": 8,
    "gold_drop": 30,
    "type": "flying",
    "size": 36,
    "animation_frames": 4
}
```

### Thêm Tower mới

```python
TOWER_TEMPLATES["sniper"] = {
    "id": "sniper",
    "color": (0, 255, 128),
    "damage": 100,
    "range": 300,
    "attack_speed": 3.0,
    "projectile": "bullet",
    "cost": 150,
    "size": 36
}
```

### Thêm Wave mới

```python
WAVE_TEMPLATES.append({
    "wave": 4,
    "enemies": [
        {"type": "dragon", "count": 5, "spawn_delay": 3.0}
    ]
})
```

## 🎮 Gameplay Loop

1. **Start**: Nhấn SPACE để bắt đầu
2. **Select Tower**: Nhấn 1 hoặc 2, hoặc click vào button
3. **Place Tower**: Click vào build node (vòng xám)
4. **Defend**: Towers tự động bắn enemies
5. **Earn Gold**: Kill enemies để lấy gold
6. **Upgrade**: Build thêm towers
7. **Win**: Survive tất cả waves
8. **Lose**: Nếu lives <= 0

## 📁 File Structure

```
tower_defense_pygame/
├── main.py              # Toàn bộ game logic (1150+ dòng)
├── README.md            # Hướng dẫn này
└── assets/              # Thư mục cho sprites (optional)
    ├── map/
    ├── enemy/
    ├── tower/
    ├── projectile/
    └── ui/
```

## ⚡ Features

✅ Full core loop implementation  
✅ 9 core systems modular architecture  
✅ State machines cho Enemy & Tower  
✅ Path-based enemy movement  
✅ Tower targeting & cooldown  
✅ Projectile physics & collision  
✅ AOE damage (Cannon)  
✅ Wave progression system  
✅ Resource management (Gold/Lives)  
✅ Win/Lose conditions  
✅ Animated entities  
✅ UI với tower selection panel  
✅ Preview range khi chọn tower  
✅ HP bars cho enemies  
✅ Start/Game Over/Victory screens  

## 🚀 Roadmap Extensions

- [ ] Thêm sound effects
- [ ] Thêm nhiều tower types
- [ ] Thêm enemy abilities (speed boost, armor boost)
- [ ] Tower upgrades
- [ ] Multiple maps
- [ ] High score system
- [ ] Particle effects
- [ ] Sprite animations thay vì procedural

---

**Enjoy building your Tower Defense! 🏰⚔️**
