# This is a sample Python script.


import unittest
from unittest.mock import patch, call


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


class Calculator:
    def __init__(self, operator):
        self.operation = operator

    def __call__(self, *args, **kwargs):
        return self.operation(*args)


class PrintTest(unittest.TestCase):
    @patch('builtins.print')
    def test_print(self, mock_print):
        print_hi('foo')

        mock_print.assert_called_with('Hi, foo')
        assert mock_print.mock_calls == [call('Hi, foo')]


class CalculatorTest(unittest.TestCase):
    def test_sum(self):
        operation = lambda x, y: x + y
        self.assertEqual(Calculator(operation)(1, 2), 3)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    unittest.main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
