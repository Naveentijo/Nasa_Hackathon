from settings import *

class Asteroid:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(50, WIDTH-50), -20, 30, 30)
        self.speed = random.randint(2, 5)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.y = -20
            self.rect.x = random.randint(50, WIDTH-50)

    def draw(self):
        pygame.draw.rect(screen, GRAY, self.rect)

class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 5, 10)

    def update(self):
        self.rect.y -= 10

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)
