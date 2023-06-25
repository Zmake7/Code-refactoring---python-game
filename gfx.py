########################################################################################################################
# Destroyer - a small boat shooter game.                                                                               #
# Copyright (C) 2018 by Hendrik Braun                                                                                  #
#                                                                                                                      #
# This program is free software: you can redistribute it and/or modify it under the terms of the                       #
# GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or         #
# (at your option) any later version.                                                                                  #
#                                                                                                                      #
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied   #
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more        #
# details.                                                                                                             #
#                                                                                                                      #
# You should have received a copy of the GNU General Public License along with this program.                           #
# If not, see <http://www.gnu.org/licenses/>.                                                                          #
########################################################################################################################


import pygame
import datetime

# 指定不透明度后，将对象传送到窗口。参数（窗口，图像对象，图像矩形区域，不透明度）
def blit_alpha(screen, image, rect, opacity):

    """
    Function for blit:ing objects with specified opacity onto the game window

    :returns
    """

    x = rect[0]
    y = rect[1]
    temp = pygame.Surface((image.get_width(), image.get_height())).convert() # 与图像大小相同的临时表面
    temp.blit(screen, (-x, -y)) # 窗口放在临时表面上
    temp.blit(image, (0, 0)) # 图像对象放在临时表面上
    temp.set_alpha(opacity)
    screen.blit(temp, rect) # 将临时表面会知道窗口指定区域

# 淡入淡出效果
class Fade_fx(object):
    def __init__(self, image, rect, time):

        """
        Class for fade effects. Those are for example boats that have been shot, so they don't just disappear but
        rather fade out.

        :param image : image to be faded
        :param rect  : position rectangle of the image
        :param time  : fade time in seconds
        :type image  : pygame.Image
        :type rect   : pygame.Rect
        :type time   : int

        :returns:
        """

        self._image = image
        self._rect = rect
        self._time = time
        self._steps = 255/self._time
        self._old_time = datetime.datetime.now()
        self._total_time = 0
        self._alpha = 255

    def fade(self, time_delta):
        if self._alpha < 0:
            return -1
        else:
            self._total_time += time_delta
            self._alpha = 255 - self._steps * self._total_time
        return 0

    def get_image(self):
        return self._image, self._rect

    def get_alpha(self):
        return self._alpha


#管理淡入淡出效果
class Fades(object):
    def __init__(self, timer):

        """
        Class for managing all the fades in the game window
        """

        self.__fade_list = []
        self.__timer = timer

    def add_fade(self, image, rect, time):
        self.__fade_list.append(Fade_fx(image, rect, time))

    def fade(self):
        new_fades = []
        for i,v in enumerate(self.__fade_list):
            if not v.fade(self.__timer.get_delta()) == -1:
                new_fades.append(v)
        self.__fade_list = new_fades

    def get_fades(self):
        return self.__fade_list


class Text_fx(object):
    def __init__(self, origin, text, time, movement, font_size=16, positive=True):

        """
        Class for text effects. Those are for example the point texts shown when an enemy is destroyed. The text is
        moved and faded at the same time, giving it a smooth appearance.

        origin (list of int)  : origin of the text. This will be the bottom center position of the text rectangle
        text (string)         : text to be displayed
        time (int)            : time until complete fade and movement in ms
        movement (int)        : text movement range towards north in pixels
        positive (bool)       : if positive, text is black, otherwise red
        """

        self._text = text
        self._time = time
        self._movement = movement

        self._alpha_steps = 255.0/self._time
        self._steps = self._movement/float(self._time)
        self._origin = origin
        self._time_delta = 0
        self._alpha = 255
        self._color = (0,0,0)
        self._rect = None
        self._font_size = font_size

        if not positive:
            self._color = (190,28,28)

        myfont = pygame.font.SysFont('Arial', self._font_size)
        self._image = myfont.render(self._text, True, self._color)
        rect = self._image.get_rect()
        self._size_x, self._size_y = rect[2], rect[3]
        self._position = (self._origin[0] - (self._size_x/2), self._origin[1] - (self._size_y/2))
        self._rect = (self._position[0], self._position[1], self._size_x, self._size_y)

    def move(self, time_delta):
        if self._alpha < 0:
            return -1
        else:
            self._time_delta += time_delta * 1000
            self._alpha = 255 - self._alpha_steps * self._time_delta
            self._position = (self._position[0], round(self._origin[1] - self._steps * self._time_delta, 0))
            self._rect = pygame.Rect(self._position[0], self._position[1], self._size_x, self._size_y)
        return 0

    def get_image(self):
        return self._image, self._rect

    def get_alpha(self):
        return self._alpha


class Texts(object):

    """
    Class holding all text effect objects in the game
    """

    def __init__(self, timer):
        self.__text_list = []
        self.__timer = timer

    def add_text(self, origin, text, positive=True, font_size=16):
        self.__text_list.append(Text_fx(origin, text, 1000, 80, font_size=font_size, positive=positive))

    def move(self):
        new_texts = []
        for i,v in enumerate(self.__text_list):
            if not v.move(self.__timer.get_delta()) == -1:
                new_texts.append(v)
        self.__text_list = new_texts

    def get_texts(self):
        return self.__text_list


class Explosion(object):
    def __init__(self, origin, pause):

        """
        Explosion animation class. Shows the sequence of explosion images at specified intervals to create the
        illusion of an awesome explosion
        origin (list of int)  : origin as x,y. Usually the impact point of the bullet Lower center of the image
                                rectangle
        pause (int)           : pause between the images in ms

        TODO
        """

        self.__frame = 1
        self.__image = pygame.image.load("./media/explosion/frame_1.png")
        self.__old_time = datetime.datetime.now()
        self.__rect = pygame.Rect(origin[0]-63, origin[1]-132, 62, 132)
        self.__pause = pause
        self.__total_time_delta = 0

    def next_frame(self, timer):

        """
        Method to walk through the frames and change image if the specified pause time has elapsed. If the explosion
        sequence is finished, it returns True, otherwise False.
        """

        self.__total_time_delta += timer.get_delta()
        if self.__frame > 17:
            return True
        if self.__total_time_delta*1000 >= self.__pause:
            self.__image = pygame.image.load("./media/explosion/frame_{}.png".format(self.__frame))
            self.__total_time_delta = 0
            self.__frame += 1
        return False

    def get_image(self):
        return self.__image, self.__rect


class Explosions(object):

    """
    Class holding all instances of explosion objects in the game.
    """

    def __init__(self, timer):
        self.__explosion_list = []
        self.__timer = timer

    def add_explosion(self, explosion):
        self.__explosion_list.append(explosion)

    def change_frames(self):
        new_list = []
        for e in self.__explosion_list:
            if not e.next_frame(self.__timer):
                new_list.append(e)
        self.__explosion_list = new_list

    def get_explosions(self):
        return self.__explosion_list


class Destroyer_gfx(object):

    def __init__(self, screen, destroyer, enemies, bullets, torpedos, explosions, fades, texts, points, crates,
                 game_level, font_size, bg_image):

        """
        Main graphics class. This is where all the elements are drawn.

        window_size (list of int) : window size in px as x,y
        destroyer (Destroyer)     : Destroyer class game instance
        enemies (Enemies)         : Enemies class game instance
        bullets (Bullets)         : Bullets class game instance
        torpedos (Torpedos)       : Torpedos class game instance
        explosions (Explosions)   : Explosions class game instance
        fades (Fades)             : Fades class game instance
        texts (Texts)             : Texts class game instance
        points (Points)           : Points class game instance
        crates (Creates)          : Crates class game instance
        font_size (int)           : HUD font size
        bg_image (string)         : path to the background image

        TODO
        """

        self.__destroyer = destroyer
        self.__enemies = enemies
        self.__bullets = bullets
        self.__torpedos = torpedos
        self.__fades = fades
        self.__screen = screen
        self.__background_path = bg_image
        self.__window_size = self.__screen.get_size()
        self.__explosions = explosions
        self.__points = points
        self.__texts = texts
        self.__font_size = font_size
        self.__crates = crates
        self.__game_level = game_level
        self.make_background()

    def __render_hud(self):

        """
        Method for rendering the HUD, showing information on the player HP, points and level.
        :return:
        """

        myfont = pygame.font.SysFont('Arial', self.__font_size)
        rect = pygame.Rect(0,0,self.__window_size[0],self.__font_size)
        pygame.draw.rect(self.__screen, (150,150,150), rect, 0)

        points = myfont.render('Points: {}'.format(self.__points.get_points()), True, (255, 255, 255))
        self.__screen.blit(points, (0,0))

        hp_ratio = self.__destroyer.get_hp() / float(self.__destroyer.get_max_hp())
        hp = myfont.render('HP: {}'.format(self.__destroyer.get_hp()), True, (255, 255*hp_ratio,255*hp_ratio))
        self.__screen.blit(hp, (100,0))

        max_hp = myfont.render("Max HP:{}".format(self.__destroyer.get_max_hp()), True, (255,255,255))
        self.__screen.blit(max_hp, (200,0))

        level = myfont.render("Level: {}".format(self.__game_level.get_level() +1), True, (255,255,255))
        size_x = level.get_rect()[2]
        self.__screen.blit(level, (self.__window_size[0] - size_x - 10, 0))


    def make_background(self):

        """
        Method for painting the stretching the background and drawing it onto the screen
        :return:
        """

        self.__background = pygame.image.load(self.__background_path)
        self.__background = pygame.transform.scale(self.__background, (self.__window_size[0], self.__window_size[1]))
        self.__background_rect = self.__background.get_rect()
        self.__background_rect.left, self.__background_rect.top = [0,0]

    def get_shooting_info(self):
        shooting_power = self.__destroyer.get_shooting_power()
        tower_dir = self.__destroyer.get_direction()
        return shooting_power, tower_dir

    def draw(self):

        """
        The drawing method itself. Drawing order:
        1. Background image
        2. Destroyer
        3. Bullets
        4. Crates
        5. Fades
        6. Tower
        7. Torpedos
        8. Enemies
        9. Destroyer pipe
        10. Explosions
        11. Texts
        12. HUD

        :return:
        """
        # 绘制背景图片
        self.__screen.blit(self.__background, self.__background_rect)
        # 绘制毁灭者
        self.__screen.blit(self.__destroyer.get_image()[0], self.__destroyer.get_image()[1])
        # 绘制射击力量条
        #Drawing the shoot power bar
        shooting_power, tower_dir = self.get_shooting_info()
        if 0 <= tower_dir < 90 or 270 < tower_dir < 360:
            self.__screen.fill((255 - shooting_power * 2.55, shooting_power * 2.55, 0),
                               (self.__window_size[0] / 2 - 25, self.__window_size[1] / 2 + 30,
                                shooting_power / 2, 3))
            pygame.draw.rect(self.__screen, (0, 0, 0),
                             (self.__window_size[0] / 2 - 26, self.__window_size[1] / 2 + 29,
                              shooting_power / 2 + 1, 4), 1)
        else:
            self.__screen.fill((255 - shooting_power * 2.55, shooting_power * 2.55, 0),
                               (self.__window_size[0] / 2 - 25, self.__window_size[1] / 2 - 30,
                                shooting_power / 2, 3))
            pygame.draw.rect(self.__screen, (0, 0, 0),
                             (self.__window_size[0] / 2 - 26, self.__window_size[1] / 2 - 31,
                              shooting_power / 2 + 1, 4), 1)

        # 绘制子弹
        for b in self.__bullets.get_bullets():
            self.__screen.blit(b.get_image()[0], b.get_image()[1])
            trail = b.get_trail()
            if trail is not None:
                self.__fades.add_fade(trail.get_image(), trail.get_rect(), 0.4)
        # 绘制箱子
        for c in self.__crates.get_crates():
            self.__screen.blit(c.get_image()[0], c.get_image()[1])
        # 绘制淡出效果
        for f in self.__fades.get_fades():
            blit_alpha(self.__screen, f.get_image()[0], f.get_image()[1], f.get_alpha())
        # 绘制塔
        self.__screen.blit(self.__destroyer.get_tower()[0], self.__destroyer.get_tower()[1])
        # 绘制鱼雷
        for t in self.__torpedos.get_torpedos():
            self.__screen.blit(t.get_image()[0], t.get_image()[1])
        # 绘制敌人
        for e in self.__enemies.get_enemies():
            self.__screen.blit(e.get_image()[0], e.get_image()[1])

        # 绘制爆炸
        for e in self.__explosions.get_explosions():
            self.__screen.blit(e.get_image()[0], e.get_image()[1])
        # 绘制文字
        for f in self.__texts.get_texts():
            blit_alpha(self.__screen, f.get_image()[0], f.get_image()[1], f.get_alpha())
        # 绘制HUD
        self.__render_hud()
        # 更新显示
        pygame.display.update()

    def get_screen(self):
        return self.__screen
