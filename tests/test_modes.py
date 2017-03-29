#!/usr/bin/env python3

# This file is a part of __PROGRAM_NAME__ __PROGRAM_VERSION__
#
# This file installs __PROGRAM_NAME__.py and some scripts in the operating
# system, cleans temporary files and directory in the project.
#
# __PROGRAM_COPYRIGHT__ __PROGRAM_AUTHOR__ __PROGRAM_AUTHOR_EMAIL__
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


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
