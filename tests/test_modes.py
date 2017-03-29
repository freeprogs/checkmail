#!/usr/bin/env python3

import unittest

import sys
sys.path.append('..')
from checkmail import ModesHandler


class ModeRangeGoodInput(unittest.TestCase):

    def test_mode_is_not_enabled_if_nothing_set(self):
        handler = ModesHandler()
        handler.start()
        res = handler.is_enabled_range()
        handler.end()
        self.assertFalse(res)

    def test_mode_is_enabled_if_start_set(self):
        handler = ModesHandler()
        handler.start()
        handler.set_range(start=1)
        res = handler.is_enabled_range()
        handler.end()
        self.assertTrue(res)

    def test_mode_is_enabled_if_end_set(self):
        handler = ModesHandler()
        handler.start()
        handler.set_range(end=1)
        res = handler.is_enabled_range()
        handler.end()
        self.assertTrue(res)

    def test_can_get_only_start(self):
        handler = ModesHandler()
        handler.start()
        handler.set_range(start=1, end=2)
        res = handler.get_range_start()
        handler.end()
        self.assertEqual(res, 1, msg=res)

    def test_can_get_only_end(self):
        handler = ModesHandler()
        handler.start()
        handler.set_range(start=1, end=2)
        res = handler.get_range_end()
        handler.end()
        self.assertEqual(res, 2, msg=res)

    def test_can_get_both_start_and_end(self):
        handler = ModesHandler()
        handler.start()
        handler.set_range(start=1, end=2)
        res = handler.get_range()
        handler.end()
        self.assertEqual(res, (1, 2), msg=res)

    def test_can_unset_only_start(self):
        handler = ModesHandler()
        handler.start()
        handler.set_range(start=1, end=2)
        handler.unset_range(start=True)
        res = handler.get_range()
        handler.end()
        self.assertEqual(res, (None, 2), msg=res)

    def test_can_unset_only_end(self):
        handler = ModesHandler()
        handler.start()
        handler.set_range(start=1, end=2)
        handler.unset_range(end=True)
        res = handler.get_range()
        handler.end()
        self.assertEqual(res, (1, None), msg=res)

    def test_can_unset_both_start_and_end(self):
        handler = ModesHandler()
        handler.start()
        handler.set_range(start=1, end=2)
        handler.unset_range(start=True, end=True)
        res = handler.get_range()
        handler.end()
        self.assertEqual(res, (None, None), msg=res)


if __name__ == '__main__':
    unittest.main()
