# el segundo ejercicio fue el del robot ese q tiene varios comandos:
# avanzar, girar 90 a la izq, girar 90 a la derecha,
# y cd acaba la lista de ordenes tienes q retornar la posicion X,Y y la direccion hacia donde mira
# N, W, S, E
# me preguntó dos cosas, 1) como reducir el dry 2) si añadiéramos NW, NE, SW y SE, como cambiaria la cosa
import unittest
from enum import Enum

MAX_X = 10
MAX_Y = 10


class Orientation(Enum):
    NORTH = 0
    SOUTH = 180
    WEST = 270
    EAST = 90


class Order(Enum):
    FORWARD = 'F'
    TURN_RIGHT = 'R'
    TURN_LEFT = 'L'


class Robot:
    def __init__(self, orientation: Orientation, position: tuple):
        self.orientation = orientation
        self.position = position

    def _turn_right(self):
        self.orientation = Orientation((self.orientation.value + 90) % 360)

    def _turn_left(self):
        self.orientation = Orientation((self.orientation.value - 90) % 360)

    def _move_north(self):
        if self.position[1] + 1 < MAX_Y:
            self.position = self.position[0], self.position[1] + 1

    def _move_south(self):
        if self.position[1] + 1 >= 0:
            self.position = self.position[0], self.position[1] - 1

    def _move_east(self):
        if self.position[0] + 1 < MAX_X:
            self.position = self.position[0] + 1, self.position[1]

    def _move_west(self):
        if self.position[0] - 1 >= 0:
            self.position = self.position[0] - 1, self.position[1]

    def move_from_order(self, order: Order):
        if order == Order.FORWARD:
            if self.orientation == Orientation.NORTH:
                self._move_north()
            elif self.orientation == Orientation.SOUTH:
                self._move_south()
            elif self.orientation == Orientation.EAST:
                self._move_east()
            elif self.orientation == Orientation.WEST:
                self._move_west()
        elif order == Order.TURN_RIGHT:
            self._turn_right()
        elif order == Order.TURN_LEFT:
            self._turn_left()


def process_orders(init_position: tuple, orientation_str: str, orders: str):
    orientation = Orientation[orientation_str.upper()]
    robot = Robot(orientation, init_position)
    for order_str in orders:
        order = Order(order_str)
        robot.move_from_order(order)

    return robot.position, str(robot.orientation.name).capitalize()


class ProcessOrdersTest(unittest.TestCase):
    def test_pos_0_0_North_Forward(self):
        init_position = (0, 0)
        ((x, y), orientation) = process_orders(init_position, 'North', 'F')
        self.assertEqual(x, 0)
        self.assertEqual(y, 1)
        self.assertEqual(orientation, 'North')

    def test_pos_0_0_N_FF(self):
        init_position = (0, 0)
        ((x, y), orientation) = process_orders(init_position, 'North', 'FF')
        self.assertEqual(x, 0)
        self.assertEqual(y, 2)
        self.assertEqual(orientation, 'North')

    def test_pos_0_0_N_R(self):
        init_position = (0, 0)
        ((x, y), orientation) = process_orders(init_position, 'North', 'R')
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)
        self.assertEqual(orientation, 'East')

    def test_pos_0_0_N_RF(self):
        init_position = (0, 0)
        ((x, y), orientation) = process_orders(init_position, 'North', 'RF')
        self.assertEqual(x, 1)
        self.assertEqual(y, 0)
        self.assertEqual(orientation, 'East')

    def test_pos_0_0_N_L(self):
        init_position = (0, 0)
        ((x, y), orientation) = process_orders(init_position, 'North', 'L')
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)
        self.assertEqual(orientation, 'West')

    def test_pos_0_0_N_LL(self):
        init_position = (0, 0)
        ((x, y), orientation) = process_orders(init_position, 'North', 'LL')
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)
        self.assertEqual(orientation, 'South')

    def test_pos_0_0_N_LLL(self):
        init_position = (0, 0)
        ((x, y), orientation) = process_orders(init_position, 'North', 'LLL')
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)
        self.assertEqual(orientation, 'East')

    def test_pos_0_0_N_LF(self):
        init_position = (0, 0)
        ((x, y), orientation) = process_orders(init_position, 'North', 'LF')
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)
        self.assertEqual(orientation, 'West')

    def test_pos_0_0_N_LFF(self):
        init_position = (0, 0)
        ((x, y), orientation) = process_orders(init_position, 'North', 'LFF')
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)
        self.assertEqual(orientation, 'West')


if __name__ == '__main__':
    process_orders('F')
