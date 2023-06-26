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


from gfx import *
from units import *
import pygame

# 处理游戏得分
class Points(object):
    def __init__(self):
        """
        # Class for handling game points.
        """
        self.__points = 0

    def add_points(self, points):
        self.__points += points

    def reduce_points(self, points):
        if self.__points >= 0 + points:
            self.__points -= points
        else:
            self.__points = 0

    def get_points(self):
        return self.__points

# 初始化游戏逻辑
class Destroyer_logic(object):

    def __init__(self, timer, destroyer, destroyer_options, enemies, bullets, torpedos, explosions, fades, texts,
                 points, crates, window_size):

        self.__destroyer = destroyer
        self.__bullets = bullets
        self.__enemies = enemies
        self.__fades = fades
        self.__window_size = window_size
        self.__torpedos = torpedos
        self.__explosions = explosions
        self.__points = points
        self.__texts = texts
        self.__crates = crates
        self.__timer = timer
        self.__destroyer_options = destroyer_options

    # 检查是否有窗口外的子弹。返回要删除的子弹索引列表
    def __check_bullets(self):
        bullet_remove_list = []
        bullet_list = self.__bullets.get_bullets()

        for b, _bullet in enumerate(bullet_list):
            if not (self.__window_size[0] >= _bullet.get_position()[0] >= 0) or \
                    not (self.__window_size[1] >= _bullet.get_position()[1] >= 0):
                bullet_remove_list.append(b)
        return bullet_remove_list

    # 检查子弹和敌人之间的碰撞以及这种情况下会发生什么。返回要删除的子弹和敌人的列表。
    def __check_bullets_enemies(self):
        enemy_remove_list = []
        bullet_remove_list = []
        enemy_list = self.__enemies.get_enemies()
        bullet_list = self.__bullets.get_bullets()

        for b, _bullet in enumerate(bullet_list):
            if _bullet.is_friendly():
                for e, _enemy in enumerate(enemy_list):
                    if _bullet.get_image()[1].colliderect(_enemy.get_image()[1]):
                        bullet_remove_list.append(b)
                        self.__explosions.add_explosion(Explosion(_bullet.get_position(), 20))
                        if _enemy.reduce_hp(_bullet.get_damage()):
                            enemy_remove_list.append(e)
                            self.__points.add_points(_enemy.get_params()["points"])
                            self.__fades.add_fade(_enemy.get_image()[0], _enemy.get_image()[1], 0.5)
                            self.__texts.add_text(_bullet.get_position(), "+{}".
                                                  format(_enemy.get_params()["points"]))
            else:
                if _bullet.get_image()[1].colliderect(self.__destroyer.get_image()[1]):
                    bullet_remove_list.append(b)
                    self.__explosions.add_explosion(Explosion(_bullet.get_position(), 20))
                    self.__texts.add_text(_bullet.get_position(), "-{}".
                                          format(_bullet.get_damage(), positive=False))
                    self.__destroyer.reduce_hp(_bullet.get_damage())
        return bullet_remove_list, enemy_remove_list

    # 检查敌人是否超出游戏窗口。返回一个需要移除的敌人列表。
    def __check_enemies(self):
        enemies_remove_list = []
        for e, _enemy in enumerate(self.__enemies.get_enemies()):
            rect = _enemy.get_extent()
            # 如果敌人向上移动且超出窗口，则将其从列表中移除并减少玩家的分数。
            if _enemy.get_direction() == 0:
                if rect[1] <= 0:
                    enemies_remove_list.append(e)
                    self.__points.reduce_points(_enemy.get_params()["points"])
            # 如果敌人向右移动且超出窗口，则将其从列表中移除并减少玩家的分数。
            if _enemy.get_direction() == 1:
                if rect[0] >= self.__window_size[0]:
                    enemies_remove_list.append(e)
                    self.__points.reduce_points(_enemy.get_params()["points"])
            # 如果敌人向下移动且超出窗口，则将其从列表中移除并减少玩家的分数。
            if _enemy.get_direction() == 2:
                if rect[1] > self.__window_size:
                    enemies_remove_list.append(e)
                    self.__points.reduce_points(_enemy.get_params()["points"])
            # 如果敌人向左移动且超出窗口，则将其从列表中移除并减少玩家的分数。
            if _enemy.get_direction() == 3:
                if rect[2] <= 0:
                    enemies_remove_list.append(e)
                    self.__points.reduce_points(_enemy.get_params()["points"])
        return enemies_remove_list

    # 检查鱼雷是否超出游戏窗口。返回一个需要移除的鱼雷列表。
    def __check_torpedos(self):
        torpedos_remove_list = []
        for t, _torpedo in enumerate(self.__torpedos.get_torpedos()):
            rect = _torpedo.get_rect()
            # 如果鱼雷击中了驱逐舰，则将其从列表中移除，并添加爆炸效果、减少驱逐舰的生命值和玩家的分数。
            if _torpedo.get_image()[1].colliderect(self.__destroyer.get_image()[1]):
                torpedos_remove_list.append(t)
                self.__explosions.add_explosion(Explosion(_torpedo.get_position(), 20))
                self.__texts.add_text(_torpedo.get_position(), "-{}".
                                      format(_torpedo.get_params()["points"]), positive = False)
                self.__destroyer.reduce_hp(_torpedo.get_damage())
            # 如果鱼雷向上，右，下，左移动且超出窗口，则将其从列表中移除。
            elif _torpedo.get_direction() == 0:
                if rect[1] <= 0:
                    torpedos_remove_list.append(t)
            elif _torpedo.get_direction() == 1:
                if rect[0] >= self.__window_size[0]:
                    torpedos_remove_list.append(t)
            elif _torpedo.get_direction() == 2:
                if rect[1] >= self.__window_size[1]:
                    torpedos_remove_list.append(t)
            elif _torpedo.get_direction() == 3:
                if rect[2] <= 0:
                    torpedos_remove_list.append(t)
        return torpedos_remove_list

    # 检查子弹和鱼雷之间的碰撞，以及在这种情况下会发生什么。返回要删除的子弹和鱼雷的列表。
    def __check_bullets_torpedos(self):
        # 初始化要移除的鱼雷和子弹的列表
        torpedo_remove_list = []
        bullet_remove_list = []
        torpedo_list = self.__torpedos.get_torpedos()
        bullet_list = self.__bullets.get_bullets()
        # 遍历子弹列表
        for b,_bullet in enumerate(bullet_list):
            if _bullet.is_friendly():
                # 遍历鱼雷列表
                for t, _torpedo in enumerate(torpedo_list):
                    # 如果子弹和鱼雷发生碰撞，将它们添加到要移除的列表中
                    if _bullet.get_image()[1].colliderect(_torpedo.get_image()[1]):
                        bullet_remove_list.append(b)
                        torpedo_remove_list.append(t)
                        # 添加得分、爆炸、淡出和文本效果
                        self.__points.add_points(_torpedo.get_params()["points"])
                        self.__explosions.add_explosion(Explosion(_bullet.get_position(), 20))
                        self.__fades.add_fade(_torpedo.get_image()[0], _torpedo.get_image()[1], 0.5)
                        self.__texts.add_text(_bullet.get_position(), "+{}".
                                              format(_torpedo.get_params()["points"]))
        return bullet_remove_list, torpedo_remove_list

    # Defining the effect of each type of crate
    # 定义每种类型箱子的效果
    def apply_crate_effect(self, crate, bullet_position):
        if crate.get_type() == 0:
            self.__destroyer.increase_hp(crate.get_effect_points())
            self.__texts.add_text(bullet_position, "+{}hp".format(crate.get_effect_points()))
        elif crate.get_type() == 1:
            self.__destroyer.increase_max_hp(crate.get_effect_points())
            self.__texts.add_text(bullet_position, "+{} max hp".format(crate.get_effect_points()))
        elif crate.get_type() == 2:
            self.__destroyer.reset_hp()
            self.__texts.add_text(bullet_position, "HP refilled!")
        elif crate.get_type() == 3:
            for e in self.__enemies.get_enemies():
                self.__bullets.add_bullet(Destroyer_bullet_1(self.__timer, e.get_center_point(), 0))
            self.__texts.add_text(bullet_position, "C'EST LA BOMBE!")
        elif crate.get_type() == 4:
            x = crate.get_position()[0]
            y = crate.get_position()[1]
            self.__bullets.add_bullet(Mine(self.__timer, (x, y - 40), 0))
            self.__bullets.add_bullet(Mine(self.__timer, (x + 40, y), 0))
            self.__bullets.add_bullet(Mine(self.__timer, (x, y + 40), 0))
            self.__bullets.add_bullet(Mine(self.__timer, (x - 40, y), 0))
            self.__texts.add_text(bullet_position, "Mines!")
        elif crate.get_type() == 5:
            self.__destroyer_options.set_reload_time(100, 10)
            self.__destroyer_options.set_power_reduction(0, 10)
            self.__destroyer_options.set_power_refill(500, 10)
            self.__texts.add_text(bullet_position, "M..m...machine gun!!!")
            self.__destroyer_options.set_text_timer(10)

    # 检查子弹和箱子之间的碰撞，以及在这种情况下会发生什么。返回要删除的子弹和箱子的列表。
    def __check_bullets_crates(self):
        # 初始化要移除的箱子和子弹的列表
        bullet_remove_list = []
        crate_remove_list = []
        bullet_list = self.__bullets.get_bullets()
        crate_list = self.__crates.get_crates()

        # 遍历子弹列表
        for b, _bullet in enumerate(bullet_list):
            if _bullet.is_friendly():
                # 遍历箱子列表
                for c, _crate in enumerate(crate_list):
                    # 如果子弹和箱子发生碰撞，将它们添加到要移除的列表中
                    if _bullet.get_image()[1].colliderect(_crate.get_rect()):
                        bullet_remove_list.append(b)
                        crate_remove_list.append(c)
                        # 添加得分和爆炸效果
                        self.__points.add_points(_crate.get_points())
                        self.__explosions.add_explosion(Explosion(_bullet.get_position(), 20))
                        self.apply_crate_effect(_crate, _bullet.get_position())

        return bullet_remove_list, crate_remove_list

    def __check_enemies_crates(self):
        crates_remove_list = []
        crate_list = self.__crates.get_crates()
        for e, _enemy in enumerate(self.__enemies.get_enemies()):
            for c, _crate in enumerate(crate_list):
                if _enemy.get_rect().colliderect(_crate.get_rect()):
                    crates_remove_list.append(c)
        return crates_remove_list

    def check(self):
        bullet_remove_list_1 = self.__check_bullets()
        bullet_remove_list_2, enemy_remove_list_1 = self.__check_bullets_enemies()
        enemy_remove_list_2 = self.__check_enemies()
        torpedo_remove_list_1 = self.__check_torpedos()
        bullet_remove_list_3, torpedo_remove_list_2 = self.__check_bullets_torpedos()
        bullet_remove_list_4, crate_remove_list_1 = self.__check_bullets_crates()
        crate_remove_list_2 = self.__check_enemies_crates()

        bullet_remove_list = list(set(bullet_remove_list_1 + bullet_remove_list_2 + bullet_remove_list_3 +
                                      bullet_remove_list_4))
        enemy_remove_list = list(set(enemy_remove_list_1 + enemy_remove_list_2))
        torpedo_remove_list = list(set(torpedo_remove_list_1 + torpedo_remove_list_2))
        crate_remove_list = list(set(crate_remove_list_1 + crate_remove_list_2))

        self.__bullets.remove_bullets(bullet_remove_list)
        self.__enemies.remove_enemies(enemy_remove_list)
        self.__torpedos.remove_torpedos(torpedo_remove_list)
        self.__crates.remove_crates(crate_remove_list)

        if len(self.__enemies.get_enemies()) == 0:
            self.__enemies.add_enemy()

        # 将本轮中击败的敌人数量添加到总数中
        #Add the number of enemies sunk in this round to the total count
        self.__enemies.inc_sunk_count(len(enemy_remove_list_1))


