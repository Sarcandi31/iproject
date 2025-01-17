import pygame as pg, asyncio, sys
from os.path import join, dirname, abspath
from PIL import Image

pg.init()

# Настройки игры
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 400
FPS = 60
GRAVITY = 0.5
SPEED = 5

# Цвета
BACKGROUND_COLOR = (120, 255, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Инициализация экрана и шрифта
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("Dino Game")
font = pg.font.Font(None, 36)

# Загрузка спрайтов
dino_surf = pg.Surface((50, 50))
dino_surf.fill((100, 200, 100))  # Зеленый квадрат вместо спрайта динозавра


# Функция для получения полного пути к файлу
def get_file_path(file_name: str) -> str:
    return join(dirname(abspath(__file__)), file_name)


# Загрузка изображения кактуса
cactus_image = pg.image.load(
    get_file_path("img/buk.png")
).convert_alpha()
cactus_surf = pg.transform.scale(cactus_image, (40, 40))
cactus_surf.set_colorkey(WHITE)


def load_gif_frames(file_path: str) -> list[pg.Surface]:
    image = Image.open(file_path)
    frames = []
    try:
        while True:
            frame = image.copy()
            frame = frame.convert("RGBA")
            pg_image = pg.image.frombuffer(frame.tobytes(), frame.size, "RGBA")
            frames.append(pg.transform.scale(pg_image, (100, 100)))
            image.seek(len(frames))  # Move to the next frame
    except EOFError:
        pass
    return frames


class Player:
    def __init__(self):
        self.frames = load_gif_frames(get_file_path("img/croco.gif"))
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(midbottom=(100, SCREEN_HEIGHT - 20))
        self.velocity = 0
        self.on_ground = True
        self.tick_count = 0
        self.mask = pg.mask.from_surface(self.image)  # Создаем маску

    def jump(self):
        if self.on_ground:
            self.velocity = -12
            self.on_ground = False

    def apply_gravity(self):
        self.velocity += GRAVITY
        self.rect.y += int(self.velocity)
        if self.rect.bottom >= SCREEN_HEIGHT - 20:
            self.rect.bottom = SCREEN_HEIGHT - 20
            self.velocity = 0
            self.on_ground = True

    def update(self):
        self.tick_count += 1
        if self.tick_count >= 30:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.tick_count = 0
            self.mask = pg.mask.from_surface(self.image)  # Обновляем маску

    def draw(self):
        if not self.on_ground:
            rotated_image = pg.transform.rotate(self.image, 20)
            rotated_rect = rotated_image.get_rect(center=self.rect.center)
            screen.blit(rotated_image, rotated_rect.topleft)
        else:
            screen.blit(self.image, self.rect)


class Cactus:
    def __init__(self, x):
        self.image = cactus_surf
        self.rect = self.image.get_rect(midbottom=(x, SCREEN_HEIGHT - 20))
        self.mask = pg.mask.from_surface(self.image)  # Создаем маску

    def move(self):
        self.rect.x -= SPEED
        if self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH

    def draw(self):
        screen.blit(self.image, self.rect)


async def main():
    clock = pg.time.Clock()
    player = Player()
    cacti = [Cactus(SCREEN_WIDTH + i * 300) for i in range(3)]
    score = 0

    waiting_for_start = True
    while waiting_for_start:
        screen.fill(BACKGROUND_COLOR)
        start_text = font.render("Press SPACE to start", True, BLACK)
        screen.blit(
            start_text,
            (
                SCREEN_WIDTH // 2 - start_text.get_width() // 2,
                SCREEN_HEIGHT // 2 - start_text.get_height() // 2,
            ),
        )
        pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                waiting_for_start = False
        await asyncio.sleep(0)

    running = True
    game_over = False
    while running:
        screen.fill(BACKGROUND_COLOR)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                if game_over:
                    game_over = False
                    player = Player()
                    cacti = [Cactus(SCREEN_WIDTH + i * 300) for i in range(3)]
                    score = 0

        keys = pg.key.get_pressed()
        if keys[pg.K_SPACE] and not game_over:
            player.jump()

        if not game_over:
            player.apply_gravity()
            player.update()
            for cactus in cacti:
                cactus.move()

            # Проверка столкновений с использованием масок
            for cactus in cacti:
                offset = (
                    cactus.rect.x - player.rect.x,
                    cactus.rect.y - player.rect.y,
                )
                if player.mask.overlap(cactus.mask, offset):
                    game_over = True

            score += 1

        player.draw()
        for cactus in cacti:
            cactus.draw()

        score_text = font.render(f"Score: {score // 10}", True, BLACK)
        screen.blit(score_text, (10, 10))
        if game_over:
            game_over_text = font.render("Вы проиграли", True, BLACK)
            screen.blit(
                game_over_text,
                (
                    SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                    SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2,
                ),
            )

        pg.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())
