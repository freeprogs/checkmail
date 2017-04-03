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
from checkmail import AccountHandler


class AccountHandlerGoodInput(unittest.TestCase):

    def setUp(self):
        self.ah = AccountHandler()
        self.ah.start()

    def tearDown(self):
        self.ah.end()

    def test_default_filling(self):
        self.assertEqual(self.ah.get(), (None,) * 5)

    def test_start_end_flush(self):
        ah = AccountHandler()
        ah.start()
        i = ('a', 'b', 'c', 'd', 'e')
        ah.set(*i)
        self.assertEqual(ah.get(), i)
        ah.end()
        ah.start()
        self.assertEqual(ah.get(), (None,) * 5)
        ah.end()

    def test_get_all(self):
        self.assertEqual(self.ah.get(), (None,) * 5)

        lst = (
            ('x',) * 5,
            (1,) * 5,
            ('x', 1, 'x', 1, 'x'),
            (1, 'x', 1, 'x', 1),
        )

        for i in lst:
            self.ah.set(name=i[0], server=i[1],
                        port=i[2], user=i[3],
                        password=i[4])
            self.assertEqual(self.ah.get(), i)

    def test_get_name(self):
        self.assertIsNone(self.ah.get_name(), None)
        for i in ('x', 1):
            self.ah.set(name=i)
            self.assertEqual(self.ah.get_name(), i)

    def test_get_server(self):
        self.assertIsNone(self.ah.get_server(), None)
        for i in ('x', 1):
            self.ah.set(server=i)
            self.assertEqual(self.ah.get_server(), i)

    def test_get_port(self):
        self.assertIsNone(self.ah.get_port(), None)
        for i in ('x', 1):
            self.ah.set(port=i)
            self.assertEqual(self.ah.get_port(), i)

    def test_get_user(self):
        self.assertIsNone(self.ah.get_user(), None)
        for i in ('x', 1):
            self.ah.set(user=i)
            self.assertEqual(self.ah.get_user(), i)

    def test_get_password(self):
        self.assertIsNone(self.ah.get_password(), None)
        for i in ('x', 1):
            self.ah.set(password=i)
            self.assertEqual(self.ah.get_password(), i)

    def test_isempty_with_any_field(self):

        def checkie(t):
            ah = AccountHandler()
            ah.start()
            ah.set(name=t[0], server=t[1],
                   port=t[2], user=t[3],
                   password=t[4])
            res = ah.is_empty()
            ah.end()
            return res

        lst = (
            ((None, None, None, None, None), True),
            (('x', None, None, None, None), False),
            ((None, 'x', None, None, None), False),
            ((None, None, 'x', None, None), False),
            ((None, None, None, 'x', None), False),
            ((None, None, None, None, 'x'), False),
        )

        for i, o in lst:
            self.assertEqual(checkie(i), o, msg=i)

    def test_isempty_with_false_field(self):

        def checkie(t):
            ah = AccountHandler()
            ah.start()
            ah.set(name=t[0], server=t[1],
                   port=t[2], user=t[3],
                   password=t[4])
            res = ah.is_empty()
            ah.end()
            return res

        lst = (
            ((False, None, None, None, None), False),
            ((None, False, None, None, None), False),
            ((None, None, False, None, None), False),
            ((None, None, None, False, None), False),
            ((None, None, None, None, False), False),
        )

        for i, o in lst:
            self.assertEqual(checkie(i), o, msg=i)

    def test_hasempty_any_field(self):

        def checkhe(t):
            ah = AccountHandler()
            ah.start()
            ah.set(name=t[0], server=t[1],
                   port=t[2], user=t[3],
                   password=t[4])
            res = ah.has_empty()
            ah.end()
            return res

        lst = (
            ((None, 'b', 'c', 'd', 'e'), True),
            (('a', None, 'c', 'd', 'e'), True),
            (('a', 'b', None, 'd', 'e'), True),
            (('a', 'b', 'c', None, 'e'), True),
            (('a', 'b', 'c', 'd', None), True),
        )

        for i, o in lst:
            self.assertEqual(checkhe(i), o, msg=i)

    def test_hasempty_false_fields(self):
        i = (False,) * 5
        self.ah.set(*i)
        self.assertFalse(self.ah.has_empty())

    def test_set_by_names(self):

        def checknam(t):
            ah = AccountHandler()
            ah.start()
            ah.set(name=t[0], server=t[1],
                   port=t[2], user=t[3],
                   password=t[4])
            out = (ah.get_name(),
                   ah.get_server(),
                   ah.get_port(),
                   ah.get_user(),
                   ah.get_password())
            ah.end()
            return out

        i = ('a', 'b', 'c', 'd', 'e')
        self.assertEqual(checknam(i), i)

    def test_set_by_positions(self):

        def checkpos(t):
            ah = AccountHandler()
            ah.start()
            ah.set(*t)
            out = (ah.get_name(),
                   ah.get_server(),
                   ah.get_port(),
                   ah.get_user(),
                   ah.get_password())
            ah.end()
            return out

        i = ('a', 'b', 'c', 'd', 'e')
        self.assertEqual(checkpos(i), i)

    def test_set_some_by_names(self):

        def checknam(t):
            ah = AccountHandler()
            ah.start()
            ah.set(name=t[0], server=t[1],
                   port=t[2], user=t[3],
                   password=t[4])
            out = (ah.get_name(),
                   ah.get_server(),
                   ah.get_port(),
                   ah.get_user(),
                   ah.get_password())
            ah.end()
            return out

        lst = (
            ('a', None, None, None, None),
            (None, 'b', None, None, None),
            (None, None, 'c', None, None),
            (None, None, None, 'd', None),
            (None, None, None, None, 'e'),

            ('a', 'b', None, None, None),
            (None, 'b', 'c', None, None),
            (None, None, 'c', 'd', None),
            (None, None, None, 'd', 'e'),

            ('a', 'b', 'c', None, None),
            (None, 'b', 'c', 'd', None),
            (None, None, 'c', 'd', 'e'),

            ('a', 'b', 'c', 'd', None),
            (None, 'b', 'c', 'd', 'e'),
        )

        for i in lst:
            self.assertEqual(checknam(i), i)

    def test_set_some_by_positions(self):

        def checkpos(t):
            ah = AccountHandler()
            ah.start()
            ah.set(*t)
            out = (ah.get_name(),
                   ah.get_server(),
                   ah.get_port(),
                   ah.get_user(),
                   ah.get_password())
            ah.end()
            return out

        lst = (
            ('a', None, None, None, None),
            (None, 'b', None, None, None),
            (None, None, 'c', None, None),
            (None, None, None, 'd', None),
            (None, None, None, None, 'e'),

            ('a', 'b', None, None, None),
            (None, 'b', 'c', None, None),
            (None, None, 'c', 'd', None),
            (None, None, None, 'd', 'e'),

            ('a', 'b', 'c', None, None),
            (None, 'b', 'c', 'd', None),
            (None, None, 'c', 'd', 'e'),

            ('a', 'b', 'c', 'd', None),
            (None, 'b', 'c', 'd', 'e'),
        )

        for i in lst:
            self.assertEqual(checkpos(i), i)

    def test_set_some_by_both(self):

        def checkposnam(p, n):
            ah = AccountHandler()
            ah.start()
            ah.set(*p, **n)
            out = (ah.get_name(),
                   ah.get_server(),
                   ah.get_port(),
                   ah.get_user(),
                   ah.get_password())
            ah.end()
            return out

        lst = (
            (('a',), {'server': 'b'},
             ('a', 'b', None, None, None)),
            (('a', 'b'), {'port': 'c', 'user': 'd'},
             ('a', 'b', 'c', 'd', None)),
            (('a', 'b'), {'user': 'd', 'port': 'c'},
             ('a', 'b', 'c', 'd', None)),
        )

        for t, d, o in lst:
            self.assertEqual(checkposnam(t, d), o, msg=(t, d))

    def test_unset(self):

        def checkposnam(p, n):
            ah = AccountHandler()
            ah.start()
            ah.set(*p)
            ah.unset(**n)
            out = (ah.get_name(),
                   ah.get_server(),
                   ah.get_port(),
                   ah.get_user(),
                   ah.get_password())
            ah.end()
            return out

        lst = (
            (('a', 'b', 'c', 'd', 'e'),
             {'name': True},
             (None, 'b', 'c', 'd', 'e')),
            (('a', 'b', 'c', 'd', 'e'),
             {'server': True},
             ('a', None, 'c', 'd', 'e')),
            (('a', 'b', 'c', 'd', 'e'),
             {'port': True},
             ('a', 'b', None, 'd', 'e')),
            (('a', 'b', 'c', 'd', 'e'),
             {'user': True},
             ('a', 'b', 'c', None, 'e')),
            (('a', 'b', 'c', 'd', 'e'),
             {'password': True},
             ('a', 'b', 'c', 'd', None)),

            (('a', 'b', 'c', 'd', 'e'),
             {'name': True, 'server': True},
             (None, None, 'c', 'd', 'e')),
            (('a', 'b', 'c', 'd', 'e'),
             {'server': True, 'port': True},
             ('a', None, None, 'd', 'e')),
            (('a', 'b', 'c', 'd', 'e'),
             {'port': True, 'user': True},
             ('a', 'b', None, None, 'e')),
            (('a', 'b', 'c', 'd', 'e'),
             {'user': True, 'password': True},
             ('a', 'b', 'c', None, None)),
        )

        for t, d, o in lst:
            self.assertEqual(checkposnam(t, d), o, msg=(t, d))


if __name__ == '__main__':
    unittest.main()
