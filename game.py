import pygame
import sys
from units import *
from gfx import *
from menus import *
from logic import *
from unit_handling import *
from time import sleep
import datetime

class Timer(object):
    """This class is used as a time tracker for the game. Each cykle through the main loop the time difference is
    measure. The object is then passed into different game objects that require time deltas and their calculations are
    based on the time delta received from the Timer game instance.
    """
    def __init__(self):
        self.__old_time = None
        self.__new_time = None
        self.__delta = None

    def start(self):
        self.__old_time = datetime.datetime.now()
        self.__delta = 0

    def time(self):
        new_time = datetime.datetime.now()
        self.__delta = (new_time-self.__old_time).total_seconds()
        self.__old_time = new_time

    def get_delta(self):
        return self.__delta

    def reset(self):
        self.__old_time = datetime.datetime.now()
        self.__delta = 0

class Game_level(object):
    def __init__(self, init_level=0):
        self.__game_level = init_level

    def increase(self):
        self.__game_level += 1

    def get_level(self):
        return self.__game_level


class Destroyer_game(object):
    """
    The following dictionaries give the game level dependent variable values for game level brakes, maximum enemies
    and enemy wait ranges. Game level breaks define how many enemies the player has to sink before going to the next
    level. Max enemies defines the maximum number of enemies per game level. Enemy wait time ranges define the wait
    time interval in seconds that is used when spawning the next enemy.
    """
    __game_level_breaks = {
        0:20,
        1:20,
        2:20,
        3:20,
        4:20,
        5:20,
        6:20,
        7:20,
        8:20,
        9:20
    }

    __max_enemies = {
        0:5,
        1:5,
        2:6,
        3:6,
        4:7,
        5:7,
        6:8,
        7:8,
        8:10,
        9:10
    }

    __enemy_wait_time_ranges = {
        0:(1,3),
        1:(1,3),
        2:(1,3),
        3:(1,3),
        4:(1,3),
        5:(1,3),
        6:(1,2),
        7:(1,2),
        8:(1,2),
        9:(1,2),
    }

    def __init__(self, window_size=(1280, 1024), init_game_level=0, font_size=16):
        """
        Main class for the game creating and managing all game object class instances.

        :param window_size      : window size as x,y
        :param init_game_level  : the initial game level
        :param enemy_wait_range : range of spawn waiting times between enemies in seconds
        :param font_size        : font size for HUD
        :type window_size       : set
        :type init_game_level   : set
        :type font_size         : int

        :returns:
        """
        self.__window_size = window_size
        self.__center = (self.__window_size[0]/2, self.__window_size[1]/2)
        self.__enemies = []
        self.__bullets = []
        self.__enemy_strenght = None
        self.__font_size = font_size
        self.__total_enemies = 0
        self.__max_level = max(self.__game_level_breaks.keys())
        self.__next_level_in = self.__game_level_breaks[init_game_level]
        self.__max_enemies_ff = self.__max_enemies[init_game_level]
        self.__wait_time_range = self.__enemy_wait_time_ranges[init_game_level]
        self.__init_game_level = init_game_level
        self.__font_size = font_size
        self.__screen = pygame.display.set_mode(window_size)

    def run(self):
        #Initializing all game objects
        timer = Timer()
        pygame.init()
        pygame.font.init()
        game_level = Game_level(self.__init_game_level)
        points = Points()
        texts = Texts(timer)
        explosions = Explosions(timer)
        destroyer_options = Destroyer_options(timer)
        destroyer = Destroyer(0, 5000, destroyer_options, self.__window_size)
        bullets = Bullets(timer, (self.__window_size[0]/2, self.__window_size[1]/2), self.__window_size)
        torpedos = Torpedos(timer)
        crates = Crates(timer, self.__window_size, self.__font_size + 20, destroyer, game_level)
        enemies = Enemies(timer, self.__wait_time_range, self.__max_enemies_ff, torpedos, crates, bullets, game_level,
                          self.__window_size, self.__font_size)
        crates.set_enemies(enemies)
        fades = Fades(timer)
        timer.start()
        enemies.add_enemy()

        #Initializing game logic
        logic = Destroyer_logic(timer, destroyer, destroyer_options, enemies, bullets, torpedos, explosions, fades,
                                texts, points, crates,  self.__window_size)

        #Initializing game graphics
        graphics = Destroyer_gfx(self.__screen, destroyer, enemies, bullets, torpedos, explosions, fades, texts, points,
                                 crates, game_level, self.__font_size, "./media/background.png")

        #Initializing game menus
        kwargs = {"add_text":[0,"Hello","Hallo"]}
        ingame_menu = Ingame_menu(self.__screen, self.__window_size, "Titel", "Background", **kwargs)

        graphics.draw()
        exit_game = False
        counter = 0
        oldtime = datetime.datetime.now()

        while not exit_game:

            #Level handling
            if enemies.get_sunk_count() >= self.__next_level_in:
                if game_level.get_level() < self.__max_level:
                    game_level.increase()
                    enemies.reset_sunk_count()
                    enemies.set_max_enemies(self.__max_enemies[game_level.get_level()])
                    enemies.set_wait_time_range(self.__enemy_wait_time_ranges[game_level.get_level()])
                    self.__next_level_in = self.__game_level_breaks[game_level.get_level()]
                    texts.add_text((self.__window_size[0]/2, self.__window_size[1]/2),
                                   "LEVEL UP!", font_size=50, positive=True)

            destroyer.regenerate_power()
            enemies.add_enemy()
            enemies.move()
            enemies.shoot()
            torpedos.move()
            bullets.move()
            explosions.change_frames()
            fades.fade()
            texts.move()
            crates.make_crate(timer)
            crates.check()
            logic.check()
            destroyer_check = destroyer_options.check()
            if destroyer_check is not None:
                texts.add_text((self.__window_size[0]/2, self.__window_size[1]/2), "{}...".format(destroyer_check), font_size=18)

            self.__total_enemies = enemies.get_total_enemies()

            if destroyer.get_hp() <= 0:
                return True

            keys = pygame.key.get_pressed()

            if keys[pygame.K_RIGHT]:
                destroyer.turn_tower(1,2)

            if keys[pygame.K_LEFT]:
                destroyer.turn_tower(3,2)

            if keys[pygame.K_SPACE]:
                if destroyer.shoot():
                    fades.add_fade(destroyer.get_flash()[0], destroyer.get_flash()[1], 0.15)
                    bullet_pos = project_point(self.__center[0], self.__center[1], destroyer.get_direction(),
                                               destroyer.get_tower_height()+3)
                    bullets.add_bullet(Destroyer_bullet_1(timer, bullet_pos, destroyer.get_direction()))

            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()

                if event.type is pygame.KEYDOWN:
                    key = pygame.key.name(event.key)

                    if key == "escape":
                        if ingame_menu.show() == 2:
                            exit_game = True
                        else:
                            timer.reset()

                    if key == "b":
                        destroyer_options.set_reload_time(100,10)
                        destroyer_options.set_power_reduction(0,10)
                        destroyer_options.set_power_refill(500,10)
                        destroyer_options.set_text_timer(10)


            graphics.draw()
            timer.time()
            new_time = datetime.datetime.now()
            if (new_time-oldtime).total_seconds() >= 1:
                counter=0
                oldtime = new_time
            else:
                counter += 1

    def __del__(self):
        pass
