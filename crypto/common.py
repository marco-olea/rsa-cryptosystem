from typing import Tuple, Optional


def euclidean_algorithm(a: int, b: int) -> Tuple[int, int, int]:
    """Return a tuple (d, x, y) that satisfies d = ax + by.

    >>> euclidean_algorithm(8, 20)
    (4, -2, 1)
    >>> euclidean_algorithm(11, 5)
    (1, 1, -2)
    """
    exchanged = False
    if a < b:
        a, b = b, a
        exchanged = True
    if b == 0:
        return (a, 0, 1) if exchanged else (a, 1, 0)
    x1, x2, y1, y2 = 0, 1, 1, 0
    while b > 0:
        q = a // b
        r = a - q * b
        x = x2 - q * x1
        y = y2 - q * y1
        a, b = b, r
        x1, x2, y1, y2 = x, x1, y, y1
    return (a, y2, x2) if exchanged else (a, x2, y2)


def gcd(a: int, b: int) -> int:
    """Return the greatest common divisor of two positive integers a and b.

    >>> gcd(6, 21)
    3
    >>> gcd(14, 280)
    14
    """
    return euclidean_algorithm(abs(a), abs(b))[0]


def modular_inverse(a: int, mod: int) -> Optional[int]:
    """Return the modular multiplicative inverse of a if it exists.

    >>> modular_inverse(7, 14)

    >>> modular_inverse(7, 13)
    2
    """
    d, x, y = euclidean_algorithm(a, mod)
    if d == 1:
        return x if x > 0 else x + mod


def power(base: int, exponent: int, mod: int) -> int:
    """Modular exponentiation of three given integers.

    This function uses the Square and Multiply algorithm.

    >>> power(4, 3, 5)
    4
    >>> power(3, 4, 8)
    1

    Args:
        base:     The base.
        exponent: The nonnegative power that the base will be raised to.
        mod:      The modulo.
    Returns:
        (base^exponent) % mod
    """
    result, next_bit = 1, 0
    while exponent >> next_bit > 0:
        next_bit += 1
    # result{k} = result{k+1}^2 * base^(b{k}) where exp = b{k}b{k-1}...b{0} (bits)
    while next_bit > 0:
        result = (result**2 * base**(exponent >> next_bit - 1 & 1)) % mod
        next_bit -= 1
    return result


def largest_power_two_factor(a: int) -> int:
    """Return the largest integer s for which 2^s is a factor of a.

    >>> largest_power_two_factor(3)
    0
    >>> largest_power_two_factor(24)
    3

    Args:
        a: A positive integer.
    Returns:
        The largest s such that 2^s divides a.
    """
    if a <= 0:
        raise Exception('Argument must be a positive integer.')
    s = 0
    while (a >> s) & 1 == 0:
        s += 1
    return s
