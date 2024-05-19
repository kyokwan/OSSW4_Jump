import pygame
import sys
import importlib

def run_stage():
    pygame.init()

# 화면 크기 설정
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("점프 점프")

# 색깔 정의
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
FLOOR_COLOR = (144, 228, 144)

# 캐릭터 속성 설정
character_width, character_height = 50, 50
character_x, character_y = 50, 50
character_speed = 6
jump_speed = 18
gravity = 1

# 바닥 속성 설정
floor_height = 22
floor_y = SCREEN_HEIGHT - floor_height

# 발판 속성 설정
platform_width, platform_height = 100, 20
platform_color = BLUE

# 블록 좌표 설정
blocks_positions = [
    (50, 100),
    (200, 400),
    (500, 300),
    (600, 200)
]

# 블록 클래스 정의
class Block:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# 블록 리스트 초기화
blocks = [Block(x, y) for x, y in blocks_positions]

# 포탈 클래스 정의
class Portal:
    def __init__(self, x, y, width, height, target_stage):
        self.rect = pygame.Rect(x, y, width, height)
        self.target_stage = target_stage

# 포탈 리스트 초기화
portal_width, portal_height = 40, 40
portals = Portal(629,  200 - portal_height - 10, portal_width, portal_height, 'stage3'),

clock = pygame.time.Clock()

# 충돌 감지
def check_collision(character, blocks):
    for block in blocks:
        if character.colliderect(pygame.Rect(block.x, block.y, platform_width, platform_height)):
            return block
    return None

# 포탈 충돌 감지
def check_portal_collision(character, portals):
    for portal in portals:
        if character.colliderect(portal.rect):
            return portal
    return None

# 게임 루프
running = True
vertical_momentum = 0
is_on_ground = True
space_pressed = False

while running:
    screen.fill(WHITE)
    character_rect = pygame.Rect(character_x, character_y, character_width, character_height)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                space_pressed = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                space_pressed = False

    if space_pressed and is_on_ground:
        vertical_momentum = -jump_speed
        is_on_ground = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        character_x -= character_speed
    if keys[pygame.K_RIGHT]:
        character_x += character_speed

    # 화면 범위 제한 및 바닥 충돌 처리
    character_x = max(0, min(SCREEN_WIDTH - character_width, character_x))
    vertical_momentum += gravity
    character_y += vertical_momentum
    character_y = min(character_y, floor_y - character_height)

    # 바닥 그리기
    pygame.draw.rect(screen, FLOOR_COLOR, (0, floor_y, SCREEN_WIDTH, floor_height))

    # 충돌 검사 및 처리
    block_collided = check_collision(character_rect, blocks)
    if block_collided:
        if vertical_momentum > 0:
            character_y = block_collided.y - character_height
            vertical_momentum = 0
            is_on_ground = True
    elif character_y >= floor_y - character_height:
        character_y = floor_y - character_height
        vertical_momentum = 0
        is_on_ground = True
    else:
        is_on_ground = False

    # 포탈 충돌 검사 및 처리
    portal_collided = check_portal_collision(character_rect, portals)
    if portal_collided:
        stage_module = importlib.import_module(portal_collided.target_stage)
        stage_module.run_stage()
        running = False

    # 발판 그리기
    for block in blocks:
        pygame.draw.rect(screen, platform_color, (block.x, block.y, platform_width, platform_height))

    # 포탈 그리기
    for portal in portals:
        pygame.draw.rect(screen, (255, 0, 255), portal.rect)  # 포탈 색상은 보라색으로 설정

    # 캐릭터 생성
    pygame.draw.rect(screen, RED, character_rect)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()