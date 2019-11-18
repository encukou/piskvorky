from random import randrange

from util import tah

def tah_pocitace(pole, symbol):
    if '-' not in pole:
        raise ValueError('pole je plné')
    while True:
        pozice = randrange(len(pole))
        if pole[pozice] == '-':
            return tah(pole, pozice, symbol)
