import pygame.mixer

class Music:
    def __init__(self, file, loop):
        pygame.mixer.init()
        self.mixer = pygame.mixer
        self.mixer.music.load(file)
        self.mixer.music.play(-1 if loop else 0)

    def stop(self):
        self.mixer.music.stop()

    def pause(self):
        self.mixer.music.pause()

    def resume(self):
        self.mixer.music.unpause()

    def unload(self):
        self.mixer.music.stop()
        self.mixer.music.unload()

    def volume_up(self):
        current_volume = self.mixer.music.get_volume()
        new_volume = min(current_volume + 0.1, 1.0)
        self.mixer.music.set_volume(new_volume)

    def volume_down(self):
        current_volume = self.mixer.music.get_volume()
        new_volume = max(current_volume - 0.1, 0.0)
        self.mixer.music.set_volume(new_volume)