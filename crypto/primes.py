from math import sqrt, ceil
from random import randint, random
from typing import List

from crypto import CURSOR
from crypto.common import power, largest_power_two_factor


def brute_force_primality(n: int) -> bool:
    """Determine if n is prime by brute force.

    Args:
        n: A positive integer.
    Returns:
        <code>True</code> if n is prime, <code>False</code> otherwise.
    """
    if n in [2, 3]:
        return True
    if n == 1 or n % 2 == 0 or n % 3 == 0:
        return False
    for i in range(4, 1 + ceil(sqrt(n))):
        if n % i == 0:
            return False
    return True


def miller_rabin_primality(n: int, t: int) -> bool:
    """Determine if n is prime using the Miller-Rabin probabilistic primality test.

    If the algorithm declares "Composite" (False), then n is guaranteed to be composite.
    If n is prime, the test will always declare "Prime" (True).
    If n is composite, the test declares "Prime" (True) with a probability of (1/4)^t.

    Args:
        n: An integer greater than or equal to 3.
        t: Security parameter; must be greater than or equal to one.
    Returns:
        <code>True</code> if n is a probable prime, <code>False</code> if <i>n</i>
         is definitely composite.
    """
    s = largest_power_two_factor(n - 1)
    r = (n - 1) // 2**s
    for _ in range(t):
        a = randint(2, n - 2)
        y = power(a, r, n)
        if y not in [1, n - 1]:
            j = 1
            while j <= s - 1 and y != n - 1:
                y = power(y, 2, n)
                if y == 1:
                    return False
                j += 1
            if y != n - 1:
                return False
    return True


def random_search(k: int, t: int = 1) -> int:
    """Return a random k-bit probable prime.
    
    If a random k-bit odd integer is divisible by a small prime, it is less
    computationally expensive to rule out the candidate by trial division than
    by using the Miller-Rabin test. Since the probability that a random integer
    has a small prime divisor is relatively large, before applying the
    Miller-Rabin test, the candidate is tested for small divisors below a bound
    B, hereby determined to be k^2, which is the cost of multiplying two k-digit
    numbers using the standard algorithm.

    The probability that this function does not return a prime number is
    k^2 * 16^(-sqrt(k)) for k >= 2 and the default t = 1.
        
    Args:
        k: Number of bits, must be greater than or equal to 2.
        t: Security parameter for the Miller-Rabin test; default value is 1.
    Returns:
        A random k-bit probable prime.
    """
    # Get first B primes.
    primes = first_k_primes(int(k**2))
    probable_prime = None
    while not probable_prime:
        # Generate an odd k-bit integer n at random.
        n = 1
        for _ in range(k - 2):
            n <<= 1
            n |= 0 if random() < 0.5 else 1
        n = (n << 1) | 1
        is_composite = False
        # Determine if n is prime using trial division.
        for p in primes:
            if n % p == 0:
                is_composite = True
                break
        # Determine if n is prime using the more costly Miller-Rabin test.
        if not is_composite and miller_rabin_primality(n, t):
            probable_prime = n
    return probable_prime


def first_k_primes(k: int) -> List[int]:
    """Return a list of the first k prime numbers."""
    CURSOR.execute('SELECT * FROM primes WHERE ord BETWEEN 1 AND ?', [k])
    primes = [row[1] for row in CURSOR]
    return primes


def populate_database(k: int) -> None:
    """Populate the database with k prime numbers.

    If the database is empty, adds the first k prime numbers. Otherwise, adds
    the next k prime numbers after the largest stored in the database.
    
    Args:
        k: A positive integer.
    """
    CURSOR.execute('SELECT COALESCE(MAX(ord), 0) FROM primes')
    max_ord = CURSOR.fetchone()[0]
    if max_ord == 0:
        primes = [(1, 2)]
        i, p = 2, 3
    else:
        CURSOR.execute('SELECT * FROM primes WHERE ord = ?', [max_ord])
        last_row = CURSOR.fetchone()
        primes = []
        i, p = last_row[0] + 1, last_row[1] + 2
    while len(primes) < k:
        if brute_force_primality(p):
            primes.append((i, p))
            i += 1
        p += 2
    CURSOR.executemany('INSERT OR IGNORE INTO primes VALUES (?, ?)', primes)
    CURSOR.connection.commit()


def random_prime_in_database() -> int:
    """Return a random prime number in the database."""
    max_ord = CURSOR.execute('SELECT MAX(ord) FROM primes').fetchone()[0]
    CURSOR.execute('SELECT * FROM primes WHERE ord = ?', [randint(1, max_ord)])
    return CURSOR.fetchone()[1]
