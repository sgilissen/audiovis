#
# NOTE: Make sure to modify music variable below.
# Script won't work otherwise.
#
import librosa
import pygame
import numpy as np

music = "mus.mp3"  # Modify this, or add a mus.mp3 file in the root directory of the script.


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
    pygame.display.set_caption('Audio spectrum test')

    info_obj = pygame.display.Info()
    screen_w = int(info_obj.current_w / 2.5)
    # screen = pygame.display.set_mode([info_obj.current_w, info_obj.current_h])
    # ^^^ Does not play nicely with multiple-monitor setups. :( Hardcoding to 1080p instead.
    screen = pygame.display.set_mode([1920, 1080])

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

    pg_window = True
    while pg_window:
        t = pygame.time.get_ticks()
        delta_time = (t - get_ticks_last_frame) / 1000.0
        get_ticks_last_frame = t

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pg_window = False

        screen.fill((0, 0, 0))

        for b in bars:
            b.update(delta_time, get_decibel(pygame.mixer.music.get_pos()/1000.0, b.freq))
            b.render(screen)

        pygame.display.flip()


pygame.quit()


if __name__ == "__main__":
    main()
