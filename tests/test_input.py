#!/usr/bin/env python3

import unittest
from unittest.mock import patch

import sys
sys.path.append('..')
from mail import (InputHandler,
                  InputNumNone,
                  InputNumError,
                  InputNumRangeError)


class InputHandlerGoodInput(unittest.TestCase):

    def setUp(self):
        self.p1 = patch('mail.input', create=True)
        self.m1 = self.p1.start()
        self.p2 = patch('getpass.getpass')
        self.m2 = self.p2.start()

    def tearDown(self):
        self.p1.stop()
        self.p2.stop()

    def test_can_set_empty_default_prompt_for_string_input(self):
        handler = InputHandler()
        handler.start()
        handler.input_string()
        handler.end()
        self.m1.assert_called_once_with('')

    def test_can_set_default_prompt_for_string_input(self):
        handler = InputHandler()
        handler.start(string_prompt='a')
        handler.input_string()
        handler.end()
        self.m1.assert_called_once_with('a')

    def test_can_set_nondefault_prompt_for_string_input(self):
        handler = InputHandler()
        handler.start()
        handler.input_string('a')
        handler.end()
        self.m1.assert_called_once_with('a')

    def test_can_replace_default_prompt_for_string_input(self):
        handler = InputHandler()
        handler.start(string_prompt='a')
        handler.input_string()
        handler.input_string('b')
        handler.end()
        self.m1.assert_any_call('a')
        self.m1.assert_any_call('b')

    def test_can_input_a_string_in_string_input(self):

        def check(s):
            self.m1.reset_mock()
            self.m1.return_value = s
            handler = InputHandler()
            handler.start()
            res = handler.input_string()
            handler.end()
            return res

        lst = [
            ('a', 'a'),
            ('a a', 'a a'),
            ('a a a', 'a a a'),
            ('$', '$'),
        ]

        for i, o in lst:
            self.assertEqual(i, o, msg=repr(i))

    def test_can_set_empty_default_prompt_for_number_input(self):
        handler = InputHandler()
        handler.start()
        handler.input_number()
        handler.end()
        self.m1.assert_called_once_with('')

    def test_can_set_default_prompt_for_number_input(self):
        handler = InputHandler()
        handler.start(number_prompt='a')
        handler.input_number()
        handler.end()
        self.m1.assert_called_once_with('a')

    def test_can_set_nondefault_prompt_for_number_input(self):
        handler = InputHandler()
        handler.start()
        handler.input_number(prompt='a')
        handler.end()
        self.m1.assert_called_once_with('a')

    def test_can_replace_default_prompt_for_number_input(self):
        handler = InputHandler()
        handler.start(number_prompt='a')
        handler.input_number()
        handler.input_number(prompt='b')
        handler.end()
        self.m1.assert_any_call('a')
        self.m1.assert_any_call('b')

    def test_can_input_a_number_in_number_input(self):

        def check(s):
            self.m1.reset_mock()
            self.m1.return_value = s
            handler = InputHandler()
            handler.start()
            res = handler.input_number()
            handler.end()
            return res

        lst = [
            ('0', 0),

            ('1', 1),
            ('2', 2),
            ('10', 10),

            ('-1', -1),
            ('-2', -2),
            ('-10', -10),

            ('-1000000', -1000000),
            ('1000000', 1000000),

            ('000', 0),
            ('0001', 1),
        ]

        for i, o in lst:
            self.assertEqual(check(i), o, msg=repr(i))

    def test_raise_none_on_empty_input_in_number_input(self):
        self.m1.return_value = ''
        handler = InputHandler()
        handler.start()
        self.assertRaises(InputNumNone, handler.input_number)
        handler.end()

    def test_can_input_a_number_in_range_in_number_input(self):
        self.m1.return_value = '5'
        handler = InputHandler()
        handler.start()
        res = handler.input_number(1, 10)
        handler.end()
        self.assertEqual(res, 5, msg=res)

    def test_can_see_borders_of_range_in_number_input(self):
        self.m1.return_value = '1'
        handler = InputHandler()
        handler.start()
        res = handler.input_number(1, 3)
        handler.end()
        self.assertEqual(res, 1, msg=res)

        self.m1.return_value = '3'
        handler = InputHandler()
        handler.start()
        res = handler.input_number(1, 3)
        handler.end()
        self.assertEqual(res, 3, msg=res)

    def test_can_set_only_left_border_of_range_in_number_input(self):
        self.m1.return_value = '10'
        handler = InputHandler()
        handler.start()
        res = handler.input_number(number_min=1)
        handler.end()
        self.assertEqual(res, 10, msg=res)

    def test_can_set_only_right_border_of_range_in_number_input(self):
        self.m1.return_value = '1'
        handler = InputHandler()
        handler.start()
        res = handler.input_number(number_max=10)
        handler.end()
        self.assertEqual(res, 1, msg=res)

    def test_can_set_empty_default_prompt_for_password_input(self):
        handler = InputHandler()
        handler.start()
        handler.input_password()
        handler.end()
        self.m2.assert_called_once_with('')

    def test_can_set_default_prompt_for_password_input(self):
        handler = InputHandler()
        handler.start(password_prompt='a')
        handler.input_password()
        handler.end()
        self.m2.assert_called_once_with('a')

    def test_can_set_nondefault_prompt_for_password_input(self):
        handler = InputHandler()
        handler.start()
        handler.input_password('a')
        handler.end()
        self.m2.assert_called_once_with('a')

    def test_can_replace_default_prompt_for_password_input(self):
        handler = InputHandler()
        handler.start(password_prompt='a')
        handler.input_password()
        handler.input_password('b')
        handler.end()
        self.m2.assert_any_call('a')
        self.m2.assert_any_call('b')

    def test_can_set_several_default_prompts_for_inputs(self):
        handler = InputHandler()
        handler.start(number_prompt='a',
                      password_prompt='b',
                      string_prompt='c')
        handler.input_number()
        handler.input_password()
        handler.input_string()
        handler.end()
        self.m1.assert_any_call('a')
        self.m1.assert_any_call('c')
        self.m2.assert_called_once_with('b')


class InputHandlerBadInput(unittest.TestCase):

    def setUp(self):
        self.p1 = patch('mail.input', create=True)
        self.m1 = self.p1.start()
        self.p2 = patch('getpass.getpass')
        self.m2 = self.p2.start()

    def tearDown(self):
        self.p1.stop()
        self.p2.stop()

    def test_raise_on_incorrect_input_in_number_input(self):

        def check(s):
            self.m1.reset_mock()
            self.m1.return_value = s
            handler = InputHandler()
            handler.start()
            handler.input_number()
            handler.end()

        lst = [
            ' ',
            'a',
            'a1',
            '1a',
            '1 a',
        ]

        for i in lst:
            with self.assertRaises(InputNumError, msg=repr(i)):
                check(i)

    def test_raise_on_incorrect_borders_of_range_in_number_input(self):
        def check(s, start, end):
            self.m1.return_value = s
            handler = InputHandler()
            handler.start()
            handler.input_number(start, end)
            handler.end()

        lst = [
            ('0', 1, 3),
            ('4', 1, 3),

            ('0', 1, 1),
            ('2', 1, 1),
        ]

        for i1, i2, i3 in lst:
            with self.assertRaises(InputNumRangeError, msg=(i1, i2, i3)):
                check(i1, i2, i3)

    def test_raise_on_incorrect_left_border_of_range_in_number_input(self):
        i1, i2 = '0', 1
        self.m1.return_value = i1
        handler = InputHandler()
        handler.start()
        with self.assertRaises(InputNumRangeError, msg=(i1, i2)):
            handler.input_number(number_min=i2)
        handler.end()

    def test_raise_on_incorrect_right_border_of_range_in_number_input(self):
        i1, i2 = '2', 1
        self.m1.return_value = i1
        handler = InputHandler()
        handler.start()
        with self.assertRaises(InputNumRangeError, msg=(i1, i2)):
            handler.input_number(number_max=i2)
        handler.end()


if __name__ == '__main__':
    unittest.main()
