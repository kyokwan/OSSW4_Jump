import pygame
import sys
import Map_1
import Map_2

pygame.init()

# 화면 크기 설정
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("점프 점프")

# 색깔 
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
FLOOR_COLOR = (144, 228, 144) # 바닥 색깔
PORTAL_COLOR = (255, 215, 0)  # 포탈 색깔 
SPIKE_COLOR = (0, 0, 0)  # 가시 색깔

# 캐릭터 속성 
character_width, character_height = 50, 50
character_x, character_y = 30, SCREEN_HEIGHT - character_height * 2
character_speed = 10
jump_speed = 20
gravity = 1.4

# 바닥 속성 
floor_height = 22  
floor_y = SCREEN_HEIGHT - floor_height

# 발판 속성 
platform_width, platform_height = 100, 20
platform_color = BLUE

# 가시 속성 및 위치
spike_width, spike_height = 10, 20
spike_positions = [(x, floor_y - spike_height) for x in range(400, 600, spike_width)]

# 점프 블록
class Block:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# 포탈 
class Portal:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# 맵 로드 
def load_map(map_module):
    blocks = [Block(x, y) for x, y in map_module.blocks_positions]
    portal = Portal(*map_module.portal_position)
    return blocks, portal

# 초기 맵 설정
map_modules = [Map_1, Map_2]
current_map_index = 0
blocks, portal = load_map(map_modules[current_map_index])

clock = pygame.time.Clock()

# 충돌 감지
def check_collision(character, blocks):
    for block in blocks:
        if character.colliderect(pygame.Rect(block.x, block.y, platform_width, platform_height)):
            return block
    return None

# 포탈 충돌 감지
def check_portal_collision(character, portal):
    portal_rect = pygame.Rect(portal.x, portal.y, platform_width, platform_height)
    return character.colliderect(portal_rect)

# 가시 충돌 감지
def check_spike_collision(character, spikes):
    for spike in spikes:
        if character.colliderect(pygame.Rect(spike[0], spike[1], spike_width, spike_height)):
            return True
    return False

# 다음 맵 로드
def load_next_map():
    global current_map_index, character_x, character_y, blocks, portal
    current_map_index += 1
    if current_map_index < len(map_modules):
        character_x, character_y = 30, SCREEN_HEIGHT - character_height * 2
        blocks, portal = load_map(map_modules[current_map_index])
    else:
        print("게임 클리어!")
        pygame.quit()
        sys.exit()

# 게임 초기화
def reset_game():
    global character_x, character_y, vertical_momentum, is_on_ground
    character_x, character_y = 30, SCREEN_HEIGHT - character_height * 2
    vertical_momentum = 0
    is_on_ground = True

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

    # 화면 범위 제한, 바닥 충돌 처리
    character_x = max(0, min(SCREEN_WIDTH - character_width, character_x))
    vertical_momentum += gravity
    character_y += vertical_momentum
    character_y = min(character_y, floor_y - character_height)

    # 바닥 
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

    # 포탈 충돌 검사
    if check_portal_collision(character_rect, portal):
        load_next_map()

    # 가시 충돌 검사
    if check_spike_collision(character_rect, spike_positions):
        reset_game()

    # 발판 
    for block in blocks:
        pygame.draw.rect(screen, platform_color, (block.x, block.y, platform_width, platform_height))

    # 가시 그리기
    for spike in spike_positions:
        pygame.draw.rect(screen, SPIKE_COLOR, (spike[0], spike[1], spike_width, spike_height))

    # 포탈 
    pygame.draw.rect(screen, PORTAL_COLOR, (portal.x, portal.y, platform_width, platform_height))

    # 캐릭터 
    pygame.draw.rect(screen, RED, character_rect)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
