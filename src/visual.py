import sys
from colorsys import hsv_to_rgb
from enum import Enum
from math import cos, pi, sin

import pygame

WIDTH = 600
HEIGHT = 600
PIXEL_RADIUS = 10
TOTAL_PIXELS = 50
CIRCLE_RADIUS = 200


class Pixel:
    x: int
    y: int
    color: tuple[int, int, int]

    def __init__(self, number: int):
        angle = 2 * pi / TOTAL_PIXELS * number
        self.x = CIRCLE_RADIUS * cos(angle) + WIDTH / 2
        self.y = -1 * CIRCLE_RADIUS * sin(angle) + HEIGHT / 2
        self.color = (255, 255, 255)

    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), PIXEL_RADIUS)


class AnimationType(Enum):
    SOLID = "solid"
    RAINBOW = "rainbow"


class Visual:
    pygame.init()

    clock: pygame.time.Clock
    display: pygame.Surface

    pixels: list[Pixel] = [Pixel(i) for i in range(TOTAL_PIXELS)]

    animation_type: AnimationType
    animation_colors: list[tuple[int, int, int]]
    animation_frames: int

    def animate_solid(self):
        for pixel in self.pixels:
            pixel.color = self.animation_colors[0]

    def animate_rainbow(self):
        K = 120
        move = (self.animation_frames % K) / K
        for i, pixel in enumerate(self.pixels):
            hue = i / TOTAL_PIXELS + move
            pixel.color = tuple(round(j * 255) for j in hsv_to_rgb(hue % 1, 1, 1))

    def run(self):
        self.clock = pygame.time.Clock()
        self.display = pygame.display.set_mode((WIDTH, HEIGHT))
        self.pixels = [Pixel(i) for i in range(TOTAL_PIXELS)]

        self.animation_type: AnimationType = AnimationType.RAINBOW
        self.animation_colors: list[tuple[int, int, int]] = [[255, 0, 0]]
        self.animation_frames: int = 0

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.display.fill((0, 0, 0))

            if self.animation_type == AnimationType.SOLID:
                self.animate_solid()
            elif self.animation_type == AnimationType.RAINBOW:
                self.animate_rainbow()

            for pixel in self.pixels:
                pixel.draw(self.display)

            pygame.display.update()
            self.clock.tick(60)
            self.animation_frames += 1
