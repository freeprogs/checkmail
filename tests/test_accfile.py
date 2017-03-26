#!/usr/bin/env python3

import unittest
from unittest.mock import patch

import sys
sys.path.append('..')
from mail import (AccFileNoFileError,
                  AccFileNotFileError,
                  AccFileFieldsError,
                  AccFileHandler)


class ReadFileGoodInput(unittest.TestCase):

    def setUp(self):
        self.p1 = patch('os.path')
        self.p2 = patch('mail.open', create=True)
        self.m1 = self.p1.start()
        self.m1.exists.return_value = True
        self.m1.isfile.return_value = True
        self.m2 = self.p2.start()
        self.open_iter = \
            self.m2.return_value. \
            __enter__.return_value.__iter__

    def tearDown(self):
        self.p1.stop()
        self.p2.stop()

    def test_field_contents_in_one_line(self):

        def checkl(ls):
            self.open_iter.reset_mock()
            self.open_iter.return_value = ls

            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', ':', 5,
                                 'password', 4)
            afh.start()
            afh.load_accounts()
            afh.end()

        lst = (
           '::::',
           'a::::',
           ':b:::',
           '::c::',
           ':::d:',
           '::::e',

           'a:b:::',
           'a:b:c::',
           'a:b:c:d:',
           'a:b:c:d:e',

           'aaa:bbb:ccc:ddd:eee',
           'aa aa:bb bb:cc cc:dd dd:ee ee',
           ' aa : bb : cc : dd : ee '
        )

        for i in lst:
            try:
                checkl([i])
            except:
                self.fail(repr(i))

    def test_field_contents_in_several_lines(self):

        def checkl(ls):
            self.open_iter.reset_mock()
            self.open_iter.return_value = ls

            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', ':', 5,
                                 'password', 4)
            afh.start()
            afh.load_accounts()
            afh.end()

        lst = (
            ['::::', '::::'],
            ['a:b:c:d:e', 'a:b:c:d:e'],
            ['aa:bb:cc:dd:ee', 'aa:bb:cc:dd:ee'],
            ['aa aa:bb bb:cc cc:dd dd:ee ee',
             'aa aa:bb bb:cc cc:dd dd:ee ee'],

            ['::::', '::::', '::::'],
            ['a:b:c:d:e', 'a:b:c:d:e', 'a:b:c:d:e'],
            ['aa:bb:cc:dd:ee', 'aa:bb:cc:dd:ee', 'aa:bb:cc:dd:ee'],
            ['aa aa:bb bb:cc cc:dd dd:ee ee',
             'aa aa:bb bb:cc cc:dd dd:ee ee',
             'aa aa:bb bb:cc cc:dd dd:ee ee'],
        )

        for i in lst:
            try:
                checkl(i)
            except:
                self.fail(i)

    def test_fields_quantity_corresponds_to_lines(self):

        def checkln(ls, n):
            self.open_iter.reset_mock()
            self.open_iter.return_value = ls

            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', ':', n,
                                 'password', 4)
            afh.start()
            afh.load_accounts()
            afh.end()

        lst = (
            (0, ['']),
            (1, ['a']),
            (2, [':']),
            (3, ['::']),
            (4, [':::']),
            (5, ['::::']),
            (6, [':::::']),
            (7, ['::::::']),
            (8, [':::::::']),
            (9, ['::::::::']),
            (10, [':::::::::']),

            (0, ['', '']),
            (1, ['a', 'a']),
            (2, [':', ':']),
            (3, ['::', '::']),
            (4, [':::', ':::']),
            (5, ['::::', '::::']),
            (6, [':::::', ':::::']),
            (7, ['::::::', '::::::']),
            (8, [':::::::', ':::::::']),
            (9, ['::::::::', '::::::::']),
            (10, [':::::::::', ':::::::::']),

            (0, ['', '', '']),
            (1, ['a', 'a', 'a']),
            (2, [':', ':', ':']),
            (3, ['::', '::', '::']),
            (4, [':::', ':::', ':::']),
            (5, ['::::', '::::', '::::']),
            (6, [':::::', ':::::', ':::::']),
            (7, ['::::::', '::::::', '::::::']),
            (8, [':::::::', ':::::::', ':::::::']),
            (9, ['::::::::', '::::::::', '::::::::']),
            (10, [':::::::::', ':::::::::', ':::::::::']),
        )

        for n, i in lst:
            try:
                checkln(i, n)
            except:
                self.fail((n, i))

    def test_fields_with_another_delimiter(self):

        def checkld(ls, d):
            self.open_iter.reset_mock()
            self.open_iter.return_value = ls

            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', d, 3,
                                 'password', 4)
            afh.start()
            lst = afh.load_accounts()
            afh.end()
            return lst

        lst = (
            (':', ['a:b:c'], [['a', 'b', 'c']]),
            (';', ['a;b;c'], [['a', 'b', 'c']]),
            (',', ['a,b,c'], [['a', 'b', 'c']]),

            (':', ['a:b:c', 'a:b:c'],
                  [['a', 'b', 'c'], ['a', 'b', 'c']]),
            (';', ['a;b;c', 'a;b;c'],
                  [['a', 'b', 'c'], ['a', 'b', 'c']]),
            (',', ['a,b,c', 'a,b,c'],
                  [['a', 'b', 'c'], ['a', 'b', 'c']]),

            (':', ['a:b:c', 'a:b:c', 'a:b:c'],
                  [['a', 'b', 'c'], ['a', 'b', 'c'], ['a', 'b', 'c']]),
            (';', ['a;b;c', 'a;b;c', 'a;b;c'],
                  [['a', 'b', 'c'], ['a', 'b', 'c'], ['a', 'b', 'c']]),
            (',', ['a,b,c', 'a,b,c', 'a,b,c'],
                  [['a', 'b', 'c'], ['a', 'b', 'c'], ['a', 'b', 'c']]),
        )

        for d, i, o in lst:
            self.assertEqual(checkld(i, d), o, msg=(d, i))

    def test_replace_empty_field_to_constant(self):

        def checkl(ls):
            self.open_iter.reset_mock()
            self.open_iter.return_value = ls

            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', ':', 3,
                                 'password', 4)
            afh.start()
            lst = afh.load_accounts()
            afh.end()
            return lst

        lst = (
            (['::'], [[None, None, None]]),
            (['a::'], [['a', None, None]]),
            ([':a:'], [[None, 'a', None]]),
            (['::a'], [[None, None, 'a']]),
            ([':a:a'], [[None, 'a', 'a']]),
            (['a::a'], [['a', None, 'a']]),
            (['a:a:'], [['a', 'a', None]]),

            (['::', '::'], [[None, None, None],
                            [None, None, None]]),
            (['::', 'a:b:c'], [[None, None, None],
                               ['a', 'b', 'c']]),
            (['a:b:c', '::'], [['a', 'b', 'c'],
                               [None, None, None]]),
        )

        for i, o in lst:
            self.assertEqual(checkl(i), o, msg=i)

    def test_discard_empty_lines(self):

        def checkl(ls):
            self.open_iter.reset_mock()
            self.open_iter.return_value = ls

            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', ':', 3,
                                 'password', 4)
            afh.start()
            lst = afh.load_accounts()
            afh.end()
            return lst

        lst = (
            ([''], []),

            (['', 'a:b:c'], [['a', 'b', 'c']]),
            (['a:b:c', ''], [['a', 'b', 'c']]),

            (['', 'a:b:c', 'd:e:f'], [['a', 'b', 'c'],
                                      ['d', 'e', 'f']]),
            (['a:b:c', '', 'd:e:f'], [['a', 'b', 'c'],
                                      ['d', 'e', 'f']]),
            (['a:b:c', 'd:e:f', ''], [['a', 'b', 'c'],
                                      ['d', 'e', 'f']]),
        )

        for i, o in lst:
            self.assertEqual(checkl(i), o, msg=i)

    def test_discard_whitespace_lines(self):

        def checkl(ls):
            self.open_iter.reset_mock()
            self.open_iter.return_value = ls

            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', ':', 3,
                                 'password', 4)
            afh.start()
            lst = afh.load_accounts()
            afh.end()
            return lst

        lst = (
            ([' '], []),
            (['  '], []),
            (['\t'], []),
            (['\t\t'], []),
            ([' \t'], []),

            ([' ', 'a:b:c'], [['a', 'b', 'c']]),
            (['  ', 'a:b:c'], [['a', 'b', 'c']]),
            (['\t', 'a:b:c'], [['a', 'b', 'c']]),
            (['\t\t', 'a:b:c'], [['a', 'b', 'c']]),
            ([' \t', 'a:b:c'], [['a', 'b', 'c']]),
        )

        for i, o in lst:
            self.assertEqual(checkl(i), o, msg=i)

    def test_discard_commented_lines(self):

        def checkl(ls):
            self.open_iter.reset_mock()
            self.open_iter.return_value = ls

            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', ':', 3,
                                 'password', 4)
            afh.start()
            lst = afh.load_accounts()
            afh.end()
            return lst

        lst = (
            (['# text'], []),
            (['# text', '# text'], []),

            (['# text', 'a:b:c'], [['a', 'b', 'c']]),
            (['a:b:c', '# text'], [['a', 'b', 'c']]),

            (['# text', 'a:b:c', 'd:e:f'], [['a', 'b', 'c'],
                                            ['d', 'e', 'f']]),
            (['a:b:c', '# text', 'd:e:f'], [['a', 'b', 'c'],
                                            ['d', 'e', 'f']]),
            (['a:b:c', 'd:e:f', '# text'], [['a', 'b', 'c'],
                                            ['d', 'e', 'f']]),
        )

        for i, o in lst:
            self.assertEqual(checkl(i), o, msg=i)

    def test_another_comment_indicator(self):

        def checkls(ls, s):
            self.open_iter.reset_mock()
            self.open_iter.return_value = ls

            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', s, ':', 3,
                                 'password', 4)
            afh.start()
            lst = afh.load_accounts()
            afh.end()
            return lst

        lst = (
            ('#', ['# text'], []),
            ('#', ['# text', '# text'], []),
            ('#', ['# text', 'a:b:c'], [['a', 'b', 'c']]),

            ('@', ['@ text'], []),
            ('@', ['@ text', '@ text'], []),
            ('@', ['@ text', 'a:b:c'], [['a', 'b', 'c']]),

            (';', ['; text'], []),
            (';', ['; text', '; text'], []),
            (';', ['; text', 'a:b:c'], [['a', 'b', 'c']]),
        )

        for s, i, o in lst:
            self.assertEqual(checkls(i, s), o, msg=(s, i))

    def test_comment_indicator_with_several_chars(self):

        def checkls(ls, s):
            self.open_iter.reset_mock()
            self.open_iter.return_value = ls

            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', s, ':', 3,
                                 'password', 4)
            afh.start()
            lst = afh.load_accounts()
            afh.end()
            return lst

        lst = (
            ('##', ['## text'], []),
            ('##', ['## text', '## text'], []),
            ('##', ['## text', 'a:b:c'], [['a', 'b', 'c']]),

            (' x ', [' x  text'], []),
            (' x ', [' x  text', ' x  text'], []),
            (' x ', [' x  text', 'a:b:c'], [['a', 'b', 'c']]),
        )

        for s, i, o in lst:
            self.assertEqual(checkls(i, s), o, msg=(s, i))

    def test_discard_whitespace_and_commented_lines(self):

        def checkl(ls):
            self.open_iter.reset_mock()
            self.open_iter.return_value = ls

            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', ':', 3,
                                 'password', 4)
            afh.start()
            lst = afh.load_accounts()
            afh.end()
            return lst

        lst = (
            ([' # text'], []),
            (['  # text'], []),
            ([' # text', 'a:b:c'], [['a', 'b', 'c']]),
            (['  # text', 'a:b:c'], [['a', 'b', 'c']]),
        )

        for i, o in lst:
            self.assertEqual(checkl(i), o, msg=i)

class ReadFileBadInput(unittest.TestCase):

    def setUp(self):
        self.p1 = patch('os.path')
        self.p2 = patch('mail.open', create=True)
        self.m1 = self.p1.start()
        self.m1.exists.return_value = True
        self.m1.isfile.return_value = True
        self.m2 = self.p2.start()
        self.open_iter = \
            self.m2.return_value. \
            __enter__.return_value.__iter__

    def tearDown(self):
        self.p1.stop()
        self.p2.stop()

    def test_file_doesnt_exist(self):
        self.m1.exists.reset_mock()
        self.m1.exists.return_value = False

        afh = AccFileHandler('prog', 'version',
                             'filename',
                             'utf-8', '#', ':', 5,
                             'password', 4)
        afh.start()
        self.assertRaises(AccFileNoFileError, afh.load_accounts)
        afh.end()

    def test_file_isnt_a_file(self):
        self.m1.isfile.reset_mock()
        self.m1.isfile.return_value = False

        afh = AccFileHandler('prog', 'version',
                             'filename',
                             'utf-8', '#', ':', 5,
                             'password', 4)
        afh.start()
        self.assertRaises(AccFileNotFileError, afh.load_accounts)
        afh.end()

    def test_incorrect_fields_quantity_in_one_line(self):

        def checkl(ls):
            self.open_iter.reset_mock()
            self.open_iter.return_value = ls

            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', ':', 5,
                                 'password', 4)
            afh.start()
            afh.load_accounts()
            afh.end()

        lst = (
            ':',
            '::',
            ':::',
            ':::::',
            '::::::',

            'a',
            'a:',
            'a:b',
            'a:b:',
            'a:b:c',
            'a:b:c:',
            'a:b:c:d',
            'a:b:c:d:e:',
            'a:b:c:d:e:f',
        )

        for i in lst:
            with self.assertRaises(AccFileFieldsError, msg=repr(i)):
                checkl([i])

    def test_incorrect_fields_quantity_in_several_lines(self):

        def checkl(ls):
            self.open_iter.reset_mock()
            self.open_iter.return_value = ls

            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', ':', 5,
                                 'password', 4)
            afh.start()
            afh.load_accounts()
            afh.end()

        lst = (
            ['::::', ':::::'],
            ['a:b:c:d:e', 'a:b:c:d:e:f'],
            ['::::', '::::', ':::::'],
            ['a:b:c:d:e', 'a:b:c:d:e', 'a:b:c:d:e:f'],
        )

        for i in lst:
            with self.assertRaises(AccFileFieldsError, msg=i):
                checkl(i)

    def test_fields_quantity_doesnt_correspond_to_lines(self):

        def checkln(ls, n):
            self.open_iter.reset_mock()
            self.open_iter.return_value = ls

            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', ':', n,
                                 'password', 4)
            afh.start()
            afh.load_accounts()
            afh.end()

        lst = (
            (0, ['a']),
            (1, [':']),
            (2, ['a']),
            (2, ['::']),
            (3, [':']),
            (3, [':::']),
            (4, ['::']),
            (4, ['::::']),
            (5, [':::']),
            (5, [':::::']),
            (6, ['::::']),
            (6, ['::::::']),
            (7, [':::::']),
            (7, [':::::::']),
            (8, ['::::::']),
            (8, ['::::::::']),
            (9, [':::::::']),
            (9, [':::::::::']),
            (10, ['::::::::']),
            (10, ['::::::::::']),

            (0, ['', 'a']),
            (1, ['a', ':']),
            (2, [':', 'a']),
            (2, [':', '::']),
            (3, ['::', ':']),
            (3, ['::', ':::']),
            (4, [':::', '::']),
            (4, [':::', '::::']),
            (5, ['::::', ':::']),
            (5, ['::::', ':::::']),
            (6, [':::::', '::::']),
            (6, [':::::', '::::::']),
            (7, ['::::::', ':::::']),
            (7, ['::::::', ':::::::']),
            (8, [':::::::', '::::::']),
            (8, [':::::::', '::::::::']),
            (9, ['::::::::', ':::::::']),
            (9, ['::::::::', ':::::::::']),
            (10, [':::::::::', '::::::::']),
            (10, [':::::::::', '::::::::::']),

            (0, ['', '', 'a']),
            (1, ['a', 'a', ':']),
            (2, [':', ':', 'a']),
            (2, [':', ':', '::']),
            (3, ['::', '::', ':']),
            (3, ['::', '::', ':::']),
            (4, [':::', ':::', '::']),
            (4, [':::', ':::', '::::']),
            (5, ['::::', '::::', ':::']),
            (5, ['::::', '::::', ':::::']),
            (6, [':::::', ':::::', '::::']),
            (6, [':::::', ':::::', '::::::']),
            (7, ['::::::', '::::::', ':::::']),
            (7, ['::::::', '::::::', ':::::::']),
            (8, [':::::::', ':::::::', '::::::']),
            (8, [':::::::', ':::::::', '::::::::']),
            (9, ['::::::::', '::::::::', ':::::::']),
            (9, ['::::::::', '::::::::', ':::::::::']),
            (10, [':::::::::', ':::::::::', '::::::::']),
            (10, [':::::::::', ':::::::::', '::::::::::']),
        )

        for n, i in lst:
            with self.assertRaises(AccFileFieldsError, msg=(n, i)):
                checkln(i, n)

class WriteFileGoodInput(unittest.TestCase):

    def setUp(self):
        self.p = patch('mail.open', create=True)
        self.m = self.p.start()
        self.ostream = \
            self.m.return_value. \
            __enter__.return_value

    def tearDown(self):
        self.p.stop()

    def test_comment_program_name(self):

        def checkname(name):
            self.m.reset_mock()
            afh = AccFileHandler(name, 'version',
                                 'filename',
                                 'utf-8', '#', ':', 5,
                                 'password', 4)
            afh.start()
            afh.save_accounts([])
            afh.end()
            out = self.ostream.mock_calls[0][1][0]
            return out

        lst = (
            ('x', '# This is the config file of x version\n'),
            ('xx', '# This is the config file of xx version\n'),
            ('x x', '# This is the config file of x x version\n'),
            ('xx xx', '# This is the config file of xx xx version\n'),
        )

        for i, o in lst:
            self.assertEqual(checkname(i), o, msg=repr(i))

    def test_comment_program_version(self):

        def checkver(ver):
            self.m.reset_mock()
            afh = AccFileHandler('prog', ver,
                                 'filename',
                                 'utf-8', '#', ':', 5,
                                 'password', 4)
            afh.start()
            afh.save_accounts([])
            afh.end()
            out = self.ostream.mock_calls[0][1][0]
            return out

        lst = (
            ('1', '# This is the config file of prog 1\n'),
            ('11', '# This is the config file of prog 11\n'),
            ('11 11', '# This is the config file of prog 11 11\n'),
            ('1.1.1', '# This is the config file of prog 1.1.1\n'),
        )

        for i, o in lst:
            self.assertEqual(checkver(i), o, msg=repr(i))

    def test_no_accounts_exist(self):

        def checka(acs):
            self.m.reset_mock()
            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', ':', 5,
                                 'password', 4)
            afh.start()
            afh.save_accounts(acs)
            afh.end()
            out = [i[1][0] for i in self.ostream.mock_calls]
            out = out[2:] # remove comment
            return out

        self.assertEqual(checka([]), [])

    def test_one_account_exists(self):

        def checka(acs):
            self.m.reset_mock()
            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', ':', 3,
                                 'password', 4)
            afh.start()
            afh.save_accounts(acs)
            afh.end()
            out = [i[1][0] for i in self.ostream.mock_calls]
            out = out[2:] # remove comment
            return out

        lst = (
            ([['a', 'b', 'c']],
             ['a:b:c\n']),
            ([['aa', 'bb', 'cc']],
             ['aa:bb:cc\n']),
            ([['aa aa', 'bb bb', 'cc cc']],
             ['aa aa:bb bb:cc cc\n']),
        )

        for i, o in lst:
            self.assertEqual(checka(i), o, msg=i)

    def test_several_accounts_exist(self):

        def checka(acs):
            self.m.reset_mock()
            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', ':', 3,
                                 'password', 4)
            afh.start()
            afh.save_accounts(acs)
            afh.end()
            out = [i[1][0] for i in self.ostream.mock_calls]
            out = out[2:] # remove comment
            return out

        lst = (
            ([['a', 'b', 'c'], ['a', 'b', 'c']],
             ['a:b:c\n', 'a:b:c\n']),
            ([['a', 'b', 'c'], ['a', 'b', 'c'], ['a', 'b', 'c']],
             ['a:b:c\n', 'a:b:c\n', 'a:b:c\n']),
        )

        for i, o in lst:
            self.assertEqual(checka(i), o, msg=i)

    def test_fields_with_another_delimiter(self):

        def checkad(acs, d):
            self.m.reset_mock()
            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', d, 3,
                                 'password', 4)
            afh.start()
            afh.save_accounts(acs)
            afh.end()
            out = [i[1][0] for i in self.ostream.mock_calls]
            out = out[2:] # remove comment
            return out

        lst = (
            (':', [['a', 'b', 'c']], ['a:b:c\n']),
            (';', [['a', 'b', 'c']], ['a;b;c\n']),
            (',', [['a', 'b', 'c']], ['a,b,c\n']),
        )

        for d, i, o in lst:
            self.assertEqual(checkad(i, d), o, msg=(d, i))

    def test_another_fields_quantity(self):

        def checkan(acs, n):
            self.m.reset_mock()
            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', ':', n,
                                 'password', 4)
            afh.start()
            afh.save_accounts(acs)
            afh.end()
            out = [i[1][0] for i in self.ostream.mock_calls]
            out = out[2:] # remove comment
            return out

        lst = (
            (0, [], []),
            (1, [['a']], ['a\n']),
            (2, [['a', 'b']], ['a:b\n']),
            (3, [['a', 'b', 'c']], ['a:b:c\n']),
            (4, [['a', 'b', 'c', 'd']], ['a:b:c:d\n']),
            (5, [['a', 'b', 'c', 'd', 'e']], ['a:b:c:d:e\n']),
        )

        for n, i, o in lst:
            self.assertEqual(checkan(i, n), o, msg=(n, i))

    def test_limit_fields_quantity_min(self):

        def checkan(acs, n):
            self.m.reset_mock()
            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', ':', n,
                                 'password', 4)
            afh.start()
            afh.save_accounts(acs)
            afh.end()
            out = [i[1][0] for i in self.ostream.mock_calls]
            out = out[2:] # remove comment
            return out

        self.assertEqual(checkan([], 0), [])

    def test_limit_fields_quantity_max(self):

        def checkan(acs, n):
            self.m.reset_mock()
            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', ':', n,
                                 'password', 4)
            afh.start()
            afh.save_accounts(acs)
            afh.end()
            out = [i[1][0] for i in self.ostream.mock_calls]
            out = out[2:] # remove comment
            return out

        i = [['a' for _ in range(10000)]]
        o = [(':'.join(it) + '\n') for it in i]
        self.assertEqual(checkan(i, 10000), o)

    def test_limit_accounts_quantity_min(self):

        def checka(acs):
            self.m.reset_mock()
            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', ':', 3,
                                 'password', 4)
            afh.start()
            afh.save_accounts(acs)
            afh.end()
            out = [i[1][0] for i in self.ostream.mock_calls]
            out = out[2:] # remove comment
            return out

        self.assertEqual(checka([]), [])

    def test_limit_accounts_quantity_max(self):

        def checka(acs):
            self.m.reset_mock()
            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', ':', 3,
                                 'password', 4)
            afh.start()
            afh.save_accounts(acs)
            afh.end()
            out = [i[1][0] for i in self.ostream.mock_calls]
            out = out[2:] # remove comment
            return out

        i = [['a', 'b', 'c'] for _ in range(10000)]
        o = [':'.join(it) + '\n' for it in i]
        self.assertEqual(checka(i), o)

class WriteFileBadInput(unittest.TestCase):

    def setUp(self):
        self.p = patch('mail.open', create=True)
        self.m = self.p.start()
        self.ostream = \
            self.m.return_value. \
            __enter__.return_value

    def tearDown(self):
        self.p.stop()

    def test_incorrect_fields_quantity(self):

        def checkan(acs, n):
            self.m.reset_mock()
            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', ':', n,
                                 'password', 4)
            afh.start()
            afh.save_accounts(acs)
            afh.end()

        lst = (
            (0, [['a']]),
            (1, [[]]),
            (1, [['a', 'b']]),
            (2, [['a']]),
            (2, [['a', 'b', 'c']]),
            (3, [['a', 'b']]),
            (3, [['a', 'b', 'c', 'd']]),
        )

        for n, i in lst:
            with self.assertRaises(AccFileFieldsError, msg=(n, i)):
                checkan(i, n)

    def test_incorrect_fields_quantity_initial(self):

        def checkf(n):
            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', ':', n,
                                 'password', 4)
            afh.start()
            afh.end()

        self.assertRaises(ValueError, checkf, -1)

class AccountEncryptionGoodInput(unittest.TestCase):

    def setUp(self):
        self.p = patch('mail.PasswordHandler')
        self.m = self.p.start()
        self.m.return_value.encrypt_sum = \
            lambda s, p: '<{}>{}'.format((p, 'password')[p is None], s)
        self.m.return_value.encode = \
            lambda s: '<enc>' + s
        self.m.return_value.decrypt_sum = \
            lambda s, p: '<{}>{}'.format((p, 'password')[p is None], s)
        self.m.return_value.decode = \
            lambda s: '<dec>' + s

    def tearDown(self):
        self.p.stop()

    def test_encrypt(self):

        def checkap(a, p):
            acopy = a[:]
            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', ':', 5,
                                 'password', 4)
            afh.start()
            afh.encrypt_account(acopy, p)
            afh.end()
            return acopy

        lst = (
            (['a', 'b', 'c', 'd', 'e'],
             None,
             ['a', 'b', 'c', 'd', '<enc><password>e']),
            (['a', 'b', 'c', 'd', 'e'],
             '',
             ['a', 'b', 'c', 'd', '<enc><>e']),
            (['a', 'b', 'c', 'd', 'e'],
             'x',
             ['a', 'b', 'c', 'd', '<enc><x>e']),
            (['a', 'b', 'c', 'd', 'e'],
             'x x',
             ['a', 'b', 'c', 'd', '<enc><x x>e']),
        )

        for i, p, o in lst:
            self.assertEqual(checkap(i, p), o, msg=(i, p))

    def test_decrypt(self):

        def checkap(a, p):
            acopy = a[:]
            afh = AccFileHandler('prog', 'version',
                                 'filename',
                                 'utf-8', '#', ':', 5,
                                 'password', 4)
            afh.start()
            afh.decrypt_account(acopy, p)
            afh.end()
            return acopy

        lst = (
            (['a', 'b', 'c', 'd', 'e'],
             None,
             ['a', 'b', 'c', 'd', '<password><dec>e']),
            (['a', 'b', 'c', 'd', 'e'],
             '',
             ['a', 'b', 'c', 'd', '<><dec>e']),
            (['a', 'b', 'c', 'd', 'e'],
             'x',
             ['a', 'b', 'c', 'd', '<x><dec>e']),
            (['a', 'b', 'c', 'd', 'e'],
             'x x',
             ['a', 'b', 'c', 'd', '<x x><dec>e']),
        )

        for i, p, o in lst:
            self.assertEqual(checkap(i, p), o, msg=(i, p))

class AccountEncryptionBadInput(unittest.TestCase):

    def setUp(self):
        self.p = patch('mail.PasswordHandler')
        self.m = self.p.start()
        self.m.return_value.encrypt_sum = \
            lambda s, p: '<{}>{}'.format((p, 'password')[p is None], s)
        self.m.return_value.encode = \
            lambda s: '<enc>' + s
        self.m.return_value.decrypt_sum = \
            lambda s, p: '<{}>{}'.format((p, 'password')[p is None], s)
        self.m.return_value.decode = \
            lambda s: '<dec>' + s

    def tearDown(self):
        self.p.stop()

    def test_incorrect_encrypt_field_quantity(self):

        afh = AccFileHandler('prog', 'version',
                             'filename',
                             'utf-8', '#', ':', 5,
                             'password', 4)
        afh.start()
        self.assertRaises(IndexError,
                          afh.encrypt_account,
                          ['a', 'b', 'c', 'd'],
                          'password')
        afh.end()

    def test_incorrect_decrypt_field_quantity(self):

        afh = AccFileHandler('prog', 'version',
                             'filename',
                             'utf-8', '#', ':', 5,
                             'password', 4)
        afh.start()
        self.assertRaises(IndexError,
                          afh.decrypt_account,
                          ['a', 'b', 'c', 'd'],
                          'password')
        afh.end()


if __name__ == '__main__':
    unittest.main()
