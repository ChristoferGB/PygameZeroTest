import pgzrun
import random
import sys

# Window sizing
WIDTH = 800
HEIGHT = 600

# Colors
primaryColor = (15, 87, 45)
secondaryColor = (32, 184, 96)
configColor = (15, 63, 87)
alertColor = (87, 17, 17)

# Backgrounds
menuBackground = Actor("background_menu")
gameBackground = Actor("background_game")

# Menu
state = "menu"
soundOn = True

# Menu buttons
buttons = {
    "play": Rect((WIDTH//2 - 100, 210), (200, 50)),
    "sounds": Rect((WIDTH//2 - 100, 280), (200, 50)),
    "exit": Rect((WIDTH//2 - 100, 350), (200, 50)),
    "restart": Rect((WIDTH//2 - 100, 280), (200, 50)),
}

# Music
music.set_volume(0.5)
music.play('background_music')

# Hero 
gravity = 0.7
jumpStrenght = -15
initialPosition = (WIDTH // 2, HEIGHT - 100)
hero = Actor('hero_front_a', initialPosition)
hero.vy = 0
heroJumpUpFrames = ['hero_front_a', 'hero_front_b']
heroJumpRightFrames = ['hero_jump_right_a', 'hero_jump_right_b']
heroJumpLeftFrames = ['hero_jump_left_a', 'hero_jump_left_b']
heroFrameIndex = 0
heroFrameTimer = 0

# Enemies
enemies = []
timeForNextEnemy = 0
enemyWalkFrames = ['enemy_a', 'enemy_b']
enemyFrameIndex = 0
enemyFrameTimer = 0

# Points 
points = 0
highestY = hero.y

# Platforms
platforms = []
minWidth = 150
maxWidth = 250
verticalSpace = 100


def draw():
    if state == "menu":
        drawsMenu()
    elif state == "game":
        drawsGame()
    elif state == "gameOver":
        drawsGameOver()


def update():
    global highestY

    if state != "game":
        return

    jumpAndCountPoints()

    horizontalMove()
    
    # Hero fell
    if hero.y > HEIGHT:
        endGame()
    
    heroPlatformColision()

    # Updates enemies
    for enemy in enemies:
        isOnPlatform = enemyPlatformColision(enemy)

        # Gravity
        if isOnPlatform == False:
            enemy.vy += gravity
            enemy.y += enemy.vy

        moveEnemy(enemy)

        # Hero colision
        heroHitbox = Rect((hero.x - 15, hero.y - 30), (40, 60))
        enemyHitbox = Rect((enemy.x - 15, enemy.y - 30), (40, 60))
        if heroHitbox.colliderect(enemyHitbox):
            endGame()

        global enemyFrameTimer, enemyFrameIndex, enemyWalkFrames
        if enemy.vy == 0: 
            enemyFrameTimer, enemyFrameIndex = updatesAnimation(enemyFrameTimer, enemyFrameIndex, enemyWalkFrames, enemy)

    # Remove enemies out of the screen
    enemies[:] = [i for i in enemies if i.y < HEIGHT + 100]

    generatesNewEnemies()

    verticalScroll()

    addAndRemovePlatforms()


def on_mouse_down(pos):
    global state, soundOn, points, highestY
    if state == "menu":
        if buttons["play"].collidepoint(pos):
            state = "game"
            hero.pos = initialPosition
            hero.vy = 0
            points = 0
            highestY = HEIGHT
            initializePlatforms()
            enemies.clear()
        elif buttons["sounds"].collidepoint(pos):
            soundOn = not soundOn
            if soundOn:
                music.play('background_music')
            else:
                music.stop()
        elif buttons["exit"].collidepoint(pos):
            sys.exit()
    elif state == "gameOver":
        if buttons["restart"].collidepoint(pos):
            state = "menu"
            if soundOn:
                music.play('background_music')
        elif buttons["exit"].collidepoint(pos):
            sys.exit()

def initializePlatforms():
    platforms.clear()
    platforms.append(Rect(((WIDTH // 2) - 200, 550), (400, 40)))
    y = HEIGHT - 50
    while y > -HEIGHT:
        x = random.randint(0, WIDTH - maxWidth)
        w = random.randint(minWidth, maxWidth)
        platforms.append(Rect((x, y), (w, 20)))
        y -= verticalSpace

def drawsMenu():
    menuBackground.draw()
    screen.draw.text("Hero Climber", center=(WIDTH/2, 60), fontsize=50, color=primaryColor)
    screen.draw.text("Use as setas para mover o seu heroi.", center=(WIDTH/2, 120), fontsize=30, color=primaryColor)
    screen.draw.text("Evite os inimigos que vem ao seu encontro.", center=(WIDTH/2, 150), fontsize=30, color=primaryColor)
    screen.draw.text("Suba o mais alto que puder.", center=(WIDTH/2, 180), fontsize=30, color=primaryColor)

    screen.draw.filled_rect(buttons["play"], primaryColor)
    screen.draw.text("Jogar", center=buttons["play"].center, fontsize=32, color="white")

    screen.draw.filled_rect(buttons["sounds"], configColor)
    som_texto = "Sons: Ligado" if soundOn else "Sons: Desligado"
    screen.draw.text(som_texto, center=buttons["sounds"].center, fontsize=28, color="white")

    screen.draw.filled_rect(buttons["exit"], alertColor)
    screen.draw.text("Sair", center=buttons["exit"].center, fontsize=32, color="white")

def drawsGame():
    gameBackground.draw()
    screen.draw.text("Pontos", center=(WIDTH - 50, 30), fontsize=28, color=primaryColor)
    screen.draw.text(str(points), center=(WIDTH - 50, 60), fontsize=24, color=primaryColor)
    for plat in platforms:
        screen.draw.filled_rect(plat, secondaryColor)
    hero.draw()
    for enemy in enemies:
        enemy.draw()

def drawsGameOver():
    gameBackground.draw()
    screen.draw.text("Game Over", center=(WIDTH/2, 60), fontsize=50, color=primaryColor)
    screen.draw.text("Pontos totais: " + str(points), center=(WIDTH/2, 120), fontsize=40, color=secondaryColor)

    screen.draw.filled_rect(buttons["restart"], primaryColor)
    screen.draw.text("Retornar ao Menu", center=buttons["restart"].center, fontsize=28, color="white")

    screen.draw.filled_rect(buttons["exit"], alertColor)
    screen.draw.text("Sair", center=buttons["exit"].center, fontsize=32, color="white")

def horizontalMove():
    global heroFrameTimer, heroFrameIndex, heroJumpRightFrames, heroJumpLeftFrames
    # Horizontal moviment
    if keyboard.left:
        hero.x -= 5
        if hero.x < 35:
            hero.x = 35
        heroFrameTimer, heroFrameIndex = updatesAnimation(heroFrameTimer, heroFrameIndex, heroJumpLeftFrames, hero)
    elif keyboard.right:
        hero.x += 5
        if hero.x > WIDTH - 35:
            hero.x = WIDTH - 35
        heroFrameTimer, heroFrameIndex = updatesAnimation(heroFrameTimer, heroFrameIndex, heroJumpRightFrames, hero)
    else:
        heroFrameTimer, heroFrameIndex = updatesAnimation(heroFrameTimer, heroFrameIndex, heroJumpUpFrames, hero)

def updatesAnimation(timer, index, frames, asset):
    timer += 1
    if timer >= 10:
        timer = 0
        index = (index + 1) % len(frames)
        asset.image = frames[index]
    return timer, index

def jumpAndCountPoints():
    global points
    hero.vy += gravity
    hero.y += hero.vy
    points = int(highestY // 10)

def endGame():
    global state
    if soundOn:
        music.stop()
        sounds.game_over.play()
    state = "gameOver"

def heroPlatformColision():
    if hero.vy > 0:
        footPosition = Rect((hero.x - 10, hero.y + hero.height // 2), (20, 5))
        for plat in platforms:
            if plat.colliderect(footPosition):
                hero.vy = jumpStrenght
                if soundOn:
                    sounds.jump.play()
                break

def enemyPlatformColision(enemy):
    isOnPlatform = False
    for plat in platforms:
        if Rect((enemy.x - 10, enemy.y + enemy.height // 2), (20, 5)).colliderect(plat):
            enemy.vy = 0
            isOnPlatform = True
            break
    return isOnPlatform

def moveEnemy(enemy):
    if enemy.vy == 0:
        if enemy.x < hero.x:
            enemy.x += 1.5
        elif enemy.x > hero.x:
            enemy.x -= 1.5

def generatesNewEnemies():
    global timeForNextEnemy
    timeForNextEnemy -= 1
    if timeForNextEnemy <= 0:
        newEnemy = Actor("enemy_a")
        newEnemy.x = random.randint(0, WIDTH)
        newEnemy.y = -50
        newEnemy.vy = 0
        enemies.append(newEnemy)
        timeForNextEnemy = random.randint(90, 200)

def verticalScroll():
    global highestY
    if hero.y < HEIGHT // 2:
        movementY = HEIGHT // 2 - hero.y
        hero.y = HEIGHT // 2
        for plat in platforms:
            plat.y += movementY
        for enemy in enemies:
            enemy.y += movementY
        highestY += movementY

def addAndRemovePlatforms():
    platforms[:] = [p for p in platforms if p.y < HEIGHT]
    while len(platforms) == 0 or min(p.y for p in platforms) > 0:
        x = random.randint(0, WIDTH - maxWidth)
        w = random.randint(minWidth, maxWidth)
        y = min(p.y for p in platforms) - verticalSpace if platforms else HEIGHT - 100
        platforms.append(Rect((x, y), (w, 20)))