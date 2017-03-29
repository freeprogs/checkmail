#!/usr/bin/env python3

import unittest
from unittest.mock import patch
import io

import sys
sys.path.append('..')
from checkmail import AccViewerHandler


class AccViewerHandlerGoodInput(unittest.TestCase):

    def setUp(self):
        sys.stdout = io.StringIO()
        self.p1 = patch('checkmail.input', create=True)
        self.p2 = patch('os.system')
        self.m1 = self.p1.start()
        self.m2 = self.p2.start()

    def tearDown(self):
        self.p1.stop()
        self.p2.stop()

    def read_output(self):
        sys.stdout.seek(0)
        return sys.stdout.read()

    def test_can_print_one_account(self):

        def check(lst):
            handler = AccViewerHandler()
            handler.start('h', 3, 4, 'm')
            handler.print_pages(lst)
            handler.end()
            output = self.read_output()
            return output

        def match(s):
            return '1 a\n         "c" at "b"' in s

        i = [('a', 'b', 'c')]
        o = check(i)
        self.assertTrue(match(o), msg=(i, o))

    def test_can_print_several_accounts(self):

        def check(lst):
            handler = AccViewerHandler()
            handler.start('h', 3, 4, 'm')
            handler.print_pages(lst)
            handler.end()
            output = self.read_output()
            return output

        def match(s):
            res = ('1 a1\n         "c1" at "b1"' in s,
                   '2 a2\n         "c2" at "b2"' in s,
                   '3 a3\n         "c3" at "b3"' in s)
            return all(res)

        i = [('a1', 'b1', 'c1'),
             ('a2', 'b2', 'c2'),
             ('a3', 'b3', 'c3')]
        o = check(i)
        self.assertTrue(match(o), msg=(i, o))

    def test_will_print_newlines_when_no_accounts(self):

        def check(lst):
            handler = AccViewerHandler()
            handler.start('h', 3, 4, 'm')
            handler.print_pages(lst)
            handler.end()
            output = self.read_output()
            return output

        def match(s):
            res = ('h\n' + '\n' * 9 in s,)
            return all(res)

        i = []
        o = check(i)
        self.assertTrue(match(o), msg=(i, o))

    def test_will_replace_absent_accounts_by_newlines(self):

        def check(lst):
            handler = AccViewerHandler()
            handler.start('h', 3, 4, 'm')
            handler.print_pages(lst)
            handler.end()
            output = self.read_output()
            return output

        def match(s):
            res = ('1 a1\n         "c1" at "b1"' in s,
                   'at "b1"\n' + '\n' * 6 in s)
            return all(res)

        i = [('a1', 'b1', 'c1')]
        o = check(i)
        self.assertTrue(match(o), msg=(i, o))

        def match(s):
            res = ('1 a1\n         "c1" at "b1"' in s,
                   '2 a2\n         "c2" at "b2"' in s,
                   'at "b2"\n' + '\n' * 3 in s)
            return all(res)

        i = [('a1', 'b1', 'c1'),
             ('a2', 'b2', 'c2')]
        o = check(i)
        self.assertTrue(match(o), msg=(i, o))

    def test_can_have_multiline_header(self):

        i = 'h1\nh2'
        handler = AccViewerHandler()
        handler.start(i, 3, 4, 'm')
        handler.print_pages([('a', 'b', 'c')])
        handler.end()
        o = self.read_output()

        def match(s):
            res = (s.startswith(i),
                   '1 a\n         "c" at "b"' in s)
            return all(res)

        self.assertTrue(match(o), msg=(i, o))

    def test_can_have_unicode_chars_in_header(self):

        i = 'h深'
        handler = AccViewerHandler()
        handler.start(i, 3, 4, 'm')
        handler.print_pages([('a', 'b', 'c')])
        handler.end()
        o = self.read_output()

        def match(s):
            res = (s.startswith(i),
                   '1 a\n         "c" at "b"' in s)
            return all(res)

        self.assertTrue(match(o), msg=(i, o))

    def test_will_print_header_on_every_page(self):

        def check(lst):
            handler = AccViewerHandler()
            handler.start('h', 3, 4, 'm')
            handler.print_pages(lst)
            handler.end()
            output = self.read_output()
            return output

        def match(s):
            res = ('1 a1\n         "c1" at "b1"' in s,
                   '9 a9\n         "c9" at "b9"' in s,
                   s.count('h') == 3)
            return all(res)

        i = [('a1', 'b1', 'c1'),
             ('a2', 'b2', 'c2'),
             ('a3', 'b3', 'c3'),
             ('a4', 'b4', 'c4'),
             ('a5', 'b5', 'c5'),
             ('a6', 'b6', 'c6'),
             ('a7', 'b7', 'c7'),
             ('a8', 'b8', 'c8'),
             ('a9', 'b9', 'c9')]
        o = check(i)
        self.assertTrue(match(o), msg=(i, o))

    def test_can_have_multiline_message(self):

        i = 'm1\nm2'
        handler = AccViewerHandler()
        handler.start('h', 3, 4, i)
        handler.print_pages([('a', 'b', 'c')])
        handler.end()
        o = self.read_output()

        def match(s):
            res = ('1 a\n         "c" at "b"' in s,
                   s.endswith(i + '\n'))
            return all(res)

        self.assertTrue(match(o), msg=(i, o))

    def test_can_have_unicode_chars_in_message(self):

        i = 'm深'
        handler = AccViewerHandler()
        handler.start('h', 3, 4, i)
        handler.print_pages([('a', 'b', 'c')])
        handler.end()
        o = self.read_output()

        def match(s):
            res = ('1 a\n         "c" at "b"' in s,
                   s.endswith(i + '\n'))
            return all(res)

        self.assertTrue(match(o), msg=(i, o))

    def test_will_print_message_on_every_page(self):

        def check(lst):
            handler = AccViewerHandler()
            handler.start('h', 3, 4, 'm')
            handler.print_pages(lst)
            handler.end()
            output = self.read_output()
            return output

        def match(s):
            res = ('1 a1\n         "c1" at "b1"' in s,
                   '9 a9\n         "c9" at "b9"' in s,
                   s.count('m') == 3)
            return all(res)

        i = [('a1', 'b1', 'c1'),
             ('a2', 'b2', 'c2'),
             ('a3', 'b3', 'c3'),
             ('a4', 'b4', 'c4'),
             ('a5', 'b5', 'c5'),
             ('a6', 'b6', 'c6'),
             ('a7', 'b7', 'c7'),
             ('a8', 'b8', 'c8'),
             ('a9', 'b9', 'c9')]
        o = check(i)
        self.assertTrue(match(o), msg=(i, o))

    def test_can_print_total_number_of_accounts(self):

        def check(lst):
            handler = AccViewerHandler()
            handler.start('h', 3, 4, 'm')
            handler.print_pages(lst)
            handler.end()
            output = self.read_output()
            return output

        i = []
        o = check(i)
        self.assertTrue('of 0\n' in o, msg=(i, o))

        i = [('a1', 'b1', 'c1'),
             ('a2', 'b2', 'c2'),
             ('a3', 'b3', 'c3')]
        o = check(i)
        self.assertTrue('of 3\n' in o, msg=(i, o))

        i = [('a1', 'b1', 'c1'),
             ('a2', 'b2', 'c2'),
             ('a3', 'b3', 'c3'),
             ('a4', 'b4', 'c4')]
        o = check(i)
        self.assertTrue('of 4\n' in o, msg=(i, o))

    def test_prints_correct_number_of_pages_for_accounts(self):

        def check(lst):
            handler = AccViewerHandler()
            handler.start('h', 3, 4, 'm')
            handler.print_pages(lst)
            handler.end()
            output = self.read_output()
            return output

        i = [('a1', 'b1', 'c1'),
             ('a2', 'b2', 'c2'),
             ('a3', 'b3', 'c3')]
        o = check(i)
        self.assertTrue(' page 1/1 of ' in o, msg=(i, o))

        i = [('a1', 'b1', 'c1'),
             ('a2', 'b2', 'c2'),
             ('a3', 'b3', 'c3'),
             ('a4', 'b4', 'c4'),
             ('a5', 'b5', 'c5'),
             ('a6', 'b6', 'c6'),
             ('a7', 'b7', 'c7'),
             ('a8', 'b8', 'c8'),
             ('a9', 'b9', 'c9')]
        o = check(i)
        self.assertTrue(' page 1/3 of ' in o, msg=(i, o))
        self.assertTrue(' page 2/3 of ' in o, msg=(i, o))
        self.assertTrue(' page 3/3 of ' in o, msg=(i, o))

    def test_will_put_excess_account_on_next_page(self):

        def check(lst):
            handler = AccViewerHandler()
            handler.start('h', 3, 4, 'm')
            handler.print_pages(lst)
            handler.end()
            output = self.read_output()
            return output

        i = [('a1', 'b1', 'c1'),
             ('a2', 'b2', 'c2'),
             ('a3', 'b3', 'c3')]
        o = check(i)
        self.assertTrue(' page 1/1 of ' in o, msg=(i, o))

        i = [('a1', 'b1', 'c1'),
             ('a2', 'b2', 'c2'),
             ('a3', 'b3', 'c3'),
             ('a4', 'b4', 'c4')]
        o = check(i)
        self.assertTrue('h\n   4 a4\n         "c4" at "b4"' in o, msg=(i, o))
        self.assertTrue(' page 1/2 of ' in o, msg=(i, o))
        self.assertTrue(' page 2/2 of ' in o, msg=(i, o))

    def test_will_replace_to_unknown_empty_account_name(self):

        i = [(None, 'b', 'c')]
        handler = AccViewerHandler()
        handler.start('h', 3, 4, 'm')
        handler.print_pages(i)
        handler.end()
        o = self.read_output()

        def match(s):
            res = ('1 Unknown\n         "c" at "b"' in s,)
            return all(res)

        self.assertTrue(match(o), msg=(i, o))

    def test_will_replace_to_none_empty_server_name(self):

        i = [('a', None, 'c')]
        handler = AccViewerHandler()
        handler.start('h', 3, 4, 'm')
        handler.print_pages(i)
        handler.end()
        o = self.read_output()

        def match(s):
            res = ('1 a\n         "c" at None' in s,)
            return all(res)

        self.assertTrue(match(o), msg=(i, o))

    def test_will_replace_to_none_empty_user_name(self):

        i = [('a', 'b', None)]
        handler = AccViewerHandler()
        handler.start('h', 3, 4, 'm')
        handler.print_pages(i)
        handler.end()
        o = self.read_output()

        def match(s):
            res = ('1 a\n         None at "b"' in s,)
            return all(res)

        self.assertTrue(match(o), msg=(i, o))

    def test_will_align_equally_account_numbers(self):

        def check(lst):
            handler = AccViewerHandler()
            handler.start('h', 3, 4, 'm')
            handler.print_pages(lst)
            handler.end()
            output = self.read_output()
            return output

        def match(s):
            res = ('\n   1 a1\n         "c1" at "b1"' in s,
                   '\n   2 a2\n         "c2" at "b2"' in s,
                   '\n   3 a3\n         "c3" at "b3"' in s,
                   ' page 1/2 of ' in s,
                   '\n   4 a4\n         "c4" at "b4"' in s,
                   ' page 2/2 of ' in s)
            return all(res)

        i = [('a1', 'b1', 'c1'),
             ('a2', 'b2', 'c2'),
             ('a3', 'b3', 'c3'),
             ('a4', 'b4', 'c4')]
        o = check(i)
        self.assertTrue(match(o), msg=(i, o))

    def test_can_accept_generator_with_accounts(self):

        def check(lst):
            handler = AccViewerHandler()
            handler.start('h', 3, 4, 'm')
            handler.print_pages(lst)
            handler.end()
            output = self.read_output()
            return output

        def match(s):
            return '1 a\n         "c" at "b"' in s

        i = (i for i in [('a', 'b', 'c')])
        o = check(i)
        self.assertTrue(match(o), msg=(i, o))


class AccViewerHandlerBadInput(unittest.TestCase):

    def setUp(self):
        sys.stdout = io.StringIO()
        self.p1 = patch('checkmail.input', create=True)
        self.p2 = patch('os.system')
        self.m1 = self.p1.start()
        self.m2 = self.p2.start()

    def tearDown(self):
        self.p1.stop()
        self.p2.stop()

    def read_output(self):
        sys.stdout.seek(0)
        return sys.stdout.read()

    def test_raise_on_negative_page_size(self):

        i = -1
        handler = AccViewerHandler()
        with self.assertRaises(ValueError, msg=i):
            handler.start('h', i, 4, 'm')
            handler.end()

    def test_raise_on_zero_page_size(self):

        i = 0
        handler = AccViewerHandler()
        with self.assertRaises(ValueError, msg=i):
            handler.start('h', i, 4, 'm')
            handler.end()

    def test_raise_on_negative_width_of_account_number(self):

        i = -1
        handler = AccViewerHandler()
        with self.assertRaises(ValueError, msg=i):
            handler.start('h', 3, i, 'm')
            handler.end()


if __name__ == '__main__':
    unittest.main()
