#!/usr/bin/env python3

import unittest

import sys
sys.path.append('..')
from checkmail import HeadersHandler


class HeadersHandlerGoodInput(unittest.TestCase):

    def test_filter_plain_ascii(self):

        def checkhs(hl, sl):
            hh = HeadersHandler()
            hh.start(hl)
            out = hh.filter(sl)
            hh.end()
            return out

        lst = (
            ([b'a: b'],
             ['a'],
             ('b',)),
            ([b'a: b', b'c: d'],
             ['a', 'c'],
             ('b', 'd')),
            ([b'a: b', b'c: d', b'e: f'],
             ['a', 'c', 'e'],
             ('b', 'd', 'f')),

            ([b'a: b', b'c: d', b'e: f'],
             ['a'],
             ('b',)),
            ([b'a: b', b'c: d', b'e: f'],
             ['c'],
             ('d',)),
            ([b'a: b', b'c: d', b'e: f'],
             ['e'],
             ('f',)),

            ([b'a: b', b'c: d', b'e: f'],
             ['a', 'c'],
             ('b', 'd')),
            ([b'a: b', b'c: d', b'e: f'],
             ['c', 'e'],
             ('d', 'f')),
            ([b'a: b', b'c: d', b'e: f'],
             ['a', 'e'],
             ('b', 'f')),
            ([b'a: b', b'c: d', b'e: f'],
             ['a', 'c', 'e'],
             ('b', 'd', 'f')),
        )

        for h, s, o in lst:
            self.assertEqual(checkhs(h, s), o, msg=(h, s))

    def test_filter_plain_utf8(self):

        def checkhs(hl, sl):
            hh = HeadersHandler()
            hh.start(hl)
            out = hh.filter(sl)
            hh.end()
            return out

        lst = (
            ([b'a: \xd0\xb0\xd0\xb1\xd0\xb2',
              b'Content-Type: charset=utf-8'],
             ['a'],
             ('абв',)),
            ([b'a: \xd0\xb0\xd0\xb1\xd0\xb2',
              b'b: \xd0\xb3\xd0\xb4\xd0\xb5',
              b'Content-Type: charset=utf-8'],
             ['a', 'b'],
             ('абв', 'где')),
            ([b'a: \xd0\xb0\xd0\xb1\xd0\xb2',
              b'b: \xd0\xb3\xd0\xb4\xd0\xb5',
              b'c: \xd1\x91\xd0\xb6\xd0\xb7',
              b'Content-Type: charset=utf-8'],
             ['a', 'b', 'c'],
             ('абв', 'где', 'ёжз')),
        )

        for h, s, o in lst:
            self.assertEqual(checkhs(h, s), o, msg=(h, s))

    def test_filter_plain_contype_position(self):

        def checkhs(hl, sl):
            hh = HeadersHandler()
            hh.start(hl)
            out = hh.filter(sl)
            hh.end()
            return out

        h = [b'Content-Type: charset=utf-8',
             b'a: \xd0\xb0\xd0\xb1\xd0\xb2']
        s = ['a']
        o = ('абв',)

        self.assertEqual(checkhs(h, s), o, msg=(h, s))

    def test_filter_plain_no_contype(self):

        def checkhs(hl, sl):
            hh = HeadersHandler()
            hh.start(hl)
            out = hh.filter(sl)
            hh.end()
            return out

        lst = (
            ([b'a: \xd0\xb0\xd0\xb1\xd0\xb2'],
             ['a'],
             ('\xd0\xb0\xd0\xb1\xd0\xb2',)),
            ([b'a: \xd0\xb0\xd0\xb1\xd0\xb2',
              b'b: \xd0\xb3\xd0\xb4\xd0\xb5'],
             ['a', 'b'],
             ('\xd0\xb0\xd0\xb1\xd0\xb2',
              '\xd0\xb3\xd0\xb4\xd0\xb5')),
        )

        for h, s, o in lst:
            self.assertEqual(checkhs(h, s), o, msg=(h, s))

    def test_filter_plain_encodings(self):

        def checkte(t, e):
            hl = [
                b'a: ' + t,
                b'Content-Type: charset=' + e.encode('latin1')
            ]
            sl = ['a']
            hh = HeadersHandler()
            hh.start(hl)
            out = hh.filter(sl)
            hh.end()
            return out[0]

        lst = (
            (b'\xd0\xb0\xd0\xb1\xd0\xb2', 'utf-8', 'абв'),
            (b'\xe0\xe1\xe2', 'cp1251', 'абв'),
            (b'\xc1\xc2\xd7', 'koi8-r', 'абв'),
        )

        for i, e, o in lst:
            self.assertEqual(checkte(i, e), o, msg=(i, e))

    def test_filter_mime_encodings(self):

        def checkm(m):
            hl = [b'a: ' + m,
                  b'Content-Type: charset=utf-8']
            sl = ['a']
            hh = HeadersHandler()
            hh.start(hl)
            out = hh.filter(sl)
            hh.end()
            return out[0]

        lst = (
            (b'=?iso-8859-1?q?abc?=', 'abc'),
            (b'=?utf-8?q?=d0=b0=d0=b1=d0=b2?=', 'абв'),
            (b'=?cp1251?q?=e0=e1=e2?=', 'абв'),
            (b'=?koi8-r?q?=c1=c2=d7?=', 'абв'),
        )

        for i, o in lst:
            self.assertEqual(checkm(i), o, msg=i)

    def test_filter_mime_several_chunks(self):

        def checkm(m):
            hl = [
                b'a: ' + m,
                b'Content-Type: charset=utf-8'
            ]
            sl = ['a']
            hh = HeadersHandler()
            hh.start(hl)
            out = hh.filter(sl)
            hh.end()
            return out[0]

        lst = (
            (b'=?utf-8?q?=d0=b0=d0=b1=d0=b2?=' * 2, 'абв' * 2),
            (b'=?utf-8?q?=d0=b0=d0=b1=d0=b2?=' * 3, 'абв' * 3),
            (b'=?utf-8?q?=d0=b0=d0=b1=d0=b2?=' * 4, 'абв' * 4),
            (b'=?utf-8?q?abc=d0=b0=d0=b1=d0=b2?=def' * 2, 'abcабвdef' * 2),
            (b'=?utf-8?q?abc=d0=b0=d0=b1=d0=b2?=def' * 3, 'abcабвdef' * 3),
            (b'=?utf-8?q?abc=d0=b0=d0=b1=d0=b2?=def' * 4, 'abcабвdef' * 4),
        )

        for i, o in lst:
            self.assertEqual(checkm(i), o, msg=i)

    def test_filter_mime_mix_raw_with_chunk(self):

        def checkm(m):
            hl = [
                b'a: ' + m,
                b'Content-Type: charset=utf-8'
            ]
            sl = ['a']
            hh = HeadersHandler()
            hh.start(hl)
            out = hh.filter(sl)
            hh.end()
            return out[0]

        lst = (
            (b'=?utf-8?q?abc=d0=b0=d0=b1=d0=b2?=', 'abcабв'),
            (b'=?utf-8?q?=d0=b0=d0=b1=d0=b2abc?=', 'абвabc'),

            (b'=?utf-8?q?abc=d0=b0=d0=b1=d0=b2?='
             b'=?utf-8?q?=d0=b0=d0=b1=d0=b2?=',
             'abcабвабв'),
            (b'=?utf-8?q?=d0=b0=d0=b1=d0=b2?=abc'
             b'=?utf-8?q?=d0=b0=d0=b1=d0=b2?=',
             'абвabcабв'),
            (b'=?utf-8?q?=d0=b0=d0=b1=d0=b2?='
             b'=?utf-8?q?=d0=b0=d0=b1=d0=b2?=abc',
             'абвабвabc'),
        )

        for i, o in lst:
            self.assertEqual(checkm(i), o, msg=i)

    def test_filter_mime_encmethod_base64(self):

        def checkm(m):
            hl = [
                b'a: ' + m,
                b'Content-Type: charset=utf-8'
            ]
            sl = ['a']
            hh = HeadersHandler()
            hh.start(hl)
            out = hh.filter(sl)
            hh.end()
            return out[0]

        lst = (
            (b'=?iso-8859-1?b?YWJj?=', 'abc'),
            (b'=?utf-8?b?0LDQsdCy?=', 'абв'),
            (b'=?cp1251?b?4OHi?=', 'абв'),
            (b'=?koi8-r?b?wcLX?=', 'абв'),
        )

        for i, o in lst:
            self.assertEqual(checkm(i), o, msg=i)

    def test_filter_mime_initial_contype_decode(self):

        def checkme(m, e):
            hl = [
                b'a: ' + m,
                b'Content-Type: charset=' + e.encode('latin1')
            ]
            sl = ['a']
            hh = HeadersHandler()
            hh.start(hl)
            out = hh.filter(sl)
            hh.end()
            return out[0]

        lst = (
            (b'=?iso-8859-1?q?abc?=\xd0\xb0\xd0\xb1\xd0\xb2',
             'utf-8',
             'abcабв'),
            (b'=?iso-8859-1?q?abc?=def\xd0\xb0\xd0\xb1\xd0\xb2',
             'utf-8',
             'abcdefабв'),
            (b'=?iso-8859-1?q?abc?=\xd0\xb0def\xd0\xb1ghi\xd0\xb2',
             'utf-8',
             'abcаdefбghiв'),
            (b'=?iso-8859-1?q?abc?=\xd0\xb0\xd0\xb1\xd0\xb2def',
             'utf-8',
             'abcабвdef'),

            (b'\xd0\xb0\xd0\xb1\xd0\xb2=?iso-8859-1?q?abc?=',
             'utf-8',
             'абвabc'),
            (b'def\xd0\xb0\xd0\xb1\xd0\xb2=?iso-8859-1?q?abc?=',
             'utf-8',
             'defабвabc'),
            (b'\xd0\xb0def\xd0\xb1ghi\xd0\xb2=?iso-8859-1?q?abc?=',
             'utf-8',
             'аdefбghiвabc'),
            (b'\xd0\xb0\xd0\xb1\xd0\xb2def=?iso-8859-1?q?abc?=',
             'utf-8',
             'абвdefabc'),
            (b'\xd0\xb0\xd0\xb1\xd0\xb2=?iso-8859-1?q?abc?='
             b'\xd0\xb3\xd0\xb4\xd0\xb5',
             'utf-8',
             'абвabcгде'),
            (b'\xd0\xb0\xd0\xb1\xd0\xb2=?iso-8859-1?q?abc?='
             b'\xd0\xb3\xd0\xb4\xd0\xb5=?iso-8859-1?q?def?=',
             'utf-8',
             'абвabcгдеdef'),

            (b'=?iso-8859-1?q?abc?=\xe0\xe1\xe2',
             'cp1251',
             'abcабв'),
            (b'=?utf-8?q?=d0=b0=d0=b1=d0=b2?='
             b'\xd0\xb3\xd0\xb4\xd0\xb5',
             'utf-8',
             'абвгде'),
            (b'=?utf-8?q?=d0=b0=d0=b1=d0=b2?='
             b'\xe3\xe4\xe5',
             'cp1251',
             'абвгде'),
        )

        for h, e, o in lst:
            self.assertEqual(checkme(h, e), o, msg=(h, e))

class HeadersHandlerBadInput(unittest.TestCase):

    def test_filter_plain_incorrect_encoding(self):

        def checkte(t, e):
            hl = [
                b'a: ' + t,
                b'Content-Type: charset=' + e.encode('latin1')
            ]
            sl = ['a']
            hh = HeadersHandler()
            hh.start(hl)
            out = hh.filter(sl)
            hh.end()
            return out[0]

        lst = (
            (b'\xe0\xe1\xe2', 'utf-8'),
            (b'\xc1\xc2\xd7', 'utf-8'),
            (b'\xe0\xe1\xe2', 'ascii'),
            (b'\xc1\xc2\xd7', 'ascii'),
        )

        for i, e in lst:
            with self.assertRaises(UnicodeDecodeError, msg=(i, e)):
                checkte(i, e)

    def test_filter_mime_incorrect_encoding(self):

        def checkm(m):
            hl = [
                b'a: ' + m,
                b'Content-Type: charset=utf-8'
            ]
            sl = ['a']
            hh = HeadersHandler()
            hh.start(hl)
            out = hh.filter(sl)
            hh.end()
            return out[0]

        lst = (
            b'=?utf-8?q?=e0=e1=e2?=',
            b'=?utf-8?q?=c1=c2=d7?=',
            b'=?ascii?q?=e0=e1=e2?=',
            b'=?ascii?q?=c1=c2=d7?=',

            b'=?utf-8?q?=d0=b0=d0=b1=d0=b2?==?utf-8?q?=e0=e1=e2?=',
            b'=?utf-8?q?=e0=e1=e2?==?utf-8?q?=d0=b0=d0=b1=d0=b2?=',
        )

        for i in lst:
            with self.assertRaises(UnicodeDecodeError, msg=i):
                checkm(i)

    def test_filter_plain_unknown_encoding(self):

        def checkte(t, e):
            hl = [
                b'a: ' + t,
                b'Content-Type: charset=' + e.encode('latin1')
            ]
            sl = ['a']
            hh = HeadersHandler()
            hh.start(hl)
            out = hh.filter(sl)
            hh.end()
            return out[0]

        i, e = (b'\xe0\xe1\xe2', 'unknown')

        with self.assertRaises(LookupError, msg=(i, e)):
            checkte(i, e)

    def test_filter_mime_unknown_encoding(self):

        def checkm(m):
            hl = [
                b'a: ' + m,
                b'Content-Type: charset=utf-8'
            ]
            sl = ['a']
            hh = HeadersHandler()
            hh.start(hl)
            out = hh.filter(sl)
            hh.end()
            return out[0]

        i = b'=?unknown?q?=e0=e1=e2?='

        with self.assertRaises(LookupError, msg=i):
            checkm(i)


if __name__ == '__main__':
    unittest.main()
