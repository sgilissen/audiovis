import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

import random

import librosa
import pygame
import numpy as np

music = "mus.mp3"  # Modify this, or add a mus.mp3 file in the root directory of the script.

vertices = (
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1)
)

edges = (
    (0, 1),
    (0, 3),
    (0, 4),
    (2, 1),
    (2, 3),
    (2, 7),
    (6, 3),
    (6, 4),
    (6, 7),
    (5, 1),
    (5, 4),
    (5, 7)
)

surfaces = (
    (0, 1, 2, 3),
    (3, 2, 7, 6),
    (6, 7, 5, 4),
    (4, 5, 1, 0),
    (1, 5, 7, 2),
    (4, 0, 3, 6)
)

colors = (
    (1, 0, 0),
    (0, 1, 0),
    (0, 0, 1),
    (0, 1, 0),
    (1, 1, 1),
    (0, 1, 1),
    (1, 0, 0),
    (0, 1, 0),
    (0, 0, 1),
    (1, 0, 0),
    (1, 1, 1),
    (0, 1, 1),
)


def clamp(min_value, max_value, value):
    if value < min_value:
        return min_value

    if value > max_value:
        return max_value

    return value

class FreqBar:
    def __init__(self, x, y, freq, color, width=50, min_height=10, max_height=100, min_decibel=-80, max_decibel=0):
        self.x, self.y, self.freq = x, y, freq
        self.color = color
        self.width, self.min_height, self.max_height = width, min_height, max_height
        self.height = min_height
        self.min_decibel, self.max_decibel = min_decibel, max_decibel
        self.__decibel_height_ratio = (self.max_height - self.min_height)/(self.max_decibel - self.min_decibel)

    # b.update(delta_time, get_decibel(pygame.mixer.music.get_pos() / 1000.0, b.freq))
    def update(self, dt, decibel):
        desired_height = decibel * self.__decibel_height_ratio + self.max_height
        speed = (desired_height - self.height)/0.1
        self.height += speed * dt
        self.height = clamp(self.min_height, self.max_height, self.height)

    def render(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y + self.max_height - self.height, self.width, self.height))



def set_vertices(x, y, z):
    x_value_change = x  # random.randrange(-10, 10)
    y_value_change = y  #
    z_value_change = z  # random.randrange(-10, 10)
    # x_value_change = x
    # y_value_change = y
    # z_value_change = -20

    new_vertices = []

    for vert in vertices:
        new_vert = []

        new_x = vert[0] + x_value_change
        new_y = vert[1] + y_value_change
        new_z = vert[2] + z_value_change

        new_vert.append(new_x)
        new_vert.append(new_y)
        new_vert.append(new_z)

        new_vertices.append(new_vert)

    return new_vertices


def cube(vertices):
    glBegin(GL_QUADS)

    for surface in surfaces:
        x = 0

        for vertex in surface:
            x += 1
            glColor3fv(colors[x])
            glVertex3fv(vertices[vertex])

    glEnd()

    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()


def main():
    time_series, sample_rate = librosa.load(music)
    stft = np.abs(librosa.stft(time_series, hop_length=512, n_fft=2048*4))
    spectro = librosa.amplitude_to_db(stft, ref=np.max)
    freqs = librosa.core.fft_frequencies(n_fft=2048*4)

    times = librosa.core.frames_to_time(np.arange(spectro.shape[1]), sr=sample_rate, hop_length=512, n_fft=2048*4)
    time_index_ratio = len(times) / times[len(times) - 1]
    freq_index_ratio = len(freqs) / freqs[len(freqs) - 1]


    def get_decibel(target_time, freq):
        return spectro[int(freq * freq_index_ratio)][int(target_time * time_index_ratio)]

    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    gluPerspective(75, (display[0] / display[1]), 0.1, 50.0)

    glTranslatef(random.randrange(-5, 5), random.randrange(-5, 5), -40)
    glRotatef(10, 0, 0, 60)
    glRotatef(10, 60, 0, 0)

    bars = []
    freqs = np.arange(100, 8000, 100)
    r = len(freqs)

    width = display[1] / r

    x = (display[1] - width * r) / 2

    for c in freqs:
        bars.append(FreqBar(x, 300, c, (32, 105, 224), max_height=500, width=int(width)))
        x += width

    pygame.mixer.music.load("mus.mp3")
    pygame.mixer.music.play(0)

    x_move = 0
    y_move = 0

    cube_matrix_x, cube_matrix_y = np.meshgrid([range(8)], range(8), indexing='ij')
    cube_matrix = np.array((cube_matrix_x, cube_matrix_y)).T

    cube_dict = {}




    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x_move = 0.3
                if event.key == pygame.K_RIGHT:
                    x_move = -0.3

                if event.key == pygame.K_UP:
                    y_move = -0.3
                if event.key == pygame.K_DOWN:
                    y_move = 0.3

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    x_move = 0

                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    y_move = 0



        t = pygame.time.get_ticks()
        get_ticks_last_frame = t
        delta_time = (t - get_ticks_last_frame) / 1000.0

        glRotatef(1, x_move, y_move, 0)

        for b in bars:
            b.update(delta_time, get_decibel(pygame.mixer.music.get_pos() / 1000.0, b.freq))

        num_cube = 1
        for row in range(len(cube_matrix)):
            for col in cube_matrix[row]:
                cube_freq = get_decibel(pygame.mixer.music.get_pos() / 1000.0, bars[row].freq)
                cube_dict[num_cube] = set_vertices(col[0] * 3, col[1] * 3, -cube_freq/8)
                num_cube += 1

        x = glGetDoublev(GL_MODELVIEW_MATRIX)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for each_cube in cube_dict:
            cube(cube_dict[each_cube])

        pygame.display.flip()
        pygame.time.wait(10)


main()
pygame.quit()
quit()