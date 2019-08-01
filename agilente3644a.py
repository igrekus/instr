class AgilentE3644A:
    """
    Agilent E3644A
    Single channel power source.
    """
    def __init__(self, address: str, idn: str, inst):
        self._address = address
        self._idn = idn
        self._name = idn.split(',')[1].strip()
        self._inst = inst

        self._active_channel = 1

    def __str__(self):
        return f'{self._name}'

    def __repr__(self):
        return f'{self.__class__}(idn={self._idn})'

    def send(self, command):
        print(f'{self._name}: {command}', self._inst.write(command))

    def query(self, question):
        answer = self._inst.query(question)
        print(f'{self._name}: {question} {answer}')
        return answer

    def reset(self):
        print(f'{self._name} reset')
        print(self.send('*RST'))
        self.active_channel = 1

    def ping(self):
        print(self.query('*IDN?'))

    # TODO make chan switch decorator
    def set_current(self, chan: int, value: float, unit: str):
        if chan not in [1, 2]:
            raise ValueError('Wrong channel index.')

        if chan != self.active_channel:
            self.active_channel = chan

        self.send(f'CURRent {value}{unit}')

    def set_voltage_limit(self, chan: int, value: float, unit: str):
        if chan not in [1, 2]:
            raise ValueError('Wrong channel index.')

        if chan != self.active_channel:
            self.active_channel = chan

        self.send(f'VOLT:PROT {value}{unit}')
        self.send(f'VOLT:PROT:STAT ON{value}{unit}')

    def set_voltage(self, chan: int, value: float, unit: str):
        if chan not in [1, 2]:
            raise ValueError('Wrong channel index.')

        if chan != self.active_channel:
            self.active_channel = chan

        self.send(f'VOLT {value}{unit}')

    def set_output(self, chan, state):
        if chan not in [1, 2]:
            raise ValueError('Wrong channel index.')

        if chan != self.active_channel:
            self.active_channel = chan

        self.send(f'OUTP {state}')

    def set_system_local(self):
        # pass
        self.send(f'system:local')

    # set parameters and trigger output
    # VOLT:TRIG 3.0
    # CURR:TRIG 1.0
    # TRIG:SOUR IMM
    # INIT

    # or
    # APPLy volt, curr

    # select output
    # INSTrument:SELect OUTPut1|OUTPut2

    # select trigger source
    # TRIGger:SOURce BUS|IMMediate --> *TRG|INITiate

    # src.send('*RST')
    #
    # src.send(f'INST:SEL OUTP1')
    # src.send(f'volt:prot 4')
    # src.send(f'current 2')
    # src.send(f'voltage 2')
    #
    # src.send(f'outp on')
    #
    # time.sleep(5)
    #
    # src.send(f'outp off')

    @property
    def name(self):
        return self._name

    @property
    def active_channel(self):
        return self._active_channel

    @active_channel.setter
    def active_channel(self, chan):
        if chan not in [1, 2]:
            raise ValueError('Wrong channel index.')

        if chan != self._active_channel:
            print(f'{self._name} select chan {chan}', self.send(f'INST:SEL OUTP{chan}'))
            self._active_channel = chan

    @property
    def addr(self):
        return self._address

    @property
    def model(self):
        return self.name

    @property
    def status(self):
        return f'{self.model} at {self.addr}'
