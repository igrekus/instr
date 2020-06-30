class AgilentN9030A:

    # TODO implement SCPI: set reference level

    def __init__(self, address: str, idn: str, inst):
        self._address = address
        self._idn = idn
        self._name = idn.split(',')[1].strip()
        self._inst = inst

    def __str__(self):
        return f'{self._name}'

    def __repr__(self):
        return f'{self.__class__}(idn={self._idn})'

    def send(self, command):
        print(f'{self._name}', self._inst.write(command))

    def query(self, question):
        answer = self._inst.query(question)
        print(f'{self._name} {answer}')
        return answer

    def ping(self):
        print(self.query('*IDN?'))

    def set_autocalibrate(self, state):
        self.send(f':CAL:AUTO {state}')

    def set_span(self, value, unit):
        self.send(f':SENS:FREQ:SPAN {value}{unit}')

    def set_marker_mode(self, marker: int, mode='POS'):
        self.send(f':CALC:MARK{marker}:MODE {mode}')

    def set_pow_attenuation(self, value):
        self.send(f':POW:ATT {value}')

    def set_measure_center_freq(self, value, unit):
        # TODO hack for E4446A
        com = f':SENSe:FREQuency:RF:CENTer {value}{unit}'
        if self._name == 'E4446A':
            com = f':SENSe:FREQuency:CENTer {value}{unit}'
        self.send(com)

    def set_marker1_x_center(self, value, unit):
        self.send(f':CALCulate:MARKer1:X:CENTer {value}{unit}')

    def read_pow(self, marker: int=1) -> float:
        answer = self.query(f':CALCulate:MARKer{marker}:Y?')
        return float(answer)

    def remove_marker(self, marker=1):
        return self.send(f':CALC:MARK{marker}:MODE OFF')

    def set_system_local(self):
        # pass
        self.send(f'system:local')

    @property
    def name(self):
        return self._name

    @property
    def addr(self):
        return self._address

    @property
    def model(self):
        return self.name

    @property
    def status(self):
        return f'{self.model} at {self.addr}'
