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

class Destroyer_logic(object):

    def __init__(self, timer, destroyer, destroyer_options, enemies, bullets, torpedos, explosions, fades, texts,
                 points, crates, window_size):

        """
        This is where all the game logic magic happens. Takes the instances of the different game objects and checks
        for e.g. collisions. Defines what happens when collisions are detected.

        :param destroyer    : game instance of destroyer class
        :param enemies      : game instance of enemies class
        :param bullets      : game instance of bullets class
        :param torpedos     : game instance of torpedos class
        :param explosions   : game instance of Explosions class
        :param fades        : game instance of Fades class
        :param texts        : game instance of Texts class
        :param points       : game instance of points class
        :param crates       : game instance of crates class
        :param window_size  : window size as x(int), y(int)
        :type destroyer     : Destroyer
        :type enemies       : Enemies
        :type bullets       : Bullets
        :type torpedos      : Torpedos
        :type explosions    : Explosions
        :type fades         : Fades
        :type texts         : Texts
        :type points        : Points
        :type crates        : Crates
        :type window_size   : list

        :returns:
        """

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

    def __check_bullets(self):

        """
        Checks if any of the bullets are outside the game window. Returns a list of indices for the bullets that are
        to be removed.

        :returns: list
        """
        bullet_remove_list = []
        bullet_list = self.__bullets.get_bullets()

        for b, _bullet in enumerate(bullet_list):
            if not (self.__window_size[0] >= _bullet.get_position()[0] >= 0) or \
                    not (self.__window_size[1] >= _bullet.get_position()[1] >= 0):
                bullet_remove_list.append(b)
        return bullet_remove_list

    def __check_bullets_enemies(self):

        """
        Checks for collisions between bullets and enemies and what happens in that case. Returns list of bullets and
        enemies that are to be removed.

        :returns: list
        """
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

    def __check_enemies(self):

        """
        Checks if any of the enemies are outside the game window. Returns a list of enemies that are to be removed

        :returns: list
        """
        enemies_remove_list = []
        for e, _enemy in enumerate(self.__enemies.get_enemies()):
            rect = _enemy.get_extent()

            if _enemy.get_direction() == 0:
                if rect[1] <= 0:
                    enemies_remove_list.append(e)
                    self.__points.reduce_points(_enemy.get_params()["points"])

            if _enemy.get_direction() == 1:
                if rect[0] >= self.__window_size[0]:
                    enemies_remove_list.append(e)
                    self.__points.reduce_points(_enemy.get_params()["points"])

            if _enemy.get_direction() == 2:
                if rect[1] > self.__window_size:
                    enemies_remove_list.append(e)
                    self.__points.reduce_points(_enemy.get_params()["points"])

            if _enemy.get_direction() == 3:
                if rect[2] <= 0:
                    enemies_remove_list.append(e)
                    self.__points.reduce_points(_enemy.get_params()["points"])
        return enemies_remove_list

    def __check_torpedos(self):

        """
        Checks if any of the torpedos are outside the game window. Returns a list of torpedos that are to be removed

        :returns: list
        """

        torpedos_remove_list = []
        for t, _torpedo in enumerate(self.__torpedos.get_torpedos()):
            rect = _torpedo.get_rect()

            if _torpedo.get_image()[1].colliderect(self.__destroyer.get_image()[1]):
                torpedos_remove_list.append(t)
                self.__explosions.add_explosion(Explosion(_torpedo.get_position(), 20))
                self.__texts.add_text(_torpedo.get_position(), "-{}".
                                      format(_torpedo.get_params()["points"]), positive = False)
                self.__destroyer.reduce_hp(_torpedo.get_damage())

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

    def __check_bullets_torpedos(self):

        """
        Checks for collisions between bullets and torpedos and what happens in that case. Returns list of bullets
        torpedos that are to be removed.

        :returns: list
        """

        torpedo_remove_list = []
        bullet_remove_list = []
        torpedo_list = self.__torpedos.get_torpedos()
        bullet_list = self.__bullets.get_bullets()

        for b,_bullet in enumerate(bullet_list):
            if _bullet.is_friendly():
                for t, _torpedo in enumerate(torpedo_list):
                    if _bullet.get_image()[1].colliderect(_torpedo.get_image()[1]):
                        bullet_remove_list.append(b)
                        torpedo_remove_list.append(t)
                        self.__points.add_points(_torpedo.get_params()["points"])
                        self.__explosions.add_explosion(Explosion(_bullet.get_position(), 20))
                        self.__fades.add_fade(_torpedo.get_image()[0], _torpedo.get_image()[1], 0.5)
                        self.__texts.add_text(_bullet.get_position(), "+{}".
                                              format(_torpedo.get_params()["points"]))
        return bullet_remove_list, torpedo_remove_list

    def __check_bullets_crates(self):

        """
        Checks for collisions between bullets and crates and what happens in that case. Returns list of bullets and
        crates that are to be removed.

        :returns: list
        """

        bullet_remove_list = []
        crate_remove_list = []
        bullet_list = self.__bullets.get_bullets()
        crate_list = self.__crates.get_crates()

        for b, _bullet in enumerate(bullet_list):
            if _bullet.is_friendly():
                for c, _crate in enumerate(crate_list):
                    if _bullet.get_image()[1].colliderect(_crate.get_rect()):
                        bullet_remove_list.append(b)
                        crate_remove_list.append(c)
                        self.__points.add_points(_crate.get_points())
                        self.__explosions.add_explosion(Explosion(_bullet.get_position(), 20))

                        #Defining the effect of each type of crate
                        if _crate.get_type() == 0:
                            self.__destroyer.increase_hp(_crate.get_effect_points())
                            self.__texts.add_text(_bullet.get_position(), "+{}hp".
                                                  format(_crate.get_effect_points()))

                        if _crate.get_type() == 1:
                            self.__destroyer.increase_max_hp(_crate.get_effect_points())
                            self.__texts.add_text(_bullet.get_position(), "+{} max hp".
                                              format(_crate.get_effect_points()))

                        if _crate.get_type() == 2:
                            self.__destroyer.reset_hp()
                            self.__texts.add_text(_bullet.get_position(), "HP refilled!".
                                                  format(_crate.get_effect_points()))

                        if _crate.get_type() == 3:
                            for e in self.__enemies.get_enemies():
                                self.__bullets.add_bullet(Destroyer_bullet_1(self.__timer,
                                                                             e.get_center_point(), 0))
                            self.__texts.add_text(_bullet.get_position(), "C'EST LA BOMBE!".
                                                  format(_crate.get_effect_points()))

                        if _crate.get_type() == 4:
                            x = _crate.get_position()[0]
                            y = _crate.get_position()[1]

                            self.__bullets.add_bullet(Mine(self.__timer,(x, y-40), 0))
                            self.__bullets.add_bullet(Mine(self.__timer,(x+40, y), 0))
                            self.__bullets.add_bullet(Mine(self.__timer,(x, y+40), 0))
                            self.__bullets.add_bullet(Mine(self.__timer,(x-40, y), 0))

                            self.__texts.add_text(_bullet.get_position(), "Mines!".
                                                  format(_crate.get_effect_points()))
                            break

                        if _crate.get_type() == 5:
                            self.__destroyer_options.set_reload_time(100,10)
                            self.__destroyer_options.set_power_reduction(0,10)
                            self.__destroyer_options.set_power_refill(500,10)
                            self.__texts.add_text(_bullet.get_position(), "M..m...machine gun!!!".
                                                  format(_crate.get_effect_points()))
                            self.__destroyer_options.set_text_timer(10)


        return bullet_remove_list, crate_remove_list

    def __check_enemies_crates(self):

        """
        Checks for collisions between enemies and crates and what happens in that case. Returns list of crates that
        are to be removed.

        :returns: list
        """
        crates_remove_list = []
        crate_list = self.__crates.get_crates()
        for e, _enemy in enumerate(self.__enemies.get_enemies()):
            for c, _crate in enumerate(crate_list):
                if _enemy.get_rect().colliderect(_crate.get_rect()):
                    crates_remove_list.append(c)
        return crates_remove_list

    def check(self):

        """
        Runs the collision check functions above. The returned lists containing the list indices of the objects that
        are to be deleted are combined per object type. The lists are then "destilled" down to unique indices in
        order to prevent double entries leading to problems during removal. Calls the remove methods for each object
        type with the "destilled" list as argument. Spawns a new enemy in case all enemies are gone. Returns true if
        the destroyer has been destroyed.

        :returns: boolean
        """

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

        #Add the number of enemies sunk in this round to the total count
        self.__enemies.inc_sunk_count(len(enemy_remove_list_1))


