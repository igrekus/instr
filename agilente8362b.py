class AgilentE8362B(object):

    model = 'E8362B'

    def __init__(self, idn: str, inst):
        self._idn = idn
        _, name, _, _ = idn.split(',')
        self._name = name.strip()
        self._inst = inst

    def __str__(self):
        return f'{self._name}'

    def __repr__(self):
        return f'{self.__class__}(idn={self._idn})'

    def send(self, command):
        print(f'{self._name} send {command}:', self._inst.write(command))

    def query(self, question):
        print(f'{self._name} ask {question}')
        answer = self._inst.query(question)
        print(f'{self._name} answer: {answer}')
        return answer

    def ping(self):
        return self._inst.query('*IDN?')

    def set_autocalibrate(self, status: str):
        self.send(f':CAL:AUTO {status}')

    def set_span(self, value, unit):
        self.send(f':SENS:FREQ:SPAN {str(value)}{unit}')

    def set_marker_mode(self, marker: int, mode='POS'):
        self.send(f':CALC:MARK{marker}:MODE {mode}')

    def set_pow_attenuation(self, value):
        self.send(f':POW:ATT {value}')

    def set_measure_center_freq(self, value, unit):
        self.send(f':SENSe:FREQuency:RF:CENTer {str(value)}{unit}')

    def set_marker1_x_center(self, value, unit):
        self.send(f':CALCulate:MARKer1:X:CENTer {str(value)}{unit}')

    def read_pow(self, marker: int) -> float:
        answer = self.query(f':CALCulate:MARKer:Y?')
        return float(answer)
        # return random.choice([-12, -50])

    def remove_marker(self, marker):
        return self.send(f'SET MARKER{marker} OFF')

    def set_system_local(self):
        # pass
        self.send(f'system:local')

    @property
    def name(self):
        return self._name

    @classmethod
    def from_instance(cls, idn, inst):
        return cls(idn=idn, inst=inst)

    @classmethod
    def from_address_string(cls, address: str):
        import visa
        rm = visa.ResourceManager()
        try:
            inst = rm.open_resource(address)
            idn = inst.query('*IDN?')
            return cls(idn, inst=inst)
        except visa.VisaIOError as ex:
            raise RuntimeError(f'VISA error: {address}: {ex}')

    @classmethod
    def try_find(cls):
        import visa
        rm = visa.ResourceManager()
        for res in rm.list_resources():
            try:
                inst = rm.open_resource(res)
                idn = inst.query('*IDN?')
                if cls.model in idn:
                    return cls(idn=idn, inst=inst)
            except visa.VisaIOError as ex:
                print(f'VISA error: {ex}')


