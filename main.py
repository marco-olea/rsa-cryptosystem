from argparse import ArgumentParser, FileType
from os.path import isfile
from sys import stdout

from crypto.rsa import RSA, PublicKey, PrivateKey

if __name__ == '__main__':
    parser = ArgumentParser(description='Encrypt or decrypt a file or string using '
                                        'the RSA algorithm.')
    parser.add_argument('option', choices=['e', 'd'], type=str,
                        help='Specifies whether to encrypt or decrypt the input.')
    parser.add_argument('infile', metavar='INPUT', type=str, nargs='+',
                        help='A file name or string.')
    parser.add_argument('-o', metavar='OUTPUT', type=FileType('w'), default=stdout,
                        dest='outfile',
                        help='File to write the results to.')
    args = parser.parse_args()

    if isfile('publickey') and isfile('privatekey'):
        print('Found keys.')
        with open('publickey', 'r') as public_key_file:
            public_key = PublicKey(int(public_key_file.readline()),
                                   int(public_key_file.readline()))
        with open('privatekey', 'r') as private_key_file:
            private_key = PrivateKey(int(private_key_file.readline()),
                                     int(private_key_file.readline()))
        rsa = RSA(public_key, private_key)
    else:
        print('Generating keys...')
        rsa = RSA.generate()
        with open('publickey', 'w') as public_key_file:
            public_key_file.write(str(rsa.public_key))
        with open('privatekey', 'w') as private_key_file:
            private_key_file.write(str(rsa.private_key))

    try:
        with open(' '.join(args.infile), 'r') as infile:
            str_input = ''.join(list(infile))
    except FileNotFoundError:
        str_input = ' '.join(args.infile)

    try:
        if args.option == 'e':
            print('Encrypting input...')
            args.outfile.write(rsa.encrypt(str_input))
        else:
            print('Decrypting input...\n')
            args.outfile.write(f'********************\n{rsa.decrypt(str_input)}\n'
                               f'********************\n\n')
        print('Done.')
    except Exception:
        print('The given input was not generated with ./publickey '
              'and ./privatekey.')
