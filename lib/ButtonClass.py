import os

import pygame


class ButtonPy:
    """Create a button, then blit the surface in the while loop"""

    def __init__(self, x, y, states):
        self.rect = None
        self.size = None
        self.surface = None
        self.x = x
        self.y = y
        self.states = states
        self.state = self.states[0]
        self.update_button()

    def change_state(self):
        self.states.append(self.states.pop(0))
        self.state = self.states[0]
        self.update_button()

    def update_button(self):
        imgpath = os.path.join(os.path.dirname(__file__), '..', 'img', self.state + '.png')
        self.surface = pygame.image.load(imgpath)
        self.size = self.surface.get_size()
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])
