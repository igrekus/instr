import datetime

from instr.obzor304 import Obzor304

TOUCHSTONE_S2P = "S2P"


class Obzor304Mock(Obzor304):

    def __init__(self, address: str):
        self._address = address
        self._idn = 'OBZOR304 mock'
        self._folder = ""

    def send(self, command):
        print('Obzor304 mock:', command)
        return 'success'

    def measure(self, n: int):
        meas_file_name = self._folder + f'\\lpf_{str(n).zfill(3)}.s2p'
        print('\nOBZOR-304: запускаем измерение:', self.send('INIT1; *OPC?'))

        freqs = self.query('SENS:FREQ:DATA?')
        amps = self.query('CALC1:DATA:FDAT?')

        freqs = '300,4000,50000,600000,7000000'
        amps = '10,0,5,0,0,0,-10,0,-40,0'
        print('freqs:', freqs.count(',') + 1, freqs)
        print('amp:', amps.count(',') + 1, amps)

        print('OBZOR-304: сохраняем результат измерений: ',
              self.send(f'MMEM:STOR:SNP "{meas_file_name}"'), f'\nФайл:{meas_file_name}')
        return freqs, amps

    def query(self, question):
        print('Obzor304 mock', question)
        return 'success'
