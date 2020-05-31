# RSA Encryption/Decryption tool

    usage: main.py [-h] [-o OUTPUT] {e,d} INPUT [INPUT ...]

    Encrypt or decrypt a file or string using the RSA algorithm.

    positional arguments:
        {e,d}       Specifies whether to encrypt or decrypt the input.
        INPUT       A file name or string.

    optional arguments:
      -h, --help  show this help message and exit
      -o OUTPUT   File to write the results to.


This project uses no third-party libraries for cryptography-related functions (primality tests,
probabilistic prime number searches, number theory-related things like the euclidean algorithm,
gcd, modular inverse, square-and-multiply algorithm, etc). These have been implemented from scratch.

##Reference: 
"Handbook of Applied Cryptography"

Alfred Menezes, Paul van Oorschot, and Scott Vanstone

Written in Python 3.7.1 and tested up to 3.8.2.
