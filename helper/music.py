import pygame.mixer


class Music:
    def __init__(self, file, loop):
        # Check if an instance exist, if existed, do not init pygame mixer again
        exist = False
        if not exist:
            pygame.mixer.init()

        self.file = file
        self.loop = loop

        self.mixer = pygame.mixer
        self.mixer.music.load(self.file)
        self.mixer.music.play(-1 if loop else 0)
        exist = True

    def stop(self):
        self.mixer.music.stop()

    def pause(self):
        self.mixer.music.pause()

    def resume(self):
        self.mixer.music.load(self.file)
        self.mixer.music.play(self.loop)

    def unload(self):
        self.mixer.music.stop()
        self.mixer.music.unload()

    def set_volume(self, volume):
        self.mixer.music.set_volume(max(0.0, min(volume, 1.0)))

    def volume_up(self):
        current_volume = self.mixer.music.get_volume()
        new_volume = min(current_volume + 0.1, 1.0)
        self.mixer.music.set_volume(new_volume)

    def volume_down(self):
        current_volume = self.mixer.music.get_volume()
        new_volume = max(current_volume - 0.1, 0.0)
        self.mixer.music.set_volume(new_volume)
