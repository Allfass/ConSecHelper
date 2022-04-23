import sys


# режим дебага
DEBUG = False
if '-d' in sys.argv:
    DEBUG = True
    print('Включен debug-режим')
