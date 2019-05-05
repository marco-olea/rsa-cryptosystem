from os import path, pardir
from sqlite3 import connect

filename = path.join(path.dirname(__file__), pardir, 'primes.db')
connection = connect(filename)
CURSOR = connection.cursor()
