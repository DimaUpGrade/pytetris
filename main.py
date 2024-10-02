import pygame
from copy import deepcopy
from random import choice, randrange

W, H = 10, 20
TILE = 45
GAME_RES = W * TILE, H * TILE
RES = 750, 940
FPS = 75

pygame.init()
pygame.display.set_caption('PyTetris')
sc = pygame.display.set_mode(RES)
game_sc = pygame.Surface(GAME_RES)
clock = pygame.time.Clock()

grid = [pygame.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(W) for y in range(H)]

figures_pos = [
        [(-1, 0), (-2, 0), (0, 0), (1, 0)],
        [(0, -1), (-1, -1), (-1, 0), (0, 0)],
        [(-1, 0), (-1, 1), (0, 0), (0, -1)],
        [(0, 0), (-1, 0), (0, 1), (-1, -1)],
        [(0, 0), (0, -1), (0, 1), (-1, -1)],
        [(0, 0), (0, -1), (0, 1), (1, -1)],
        [(0, 0), (0, -1), (0, 1), (-1, 0)]
]

figures = [[pygame.Rect(x + W // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in figures_pos]
figure_rect = pygame.Rect(0, 0, TILE - 2, TILE - 2)
field = [[0 for _ in range(W)] for _ in range(H)]

anim_count, anim_speed, anim_limit = 0, 60, 2000
figure, next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))

window_bg = pygame.image.load('assets/images/window_bg.png').convert()
field_bg = pygame.image.load('assets/images/field_bg.png').convert()

title_font = pygame.font.Font('assets/fonts/Tiny5-Regular.ttf', 52)
regular_font = pygame.font.Font('assets/fonts/Tiny5-Regular.ttf', 32)

title_tetris = title_font.render('PYTETRIS', True, pygame.Color('white'))
title_score = regular_font.render('SCORE', True, pygame.Color('cyan'))
title_highscore = regular_font.render('HIGHSCORE', True, pygame.Color('purple'))

get_color = lambda : (randrange(30, 256), randrange(30, 256), randrange(30, 256))
color, next_color = get_color(), get_color()

score, lines = 0, 0
scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}


def check_borders():
    if figure[i].x < 0 or figure[i].x > W - 1:
        return False
    elif figure[i].y > H - 1 or field[figure[i].y][figure[i].x]:
        return False
    return True


def get_highscore():
    try:
        with open('highscore') as f:
            highscore = f.readline()
            return int(highscore)
    except FileNotFoundError:
        with open('highscore', 'w') as f:
            f.write('0')
    except ValueError:
        with open('highscore', 'w') as f:
            f.write('0')


def set_highscore(highscore, score):
    max_score = max(highscore, score)
    with open('highscore', 'w') as f:
        f.write(str(max_score))


while True:
    highscore = get_highscore()
    dx, rotate = 0, False
    sc.blit(window_bg, (0, 0))
    sc.blit(game_sc, (45, 20))
    game_sc.blit(field_bg, (0, 0))

    # delay for full lines
    for i in range(lines):
        pygame.time.wait(200)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_a, pygame.K_LEFT):
                dx = -1
            elif event.key in (pygame.K_d, pygame.K_RIGHT):
                dx = 1
            elif event.key in (pygame.K_s, pygame.K_DOWN):
                anim_limit = 100
            elif event.key in (pygame.K_w, pygame.K_UP):
                rotate = True

    # move x
    figure_old = deepcopy(figure)
    for i in range(4):
        figure[i].x += dx
        if not check_borders():
            figure = deepcopy(figure_old)
            break

    # move y
    anim_count += anim_speed
    if anim_count > anim_limit:
        anim_count = 0
        figure_old = deepcopy(figure)
        for i in range(4):
            figure[i].y += 1
            if not check_borders():
                for i in range(4):
                    field[figure_old[i].y][figure_old[i].x] = color
                figure, color = next_figure, next_color
                next_figure, next_color = deepcopy(choice(figures)), get_color()
                anim_limit = 2000
                break
    
    # rotate
    center = figure[0]
    figure_old = deepcopy(figure)
    if rotate:
        for i in range(4):
            x = figure[i].y - center.y
            y = figure[i].x - center.x
            figure[i].x = center.x - x
            figure[i].y = center.y + y

            if not check_borders():
                figure = deepcopy(figure_old)
                break

    # check lines
    line, lines = H - 1, 0
    for row in range(H - 1, -1, -1):
        count = 0
        for i in range(W):
            if field[row][i]:
                count += 1
            field[line][i] = field[row][i]
        if count < W:
            line -= 1
        else:
            anim_speed += 3
            lines += 1

    # compute score
    score += scores[lines]

    # draw grid
    [pygame.draw.rect(game_sc, (40, 40, 40), i_rect, 1) for i_rect in grid]

    # draw figure
    for i in range(4):
        figure_rect.x = figure[i].x * TILE
        figure_rect.y = figure[i].y * TILE
        pygame.draw.rect(game_sc, color, figure_rect)

    # draw next figure
    for i in range(4):
        figure_rect.x = next_figure[i].x * TILE + 380
        figure_rect.y = next_figure[i].y * TILE + 185
        pygame.draw.rect(sc, next_color, figure_rect)

    # draw field
    for y, row in enumerate(field):
        for x, col in enumerate(row):
            if col:
                figure_rect.x, figure_rect.y = x * TILE, y * TILE
                pygame.draw.rect(game_sc, col, figure_rect)

    # draw titles
    sc.blit(title_tetris, (512, 40))
    sc.blit(title_highscore, (535, 780))
    sc.blit(regular_font.render(str(highscore), True, pygame.Color('white')), (535, 820))
    sc.blit(title_score, (535, 500))
    sc.blit(regular_font.render(str(score), True, pygame.Color('white')), (535, 540))
    # game over
    for i in range(W):
        if field[0][i]:
            set_highscore(highscore, score)
            field = [[0 for _ in range(W)] for _ in range(H)]
            anim_count, anim_speed, anim_limit = 0, 60, 20000
            score = 0
            for i_rect in grid:
                pygame.draw.rect(game_sc, get_color(), i_rect)
                sc.blit(game_sc, (45, 20))
                pygame.display.flip()
                clock.tick(100)
            pygame.time.wait(1000)

    pygame.display.flip()
    clock.tick(FPS)