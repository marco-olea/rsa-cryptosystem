from math import log
from random import randint
from base64 import b64encode, b64decode
from crypto.common import modular_inverse, power
from crypto.primes import random_search, random_prime_in_database


class PublicKey:
    def __init__(self, n: int, e: int):
        self.n = n
        self.e = e
        

class PrivateKey:
    def __init__(self, n: int, d: int):
        self.n = n
        self.d = d


class RSA:
    
    MIN_DIGITS = 100
    MAX_DIGITS = 119
    SECURITY = 10
    
    def __init__(self, public_key: PublicKey, private_key: PrivateKey):
        self.public_key = public_key
        self.private_key = private_key
    
    @classmethod
    def generate(cls):
        # Choose random prime numbers p and q.
        num_digits_1 = num_digits_2 = 0
        while num_digits_1 == num_digits_2:
            num_digits_1 = randint(cls.MIN_DIGITS, cls.MAX_DIGITS)
            num_digits_2 = randint(cls.MIN_DIGITS, cls.MAX_DIGITS)
        num_bits_1 = 1 + int(log(10**(num_digits_1 - 1), 2))
        num_bits_2 = 1 + int(log(10**(num_digits_2 - 1), 2))
        p = random_search(num_bits_1, t=cls.SECURITY)
        q = random_search(num_bits_2, t=cls.SECURITY)
        
        # Compute Euler's Totient Function (phi) of n = pq.
        phi_n = (p - 1) * (q - 1)
        
        # Choose a random e such that 1 < e < phi_n and gcd(e, phi_n) = 1.
        # If we choose a random prime instead of any random number, we only need to check if phi_n
        # is a multiple of e to verify that phi_n and e are relatively prime.
        e = 1
        while phi_n % e == 0:
            # Clearly phi_n is at least 200 decimal digits. The database does not store primes of
            # this size, i.e., any element e in the database satisfies 1 < e < phi_n.
            e = random_prime_in_database()
        
        # Compute d, the modular multiplicative inverse of e mod phi_n.
        d = modular_inverse(e, phi_n)
        
        n = p * q
        return RSA(PublicKey(n, e), PrivateKey(n, d))
    
    def encrypt(self, message: str) -> str:
        transformed_numbers = [
            str(power(m, self.public_key.e, self.public_key.n))
            for m in message.encode()]  # message.encode() -> utf-8 byte array
        transformed_numbers = [
            ('' if len(transformed_number) % 2 == 0 else '0') + transformed_number
            for transformed_number in transformed_numbers]
        byte_arrays = [
            [int(c[i: i + 2]) for i in range(0, len(c), 2)]
            for c in transformed_numbers]
        b64_strings = [
            b64encode(bytes(byte_array)).decode()  # message.decode() -> utf-8 string
            for byte_array in byte_arrays]
        return '\n'.join(b64_strings)
    
    def decrypt(self, message: str) -> str:
        b64_arrays = [
            b64decode(line.encode())
            for line in message.strip().split()]
        byte_arrays = [
            [int(b) for b in b64_array]
            for b64_array in b64_arrays]
        transformed_numbers = [
            int(''.join([f'{b:02}' for b in byte_array]))
            for byte_array in byte_arrays]
        original_numbers = [
            power(c, self.private_key.d, self.private_key.n)
            for c in transformed_numbers]
        return bytes(original_numbers).decode()
    
    
if __name__ == '__main__':
    rsa = RSA.generate()
    msg = 'This is the message. áüñ'
    enc = rsa.encrypt(msg)
    dec = rsa.decrypt(enc)
    print(enc)
    print(dec)
