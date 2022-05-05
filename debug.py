import sys


# Режим дебага
# Ключ d используется после аргумента пути к dockerfile
DEBUG = False
if '-d' in sys.argv:
    DEBUG = True
    print('Включен debug-режим')
