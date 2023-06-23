import pygame
import sys
from time import sleep
from gfx import blit_alpha
from sprite import Sprite


class Menu(object):
    _entries = {
        0:"",
        1:"",
        2:""
    }

    def paint(self):
        rect2 = pygame.Rect(self._window_size[0]/2 - 190, self._window_size[1]/2 - 110, 400, 200)
        pygame.draw.rect(self._screen, (0,150,150), rect2, 0)
        rect = pygame.Rect(self._window_size[0]/2 - 200, self._window_size[1]/2 - 100, 400, 200)
        pygame.draw.rect(self._screen, (150,150,150), rect, 0)
        for key,item in self._entries_sprite_dict.items():
            item.draw(self._screen)
        self._arrow_image_left.draw(self._screen)
        self._arrow_image_right.draw(self._screen)

        pygame.display.update()

    def __init__(self, screen, window_size, title, background, option, **kwargs):
        self._screen = screen
        self._title = title
        self._background = background
        self._entries_sprite_dict = {}
        self._window_size = window_size
        self._arrow_positions = {}
        self._arrow_image_left = Sprite("./media/menu_arrow.png")
        self._arrow_image_right = Sprite(pygame.transform.rotate(self._arrow_image_left.get_image(), 180))
        self._arrow_image_size = self._arrow_image_left.get_size()
        self._option = option

        self.__add_text = (kwargs["add_text"],None)
        entry_size_y = 20
        start_y = window_size[1]/2 - len(self._entries) * (entry_size_y/2)
        i = 0
        item_nr = 0

        for key, item in self._entries.items():
            if not item == " ":
                sprite = Sprite.from_text(item)
                size=sprite.get_size()
                sprite.move_to(window_size[0]/2 - size[0]/2, start_y + i * entry_size_y)
                self._entries_sprite_dict.update({item_nr:sprite})
                self._arrow_positions.update({item_nr:[pygame.Rect(sprite.get_pos()[0] - 110, sprite.get_pos()[1] +
                                                                  size[1]/2 - 6, 104, 12),
                                                       pygame.Rect(sprite.get_pos()[0] + size[0] + 6, sprite.get_pos()[1] +
                                                                   size[1]/2 - 6, 104, 12)]})
                self._arrow_image_left.set_rect(self._arrow_positions[0][0])
                self._arrow_image_right.set_rect(self._arrow_positions[0][1])
                item_nr += 1
            i += 1

    def show(self):
        option = self._option
        max_option = max(self._entries.keys())

        exit = False

        self._arrow_image_left.set_rect(self._arrow_positions[option][0])
        self._arrow_image_right.set_rect(self._arrow_positions[option][1])

        while not exit:

            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()

                if event.type is pygame.KEYDOWN:
                    key = pygame.key.name(event.key)

                    if key == "down":
                        if not option == max_option - 1:
                            option += 1
                        else:
                            option = 0

                    if key == "up":
                        if not option == 0:
                            option -= 1
                        else:
                            option = max_option -1

                    self._arrow_image_left.set_rect(self._arrow_positions[option][0])
                    self._arrow_image_right.set_rect(self._arrow_positions[option][1])

                    if key == "escape":
                        option = -1
                        exit = True

                    if key == "return":
                        exit = True
            self.paint()

        return option

class Ingame_menu(Menu):
    _entries={
        0:"Settings",
        1:"Return to game",
        2:" ",
        3:"Exit game"
    }

    def __init__(self, screen, size, title, background, **kwargs):
        Menu.__init__(self,screen, size, title, background, option = 1, **kwargs)

