import visa


class Pna20(object):

    model = 'PNA20'

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
        if 'CALC:PN:TRAC:' not in question and 'CALC:FN:TRAC:' not in question:
            answer = self._inst.query(question)
        else:
            answer = self._inst.query_binary_values(question)
        print(f'> {answer}')
        return answer

    def ping(self):
        return self._inst.query('*IDN?')

    def reset(self):
        return self.send(f'*RST')

    # :CALCULATE subsystem
    def calc_wait_average(self, param='ALL'):
        return self.send(f':CALCulate:WAIT:AVERage {param}')

    def calc_pn_trace_freq(self):
        return self.query(f':CALCulate:PN:TRACe:FREQuency?')

    def calc_pn_trace_noise(self):
        return self.query(f':CALCulate:PN:TRACe:NOISe?')

    # :SENSE subsystem
    def sense_pn_average(self, value: int):
        return self.send(f':SENSe:PN:AVERage {value}')

    def sense_freq_start(self, value: int):
        return self.send(f':SENSe:PN:FREQuency:STARt {value}')

    def sense_freq_stop(self, value: int):
        return self.send(f':SENSe:PN:FREQuency:STOP {value}')

    def sense_references_tune_max(self, source: int, value: float):
        return self.send(f':SENSe:PN:REFerences:TUNE:MAX {source},{value}')

    # SYSTEM subsystem
    def system_error_all(self):
        return self.query(':SYSTEM:ERROR:ALL?')

    # :TRIGGER subsystem
    def trigger_init(self):
        return self.send(f'INIT')

    @property
    def name(self):
        return self._name

    @property
    def operation_complete(self):
        # TODO check query return value
        ans = self.query('*OPC?')
        return bool(ans)

    @classmethod
    def from_instance(cls, idn, inst):
        return cls(idn=idn, inst=inst)

    @classmethod
    def from_address_string(cls, address: str):
        rm = visa.ResourceManager()
        try:
            inst = rm.open_resource(address)
            idn = inst.query('*IDN?')
            return cls(idn, inst=inst)
        except visa.VisaIOError as ex:
            raise RuntimeError(f'VISA error: {address}: {ex}')

    @classmethod
    def try_find(cls):
        rm = visa.ResourceManager()
        for res in rm.list_resources():
            print(f'trying {res}')
            try:
                inst = rm.open_resource(res)
                idn = inst.query('*IDN?')
                if cls.model in idn:
                    return cls(idn=idn, inst=inst), res
            except visa.VisaIOError as ex:
                print(f'VISA error: {ex}')


