#
# NOTE: Make sure to modify music variable below.
# Script won't work otherwise.
#
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import librosa
import pygame
#from pygame.locals import *
import numpy as np

music = "mus.mp3"  # Modify this, or add a mus.mp3 file in the root directory of the script.
sync_thing = True

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

    def update(self, dt, decibel):
        desired_height = decibel * self.__decibel_height_ratio + self.max_height
        speed = (desired_height - self.height)/0.1
        self.height += speed * dt
        self.height = clamp(self.min_height, self.max_height, self.height)

    def render(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y + self.max_height - self.height, self.width, self.height))


def draw_grid():
    numcolumns = 50
    numrows = 50
    glLineWidth(4)
    glBegin(GL_LINES)

    for i in range(0, numrows, 1):
        glVertex3f(i, 0.0, 0.0)
        glVertex3f(i, numcolumns, 0.0)
        glVertex3f(0.0, i, 0.0)
        glVertex3f(100.0, i, 0.0)
    glEnd()


def draw_cover():
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glBegin(GL_LINES)
    glColor4f(1.0, 0.0, 0.0, 1.0)
    glVertex2f(4, 0.6)
    glVertex2f(-4, 0.6)
    glEnd()

    glBegin(GL_LINES)
    glColor4f(0.78, 0.96, 0.26, 1.0)
    glVertex2f(4, -0.6)
    glVertex2f(-4, -0.6)
    glEnd()

    glBegin(GL_QUADS)
    glColor4f(0.78, 0.96, 0.26, 1.0)
    # glColor4f(0.0, 0.0, 1.0, 1.0)
    glVertex2f(4, 0)
    glVertex2f(-4, 0)
    glColor4f(0.0, 0.0, 0.0, 0.0)
    glVertex2f(-4, -1.5)
    glVertex2f(4, -1.74)
    glEnd()

    glBegin(GL_QUADS)
    glColor4f(1.0, 0.0, 0.0, 1.0)
    glVertex2f(4, 0)
    glVertex2f(-4, 0)
    glColor4f(0.0, 0.0, 0.0, 0)
    glVertex2f(-4, 1.5)
    glVertex2f(4, 1.74)
    glEnd()

    glBegin(GL_QUADS)
    glColor4f(0.0, 0.0, 0.0, 1.0)
    glVertex2f(4, -0.6)
    glVertex2f(-4, -0.6)
    glColor4f(0.0, 0.0, 0.0, 1.0)
    glVertex2f(-4, 0.6)
    glVertex2f(4, 0.6)
    glEnd()


def draw_triangles(frequencies):
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glBegin(GL_TRIANGLE_STRIP)
    glNormal3f(0, 0, 1)

    for i in np.arange(0.0, 2.0, 0.5):
        for j in np.arange(-1.0, 1.0, 0.05):
            glVertex3f(j, 1-i+0.05, 0)
            glVertex3f(j, 1-i, 0)

    glEnd()


def main():
    time_series, sample_rate = librosa.load(music)
    stft = np.abs(librosa.stft(time_series, hop_length=512, n_fft=2048*4))
    spectro = librosa.amplitude_to_db(stft, ref=np.max)
    freqs = librosa.core.fft_frequencies(n_fft=2048*4)

    times = librosa.core.frames_to_time(np.arange(spectro.shape[1]), sr=sample_rate, hop_length=512, n_fft=2048*4)
    time_index_ratio = len(times) / times[len(times) - 1]
    freq_index_ratio = len(freqs) / freqs[len(freqs) - 1]

    field_scroll = -20

    view_rotate = 0

    def get_decibel(target_time, freq):
        return spectro[int(freq * freq_index_ratio)][int(target_time * time_index_ratio)]

    pygame.init()
    pygame.display.set_caption('Audio spectrum test')

    info_obj = pygame.display.Info()
    screen_w = int(info_obj.current_w / 2.5)
    # screen = pygame.display.set_mode([info_obj.current_w, info_obj.current_h])
    # ^^^ Does not play nicely with multiple-monitor setups. :( Hardcoding to 1080p instead.
    display = (1920, 1080)
    screen = pygame.display.set_mode(display, GL_DOUBLEBUFFER)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)
    glEnable(GL_TEXTURE_2D)


    bars = []
    freqs = np.arange(100, 8000, 100)
    r = len(freqs)
    width = screen_w / r

    x = (screen_w - width * r) / 2
    for c in freqs:
        bars.append(FreqBar(x, 300, c, (32, 105, 224), max_height=500, width=int(width)))
        x += width

    t = pygame.time.get_ticks()
    get_ticks_last_frame = t
    pygame.mixer.music.load("mus.mp3")
    pygame.mixer.music.play(0)

    x_pos = 80
    y_pos = 0

    pg_window = True
    while pg_window:
        t = pygame.time.get_ticks()
        delta_time = (t - get_ticks_last_frame) / 1000.0
        get_ticks_last_frame = t

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pg_window = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                elif event.key == pygame.K_SPACE:
                    if sync_thing:
                        print(f"SyncThing: Track pos.: {pygame.mixer.music.get_pos()}")
                elif event.key == pygame.K_DOWN:
                    y_pos -= 0.1
                    print(f"Y: {y_pos}")
                elif event.key == pygame.K_UP:
                    y_pos += 0.1
                    print(f"Y: {y_pos}")
                elif event.key == pygame.K_LEFT:
                    x_pos -= 0.1
                    print(f"X: {x_pos}")
                elif event.key == pygame.K_RIGHT:
                    x_pos += 0.1
                    print(f"X: {x_pos}")

        #screen.fill((0, 0, 0))

        #for b in bars:
        #    b.update(delta_time, get_decibel(pygame.mixer.music.get_pos()/1000.0, b.freq))
        #    b.render(screen)
        #    print(f"Delta time: {delta_time} - dB: {get_decibel(pygame.mixer.music.get_pos()/1000.0, b.freq)}")

        # --------------------------------------
        # Scroll stuff
        # --------------------------------------
        if field_scroll >= -10:
            field_scroll = -20
        else:
            field_scroll += delta_time * 6

        # print(f"Freq: {(get_decibel(pygame.mixer.music.get_pos()/1000.0, bars[5].freq) * -1) / 100000}")
        # print(f"DeltaTime: {delta_time}")
        # print(f"POS: {pygame.mixer.music.get_pos()}")
        frequencies = {}
        #for i, b in bars:
        #    frequencies[i] = b.freq

        # print(frequencies)
        col_freq = (get_decibel(pygame.mixer.music.get_pos() / 1000.0, bars[5].freq) * -1) / 100
        # print(col_freq)

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        # --------------------------------------
        # Floor stuff
        # --------------------------------------
        glPushMatrix()
        glColor4f(0.78, 0.96, 0.26, 1.0)
        glRotate(100, 200, 0, 0)
        glTranslatef(-20, field_scroll, 3.6)
        draw_grid()
        glPopMatrix()

        glPushMatrix()
        glColor3f(0.87, 0.0, 0.0)
        glRotate(80, 200, 0, 0)
        glTranslatef(-20, field_scroll, -3.6)
        draw_grid()
        glPopMatrix()

        glPushMatrix()
        draw_cover()
        glPopMatrix()

        glPushMatrix()
        # draw_triangles(0)
        glPopMatrix()

        pygame.display.flip()


pygame.quit()


if __name__ == "__main__":
    main()
