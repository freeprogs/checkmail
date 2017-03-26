#!/usr/bin/env python3

import unittest


class Test(unittest.TestCase):
    def setUp(self):
        self.func = None

    def test_(self):
        self.assertEqual(self.func(i), o, str(i))

    def test_(self):
        lst = [
            #
        ]
        for i, o in lst:
            self.assertEqual(self.func(i), o, str((i, o)))

if __name__ == '__main__':
    unittest.main()
