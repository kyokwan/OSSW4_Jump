import pygame
import sys
import Map_1

pygame.init()

# 화면 크기 설정
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("점프 점프")

# 색깔
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
FLOOR_COLOR = (144, 228, 144)  # 바닥 색
SPIKE_COLOR = (0, 0, 0)        # 가시 색

# 캐릭터 속성
character_width, character_height = 20, 20
character_x, character_y = 30, SCREEN_HEIGHT - character_height * 2
character_speed = 6
jump_speed = 20
gravity = 1.4

# 바닥 속성
floor_height = 40
floor_y = SCREEN_HEIGHT - floor_height

# 발판 속성
platform_width, platform_height = 50, 20
platform_color = BLUE

# 가시 속성 및 위치
spike_width, spike_height = 10, 20
spike_positions = [(x, floor_y - spike_height) for x in range(550, 600, spike_width)]

# 맵의 최대 크기
max_map_width = 1200

# 바닥 구멍 정보 로드
floor_holes = Map_1.floor_holes

# 포탈 속성
portal_position = Map_1.portal_position
portal_size = 70

# 포탈 이미지 로드
portal_image = pygame.image.load('portal_image.png')
portal_image = pygame.transform.scale(portal_image, (portal_size, portal_size))
portal_angle = 0  # 포탈 회전 각도 초기화

# 점프 블럭 속성
class Block:
    def __init__(self, x, y, speed=0, cloud=False):
        self.x = x
        self.y = y
        self.speed = speed
        self.cloud = cloud  # 구름 블록 여부
        self.is_visible = True

    def move(self):
        if self.speed != 0:
            self.x += self.speed
            if self.x > SCREEN_WIDTH:
                self.is_visible = False

jumping_block = Block(1100, 400)
jumping_block.is_visible = False

# 트리거 영역
trigger_zone = pygame.Rect(1100, 350, 20, 20)

# 맵 로드
def load_map(map_module):
    blocks = [Block(x, y, cloud=(y == 260 and x in [100])) for x, y in map_module.blocks_positions]
    return blocks

# 초기 맵 설정
map_modules = [Map_1]
current_map_index = 0
blocks = load_map(map_modules[current_map_index])

def check_collision(character, blocks):
    for block in blocks:
        if block.is_visible and not block.cloud and character.colliderect(pygame.Rect(block.x, block.y, platform_width, platform_height)):
            return block
    return None

def check_spike_collision(character, spikes):
    for spike in spikes:
        if character.colliderect(pygame.Rect(spike[0], spike[1], spike_width, spike_height)):
            return True
    return False

def check_trigger_zone_collision(character, trigger_zone):
    return character.colliderect(trigger_zone)

def check_portal_collision(character, portal_pos, portal_size):
    portal_rect = pygame.Rect(portal_pos[0], portal_pos[1], portal_size, portal_size)
    return character.colliderect(portal_rect)

def load_next_map():
    global current_map_index, character_x, character_y, blocks, camera_x
    current_map_index += 1
    if current_map_index < len(map_modules):
        character_x, character_y = 30, SCREEN_HEIGHT - character_height * 2
        camera_x = 0
        blocks = load_map(map_modules[current_map_index])
    else:
        print("게임 클리어!")
        pygame.quit()
        sys.exit()

def reset_game():
    global character_x, character_y, vertical_momentum, is_on_ground, blocks, camera_x, jumping_block
    character_x, character_y = 30, SCREEN_HEIGHT - character_height * 2
    vertical_momentum = 0
    is_on_ground = True
    camera_x = 0
    blocks = load_map(map_modules[current_map_index])
    for block in blocks:
        block.is_visible = True
    jumping_block.is_visible = False

running = True
vertical_momentum = 0
is_on_ground = True
space_pressed = False
camera_x = 0

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

    character_x = max(0, character_x)
    character_x = min(character_x, max_map_width - character_width)

    vertical_momentum += gravity
    character_y += vertical_momentum

    if character_y > SCREEN_HEIGHT:
        reset_game()

    is_on_ground = False
    if character_y >= floor_y - character_height:
        is_in_hole = False
        for hole_start, hole_end in floor_holes:
            if hole_start < character_x < hole_end:
                is_in_hole = True
                break

        if not is_in_hole: 
            character_y = floor_y - character_height
            vertical_momentum = 0
            is_on_ground = True

    if character_x > SCREEN_WIDTH // 2:
        camera_x = character_x - SCREEN_WIDTH // 2
        camera_x = min(camera_x, max_map_width - SCREEN_WIDTH)
    else:
        camera_x = 0

    pygame.draw.rect(screen, FLOOR_COLOR, (0 - camera_x, floor_y, max_map_width, floor_height))
    for hole_start, hole_end in floor_holes:
        pygame.draw.rect(screen, WHITE, (hole_start - camera_x, floor_y, hole_end - hole_start, floor_height))

    if check_trigger_zone_collision(character_rect, trigger_zone):
        jumping_block.is_visible = True

    if jumping_block.is_visible:
        pygame.draw.rect(screen, platform_color, (jumping_block.x - camera_x, jumping_block.y, platform_width, platform_height))

    if character_rect.colliderect(pygame.Rect(jumping_block.x, jumping_block.y, platform_width, platform_height)):
        character_y = -character_height  # 맵 밖으로 점프하여 죽음

    block_collided = check_collision(character_rect, blocks)
    if block_collided:
        if vertical_momentum > 0:
            character_y = block_collided.y - character_height
            vertical_momentum = 0
            is_on_ground = True

    if check_spike_collision(character_rect, spike_positions):
        reset_game()

    for block in blocks:
        if block.is_visible:
            pygame.draw.rect(screen, platform_color, (block.x - camera_x, block.y, platform_width, platform_height))

    portal_angle += 2
    rotated_portal_image = pygame.transform.rotate(portal_image, portal_angle)
    portal_rect = rotated_portal_image.get_rect(center=(portal_position[0] - camera_x + portal_size // 2, portal_position[1] + portal_size // 2))
    screen.blit(rotated_portal_image, portal_rect.topleft)

    if check_portal_collision(character_rect, portal_position, portal_size):
        load_next_map()

    pygame.draw.rect(screen, RED, character_rect.move(-camera_x, 0))
    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
