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

    def __str__(self):
        return self._idn

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
        print('OBZOR-304: устанавливаем тип выходного файла', self.send(f'MMEM:STOR:SNP:TYPE:{ftype}'), f'| file_type={ftype}')

    def set_active_window(self, num: int):
        print('OBZOR-304: устанавливаем активное окно:', self.send(f'DISP:WIND{num}:ACT'))

    def set_trigger_source(self, source: str):
        print('OBZOR-304: устанавливаем источник триггер-сигнала:', self.send(f'TRIG:SOUR {source}'))

    def make_data_dir(self):
        self._folder = r'C:\!meas\LPF_' + datetime.date.today().isoformat()
        print('OBZOR-304: создаём папку для сохранения результатов измерений:',
              self.send(f'MMEM:MDIR "{self._folder}"'), f'| dir={self._folder}')

    def reset_instrument(self):
        print(self.send('*CLS'))

    def measure(self, n: int):
        meas_file_name = self._folder + f'\\lpf_{str(n).zfill(3)}.s2p'
        print('OBZOR-304: запускаем измерение:', self.send('INIT1; *OPC?'))

        # FIXME: detector doesn't work
        # print('OBZOR-304: запускаем измерение:', self._inst.write('TRIGger:SEQuence:SINGle'))
        # TODO: get confirmation for measurement end
        # print(self._inst.query('*OPC?'))
        # while self._inst.query('*OPC?') != '1':
        #     print('waiting')

        sleep(0.7)
        freqs = self.query('SENS:FREQ:DATA?')
        amps = self.query('CALC1:DATA:FDAT?')
        # print('freqs:', freqs.count(',') + 1, freqs)
        # print('amp:', amps.count(',') + 1, amps)
        print('OBZOR-304: сохраняем результат измерений: ',
              self.send(f'MMEM:STOR:SNP "{meas_file_name}"'), f'\nФайл: {meas_file_name}')
        return freqs, amps

    def finish(self):
        print('OBZOR-304: выключаем непрерывную подачу триггер-сигнала:', self.send('INITiate1:CONTinuous ON'))
        self.set_trigger_source('INT')
