#!/usr/bin/env python3

import unittest
from unittest.mock import patch

import sys
sys.path.append('..')
from checkmail import (ConnectionHandler,
                       ConnectionRangeError,
                       Pop3TopTimeoutError,
                       Pop3CantDecodeHeaders)


class ConnectionHandlerPop3GoodInput(unittest.TestCase):

    def setUp(self):
        self.p1 = patch('checkmail.Pop3Handler', autospec=True)
        self.m1 = self.p1.start()

    def tearDown(self):
        self.p1.stop()

    def test_can_receive_one_message(self):
        self.m1.return_value.count_messages.return_value = 1
        self.m1.return_value.get_message_headers.return_value = ('a', 'b')
        ch = ConnectionHandler('server', 'port', 'user', 'password', 10)
        ch.start()
        res = ch.get_pop3_addrsubj()
        ch.end()
        self.assertEqual(res, [('a', 'b')], msg=res)

    def test_can_receive_several_messages(self):

        def check(n, lst):
            self.m1.return_value.count_messages.return_value = n
            self.m1.return_value.get_message_headers.side_effect = lst
            ch = ConnectionHandler('server', 'port', 'user', 'password', 10)
            ch.start()
            res = ch.get_pop3_addrsubj()
            ch.end()
            return res

        lst = [
            (2, [('a1', 'b1'),
                 ('a2', 'b2')]),
            (3, [('a1', 'b1'),
                 ('a2', 'b2'),
                 ('a3', 'b3')]),
            (4, [('a1', 'b1'),
                 ('a2', 'b2'),
                 ('a3', 'b3'),
                 ('a4', 'b4')]),
        ]

        for i1, i2 in lst:
            o = i2
            self.assertEqual(check(i1, i2), o, msg=(i1, i2))

    def test_will_try_to_receive_one_message_three_times(self):
        self.m1.return_value.count_messages.return_value = 1
        self.m1.return_value.get_message_headers.side_effect = [
            Pop3TopTimeoutError,
            Pop3TopTimeoutError,
            ('a', 'b')
        ]
        ch = ConnectionHandler('server', 'port', 'user', 'password', 10)
        ch.start()
        res = ch.get_pop3_addrsubj()
        ch.end()

        self.assertEqual(res, [('a', 'b')], msg=res)

        self.m1.return_value.count_messages.return_value = 1
        self.m1.return_value.get_message_headers.side_effect = [
            Pop3TopTimeoutError,
            Pop3TopTimeoutError,
            Pop3TopTimeoutError,
            ('a', 'b')
        ]
        ch = ConnectionHandler('server', 'port', 'user', 'password', 10)
        ch.start()
        res = ch.get_pop3_addrsubj()
        ch.end()

        self.assertNotEqual(res, [('a', 'b')], msg=res)

    def test_make_failure_message_when_cant_receive_it_3_times(self):
        self.m1.return_value.count_messages.return_value = 1
        self.m1.return_value.get_message_headers.side_effect = [
            Pop3TopTimeoutError,
            Pop3TopTimeoutError,
            Pop3TopTimeoutError,
            ('a', 'b')
        ]
        ch = ConnectionHandler('server', 'port', 'user', 'password', 10)
        ch.start()
        res = ch.get_pop3_addrsubj()
        ch.end()

        o = [('unknown', "can't receive headers")]
        self.assertEqual(res, o, msg=res)

    def test_make_failure_message_when_cant_decode_it(self):
        self.m1.return_value.count_messages.return_value = 1
        self.m1.return_value.get_message_headers.side_effect = [
            Pop3CantDecodeHeaders
        ]
        ch = ConnectionHandler('server', 'port', 'user', 'password', 10)
        ch.start()
        res = ch.get_pop3_addrsubj()
        ch.end()

        o = [('unknown', "can't decode headers")]
        self.assertEqual(res, o, msg=res)

    def test_can_receive_failures_mixed_with_success_messages(self):
        self.m1.return_value.count_messages.return_value = 7
        self.m1.return_value.get_message_headers.side_effect = [
            ('a1', 'b1'),
            Pop3CantDecodeHeaders,
            ('a2', 'b2'),
            Pop3TopTimeoutError,
            Pop3TopTimeoutError,
            Pop3TopTimeoutError,
            ('a3', 'b3'),
            Pop3CantDecodeHeaders,
            ('a4', 'b4'),
        ]
        ch = ConnectionHandler('server', 'port', 'user', 'password', 10)
        ch.start()
        res = ch.get_pop3_addrsubj()
        ch.end()

        o = [('a1', 'b1'),
             ('unknown', "can't decode headers"),
             ('a2', 'b2'),
             ('unknown', "can't receive headers"),
             ('a3', 'b3'),
             ('unknown', "can't decode headers"),
             ('a4', 'b4')]

        self.assertEqual(res, o, msg=res)


class ConnectionHandlerPop3RangeGoodInput(unittest.TestCase):

    def setUp(self):
        self.p1 = patch('checkmail.Pop3Handler', autospec=True)
        self.m1 = self.p1.start()

    def tearDown(self):
        self.p1.stop()

    def test_can_receive_one_message(self):
        self.m1.return_value.count_messages.return_value = 1
        self.m1.return_value.get_message_headers.return_value = ('a', 'b')
        ch = ConnectionHandler('server', 'port', 'user', 'password', 10)
        ch.start()
        res = ch.get_pop3_addrsubj_range(None, None)
        ch.end()
        self.assertEqual(res, [('a', 'b')], msg=res)

    def test_can_receive_several_messages(self):

        def check(n, lst):
            self.m1.return_value.count_messages.return_value = n
            self.m1.return_value.get_message_headers.side_effect = lst
            ch = ConnectionHandler('server', 'port', 'user', 'password', 10)
            ch.start()
            res = ch.get_pop3_addrsubj_range(None, None)
            ch.end()
            return res

        lst = [
            (2, [('a1', 'b1'),
                 ('a2', 'b2')]),
            (3, [('a1', 'b1'),
                 ('a2', 'b2'),
                 ('a3', 'b3')]),
            (4, [('a1', 'b1'),
                 ('a2', 'b2'),
                 ('a3', 'b3'),
                 ('a4', 'b4')]),
        ]

        for i1, i2 in lst:
            o = i2
            self.assertEqual(check(i1, i2), o, msg=(i1, i2))

    def test_will_try_to_receive_one_message_three_times(self):
        self.m1.return_value.count_messages.return_value = 1
        self.m1.return_value.get_message_headers.side_effect = [
            Pop3TopTimeoutError,
            Pop3TopTimeoutError,
            ('a', 'b')
        ]
        ch = ConnectionHandler('server', 'port', 'user', 'password', 10)
        ch.start()
        res = ch.get_pop3_addrsubj_range(None, None)
        ch.end()

        self.assertEqual(res, [('a', 'b')], msg=res)

        self.m1.return_value.count_messages.return_value = 1
        self.m1.return_value.get_message_headers.side_effect = [
            Pop3TopTimeoutError,
            Pop3TopTimeoutError,
            Pop3TopTimeoutError,
            ('a', 'b')
        ]
        ch = ConnectionHandler('server', 'port', 'user', 'password', 10)
        ch.start()
        res = ch.get_pop3_addrsubj_range(None, None)
        ch.end()

        self.assertNotEqual(res, [('a', 'b')], msg=res)

    def test_make_failure_message_when_cant_receive_it_3_times(self):
        self.m1.return_value.count_messages.return_value = 1
        self.m1.return_value.get_message_headers.side_effect = [
            Pop3TopTimeoutError,
            Pop3TopTimeoutError,
            Pop3TopTimeoutError,
            ('a', 'b')
        ]
        ch = ConnectionHandler('server', 'port', 'user', 'password', 10)
        ch.start()
        res = ch.get_pop3_addrsubj_range(None, None)
        ch.end()

        o = [('unknown', "can't receive headers")]
        self.assertEqual(res, o, msg=res)

    def test_make_failure_message_when_cant_decode_it(self):
        self.m1.return_value.count_messages.return_value = 1
        self.m1.return_value.get_message_headers.side_effect = [
            Pop3CantDecodeHeaders
        ]
        ch = ConnectionHandler('server', 'port', 'user', 'password', 10)
        ch.start()
        res = ch.get_pop3_addrsubj_range(None, None)
        ch.end()

        o = [('unknown', "can't decode headers")]
        self.assertEqual(res, o, msg=res)

    def test_can_receive_failures_mixed_with_success_messages(self):
        self.m1.return_value.count_messages.return_value = 7
        self.m1.return_value.get_message_headers.side_effect = [
            ('a1', 'b1'),
            Pop3CantDecodeHeaders,
            ('a2', 'b2'),
            Pop3TopTimeoutError,
            Pop3TopTimeoutError,
            Pop3TopTimeoutError,
            ('a3', 'b3'),
            Pop3CantDecodeHeaders,
            ('a4', 'b4'),
        ]
        ch = ConnectionHandler('server', 'port', 'user', 'password', 10)
        ch.start()
        res = ch.get_pop3_addrsubj_range(None, None)
        ch.end()

        o = [('a1', 'b1'),
             ('unknown', "can't decode headers"),
             ('a2', 'b2'),
             ('unknown', "can't receive headers"),
             ('a3', 'b3'),
             ('unknown', "can't decode headers"),
             ('a4', 'b4')]

        self.assertEqual(res, o, msg=res)

    def test_can_receive_one_message_with_equal_range_ends(self):
        self.m1.return_value.count_messages.return_value = 3
        method = self.m1.return_value.get_message_headers
        ch = ConnectionHandler('server', 'port', 'user', 'password', 10)
        ch.start()

        lst = [(1, 1, 1),
               (2, 2, 1),
               (3, 3, 1)]

        for i1, i2, o in lst:
            ch.get_pop3_addrsubj_range(i1, i2)
            self.assertEqual(method.call_count, o, msg=(i1, i2))
            method.reset_mock()

        ch.end()

    def test_can_receive_several_messages_with_range(self):
        self.m1.return_value.count_messages.return_value = 5
        method = self.m1.return_value.get_message_headers
        ch = ConnectionHandler('server', 'port', 'user', 'password', 10)
        ch.start()

        lst = [
            (1, 2, 2),
            (1, 3, 3),
            (2, 3, 2),
            (2, 4, 3),
            (1, 5, 5)
        ]

        for i1, i2, o in lst:
            ch.get_pop3_addrsubj_range(i1, i2)
            self.assertEqual(method.call_count, o, msg=(i1, i2))
            method.reset_mock()

        ch.end()

    def test_will_stop_on_last_message_if_range_end_is_greater(self):
        self.m1.return_value.count_messages.return_value = 3
        method = self.m1.return_value.get_message_headers
        ch = ConnectionHandler('server', 'port', 'user', 'password', 10)
        ch.start()

        lst = [
            (1, 4, 3),
            (1, 5, 3),
            (2, 4, 2),
            (2, 5, 2),
            (3, 4, 1)
        ]

        for i1, i2, o in lst:
            ch.get_pop3_addrsubj_range(i1, i2)
            self.assertEqual(method.call_count, o, msg=(i1, i2))
            method.reset_mock()

        ch.end()

    def test_raise_on_range_start_is_greater_than_last_message(self):
        self.m1.return_value.count_messages.return_value = 3
        ch = ConnectionHandler('server', 'port', 'user', 'password', 10)
        ch.start()
        self.assertRaises(ConnectionRangeError,
                          ch.get_pop3_addrsubj_range, 4, 4)
        ch.end()

    def test_can_see_empty_box_with_set_range(self):
        self.m1.return_value.count_messages.return_value = 0
        ch = ConnectionHandler('server', 'port', 'user', 'password', 10)
        ch.start()

        res = ch.get_pop3_addrsubj_range(1, 1)
        self.assertEqual(res, [])
        res = ch.get_pop3_addrsubj_range(1, 3)
        self.assertEqual(res, [])

        ch.end()


if __name__ == '__main__':
    unittest.main()
