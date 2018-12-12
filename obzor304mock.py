import datetime
import random

from instr.obzor304 import Obzor304

TOUCHSTONE_S2P = "S2P"


class Obzor304Mock(Obzor304):

    def __init__(self, address: str):
        self._address = address
        self._idn = 'OBZOR304 mock'
        self._folder = ""
        self._delay = 0

    def send(self, command):
        print('Obzor304 mock:', command)
        return 'success'

    def query(self, question):
        print('Obzor304 mock', question)
        if question == 'SENS:FREQ:DATA?':
            return '300,4000,50000,600000,7000000'
        elif question == 'CALC1:DATA:FDAT?':
            amps = list(map(lambda x: x - random.randint(1, 2), [2, 0, 1, 0, 1, 0, -3, 0, -6, 0]))
            return ','.join(map(str, amps))
        return 'success'
