"""
tetris.py

a tetris implementation using python and pygame

100 line marathon

 todo list
===========
[x] fix rotation
[/] adjust lock in and leveling
[] get jiggy wit it
"""

import pygame as pg
from pygame.locals import *
from random import choice, shuffle

from piecedata import pieces, offset_data

pg.init()

W, H = 640, 480
PW, PH = 16, 16
BW, BH = 10, 22
SCREEN = pg.display.set_mode((W, H))
HEL16 = pg.font.SysFont("Helvetica", 16)
HEL32 = pg.font.SysFont("Helvetica", 32)
CLOCK = pg.time.Clock()
BOARD= []
for i in range(BH):
    BOARD.append([])
for line in BOARD:
    for i in range(BW):
        line.append(0)
    
POS = (4, 0),
PIECE = None
ROT = 0 # % 4
LVL = 1
LINES = 0
TIME = 0
NEXT_FIVE = []
HOLD = None

colorkey = {
    "I":(14, 176, 155),
    "O":(169, 179, 23),
    "T":(119, 33, 117),
    "S":(42, 152, 25),
    "Z":(148, 44, 44),
    "J":(43, 43, 127),
    "L":(151, 88, 34),
}

def get_board_as_surface():
    surface = pg.Surface((BW * PW, ((BH - 2) * PH)+6)) # give the player a glimpse at the hidden row
    surface.fill((100, 100, 100))
    for Y, line in enumerate(BOARD):
        for X, piece in enumerate(line):
            if piece in colorkey:
                pg.draw.rect(surface, colorkey[piece], pg.rect.Rect((X*PW, ((Y-2)*PH)+6), (PW, PH)))
    return surface

def get_HUD(bkg_color=(100, 100, 100)):
    surf = pg.Surface((128, 192))
    surf.blit(HEL16.render(""",.+*` Lines `*+., """, 0, (255, 255, 255)), (0, 0))
    surf.blit(HEL32.render(str(LINES), 0, (255, 255, 255)), (30, 16))
    surf.blit(HEL16.render(""",.+*` Time  `*+., """, 0, (255, 255, 255)), (0, 64))
    surf.blit(HEL32.render(str(TIME)[:-3], 0, (255, 255, 255)), (30, 80))
    surf.blit(HEL16.render(""",.+*` Level `*+., """, 0, (255, 255, 255)), (0, 128))
    surf.blit(HEL32.render(str(LVL), 0, (255, 255, 255)), (30, 144))
    return surf


def get_piece_as_surf(piece):
    surf = pg.Surface((PW * len(piece[0]), PH * len(piece)))
    surf.fill((1, 0, 0))
    for Y, line in enumerate(piece):
        for X, slot in enumerate(line):
            if slot in colorkey:
                pg.draw.rect(surf, colorkey[slot], pg.rect.Rect((X*PW, Y* PH), (PW, PH)))
    surf.set_colorkey((1, 0, 0))
    return surf


def get_next_five_display():
    surf = pg.Surface((5*PW, 25*PH))
    surf.fill((1, 0, 0))
    for i, pce in enumerate(NEXT_FIVE):
        surf.blit(get_piece_as_surf(pieces[pce][0]), (0, i*(4*PH)))
    surf.set_colorkey((1, 0, 0))
    return surf

def get(dest, pos): return dest[pos[1]][pos[0]]
def put(dest, pos, dump): dest[pos[1]][pos[0]] = dump

def place_piece(piece, pos):
    W, H = len(piece[0]), len(piece)
    _X, _Y = pos
    X, Y = 0, 0
    while Y < H:
        while X < W:
            try:
                if get(piece, (X, Y)) != 0:
                    if X+_X < 0: return False
                    if get(BOARD, (X+_X, Y+_Y)) != 0:
                        return False
            except IndexError: return False
            X += 1
        X = 0
        Y += 1
    X, Y = 0, 0
    while Y < H:
        while X < W:
            if get(piece, (X, Y)) != 0:
                put(BOARD, (X+_X, Y+_Y), get(piece, (X, Y)))
            X += 1
        X = 0
        Y += 1
    return True


def remove_piece(piece, pos):
    W, H = len(piece[0]), len(piece)
    _X, _Y = pos
    X, Y = 0, 0
    while Y < H:
        while X < W:
            if get(piece, (X, Y)) != 0:
                put(BOARD, (X+_X, Y+_Y), 0)
            X += 1
        X = 0
        Y += 1


def fill_pieces():
    global NEXT_FIVE
    if len(NEXT_FIVE) < 5:
        more = ["I", "O", "T", "S", "Z", "J", "L"]
        shuffle(more)
        NEXT_FIVE += more


def make_piece(spawn=(4, 0)):
    global POS, PIECE, ROT
    piece = NEXT_FIVE.pop(0)
    fill_pieces()

    POS = spawn
    ROT = 0
    PIECE = pieces[piece][ROT]
    return place_piece(PIECE, POS)


def move_piece(x, y):
    global POS
    remove_piece(PIECE, POS)
    if place_piece(PIECE, (POS[0]+x, POS[1]+y)):
        POS = (POS[0]+x, POS[1]+y)
        return True
    else:
        place_piece(PIECE, POS)
        return False


def rotate_piece(cl): # 1 for clockwise, -1 for counter clockise
    """ attempted implementation of the SRS system """
    global PIECE, ROT, POS
    i=0
    while PIECE[i][i] == 0: i += 1
    piece = PIECE[i][i]
    for key in offset_data:
        if piece is "O":
            offsets = [(0, 0)]
        if piece in key:
            offsets = offset_data[key][(ROT, (ROT + cl) % 4)]
    
    remove_piece(PIECE, POS)
    for offs in offsets:
        offset = POS[0] + offs[0], POS[1] + offs[1]
        if place_piece(pieces[piece][(ROT + cl) % 4], offset):
            ROT = (ROT + cl) % 4
            PIECE = pieces[piece][ROT]
            POS = offset
            break
            
def _pprint():
    print(NEXT_FIVE)
    s = "+" * 10
    for line in BOARD:
        for piece in line:
            if piece == 0: s += " "
            else: s += piece
        s += "\n"
    print(s)


def check_lines():
    global LINES, LVL
    dead = []
    for i, line in enumerate(BOARD):
        if 0 not in line: dead.append(i)
    if dead:
        LINES += len(dead)
        if len(dead) == 4: LINES += 1
        t = 0
        CLOCK.tick()
        while t < 300:
            t += CLOCK.tick()
            for n in dead:
                pg.draw.rect(  SCREEN,
                               (255, 255, 255),
                               pg.rect.Rect((50, 90 + PH*(n-1)), (BW*PW, PH)))
            pg.display.update()
        for n in dead:
            BOARD.pop(n)
            BOARD.insert(0, [0,]*10)
    LVL = (LINES // 15) + 1

def hold():
    global HOLD, PIECE, POS
    remove_piece(PIECE, POS)
    if HOLD is not None:
        PIECE, HOLD = HOLD, PIECE
        POS = (4, 0)
    else:
        HOLD = PIECE
        make_piece()

if __name__ == "__main__":
    fill_pieces()
    Quit = False
    CLOCK.tick()
    f = 0
    down = False
    swap = False
    while not Quit and LINES < 100:
        f += 1
        TIME += CLOCK.tick(30)
        if PIECE is None: make_piece()
        rotate = False; move = False; drop = False
        for e in pg.event.get():
            if e.type == QUIT: Quit = True
            if e.type == KEYDOWN:
                if e.key == K_p: import pdb; pdb.set_trace()
                if e.key == K_z: rotate = -1
                if e.key == K_x: rotate = 1
                if e.key == K_LEFT: move = -1
                if e.key == K_RIGHT: move = 1
                if e.key == K_DOWN: down = True
                if e.key == K_UP: drop = True
                if e.key == K_SPACE and not swap:
                    swap = True
                    hold()
            if e.type == KEYUP:
                if e.key == K_DOWN: down = False
        if rotate:
            f = 0
            rotate_piece(rotate)
        if move: move_piece(move, 0)
        if f % (30 // LVL) == 0 or down:
            if move_piece(0, 1): f = 0
            elif min(f / (15 // LVL) > 1.5, 30):
                check_lines()
                swap = False
                if not make_piece(): Quit = True
        if drop:
            while move_piece(0, 1): continue
            check_lines()
            swap = False
            if not make_piece(): Quit = True
        SCREEN.fill((0, 0, 0))
        SCREEN.blit(HEL32.render(""",.+*`*+.,.+*`*+.,.+*` Tetris `*+.,.+*`*+.,.+*`*+.,""", 0, (255, 255, 255)), (14, 16))
        SCREEN.blit(get_board_as_surface(), (50, 100))
        SCREEN.blit(get_next_five_display(), (230, 100))
        SCREEN.blit(get_HUD(), (312, 132))
        if HOLD is not None:
            SCREEN.blit(get_piece_as_surf(HOLD), (18, 68))
        pg.display.update()

    pg.display.quit()
    pg.quit()

    with open('halloffame.txt', 'r') as f:
        halloffame = eval(f.read())
    
    i = 0
    while i < len(halloffame): 
        name, lines, time = halloffame[i]
        if lines < LINES or (lines == LINES and int(time) < int(TIME)):
            break
        i += 1
    halloffame.insert(i, (input("name?\n> "), LINES, str(TIME)[:-3]))

    with open('halloffame.txt', "w") as f:
        f.write(repr(halloffame[:10]))
    print(" +====================+")
    print("+######################+")
    print("|#### HALL OF FAME ####|")
    print("+######################+")
    print(" + name | lines  time +")
    for name, lines, time in halloffame:
        print(name[:8] + " "*(8 - len(name))+"|", lines, "    ", time)
