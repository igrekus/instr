import datetime
import visa
from time import sleep

TOUCHSTONE_S2P = 'S2P'


class Obzor304:
    def __init__(self, address: str):
        # TODO: move resource manager out of this class
        self._address = address
        self._rm = visa.ResourceManager()
        self._inst = self._rm.open_resource(address)
        self._idn = self.query('*IDN?')
        self._folder = ''
        self._delay = 0.7

    def __str__(self):
        return f'{self._idn} at {self._address.strip("TCPIP::").strip("::INSTR")}'

    def send(self, command):
        return self._inst.write(command)

    def query(self, question):
        return self._inst.query(question)

    def init_instrument(self):
        # self.reset_instrument()
        self.set_active_window(1)
        self.make_data_dir()
        self.set_touchstone_file_type(TOUCHSTONE_S2P)
        self.set_trigger_source('INT')

    def set_touchstone_file_type(self, ftype: str):
        print('OBZOR-304: set out file type', self.send(f'MMEM:STOR:SNP:TYPE:{ftype}'), f'| file_type={ftype}')

    def set_active_window(self, num: int):
        print('OBZOR-304: set active window:', self.send(f'DISP:WIND{num}:ACT'))

    def set_trigger_source(self, source: str):
        print('OBZOR-304: set trigger source:', self.send(f'TRIG:SOUR {source}'))

    def make_data_dir(self):
        self._folder = r'C:\!meas\LPF_' + datetime.date.today().isoformat()
        print('OBZOR-304: create out folder:',
              self.send(f'MMEM:MDIR "{self._folder}"'), f'| dir={self._folder}')

    def reset_instrument(self):
        print(self.send('*CLS'))

    def measure(self, n: int):
        meas_file_name = self._folder + f'\\lpf_{str(n).zfill(3)}.s2p'
        print('OBZOR-304: trigger measure:', self.send('INIT1; *OPC?'))

        # FIXME: detector doesn't work
        # print('OBZOR-304: запускаем измерение:', self._inst.write('TRIGger:SEQuence:SINGle'))
        # TODO: get confirmation for measurement end
        # print(self._inst.query('*OPC?'))
        # while self._inst.query('*OPC?') != '1':
        #     print('waiting')

        sleep(self._delay)
        freqs = self.query('SENS:FREQ:DATA?')
        amps = self.query('CALC1:DATA:FDAT?')
        # print('freqs:', freqs.count(',') + 1, freqs)
        # print('amp:', amps.count(',') + 1, amps)
        print('OBZOR-304: save measure:',
              self.send(f'MMEM:STOR:SNP "{meas_file_name}"'), f'\nФайл: {meas_file_name}')
        return freqs, amps

    def finish(self):
        print('OBZOR-304: continuous trigger off:', self.send('INITiate1:CONTinuous ON'))
        self.set_trigger_source('INT')
