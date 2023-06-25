import pygame
import sys
from units import *
from gfx import *
from menus import *
from logic import *
from unit_handling import *
from time import sleep
import datetime

#Timer类用于测量游戏周期之间的时间差，并将此差返回给需要它的其他游戏对象。
class Timer(object):
    """This class is used as a time tracker for the game. Each cykle through the main loop the time difference is
    measure. The object is then passed into different game objects that require time deltas and their calculations are
    based on the time delta received from the Timer game instance.
    """
    #定义三个私有属性
    def __init__(self):
        self.__old_time = None
        self.__new_time = None
        self.__delta = None

    #开始计时
    def start(self):
        self.__old_time = datetime.datetime.now()
        self.__delta = 0

    #更新计时
    def time(self):
        new_time = datetime.datetime.now()
        self.__delta = (new_time-self.__old_time).total_seconds()
        self.__old_time = new_time

    #返回时间差
    def get_delta(self):
        return self.__delta

    #重置时间
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

    #类变量，每个级别内需要击败多少才能进入下一等级
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

    #每个级别最多同时出现多少敌人
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

    #敌人出现时长
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
        self.__enemies = []#敌人列表
        self.__bullets = []#子弹列表
        self.__enemy_strenght = None#敌人初始强度
        self.__font_size = font_size
        self.__total_enemies = 0#已击败敌人数量
        self.__max_level = max(self.__game_level_breaks.keys())#游戏中最大级别
        self.__next_level_in = self.__game_level_breaks[init_game_level]#距离下一级还需要打败多少敌人
        self.__max_enemies_ff = self.__max_enemies[init_game_level]#当前级别允许的最大敌人数量
        self.__wait_time_range = self.__enemy_wait_time_ranges[init_game_level]#停留时间
        self.__init_game_level = init_game_level#初始级别
        #self.__font_size = font_size
        self.__screen = pygame.display.set_mode(window_size)

    #等级控制
    def handle_level_up(self,game_level, enemies, texts, max_level, max_enemies, enemy_wait_time_ranges, game_level_breaks,
                        window_size):
        if enemies.get_sunk_count() >= game_level_breaks[game_level.get_level()]:
            if game_level.get_level() < max_level:
                game_level.increase()
                enemies.reset_sunk_count()
                enemies.set_max_enemies(max_enemies[game_level.get_level()])
                enemies.set_wait_time_range(enemy_wait_time_ranges[game_level.get_level()])
                next_level_in = game_level_breaks[game_level.get_level()]
                texts.add_text((window_size[0] / 2, window_size[1] / 2), "LEVEL UP!", font_size=50, positive=True)
            return next_level_in
        else:
            return None

    #键盘控制游戏事件
    def handle_events(self, ingame_menu, timer, destroyer_options=None):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type is pygame.KEYDOWN:
                key = pygame.key.name(event.key)

                if key == "escape":
                    if ingame_menu.show() == 2:
                        exit_game = True
                    else:
                        timer.reset()

                if key == "b":
                    destroyer_options.set_reload_time(100, 10)
                    destroyer_options.set_power_reduction(0, 10)
                    destroyer_options.set_power_refill(500, 10)
                    destroyer_options.set_text_timer(10)

    #键盘控制游戏角色
    def handle_keys(self, keys, destroyer, fades, bullets, timer):
        if keys[pygame.K_RIGHT]:
            destroyer.turn_tower(1, 2)

        if keys[pygame.K_LEFT]:
            destroyer.turn_tower(3, 2)

        if keys[pygame.K_SPACE]:
            if destroyer.shoot():
                fades.add_fade(destroyer.get_flash()[0], destroyer.get_flash()[1], 0.15)
                bullet_pos = project_point(self.__center[0], self.__center[1], destroyer.get_direction(),
                                           destroyer.get_tower_height() + 3)
                bullets.add_bullet(Destroyer_bullet_1(timer, bullet_pos, destroyer.get_direction()))

    def run(self):
        #Initializing all game objects
        timer = Timer()
        pygame.init()#初始化库，不写没法用这个库
        pygame.font.init()#初始化字体模块
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

            #处理等级
            next_level_in = self.handle_level_up(game_level, enemies, texts, self.__max_level, self.__max_enemies,
                                            self.__enemy_wait_time_ranges, self.__game_level_breaks, self.__window_size)
            if next_level_in is not None:
                self.__next_level_in = next_level_in

            destroyer.regenerate_power()#恢复主角能量
            enemies.add_enemy()#增加敌人
            enemies.move()#移动敌人
            enemies.shoot()#敌人射击
            torpedos.move()#移动鱼雷
            bullets.move()#移动子弹
            explosions.change_frames()#改变爆炸效果的帧数
            fades.fade()#淡出对象
            texts.move()#移动文字
            crates.make_crate(timer)#制造补给
            crates.check()#检查补给是否被获得
            logic.check()#检查游戏逻辑
            destroyer_check = destroyer_options.check()#检查主角选项
            if destroyer_check is not None:
                texts.add_text((self.__window_size[0]/2, self.__window_size[1]/2), "{}...".format(destroyer_check), font_size=18)

            self.__total_enemies = enemies.get_total_enemies()

            if destroyer.get_hp() <= 0:
                return True

            #控制游戏角色
            keys = pygame.key.get_pressed()
            self.handle_keys(keys, destroyer, fades, bullets, timer)

            #控制游戏事件
            self.handle_events(ingame_menu, timer)

            #作图
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
