class SemiconductorAnalyzer:
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
