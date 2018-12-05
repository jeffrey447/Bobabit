# Boba Bit
# by Henry C, Jeffrey H, Stephanie K, Mary N
import pygame
import sys
import os
import time
import random
# https://www.pygame.org/docs/tut/PygameIntro.html

pygame.init() #initalize pygame in general
pygame.mixer.init() # initalize the sound service

# screen in the beginning introducing all droppings
# 3 toppings : black boba, lychee jelly, pudding
### Lose a life if you catch a $0.50 coin
### Point system: boba: 1, lychee jelly: , pudding: 
# no winning condition; just track hiscore
# Losing condition: drop 3 toppings 3 lives

# 0 = MENU
# 1 = INSTRUCTIONS
# 2 = PLAY FIELD
# 3 = GAME RESULTS
state = 0

SETTINGS = {
  "maxLives": 3,
  "toppings": [
    {"name": "boba", "points": 1},
    {"name": "bean", "points": 2},
    {"name": "lychee", "points": 3},
    {"name": "pudding", "points": 4},
    {"name": "coin", "points": -1}
  ]
}

highScore = 0
score = 0
lives = SETTINGS['maxLives']

def get_files(dir):
    for (_, _, filenames) in os.walk(dir):
        return filenames

images = {}
for file in get_files('assets/images/'):
    name = os.path.splitext(file)[0]
    images[name] = pygame.image.load('assets/images/' + file)

sfx = {}
for file in get_files('assets/sfx/'):
    info = os.path.splitext(file)
    
    name = info[0]
    ext = info[1]

    path = 'assets/sfx/' + file
    
    if ext == '.ogg':
        pygame.mixer.music.load(path)
    else:
        sfx[name] = pygame.mixer.Sound(path)


size = (width, height) = (500, 750)
scrn = pygame.display.set_mode(size)
pygame.display.set_caption('BobaBit')
pygame.display.set_icon(images['appicon'])
# we should have one .ogg file that is loaded so we'll play it then loop it indefinitely
pygame.mixer.music.play(-1)

class Topping: # Inherit the base Sprite class.
    def __init__(self, index):
        pygame.sprite.Sprite.__init__(self)
        
        details = SETTINGS['toppings'][index]
        self.index = index
        self.name = details['name']
        self.points = details['points']
        self.image = images[self.name]
        self.size = self.image.get_size()
        
        self.x = 0
        self.y = 0

MAINFONT = 'assets/fonts/bubblegun.ttf'
mFont = pygame.font.Font(MAINFONT, 24)

# EDITING IMAGES HERE
images['bg'] = pygame.transform.scale(images['bg'], size)
images['logo'] = pygame.transform.scale(images['logo'], (int(568 // 1.25), int(382 // 1.25)))
images['gameover'] = pygame.transform.scale(images['gameover'], (int(1060 // 2.35), int(660 // 2.35)))

toppSize = (x, y) = (50,50)
images['boba'] = pygame.transform.scale(images['boba'], toppSize)
images['bean'] = pygame.transform.scale(images['bean'], toppSize)
images['lychee'] = pygame.transform.scale(images['lychee'], toppSize)
images['pudding'] = pygame.transform.scale(images['pudding'], toppSize)
images['coin'] = pygame.transform.scale(images['coin'], toppSize)

images['heart'] = pygame.transform.scale(images['heart'], (25,25))
images['heart_grey'] = pygame.transform.scale(images['heart_grey'], (25,25))
images['cup'] = pygame.transform.scale(images['cup'], (100, 143))

images['rightkey'] = pygame.transform.scale(images['rightkey'], (25, 25))
images['leftkey'] = pygame.transform.flip(images['rightkey'], True, False)
images['shift'] = pygame.transform.scale(images['shift'], (25, 35))

playRect = pygame.Rect((width - 300) // 2, (height + 450) // 2, 300, 120)
images['playbtn'] = pygame.transform.scale(images['playbtn'], playRect.size)

initX = (width - images['cup'].get_size()[0]) // 2
movementX = 0
leftHold = False
rightHold = False
shiftHold = False

lastCreated = time.time()

collided = False # debounce, preventing multiple collision detection
toppings = []
particles = []

def getSpeed(score):
    fallSpeed = 0.25
    spawnSpeed = 0.8
    if score > 10 and score <= 20:
        fallSpeed = 0.3
        spawnSpeed = 0.7
    elif score > 20 and score <= 40:
        fallSpeed = 0.4
        spawnSpeed = 0.6
    elif score > 40 and score <= 60:
        fallSpeed = 0.5
        spawnSpeed = 0.45
    elif score > 60:
        fallSpeed = 0.65
        spawnSpeed = 0.4
    
    return {
        "fallSpeed": fallSpeed,
        "spawnSpeed": spawnSpeed
    }

while True:
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            sys.exit() # make sure pygame clears everything out smoothly
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_SPACE:
                if state == 0:
                    state = 1
                elif state == 3:
                    lives = 3 # RESET
                    score = 0
                    toppings = []
                    mFont = pygame.font.Font(MAINFONT, 24)
                    state = 0
            elif ev.key == pygame.K_LEFT:
                leftHold = True
            elif ev.key == pygame.K_RIGHT:
                rightHold = True
            elif ev.key == pygame.K_LSHIFT or ev.key == pygame.K_RSHIFT:
                shiftHold = True
        elif ev.type == pygame.KEYUP:
            if ev.key == pygame.K_LEFT:
                leftHold = False
            elif ev.key == pygame.K_RIGHT:
                rightHold = False
            elif ev.key == pygame.K_LSHIFT or ev.key == pygame.K_RSHIFT:
                shiftHold = False
        elif ev.type == pygame.MOUSEBUTTONUP:
            pos = ev.pos
            if playRect.collidepoint(pos) and state == 1:
                state = 2
    
    scrn.blit(images['bg'], (0, 0))
    if (state == 0):
        # draw the menu
        scrn.blit(images['logo'], ((15, 15)))
        credits = mFont.render('Game developed by Henry C., Jeff H.,', True, (0,0,0))
        credits2 = mFont.render('Mary N., & Stephanie K.', True, (0,0,0))
        menuInstr = mFont.render('Press "Space" to proceed', True, (0,0,0))
        scrn.blit(credits, ((width / 2) - 200, (height / 2) + 250))
        scrn.blit(credits2, ((width / 2) - 127, (height / 2) + 275))
        scrn.blit(menuInstr, ((width / 2) - 125, (height / 2) - 50))
    
    elif (state == 1):
        # toppings descriptions
        instructions = mFont.render('Collect boba toppings to earn points!', True, (0,0,0)) #draws instructions
        scrn.blit(instructions, (30, 30))
        scrn.blit(images['boba'], (50, 75))
        bobaInfo = mFont.render ('Boba Pearls: +1 point', True, (0,0,0)) #draws boba info
        scrn.blit(bobaInfo, (150, 90))
        scrn.blit(images['bean'], (50, 150))
        beanInfo = mFont.render ('Red Bean: +2 points', True, (0,0,0)) #draws red bean info
        scrn.blit(beanInfo, (150, 160))
        scrn.blit(images['lychee'], (50, 225))
        lycheeInfo = mFont.render ('Lychee Jelly: +3 points', True, (0,0,0)) #draws lychee info
        scrn.blit(lycheeInfo, (150, 235))
        scrn.blit(images['pudding'], (50, 300))
        puddingInfo = mFont.render ('Egg Pudding: +3 points', True, (0,0,0)) #draws pudding info
        scrn.blit(puddingInfo, (150, 315))
        scrn.blit(images['coin'], (50, 375))
        coinInfo = mFont.render ('Extra Topping Charge: -1 Life', True, (0,0,0)) #coin info
        scrn.blit(coinInfo, (150, 390))
        
        #instructions
        scrn.blit(images['heart'], (30, 450))
        scrn.blit(images['heart'], (55, 450))
        scrn.blit(images['heart'], (80, 450))
        lifeInfo = mFont.render ('3 LIVES', True, (0,0,0))
        scrn.blit(lifeInfo, (115, 450))
        lifeInfo2 = mFont.render ('Miss a topping or collect a coin = -1 life', True, (0,0,0))
        scrn.blit(lifeInfo2, (50, 475))
        scrn.blit(images['leftkey'], (30, 510))
        scrn.blit(images['rightkey'], (55, 510))
        keyInfo = mFont.render ('Use left and right arrow keys to move', True, (0,0,0))
        scrn.blit(keyInfo, (90, 510))
        scrn.blit(images['shift'], (30, 545))
        shiftInfo = mFont.render ('Hold shift to speed up', True, (0,0,0))
        scrn.blit(shiftInfo, (70, 547))
        
        scrn.blit(images['playbtn'], (playRect.x, playRect.y))
    
    elif (state == 2):
        # play field
        scoreLabel = mFont.render('Score: ' + str(score), True, (0,0,0))
        scrn.blit(scoreLabel, (5, height-35))
        
        scoreHLabel = mFont.render('High Score: ' + str(highScore), True, (0,0,0))
        scrn.blit(scoreHLabel, (5, height-60))
        
        for i in range(SETTINGS['maxLives'], 0, -1):
            # if i > lives then make that image grayed out since they lost that life
            scrn.blit(images['heart_grey'] if (i > lives) else images['heart'], 
                     (((width - 10) - (i*25), height - 35)))
        
        cupRect = scrn.blit(images['cup'], (initX + movementX, height-195))
        hitboxRect = pygame.Rect(cupRect.x, cupRect.y-25, cupRect.width, 50)     
        
        if leftHold:
            if ((initX + movementX) - 0.5 >= 0):
                movementX -= 0.5 if not shiftHold else 0.8
        elif rightHold:
            if ((initX + movementX) + 0.5 <= (width - images['cup'].get_size()[0])):
                movementX += 0.5 if not shiftHold else 0.8
        
        movementDetails = getSpeed(score)
        currentTime = time.time()
        if( (currentTime - lastCreated) >= movementDetails['spawnSpeed'] ):
            lastCreated = currentTime
            topp = Topping(random.randint(0, 4))
            topp.x = random.randint(0 + topp.size[0], width - topp.size[1])
            toppings.append(topp)
        
        for topp in toppings:
            if topp.y > (height - topp.size[1]):
                # lose a life
                toppings.remove(topp)
                if (topp.points > 0):
                    # indicating it is not a coin
                    lives -= 1
                    
                    if lives < 1:
                        # done
                        sfx['gameover'].play()
                        state = 3
            else:
                topp.y += movementDetails['fallSpeed']
                toppRect = scrn.blit(topp.image, (topp.x, topp.y))
                
                if toppRect.colliderect(hitboxRect) and not collided:
                    # the topping landed on the top of the cup which is the hitbox
                    collided = True
                    if (topp.points > 0):
                        score += topp.points
                        if (score > highScore):
                            highScore = score
                    else:
                        # negative meaning lose a life
                        lives -= 1
                        
                        if lives < 1:
                            # done
                            sfx['gameover'].play()
                            state = 3
                    sfx['pointgain'].play()
                    toppings.remove(topp)
                    collided = False
    elif (state == 3):
        # end screen
        mFont = pygame.font.Font(MAINFONT, 50)
        
        scrn.blit(images['gameover'], ((width // 2) - 220, 25))
        endScore = mFont.render ('Final score: ' + str(score), True, (0,0,0))
        scrn.blit(endScore, (100, 300))
        highScoreS = mFont.render('High score: ' + str(highScore), True, (0,0,0))
        scrn.blit(highScoreS, (100, 350))
        
        mFont = pygame.font.Font(MAINFONT, 35)
        returnToMain = mFont.render('Press "Space" to', True, (0,0,0))
        returnToMain2 = mFont.render('return to menu!', True, (0,0,0))
        scrn.blit(returnToMain, (15, 670))
        scrn.blit(returnToMain2, (15, 705))
    
    # update the graphics
    pygame.display.flip()