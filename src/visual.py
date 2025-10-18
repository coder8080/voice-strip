from colorsys import hsv_to_rgb
from dataclasses import dataclass
from enum import Enum
from math import cos, floor, pi, sin
from queue import Queue
from typing import Optional

import pygame
from pydantic import TypeAdapter

WIDTH = 600
HEIGHT = 600
PIXEL_RADIUS = 10
TOTAL_PIXELS = 50
CIRCLE_RADIUS = 200


class Pixel:
    x: float
    y: float
    color: tuple[int, int, int]

    def __init__(self, number: int):
        angle = 2 * pi / TOTAL_PIXELS * number
        self.x = CIRCLE_RADIUS * cos(angle) + WIDTH / 2
        self.y = -CIRCLE_RADIUS * sin(angle) + HEIGHT / 2
        self.color = (255, 255, 255)

    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), PIXEL_RADIUS)


ColorAdapter = TypeAdapter(tuple[int, int, int])


class AnimationType(Enum):
    SOLID = "solid"
    RAINBOW = "rainbow"
    BREATH = "breath"
    LOOP = "loop"


@dataclass
class Command:
    type: AnimationType
    colors: list[tuple[int, int, int]]


class Visual:
    def __init__(self):
        pygame.init()
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.display: Optional[pygame.Surface] = None
        self.pixels: list[Pixel] = [Pixel(i) for i in range(TOTAL_PIXELS)]
        self.animation_type: AnimationType = AnimationType.LOOP
        self.animation_colors: list[tuple[int, int, int]] = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
        ]
        self.animation_frames: int = 0
        self.q: Queue[Command] = Queue()

    def animate_solid(self):
        for pixel in self.pixels:
            pixel.color = self.animation_colors[0]

    def animate_rainbow(self):
        K = 120
        move = (self.animation_frames % K) / K
        for i, pixel in enumerate(self.pixels):
            hue = i / TOTAL_PIXELS + move
            pixel.color = ColorAdapter.validate_python(
                tuple(round(j * 255) for j in hsv_to_rgb(hue % 1, 1, 1))
            )

    def animate_breath(self):
        N = 15
        V = (sin(self.animation_frames / N) + 1) / 2
        color = ColorAdapter.validate_python(
            tuple([floor(val * V) for val in self.animation_colors[0]])
        )
        for pixel in self.pixels:
            pixel.color = color

    def animate_loop(self):
        k = 60
        n = k * len(self.animation_colors)
        m = self.animation_frames % n
        i = m // k
        j = (i + 1) % len(self.animation_colors)
        v2 = m % k
        v1 = k - v2
        k1 = v1 / k
        k2 = v2 / k
        c1 = self.animation_colors[i]
        c2 = self.animation_colors[j]
        c = ColorAdapter.validate_python(
            tuple([floor(k1 * c1[x] + k2 * c2[x]) for x in range(3)])
        )
        for pixel in self.pixels:
            pixel.color = c

    def send_command(self, type: AnimationType, colors: list[tuple[int, int, int]]):
        self.q.put(Command(type=type, colors=colors))

    def run(self):
        self.clock = pygame.time.Clock()
        self.display = pygame.display.set_mode((WIDTH, HEIGHT))
        self.pixels = [Pixel(i) for i in range(TOTAL_PIXELS)]
        self.animation_type = AnimationType.LOOP
        self.animation_colors = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
        ]
        self.animation_frames = 0
        self.q = Queue()

        while True:
            stopped = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    stopped = True
                    break

            if stopped:
                break

            while not self.q.empty():
                cmd = self.q.get()
                self.animation_type = cmd.type
                self.animation_colors = cmd.colors

            self.display.fill((0, 0, 0))

            if self.animation_type == AnimationType.SOLID:
                self.animate_solid()
            elif self.animation_type == AnimationType.RAINBOW:
                self.animate_rainbow()
            elif self.animation_type == AnimationType.BREATH:
                self.animate_breath()
            elif self.animation_type == AnimationType.LOOP:
                self.animate_loop()

            for pixel in self.pixels:
                pixel.draw(self.display)

            pygame.display.update()
            self.clock.tick(60)
            self.animation_frames += 1


visual = Visual()
