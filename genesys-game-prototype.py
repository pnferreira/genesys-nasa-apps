import pygame
import random
import math

# Inicialização
pygame.init()

# Cores
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
RED = (255, 0, 0)

# Dimensões
WIDTH, HEIGHT = 800, 600

# Adicione isso no começo para definir as fontes
pygame.font.init()
font = pygame.font.SysFont(None, 36)

# Janela
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GeneSys")

class Snake:
    def __init__(self):
        self.segments = [(WIDTH // 2, HEIGHT // 2)]
        self.angle = random.uniform(0, 2*math.pi)
        self.speed = 5
        self.length = 30
        self.angle_variation = 0.1
        self.sin_wave = 0
        self.sin_frequency = 0.1
        self.sin_amplitude = 0.5
        self.health = 100
        self.max_speed = 5
        self.radioactivity = 5 # Define quão rápido a saúde diminui por frame
        self.original_radioactivity = 5

    def adjust_radioactivity(self, value):
        self.radioactivity += value
        # Garante que a radioatividade nunca seja negativa e não exceda o valor original
        self.radioactivity = max(0, min(self.original_radioactivity, self.radioactivity))

    def reset_radioactivity(self):
        # Aumenta gradualmente a radioatividade em direção ao valor original
        if self.radioactivity < self.original_radioactivity:
            self.adjust_radioactivity(0.02)


    def update_health(self):
        self.health -= self.radioactivity*0.01
        self.health = max(0, self.health)  # Saúde nunca fica abaixo de 0
        self.speed = self.max_speed * (self.health / 100.0)  # Ajusta a velocidade com base na saúde


    def move_towards(self, target):
        dx = target[0] - self.segments[0][0]
        dy = target[1] - self.segments[0][1]
        target_angle = math.atan2(dy, dx)
        angle_diff = (target_angle - self.angle) % (2*math.pi)
        if angle_diff > math.pi:
            angle_diff -= 2*math.pi
        
        if abs(angle_diff) < self.angle_variation:
            self.angle = target_angle
        elif angle_diff > 0:
            self.angle += self.angle_variation
        else:
            self.angle -= self.angle_variation
        
        self.angle += 0.3 * self.sin_amplitude * math.sin(self.sin_wave)
        self.sin_wave += self.sin_frequency


    def update(self):
        dx = self.speed * math.cos(self.angle)
        dy = self.speed * math.sin(self.angle)
        new_segment = (self.segments[0][0] + dx, self.segments[0][1] + dy)
        self.segments.insert(0, new_segment)
        while len(self.segments) > self.length:
            self.segments.pop()

    def draw(self, screen):
        for segment in self.segments:
            pygame.draw.circle(screen, GREEN, (int(segment[0]), int(segment[1])), 7)  # Raio ajustado para 7

class Food:
    def __init__(self):
        self.position = [random.randint(0, WIDTH), random.randint(0, HEIGHT)]

    def draw(self, screen):
        pygame.draw.circle(screen, RED, (int(self.position[0]), int(self.position[1])), 8)

    def randomize_position(self):
        self.position = [random.randint(0, WIDTH), random.randint(0, HEIGHT)]

class Machine:
    def __init__(self, x, y):
        self.position = [x, y]
        self.effect_radius = 100

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 255), (self.position[0] - 10, self.position[1] - 10, 20, 20))
        pygame.draw.circle(screen, (173, 216, 230, 80), self.position, self.effect_radius, 2)

class SpecialFood:
    def __init__(self, x, y):
        self.position = [x, y]

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 165, 0), self.position, 10)

    def eaten_by(self, snake):
        distance_to_snake = math.sqrt((self.position[0] - snake.segments[0][0])**2 + (self.position[1] - snake.segments[0][1])**2)
        return distance_to_snake < 20



snake = Snake()
food = Food()
machines = []
special_foods = []

running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Permitindo ao usuário colocar máquinas e comidas especiais
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Botão esquerdo do mouse
                machines.append(Machine(event.pos[0], event.pos[1]))
            elif event.button == 3:  # Botão direito do mouse
                special_foods.append(SpecialFood(event.pos[0], event.pos[1]))


    if special_foods:
        closest_special_food = min(special_foods, key=lambda x: math.sqrt((x.position[0] - snake.segments[0][0])**2 + (x.position[1] - snake.segments[0][1])**2))
        snake.move_towards(closest_special_food.position)
    else:
        snake.move_towards(food.position)
    snake.update()

    distance_to_food = math.sqrt((food.position[0] - snake.segments[0][0]) ** 2 + (food.position[1] - snake.segments[0][1]) ** 2)
    if distance_to_food < 15:  # Ajustado para 15
        food.randomize_position()

    snake.draw(screen)
    food.draw(screen)

    snake.update_health()

    # Renderizar a saúde na tela
    health_surface = font.render(f'Health: {int(snake.health)}', True, (0, 0, 0))
    screen.blit(health_surface, (10, 10))

    # Renderizar o nível de radioatividade na tela
    radio_surface = font.render(f'Radioactivity: {snake.radioactivity:.2f}', True, (0, 0, 0))
    screen.blit(radio_surface, (10, 50))

    near_machine = False  # Esta flag verifica se a cobra está perto de alguma máquina

    for machine in machines:
        machine.draw(screen)
        distance_to_machine = math.sqrt((machine.position[0] - snake.segments[0][0])**2 + (machine.position[1] - snake.segments[0][1])**2)
        if distance_to_machine < machine.effect_radius:
            near_machine = True
            snake.health += 0.03  # Recupera um pouco de saúde
            snake.adjust_radioactivity(-0.01)  # Diminui a radioatividade de maneira mais gradual

    if not near_machine:
        snake.reset_radioactivity()  # Aumenta gradualmente a radioatividade até o valor original

    for special_food in special_foods:
        special_food.draw(screen)
        if special_food.eaten_by(snake):
            snake.health += 20  # Aumenta a saúde da cobra
            special_foods.remove(special_food)  # Remove a comida especial


    # Verificar se a cobrinha morreu
    if snake.health <= 0:
        running = False
        death_surface = font.render('C. Elegans Died!', True, (255, 0, 0))
        screen.blit(death_surface, (WIDTH // 2 - 100, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(2000)  # Espera 2 segundos antes de fechar


    pygame.display.flip()

    pygame.time.Clock().tick(60)