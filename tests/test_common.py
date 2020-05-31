from random import randint
from unittest import TestCase

from crypto.common import euclidean_algorithm, gcd, modular_inverse, power, largest_power_two_factor


class TestCommonFunctions(TestCase):
    UPPER_BOUND = 10000
    SIZE = 20000

    @classmethod
    def setUpClass(cls):
        cls.integers = [
            (randint(0, cls.UPPER_BOUND), randint(0, cls.UPPER_BOUND), randint(0, cls.UPPER_BOUND))
            for _ in range(cls.SIZE)]

    def test_euclidean_algorithm(self):
        for (a, b, _) in self.integers:
            d, x, y = euclidean_algorithm(a, b)
            self.assertEqual(d, a * x + b * y)

    def test_gcd(self):
        for (a, b, _) in self.integers:
            d = gcd(a, b)
            self.assertEqual(0, a % d)
            self.assertEqual(0, b % d)

    def test_modular_inverse(self):
        for (a, mod, _) in self.integers:
            if a == 0 or mod in [0, 1]:
                continue
            d = gcd(a, mod)
            a_inv = modular_inverse(a, mod)
            if d == 1:
                self.assertIsNotNone(a_inv)
                self.assertEqual(1, (a * a_inv) % mod)
            else:
                self.assertIsNone(a_inv)

    def test_power(self):
        for (a, b, c) in self.integers:
            if c > 0:
                self.assertEqual((a**b) % c, power(a, b, c))

    def test_largest_power_two_factor(self):
        for (a, _, _) in self.integers:
            if a == 0:
                self.assertRaises(Exception, largest_power_two_factor, a)
            else:
                s = largest_power_two_factor(a)
                r = a // 2**s
                self.assertEqual(a, r * 2**s)
