import pygame
import os

WIDTH = 800
HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Inicializar Pygame
pygame.init()
pygame.mixer.init()

# Configurar la pantalla de Pygame
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Shooter Game')
clock = pygame.time.Clock()

# Cargar la imagen de fondo
background = pygame.image.load('assets/background2.jpg').convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
# Cargar sonido de explosión
explosion_sound = pygame.mixer.Sound('assets\explosion_sound.wav')
explosion_sound.set_volume(0.15)

from models.nave import Nave
from models.meteor import Meteor
from models.bullet import Bullet
from models.collision import Collision

# Función para dibujar texto en pantalla
def draw_text(surface, text, size, x, y):
    font = pygame.font.Font(pygame.sysfont.match_font('serif'), size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

# Función para dibujar la barra de vida
def draw_life_bar(surface, x, y, percent_life):
    if percent_life < 0:
        percent_life = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (percent_life / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    
    if percent_life > 50:
        bar_color = (0, 255, 0)  
    else:
        bar_color = (255, 0, 0)  
    
    pygame.draw.rect(surface, bar_color, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)

    life_text = f"Life: {int(percent_life)}"
    draw_text(surface, life_text, 20, x - 70, y - 5)
    
# Función para añadir un nuevo meteoro
def add_meteor():
    meteor = Meteor()
    all_sprites.add(meteor)
    meteor_list.add(meteor)


life_interval = 5000

# Función para cargar el mejor puntaje
def load_high_score():
    if os.path.exists('high_score.txt'):
        with open('high_score.txt', 'r') as file:
            return int(file.read())
    return 0

# Función para guardar el mejor puntaje
def save_high_score(score):
    with open('high_score.txt', 'w') as file:
        file.write(str(score))

# Cargar el mejor puntaje
high_score = load_high_score()

# Función para manejar el menu del juego
def game_over_menu(score):
    screen.blit(background, (0, 0))
    draw_text(screen, "GAME OVER", 64, WIDTH // 2, HEIGHT // 4)
    draw_text(screen, f"Score: {score}", 44, WIDTH // 2, HEIGHT // 2)
    draw_text(screen, f"High Score: {high_score}", 35, WIDTH // 2, HEIGHT // 1.7)
    draw_text(screen, "Press R to Restart or Q to Quit", 22, WIDTH // 2, HEIGHT * 3 // 4)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    waiting = False
                    run_game() 
                elif event.key == pygame.K_q:
                    pygame.quit()
                    exit()
#Función para mostrar la pantalla de inicio
def show_start_screen():
    screen.blit(background, (0, 0))
    draw_text(screen, "SHOOTER GAME", 64, WIDTH // 2, HEIGHT // 4)
    draw_text(screen, "Press SPACE to Start", 22, WIDTH // 2, HEIGHT // 2)
    draw_text(screen, "Press P to Paused", 22, WIDTH // 2, HEIGHT // 1.8)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
# Función para pausar el juego
def pause_game():
    draw_text(screen, "PAUSED", 64, WIDTH // 2, HEIGHT // 4)
    draw_text(screen, "Press P to Resume", 22, WIDTH // 2, HEIGHT // 2)
    pygame.display.flip()

    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = False


# Función principal para ejecutar el juego
def run_game():
    global all_sprites, bullets, meteor_list, Collision_list, nave, score, high_score

    # Configuración inicial
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    meteor_list = pygame.sprite.Group()
    Collision_list = pygame.sprite.Group()
    for _ in range(8):
        add_meteor()

    nave = Nave()
    all_sprites.add(nave)

    score = 0
    pygame.mixer.music.load('assets\\game_sound.ogg')
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(loops=-1)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    nave.shoot(all_sprites, bullets)
                elif event.key == pygame.K_p:
                    pause_game()

        all_sprites.update()

        # Dibuja el fondo cubriendo toda la ventana
        screen.blit(background, (0, 0))

        # Colisiones y actualización de score
        hits = pygame.sprite.groupcollide(bullets, meteor_list, True, True)
        for hit in hits:
            score += 10
            explosion_sound.play()
            collision = Collision(hit.rect.center)
            all_sprites.add(collision)
            add_meteor()

        # Colisiones entre nave y meteoros
        hits = pygame.sprite.spritecollide(nave, meteor_list, True)
        for hit in hits:
            nave.life -= 10
            add_meteor()
            if nave.life <= 0:
                running = False

        if score > high_score:
            high_score = score

        # Dibujar sprites y demás elementos en pantalla
        all_sprites.draw(screen)

        draw_text(screen, f"Score: {score}", 20, 50, 10)
        draw_text(screen, f"High Score: {high_score}", 20, 80, 40)
        draw_life_bar(screen, WIDTH - 120, 10, nave.life)

        pygame.display.flip()
        clock.tick(60)

    # Guardar el mejor puntaje 
    if score > high_score:
        save_high_score(high_score)

    game_over_menu(score)

show_start_screen() 

run_game() 
