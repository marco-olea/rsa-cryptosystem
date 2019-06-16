from math import log
from random import randint
from base64 import b64encode, b64decode
from crypto.common import modular_inverse, power
from crypto.primes import random_search, random_prime_in_database


class PublicKey:
    """Represents the public parameters in the RSA cryptosystem.
    
    Attributes:
        n: The product of two (large) prime numbers.
        e: An integer such that 1 < e < φ(n) and e and φ(n) are coprime, where φ is Euler's Totient
            Function.
    """
    
    def __init__(self, n: int, e: int):
        """Create a Public Key with the given parameters."""
        self.n = n
        self.e = e
        

class PrivateKey:
    """Represents the private parameters in the RSA cryptosystem.

    Attributes:
        n: The product of two (large) prime numbers.
        d: The modular multiplicative inverse of the public parameter e modulo φ(n).
    """
    
    def __init__(self, n: int, d: int):
        """Create a Private Key with the given parameters."""
        self.n = n
        self.d = d


class RSA:
    """The RSA cryptosystem for encryption and decryption.
    
    Attributes:
        public_key: The public parameters.
        private_key: The private parameters.
    """
    
    MIN_DIGITS = 100
    """The minimum size of the randomly-generated prime numbers."""
    
    MAX_DIGITS = 119
    """The maximum size of the randomly-generated prime numbers."""
    
    SECURITY = 10
    """Security parameter for the Miller-Rabin probabilistic primality test."""
    
    MAX_GROUP_SIZE = 30
    """Maximum number of bytes to group together."""
    
    DELIMITER = '$'
    """Delimiter character that is not used in Python 3.7's Base64 encoding implementation."""
    
    def __init__(self, public_key: PublicKey, private_key: PrivateKey):
        """Initialize the cryptosystem with the given keys."""
        self.public_key = public_key
        self.private_key = private_key
    
    @classmethod
    def generate(cls):
        """Initialize the cryptosystem with randomly-generated parameters."""
        # Choose random prime numbers p and q.
        num_digits_1 = num_digits_2 = 0
        while num_digits_1 == num_digits_2:
            num_digits_1 = randint(cls.MIN_DIGITS, cls.MAX_DIGITS)
            num_digits_2 = randint(cls.MIN_DIGITS, cls.MAX_DIGITS)
        num_bits_1 = 1 + int(log(10**(num_digits_1 - 1), 2))
        num_bits_2 = 1 + int(log(10**(num_digits_2 - 1), 2))
        p = random_search(num_bits_1, t=cls.SECURITY)
        q = random_search(num_bits_2, t=cls.SECURITY)
        
        # Compute φ(n) = φ(p)φ(q).
        phi_n = (p - 1) * (q - 1)
        
        # Choose a random e such that 1 < e < φ(n) and gcd(e, φ(n)) = 1.
        # If we choose a random prime instead of any random number, we only need to check if φ(n)
        # is a multiple of e to verify that φ(n) and e are relatively prime.
        e = 1
        while phi_n % e == 0:
            # Clearly φ(n) is at least 200 decimal digits. The database does not store primes of
            # this size, i.e., any element e in the database satisfies 1 < e < φ(n).
            e = random_prime_in_database()
        
        # Compute d, the modular multiplicative inverse of e mod φ(n).
        d = modular_inverse(e, phi_n)
        
        n = p * q
        return RSA(PublicKey(n, e), PrivateKey(n, d))
    
    def encrypt(self, message: str) -> str:
        """Encrypt a string.
        
        Note that all occurrences of the NULL character U+0000 will be lost in the encryption
        process.
        """
        # Get the UTF-8 byte array of the message, and convert each byte into a string of 3 digits.
        message = [f'{b:03}' for b in message.encode()]
        length = len(message)
        # Choose the size of each group of bytes.
        group_size = randint(1, length if length < self.MAX_GROUP_SIZE else self.MAX_GROUP_SIZE)
        # Append ['000'] until len(message) is a multiple of group_size.
        message += ['000'] * (group_size - length % group_size)
        # Join into groups.
        groups = [message[i: i + group_size] for i in range(0, length, group_size)]
        # Numbers to which the transformation will be applied.
        numbers = [int(''.join(group)) for group in groups]
        # Apply m^e % n = c to each number m, and convert c to a string.
        transformed_numbers = [str(power(m, self.public_key.e, self.public_key.n)) for m in numbers]
        # Pre-appends '' or '0' to make sure each string has an even number of digits.
        transformed_numbers = [
            ('' if len(transformed_number) % 2 == 0 else '0') + transformed_number
            for transformed_number in transformed_numbers]
        # Now we split each every transformed number into pairs of digits that represent bytes.
        # Three-digit numbers might not be in [0, 255], but two-digit numbers always will be.
        byte_arrays = [
            [int(c[i: i + 2]) for i in range(0, len(c), 2)]
            for c in transformed_numbers]
        # Encode the resulting byte arrays with base64.
        b64_strings = [
            b64encode(bytes(byte_array)).decode()  # message.decode() -> utf-8 string
            for byte_array in byte_arrays]
        # Return the strings separated by a delimiter.
        return self.DELIMITER.join(b64_strings)
    
    def decrypt(self, message: str) -> str:
        """Decrypt a string that was encrypted with this class's encrypt method."""
        # Decode each string with base64.
        b64_arrays = [b64decode(line.encode()) for line in message.split(self.DELIMITER)]
        # Get the int (two-digit) representation of each byte in every byte array.
        byte_arrays = [
            [int(b) for b in b64_array]
            for b64_array in b64_arrays]
        # Concatenate each byte array to form a string representing c. Single-digit numbers get
        # pre-appended with a '0'. Convert the result to an int.
        transformed_numbers = [
            int(''.join([f'{b:02}' for b in byte_array]))
            for byte_array in byte_arrays]
        # Apply c^d % n = m to each transformed number c to get the original number m.
        numbers = [
            str(power(c, self.private_key.d, self.private_key.n))
            for c in transformed_numbers]
        # Split each number m (starting from right to left) into three-digit numbers.
        decrypted_bytes = [
            int(m[(0 if i < 3 else i - 3): i])
            for m in numbers[::-1] for i in range(len(m), 0, -3)]
        # Reverse and remove all zeros.
        original_byte_array = [dec_byte for dec_byte in decrypted_bytes[::-1] if dec_byte != 0]
        return bytes(original_byte_array).decode()
