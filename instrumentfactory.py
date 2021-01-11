import visa

from instr.agilent34410a import Agilent34410A
from instr.agilent34410amock import Agilent34410AMock
from instr.agilente3644a import AgilentE3644A
from instr.agilente3644amock import AgilentE3644AMock
from instr.agilentn1914a import AgilentN1914A
from instr.agilentn1914amock import AgilentN1914AMock
from instr.agilentn5183a import AgilentN5183A
from instr.agilentn5183amock import AgilentN5183AMock
from instr.agilentn9030a import AgilentN9030A
from instr.agilentn9030amock import AgilentN9030AMock
from instr.agilente8362b import AgilentE8362B
from instr.agilente8362bmock import AgilentE8362BMock
from instr.oscilloscope import Oscilloscope
from instr.oscilloscopemock import OscilloscopeMock
from instr.semiconductoranalyzer import SemiconductorAnalyzer
from instr.semiconductoranalyzermock import SemiconductorAnalyzerMock

mock_enabled = True


class InstrumentFactory:
    def __init__(self, addr, label):
        self.applicable = None
        self.addr = addr
        self.label = label
    def find(self):
        # TODO remove applicable instrument when found one if needed more than one instrument of the same type
        # TODO: idea: pass list of applicable instruments to differ from the model of the same type?
        instr = self.from_address()
        # if not instr:
        #     return self.try_find()
        return instr
    def from_address(self):
        raise NotImplementedError
    def try_find(self):
        raise NotImplementedError()


class GeneratorFactory(InstrumentFactory):
    def __init__(self, addr):
        super().__init__(addr=addr, label='Генератор')
        self.applicable = ['N5183A', 'N5181B', 'E4438C', 'E8257D', 'HMC-T2100']
    def from_address(self):
        if mock_enabled:
            return AgilentN5183A(self.addr, '1,N5183A mock,1', AgilentN5183AMock())
        try:
            rm = visa.ResourceManager()
            inst = rm.open_resource(self.addr)
            idn = inst.query('*IDN?')
            name = idn.split(',')[1].strip()
            if name in self.applicable:
                return AgilentN5183A(self.addr, idn, inst)
        except Exception as ex:
            print('Generator find error:', ex)
            exit(1)


class AnalyzerFactory(InstrumentFactory):
    def __init__(self, addr):
        super().__init__(addr=addr, label='Анализатор')
        self.applicable = ['N9030A', 'N9041B', 'E4446A']
    def from_address(self):
        if mock_enabled:
            return AgilentN9030A(self.addr, '1,N9030A mock,1', AgilentN9030AMock())
        try:
            rm = visa.ResourceManager()
            inst = rm.open_resource(self.addr)
            idn = inst.query('*IDN?')
            name = idn.split(',')[1].strip()
            if name in self.applicable:
                return AgilentN9030A(self.addr, idn, inst)
        except Exception as ex:
            print('Analyzer find error:', ex)
            exit(2)


class MultimeterFactory(InstrumentFactory):
    def __init__(self, addr):
        super().__init__(addr=addr, label='Мультиметр')
        self.applicable = ['34410A']
    def from_address(self):
        if mock_enabled:
            return Agilent34410A(self.addr, '1,34410A mock,1', Agilent34410AMock())
        try:
            rm = visa.ResourceManager()
            inst = rm.open_resource(self.addr)
            idn = inst.query('*IDN?')
            name = idn.split(',')[1].strip()
            if name in self.applicable:
                return Agilent34410A(self.addr, idn, inst)
        except Exception as ex:
            print('Multimeter find error:', ex)
            exit(3)


class SourceFactory(InstrumentFactory):
    def __init__(self, addr):
        super().__init__(addr=addr, label='Исчточник питания')
        self.applicable = ['E3648A', 'N6700C', 'E3631A', 'E3644A']
    def from_address(self):
        if mock_enabled:
            return AgilentE3644A(self.addr, '1,E3648A mock,1', AgilentE3644AMock())
        try:
            rm = visa.ResourceManager()
            inst = rm.open_resource(self.addr)
            idn = inst.query('*IDN?')
            name = idn.split(',')[1].strip()
            if name in self.applicable:
                return AgilentE3644A(self.addr, idn, inst)
        except Exception as ex:
            print('Source find error:', ex)
            exit(4)


class NetworkAnalyzerFactory(InstrumentFactory):
    def __init__(self, addr):
        super().__init__(addr=addr, label='Анализатор цепей')
        self.applicable = ['E8362B']
    def from_address(self):
        if mock_enabled:
            return AgilentE8362B(self.addr, '1,E8362B mock,1', AgilentE8362BMock())
        try:
            rm = visa.ResourceManager()
            inst = rm.open_resource(self.addr)
            idn = inst.query('*IDN?')
            name = idn.split(',')[1].strip()
            if name in self.applicable:
                return AgilentE8362B(self.addr, idn, inst)
        except Exception as ex:
            print('Source find error:', ex)
            exit(5)


class PowerMeterFactory(InstrumentFactory):
    def __init__(self, addr):
        super().__init__(addr=addr, label='Анализатор цепей')
        self.applicable = ['N1914A', 'N1912A']
    def from_address(self):
        if mock_enabled:
            return AgilentN1914A(self.addr, '1,N1914A mock,1', AgilentN1914AMock())
        try:
            rm = visa.ResourceManager()
            inst = rm.open_resource(self.addr)
            idn = inst.query('*IDN?')
            name = idn.split(',')[1].strip()
            if name in self.applicable:
                return AgilentE3644A(self.addr, idn, inst)
        except Exception as ex:
            print('Source find error:', ex)
            exit(6)


class OscilloscopeFactory(InstrumentFactory):
    """
    Applicable models:
        - AGILENT TECHNOLOGIES,DSO-X 3034A,MY51452204,02.00.2011101301
    """
    def __init__(self, addr):
        super().__init__(addr=addr, label='Осциллограф')
        self.applicable = ['DSO-X 3034A']
    def from_address(self):
        if mock_enabled:
            return Oscilloscope(self.addr, '1,DSO-X 3034A mock,1', OscilloscopeMock())
        try:
            rm = visa.ResourceManager()
            inst = rm.open_resource(self.addr)
            idn = inst.query('*IDN?')
            name = idn.split(',')[1].strip()
            if name in self.applicable:
                return Oscilloscope(self.addr, idn, inst)
        except Exception as ex:
            print('Source find error:', ex)
            exit(7)


class SemiconductorAnalyzerFactory(InstrumentFactory):
    """
    Applicable models:
        - B1500A analyzer #TODO fix id string
    """
    def __init__(self, addr):
        super().__init__(addr=addr, label='Анализатор п/п приборов')
        self.applicable = ['B1500A']
    def from_address(self):
        if mock_enabled:
            return SemiconductorAnalyzer(self.addr, '1,B1500A mock,1', SemiconductorAnalyzerMock())
        try:
            rm = visa.ResourceManager()
            inst = rm.open_resource(self.addr)
            idn = inst.query('*IDN?')
            name = idn.split(',')[1].strip()
            if name in self.applicable:
                return SemiconductorAnalyzer(self.addr, idn, inst)
        except Exception as ex:
            print('Semiconductor analyzer find error:', ex)
            exit(7)
