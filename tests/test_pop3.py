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
from unittest.mock import patch

import sys
sys.path.append('..')
from checkmail import (Pop3ConnectServerError,
                       Pop3ConnectPortError,
                       Pop3ConnectTimeoutError,
                       Pop3LoginError,
                       Pop3LoginTimeoutError,
                       Pop3TopTimeoutError,
                       Pop3CantDecodeHeaders,
                       Pop3Handler)
import poplib

import socket


class Pop3HandlerGoodInput(unittest.TestCase):

    def setUp(self):
        self.p1 = patch('poplib.POP3_SSL', autospec=True)
        self.m1 = self.p1.start()

    def tearDown(self):
        self.p1.stop()

    def test_raise_when_in_connection_happens_timeout(self):
        self.m1.side_effect = [socket.timeout]
        p3h = Pop3Handler('server', '995', 'user', 'password', 10)
        p3h.start()
        self.assertRaises(Pop3ConnectTimeoutError, p3h.login)
        p3h.end()

    def test_raise_when_in_connection_incorrect_port(self):
        self.m1.side_effect = [ConnectionRefusedError]
        p3h = Pop3Handler('server', '995', 'user', 'password', 10)
        p3h.start()
        self.assertRaises(Pop3ConnectPortError, p3h.login)
        p3h.end()

    def test_raise_when_in_connection_happens_unknown_error(self):
        self.m1.side_effect = [socket.gaierror]
        p3h = Pop3Handler('server', '995', 'user', 'password', 10)
        p3h.start()
        self.assertRaises(Pop3ConnectServerError, p3h.login)
        p3h.end()

    def test_raise_when_in_user_happens_timeout(self):
        self.m1.return_value.user.side_effect = [socket.timeout]
        p3h = Pop3Handler('server', '995', 'user', 'password', 10)
        p3h.start()
        self.assertRaises(Pop3LoginTimeoutError, p3h.login)
        p3h.end()

    def test_raise_when_in_user_happens_unknown_error(self):
        self.m1.return_value.user.side_effect = [poplib.error_proto]
        p3h = Pop3Handler('server', '995', 'user', 'password', 10)
        p3h.start()
        self.assertRaises(Pop3LoginError, p3h.login)
        p3h.end()

    def test_raise_when_in_password_happens_timeout(self):
        self.m1.return_value.pass_.side_effect = [socket.timeout]
        p3h = Pop3Handler('server', '995', 'user', 'password', 10)
        p3h.start()
        self.assertRaises(Pop3LoginTimeoutError, p3h.login)
        p3h.end()

    def test_raise_when_password_is_incorrect(self):
        self.m1.return_value.pass_.side_effect = [poplib.error_proto]
        p3h = Pop3Handler('server', '995', 'user', 'password', 10)
        p3h.start()
        self.assertRaises(Pop3LoginError, p3h.login)
        p3h.end()

    def test_raise_when_in_top_happens_timeout(self):
        self.m1.return_value.list.return_value = (b'+OK 1 1234',)
        self.m1.return_value.top.side_effect = [socket.timeout]
        p3h = Pop3Handler('server', '995', 'user', 'password', 10)
        p3h.start()
        p3h.login()
        self.assertRaises(Pop3TopTimeoutError,
                          p3h.get_message_headers, 1, ['a'])
        p3h.end()

    def test_get_number_of_messages_after_login(self):

        def checkn(n):
            p3h = Pop3Handler('server', '995', 'user', 'password', 10)
            p3h.start()
            p3h.login()
            self.m1.return_value.list.return_value = \
                (b'+OK ' + str(n).encode('ascii') + b' 1234',)
            res = p3h.count_messages()
            p3h.disconnect()
            p3h.end()
            return res

        for i in range(5):
            self.assertEqual(checkn(i), i, msg=i)

    def test_can_decode_mime_headers_with_correct_encoding(self):

        def checkhs(h, s):
            self.m1.return_value.list.return_value = (b'+OK 1 1234',)
            self.m1.return_value.top.return_value = (
                None,
                h,
                None
            )
            p3h = Pop3Handler('server', '995', 'user', 'password', 10)
            p3h.start()
            p3h.login()
            res = p3h.get_message_headers(1, s)
            p3h.end()
            return res

        lst = (
            ([b'a: =?utf-8?q?=d0=b0=d0=b1=d0=b2?='],
             ['a'],
             ('абв',)),
            ([b'a: =?utf-8?q?=d0=b0=d0=b1=d0=b2?=',
              b'b: =?utf-8?q?=d0=b3=d0=b4=d0=b5?='],
             ['a', 'b'],
             ('абв', 'где',))
        )

        for i1, i2, o in lst:
            self.assertEqual(checkhs(i1, i2), o, msg=(i1, i2))


class Pop3HandlerBadInput(unittest.TestCase):

    def setUp(self):
        self.p1 = patch('poplib.POP3_SSL', autospec=True)
        self.m1 = self.p1.start()

    def tearDown(self):
        self.p1.stop()

    def test_return_zero_when_found_negative_number_of_messages(self):

        def checkn(n):
            p3h = Pop3Handler('server', '995', 'user', 'password', 10)
            p3h.start()
            p3h.login()
            self.m1.return_value.list.return_value = \
                (b'+OK ' + str(n).encode('ascii') + b' 1234',)
            res = p3h.count_messages()
            p3h.disconnect()
            p3h.end()
            return res

        lst = ((-1, 0),
               (-2, 0),
               (-3, 0))

        for i, o in lst:
            self.assertEqual(checkn(i), o, msg=i)

    def test_raise_on_decode_mime_headers_with_incorrect_encoding(self):

        def checkhs(h, s):
            self.m1.return_value.list.return_value = (b'+OK 1 1234',)
            self.m1.return_value.top.return_value = (
                None,
                h,
                None
            )
            p3h = Pop3Handler('server', '995', 'user', 'password', 10)
            p3h.start()
            p3h.login()
            res = p3h.get_message_headers(1, s)
            p3h.end()
            return res

        lst = (
            ([b'a: =?utf-8?q?=d0?='], ['a']),
            ([b'a: =?cp1251?q?=f0=9f=98=82?='], ['a']),
            ([b'a: =?utf-8?q?=d0=b0=d0=b1=d0=b2?=',
              b'b: =?utf-8?q?=d0?='],
             ['a', 'b']),
        )

        for i1, i2 in lst:
            self.assertRaises(Pop3CantDecodeHeaders, checkhs, i1, i2)


if __name__ == '__main__':
    unittest.main()
