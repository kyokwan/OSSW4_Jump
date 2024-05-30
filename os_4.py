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

# trick_hole 속성 추가
trick_hole_x, trick_hole_y = 700, floor_y
trick_hole_visible = False
trick_hole_speed = 2  # 트릭홀이 내려가는 속도

# 점프 블록의 가로 길이 설정
jumping_block_width = platform_width + 15  # 기본 플랫폼 가로 길이보다 15 증가

# 점프 블록
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

# 맵 로드
def load_map(map_module):
    blocks = [Block(x, y, cloud=(y == 260 and x in [100])) for x, y in map_module.blocks_positions]
    return blocks

# 초기 맵 설정
map_modules = [Map_1]
current_map_index = 0
blocks = load_map(map_modules[current_map_index])

# 충돌 영역 설정
del_block_1 = pygame.Rect(220, 350, 100, 100)
add_block_1 = pygame.Rect(50, 340, 30, 30)
trigger_moving_block_zone = pygame.Rect(160, 220, 30, 30)
trigger_falling_block_zone = pygame.Rect(800, 320, 50, 10)  # 트리거 영역 수정
clock = pygame.time.Clock()
trigger_zone = pygame.Rect(680, 510, 240, 50)
spike_trigger_zone = pygame.Rect(540, 455, 20, 100)
jumping_block = Block(1100, 450)
jumping_block.is_visible = False
jumping_trigger_zone = pygame.Rect(1050, 400, 150, 20)  # 점핑 블럭 트리거 영역 추가

# 폰트 설정
font = pygame.font.Font(None, 20)

# 타이머 설정
block_spawn_time = 0
block_spawn_delay = 2  # 2초 후 블록 생성

# 떨어지는 블록 설정
falling_block = Block(800, 0, speed=10)  # 속도를 2배로 빠르게 설정
falling_block.is_visible = False  # 초기에는 보이지 않도록 설정

def check_collision(character, blocks):
    for block in blocks:
        if block.is_visible and not block.cloud and character.colliderect(pygame.Rect(block.x, block.y, platform_width, platform_height)):
            return block
    return None

def check_bottom_collision(character, block):
    if block.cloud:  # 구름 블록일 경우
        if character.bottom >= block.y and character.top < block.y and character.right > block.x and character.left < block.x + platform_width:
            return True
    else:
        block_rect = pygame.Rect(block.x, block.y, platform_width, platform_height)
        if character.bottom >= block_rect.top and character.top < block_rect.top and character.right > block_rect.left and character.left < block_rect.right:
            return True
    return False

# 가시 충돌 감지
def check_spike_collision(character, spikes):
    for spike in spikes:
        if character.colliderect(pygame.Rect(spike[0], spike[1], spike_width, spike_height)):
            return True
    return False

# 특정 영역 충돌 감지
def check_trigger_zone_collision(character, trigger_zone):
    return character.colliderect(trigger_zone)

# 떨어지는 블록 충돌 감지
def check_falling_block_collision(character, block):
    block_rect = pygame.Rect(block.x, block.y, platform_width, platform_height)
    if character.colliderect(block_rect):
        return True
    return False

# 포탈 충돌 감지
def check_portal_collision(character, portal_pos, portal_size):
    portal_rect = pygame.Rect(portal_pos[0], portal_pos[1], portal_size, portal_size)
    return character.colliderect(portal_rect)

# 다음 맵 로드
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

# 바닥 속성을 변경
floor_dropped = False
drop_y = SCREEN_HEIGHT - floor_height + 200  # 떨어진 바닥의 y 좌표

# 게임 초기화
def reset_game():
    global character_x, character_y, vertical_momentum, is_on_ground, blocks, additional_block_added_1, additional_block_added_2, moving_block_triggered, block_spawn_time, block_spawned, camera_x, trick_hole_visible, trick_hole_y, falling_block, spike_height, spike_positions, spike_triggered, on_jumping_block, jump_timer
    character_x, character_y = 30, SCREEN_HEIGHT - character_height * 2
    vertical_momentum = 0
    is_on_ground = True
    additional_block_added_1 = False  
    additional_block_added_2 = False  
    moving_block_triggered = False  # 움직이는 블록 초기화
    block_spawn_time = 0  # 타이머 초기화
    block_spawned = False  # 블록이 생성되지 않은 상태로 초기화
    camera_x = 0  # 카메라 초기화
    blocks = load_map(map_modules[current_map_index])
    for block in blocks:
        block.is_visible = True
    trick_hole_visible = False  # 트릭 홀 초기화
    trick_hole_y = floor_y  # 트릭홀 위치 초기화
    falling_block = Block(800, 0, speed=10)  # 속도를 2배
    falling_block.is_visible = False  # 초기에는 보이지 않도록 설정
    spike_height = 20  # 가시 높이 초기화
    spike_positions = [(x, floor_y - spike_height) for x in range(550, 600, spike_width)]  # 가시 위치 초기화
    spike_triggered = False  # 가시 트리거 초기화
    jumping_block.is_visible = False  # 점핑 블럭 초기화
    on_jumping_block = False  # 점핑 블럭 상태 초기화
    jump_timer = 0  # 점핑 블럭 타이머 초기화
    
# 게임 루프
running = True
vertical_momentum = 0
is_on_ground = True
space_pressed = False
additional_block_added_1 = False 
additional_block_added_2 = False 
moving_block_triggered = False  
block_spawned = False  
camera_x = 0  # 카메라 초기화
on_jumping_block = False  # 점핑 블럭 상태 초기화
jump_timer = 0  # 점핑 블럭 타이머 초기화

# 캐릭터의 상단이 블록의 하단에 닿을 때
def check_top_collision(character, block):
    block_rect = pygame.Rect(block.x, block.y, platform_width, platform_height)
    if (character.top <= block_rect.bottom and character.bottom > block_rect.bottom and
            character.right > block_rect.left and character.left < block_rect.right):
        return True
    return False

# 게임 루프 내 충돌 검사 및 처리 부분 수정
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

    if not on_jumping_block:
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

    if trick_hole_visible:
        pygame.draw.rect(screen, WHITE, (trick_hole_x - camera_x, trick_hole_y, 30, floor_height))
        if trick_hole_y < SCREEN_HEIGHT:
            trick_hole_y += trick_hole_speed  # 트릭홀의 y 좌표를 점진적으로 증가시킴
    else:
        pygame.draw.rect(screen, FLOOR_COLOR, (trick_hole_x - camera_x, floor_y, 220, floor_height))

    if check_trigger_zone_collision(character_rect, trigger_falling_block_zone):
        falling_block.is_visible = True

    if falling_block.is_visible:
        falling_block.y += falling_block.speed
        pygame.draw.rect(screen, platform_color, (falling_block.x - camera_x, falling_block.y, platform_width, platform_height))

    if check_falling_block_collision(character_rect, falling_block):
        reset_game()

    block_collided = check_collision(character_rect, blocks)
    if block_collided:
        if vertical_momentum > 0:
            character_y = block_collided.y - character_height
            vertical_momentum = 0
            is_on_ground = True
        elif check_top_collision(character_rect, block_collided):
            character_y = block_collided.y + platform_height
            vertical_momentum = gravity
            is_on_ground = False

    if check_spike_collision(character_rect, spike_positions):
        reset_game()

    if check_trigger_zone_collision(character_rect, trigger_zone):
        trick_hole_visible = True
        
    if check_trigger_zone_collision(character_rect, del_block_1):
        blocks[1].is_visible = False
        
    if check_trigger_zone_collision(character_rect, trigger_moving_block_zone) and not moving_block_triggered and not block_spawned:
        block_spawn_time = pygame.time.get_ticks()
        moving_block_triggered = True

    if moving_block_triggered and not block_spawned and (pygame.time.get_ticks() - block_spawn_time) >= block_spawn_delay * 400:
        moving_block = Block(-platform_width, 230, speed=9)
        blocks.append(moving_block)
        block_spawned = True

    if character_rect.colliderect(add_block_1) and not additional_block_added_1:
        blocks.append(Block(50, 375))
        additional_block_added_1 = True

    if character_rect.colliderect(jumping_trigger_zone):
        jumping_block.is_visible = True

    if jumping_block.is_visible:
        pygame.draw.rect(screen, platform_color, (jumping_block.x - camera_x, jumping_block.y, jumping_block_width, platform_height))
        if character_rect.colliderect(pygame.Rect(jumping_block.x, jumping_block.y, jumping_block_width, platform_height)):
            on_jumping_block = True
            jump_timer = pygame.time.get_ticks()

    if on_jumping_block:
        elapsed_time = pygame.time.get_ticks() - jump_timer
        if elapsed_time < 2000:  # 2초 동안 위로 날아가는 효과
            vertical_momentum = -5  # 위로 날아가는 속도를 천천히 설정
        else:
            reset_game()  # 2초 후에 게임을 리셋 (캐릭터가 죽는 효과)

    for block in blocks:
        if block.speed != 0:
            block.move()
            if block.is_visible and character_rect.colliderect(pygame.Rect(block.x, block.y, platform_width, platform_height)):
                reset_game()

    for block in blocks:
        if block.is_visible:
            pygame.draw.rect(screen, platform_color, (block.x - camera_x, block.y, platform_width, platform_height))
            text = font.render(f"({block.x}, {block.y})", True, RED)
            screen.blit(text, (block.x - camera_x, block.y - 20))

    # 가시 !
    if check_trigger_zone_collision(character_rect, spike_trigger_zone):
        spike_height = 110  # 높이 변경
        spike_positions = [(x, floor_y - spike_height) for x in range(550, 600, spike_width)]
    
    for spike in spike_positions:
        pygame.draw.rect(screen, SPIKE_COLOR, (spike[0] - camera_x, spike[1], spike_width, spike_height))

    # 트리거 영역 그리기
    pygame.draw.rect(screen, (0, 255, 0), trigger_falling_block_zone.move(-camera_x, 0), 2)
    pygame.draw.rect(screen, (0, 0, 0), del_block_1.move(-camera_x, 0), 2)
    pygame.draw.rect(screen, (0, 255, 0), add_block_1.move(-camera_x, 0), 2)
    pygame.draw.rect(screen, (0, 0, 255), trigger_moving_block_zone.move(-camera_x, 0), 2)
    pygame.draw.rect(screen, (0, 255, 0), trigger_zone.move(-camera_x, 0), 2)
    pygame.draw.rect(screen, (0, 0, 255), spike_trigger_zone.move(-camera_x, 0), 2)
    pygame.draw.rect(screen, (255, 0, 0), jumping_trigger_zone.move(-camera_x, 0), 2)  # 점핑 블럭 트리거 영역 그리기

    # 포탈 이미지 회전
    portal_angle += 2  # 회전 속도 
    rotated_portal_image = pygame.transform.rotate(portal_image, portal_angle)
    portal_rect = rotated_portal_image.get_rect(center=(portal_position[0] - camera_x + portal_size // 2, portal_position[1] + portal_size // 2))
    screen.blit(rotated_portal_image, portal_rect.topleft)

    # 포탈 충돌 감지 및 다음 맵 로드
    if check_portal_collision(character_rect, portal_position, portal_size):
        load_next_map()

    pygame.draw.rect(screen, RED, character_rect.move(-camera_x, 0))
    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
