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
        print(f'{self._name}\nanswer: {answer}')
        return answer

    def ping(self):
        return self._inst.query('*IDN?')

    def reset(self):
        return self.send(f'SYSTem:FPRESet')

    def create_measurement(self, chan=1, meas_name='', meas_type='S21'):
        if not meas_name:
            meas_name = f'meas_{meas_type}'
        return self.send(f"CALCulate{chan}:PARameter:DEFine:EXTended '{meas_name}',{meas_type}"), meas_name

    def create_window(self, window=1):
        return self.send(f'DISPlay:WINDow{window}:STATe ON')

    def display_measurement(self, window=1, trace=1, meas_name=''):
        return self.send(f"DISPlay:WINDow{window}:TRACe{trace}:FEED '{meas_name}'")

    def set_trigger_source(self, source):
        """
        EXTernal - external (rear panel) source.
        IMMediate - internal source sends continuous trigger signals
        MANual - sends one trigger signal when manually triggered from the front panel or INIT:IMM is sent.
        :param source:
        :return:
        """
        return self.send(f'TRIGger:SEQuence:SOURce {source}')

    def set_trigger_point_mode(self, chan=1, mode='OFF'):
        """
        ON (or 1) - Channel measures one data point per trigger.
        OFF (or 0) - All measurements in the channel made per trigger

        :param mode:
        :return:
        """
        return self.send(f'SENSe{chan}:SWEep:TRIGger:POINt {mode}')

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


