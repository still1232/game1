// ============================================
// CORE GAME TEMPLATE - TOWER DEFENSE
// Kiến trúc chuẩn theo specification
// ============================================

// === CONFIG & DATA TEMPLATES ===

const MAP_DATA = {
    map_id: "grassland",
    background: "#2d5a27",
    path: [
        {x: 0, y: 300},
        {x: 150, y: 300},
        {x: 150, y: 150},
        {x: 400, y: 150},
        {x: 400, y: 450},
        {x: 650, y: 450},
        {x: 650, y: 250},
        {x: 800, y: 250}
    ],
    build_nodes: [
        {x: 100, y: 200},
        {x: 250, y: 250},
        {x: 300, y: 100},
        {x: 500, y: 200},
        {x: 550, y: 350},
        {x: 700, y: 350},
        {x: 750, y: 150}
    ]
};

const ENEMY_TEMPLATES = {
    goblin: {
        id: "goblin",
        color: "#90EE90",
        hp: 100,
        speed: 60,
        armor: 2,
        gold_drop: 10,
        type: "ground",
        size: 30,
        walkAnimation: ["#90EE90", "#7DDD7D", "#90EE90", "#6CCC6C"]
    },
    orc: {
        id: "orc",
        color: "#FF6B6B",
        hp: 200,
        speed: 40,
        armor: 5,
        gold_drop: 20,
        type: "ground",
        size: 35,
        walkAnimation: ["#FF6B6B", "#EE5A5A", "#FF6B6B", "#DD4949"]
    },
    boss: {
        id: "boss",
        color: "#8B0000",
        hp: 500,
        speed: 30,
        armor: 10,
        gold_drop: 50,
        type: "ground",
        size: 45,
        walkAnimation: ["#8B0000", "#7B0000", "#8B0000", "#6B0000"]
    }
};

const TOWER_TEMPLATES = {
    archer: {
        id: "archer",
        color: "#4ECDC4",
        damage: 25,
        range: 150,
        attack_speed: 1.0,
        projectile: "arrow",
        cost: 50,
        size: 40,
        attackAnimation: ["#4ECDC4", "#FFE66D", "#4ECDC4"]
    },
    cannon: {
        id: "cannon",
        color: "#FF6B6B",
        damage: 50,
        range: 120,
        attack_speed: 2.0,
        projectile: "cannonball",
        cost: 100,
        size: 45,
        attackAnimation: ["#FF6B6B", "#FFFFFF", "#FF6B6B"]
    }
};

const PROJECTILE_TEMPLATES = {
    arrow: {
        id: "arrow",
        color: "#FFE66D",
        speed: 400,
        damage: 25,
        aoe: false,
        size: 8
    },
    cannonball: {
        id: "cannonball",
        color: "#333333",
        speed: 200,
        damage: 50,
        aoe: true,
        aoe_radius: 60,
        size: 12
    }
};

const WAVE_TEMPLATES = [
    {
        wave: 1,
        enemies: [
            {type: "goblin", count: 5, spawn_delay: 1.5}
        ]
    },
    {
        wave: 2,
        enemies: [
            {type: "goblin", count: 8, spawn_delay: 1.2},
            {type: "orc", count: 3, spawn_delay: 2.0}
        ]
    },
    {
        wave: 3,
        enemies: [
            {type: "goblin", count: 10, spawn_delay: 1.0},
            {type: "orc", count: 5, spawn_delay: 1.5},
            {type: "boss", count: 1, spawn_delay: 3.0}
        ]
    }
];

// === CORE SYSTEMS ===

class ResourceSystem {
    constructor() {
        this.gold = 150;
        this.lives = 20;
        this.onGoldChange = null;
        this.onLivesChange = null;
    }

    addGold(amount) {
        this.gold += amount;
        if (this.onGoldChange) this.onGoldChange(this.gold);
    }

    spendGold(amount) {
        if (this.gold >= amount) {
            this.gold -= amount;
            if (this.onGoldChange) this.onGoldChange(this.gold);
            return true;
        }
        return false;
    }

    loseLife(amount) {
        this.lives -= amount;
        if (this.onLivesChange) this.onLivesChange(this.lives);
        return this.lives <= 0;
    }
}

class Enemy {
    constructor(template, path) {
        this.template = template;
        this.hp = template.hp;
        this.maxHp = template.hp;
        this.speed = template.speed;
        this.armor = template.armor;
        this.path = path;
        this.currentWaypoint = 0;
        this.x = path[0].x;
        this.y = path[0].y;
        this.state = "SPAWN";
        this.animationFrame = 0;
        this.animationTimer = 0;
        this.dead = false;
        this.escaped = false;
    }

    update(deltaTime) {
        if (this.state === "DEAD" || this.escaped) return;

        // Animation
        this.animationTimer += deltaTime;
        if (this.animationTimer > 0.2) {
            this.animationTimer = 0;
            this.animationFrame = (this.animationFrame + 1) % this.template.walkAnimation.length;
        }

        // Movement
        const target = this.path[this.currentWaypoint + 1];
        if (!target) {
            this.escaped = true;
            return;
        }

        const dx = target.x - this.x;
        const dy = target.y - this.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < 5) {
            this.currentWaypoint++;
            if (this.currentWaypoint >= this.path.length - 1) {
                this.escaped = true;
            }
        } else {
            const moveX = (dx / distance) * this.speed * deltaTime;
            const moveY = (dy / distance) * this.speed * deltaTime;
            this.x += moveX;
            this.y += moveY;
        }
    }

    takeDamage(damage) {
        const actualDamage = Math.max(1, damage - this.armor);
        this.hp -= actualDamage;
        if (this.hp <= 0) {
            this.state = "DEAD";
            this.dead = true;
            return true;
        }
        return false;
    }

    render(ctx) {
        if (this.state === "DEAD") return;

        const color = this.template.walkAnimation[this.animationFrame];
        
        // Body
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.template.size / 2, 0, Math.PI * 2);
        ctx.fill();

        // HP bar
        const hpPercent = this.hp / this.maxHp;
        ctx.fillStyle = "#333";
        ctx.fillRect(this.x - 15, this.y - 25, 30, 5);
        ctx.fillStyle = hpPercent > 0.5 ? "#4ECDC4" : hpPercent > 0.25 ? "#FFE66D" : "#FF6B6B";
        ctx.fillRect(this.x - 15, this.y - 25, 30 * hpPercent, 5);
    }
}

class Tower {
    constructor(template, x, y) {
        this.template = template;
        this.x = x;
        this.y = y;
        this.cooldown = 0;
        this.target = null;
        this.state = "IDLE";
        this.animationFrame = 0;
        this.animationTimer = 0;
        this.isAttacking = false;
    }

    update(deltaTime, enemies) {
        // Cooldown
        if (this.cooldown > 0) {
            this.cooldown -= deltaTime;
        }

        // Animation
        if (this.isAttacking) {
            this.animationTimer += deltaTime;
            if (this.animationTimer > 0.15) {
                this.animationTimer = 0;
                this.animationFrame = (this.animationFrame + 1) % this.template.attackAnimation.length;
                if (this.animationFrame === 0) {
                    this.isAttacking = false;
                }
            }
        }

        // Find target
        if (this.cooldown <= 0) {
            this.target = this.findTarget(enemies);
            if (this.target) {
                this.state = "ATTACK";
                this.isAttacking = true;
                this.animationFrame = 0;
                this.cooldown = this.template.attack_speed;
                return this.target;
            }
        }

        this.state = "IDLE";
        return null;
    }

    findTarget(enemies) {
        let closest = null;
        let closestDist = Infinity;

        for (const enemy of enemies) {
            if (enemy.dead || enemy.escaped) continue;

            const dx = enemy.x - this.x;
            const dy = enemy.y - this.y;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist <= this.template.range && dist < closestDist) {
                closestDist = dist;
                closest = enemy;
            }
        }

        return closest;
    }

    render(ctx) {
        const color = this.isAttacking 
            ? this.template.attackAnimation[this.animationFrame]
            : this.template.color;

        // Base
        ctx.fillStyle = "#555";
        ctx.fillRect(this.x - 20, this.y - 20, 40, 40);

        // Tower
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.template.size / 2, 0, Math.PI * 2);
        ctx.fill();

        // Range indicator (when hovering)
        if (this.showRange) {
            ctx.strokeStyle = "rgba(255, 255, 255, 0.3)";
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.template.range, 0, Math.PI * 2);
            ctx.stroke();
        }
    }
}

class Projectile {
    constructor(template, startX, startY, target) {
        this.template = template;
        this.x = startX;
        this.y = startY;
        this.target = target;
        this.active = true;
        this.damage = template.damage;
    }

    update(deltaTime) {
        if (!this.active || !this.target || this.target.dead || this.target.escaped) {
            this.active = false;
            return null;
        }

        const dx = this.target.x - this.x;
        const dy = this.target.y - this.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 10) {
            this.active = false;
            return {
                target: this.target,
                damage: this.damage,
                aoe: this.template.aoe,
                aoe_radius: this.template.aoe_radius,
                x: this.x,
                y: this.y
            };
        }

        const moveX = (dx / dist) * this.template.speed * deltaTime;
        const moveY = (dy / dist) * this.template.speed * deltaTime;
        this.x += moveX;
        this.y += moveY;

        return null;
    }

    render(ctx) {
        if (!this.active) return;

        ctx.fillStyle = this.template.color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.template.size, 0, Math.PI * 2);
        ctx.fill();

        // Trail effect
        ctx.fillStyle = "rgba(255, 255, 255, 0.3)";
        ctx.beginPath();
        ctx.arc(this.x - 5, this.y - 5, this.template.size * 0.7, 0, Math.PI * 2);
        ctx.fill();
    }
}

class WaveSystem {
    constructor() {
        this.currentWave = 0;
        this.active = false;
        this.spawnQueue = [];
        this.spawnTimer = 0;
        this.onWaveStart = null;
        this.onWaveComplete = null;
    }

    startWave(waveIndex) {
        if (waveIndex >= WAVE_TEMPLATES.length) {
            return false;
        }

        this.currentWave = waveIndex;
        const waveData = WAVE_TEMPLATES[waveIndex];
        this.active = true;
        this.spawnQueue = [];

        // Build spawn queue
        for (const enemyGroup of waveData.enemies) {
            for (let i = 0; i < enemyGroup.count; i++) {
                this.spawnQueue.push({
                    type: enemyGroup.type,
                    delay: enemyGroup.spawn_delay
                });
            }
        }

        this.spawnTimer = 0;
        if (this.onWaveStart) this.onWaveStart(waveIndex + 1);
        return true;
    }

    update(deltaTime, enemyFactory) {
        if (!this.active) return null;

        if (this.spawnQueue.length > 0) {
            this.spawnTimer -= deltaTime;
            if (this.spawnTimer <= 0) {
                const nextSpawn = this.spawnQueue.shift();
                const enemy = enemyFactory(nextSpawn.type);
                this.spawnTimer = nextSpawn.delay;
                return enemy;
            }
        } else {
            // Check if all enemies are defeated
            return "WAVE_COMPLETE";
        }

        return null;
    }
}

class CombatSystem {
    static calculateDamage(damage, armor) {
        return Math.max(1, damage - armor);
    }
}

// === MAIN GAME ENGINE ===

class Game {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        
        this.resourceSystem = new ResourceSystem();
        this.waveSystem = new WaveSystem();
        
        this.enemies = [];
        this.towers = [];
        this.projectiles = [];
        
        this.selectedTower = "archer";
        this.gameState = "INIT";
        this.lastTime = 0;
        
        this.setupUI();
        this.setupInput();
        
        this.resourceSystem.onGoldChange = (gold) => {
            document.getElementById('gold-display').textContent = gold;
        };
        this.resourceSystem.onLivesChange = (lives) => {
            document.getElementById('lives-display').textContent = lives;
            if (lives <= 0) {
                this.gameOver(false);
            }
        };

        this.waveSystem.onWaveStart = (wave) => {
            document.getElementById('wave-display').textContent = wave;
            document.getElementById('start-wave-btn').disabled = true;
        };

        this.waveSystem.onWaveComplete = () => {
            document.getElementById('start-wave-btn').disabled = false;
        };

        this.gameState = "RUNNING";
        this.lastTime = performance.now();
        requestAnimationFrame((time) => this.gameLoop(time));
    }

    setupUI() {
        // Tower selection
        document.querySelectorAll('.tower-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.tower-btn').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                this.selectedTower = btn.dataset.tower;
            });
        });

        // Start wave button
        document.getElementById('start-wave-btn').addEventListener('click', () => {
            this.waveSystem.startWave(this.waveSystem.currentWave);
        });

        // Initial UI update
        this.resourceSystem.onGoldChange(this.resourceSystem.gold);
        this.resourceSystem.onLivesChange(this.resourceSystem.lives);
    }

    setupInput() {
        this.canvas.addEventListener('click', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            // Check if clicking on build node
            const buildNode = MAP_DATA.build_nodes.find(node => {
                const dx = node.x - x;
                const dy = node.y - y;
                return Math.sqrt(dx * dx + dy * dy) < 30;
            });

            if (buildNode) {
                this.tryBuildTower(buildNode.x, buildNode.y);
            }
        });

        this.canvas.addEventListener('mousemove', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            this.mouseX = e.clientX - rect.left;
            this.mouseY = e.clientY - rect.top;
        });
    }

    tryBuildTower(x, y) {
        const towerTemplate = TOWER_TEMPLATES[this.selectedTower];
        
        // Check if tower already exists at this position
        const existing = this.towers.find(t => t.x === x && t.y === y);
        if (existing) return;

        if (this.resourceSystem.spendGold(towerTemplate.cost)) {
            const tower = new Tower(towerTemplate, x, y);
            this.towers.push(tower);
        }
    }

    createEnemy(type) {
        const template = ENEMY_TEMPLATES[type];
        return new Enemy(template, MAP_DATA.path);
    }

    update(deltaTime) {
        // Wave system
        const spawnResult = this.waveSystem.update(deltaTime, (type) => this.createEnemy(type));
        if (spawnResult && spawnResult !== "WAVE_COMPLETE") {
            this.enemies.push(spawnResult);
        } else if (spawnResult === "WAVE_COMPLETE") {
            const allDefeated = this.enemies.every(e => e.dead || e.escaped);
            if (allDefeated) {
                this.waveSystem.active = false;
                if (this.waveSystem.onWaveComplete) {
                    this.waveSystem.onWaveComplete();
                }
                // Check win condition
                if (this.waveSystem.currentWave >= WAVE_TEMPLATES.length - 1) {
                    this.gameOver(true);
                }
            }
        }

        // Update enemies
        for (const enemy of this.enemies) {
            enemy.update(deltaTime);
            
            if (enemy.escaped) {
                if (this.resourceSystem.loseLife(1)) {
                    this.gameOver(false);
                }
            }
            
            if (enemy.dead) {
                this.resourceSystem.addGold(enemy.template.gold_drop);
            }
        }

        // Remove dead/escaped enemies
        this.enemies = this.enemies.filter(e => !e.dead && !e.escaped);

        // Update towers
        for (const tower of this.towers) {
            const target = tower.update(deltaTime, this.enemies);
            if (target) {
                const projectileTemplate = PROJECTILE_TEMPLATES[tower.template.projectile];
                const projectile = new Projectile(projectileTemplate, tower.x, tower.y, target);
                this.projectiles.push(projectile);
            }
        }

        // Update projectiles
        for (const projectile of this.projectiles) {
            const hit = projectile.update(deltaTime);
            if (hit) {
                // Apply damage
                if (hit.aoe) {
                    // Area damage
                    for (const enemy of this.enemies) {
                        const dx = enemy.x - hit.x;
                        const dy = enemy.y - hit.y;
                        const dist = Math.sqrt(dx * dx + dy * dy);
                        if (dist <= hit.aoe_radius) {
                            enemy.takeDamage(hit.damage);
                        }
                    }
                } else {
                    // Single target
                    hit.target.takeDamage(hit.damage);
                }
            }
        }

        // Remove inactive projectiles
        this.projectiles = this.projectiles.filter(p => p.active);
    }

    render() {
        // Clear canvas
        this.ctx.fillStyle = MAP_DATA.background;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw path
        this.ctx.strokeStyle = "#8B7355";
        this.ctx.lineWidth = 40;
        this.ctx.lineCap = "round";
        this.ctx.lineJoin = "round";
        this.ctx.beginPath();
        this.ctx.moveTo(MAP_DATA.path[0].x, MAP_DATA.path[0].y);
        for (let i = 1; i < MAP_DATA.path.length; i++) {
            this.ctx.lineTo(MAP_DATA.path[i].x, MAP_DATA.path[i].y);
        }
        this.ctx.stroke();

        // Draw path center line
        this.ctx.strokeStyle = "#A0886A";
        this.ctx.lineWidth = 2;
        this.ctx.setLineDash([10, 10]);
        this.ctx.beginPath();
        this.ctx.moveTo(MAP_DATA.path[0].x, MAP_DATA.path[0].y);
        for (let i = 1; i < MAP_DATA.path.length; i++) {
            this.ctx.lineTo(MAP_DATA.path[i].x, MAP_DATA.path[i].y);
        }
        this.ctx.stroke();
        this.ctx.setLineDash([]);

        // Draw build nodes
        for (const node of MAP_DATA.build_nodes) {
            const hasTower = this.towers.some(t => t.x === node.x && t.y === node.y);
            this.ctx.fillStyle = hasTower ? "rgba(78, 205, 196, 0.3)" : "rgba(255, 255, 255, 0.2)";
            this.ctx.beginPath();
            this.ctx.arc(node.x, node.y, 25, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.strokeStyle = hasTower ? "#4ECDC4" : "rgba(255, 255, 255, 0.5)";
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
        }

        // Render entities (layer order: enemies -> towers -> projectiles)
        for (const enemy of this.enemies) {
            enemy.render(this.ctx);
        }

        for (const tower of this.towers) {
            tower.render(this.ctx);
        }

        for (const projectile of this.projectiles) {
            projectile.render(this.ctx);
        }

        // Draw placement preview
        if (this.mouseX && this.mouseY) {
            const buildNode = MAP_DATA.build_nodes.find(node => {
                const dx = node.x - this.mouseX;
                const dy = node.y - this.mouseY;
                return Math.sqrt(dx * dx + dy * dy) < 30;
            });

            if (buildNode && !this.towers.some(t => t.x === buildNode.x && t.y === buildNode.y)) {
                const towerTemplate = TOWER_TEMPLATES[this.selectedTower];
                const canAfford = this.resourceSystem.gold >= towerTemplate.cost;
                
                this.ctx.fillStyle = canAfford ? "rgba(78, 205, 196, 0.5)" : "rgba(255, 107, 107, 0.5)";
                this.ctx.beginPath();
                this.ctx.arc(buildNode.x, buildNode.y, towerTemplate.size / 2, 0, Math.PI * 2);
                this.ctx.fill();

                // Range preview
                this.ctx.strokeStyle = "rgba(255, 255, 255, 0.3)";
                this.ctx.lineWidth = 2;
                this.ctx.beginPath();
                this.ctx.arc(buildNode.x, buildNode.y, towerTemplate.range, 0, Math.PI * 2);
                this.ctx.stroke();
            }
        }
    }

    gameLoop(currentTime) {
        if (this.gameState !== "RUNNING") return;

        const deltaTime = (currentTime - this.lastTime) / 1000;
        this.lastTime = currentTime;

        this.update(deltaTime);
        this.render();

        requestAnimationFrame((time) => this.gameLoop(time));
    }

    gameOver(victory) {
        this.gameState = victory ? "VICTORY" : "DEFEAT";
        const messageEl = document.getElementById('message');
        messageEl.textContent = victory ? "🎉 VICTORY!" : "💀 DEFEAT!";
        messageEl.style.color = victory ? "#4ECDC4" : "#FF6B6B";
        messageEl.style.display = "block";
        
        setTimeout(() => {
            location.reload();
        }, 3000);
    }
}

// === INIT GAME ===
window.onload = () => {
    const game = new Game('gameCanvas');
};
