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
FLOOR_COLOR = (144, 228, 144)  # 바닥 색
PORTAL_COLOR = (255, 215, 0)   # 포탈 색
SPIKE_COLOR = (0, 0, 0)        # 가시 색

# 캐릭터 속성
character_width, character_height = 20, 20
character_x, character_y = 30, SCREEN_HEIGHT - character_height * 2
character_speed = 6
jump_speed = 20
gravity = 1.4

# 바닥 속성
floor_height = 40
floor_segments = [(0, 230), (430, SCREEN_WIDTH)]
floor_y = SCREEN_HEIGHT - floor_height

# 발판 속성
platform_width, platform_height = 50, 20
platform_color = BLUE

# 가시 속성 및 위치
spike_width, spike_height = 10, 20
spike_positions = [(x, floor_y - spike_height) for x in range(550, 600, spike_width)]

# 점프 블록
class Block:
    def __init__(self, x, y, speed=0):
        self.x = x
        self.y = y
        self.speed = speed
        self.is_visible = True

    def move(self):
        if self.speed != 0:
            self.x += self.speed
            if self.x > SCREEN_WIDTH:
                self.is_visible = False

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

# 충돌 영역 설정
del_block_1 = pygame.Rect(220, 350, 100, 100)
del_block_2 = pygame.Rect(100, 220, 30, 30)
add_block_1 = pygame.Rect(50, 340, 30, 30)
trigger_moving_block_zone = pygame.Rect(160, 220, 30, 30)
clock = pygame.time.Clock()

# 폰트 설정
font = pygame.font.Font(None, 20)

# 타이머 설정
block_spawn_time = 0
block_spawn_delay = 2  # 2초 후 블록 생성

# 충돌 감지
def check_collision(character, blocks):
    for block in blocks:
        if block.is_visible and character.colliderect(pygame.Rect(block.x, block.y, platform_width, platform_height)):
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

# 특정 영역 충돌 감지
def check_trigger_zone_collision(character, trigger_zone):
    return character.colliderect(trigger_zone)

# 블록의 바닥과 충돌 감지
def check_bottom_collision(character, block):
    block_rect = pygame.Rect(block.x, block.y, platform_width, platform_height)
    if character.bottom >= block_rect.top and character.top < block_rect.top and character.right > block_rect.left and character.left < block_rect.right:
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
    global character_x, character_y, vertical_momentum, is_on_ground, blocks, additional_block_added_1, additional_block_added_2, moving_block_triggered, block_spawn_time, block_spawned
    character_x, character_y = 30, SCREEN_HEIGHT - character_height * 2
    vertical_momentum = 0
    is_on_ground = True
    additional_block_added_1 = False  
    additional_block_added_2 = False  
    moving_block_triggered = False  # 움직이는 블록 초기화
    block_spawn_time = 0  # 타이머 초기화
    block_spawned = False  # 블록이 생성되지 않은 상태로 초기화
    blocks, portal = load_map(map_modules[current_map_index])
    for block in blocks:
        block.is_visible = True

# 게임 루프
running = True
vertical_momentum = 0
is_on_ground = True
space_pressed = False
additional_block_added_1 = False 
additional_block_added_2 = False 
moving_block_triggered = False  # 움직이는 블록이 생성되었는지 여부
block_spawned = False  # 블록이 생성되었는지 여부

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

    # y가 600을 넘으면 게임 리셋
    if character_y > SCREEN_HEIGHT:
        reset_game()

    # 바닥과의 충돌 체크
    is_on_ground = False
    for floor_start, floor_end in floor_segments:
        if character_x + character_width > floor_start and character_x < floor_end and character_y >= floor_y - character_height:
            character_y = floor_y - character_height
            vertical_momentum = 0
            is_on_ground = True
            break

    # 바닥 그리기
    for floor_start, floor_end in floor_segments:
        pygame.draw.rect(screen, FLOOR_COLOR, (floor_start, floor_y, floor_end - floor_start, floor_height))

    # 충돌 검사 및 처리
    block_collided = check_collision(character_rect, blocks)
    if block_collided:
        if vertical_momentum > 0:
            character_y = block_collided.y - character_height
            vertical_momentum = 0
            is_on_ground = True
        elif check_bottom_collision(character_rect, block_collided):
            character_y = block_collided.y + platform_height
            vertical_momentum = 0

    # 포탈 충돌 검사
    if check_portal_collision(character_rect, portal):
        load_next_map()

    # 가시 충돌 검사
    if check_spike_collision(character_rect, spike_positions):
        reset_game()

    # 특정 영역 충돌 검사 및 처리
    if check_trigger_zone_collision(character_rect, del_block_1):
        blocks[1].is_visible = False  
        
    if check_trigger_zone_collision(character_rect, del_block_2):
        blocks[4].is_visible = False  
        
    # 움직이는 블록 생성 트리거
    if check_trigger_zone_collision(character_rect, trigger_moving_block_zone) and not moving_block_triggered and not block_spawned:
        block_spawn_time = pygame.time.get_ticks()  # 현재 시간 저장
        moving_block_triggered = True

    # 2초 후 움직이는 블록 생성
    if moving_block_triggered and not block_spawned and (pygame.time.get_ticks() - block_spawn_time) >= block_spawn_delay * 1000:
        moving_block = Block(-platform_width, 220, speed=5)  # 왼쪽에서 오른쪽으로 이동하는 블록
        blocks.append(moving_block)
        block_spawned = True  # 블록이 생성되었음을 표시

    # 추가 블록 영역 충돌 검사
    if character_rect.colliderect(add_block_1) and not additional_block_added_1:
        blocks.append(Block(50, 375))
        additional_block_added_1 = True

    # 블록 이동 및 충돌 검사
    for block in blocks:
        if block.speed != 0:
            block.move()
            if block.is_visible and character_rect.colliderect(pygame.Rect(block.x, block.y, platform_width, platform_height)):
                reset_game()

    # 발판
    for block in blocks:
        if block.is_visible:
            pygame.draw.rect(screen, platform_color, (block.x, block.y, platform_width, platform_height))
            # 발판 위치 좌표
            text = font.render(f"({block.x}, {block.y})", True, RED)
            screen.blit(text, (block.x, block.y - 20))

    # 가시 그리기
    for spike in spike_positions:
        pygame.draw.rect(screen, SPIKE_COLOR, (spike[0], spike[1], spike_width, spike_height))

    # 포탈
    pygame.draw.rect(screen, PORTAL_COLOR, (portal.x, portal.y, platform_width, platform_height))
    # 포탈 위치 텍스트 표시 # 나중 삭제
    text = font.render(f"({portal.x}, {portal.y})", True, RED)
    screen.blit(text, (portal.x, portal.y - 20))

    # 충돌 영역 그리기 (디버깅용) # 나중에 삭제 !!
    pygame.draw.rect(screen, (0, 0, 0), del_block_1, 2)
    pygame.draw.rect(screen, (0, 255, 0), add_block_1, 2)
    pygame.draw.rect(screen, (255, 0, 255), del_block_2, 2)
    pygame.draw.rect(screen, (0, 0, 255), trigger_moving_block_zone, 2)  # 트리거 영역

    # 캐릭터
    pygame.draw.rect(screen, RED, character_rect)
    pygame.display.update()
    clock.tick(60)  # 프레임 속도 유지

pygame.quit()
sys.exit()
