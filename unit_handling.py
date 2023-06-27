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

from units import *

class Enemies():
    """
    Ship_ratios is specified of number ranges between 1 and 100 for the different ship types. If ship type 1 is
    to have a 70% chance of appearing and it is first in the list, then the range should be defined as (1,70)
    and if ship type 2 then is supposed to have a 30% chance of appearing, the range has to be specified as
    (70,100). The ship type class that will be initiated based on the randomized number is defined in add_enemy

    Ship type 0: Submarine
    Ship type 1: Gun ship
    Ship type 2: Torpedo boat
    Ship type 3: Fregatte
    """

    __ship_ratios_per_level = {
        0:[(1,30), (30,70), (70,100), (100,101)],
        1:[(1,30), (30,40), (40,100), (100,101)],
        2:[(1,30), (30,45), (45,100), (100,101)],
        3:[(0,1), (1,45), (45,100), (100,101)],
        4:[(1,30), (30,45), (45,100), (100,101)],
        5:[(1,30), (30,50), (50,100), (100,101)],
        6:[(1,30), (30,50), (50,100), (100,101)],
        7:[(1,30), (30,60), (60,100), (100,101)],
        8:[(1,30), (30,60), (60,100), (100,101)],
        9:[(1,30), (30,60), (60,100), (100,101)]
    }

    def __init__(self, timer, wait_time_range, max_enemies, torpedos, crates, bullets,  game_level, window_size,
                 top_distance, max_torpedos=1):
        """
        Class for handling all enemy ship objects.
        :param wait_time_range  : range of minimum wait time to maximum wait time for spawn of next enemy
        :param max_enemies      : maximum numbers of enemies at once on the screen
        :param torpedos         : game instance of Torpedos class
        :param crates           : game instance of Crates class
        :param game_level       : game instance of game level object. Holds the game level that is used with a
                                  multiplier defined in the class of the boat types to increase boat speed
        :param window_size      : window size in x,y
        :param top_distance     : minimum y position for spwaning enemies in order to avoid HUD
        :param max_torpedos     : maximum number of torpedos on the screen at the same time
        :type wait_time_range   : set
        :type max_enemies       : int
        :type torpedos          : Torpedos
        :type crates            : Crates
        :type game_level        : Game_level
        :type window_size       : list
        :type top_distance      : int
        :type max_torpedos      : int


        :returns:
        """
        self.__timer = timer
        self.__enemy_list = []
        self.__wait_time_range = wait_time_range
        self.__max_enemies = max_enemies
        self.__next_enemy_in = 0
        self.__window_size = window_size
        self.__game_level = game_level
        self.__ship_ratios = self.__ship_ratios_per_level[self.__game_level.get_level()]
        self.__torpedos = torpedos
        self.__bullets = bullets
        self.__crates = crates
        self.__top_distance = top_distance
        self.__max_torpedos = max_torpedos
        self.__total_enemies = 0
        self.__sunk_enemies_count = 0
        self.__total_time = 0
        self.__unit_type_count = {i:0 for i in range(len(self.__ship_ratios[0]))}

    def add_enemy(self):
        """
        Method for evaluating if an enemy is to be added, based on the actual number and the time passed since the
        last spawn.

        :returns:
        """

        def check_y_position(y):
            """
            Method to check if any other enemy is on the same position or within a frame of 80 pixels. If so, the
            position is regarded as bad and a new ship will not be spawned within that range.

            :returns: boolean
            """

            # 遍历当前的敌人列表
            for e in self.__enemy_list:
                # 获取敌人的位置信息
                rect = e.get_extent()
                # 如果y位置在敌人的上下40像素内，返回True
                if rect[1] - 40 < y < rect[3] + 40:
                    return True
            # 否则返回False
            return False

        # 定义一个内部方法，用于根据船的类型、速度、起始位置和方向来创建船
        def build_my_ship(ship_type, speed, origin, direction):
            # 根据船的类型创建不同的船
            if ship_type == 0:
                ship = Submarine(speed, origin, direction)
            elif ship_type == 1 :
                ship = Gunboat(speed, origin, direction)
            elif ship_type == 2 :
                ship = Torpedoboat(speed, origin, direction)
            elif ship_type == 3:
                ship = Fregatte(speed, origin, direction)
            return ship

        def make_ship():

            """
            Function to randomize a ship and its params based on the ratios specified in __ship_ratios.
            """

            # 随机生成船的类型
            ship_type = randrange(1,100,1)
            # 获取船的类型数量
            ship_type_count = len(self.__ship_ratios)
            # 根据游戏等级获取船的比例
            self.__ship_ratios = self.__ship_ratios_per_level[self.__game_level.get_level()]
            # 根据船的比例确定船的类型
            for i in range(ship_type_count):
                if ship_type in range(self.__ship_ratios[i][0], self.__ship_ratios[i][1]):
                    ship_type = i
                    break

            #Define ship types
            if ship_type == 0:
                param_dict = Submarine.get_params()
            elif ship_type == 1:
                param_dict = Gunboat.get_params()
            elif ship_type == 2:
                param_dict = Torpedoboat.get_params()
            elif ship_type == 3:
                param_dict = Fregatte.get_params()

            # 生成船的速度
            speed = randrange(param_dict["min_speed"], param_dict["max_speed"], 1)

            # 如果船的生成方法为1，则使用固定的生成位置和方向
            if param_dict["spawn_method"] == 1:
                spawn_origin = param_dict["fixed_spawn"][0]
                x = spawn_origin[0] if spawn_origin[0] != -1 else self.__window_size[2]
                y = spawn_origin[1] if spawn_origin[1] != -1 else self.__window_size[3]
                direction = param_dict["fixed_spawn"][1]
                return build_my_ship(ship_type, speed, (x,y), direction)

            # 如果不是固定的生成位置和方向，需要随机生成
            good_y = False

            # 循环直到找到一个好的y位置
            while not good_y:
                # 随机生成y位置
                y_rand = randrange(0,2,1)
                if y_rand == 0:
                    y = randrange(self.__top_distance + 10, self.__window_size[1]/2-param_dict["min_dist"])
                if y_rand == 1:
                    y = randrange(self.__window_size[1]/2+param_dict["min_dist"], self.__window_size[1]-10)

                # 检查y位置是否好，如果好则退出循环
                if not check_y_position(y):
                    good_y = True

            # 随机生成方向
            dir_rand = randrange(0,2,1)
            direction = 1 if dir_rand == 0 else 3
            # 根据方向确定起始位置
            if direction == 1:
                origin = -150,y
            if direction == 3:
                origin = self.__window_size[0], y

            # 返回创建的船
            return build_my_ship(ship_type, speed, origin, direction)

        # 更新总时间
        self.__total_time += self.__timer.get_delta()
        # 如果当前没有敌人，则生成一个敌人
        if len(self.__enemy_list) == 0:
            self.__enemy_list.append(make_ship())
            self.__total_enemies += 1
            self.__next_enemy_in = randrange(self.__wait_time_range[0], self.__wait_time_range[1], 1)
            self.__total_time = 0
        else:
            # 如果当前的敌人数量小于最大敌人数量，并且总时间大于下一个敌人的生成时间，则生成一个敌人
            if len(self.__enemy_list) < self.__max_enemies:
                if self.__total_time > self.__next_enemy_in:
                    self.__enemy_list.append(make_ship())
                    self.__total_enemies += 1
                    self.__next_enemy_in = randrange(self.__wait_time_range[0], self.__wait_time_range[1], 1)
                    self.__total_time = 0

    def move(self):

        """
        Move all ships.
        """

        for e in self.__enemy_list:
            e.move(self.__timer.get_delta(), self.__game_level.get_level())

    def shoot(self):
        """
        Method for making the existing ships shoot torpedos under defined cicumstances, being that they have are on
        or have passed the center of the screen, they are equipped with a torpedo (which is defined in the parameter
        dictionary in the ship class) and there are less than the allowed maximum amount of torpedos on the screen at
        this point in time. If there are more, the ship looses it's torpedo.
         :returns:
        """
        for e in self.__enemy_list:
            if e.has_torpedo() and not e.get_torpedo_shot():
                self.__shoot_torpedo(e)
            if e.shoot(self.__timer.get_delta()):
                self.__shoot_bullet(e)

    def __shoot_torpedo(self, e):
        if e.get_direction() == 1:
            center_point = e.get_center_point()
            if center_point[0] > self.__window_size[0] / 2:
                if self.__torpedos.count() >= self.__max_torpedos:
                    e.set_torpedo_shot()
                else:
                    direction = 2 if center_point[1] < self.__window_size[1] / 2 else 0
                    torpedo_type = e.get_params()["torpedo_type"]
                    if torpedo_type == 0:
                        self.__torpedos.add_torpedo(Torpedo_0(Torpedo_0.get_params()["min_speed"],
                                                              center_point, direction))
                    elif torpedo_type == 1:
                        self.__torpedos.add_torpedo(Torpedo_1(Torpedo_1.get_params()["min_speed"],
                                                              center_point, direction))
                    elif torpedo_type == 2:
                        self.__torpedos.add_torpedo(Torpedo_2(Torpedo_2.get_params()["min_speed"],
                                                              center_point, direction))
                    e.set_torpedo_shot()
        elif e.get_direction() == 3:
            center_point = e.get_center_point()
            if center_point[0] < self.__window_size[0] / 2:
                if self.__torpedos.count() >= self.__max_torpedos:
                    e.set_torpedo_shot()
                else:
                    direction = 2 if center_point[1] < self.__window_size[1] / 2 else 0
                    torpedo_type = e.get_params()["torpedo_type"]
                    if torpedo_type == 0:
                        self.__torpedos.add_torpedo(Torpedo_0(Torpedo_0.get_params()["min_speed"],
                                                              center_point, direction))
                    elif torpedo_type == 1:
                        self.__torpedos.add_torpedo(Torpedo_1(Torpedo_1.get_params()["min_speed"],
                                                              center_point, direction))
                    elif torpedo_type == 2:
                        self.__torpedos.add_torpedo(Torpedo_2(Torpedo_2.get_params()["min_speed"],
                                                              center_point, direction))
                    e.set_torpedo_shot()

    def __shoot_bullet(self, e):
        if e.get_gun_type() == 0:
            bearing = get_bearing(e.get_center_point(), (self.__window_size[0] / 2, self.__window_size[1] / 2))[0]
            self.__bullets.add_bullet(Standard_enemy_bullet(self.__timer, e.get_center_point(), bearing))
        elif e.get_gun_type() == 1:
            try:
                bearing = get_bearing(e.get_center_point(), (self.__window_size[0] / 2, self.__window_size[1] / 2))[0]
                self.__bullets.add_bullet(Fregatte_bullet(self.__timer, e.get_center_point(), bearing))
            except:
                pass
                # The above code extracts the logic for shooting torpedo and bullet into two separate methods,

    # __shoot_torpedo() and __shoot_bullet() respectively. This makes the code more readable and easier to maintain.

    def get_enemies(self):
        return self.__enemy_list

    def remove_enemies(self, indices):

        """
        Removes the enemies at given indices. Called from the Destroyer_logic class game instance.
        indices (list of int) : indices of the enemies that are to be deleted.

        :returns:
        """

        if len(indices) > 0:
            new_list = []
            for e,v in enumerate(self.__enemy_list):
                if not e in indices:
                    new_list.append(v)
            self.__enemy_list = new_list

    def set_max_enemies(self, count):
        self.__max_enemies = count

    def get_total_enemies(self):
        return self.__total_enemies

    def get_sunk_count(self):
        return self.__sunk_enemies_count

    def inc_sunk_count(self, plus):
        self.__sunk_enemies_count += plus

    def reset_sunk_count(self):
        self.__sunk_enemies_count = 0

    def set_wait_time_range(self, range):
        self.__wait_time_range = range

class Torpedos(object):
    def __init__(self, timer):
        self.__torpedo_list = []
        self.__timer = timer

    def get_torpedos(self):
        return self.__torpedo_list

    def add_torpedo(self, torpedo):
        self.__torpedo_list.append(torpedo)

    def move(self):
        for t in self.__torpedo_list:
            t.move(self.__timer.get_delta())

    def remove_torpedos(self, indices):
        if len(indices) > 0:
            new_list = []
            for e,v in enumerate(self.__torpedo_list):
                if not e in indices:
                    new_list.append(v)
            self.__torpedo_list = new_list

    def count(self):
        return len(self.__torpedo_list)


class Bullets(object):

    def __init__(self, timer, origin, window_size):
        self.__timer = timer
        self.__origin = origin
        self.__window_size = window_size
        self.__bullet_list = []

    def add_bullet(self, bullet):
        self.__bullet_list.append(bullet)

    def move(self):
        pop_list = []
        for i in range(len(self.__bullet_list)):
            if self.__bullet_list[i].move() == -1:
                pop_list.append(i)

        for p in pop_list:
            self.__bullet_list.pop(p)

    def get_bullets(self):
        return self.__bullet_list

    def remove_bullets(self, indices):
        if len(indices)>0:
            new_list = []
            for b,v in enumerate(self.__bullet_list):
                if not b in indices:
                    new_list.append(v)
            self.__bullet_list = new_list


class Crates(object):
    """Repair, Armor, Life, Bomb, Mine, Machine gun"""

    __crate_ratios = [(1,20), (20,30), (30,35), (35,60), (60,80), (80,100)]

    __wait_range_per_level = {
        0:(20,25),
        1:(20,25),
        2:(20,25),
        3:(20,25),
        4:(15,20),
        5:(15,20),
        6:(15,20),
        7:(10,15),
        8:(10,15),
        9:(10,15),
    }

    def __init__(self, timer, window_size, y_margin, destroyer, game_level, timeout=8, max_crates=2):
        """
        Class for handling crates in the game. Crates appear on randomized positions in the game at random time
        intervals.

        :param timer        : timer game instance
        :param window_size  : game window size as x,y
        :param y_margin     : y margin for crate positions based for avoiding HUD
        :param destroyer    : Destroyer game instance
        :param game_level   : game instance of the game level class
        :param timeout      : defines how long in seconds crates are in existence after spawning.
        :param max_crates   : the maximum number of crates on the screen at the same point in time
        :type window_size   : list
        :type y_margin      : int
        :type destroyer     : Destroyer
        :type game_level    : Game_level
        :type timeout       : int
        :type max_crates    : int

        :returns:
        """
        self._timer = timer
        self._window_size = window_size
        self._game_level = game_level
        self._wait_range = self.__wait_range_per_level[self._game_level.get_level()]
        self._max_crates = max_crates
        self._y_margin = y_margin
        self._destroyer = destroyer
        self._enemies = None
        self._crates_list = []
        self._total_time = 0
        self._pause = randrange(self._wait_range[0], self._wait_range[1], 1)
        self._timeout = timeout

    def make_crate(self, timer):

        """
        Checks if the time randomized during the last crate spawning event has elapsed. If that is the case, a new
        crate is created based on randomized values. The randomized values are checked against existing ship and the
        destroyer positions. The values are randomized until no collision is found.
        TODO: Randomize crate types

        :returns:
        """

        self._total_time += self._timer.get_delta()
        if self._total_time > self._pause:
            rand = randrange(1,100,1)

            for i in range(len(self.__crate_ratios)):
                if self.__crate_ratios[i][0] <= rand < self.__crate_ratios[i][1]:
                    crate_type = i
                    break

            good_pos = False
            enemies = self._enemies.get_enemies()
            destroyer = self._destroyer.get_image()
            crate_size = Crate.get_size()

            while not good_pos:
                good_pos_int = 0
                x = randrange(50,self._window_size[0]-50, 1)
                y = randrange(self._y_margin, self._window_size[1] - 50, 1)

                for e in enemies:
                    #rect = pygame.Rect(0, e.get_rect()[1], self._window_size[0], e.get_rect()[3])
                    if e.get_rect().colliderect(pygame.Rect(x,y,crate_size[0], crate_size[1])):
                        good_pos_int += 1

                if destroyer[1].colliderect(pygame.Rect(x,y,crate_size[0], crate_size[1])):
                    good_pos_int += 1

                if good_pos_int == 0:
                    good_pos = True

            if crate_type == 0:
                self._crates_list.append(Repair_crate((x,y),100, 100))
            if crate_type == 1:
                self._crates_list.append(Armor_crate((x,y),100, 100))
            if crate_type == 2:
                self._crates_list.append(Life_crate((x,y),100, 100))
            if crate_type == 3:
                self._crates_list.append(Bomb_crate((x,y),100, 100))
            if crate_type == 4:
                self._crates_list.append(Mine_crate((x,y),100, 100))
            if crate_type == 5:
                self._crates_list.append(MG_crate((x,y),100,100))

            self._wait_range = self.__wait_range_per_level[self._game_level.get_level()]
            self._pause = randrange(self._wait_range[0], self._wait_range[1], 1)
            self._total_time = 0

    def get_crates(self):
        return self._crates_list

    def remove_crates(self, indices):
        if len(indices)>0:
            new_list = []
            for b,v in enumerate(self._crates_list):
                if not b in indices:
                    new_list.append(v)
            self._crates_list = new_list

    def check(self):
        remove_list = []
        for c,v in enumerate(self._crates_list):
            if v.get_age() > self._timeout:
                remove_list.append(c)
        self.remove_crates(remove_list)

    def set_enemies(self, enemies):

        """
        The enemies object for the crates class has to be set after initialization due to a circular reference, e.g.
        that the crates class uses the enemy class and the enemy class uses the crates class. Initialize the crates
        class first, hand it over to the instance of the enemy class and then set the enemies instance in the crates
        instance using this method.

        :returns:
        """

        self._enemies = enemies
