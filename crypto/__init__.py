from os import path, pardir
from sqlite3 import connect

filename = path.join(path.dirname(__file__), pardir, 'primes.db')
connection = connect(filename)

CURSOR = connection.cursor()
"""A cursor for the connection to the primes database. Apparently for a program as simple as this
one it is safe to not explicitly close the associated connection."""
