#!/usr/bin/env python3

import unittest

import sys
sys.path.append('..')
from mail import (PswDecryptError, PasswordHandler)


class PasswordHandlerGoodInput(unittest.TestCase):

    def test_encode_to_base64(self):

        def checks(s):
            ph = PasswordHandler('password', 4)
            ph.start()
            out = ph.encode(s)
            ph.end()
            return out

        lst = (
            ('', ''),
            ('a', 'YQ=='),
            ('b', 'Yg=='),
            ('aa', 'YWE='),
            ('bb', 'YmI='),
            ('a a', 'YSBh'),
            ('b b', 'YiBi'),
        )

        for i, o in lst:
            self.assertEqual(checks(i), o, msg=repr(i))

    def test_decode_from_base64(self):

        def checks(s):
            ph = PasswordHandler('password', 4)
            ph.start()
            out = ph.decode(s)
            ph.end()
            return out

        lst = (
            ('', ''),
            ('YQ==', 'a'),
            ('Yg==', 'b'),
            ('YWE=', 'aa'),
            ('YmI=', 'bb'),
            ('YSBh', 'a a'),
            ('YiBi', 'b b'),
        )

        for i, o in lst:
            self.assertEqual(checks(i), o, msg=repr(i))

    def test_encrypt_with_empty_string(self):

        def checksph(s, p, h):
            ph = PasswordHandler(p, h)
            ph.start()
            out = ph.encrypt_sum(s)
            ph.end()
            return out

        lst = (
            ('', '', 0, 'féKÔï\x8a,;\x88LúYÊ4+.'),
            ('', 'a', 0, '÷n*«\x93\x88:"h\x0fîYv\x80\x99\x16'),
            ('', 'ab', 0, '¦Ã\x0e8\x8f\x15Èº\x1f-\x1a\x19ÉR(<'),
            ('', 'abc', 0, '\x91ÂãE\x96Ï?\xa0m¾%H®ÞZp'),
            ('', '', 4, 'ª#9Ê*\x9ca©/Æ*~^\x04(á'),
            ('', 'a', 4, 'ýÛìL\x94¶PG§í\x07U1\x03êë'),
            ('', 'ab', 4, '(\x0c\x80Kï%ð!Zþ\x8d\x14\x87\x10U°'),
            ('', 'abc', 4, 'Õ;¹:E\x14;\x86<Ê\x1e2WùãÆ'),
        )

        for i, p, h, o,  in lst:
            self.assertEqual(checksph(i, p, h), o, msg=(i, p, h))

    def test_encrypt_with_empty_password(self):

        def checksph(s, p, h):
            ph = PasswordHandler(p, h)
            ph.start()
            out = ph.encrypt_sum(s)
            ph.end()
            return out

        lst = (
            ('', '', 0, 'féKÔï\x8a,;\x88LúYÊ4+.'),
            ('a', '', 0, '.óKÊ&\nå\x98Â\x8d\x9bÁýÔ\x15k'),
            ('ab', '', 0, 'g·\x89\x9eÊá°mâa>±åQÂ5'),
            ('abc', '', 0, 'Ò\x99\x99ê+\x04\x9aç\x9c¸k¢{\x1a_U'),
            ('', '', 4, 'ª#9Ê*\x9ca©/Æ*~^\x04(á'),
            ('a', '', 4, "X\x95'lXPJK\x02ÿ\x02-F[¡â"),
            ('ab', '', 4, '®\x06yp\x12E¶1³\x9e\t\x8f\x07,Ïl'),
            ('abc', '', 4, '@\x1f²¤Ó%ß\x8buü\x80õw³\x1d¢'),
        )

        for i, p, h, o,  in lst:
            self.assertEqual(checksph(i, p, h), o, msg=(i, p, h))

    def test_encrypt_with_hashes(self):

        def checksph(s, p, h):
            ph = PasswordHandler(p, h)
            ph.start()
            out = ph.encrypt_sum(s)
            ph.end()
            return out

        lst = (
            ('a', 'p', 0, 'ø3èëe\x9c3\x89zr\x82\xad;&Ëa'),
            ('a', 'p', 8, "ÚJØI\x90\x95\x8f'öM·+elÒ¤"),
            ('a', 'p', 16,
             '\x1b\x83\x8fÞ\x97\x89\t%\x07XrÎc²´^ø3èëe\x9c3\x89zr\x82\xad;&Ëa'),
            ('ab', 'pq', 0, 'ß\x11X~ævôö\\-ìu¤ß_²'),
            ('ab', 'pq', 8, 'ïÁ¬\x97\x9f×é\x0c\x8cVöëµÐôÃ'),
            ('ab', 'pq', 16,
             '\x99#Ó\x18 XÜ\x9b\nVÇÃ~\x9a¤+ß\x11X~ævôö\\-ìu¤ß_²'),
            ('abc', 'pqr', 0, '·2·<ö\x02\rh3ê¦±\x8b®uU'),
            ('abc', 'pqr', 8, "\x03\x16Â\x9e}Ã9'1´\\\xa0\x94\x95N©"),
            ('abc', 'pqr', 16,
             '\x7fêN¿\x19r\x95»ßßì"¹\x85æu·2·<ö\x02\rh3ê¦±\x8b®uU'),
        )

        for i, p, h, o,  in lst:
            self.assertEqual(checksph(i, p, h), o, msg=(i, p, h))

    def test_encrypt_with_passwords(self):

        def checksph(s, p, h):
            ph = PasswordHandler(p, h)
            ph.start()
            out = ph.encrypt_sum(s)
            ph.end()
            return out

        lst = (
            ('', 'p', 0, 'kKoÑ´ï]ö\x05\x9cS2Ðá_\x95'),
            ('', 'pq', 0, '2is\x1a\x9eT\x9añ@6\x8a\x04Òtÿ\x13'),
            ('', 'pqr', 0, '²\t´Ù\x01ýo\x08Áz²³ö%î/'),
            ('a', 'p', 0, 'ø3èëe\x9c3\x89zr\x82\xad;&Ëa'),
            ('a', 'pq', 0, 'Ft\x00"\x92FP~\x0c¹Ùw0\x14ü{'),
            ('a', 'pqr', 0, "3\x14\x1c\x96\x1f\x89\x8fo¥'ÃAÓ_hê"),
            ('ab', 'p', 0, '\x8fðyiQ=ó·\xad\xa0Í¡\x08\x8dÀ¶'),
            ('ab', 'pq', 0, 'ß\x11X~ævôö\\-ìu¤ß_²'),
            ('ab', 'pqr', 0, '+\x04P1\x9dIBÜûý¶YÃ\x13+²'),
            ('abc', 'p', 0, '¤=_ì3ÅÃ¸ÚÇè8n>\x02ß'),
            ('abc', 'pq', 0, '\x8e¶±>ê¨Ù\rý\x0fG¸Y»º.'),
            ('abc', 'pqr', 0, '·2·<ö\x02\rh3ê¦±\x8b®uU'),

            ('', 'p', 4, 'yg\x96¢\x15ëÃ¦\xad8üõ¼ý\x14Ç'),
            ('', 'pq', 4, 'Æ&\x90Ê\x90jÜën\x8dí3þÁÅÏ'),
            ('', 'pqr', 4, '*\x00ó\x89þçñî\x93\x8bs7\x0by\x9bø'),
            ('a', 'p', 4, 'Äªh\x03\x8dÁ2J¦Q\x17¶\x03ÈD1'),
            ('a', 'pq', 4, 'Ó*\x9eþ%Æ0\x92äçô\x91\x9cêÚÏ'),
            ('a', 'pqr', 4, '\x101&Ý}\x05®D&ìNT\x00\x99$f'),
            ('ab', 'p', 4, 'Û°+1ä\x13øÿ)ÃV£órÈ('),
            ('ab', 'pq', 4, '¨\x00GáruzûÝ\x14VÄ\x03ù\x8bÆ'),
            ('ab', 'pqr', 4, '×\x98à\x7fw¦!ú¬¯ó\x88y*o\x1b'),
            ('abc', 'p', 4, '~\x90BÒ\x99ãÍ1\x88v\x11ë\x01ê\x1a\x90'),
            ('abc', 'pq', 4, '\x8dñiÈ¹w5iYq¹ýt¶\x03\x1e'),
            ('abc', 'pqr', 4, 's%8Þ¸\x16]\x0b\x08R·\x1d\x9fÇm\x1d'),
        )

        for i, p, h, o,  in lst:
            self.assertEqual(checksph(i, p, h), o, msg=(i, p, h))

    def test_encrypt_with_strings(self):

        def checksph(s, p, h):
            ph = PasswordHandler(p, h)
            ph.start()
            out = ph.encrypt_sum(s)
            ph.end()
            return out

        lst = (
            ('a', 'p', 4, 'Äªh\x03\x8dÁ2J¦Q\x17¶\x03ÈD1'),
            ('ab', 'p', 4, 'Û°+1ä\x13øÿ)ÃV£órÈ('),
            ('abc', 'p', 4, '~\x90BÒ\x99ãÍ1\x88v\x11ë\x01ê\x1a\x90'),
            ('a a', 'p', 4, '\x95î1\x9aæEcÚÒ¯Æau\x92%¹'),
            ('ab ab', 'p', 4,
             'O_\x7fÓEYùkzhíº-,f8'),
            ('abc abc', 'p', 4,
             '\x15õP`\x110wQ\x08±\x0fïÃÅÍW'),
            ('a a a', 'p', 4,
             '\n\x13Jòá=öP\x8b\x11R\x98Ù,Ë\x98'),
            ('ab ab ab', 'p', 4,
             'ÌhSKÎDÏbùêÒ.ê\x11××'),
            ('abc abc abc', 'p', 4,
             ' ¤Íæ\x08}e\x1e«÷ÛÝCI©¥'),
        )

        for i, p, h, o,  in lst:
            self.assertEqual(checksph(i, p, h), o, msg=(i, p, h))

    def test_encrypt_non_default_password(self):

        def checksp2(s, p2):
            ph = PasswordHandler('password', 4)
            ph.start()
            out = ph.encrypt_sum(s, p2)
            ph.end()
            return out

        lst = (
            ('a', '', "X\x95'lXPJK\x02ÿ\x02-F[¡â"),
            ('ab', '', '®\x06yp\x12E¶1³\x9e\t\x8f\x07,Ïl'),
            ('abc', '', '@\x1f²¤Ó%ß\x8buü\x80õw³\x1d¢'),

            ('a', 'p', 'Äªh\x03\x8dÁ2J¦Q\x17¶\x03ÈD1'),
            ('ab', 'p', 'Û°+1ä\x13øÿ)ÃV£órÈ('),
            ('abc', 'p', '~\x90BÒ\x99ãÍ1\x88v\x11ë\x01ê\x1a\x90'),

            ('a', 'pq', 'Ó*\x9eþ%Æ0\x92äçô\x91\x9cêÚÏ'),
            ('ab', 'pq', '¨\x00GáruzûÝ\x14VÄ\x03ù\x8bÆ'),
            ('abc', 'pq', '\x8dñiÈ¹w5iYq¹ýt¶\x03\x1e'),

            ('a', 'pqr', '\x101&Ý}\x05®D&ìNT\x00\x99$f'),
            ('ab', 'pqr', '×\x98à\x7fw¦!ú¬¯ó\x88y*o\x1b'),
            ('abc', 'pqr', 's%8Þ¸\x16]\x0b\x08R·\x1d\x9fÇm\x1d'),
        )

        for i, p2, o,  in lst:
            self.assertEqual(checksp2(i, p2), o, msg=(i, p2))

    def test_decrypt_with_empty_string(self):

        def checksph(s, p, h):
            ph = PasswordHandler(p, h)
            ph.start()
            out = ph.decrypt_sum(s)
            ph.end()
            return out

        lst = (
            ('féKÔï\x8a,;\x88LúYÊ4+.', '', 0, ''),
            ('÷n*«\x93\x88:"h\x0fîYv\x80\x99\x16', 'a', 0, ''),
            ('¦Ã\x0e8\x8f\x15Èº\x1f-\x1a\x19ÉR(<', 'ab', 0, ''),
            ('\x91ÂãE\x96Ï?\xa0m¾%H®ÞZp', 'abc', 0, ''),
            ('ª#9Ê*\x9ca©/Æ*~^\x04(á', '', 4, ''),
            ('ýÛìL\x94¶PG§í\x07U1\x03êë', 'a', 4, ''),
            ('(\x0c\x80Kï%ð!Zþ\x8d\x14\x87\x10U°', 'ab', 4, ''),
            ('Õ;¹:E\x14;\x86<Ê\x1e2WùãÆ', 'abc', 4, ''),
        )

        for i, p, h, o,  in lst:
            self.assertEqual(checksph(i, p, h), o, msg=(i, p, h))

    def test_decrypt_with_empty_password(self):

        def checksph(s, p, h):
            ph = PasswordHandler(p, h)
            ph.start()
            out = ph.decrypt_sum(s)
            ph.end()
            return out

        lst = (
            ('féKÔï\x8a,;\x88LúYÊ4+.', '', 0, ''),
            ('.óKÊ&\nå\x98Â\x8d\x9bÁýÔ\x15k', '', 0, 'a'),
            ('g·\x89\x9eÊá°mâa>±åQÂ5', '', 0, 'ab'),
            ('Ò\x99\x99ê+\x04\x9aç\x9c¸k¢{\x1a_U', '', 0, 'abc'),
            ('ª#9Ê*\x9ca©/Æ*~^\x04(á', '', 4, ''),
            ("X\x95'lXPJK\x02ÿ\x02-F[¡â", '', 4, 'a'),
            ('®\x06yp\x12E¶1³\x9e\t\x8f\x07,Ïl', '', 4, 'ab'),
            ('@\x1f²¤Ó%ß\x8buü\x80õw³\x1d¢', '', 4, 'abc'),
        )

        for i, p, h, o,  in lst:
            self.assertEqual(checksph(i, p, h), o, msg=(i, p, h))

    def test_decrypt_with_hashes(self):

        def checksph(s, p, h):
            ph = PasswordHandler(p, h)
            ph.start()
            out = ph.decrypt_sum(s)
            ph.end()
            return out

        lst = (
            ('ø3èëe\x9c3\x89zr\x82\xad;&Ëa',
             'p', 0, 'a'),
            ("ÚJØI\x90\x95\x8f'öM·+elÒ¤",
             'p', 8, 'a'),
            ('\x1b\x83\x8fÞ\x97\x89\t%\x07XrÎc²´^ø3èëe\x9c3\x89zr\x82\xad;&Ëa',
             'p', 16, 'a'),
            ('ß\x11X~ævôö\\-ìu¤ß_²',
             'pq', 0, 'ab'),
            ('ïÁ¬\x97\x9f×é\x0c\x8cVöëµÐôÃ',
             'pq', 8, 'ab'),
            ('\x99#Ó\x18 XÜ\x9b\nVÇÃ~\x9a¤+ß\x11X~ævôö\\-ìu¤ß_²',
             'pq', 16, 'ab'),
            ('·2·<ö\x02\rh3ê¦±\x8b®uU',
             'pqr', 0, 'abc'),
            ("\x03\x16Â\x9e}Ã9'1´\\\xa0\x94\x95N©",
             'pqr', 8, 'abc'),
            ('\x7fêN¿\x19r\x95»ßßì"¹\x85æu·2·<ö\x02\rh3ê¦±\x8b®uU',
             'pqr', 16, 'abc'),
        )

        for i, p, h, o,  in lst:
            self.assertEqual(checksph(i, p, h), o, msg=(i, p, h))

    def test_decrypt_with_passwords(self):

        def checksph(s, p, h):
            ph = PasswordHandler(p, h)
            ph.start()
            out = ph.decrypt_sum(s)
            ph.end()
            return out

        lst = (
            ('kKoÑ´ï]ö\x05\x9cS2Ðá_\x95', 'p', 0, ''),
            ('2is\x1a\x9eT\x9añ@6\x8a\x04Òtÿ\x13', 'pq', 0, ''),
            ('²\t´Ù\x01ýo\x08Áz²³ö%î/', 'pqr', 0, ''),
            ('ø3èëe\x9c3\x89zr\x82\xad;&Ëa', 'p', 0, 'a'),
            ('Ft\x00"\x92FP~\x0c¹Ùw0\x14ü{', 'pq', 0, 'a'),
            ("3\x14\x1c\x96\x1f\x89\x8fo¥'ÃAÓ_hê", 'pqr', 0, 'a'),
            ('\x8fðyiQ=ó·\xad\xa0Í¡\x08\x8dÀ¶', 'p', 0, 'ab'),
            ('ß\x11X~ævôö\\-ìu¤ß_²', 'pq', 0, 'ab'),
            ('+\x04P1\x9dIBÜûý¶YÃ\x13+²', 'pqr', 0, 'ab'),
            ('¤=_ì3ÅÃ¸ÚÇè8n>\x02ß', 'p', 0, 'abc'),
            ('\x8e¶±>ê¨Ù\rý\x0fG¸Y»º.', 'pq', 0, 'abc'),
            ('·2·<ö\x02\rh3ê¦±\x8b®uU', 'pqr', 0, 'abc'),

            ('yg\x96¢\x15ëÃ¦\xad8üõ¼ý\x14Ç', 'p', 4, ''),
            ('Æ&\x90Ê\x90jÜën\x8dí3þÁÅÏ', 'pq', 4, ''),
            ('*\x00ó\x89þçñî\x93\x8bs7\x0by\x9bø', 'pqr', 4, ''),
            ('Äªh\x03\x8dÁ2J¦Q\x17¶\x03ÈD1', 'p', 4, 'a'),
            ('Ó*\x9eþ%Æ0\x92äçô\x91\x9cêÚÏ', 'pq', 4, 'a'),
            ('\x101&Ý}\x05®D&ìNT\x00\x99$f', 'pqr', 4, 'a'),
            ('Û°+1ä\x13øÿ)ÃV£órÈ(', 'p', 4, 'ab'),
            ('¨\x00GáruzûÝ\x14VÄ\x03ù\x8bÆ', 'pq', 4, 'ab'),
            ('×\x98à\x7fw¦!ú¬¯ó\x88y*o\x1b', 'pqr', 4, 'ab'),
            ('~\x90BÒ\x99ãÍ1\x88v\x11ë\x01ê\x1a\x90', 'p', 4, 'abc'),
            ('\x8dñiÈ¹w5iYq¹ýt¶\x03\x1e', 'pq', 4, 'abc'),
            ('s%8Þ¸\x16]\x0b\x08R·\x1d\x9fÇm\x1d', 'pqr', 4, 'abc'),
        )

        for i, p, h, o,  in lst:
            self.assertEqual(checksph(i, p, h), o, msg=(i, p, h))

    def test_decrypt_with_strings(self):

        def checksph(s, p, h):
            ph = PasswordHandler(p, h)
            ph.start()
            out = ph.decrypt_sum(s)
            ph.end()
            return out

        lst = (
            ('Äªh\x03\x8dÁ2J¦Q\x17¶\x03ÈD1',
             'p', 4, 'a'),
            ('Û°+1ä\x13øÿ)ÃV£órÈ(',
             'p', 4, 'ab'),
            ('~\x90BÒ\x99ãÍ1\x88v\x11ë\x01ê\x1a\x90',
             'p', 4, 'abc'),
            ('\x95î1\x9aæEcÚÒ¯Æau\x92%¹',
             'p', 4, 'a a'),
            ('O_\x7fÓEYùkzhíº-,f8',
             'p', 4, 'ab ab'),
            ('\x15õP`\x110wQ\x08±\x0fïÃÅÍW',
             'p', 4, 'abc abc'),
            ('\n\x13Jòá=öP\x8b\x11R\x98Ù,Ë\x98',
             'p', 4, 'a a a'),
            ('ÌhSKÎDÏbùêÒ.ê\x11××',
             'p', 4, 'ab ab ab'),
            (' ¤Íæ\x08}e\x1e«÷ÛÝCI©¥',
             'p', 4, 'abc abc abc'),
        )

        for i, p, h, o,  in lst:
            self.assertEqual(checksph(i, p, h), o, msg=(i, p, h))

    def test_decrypt_non_default_password(self):

        def checksp2(s, p2):
            ph = PasswordHandler('password', 4)
            ph.start()
            out = ph.decrypt_sum(s, p2)
            ph.end()
            return out

        lst = (
            ("X\x95'lXPJK\x02ÿ\x02-F[¡â", '', 'a'),
            ('®\x06yp\x12E¶1³\x9e\t\x8f\x07,Ïl', '', 'ab'),
            ('@\x1f²¤Ó%ß\x8buü\x80õw³\x1d¢', '', 'abc'),

            ('Äªh\x03\x8dÁ2J¦Q\x17¶\x03ÈD1', 'p', 'a'),
            ('Û°+1ä\x13øÿ)ÃV£órÈ(', 'p', 'ab'),
            ('~\x90BÒ\x99ãÍ1\x88v\x11ë\x01ê\x1a\x90', 'p', 'abc'),

            ('Ó*\x9eþ%Æ0\x92äçô\x91\x9cêÚÏ', 'pq', 'a'),
            ('¨\x00GáruzûÝ\x14VÄ\x03ù\x8bÆ', 'pq', 'ab'),
            ('\x8dñiÈ¹w5iYq¹ýt¶\x03\x1e', 'pq', 'abc'),

            ('\x101&Ý}\x05®D&ìNT\x00\x99$f', 'pqr', 'a'),
            ('×\x98à\x7fw¦!ú¬¯ó\x88y*o\x1b', 'pqr', 'ab'),
            ('s%8Þ¸\x16]\x0b\x08R·\x1d\x9fÇm\x1d', 'pqr', 'abc'),
        )

        for i, p2, o,  in lst:
            self.assertEqual(checksp2(i, p2), o, msg=(i, p2))

    def test_decrypt_incorrect_password(self):

        def checksph(s, p, h):
            ph = PasswordHandler(p, h)
            ph.start()
            out = ph.decrypt_sum(s)
            ph.end()
            return out

        self.assertEqual(checksph('Äªh\x03\x8dÁ2J¦Q\x17¶\x03ÈD1', 'p', 4), 'a')
        self.assertEqual(checksph('Û°+1ä\x13øÿ)ÃV£órÈ(', 'p', 4), 'ab')
        self.assertEqual(checksph('~\x90BÒ\x99ãÍ1\x88v\x11ë\x01ê\x1a\x90', 'p', 4), 'abc')

        lst = (
            ('Äªh\x03\x8dÁ2J¦Q\x17¶\x03ÈD1', 'pq', 4),
            ('Äªh\x03\x8dÁ2J¦Q\x17¶\x03ÈD1', 'q', 4),
            ('Û°+1ä\x13øÿ)ÃV£órÈ(', 'pq', 4),
            ('Û°+1ä\x13øÿ)ÃV£órÈ(', 'q', 4),
            ('~\x90BÒ\x99ãÍ1\x88v\x11ë\x01ê\x1a\x90', 'pq', 4),
            ('~\x90BÒ\x99ãÍ1\x88v\x11ë\x01ê\x1a\x90', 'q', 4),
        )

        for i, p, h in lst:
            with self.assertRaises(PswDecryptError, msg=(i, p, h)):
                checksph(i, p, h)

    def test_decrypt_incorrect_hash(self):

        def checksph(s, p, h):
            ph = PasswordHandler(p, h)
            ph.start()
            out = ph.decrypt_sum(s)
            ph.end()
            return out

        self.assertEqual(checksph('Äªh\x03\x8dÁ2J¦Q\x17¶\x03ÈD1', 'p', 4), 'a')
        self.assertEqual(checksph('Û°+1ä\x13øÿ)ÃV£órÈ(', 'p', 4), 'ab')
        self.assertEqual(checksph('~\x90BÒ\x99ãÍ1\x88v\x11ë\x01ê\x1a\x90', 'p', 4), 'abc')

        lst = (
            ('Äªh\x03\x8dÁ2J¦Q\x17¶\x03ÈD1', 'p', 3),
            ('Äªh\x03\x8dÁ2J¦Q\x17¶\x03ÈD1', 'p', 5),
            ('Û°+1ä\x13øÿ)ÃV£órÈ(', 'p', 3),
            ('Û°+1ä\x13øÿ)ÃV£órÈ(', 'p', 5),
            ('~\x90BÒ\x99ãÍ1\x88v\x11ë\x01ê\x1a\x90', 'p', 3),
            ('~\x90BÒ\x99ãÍ1\x88v\x11ë\x01ê\x1a\x90', 'p', 5),
        )

        for i, p, h in lst:
            with self.assertRaises(PswDecryptError, msg=(i, p, h)):
                checksph(i, p, h)

    def test_incorrect_hash_range(self):
        self.assertRaises(ValueError, PasswordHandler, 'p', -1)
        self.assertRaises(ValueError, PasswordHandler, 'p', 33)


if __name__ == '__main__':
    unittest.main()
